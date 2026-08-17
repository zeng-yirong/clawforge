from __future__ import annotations

from pathlib import Path

try:
    from nanoclaw_recipe.common import discover_tasks as _discover_common_tasks
except Exception as import_error:  # pragma: no cover - startup/config error path
    _discover_common_tasks = None
    _COMMON_IMPORT_ERROR = import_error
else:
    _COMMON_IMPORT_ERROR = None

from .types import TaskSpec


def discover_tasks(base_tasks: Path, *, task_glob: str, task_ids: set[str] | None) -> list[TaskSpec]:
    if _discover_common_tasks is None:
        raise ImportError(
            "vllm_nanoclaw_runtime now reuses nanoclaw_recipe.common from the VERL Nanoclaw tree. "
            "Add the verl_0720_main/verl root to PYTHONPATH or set WORK_DIR to that repo."
        ) from _COMMON_IMPORT_ERROR

    common_specs = _discover_common_tasks(base_tasks, task_glob=task_glob, task_ids=task_ids)
    return [
        TaskSpec(
            task_id=spec.task_id,
            base_tasks=spec.base_tasks,
            task_dir=spec.task_dir,
            prompt_path=spec.prompt_path,
            env_builder_path=spec.env_builder_path,
            verifier_path=spec.verifier_path,
            input_layout=getattr(spec, "input_layout", "legacy"),
            manifest_path=getattr(spec, "manifest_path", None),
        )
        for spec in common_specs
    ]
