from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any

import yaml


CLAW_BENCH_PRO_FORMAT = "clawbenchpro-training-compatible-v1"
ADAPTER_VERSION = 2
DEFAULT_DATASETS = ("round_01_aligned_mix_800", "persona_aligned_mix_200")


class MissingPromptError(FileNotFoundError):
    def __init__(self, missing_paths: list[Path]):
        self.missing_paths = missing_paths
        super().__init__("ClawBenchPro prompt files are missing: " + ", ".join(str(path) for path in missing_paths))


ADAPTED_ENV_BUILDER = '''from __future__ import annotations

import re
import runpy
import shutil
import sys
from pathlib import Path


def build_env() -> None:
    bundle_dir = Path(__file__).resolve().parent
    implementation = bundle_dir / "_env_builder_impl.py"
    if not implementation.is_file():
        raise FileNotFoundError(f"ClawBenchPro builder implementation is missing: {implementation}")

    implementation_dir = str(implementation.parent)
    inserted_path = implementation_dir not in sys.path
    if inserted_path:
        sys.path.insert(0, implementation_dir)
    try:
        namespace = runpy.run_path(str(implementation), run_name="__nanoclaw_clawbenchpro_builder__")
        build_env_fn = namespace.get("build_env")
        if callable(build_env_fn):
            build_env_fn()
        else:
            turn_builders = []
            for name, value in namespace.items():
                match = re.fullmatch(r"(?:build|make)_turn_(\\d+)", str(name))
                if match and callable(value):
                    turn_builders.append((int(match.group(1)), value))
            if turn_builders:
                for _, builder in sorted(turn_builders):
                    builder()
            else:
                main_fn = namespace.get("main")
                if callable(main_fn):
                    main_fn()
                else:
                    for fallback_name in ("build", "create_files", "build_sandbox"):
                        fallback_fn = namespace.get(fallback_name)
                        if callable(fallback_fn):
                            fallback_fn()
                            break
                    # A small number of builders materialize their files directly
                    # at module top level. runpy.run_path above already executed them.
    finally:
        if inserted_path:
            sys.path.remove(implementation_dir)

    skills_bundle = bundle_dir / "_skills_bundle"
    if skills_bundle.is_dir():
        shutil.copytree(skills_bundle, Path.cwd() / "skills", dirs_exist_ok=True)
'''


