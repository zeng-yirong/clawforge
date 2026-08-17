from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class NanoclawTaskSpec:
    task_id: str
    base_tasks: Path
    task_dir: Path
    prompt_path: Path
    env_builder_path: Path
    verifier_path: Path | None
    input_layout: str = "legacy"
    manifest_path: Path | None = None


def normalize_task_ids(raw_task_ids: Any) -> set[str] | None:
    if raw_task_ids is None or raw_task_ids == "":
        return None
    if isinstance(raw_task_ids, str):
        task_ids = [item.strip() for item in raw_task_ids.split(",")]
    else:
        task_ids = [str(item).strip() for item in raw_task_ids]
    task_ids = [task_id for task_id in task_ids if task_id]
    return set(task_ids) if task_ids else None


def safe_name(raw_name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_name).strip("._")
    return safe or "task"


def discover_tasks(base_tasks: Path, *, task_glob: str, task_ids: set[str] | None) -> list[NanoclawTaskSpec]:
    tasks_root = base_tasks / "tasks"
    if tasks_root.is_dir():
        return discover_legacy_tasks(base_tasks, tasks_root=tasks_root, task_glob=task_glob, task_ids=task_ids)
    return discover_flat_tasks(base_tasks, task_glob=task_glob, task_ids=task_ids)


def discover_legacy_tasks(
    base_tasks: Path, *, tasks_root: Path, task_glob: str, task_ids: set[str] | None
) -> list[NanoclawTaskSpec]:
    script_root = find_script_root(base_tasks)
    specs: list[NanoclawTaskSpec] = []
    for task_dir in sorted(path for path in tasks_root.glob(task_glob) if path.is_dir()):
        task_id = task_dir.name
        if task_ids is not None and task_id not in task_ids:
            continue

        env_builder_path = task_dir / "env_builder.py"
        if not env_builder_path.is_file():
            continue

        prompt_path = find_prompt_path(tasks_root, task_dir, task_id)
        verifier_path = find_verifier_path(script_root, task_id) if script_root is not None else None
        specs.append(
            NanoclawTaskSpec(
                task_id=task_id,
                base_tasks=base_tasks,
                task_dir=task_dir,
                prompt_path=prompt_path,
                env_builder_path=env_builder_path,
                verifier_path=verifier_path,
                input_layout="legacy",
            )
        )

    if task_ids is not None:
        found_task_ids = {spec.task_id for spec in specs}
        missing_task_ids = sorted(task_ids - found_task_ids)
        if missing_task_ids:
            raise FileNotFoundError(f"requested task ids not found or missing env_builder.py: {missing_task_ids}")
    if not specs:
        raise FileNotFoundError(f"no task directories matched {task_glob!r} under {tasks_root}")
    return specs


def discover_flat_tasks(base_tasks: Path, *, task_glob: str, task_ids: set[str] | None) -> list[NanoclawTaskSpec]:
    if not base_tasks.is_dir():
        raise FileNotFoundError(f"Nanoclaw data directory not found: {base_tasks}")

    if (base_tasks / "env_builder.py").is_file():
        task_dirs = [base_tasks]
    else:
        task_dirs = sorted(path for path in base_tasks.glob(task_glob) if path.is_dir())

    specs: list[NanoclawTaskSpec] = []
    for task_dir in task_dirs:
        manifest_files, manifest_path, manifest_task_id = read_manifest(task_dir)
        task_id = manifest_task_id or task_dir.name
        if task_ids is not None and task_id not in task_ids:
            continue

        env_builder_path = resolve_manifest_file(task_dir, manifest_files, "env_builder") or task_dir / "env_builder.py"
        if not env_builder_path.is_file():
            continue

        prompt_path = find_prompt_path(base_tasks, task_dir, task_id, manifest_files=manifest_files)
        verifier_path = find_verifier_path(None, task_id, task_dir=task_dir, manifest_files=manifest_files)
        specs.append(
            NanoclawTaskSpec(
                task_id=task_id,
                base_tasks=base_tasks,
                task_dir=task_dir,
                prompt_path=prompt_path,
                env_builder_path=env_builder_path,
                verifier_path=verifier_path,
                input_layout="flat",
                manifest_path=manifest_path,
            )
        )

    if task_ids is not None:
        found_task_ids = {spec.task_id for spec in specs}
        missing_task_ids = sorted(task_ids - found_task_ids)
        if missing_task_ids:
            raise FileNotFoundError(f"requested task ids not found or missing env_builder.py: {missing_task_ids}")
    if not specs:
        raise FileNotFoundError(f"no flat Nanoclaw task directories matched {task_glob!r} under {base_tasks}")
    return specs


