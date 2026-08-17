# ruff: noqa: E501
"""Native Dataset for claw WORKPLACE + CLI training.
This adapter lets verl train from claw task directories or JSON/JSONL manifests
without converting them to parquet first. It intentionally keeps the reward
model per-sample: every train item points at its own ``verify_workplace.py``.
Supported input shapes:
1. WORKPLACE task directory, e.g. ``claw_envs/claw_chains/example_tasks``::
       tasks/prompts/<task_id>.md
       tasks/<task_id>/env_builder.py
       scripts/<task_id>/verify_workplace.py
2. JSON/JSONL manifest records with either a complete verl-style ``prompt`` and
   ``extra_info`` row, or enough claw fields to build one:
       task_id, env_name, prompt_path, env_builder, verify_script
Chain-only records from ``claw_chains_out/*.jsonl`` are not directly scoreable:
they have CLI traces, but no prompt/env_builder/verifier. By default this
dataset raises on those records so an RL run cannot silently train unscored
samples. Use a manifest that maps each chain to a WORKPLACE verifier.
"""

from __future__ import annotations

import copy
import json
import logging
import random
import re
from pathlib import Path
from typing import Any, Iterable

import torch
from torch.utils.data import Dataset

try:
    from omegaconf import DictConfig, ListConfig
except ModuleNotFoundError:  # keep this adapter importable outside a verl env
    class DictConfig(dict):  # type: ignore[no-redef]
        pass

    ListConfig = list  # type: ignore[assignment, no-redef]

logger = logging.getLogger(__name__)

TASK_ID_RE = re.compile(r"^wp_(?P<env>.+)__(?P<idx>\d+)$")
SAFE_SLUG_RE = re.compile(r"[^A-Za-z0-9_]+")

DEFAULT_TASKS_DIR = "claw_envs/claw_chains/example_tasks"
DEFAULT_CLAW_TOOL_DOCS_DIR = "claw_envs/claw_chains/claw_tool_env_docs"


SYSTEM_PROMPT_BASE = """
You are an AI assistant executing tasks inside a sandboxed WORKPLACE directory. All user paths are relative to this directory. 

Produce exactly the requested artifact(s), then call `finish`.

### Tool Selection
- **File Tools:** Use `read`, `write`, `edit`, `str_replace_editor` for direct file inspection and modification.
- **execute_bash:** Use ONLY for basic file management (`ls`, `cd`, `find`, `grep`, `mkdir`, `cp`). **STRONGLY PREFER Python (`python -c` or `.py` scripts) for any logic requiring loops, conditionals, or data parsing.** Bash control flows (`while`, `for`, `if`) and advanced processors (`awk`, `jq`, `xargs`) are blocked.

### Strict Sandbox Restrictions
1. **Path Containment:** You MUST operate strictly within the WORKPLACE. 
   - FORBIDDEN: Absolute paths, `..`, symlinks, or accessing hidden session directories.
2. **Bash Execution Rules:**
   - ALLOWED: Linear commands, piping (`|`), logical combinations (`&&`, `||`, `;`), and workspace-relative redirection (`>`, `<`).
   - FORBIDDEN: Shell control flow (`while`, `for`, `if`), text processors (`awk`, `jq`), `xargs`, subshells, command substitution, background jobs (`&`), deletion/moving (`rm`, `mv`), and destructive `find` predicates.
3. **Python Execution Rules (The Preferred Method):**
   - ALLOWED: Multi-line `python -c "<code string>"`, existing `.py` scripts, or `python -m <module>`. 
   - DO NOT try to compress complex loops and conditionals into a single line with semicolons. Use standard newlines (\n) and indentation inside the string.
   - Python is your primary tool for complex data processing. Files accessed inside Python must use literal, workspace-relative paths. Arbitrary executables and uninspectable modules are blocked.
4. **Environment Integrity:** Do NOT manage, reset, or create rollout sessions (e.g., `prepare-rollout`).
""".strip()


WITHOUT_SKILL_HEADER = """
## Environment CLI Reference
The following CLI commands are available through `execute_bash`.
""".strip()