def json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def sha256_files(paths: list[Path], *, extra: str = "") -> str:
    digest = hashlib.sha256()
    digest.update(extra.encode("utf-8"))
    for path in sorted(paths):
        digest.update(str(path.name).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def source_fingerprint(source_root: Path, dataset_names: tuple[str, ...]) -> str:
    paths = [source_root / "manifest.json", source_root / "checksums.sha256"]
    for dataset_name in dataset_names:
        dataset_root = source_root / dataset_name
        paths.extend(
            (
                dataset_root / "manifest.json",
                dataset_root / "dataset_index.jsonl",
                dataset_root / "checksums.sha256",
            )
        )
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("ClawBenchPro metadata is incomplete: " + ", ".join(missing))
    return sha256_files(paths, extra=f"adapter_version={ADAPTER_VERSION}\n")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except Exception as exc:
            raise ValueError(f"failed to read JSONL {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"expected a JSON object at {path}:{line_number}")
        rows.append(value)
    return rows


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected a YAML mapping in {path}")
    return value


def safe_relative_path(root: Path, raw_path: Any, *, label: str) -> Path:
    value = Path(str(raw_path))
    if value.is_absolute() or ".." in value.parts:
        raise ValueError(f"unsafe {label} path in ClawBenchPro index: {raw_path!r}")
    resolved = (root / value).resolve()
    root_resolved = root.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ValueError(f"{label} path escapes ClawBenchPro root: {raw_path!r}")
    return resolved


def prompt_text(source_root: Path, prompt_files: list[Any]) -> tuple[str, list[str]]:
    if not prompt_files:
        raise ValueError("ClawBenchPro task has no prompt files")
    paths = [safe_relative_path(source_root, item, label="prompt") for item in prompt_files]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise MissingPromptError([Path(path) for path in missing])
    texts = [path.read_text(encoding="utf-8").strip() for path in paths]
    if len(texts) == 1:
        return texts[0] + "\n", [str(path.relative_to(source_root)) for path in paths]

    sections = [
        "This benchmark task contains chronological user requests from one continuing workspace session.",
        "Complete all requests in order in this single training-compatible episode. Later requests update earlier requirements; preserve the accumulated state and produce the final requested workspace artifacts.",
    ]
    for turn_index, text in enumerate(texts, start=1):
        sections.extend((f"\n===== USER REQUEST {turn_index} OF {len(texts)} =====", text))
    return "\n".join(sections).strip() + "\n", [str(path.relative_to(source_root)) for path in paths]


def skill_names(task_yaml: dict[str, Any]) -> list[str]:
    skills = task_yaml.get("skills")
    available = skills.get("available") if isinstance(skills, dict) else None
    if available in (None, ""):
        return []
    if not isinstance(available, list):
        raise ValueError(f"invalid skills.available value: {available!r}")
    names = [str(item).strip() for item in available if str(item).strip()]
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate skill names in task YAML: {names}")
    return names


def repair_known_builder_issues(path: Path, task_id: str) -> list[str]:
    repairs: list[str] = []
    if task_id == "data_round_01_aligned_mix_800_0416":
        text = path.read_text(encoding="utf-8")
        broken = 'Target {td["id"]} observed:'
        fixed = "Target {td['id']} observed:"
        if broken in text:
            path.write_text(text.replace(broken, fixed), encoding="utf-8")
            repairs.append("fix_unmatched_fstring_quote_in_builder")
    if task_id == "data_persona_aligned_hard_50_0028":
        text = path.read_text(encoding="utf-8")
        broken = '''    with open("hw_specs/sub_dir/vendor_b.json", "w") as f: 
        os.makedirs("hw_specs/sub_dir", exist_ok=True)
        json.dump(hw_specs_3, f)
'''
        fixed = '''    os.makedirs("hw_specs/sub_dir", exist_ok=True)
    with open("hw_specs/sub_dir/vendor_b.json", "w") as f:
        json.dump(hw_specs_3, f)
'''
        if broken in text:
            path.write_text(text.replace(broken, fixed), encoding="utf-8")
            repairs.append("create_hw_specs_subdir_before_open")
    return repairs


def copy_task_bundle(
    *,
    source_root: Path,
    dataset_name: str,
    row: dict[str, Any],
    destination_root: Path,
) -> dict[str, Any]:
    task_id = str(row.get("task_id") or "").strip()
    if not task_id.startswith("data_"):
        raise ValueError(f"invalid ClawBenchPro task_id: {task_id!r}")
    task_yaml_path = safe_relative_path(source_root, row.get("task_file"), label="task_file")
    if not task_yaml_path.is_file():
        raise FileNotFoundError(f"ClawBenchPro task YAML is missing: {task_yaml_path}")
    task_yaml = load_yaml(task_yaml_path)
    if str(task_yaml.get("id") or "") != task_id:
        raise ValueError(
            f"task ID mismatch: index={task_id!r}, yaml={task_yaml.get('id')!r}, path={task_yaml_path}"
        )

    source_task_dir = task_yaml_path.parent / task_id
    if not source_task_dir.is_dir():
        raise FileNotFoundError(f"ClawBenchPro task bundle is missing: {source_task_dir}")
    implementation = source_task_dir / "_env_builder_impl.py"
    verifier = source_task_dir / "verify_workplace.py"
    if not implementation.is_file() or not verifier.is_file():
        raise FileNotFoundError(
            f"task {task_id} requires _env_builder_impl.py and verify_workplace.py under {source_task_dir}"
        )

    destination = destination_root / task_id
    shutil.copytree(
        source_task_dir,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "workspace_before", "workspace_after"),
    )
    shutil.copy2(task_yaml_path, destination / "task.yaml")
    combined_prompt, prompt_sources = prompt_text(source_root, list(row.get("prompt_files") or []))
    (destination / "prompts.md").write_text(combined_prompt, encoding="utf-8")
    (destination / "env_builder.py").write_text(ADAPTED_ENV_BUILDER, encoding="utf-8")

    repairs = repair_known_builder_issues(destination / "_env_builder_impl.py", task_id)
    skills = skill_names(task_yaml)
    if skills:
        source_skills_root = source_root / dataset_name / "skills"
        target_skills_root = destination / "_skills_bundle"
        target_skills_root.mkdir(parents=True, exist_ok=True)
        for skill_name in skills:
            source_skill = source_skills_root / skill_name
            if not source_skill.is_dir():
                raise FileNotFoundError(f"task {task_id} references missing skill directory: {source_skill}")
            shutil.copytree(source_skill, target_skills_root / skill_name)

    manifest = {
        "task_id": task_id,
        "format": CLAW_BENCH_PRO_FORMAT,
        "adapter_version": ADAPTER_VERSION,
        "source_dataset": dataset_name,
        "source_category": row.get("category"),
        "source_task_file": str(task_yaml_path.relative_to(source_root)),
        "source_prompt_files": prompt_sources,
        "session_count": len(prompt_sources),
        "session_policy": "chronological_prompts_combined_into_one_training_compatible_episode",
        "skills": skills,
        "repairs": repairs,
        "files": {
            "yaml": "task.yaml",
            "prompt": "prompts.md",
            "env_builder": "env_builder.py",
            "verifier": "verify_workplace.py",
        },
    }
    (destination / "manifest.json").write_text(json_dumps(manifest) + "\n", encoding="utf-8")
    return manifest


def expected_dataset_counts(source_root: Path, dataset_names: tuple[str, ...]) -> dict[str, int]:
    package_manifest = load_json(source_root / "manifest.json")
    declared = {
        str(item.get("name")): int(item.get("task_count", -1))
        for item in package_manifest.get("datasets", [])
        if isinstance(item, dict)
    }
    counts: dict[str, int] = {}
    for dataset_name in dataset_names:
        count = declared.get(dataset_name)
        if count is None or count <= 0:
            raise ValueError(f"ClawBenchPro root manifest has no positive task count for {dataset_name!r}")
        counts[dataset_name] = count
    return counts


def validate_existing_output(
    output_root: Path,
    *,
    fingerprint: str,
    expected_source_count: int,
    skip_missing_prompts: bool,
) -> bool:
    manifest_path = output_root / "benchmark_manifest.json"
    success_path = output_root / "_SUCCESS"
    if not manifest_path.is_file() or not success_path.is_file():
        return False
    manifest = load_json(manifest_path)
    if manifest.get("format") != CLAW_BENCH_PRO_FORMAT:
        return False
    if manifest.get("source_fingerprint") != fingerprint:
        return False
    if bool(manifest.get("skip_missing_prompts", False)) != skip_missing_prompts:
        return False
    tasks = manifest.get("tasks")
    excluded_tasks = manifest.get("excluded_tasks", [])
    if not isinstance(tasks, list) or not isinstance(excluded_tasks, list):
        return False
    if int(manifest.get("task_count", -1)) != len(tasks):
        return False
    if len(tasks) + len(excluded_tasks) != expected_source_count:
        return False
    return all((output_root / str(item.get("task_id"))).is_dir() for item in tasks if isinstance(item, dict))


def prepare_dataset(
    source_root: Path,
    output_root: Path,
    *,
    dataset_names: tuple[str, ...] = DEFAULT_DATASETS,
    selected_task_ids: set[str] | None = None,
    overwrite: bool = False,
    skip_missing_prompts: bool = False,
) -> dict[str, Any]:
    source_root = source_root.expanduser().resolve()
    output_root = output_root.expanduser().resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(f"ClawBenchPro source directory not found: {source_root}")
    if output_root == source_root or source_root in output_root.parents:
        raise ValueError("adapted output must not be placed inside the immutable ClawBenchPro source tree")

    dataset_counts = expected_dataset_counts(source_root, dataset_names)
    fingerprint = source_fingerprint(source_root, dataset_names)
    expected_source_count = sum(dataset_counts.values()) if selected_task_ids is None else len(selected_task_ids)
    if output_root.exists():
        if validate_existing_output(
            output_root,
            fingerprint=fingerprint,
            expected_source_count=expected_source_count,
            skip_missing_prompts=skip_missing_prompts,
        ):
            existing_manifest = load_json(output_root / "benchmark_manifest.json")
            print(
                f"[clawbenchpro_adapter_reuse] output={output_root} "
                f"tasks={existing_manifest.get('task_count')} "
                f"excluded={len(existing_manifest.get('excluded_tasks', []))} fingerprint={fingerprint}",
                flush=True,
            )
            return existing_manifest
        if not overwrite:
            raise FileExistsError(
                f"adapted output exists but is incomplete or stale: {output_root}; pass --overwrite to replace it"
            )
        shutil.rmtree(output_root)

    output_root.parent.mkdir(parents=True, exist_ok=True)
    staging_root = output_root.parent / f".{output_root.name}.tmp-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    staging_root.mkdir(parents=False, exist_ok=False)
    task_records: list[dict[str, Any]] = []
    excluded_tasks: list[dict[str, Any]] = []
    seen_task_ids: set[str] = set()
    try:
        for dataset_name in dataset_names:
            index_path = source_root / dataset_name / "dataset_index.jsonl"
            rows = load_jsonl(index_path)
            if len(rows) != dataset_counts[dataset_name]:
                raise ValueError(
                    f"dataset count mismatch for {dataset_name}: manifest={dataset_counts[dataset_name]}, index={len(rows)}"
                )
            for row in rows:
                task_id = str(row.get("task_id") or "")
                if selected_task_ids is not None and task_id not in selected_task_ids:
                    continue
                if task_id in seen_task_ids:
                    raise ValueError(f"duplicate task ID across ClawBenchPro datasets: {task_id}")
                seen_task_ids.add(task_id)
                try:
                    manifest = copy_task_bundle(
                        source_root=source_root,
                        dataset_name=dataset_name,
                        row=row,
                        destination_root=staging_root,
                    )
                except MissingPromptError as prompt_error:
                    shutil.rmtree(staging_root / task_id, ignore_errors=True)
                    if not skip_missing_prompts:
                        raise
                    excluded_tasks.append(
                        {
                            "task_id": task_id,
                            "source_dataset": dataset_name,
                            "source_category": row.get("category"),
                            "reason": "missing_prompt_files_in_published_dataset",
                            "missing_prompt_files": [str(path.relative_to(source_root)) for path in prompt_error.missing_paths],
                        }
                    )
                    print(
                        f"[clawbenchpro_adapter_exclude] task={task_id} reason=missing_prompt_files_in_published_dataset",
                        flush=True,
                    )
                    continue
                task_records.append(
                    {
                        "task_id": task_id,
                        "source_dataset": dataset_name,
                        "source_category": row.get("category"),
                        "session_count": manifest["session_count"],
                        "skill_count": len(manifest["skills"]),
                    }
                )

        if selected_task_ids is not None:
            missing = sorted(selected_task_ids - seen_task_ids)
            if missing:
                raise FileNotFoundError(f"requested ClawBenchPro task IDs were not found: {missing}")
        if len(task_records) + len(excluded_tasks) != expected_source_count:
            raise RuntimeError(
                "adapted source accounting mismatch: "
                f"expected={expected_source_count}, built={len(task_records)}, excluded={len(excluded_tasks)}"
            )

        benchmark_manifest = {
            "format": CLAW_BENCH_PRO_FORMAT,
            "adapter_version": ADAPTER_VERSION,
            "source_root": str(source_root),
            "source_fingerprint": fingerprint,
            "task_count": len(task_records),
            "source_task_count": expected_source_count,
            "skip_missing_prompts": skip_missing_prompts,
            "excluded_tasks": excluded_tasks,
            "dataset_counts": dataset_counts,
            "episode_policy": "training_identical_single_user_task_with_multi_turn_tool_interaction",
            "tasks": task_records,
        }
        (staging_root / "benchmark_manifest.json").write_text(
            json_dumps(benchmark_manifest) + "\n", encoding="utf-8"
        )
        (staging_root / "_SUCCESS").write_text(
            json_dumps(
                {
                    "format": CLAW_BENCH_PRO_FORMAT,
                    "task_count": len(task_records),
                    "source_fingerprint": fingerprint,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        os.replace(staging_root, output_root)
    except Exception:
        shutil.rmtree(staging_root, ignore_errors=True)
        raise

    print(
        f"[clawbenchpro_adapter_done] source={source_root} output={output_root} "
        f"tasks={len(task_records)} excluded={len(excluded_tasks)} fingerprint={fingerprint}",
        flush=True,
    )
    return benchmark_manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert ClawBenchPro into the flat per-task bundles consumed by the training-identical Nanoclaw recipe."
    )
    parser.add_argument("--source", required=True, type=Path, help="ClawBenchPro repository root.")
    parser.add_argument("--output", required=True, type=Path, help="Shared output directory for adapted task bundles.")
    parser.add_argument("--dataset", action="append", choices=DEFAULT_DATASETS, help="Dataset subset; repeatable.")
    parser.add_argument("--task-id", action="append", default=[], help="Adapt only selected tasks for a smoke test.")
    parser.add_argument(
        "--skip-missing-prompts",
        action="store_true",
        help="Exclude published tasks whose prompt files are absent and record them in benchmark_manifest.json.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace an incomplete or stale adapted output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    dataset_names = tuple(args.dataset) if args.dataset else DEFAULT_DATASETS
    selected_task_ids = set(args.task_id) if args.task_id else None
    prepare_dataset(
        args.source,
        args.output,
        dataset_names=dataset_names,
        selected_task_ids=selected_task_ids,
        overwrite=args.overwrite,
        skip_missing_prompts=args.skip_missing_prompts,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