def read_manifest(task_dir: Path) -> tuple[dict[str, str], Path | None, str | None]:
    manifest_path = task_dir / "manifest.json"
    if not manifest_path.is_file():
        return {}, None, None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as manifest_exc:
        raise ValueError(f"failed to read Nanoclaw manifest {manifest_path}: {manifest_exc}") from manifest_exc

    files = manifest.get("files") if isinstance(manifest, dict) else None
    manifest_files = {str(key): str(value) for key, value in files.items()} if isinstance(files, dict) else {}
    task_id = manifest.get("task_id") if isinstance(manifest, dict) else None
    return manifest_files, manifest_path, str(task_id) if task_id else None


def resolve_manifest_file(task_dir: Path, manifest_files: dict[str, str] | None, key: str) -> Path | None:
    if not manifest_files:
        return None
    relative_path = manifest_files.get(key)
    if not relative_path:
        return None
    candidate = (task_dir / relative_path).expanduser()
    return candidate if candidate.is_file() else None


TASK_BUNDLE_IGNORE = shutil.ignore_patterns(
    "workspace_before",
    "workspace_after",
    "workplace_before",
    "workplace_after",
    "__pycache__",
    ".runner_home",
    ".runner_tmp",
    ".nanoclaw_python_patch",
)


def copy_task_bundle(task_config: dict[str, Any], result_dir: Path) -> None:
    task_dir_value = task_config.get("task_dir")
    if task_dir_value:
        task_dir = Path(str(task_dir_value)).expanduser().resolve()
        if task_dir.is_dir():
            for child in sorted(task_dir.iterdir()):
                if child.name in {"workspace_before", "workspace_after", "workplace_before", "workplace_after", "__pycache__"}:
                    continue
                destination = result_dir / child.name
                if child.is_dir():
                    shutil.copytree(child, destination, ignore=TASK_BUNDLE_IGNORE, dirs_exist_ok=True)
                elif child.is_file():
                    shutil.copy2(child, destination)

    # Keep the original task bundle layout to avoid duplicate aliases such as
    # prompts.md + task_prompt.md or workplace_verifier.py + verify_workplace.py.
    # Only copy files that have stable canonical names and may live outside task_dir
    # in legacy layouts.
    named_files = {
        "env_builder.py": task_config.get("env_builder_path"),
        "manifest.json": task_config.get("manifest_path"),
    }
    for output_name, source_value in named_files.items():
        if not source_value:
            continue
        source_path = Path(str(source_value)).expanduser().resolve()
        if source_path.is_file():
            destination = result_dir / output_name
            if not destination.exists():
                shutil.copy2(source_path, destination)


def find_script_root(base_tasks: Path) -> Path | None:
    for dirname in ("scrips", "scripts"):
        candidate = base_tasks / dirname
        if candidate.is_dir():
            return candidate
    return None


def find_prompt_path(
    tasks_root: Path,
    task_dir: Path,
    task_id: str,
    *,
    manifest_files: dict[str, str] | None = None,
) -> Path:
    manifest_prompt = resolve_manifest_file(task_dir, manifest_files, "prompt")
    candidates = (
        manifest_prompt,
        tasks_root / "prompts" / f"{task_id}.md",
        task_dir / "prompts.md",
        task_dir / "prompt.md",
        task_dir / "task.md",
    )
    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"prompt file not found for {task_id}; tried: " + ", ".join(str(path) for path in candidates)
    )


def find_verifier_path(
    script_root: Path | None,
    task_id: str,
    *,
    task_dir: Path | None = None,
    manifest_files: dict[str, str] | None = None,
) -> Path | None:
    candidates: list[Path | None] = [resolve_manifest_file(task_dir, manifest_files, "verifier") if task_dir else None]
    if task_dir is not None:
        candidates.extend((task_dir / "workplace_verifier.py", task_dir / "verify_workplace.py"))
    if script_root is not None:
        candidates.extend(
            (
                script_root / task_id / "verify_workplace.py",
                script_root / f"{task_id}.py",
                script_root / "verify_workplace.py",
            )
        )
    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            return candidate
    return None


def score_summary(workplace_score: Any) -> dict[str, Any]:
    if not isinstance(workplace_score, dict):
        return {"score": None, "max_score": None, "score_ratio": None, "passed": None}

    score = workplace_score.get("total_score", workplace_score.get("score"))
    max_score = workplace_score.get("max_score")
    if isinstance(workplace_score.get("details"), list):
        detail_scores = [item.get("score") for item in workplace_score["details"] if isinstance(item, dict)]
        detail_maxes = [item.get("max_score") for item in workplace_score["details"] if isinstance(item, dict)]
        numeric_scores = [value for value in detail_scores if isinstance(value, (int, float))]
        numeric_maxes = [value for value in detail_maxes if isinstance(value, (int, float))]
        if score is None and numeric_scores:
            score = sum(numeric_scores)
        if max_score is None and numeric_maxes:
            max_score = sum(numeric_maxes)
    ratio = None
    if isinstance(score, (int, float)) and isinstance(max_score, (int, float)) and max_score:
        ratio = score / max_score
    passed = workplace_score.get("passed")
    if passed is None and ratio is not None:
        passed = ratio >= 0.999
    return {"score": score, "max_score": max_score, "score_ratio": ratio, "passed": passed}