SKILL_PATH_HEADER = """
## Environment Skill
This environment has a SKILL.md reference. Before using the environment CLI, read it with the `read` tool:
""".strip()


INLINE_SKILL_HEADER = """
## Environment Skill Reference
The following environment skill is reference material for how to use the CLI:
""".strip()


def _config_get(config: DictConfig | dict | None, key: str, default: Any = None) -> Any:
    if config is None:
        return default
    if hasattr(config, "get"):
        return config.get(key, default)
    return getattr(config, key, default)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, ListConfig)):
        return list(value)
    return [value]


def _q(value: str | Path) -> str:
    text = str(value).replace("\\", "/")
    return "'" + text.replace("'", "'\\''") + "'"


def _safe_slug(value: str) -> str:
    slug = SAFE_SLUG_RE.sub("_", value).strip("_")
    return slug or "claw"


def _repo_cli_module(cli_module: str) -> str:
    """Return a module path that works from the uni-agent repo root."""
    cli_module = cli_module.strip()
    if cli_module.startswith("claw_envs."):
        return cli_module
    return f"claw_envs.{cli_module}"


def _parse_env_from_task_id(task_id: str) -> str:
    match = TASK_ID_RE.match(task_id)
    if match:
        return match.group("env")
    return "unknown"


def _strip_frontmatter(text: str) -> str:
    stripped = text.lstrip()
    if stripped.startswith("---"):
        end = stripped.find("\n---", 3)
        if end != -1:
            return stripped[end + 4 :].lstrip("\n")
    return text


