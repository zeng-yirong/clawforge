import ast
import json
import logging
import os
import re
import warnings
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from verl.experimental.agent_loop.agent_loop import AgentLoopBase, AgentLoopOutput, register
from verl.experimental.agent_loop.source_env_runtime import SourceEnvRuntime
from verl.utils.profiler import simple_timer
from verl.utils.rollout_trace import rollout_trace_op

logger = logging.getLogger(__file__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


SYSTEM_PROMPT = """
You are an intelligent General-Purpose Embodied Agent.
Your goal is to solve user problems by generating tool calls that interact with the provided environments.
You will receive:
1. Environment descriptions
2. Tool definitions
3. The current user request
Rules:
1. You can only act through tool calls in this exact format:
   env['env_name'].tool_name(param=value)
2. Use only tools listed in the tool definitions.
3. Do not invent tools, parameters, IDs, or state.
4. If multiple tool calls are needed, return them in execution order.
5. Use valid Python literal syntax for argument values.
6. The initial and current environment states are NOT provided automatically. You MUST actively call `env['env_name'].get_env_state()` to perceive the environment state before taking actions.
7. CRITICAL: You MUST output ONLY a valid JSON object. Do not include markdown formatting, explanations, or any other conversational text.
Return exactly one JSON object and nothing else in the following format.
If tools are needed:
{
  "need_tool_call": true,
  "tool_call": [
    "env['env_name'].tool_name(param=value)"
  ]
}
If tools are not needed:
{
  "need_tool_call": false,
  "content": "Concise response."
}
Environment Descriptions:
<<ENV_DESCRIPTIONS>>
Tool Definitions:
<<TOOL_DEFINITIONS>>
""".strip()

TOOL_CALL_RE = re.compile(
    r"env\[(?P<quote>['\"])(?P<env_name>.*?)(?P=quote)\]\.(?P<call>.+)$",
    re.DOTALL,
)


def _cfg_get(config_node: Any, key: str, default: Any = None) -> Any:
    if config_node is None:
        return default
    if hasattr(config_node, "get"):
        try:
            return config_node.get(key, default)
        except Exception:
            pass
    return getattr(config_node, key, default)


def _parse_data_field(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped:
        return default

    try:
        return json.loads(stripped)
    except Exception:
        pass

    try:
        return ast.literal_eval(stripped)
    except Exception:
        return value


def to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, set):
        return [to_jsonable(item) for item in sorted(value, key=str)]
    return str(value)


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def build_system_prompt(
    env_names: list[str],
    env_descriptions: dict[str, dict[str, Any]],
    tool_definitions: dict[str, list[dict[str, Any]]],
) -> str:
    selected_env_descriptions = {
        env_name: {
            "env_des": env_descriptions.get(env_name, {}).get("env_des", ""),
            "state_des": env_descriptions.get(env_name, {}).get("state_des", ""),
        }
        for env_name in env_names
    }
    selected_tool_definitions = {env_name: tool_definitions.get(env_name, []) for env_name in env_names}

    return (
        SYSTEM_PROMPT.replace(
            "<<ENV_DESCRIPTIONS>>",
            json.dumps(to_jsonable(selected_env_descriptions), ensure_ascii=False, indent=2),
        )
        .replace(
            "<<TOOL_DEFINITIONS>>",
            json.dumps(to_jsonable(selected_tool_definitions), ensure_ascii=False, indent=2),
        )
    )


def strip_markdown(text: str) -> str:
    text = text.strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_response_json(text: str) -> Optional[dict[str, Any]]:
    cleaned = strip_markdown(text)
    candidates = [cleaned]
    if "{" in cleaned and "}" in cleaned:
        candidates.append(cleaned[cleaned.find("{") : cleaned.rfind("}") + 1])

    for candidate in candidates:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
    return None


def extract_env_name(tool_call: str) -> Optional[str]:
    match = TOOL_CALL_RE.match(tool_call.strip())
    return match.group("env_name") if match else None


def infer_completed_plan_steps(messages: list[dict[str, Any]], user_plan: list[dict[str, Any]]) -> int:
    user_contents = [str(message.get("content", "")) for message in messages if message.get("role") == "user"]
    planned_contents = [str(step.get("user_content", "")) for step in user_plan]

    completed = 0
    for content in user_contents:
        if completed < len(planned_contents) and content == planned_contents[completed]:
            completed += 1
    return completed


def count_non_system_turns(messages: list[dict[str, Any]]) -> int:
    return sum(1 for message in messages if message.get("role") != "system")


class AgentState(Enum):
    PENDING = "pending"
    GENERATING = "generating"
    PROCESSING_TOOLS = "processing_tools"
    APPENDING_USER_STEP = "appending_user_step"
    TERMINATED = "terminated"


class AgentData:
    def __init__(
        self,
        *,
        messages: list[dict[str, Any]],
        image_data: Any,
        video_data: Any,
        metrics: dict[str, Any],
        request_id: str,
        runtime: SourceEnvRuntime,
        env_names: list[str],
        init_env: dict[str, Any],
        user_plan: list[dict[str, Any]],
        next_step_index: int,
        validation_protocol: str,
        task_id: str,
    ) -> None:
        self.messages = messages
        self.image_data = image_data
        self.video_data = video_data
        self.metrics = metrics
        self.request_id = request_id
        self.runtime = runtime
        self.env_names = env_names
        self.init_env = init_env
        self.user_plan = user_plan
        self.next_step_index = next_step_index
        self.validation_protocol = validation_protocol
        self.task_id = task_id

        self.prompt_ids: list[int] = []
        self.response_ids: list[int] = []
        self.response_mask: list[int] = []
        self.response_logprobs: list[float] = []
        self.execution_trace: list[str] = []
        self.agent_turns = 0
        self.final_response: Optional[str] = None
        self.error: Optional[str] = None
        self.status = "running"
        self.is_success = False
        self.validation_result: dict[str, Any] = {}
        self.pending_tool_calls: Any = []


@register("source_env_agent")
class SourceEnvAgentLoop(AgentLoopBase):
    """Multi-turn loop for source_env style tasks and user_plan execution."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rollout_config = self.config.actor_rollout_ref.rollout
        self.multi_turn_config = rollout_config.multi_turn
        self.agent_config = _cfg_get(rollout_config, "agent", {})

        self.prompt_length = rollout_config.prompt_length
        self.response_length = rollout_config.response_length
        self.max_user_turns = _cfg_get(self.multi_turn_config, "max_user_turns", 0)
        self.max_agent_turns = _cfg_get(self.multi_turn_config, "max_agent_turns", None)
        if self.max_agent_turns is None:
            legacy_max_assistant_turns = _cfg_get(self.multi_turn_config, "max_assistant_turns", None)
            if legacy_max_assistant_turns is not None:
                warnings.warn(
                    "`multi_turn.max_assistant_turns` is deprecated for source_env_agent; "
                    "use `multi_turn.max_agent_turns` instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                self.max_agent_turns = legacy_max_assistant_turns

        if _cfg_get(self.multi_turn_config, "max_tool_turns_per_step", None) is not None:
            warnings.warn(
                "`multi_turn.max_tool_turns_per_step` is ignored by source_env_agent; "
                "use `multi_turn.max_agent_turns` to limit the complete agent interaction.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.use_validation_reward = bool(_cfg_get(self.agent_config, "use_validation_reward", True))
        self.default_long_context = bool(_cfg_get(self.agent_config, "source_env_long_context", False))

        self.default_source_env_dir = _cfg_get(self.agent_config, "source_env_dir", None)
        self.default_env_docs_file = _cfg_get(self.agent_config, "env_docs_file", None)
        self.default_tool_docs_dir = _cfg_get(self.agent_config, "tool_docs_dir", None)

    def _resolve_resource_path(self, candidate: Optional[str], env_var_name: str) -> Optional[str]:
        value = candidate or os.getenv(env_var_name)
        if not value:
            return None
        return os.path.abspath(os.path.expanduser(value))

    def _load_tool_definitions(
        self,
        env_names: list[str],
        runtime: SourceEnvRuntime,
        tool_docs_dir: Optional[str],
    ) -> dict[str, list[dict[str, Any]]]:
        fallback = runtime.get_tool_definitions()
        if not tool_docs_dir or not os.path.isdir(tool_docs_dir):
            return fallback

        tool_definitions: dict[str, list[dict[str, Any]]] = {}
        for env_name in env_names:
            path = os.path.join(tool_docs_dir, f"{env_name}.json")
            if os.path.exists(path):
                tool_definitions[env_name] = load_json(path)
            else:
                tool_definitions[env_name] = fallback.get(env_name, [])
        return tool_definitions

    def _load_env_descriptions(
        self,
        env_names: list[str],
        runtime: SourceEnvRuntime,
        env_docs_file: Optional[str],
    ) -> dict[str, dict[str, Any]]:
        fallback = runtime.get_env_descriptions()
        if not env_docs_file or not os.path.exists(env_docs_file):
            return fallback

        env_docs = load_json(env_docs_file)
        descriptions: dict[str, dict[str, Any]] = {}
        for env_name in env_names:
            descriptions[env_name] = env_docs.get(env_name, fallback.get(env_name, {}))
        return descriptions

    def _extract_task_spec(self, extra_info: dict[str, Any]) -> dict[str, Any]:
        meta = _parse_data_field(extra_info.get("meta"), {}) or {}
        user_plan = _parse_data_field(extra_info.get("user_plan"), None)
        if user_plan is None and "user_plan" in meta:
            user_plan = _parse_data_field(meta.get("user_plan"), [])
        user_plan = user_plan or []

        env_names = _parse_data_field(extra_info.get("env_names"), None)
        if env_names is None:
            env_names = _parse_data_field(meta.get("env_names"), [])
        env_names = env_names or []

        init_env = _parse_data_field(extra_info.get("init_env"), None)
        if init_env is None:
            init_env = _parse_data_field(meta.get("init_env"), {})
        init_env = init_env or {}

        validation_protocol = extra_info.get("validation_protocol")
        if validation_protocol is None:
            validation_protocol = meta.get("validation_protocol", "")
        validation_protocol = validation_protocol or ""

        task_id = str(extra_info.get("task_id") or meta.get("task_id") or "")
        long_context = _parse_data_field(extra_info.get("long_context"), None)
        if long_context is None:
            long_context = self.default_long_context

        source_env_dir = self._resolve_resource_path(
            extra_info.get("source_env_dir") or self.default_source_env_dir,
            "VERL_SOURCE_ENV_DIR",
        )
        env_docs_file = self._resolve_resource_path(
            extra_info.get("env_docs_file") or self.default_env_docs_file,
            "VERL_SOURCE_ENV_DOCS_FILE",
        )
        tool_docs_dir = self._resolve_resource_path(
            extra_info.get("tool_docs_dir") or self.default_tool_docs_dir,
            "VERL_SOURCE_ENV_TOOL_DOCS_DIR",
        )

        if not env_names and isinstance(init_env, dict):
            env_names = list(init_env.keys())

        return {
            "meta": meta,
            "user_plan": user_plan,
            "env_names": env_names,
            "init_env": init_env,
            "validation_protocol": validation_protocol,
            "task_id": task_id,
            "long_context": bool(long_context),
            "source_env_dir": source_env_dir,
            "env_docs_file": env_docs_file,
            "tool_docs_dir": tool_docs_dir,
        }

    def _prepare_initial_messages(
        self,
        raw_messages: list[dict[str, Any]],
        env_names: list[str],
        env_descriptions: dict[str, dict[str, Any]],
        tool_definitions: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        messages = list(raw_messages)
        if not any(message.get("role") == "system" for message in messages):
            system_prompt = build_system_prompt(env_names, env_descriptions, tool_definitions) # 移除 init_env
            messages = [{"role": "system", "content": system_prompt}] + messages
        return messages

    async def _append_messages_to_prompt(
        self,
        agent_data: AgentData,
        add_messages: list[dict[str, Any]],
        *,
        mask_value: int,
    ) -> bool:
        response_ids = await self.apply_chat_template(
            add_messages,
            images=None,
            videos=None,
            remove_system_prompt=True,
        )
        if len(agent_data.response_mask) + len(response_ids) >= self.response_length:
            return False

        agent_data.messages.extend(add_messages)
        agent_data.prompt_ids += response_ids
        agent_data.response_mask += [mask_value] * len(response_ids)
        if agent_data.response_logprobs:
            agent_data.response_logprobs += [0.0] * len(response_ids)
        return True

    async def _append_next_user_step(self, agent_data: AgentData) -> bool:
        if agent_data.next_step_index >= len(agent_data.user_plan):
            return False

        step = agent_data.user_plan[agent_data.next_step_index]
        content = str(step.get("user_content", ""))
        add_messages = [{"role": "user", "content": content}]
        agent_data.next_step_index += 1
        return await self._append_messages_to_prompt(agent_data, add_messages, mask_value=0)

    def _execute_tool_calls(self, agent_data: AgentData, tool_calls: Any) -> str:
        if isinstance(tool_calls, str):
            calls = [tool_calls]
        elif isinstance(tool_calls, list):
            calls = [str(item) for item in tool_calls]
        else:
            calls = [str(tool_calls)]

        if not calls:
            calls = []

        logs: list[str] = []
        for tool_call in calls:
            agent_data.execution_trace.append(tool_call)
            try:
                result = agent_data.runtime.run_model_tool_call(tool_call)
                logs.append(f"Tool: {tool_call}\nResult: {json.dumps(to_jsonable(result), ensure_ascii=False)}")
            except Exception as exc:
                logs.append(f"Tool: {tool_call}\nError: {exc}")

        if not logs:
            logs.append("No tool calls were provided.")

        # 删除了获取 agent_data.runtime.get_state() 的逻辑
        log_text = "\n\n".join(logs)
        return f"Execute results:\n{log_text}"

    def _build_validation_env_variants(self, env_final_state: Any) -> list[Any]:
        env_variants = [env_final_state]
        if isinstance(env_final_state, dict) and len(env_final_state) == 1:
            single_key = next(iter(env_final_state.keys()))
            if isinstance(env_final_state[single_key], dict):
                env_variants.append(env_final_state[single_key])
        return env_variants

    def _run_validation_protocol(
        self,
        validation_protocol: str,
        env_final_state: dict[str, Any],
        execution_trace: list[str],
        final_response: Optional[str],
    ) -> dict[str, Any]:
        if not validation_protocol:
            return {"success": None, "reason": "No validation protocol provided."}

        env_variants = self._build_validation_env_variants(env_final_state)
        last_result: dict[str, Any] = {"success": False, "reason": "Validation did not return a passing result."}

        for current_env in env_variants:
            globals_dict = {
                "__builtins__": __builtins__,
                "json": json,
                "re": re,
            }
            locals_dict: dict[str, Any] = {}

            try:
                exec(validation_protocol, globals_dict, locals_dict)
                validate_fn = locals_dict.get("validate") or globals_dict.get("validate")
                if not callable(validate_fn):
                    raise ValueError("Validation protocol does not define a callable `validate` function.")
                result = validate_fn(current_env, execution_trace, final_response)
            except Exception as exc:
                last_result = {"success": False, "reason": f"Validation protocol execution failed: {exc}"}
                continue

            if isinstance(result, dict):
                if "success" not in result:
                    result["success"] = False
                if bool(result.get("success", False)):
                    return result
                last_result = result
                continue

            if isinstance(result, bool):
                normalized_result = {"success": result}
                if result:
                    return normalized_result
                last_result = normalized_result
                continue

            last_result = {
                "success": False,
                "reason": f"Unexpected validation result type: {type(result).__name__}",
            }

        return last_result

    async def _handle_pending_state(self, agent_data: AgentData) -> AgentState:
        prompt_ids = await self.apply_chat_template(
            agent_data.messages,
            images=agent_data.image_data,
            videos=agent_data.video_data,
        )
        agent_data.prompt_ids = prompt_ids
        return AgentState.GENERATING

    async def _handle_generating_state(self, agent_data: AgentData, sampling_params: dict[str, Any]) -> AgentState:
        if self.max_agent_turns and agent_data.agent_turns >= self.max_agent_turns:
            for message in reversed(agent_data.messages):
                if message.get("role") == "assistant":
                    agent_data.final_response = str(message.get("content", "")).strip()
                    break
            else:
                agent_data.final_response = ""
            agent_data.status = "max_agent_turns_reached"
            return AgentState.TERMINATED

        current_prompt_len = len(agent_data.prompt_ids)
        # 如果 prompt 已经超过 response_length，直接终止
        if current_prompt_len >= self.response_length:
            agent_data.status = "prompt_length_exceeded"
            agent_data.final_response = agent_data.messages[-1].get("content", "") if agent_data.messages else ""
            return AgentState.TERMINATED
        sampling_params = dict(sampling_params)
        sampling_params.setdefault("max_tokens", self.response_length - current_prompt_len)
        sampling_params["max_tokens"] = max(1, sampling_params["max_tokens"])
        with simple_timer("generate_sequences", agent_data.metrics):
            output = await self.server_manager.generate(
                request_id=agent_data.request_id,
                prompt_ids=agent_data.prompt_ids,
                sampling_params=sampling_params,
                image_data=agent_data.image_data,
                video_data=agent_data.video_data,
            )

        agent_data.agent_turns += 1
        agent_data.response_ids = output.token_ids
        agent_data.prompt_ids += agent_data.response_ids
        agent_data.response_mask += [1] * len(agent_data.response_ids)
        if output.log_probs:
            agent_data.response_logprobs += output.log_probs

        assistant_message = await self.loop.run_in_executor(
            None,
            lambda: self.tokenizer.decode(agent_data.response_ids, skip_special_tokens=True),
        )
        agent_data.messages.append({"role": "assistant", "content": assistant_message})

        if len(agent_data.response_mask) >= self.response_length:
            agent_data.final_response = assistant_message.strip()
            agent_data.status = "response_length_reached"
            return AgentState.TERMINATED
        if self.max_user_turns and agent_data.next_step_index > self.max_user_turns:
            agent_data.final_response = assistant_message.strip()
            agent_data.status = "max_user_turns_reached"
            return AgentState.TERMINATED

        response = parse_response_json(assistant_message)
        if response is None or "need_tool_call" not in response:
            agent_data.error = f"invalid_format_recovered: {assistant_message[:100]}"
            agent_data.final_response = assistant_message.strip()
            if agent_data.next_step_index < len(agent_data.user_plan):
                return AgentState.APPENDING_USER_STEP
            agent_data.status = "invalid_format"
            return AgentState.TERMINATED

        if response.get("need_tool_call"):
            agent_data.pending_tool_calls = response.get("tool_call", [])
            return AgentState.PROCESSING_TOOLS

        agent_data.final_response = str(response.get("content", assistant_message.strip()))
        if agent_data.next_step_index < len(agent_data.user_plan):
            return AgentState.APPENDING_USER_STEP
        agent_data.status = "done"
        return AgentState.TERMINATED

    async def _handle_processing_tools_state(self, agent_data: AgentData) -> AgentState:
        with simple_timer("tool_calls", agent_data.metrics):
            feedback = self._execute_tool_calls(agent_data, agent_data.pending_tool_calls)

        add_messages = [{"role": "user", "content": feedback}]
        appended = await self._append_messages_to_prompt(agent_data, add_messages, mask_value=0)
        if not appended:
            agent_data.status = "response_length_reached"
            return AgentState.TERMINATED
        return AgentState.GENERATING

    async def _handle_appending_user_step_state(self, agent_data: AgentData) -> AgentState:
        appended = await self._append_next_user_step(agent_data)
        if appended:
            return AgentState.GENERATING
        agent_data.status = "done"
        return AgentState.TERMINATED

    @rollout_trace_op
    async def run(self, sampling_params: dict[str, Any], **kwargs) -> AgentLoopOutput:
        try:
            raw_messages = list(kwargs["raw_prompt"])
            multi_modal_data = await self.process_vision_info(raw_messages)
            images = multi_modal_data.get("images")
            videos = multi_modal_data.get("videos")
    
            extra_info = dict(kwargs.get("extra_info", {}) or {})
            passthrough_keys = (
                "meta",
                "user_plan",
                "task_id",
                "env_names",
                "init_env",
                "validation_protocol",
                "source_env_dir",
                "env_docs_file",
                "tool_docs_dir",
                "long_context",
            )
            for key in passthrough_keys:
                if key in kwargs and key not in extra_info:
                    extra_info[key] = kwargs[key]
            task_spec = self._extract_task_spec(extra_info)
            if not task_spec["source_env_dir"]:
                raise ValueError(
                    "Missing `source_env_dir`. Provide it in `extra_info['source_env_dir']`, "
                    "`rollout.agent.source_env_dir`, or `VERL_SOURCE_ENV_DIR`."
                )
    
            runtime = SourceEnvRuntime(
                env_configs={env_name: task_spec["init_env"].get(env_name, {}) for env_name in task_spec["env_names"]},
                source_env_dir=task_spec["source_env_dir"],
                long_context=task_spec["long_context"],
            )
    
            env_descriptions = self._load_env_descriptions(task_spec["env_names"], runtime, task_spec["env_docs_file"])
            tool_definitions = self._load_tool_definitions(task_spec["env_names"], runtime, task_spec["tool_docs_dir"])
            messages = self._prepare_initial_messages(
                raw_messages,
                task_spec["env_names"],
                # task_spec["init_env"],
                env_descriptions,
                tool_definitions,
            )
    
            next_step_index = infer_completed_plan_steps(messages, task_spec["user_plan"])
            agent_data = AgentData(
                messages=messages,
                image_data=images,
                video_data=videos,
                metrics={},
                request_id=uuid4().hex,
                runtime=runtime,
                env_names=task_spec["env_names"],
                init_env=task_spec["init_env"],
                user_plan=task_spec["user_plan"],
                next_step_index=next_step_index,
                validation_protocol=task_spec["validation_protocol"],
                task_id=task_spec["task_id"],
            )
    
            if agent_data.user_plan and next_step_index == 0:
                step = agent_data.user_plan[0]
                agent_data.messages.append({"role": "user", "content": str(step.get("user_content", ""))})
                agent_data.next_step_index = 1
    
            state = AgentState.PENDING
            while state != AgentState.TERMINATED:
                if state == AgentState.PENDING:
                    state = await self._handle_pending_state(agent_data)
                elif state == AgentState.GENERATING:
                    state = await self._handle_generating_state(agent_data, sampling_params)
                elif state == AgentState.PROCESSING_TOOLS:
                    state = await self._handle_processing_tools_state(agent_data)
                elif state == AgentState.APPENDING_USER_STEP:
                    state = await self._handle_appending_user_step_state(agent_data)
                else:
                    raise ValueError(f"Invalid state: {state}")
    
            # --- 精准保护：防止状态获取崩溃，同时保留模型运行轨迹 ---
            try:
                env_final_state = to_jsonable(agent_data.runtime.get_state())
                agent_data.validation_result = self._run_validation_protocol(
                    agent_data.validation_protocol, env_final_state,
                    agent_data.execution_trace, agent_data.final_response,
                )
                agent_data.is_success = bool(agent_data.validation_result.get("success", False))
            except Exception as env_exc:
                logger.error(f"Environment state/validation failed: {env_exc}")
                env_final_state = {"error": f"Env failed: {type(env_exc).__name__}"}
                agent_data.error = f"env_crash: {type(env_exc).__name__}"
                agent_data.validation_result = {"success": False, "reason": str(env_exc)}
            # --------------------------------------------------------
    
            response_ids = agent_data.prompt_ids[-len(agent_data.response_mask) :]
            prompt_ids = agent_data.prompt_ids[: len(agent_data.prompt_ids) - len(agent_data.response_mask)]
            output_multi_modal_data = {}
            if agent_data.image_data is not None:
                output_multi_modal_data["images"] = agent_data.image_data
            if agent_data.video_data is not None:
                output_multi_modal_data["videos"] = agent_data.video_data
    
            output = AgentLoopOutput(
                prompt_ids=prompt_ids,
                response_ids=response_ids[: self.response_length],
                response_mask=agent_data.response_mask[: self.response_length],
                multi_modal_data=output_multi_modal_data,
                response_logprobs=agent_data.response_logprobs[: self.response_length]
                if agent_data.response_logprobs
                else None,
                reward_score=(
                    (1.0 if agent_data.is_success else 0.0)
                    if self.use_validation_reward and agent_data.validation_result.get("success") is not None
                    else None
                ),
                num_turns=count_non_system_turns(agent_data.messages),
                metrics=agent_data.metrics,
                extra_fields={
                    "is_success": agent_data.is_success,
                    "task_id": agent_data.task_id,
                    "task_status": agent_data.status,
                    "task_error": agent_data.error,
                    "agent_turns": agent_data.agent_turns,
                    "user_plan": to_jsonable(agent_data.user_plan),
                    "messages": to_jsonable(agent_data.messages),
                    "final_response": agent_data.final_response,
                    "validation_result": to_jsonable(agent_data.validation_result),
                    "execution_trace": to_jsonable(agent_data.execution_trace),
                    "env_final_state": env_final_state,
                    "env_names": list(agent_data.env_names),
                },
            )
            return output
        except Exception as exc:
            # 终极安全网：只处理那些连上面代码都没拦住的致命崩溃（比如 OOM、JSON解析彻底失败等）
            logger.critical(f"Unhandled critical error in agent loop: {exc}", exc_info=True)
            return AgentLoopOutput(
                prompt_ids=[0], 
                response_ids=[],
                response_mask=[],
                multi_modal_data={},      # 补充缺失字段，防止 TypeError
                response_logprobs=None,   # 补充缺失字段，防止 TypeError
                reward_score=0.0,
                num_turns=0,
                metrics={},
                extra_fields={"is_success": False, "task_error": f"critical_crash: {type(exc).__name__}"}
            )