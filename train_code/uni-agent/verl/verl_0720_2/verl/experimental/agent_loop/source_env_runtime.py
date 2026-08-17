import ast
import copy
import importlib
import inspect
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Union, get_args, get_origin


MODEL_TOOL_CALL_RE = re.compile(
    r"env\[(?P<quote>['\"])(?P<env_name>.*?)(?P=quote)\]\.(?P<call>.+)$",
    re.DOTALL,
)


@dataclass
class LoadedEnv:
    env_name: str
    class_name: str
    env_class: type
    instance: Any


def _select_source_env_class(module: Any) -> type:
    candidates: list[type] = []
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ != module.__name__:
            continue
        if callable(getattr(cls, "_load_scenario", None)) and callable(getattr(cls, "get_env_state", None)):
            candidates.append(cls)

    if not candidates:
        raise ValueError(
            f"No source_env class found in module {module.__name__}. "
            "Expected a class with _load_scenario() and get_env_state()."
        )

    def score(cls: type) -> tuple[int, int, str]:
        public_methods = [
            name
            for name, member in inspect.getmembers(cls)
            if callable(member) and not name.startswith("_") and name != "get_env_state"
        ]
        preferred_name = int(
            any(
                token in cls.__name__.lower()
                for token in ("api", "system", "backend", "platform", "database", "server", "filesystem")
            )
        )
        return (preferred_name, len(public_methods), cls.__name__)

    return max(candidates, key=score)


def _parse_function_call(function_call: str) -> tuple[str, list[Any], dict[str, Any]]:
    try:
        expression = ast.parse(function_call, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid function call syntax: {function_call}") from exc

    call_node = expression.body
    if not isinstance(call_node, ast.Call):
        raise ValueError(f"Expected a function call, got: {function_call}")
    if not isinstance(call_node.func, ast.Name):
        raise ValueError(f"Unsupported function target in: {function_call}")

    args = [ast.literal_eval(arg) for arg in call_node.args]
    kwargs = {}
    for keyword in call_node.keywords:
        if keyword.arg is None:
            raise ValueError("**kwargs style function calls are not supported.")
        kwargs[keyword.arg] = ast.literal_eval(keyword.value)

    return call_node.func.id, args, kwargs


def _annotation_to_json_type(annotation: Any) -> str:
    if annotation in (inspect.Signature.empty, Any):
        return "string"
    if annotation in (str,):
        return "string"
    if annotation in (int,):
        return "integer"
    if annotation in (float,):
        return "number"
    if annotation in (bool,):
        return "boolean"
    if annotation in (dict,):
        return "object"
    if annotation in (list, tuple, set):
        return "array"

    origin = get_origin(annotation)
    if origin in (list, tuple, set):
        return "array"
    if origin in (dict,):
        return "object"
    if origin is Union:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _annotation_to_json_type(args[0])
    return "string"


def _build_tool_definition(loaded_env: LoadedEnv, method_name: str, method: Any) -> dict[str, Any]:
    signature = inspect.signature(method)
    properties: dict[str, dict[str, str]] = {}
    required: list[str] = []

    for parameter_name, parameter in signature.parameters.items():
        if parameter_name == "self":
            continue
        if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        properties[parameter_name] = {
            "type": _annotation_to_json_type(parameter.annotation),
            "description": f"Parameter `{parameter_name}` for `{method_name}`.",
        }
        if parameter.default is inspect.Signature.empty:
            required.append(parameter_name)

    description = inspect.getdoc(method) or ""
    description = description.splitlines()[0].strip() if description else f"Call `{method_name}` on `{loaded_env.env_name}`."

    return {
        "name": method_name,
        "description": description,
        "parameters": {
            "type": "dict",
            "properties": properties,
            "required": required,
        },
        "response": {
            "type": "dict",
            "properties": {},
        },
    }


class SourceEnvRuntime:
    """Thin runtime around dynamically loaded source_env modules."""

    def __init__(
        self,
        env_configs: dict[str, dict[str, Any]],
        source_env_dir: str,
        long_context: bool = False,
    ) -> None:
        if not source_env_dir:
            raise ValueError("`source_env_dir` is required to load custom source_env modules.")

        self.long_context = long_context
        self.source_env_dir = os.path.abspath(source_env_dir)
        self.package_name = os.path.basename(self.source_env_dir)
        self.package_parent = os.path.dirname(self.source_env_dir)
        self._ensure_import_path()

        self.envs: dict[str, LoadedEnv] = {}
        for env_name, scenario in env_configs.items():
            self.envs[env_name] = self._load_env(env_name, scenario or {})

    def _ensure_import_path(self) -> None:
        if self.package_parent not in sys.path:
            sys.path.insert(0, self.package_parent)

    def _load_env(self, env_name: str, scenario: dict[str, Any]) -> LoadedEnv:
        module = importlib.import_module(f"{self.package_name}.{env_name}")
        env_class = _select_source_env_class(module)
        env_instance = env_class()
        env_instance._load_scenario(copy.deepcopy(scenario), long_context=self.long_context)
        return LoadedEnv(
            env_name=env_name,
            class_name=env_class.__name__,
            env_class=env_class,
            instance=env_instance,
        )

    def _get_loaded_env(self, env_name: str) -> LoadedEnv:
        if env_name not in self.envs:
            raise KeyError(f"Environment '{env_name}' is not loaded.")
        return self.envs[env_name]

    def get_state(self) -> dict[str, Any]:
        return {env_name: loaded.instance.get_env_state() for env_name, loaded in self.envs.items()}

    def run_env_call(self, env_name: str, function_call: str) -> Any:
        loaded = self._get_loaded_env(env_name)
        func_name, args, kwargs = _parse_function_call(function_call)
        func = getattr(loaded.instance, func_name, None)
        if not callable(func):
            raise AttributeError(f"Environment '{env_name}' has no callable tool '{func_name}'.")
        return func(*args, **kwargs)

    def run_model_tool_call(self, tool_call: str) -> Any:
        match = MODEL_TOOL_CALL_RE.match(tool_call.strip())
        if not match:
            raise ValueError("Tool call must use the form env['env_name'].tool_name(param=value).")
        env_name = match.group("env_name")
        function_call = match.group("call")
        return self.run_env_call(env_name, function_call)

    def get_tool_definitions(self) -> dict[str, list[dict[str, Any]]]:
        tool_definitions: dict[str, list[dict[str, Any]]] = {}
        for env_name, loaded_env in self.envs.items():
            tools = []
            for method_name, method in inspect.getmembers(loaded_env.env_class, inspect.isfunction):
                if method_name.startswith("_") or method_name == "get_env_state":
                    continue
                tools.append(_build_tool_definition(loaded_env, method_name, method))
            tool_definitions[env_name] = tools
        return tool_definitions

    def get_env_descriptions(self) -> dict[str, dict[str, str]]:
        descriptions: dict[str, dict[str, str]] = {}
        current_state = self.get_state()
        for env_name, loaded_env in self.envs.items():
            env_description = getattr(loaded_env.instance, "_api_description", None)
            if not env_description:
                env_description = inspect.getdoc(loaded_env.env_class) or ""
            env_description = env_description.splitlines()[0].strip() if env_description else loaded_env.class_name

            state_keys = sorted(current_state.get(env_name, {}).keys())
            state_description = "Top-level environment state keys: " + ", ".join(state_keys)
            descriptions[env_name] = {
                "env_des": env_description,
                "state_des": state_description,
            }
        return descriptions