class ClawNativeDataset(Dataset):
    """verl-compatible Dataset that reads claw data without parquet.
    Constructor signature matches verl's ``create_rl_dataset``:
    ``dataset_cls(data_files, tokenizer, processor, config, max_samples)``
    Important config keys:
    - ``claw_repo_root``: uni-agent repo root on the training host. Defaults to
      this file's repo.
    - ``claw_format`` or ``claw_formats``: ``without_skill`` / ``skill`` /
      ``both``. Default ``without_skill``.
    - ``claw_include_cli``: prepare and document the env CLI. Default ``true``.
    - ``claw_tool_docs_dir``: directory containing ``<env>.json`` CLI docs.
    - ``claw_skill_mode``: ``path`` (default) or ``inline`` for skill format.
    - ``claw_chain_only_policy``: ``error`` (default) or ``skip`` for
      ``claw_chains_out`` records that lack verifier/workspace files.
    """

    def __init__(
        self,
        data_files: str | list[str],
        tokenizer: Any,
        config: DictConfig | dict,
        processor: Any | None = None,
        max_samples: int = -1,
    ):
        self.data_files = [str(p) for p in _as_list(data_files)]
        self.original_data_files = copy.deepcopy(self.data_files)
        self.tokenizer = tokenizer
        self.processor = processor
        self.config = config
        self.max_samples = max_samples

        self.repo_root = self._resolve_repo_root()
        self.prompt_key = _config_get(config, "prompt_key", "prompt")
        self.max_prompt_length = int(_config_get(config, "max_prompt_length", 1024))
        self.filter_overlong_prompts = bool(_config_get(config, "filter_overlong_prompts", True))
        self.apply_chat_template_kwargs = dict(_config_get(config, "apply_chat_template_kwargs", {}) or {})
        self.shuffle = bool(_config_get(config, "shuffle", False))
        self.seed = _config_get(config, "seed", None)
        self.need_tools_kwargs = bool(_config_get(config, "need_tools_kwargs", True))
        self.agent_name = str(_config_get(config, "claw_agent_name", _config_get(config, "agent_name", "swe_agent")))

        self.include_cli = bool(_config_get(config, "claw_include_cli", True))
        self.restrict_workspace = bool(_config_get(config, "claw_restrict_workspace", True))
        self.restrict_bash = bool(_config_get(config, "claw_restrict_bash", True))
        self.tool_docs_dir = self._resolve_path(
            _config_get(config, "claw_tool_docs_dir", DEFAULT_CLAW_TOOL_DOCS_DIR)
        )
        self.skill_mode = str(_config_get(config, "claw_skill_mode", "path"))
        self.chain_only_policy = str(_config_get(config, "claw_chain_only_policy", "error"))
        self.max_cli_verbs = int(_config_get(config, "claw_max_cli_verbs", 80))

        self.env_filter = set(str(v) for v in _as_list(_config_get(config, "claw_envs", None)))
        self.task_filter = set(str(v) for v in _as_list(_config_get(config, "claw_task_ids", None)))
        self.eval_timeout = float(_config_get(config, "claw_eval_timeout", 300))

        self.samples: list[dict[str, Any]] = []
        self._read_files_and_tokenize()

    def _resolve_repo_root(self) -> Path:
        configured = _config_get(self.config, "claw_repo_root", None) or _config_get(self.config, "repo_root", None)
        if configured:
            return Path(str(configured)).expanduser().resolve()
        return Path(__file__).resolve().parents[2]

    def _resolve_path(self, path_like: str | Path) -> Path:
        path = Path(str(path_like)).expanduser()
        if path.is_absolute():
            return path.resolve()
        return (self.repo_root / path).resolve()

    def _formats(self) -> list[str]:
        raw = _config_get(self.config, "claw_formats", None)
        if raw is None:
            raw = _config_get(self.config, "claw_format", "without_skill")
        formats: list[str] = []
        for item in _as_list(raw):
            fmt = str(item)
            if fmt in {"both", "mixed"}:
                formats.extend(["without_skill", "skill"])
            else:
                formats.append(fmt)
        invalid = [fmt for fmt in formats if fmt not in {"without_skill", "skill"}]
        if invalid:
            raise ValueError(f"Unsupported claw format(s): {invalid}. Use without_skill, skill, or both.")
        return formats or ["without_skill"]

    def _read_files_and_tokenize(self) -> None:
        specs = self._load_specs()
        samples: list[dict[str, Any]] = []
        for spec in specs:
            if self.env_filter and spec["env_name"] not in self.env_filter:
                continue
            if self.task_filter and spec["task_id"] not in self.task_filter:
                continue
            if self._is_full_row(spec):
                samples.append(self._normalize_full_row(spec))
                continue
            for fmt in self._formats():
                samples.append(self._build_sample(spec, fmt))

        for idx, sample in enumerate(samples):
            extra_info = sample.setdefault("extra_info", {})
            extra_info.setdefault("index", idx)
            sample.setdefault("index", idx)

        if self.shuffle:
            rng = random.Random(self.seed)
            rng.shuffle(samples)

        if self.max_samples and self.max_samples > 0:
            samples = samples[: self.max_samples]

        self.samples = self._maybe_filter_out_long_prompts(samples)
        if not self.samples:
            raise ValueError("ClawNativeDataset produced zero samples. Check data_files, filters, and manifest format.")
        logger.info("Loaded %d claw native sample(s)", len(self.samples))

    def _load_specs(self) -> list[dict[str, Any]]:
        paths = self.data_files or [DEFAULT_TASKS_DIR]
        specs: list[dict[str, Any]] = []
        chain_only_errors: list[str] = []
        for raw_path in paths:
            path = self._resolve_path(raw_path)
            if path.is_dir():
                specs.extend(self._discover_workplace_tasks(path))
            elif path.is_file() and path.suffix.lower() in {".jsonl", ".json"}:
                loaded, chain_only = self._load_manifest(path)
                specs.extend(loaded)
                chain_only_errors.extend(chain_only)
            else:
                raise ValueError(
                    f"Unsupported claw data path: {path}. Expected an example_tasks-style directory, JSON, or JSONL."
                )

        if chain_only_errors and self.chain_only_policy == "error":
            example = chain_only_errors[0]
            raise ValueError(
                "Found chain-only claw record(s) without prompt/env_builder/verify_workplace.py. "
                "These records are useful as traces but are not directly scoreable for RL. "
                "Create a manifest that maps each record to a WORKPLACE task verifier, or set "
                "`data.claw_chain_only_policy=skip`. First offending source: "
                f"{example}"
            )
        if chain_only_errors:
            logger.warning("Skipped %d chain-only claw record(s)", len(chain_only_errors))
        return specs

    def _discover_workplace_tasks(self, tasks_dir: Path) -> list[dict[str, Any]]:
        prompts_dir = tasks_dir / "tasks" / "prompts"
        if not prompts_dir.is_dir():
            raise FileNotFoundError(f"No WORKPLACE prompts dir under {tasks_dir}: {prompts_dir}")

        specs: list[dict[str, Any]] = []
        for prompt_path in sorted(prompts_dir.glob("*.md")):
            task_id = prompt_path.stem
            env_builder = tasks_dir / "tasks" / task_id / "env_builder.py"
            verifier = tasks_dir / "scripts" / task_id / "verify_workplace.py"
            if not env_builder.is_file() or not verifier.is_file():
                logger.warning("Skipping %s: missing env_builder.py or verify_workplace.py", task_id)
                continue
            env_name = _parse_env_from_task_id(task_id)
            specs.append(
                {
                    "kind": "workplace",
                    "task_id": task_id,
                    "env_name": env_name,
                    "prompt_path": prompt_path,
                    "env_builder": env_builder,
                    "verify_script": verifier,
                    "source": str(tasks_dir),
                }
            )
        return specs

    def _load_manifest(self, path: Path) -> tuple[list[dict[str, Any]], list[str]]:
        records = list(self._iter_json_records(path))
        specs: list[dict[str, Any]] = []
        chain_only: list[str] = []
        for idx, record in enumerate(records):
            source = f"{path}:{idx + 1}"
            if self._is_full_row(record):
                row = copy.deepcopy(record)
                row.setdefault("source", source)
                specs.append(row)
                continue
            if self._is_chain_only_record(record):
                chain_only.append(source)
                continue
            specs.append(self._record_to_spec(record, source))
        return specs, chain_only

    def _iter_json_records(self, path: Path) -> Iterable[dict[str, Any]]:
        if path.suffix.lower() == ".jsonl":
            with path.open("r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"Invalid JSON at {path}:{line_no}: {exc}") from exc
                    if not isinstance(obj, dict):
                        raise ValueError(f"Expected JSON object at {path}:{line_no}, got {type(obj).__name__}")
                    yield obj
            return

        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, dict) and "samples" in obj:
            obj = obj["samples"]
        if isinstance(obj, dict):
            yield obj
            return
        if not isinstance(obj, list):
            raise ValueError(f"Expected JSON object/list in {path}, got {type(obj).__name__}")
        for idx, item in enumerate(obj):
            if not isinstance(item, dict):
                raise ValueError(f"Expected JSON object in {path}[{idx}], got {type(item).__name__}")
            yield item

    def _is_full_row(self, record: dict[str, Any]) -> bool:
        return self.prompt_key in record and isinstance(record.get("extra_info"), dict)

    def _normalize_full_row(self, row: dict[str, Any]) -> dict[str, Any]:
        sample = copy.deepcopy(row)
        sample.setdefault("agent_name", self.agent_name)
        sample.setdefault("data_source", sample.get("extra_info", {}).get("data_source", "claw_envs:native"))
        extra_info = sample.setdefault("extra_info", {})
        extra_info.setdefault("data_source", sample["data_source"])
        extra_info.setdefault("need_tools_kwargs", self.need_tools_kwargs)
        return sample

    def _is_chain_only_record(self, record: dict[str, Any]) -> bool:
        has_chain = "chain" in record or "gold_actions" in record
        has_workspace = any(k in record for k in ("env_builder", "env_builder_path", "verify_script", "verifier"))
        has_prompt = any(k in record for k in ("prompt", "prompt_path", "user_prompt"))
        return bool(has_chain and not has_workspace and not has_prompt)

    def _record_to_spec(self, record: dict[str, Any], source: str) -> dict[str, Any]:
        task_id = str(record.get("task_id") or record.get("id") or "")
        env_name = str(record.get("env_name") or (_parse_env_from_task_id(task_id) if task_id else "unknown"))

        prompt_path = record.get("prompt_path")
        env_builder = record.get("env_builder") or record.get("env_builder_path")
        verify_script = record.get("verify_script") or record.get("verifier") or record.get("verify_path")

        tasks_dir = record.get("tasks_dir") or _config_get(self.config, "claw_tasks_dir", None)
        if task_id and (not prompt_path or not env_builder or not verify_script):
            base = self._resolve_path(tasks_dir or DEFAULT_TASKS_DIR)
            prompt_path = prompt_path or str(base / "tasks" / "prompts" / f"{task_id}.md")
            env_builder = env_builder or str(base / "tasks" / task_id / "env_builder.py")
            verify_script = verify_script or str(base / "scripts" / task_id / "verify_workplace.py")

        if not task_id and prompt_path:
            task_id = Path(str(prompt_path)).stem
            env_name = env_name if env_name != "unknown" else _parse_env_from_task_id(task_id)

        missing = [
            name
            for name, value in (
                ("task_id", task_id),
                ("env_name", env_name if env_name != "unknown" else None),
                ("prompt_path/user_prompt/prompt", prompt_path or record.get("user_prompt") or record.get("prompt")),
                ("env_builder", env_builder),
                ("verify_script", verify_script),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"Manifest record {source} is missing required claw fields: {missing}")

        spec = {
            "kind": "workplace",
            "task_id": task_id,
            "env_name": env_name,
            "prompt_path": self._resolve_path(prompt_path) if prompt_path else None,
            "env_builder": self._resolve_path(env_builder),
            "verify_script": self._resolve_path(verify_script),
            "scenario_id": record.get("scenario_id"),
            "source": source,
        }
        if "user_prompt" in record:
            spec["user_prompt"] = str(record["user_prompt"])
        elif "prompt" in record and isinstance(record["prompt"], str):
            spec["user_prompt"] = str(record["prompt"])
        return spec

    def _build_sample(self, spec: dict[str, Any], fmt: str) -> dict[str, Any]:
        prompt_text = self._prompt_text(spec)
        cli_docs = self._load_cli_docs(spec["env_name"]) if self.include_cli else None
        scenario_id = self._resolve_scenario_id(spec, cli_docs)
        system_prompt = self._build_system_prompt(spec, fmt, cli_docs, scenario_id)
        tools_kwargs = {
            "env": {
                "post_setup_cmd": self._build_post_setup_cmd(spec, cli_docs, scenario_id),
                "restrict_workspace": self.restrict_workspace,
                "workspace_env_var": "CLAW_WORKSPACE",
                "restrict_bash_commands": self.restrict_bash,
                "allowed_bash_command_prefixes": self._allowed_cli_prefixes(cli_docs),
            },
            "reward": {
                "name": "claw",
                "verify_script": Path(spec["verify_script"]).as_posix(),
                "workspace_env_var": "CLAW_WORKSPACE",
                "eval_timeout": self.eval_timeout,
                "metadata": {
                    "env_name": spec["env_name"],
                    "task_id": spec["task_id"],
                    "format": fmt,
                    "include_cli": self.include_cli,
                    "scenario_id": scenario_id,
                    "source": spec.get("source"),
                },
            },
        }

        data_source = f"claw_envs:{spec['env_name']}"
        return {
            "prompt": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text},
            ],
            "agent_name": self.agent_name,
            "data_source": data_source,
            "extra_info": {
                "task_id": spec["task_id"],
                "env_name": spec["env_name"],
                "data_source": data_source,
                "format": fmt,
                "scenario_id": scenario_id,
                "need_tools_kwargs": self.need_tools_kwargs,
                "tools_kwargs": tools_kwargs,
            },
        }

    def _prompt_text(self, spec: dict[str, Any]) -> str:
        if spec.get("user_prompt") is not None:
            return str(spec["user_prompt"]).strip()
        prompt_path = spec.get("prompt_path")
        if not prompt_path:
            raise ValueError(f"No prompt_path/user_prompt for task {spec.get('task_id')}")
        return Path(prompt_path).read_text(encoding="utf-8", errors="replace").strip()

    def _load_cli_docs(self, env_name: str) -> dict[str, Any]:
        path = self.tool_docs_dir / f"{env_name}.json"
        if not path.is_file():
            raise FileNotFoundError(
                f"CLI docs for env {env_name!r} not found at {path}. "
                "Set data.claw_include_cli=false for file-only WORKPLACE training, or provide data.claw_tool_docs_dir."
            )
        return json.loads(path.read_text(encoding="utf-8"))

    def _default_scenario_id(self, cli_docs: dict[str, Any] | None) -> str | None:
        if not cli_docs:
            return None
        bindings = cli_docs.get("bindings") or {}
        default_scenario = bindings.get("default_scenario_id")
        if default_scenario:
            return str(default_scenario)
        scenario_ids = [str(v) for v in (cli_docs.get("scenario_ids") or []) if str(v)]
        return scenario_ids[0] if scenario_ids else None

    def _resolve_scenario_id(self, spec: dict[str, Any], cli_docs: dict[str, Any] | None) -> str | None:
        scenario_id = spec.get("scenario_id") or self._default_scenario_id(cli_docs)
        if not scenario_id or not cli_docs:
            return str(scenario_id) if scenario_id else None

        valid_ids = [str(v) for v in (cli_docs.get("scenario_ids") or []) if str(v)]
        if not valid_ids or str(scenario_id) in valid_ids:
            return str(scenario_id)

        if len(valid_ids) == 1:
            fallback = valid_ids[0]
            logger.warning(
                "Scenario %s for task %s/env %s is not in CLI docs; falling back to the only available scenario %s",
                scenario_id,
                spec.get("task_id"),
                spec.get("env_name"),
                fallback,
            )
            return fallback

        raise ValueError(
            f"Scenario {scenario_id!r} for task {spec.get('task_id')} / env {spec.get('env_name')} "
            f"is not available. Valid scenario_ids: {valid_ids}"
        )

    def _build_system_prompt(
        self,
        spec: dict[str, Any],
        fmt: str,
        cli_docs: dict[str, Any] | None,
        scenario_id: str | None,
    ) -> str:
        parts = [SYSTEM_PROMPT_BASE]
        if not self.include_cli or not cli_docs:
            return "\n\n".join(parts)

        skill_path = self._skill_path_for_env(spec["env_name"])
        if fmt == "skill" and skill_path and self.skill_mode == "inline":
            skill_body = _strip_frontmatter(skill_path.read_text(encoding="utf-8", errors="replace")).strip()
            parts.append(f"{INLINE_SKILL_HEADER}\n\n{skill_body}")
            parts.append(self._render_cli_reference(cli_docs, scenario_id, concise=True))
        elif fmt == "skill" and skill_path:
            parts.append(f"{SKILL_PATH_HEADER}\n\n`{skill_path.as_posix()}`")
            parts.append(self._render_cli_reference(cli_docs, scenario_id, concise=True))
        else:
            if fmt == "skill" and not skill_path:
                parts.append(
                    "This sample requested skill format, but the environment has no SKILL.md on disk. Use the CLI reference below."
                )
            parts.append(f"{WITHOUT_SKILL_HEADER}\n\n{self._render_cli_reference(cli_docs, scenario_id, concise=False)}")
        return "\n\n".join(parts)

    def _skill_path_for_env(self, env_name: str) -> Path | None:
        path = self.repo_root / "claw_envs" / env_name / "SKILL.md"
        return path if path.is_file() else None

    def _render_cli_reference(
        self,
        cli_docs: dict[str, Any],
        scenario_id: str | None,
        *,
        concise: bool,
    ) -> str:
        env_name = str(cli_docs.get("env_name") or "unknown")
        cli_module = _repo_cli_module(str(cli_docs.get("cli_module") or f"{env_name}.cli"))
        command_prefix = f"python -m {cli_module}"
        bindings = cli_docs.get("bindings") or {}

        lines = [
            f"Environment: `{env_name}`",
            f"Command prefix: `{command_prefix}`",
            "The rollout session is already prepared; do not run `prepare-rollout`, `reset-rollout`, or `create-session`.",
        ]
        if scenario_id:
            lines.append(f"Scenario id: `{scenario_id}`")

        session_env = bindings.get("session_env")
        state_env = bindings.get("state_env")
        scenario_env = bindings.get("scenario_env")
        env_vars = [v for v in (session_env, state_env, scenario_env) if v]
        if env_vars:
            lines.append("The trainer exports: " + ", ".join(f"`{v}`" for v in env_vars) + ".")
        lines.append(f"Start by inspecting the environment task if needed: `{command_prefix} task`.")

        if concise:
            return "\n".join(lines)

        visible_verbs = cli_docs.get("visible_verbs") or []
        if visible_verbs:
            lines.append("Available commands:")
        for verb_doc in visible_verbs[: self.max_cli_verbs]:
            verb = str(verb_doc.get("verb") or "")
            if not verb:
                continue
            help_text = str(verb_doc.get("help") or "").strip()
            args_text = self._render_cli_args(verb_doc.get("args") or [])
            line = f"- `{command_prefix} {verb}{args_text}`"
            if help_text:
                line += f": {help_text}"
            lines.append(line)
        if len(visible_verbs) > self.max_cli_verbs:
            lines.append(f"- ... {len(visible_verbs) - self.max_cli_verbs} more commands omitted; use `{command_prefix} --help`.")
        return "\n".join(lines)

    def _allowed_cli_prefixes(self, cli_docs: dict[str, Any] | None) -> list[str]:
        if not cli_docs:
            return []
        env_name = str(cli_docs.get("env_name") or "unknown")
        raw_module = str(cli_docs.get("cli_module") or f"{env_name}.cli")
        prefixes = [
            f"python -m {_repo_cli_module(raw_module)}",
        ]
        if not raw_module.startswith("claw_envs."):
            prefixes.append(f"python -m {raw_module}")
        return list(dict.fromkeys(prefixes))

    def _render_cli_args(self, args: list[dict[str, Any]]) -> str:
        rendered: list[str] = []
        for arg in args:
            if arg.get("hidden"):
                continue
            name = str(arg.get("name") or "").strip()
            if not name:
                continue
            type_name = str(arg.get("type") or "value")
            if type_name == "bool":
                token = name
            else:
                token = f"{name} <{type_name}>"
            if not arg.get("required"):
                token = f"[{token}]"
            rendered.append(token)
        return (" " + " ".join(rendered)) if rendered else ""

    def _build_post_setup_cmd(
        self,
        spec: dict[str, Any],
        cli_docs: dict[str, Any] | None,
        scenario_id: str | None,
    ) -> str:
        env_name = spec["env_name"]
        slug = _safe_slug(env_name)
        repo_root = self.repo_root.as_posix()
        env_builder = Path(spec["env_builder"]).as_posix()
        parts = [
            f"export CLAW_REPO_ROOT={_q(repo_root)}",
            'export PYTHONPATH="$CLAW_REPO_ROOT:$CLAW_REPO_ROOT/claw_envs:$PYTHONPATH"',
            f'export CLAW_WORKSPACE="$(mktemp -d -t claw_{slug}_XXXXXX)"',
            f"cp {_q(env_builder)} \"$CLAW_WORKSPACE/env_builder.py\"",
            'cd "$CLAW_WORKSPACE"',
            "python -m uni_agent.datasets.env_builder_runner env_builder.py",
        ]

        if self.include_cli and cli_docs:
            bindings = cli_docs.get("bindings") or {}
            session_env = bindings.get("session_env")
            state_env = bindings.get("state_env")
            scenario_env = bindings.get("scenario_env")
            missing = [name for name, value in (("session_env", session_env),) if not value]
            if missing:
                raise ValueError(f"CLI docs for {env_name} missing bindings: {missing}")
            cli_module = _repo_cli_module(str(cli_docs.get("cli_module") or f"{env_name}.cli"))
            scenario_spec = dict(spec)
            if scenario_id:
                scenario_spec["scenario_id"] = scenario_id
            scenario_id = self._resolve_scenario_id(scenario_spec, cli_docs)
            if not scenario_id:
                raise ValueError(f"No scenario_id/default_scenario_id for CLI env {env_name}")
            if state_env:
                parts.append(f'export {state_env}="$(mktemp -d -t claw_state_{slug}_XXXXXX)"')
            parts.append(f'export {session_env}="claw_{slug}_$(date +%s%N)_$RANDOM"')
            if scenario_env:
                parts.append(f"export {scenario_env}={_q(scenario_id)}")
                scenario_arg = f'"${{{scenario_env}}}"'
            else:
                scenario_arg = _q(scenario_id)
            parts.extend(
                [
                    (
                        f"python -m {cli_module} prepare-rollout "
                        f"--session-id \"${{{session_env}}}\" "
                        f"--scenario-id {scenario_arg}"
                    ),
                    'cd "$CLAW_WORKSPACE"',
                ]
            )
        return " && ".join(parts)

    def _maybe_filter_out_long_prompts(self, samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.filter_overlong_prompts or self.tokenizer is None:
            return samples
        kept: list[dict[str, Any]] = []
        for sample in samples:
            try:
                length = self._prompt_length(sample[self.prompt_key])
            except Exception:  # noqa: BLE001 - match verl's defensive filtering behavior
                logger.exception("Error tokenizing sample %s; dropping it", sample.get("extra_info", {}).get("task_id"))
                continue
            if length <= self.max_prompt_length:
                kept.append(sample)
            else:
                logger.warning(
                    "Dropping overlong claw prompt %s: %d > %d",
                    sample.get("extra_info", {}).get("task_id"),
                    length,
                    self.max_prompt_length,
                )
        return kept

    def _prompt_length(self, messages: list[dict[str, Any]]) -> int:
        raw = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            **self.apply_chat_template_kwargs,
        )
        if isinstance(raw, dict) and "input_ids" in raw:
            raw = raw["input_ids"]
        if isinstance(raw, str):
            if hasattr(self.tokenizer, "encode"):
                return len(self.tokenizer.encode(raw))
            return len(raw.split())
        if isinstance(raw, torch.Tensor):
            return int(raw.numel())
        return len(raw)

    def resume_dataset_state(self) -> None:
        self.data_files = copy.deepcopy(self.original_data_files)
        self._read_files_and_tokenize()

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, item: int) -> dict[str, Any]:
        row_dict = copy.deepcopy(self.samples[item])
        row_dict["raw_prompt"] = self._build_messages(row_dict)
        row_dict["dummy_tensor"] = torch.tensor([0], dtype=torch.uint8)

        if "extra_info" not in row_dict or row_dict["extra_info"] is None:
            row_dict["extra_info"] = {}
        extra_info = row_dict["extra_info"]
        index = extra_info.get("index", row_dict.get("index", item))
        tools_kwargs = extra_info.get("tools_kwargs", {})
        interaction_kwargs = extra_info.get("interaction_kwargs", {})
        need_tools_kwargs = extra_info.get("need_tools_kwargs", self.need_tools_kwargs)
        if need_tools_kwargs and not tools_kwargs:
            logger.warning("tools_kwargs is empty for index %s, data source: %s", index, row_dict.get("data_source"))

        row_dict["index"] = index
        row_dict["tools_kwargs"] = tools_kwargs
        row_dict["interaction_kwargs"] = interaction_kwargs
        row_dict.setdefault("agent_name", self.agent_name)
        row_dict.setdefault("data_source", extra_info.get("data_source", "claw_envs:native"))
        return row_dict

    def _build_messages(self, example: dict[str, Any]) -> list[dict[str, Any]]:
        if self.prompt_key not in example:
            raise KeyError(f"Prompt key `{self.prompt_key}` not found in claw sample.")
        messages = copy.deepcopy(example[self.prompt_key])
        if not isinstance(messages, list):
            raise TypeError(f"Expected `{self.prompt_key}` to be a list of chat messages, got {type(messages).__name__}")
        return messages
