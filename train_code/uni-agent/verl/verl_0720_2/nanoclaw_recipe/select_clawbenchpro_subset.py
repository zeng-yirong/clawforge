from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nanoclaw_recipe.prepare_clawbenchpro import (
    ADAPTER_VERSION,
    CLAW_BENCH_PRO_FORMAT,
    load_json,
    load_jsonl,
    prepare_dataset,
)


SELECTION_FORMAT = "clawbenchpro-quality-base-hard-v1"
DEFAULT_QUOTA = 100
CATEGORY_MAP = {
    ("round_01_aligned_mix_800", "base"): "base",
    ("round_01_aligned_mix_800", "hard_aligned"): "hard",
    ("persona_aligned_mix_200", "base"): "base",
    ("persona_aligned_mix_200", "hard"): "hard",
}
KNOWN_BUILDER_REPAIR_TASKS = {
    "data_round_01_aligned_mix_800_0416",
    "data_persona_aligned_hard_50_0028",
}
KNOWN_VERIFIER_ZERO_OUTPUT_FAILURE_TASKS = {
    # Crashes with UnboundLocalError when the requested report is absent.
    "data_persona_aligned_base_50_0005",
    # Prints a score to stdout but does not persist workplace_score.json when
    # the requested artifact is absent.
    "data_round_01_aligned_mix_800_0406",
}
STDLIB_OR_BUNDLED_IMPORTS = {
    "argparse",
    "base64",
    "binascii",
    "collections",
    "csv",
    "datetime",
    "decimal",
    "functools",
    "glob",
    "gzip",
    "hashlib",
    "heapq",
    "html",
    "io",
    "itertools",
    "json",
    "math",
    "os",
    "pathlib",
    "random",
    "re",
    "shutil",
    "sqlite3",
    "statistics",
    "string",
    "struct",
    "sys",
    "tarfile",
    "tempfile",
    "textwrap",
    "time",
    "typing",
    "uuid",
    "xml",
    "zipfile",
    "zlib",
    # Installed by the training environment and commonly used by builders.
    "yaml",
}


@dataclass(slots=True)
class Candidate:
    task_id: str
    quality_category: str
    source_dataset: str
    source_category: str
    source_row: dict[str, Any]
    score: int
    score_breakdown: dict[str, int]
    rejected_reasons: list[str]
    diagnostics: dict[str, Any]

    @property
    def eligible(self) -> bool:
        return not self.rejected_reasons

    def selection_record(self, *, rank: int | None = None, selected: bool = False) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "quality_category": self.quality_category,
            "source_dataset": self.source_dataset,
            "source_category": self.source_category,
            "selected": selected,
            "rank": rank,
            "quality_score": self.score,
            "score_breakdown": self.score_breakdown,
            "rejected_reasons": self.rejected_reasons,
            "diagnostics": self.diagnostics,
        }


def parse_python(path: Path) -> tuple[ast.Module | None, str | None]:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path)), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def imported_modules(tree: ast.Module) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".", 1)[0])
    return modules


def function_names(tree: ast.Module) -> set[str]:
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def explicit_output_path(prompt: str) -> bool:
    patterns = (
        r"`[^`\n]+\.(?:json|jsonl|csv|txt|md|yaml|yml|xml|html|log|py|pdf)`",
        r"(?:write|save|put|store|输出|写入|保存|放到|生成).{0,80}(?:/|\\)[\w.\-]+",
    )
    return any(re.search(pattern, prompt, re.IGNORECASE | re.DOTALL) for pattern in patterns)


def verifier_writes_workspace_score(verifier_text: str) -> bool:
    patterns = (
        r"(?:Path\s*\(\s*workspace|Path\s*\(\s*workspace_path|os\.path\.join\s*\(\s*workspace)[\s\S]{0,160}workplace_score\.json",
        r"open\s*\(\s*os\.path\.join\s*\(\s*workspace[^)]*workplace_score\.json",
    )
    return any(re.search(pattern, verifier_text, re.IGNORECASE) for pattern in patterns)


def load_validation_issues(dataset_root: Path) -> dict[str, list[Any]]:
    report_path = dataset_root / "provenance" / "validation_report.json"
    if not report_path.is_file():
        return {}
    value = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        return {}
    return {
        str(item.get("task_id")): list(item.get("issues") or [])
        for item in value
        if isinstance(item, dict) and item.get("task_id")
    }


def evaluate_candidate(
    *,
    source_root: Path,
    dataset_name: str,
    row: dict[str, Any],
    quality_category: str,
    source_category: str,
    materialization: dict[str, Any] | None,
    repaired_verifier: dict[str, Any] | None,
    validation_issues: list[Any],
) -> Candidate:
    task_id = str(row.get("task_id") or "")
    dataset_root = source_root / dataset_name
    task_dir = dataset_root / "tasks" / task_id
    builder_path = task_dir / "_env_builder_impl.py"
    verifier_path = task_dir / "verify_workplace.py"
    prompt_paths = [(source_root / str(path)).resolve() for path in list(row.get("prompt_files") or [])]
    rejected: list[str] = []

    missing_prompts = [str(path) for path in prompt_paths if not path.is_file()]
    if missing_prompts:
        rejected.append("missing_prompt_files")
    if not builder_path.is_file():
        rejected.append("missing_builder")
    if not verifier_path.is_file():
        rejected.append("missing_verifier")

    builder_tree, builder_error = parse_python(builder_path) if builder_path.is_file() else (None, None)
    verifier_tree, verifier_error = parse_python(verifier_path) if verifier_path.is_file() else (None, None)
    if builder_error:
        rejected.append("builder_syntax_error")
    if verifier_error:
        rejected.append("verifier_syntax_error")
    if task_id in KNOWN_BUILDER_REPAIR_TASKS:
        rejected.append("known_builder_runtime_or_syntax_repair")
    if task_id in KNOWN_VERIFIER_ZERO_OUTPUT_FAILURE_TASKS:
        rejected.append("verifier_fails_builder_only_zero_output_smoke_test")
    if repaired_verifier is not None:
        rejected.append("verifier_required_conservative_repair")
    if validation_issues:
        rejected.append("published_validation_issues")

    verifier_text = verifier_path.read_text(encoding="utf-8", errors="replace") if verifier_path.is_file() else ""
    if "workplace_score.json" not in verifier_text:
        rejected.append("verifier_missing_workplace_score_output")
    if "details" not in verifier_text or "max_score" not in verifier_text:
        rejected.append("verifier_missing_structured_score_details")

    prompt = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in prompt_paths if path.is_file())
    builder_text = builder_path.read_text(encoding="utf-8", errors="replace") if builder_path.is_file() else ""
    builder_imports = imported_modules(builder_tree) if builder_tree is not None else set()
    external_imports = sorted(builder_imports - STDLIB_OR_BUNDLED_IMPORTS)
    # pandas-backed builders are valid in the full environment, but the compact
    # quality subset prefers task-local/stdlib builders with fewer setup risks.
    if "pandas" in external_imports:
        rejected.append("builder_requires_pandas")

    breakdown: dict[str, int] = {"eligible_baseline": 100}
    if materialization and str(materialization.get("repair_action", "")).startswith("same_group_raw"):
        breakdown["direct_same_group_verifier"] = 20
    if not any(token in verifier_text for token in ("OpenAI(", "client.chat.completions", "httpx.Client")):
        breakdown["deterministic_rule_verifier"] = 18
    if verifier_writes_workspace_score(verifier_text):
        breakdown["workspace_local_score_output"] = 15
    if '"passed"' in verifier_text or "'passed'" in verifier_text:
        breakdown["per_check_pass_flags"] = 5
    if "total_score" in verifier_text:
        breakdown["explicit_total_score"] = 5

    if builder_tree is not None:
        names = function_names(builder_tree)
        if "build_env" in names:
            breakdown["canonical_build_env"] = 8
        if "random" not in builder_imports:
            breakdown["deterministic_builder_no_random"] = 12
        elif re.search(r"random\.seed\s*\(", builder_text):
            breakdown["deterministic_builder_seeded"] = 8
        if not external_imports:
            breakdown["stdlib_or_bundled_builder_dependencies"] = 8

    prompt_length = len(prompt)
    if 300 <= prompt_length <= 6000:
        breakdown["substantive_bounded_prompt"] = 8
    elif 150 <= prompt_length <= 8000:
        breakdown["acceptable_prompt_length"] = 4
    if explicit_output_path(prompt):
        breakdown["explicit_output_artifact"] = 10
    if len(prompt_paths) == 1:
        breakdown["single_prompt_episode_fit"] = 5

    diagnostics = {
        "prompt_files": [str(path.relative_to(source_root)) for path in prompt_paths if path.is_file()],
        "missing_prompt_files": missing_prompts,
        "prompt_length_chars": prompt_length,
        "builder_imports": sorted(builder_imports),
        "builder_external_imports": external_imports,
        "builder_syntax_error": builder_error,
        "verifier_syntax_error": verifier_error,
        "verifier_materialization_action": materialization.get("repair_action") if materialization else None,
        "verifier_uses_llm_judge": any(
            token in verifier_text for token in ("OpenAI(", "client.chat.completions", "httpx.Client")
        ),
        "verifier_writes_workspace_score": verifier_writes_workspace_score(verifier_text),
        "published_validation_issues": validation_issues,
    }
    return Candidate(
        task_id=task_id,
        quality_category=quality_category,
        source_dataset=dataset_name,
        source_category=source_category,
        source_row=row,
        score=sum(breakdown.values()),
        score_breakdown=breakdown,
        rejected_reasons=sorted(set(rejected)),
        diagnostics=diagnostics,
    )


def collect_candidates(source_root: Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    for dataset_name in ("round_01_aligned_mix_800", "persona_aligned_mix_200"):
        dataset_root = source_root / dataset_name
        rows = load_jsonl(dataset_root / "dataset_index.jsonl")
        import_records = {
            str(item.get("imported_task_id")): item
            for item in load_jsonl(dataset_root / "import_manifest.jsonl")
        }
        materialization = {
            str(item.get("imported_task_id")): item
            for item in load_jsonl(dataset_root / "provenance" / "verifier_materialization_manifest.jsonl")
        }
        repairs_path = dataset_root / "provenance" / "verifier_repair_manifest.jsonl"
        repairs = {
            str(item.get("imported_task_id")): item
            for item in (load_jsonl(repairs_path) if repairs_path.is_file() else [])
        }
        issues = load_validation_issues(dataset_root)
        for row in rows:
            task_id = str(row.get("task_id") or "")
            import_record = import_records.get(task_id)
            if import_record is None:
                raise ValueError(f"task {task_id!r} is missing from {dataset_root / 'import_manifest.jsonl'}")
            # import_manifest.group is the authoritative construction group.
            # dataset_index.csv/jsonl in the published round-01 package labels
            # some early multi-turn rows as base, so it is not safe for quotas.
            source_category = str(import_record.get("group") or row.get("category") or "")
            quality_category = CATEGORY_MAP.get((dataset_name, source_category))
            if quality_category is None:
                continue
            candidates.append(
                evaluate_candidate(
                    source_root=source_root,
                    dataset_name=dataset_name,
                    row=row,
                    quality_category=quality_category,
                    source_category=source_category,
                    materialization=materialization.get(task_id),
                    repaired_verifier=repairs.get(task_id),
                    validation_issues=issues.get(task_id, []),
                )
            )
    return candidates


def select_candidates(candidates: list[Candidate], *, quota: int) -> tuple[list[Candidate], dict[str, list[Candidate]]]:
    by_category: dict[str, list[Candidate]] = {"base": [], "hard": []}
    for candidate in candidates:
        by_category[candidate.quality_category].append(candidate)

    selected: list[Candidate] = []
    for category in ("base", "hard"):
        eligible = [item for item in by_category[category] if item.eligible]
        eligible.sort(key=lambda item: (-item.score, item.source_dataset, item.task_id))
        if len(eligible) < quota:
            raise RuntimeError(f"not enough eligible {category} tasks: required={quota}, eligible={len(eligible)}")
        selected.extend(eligible[:quota])
    return selected, by_category


def write_selection_files(
    output_root: Path,
    *,
    source_root: Path,
    quota: int,
    selected: list[Candidate],
    all_candidates: dict[str, list[Candidate]],
) -> None:
    selected_ids = {item.task_id for item in selected}
    selected_by_id = {item.task_id: item for item in selected}
    records: list[dict[str, Any]] = []
    category_stats: dict[str, Any] = {}
    for category in ("base", "hard"):
        ranked = sorted(
            (item for item in all_candidates[category] if item.eligible),
            key=lambda item: (-item.score, item.source_dataset, item.task_id),
        )
        rank_map = {item.task_id: rank for rank, item in enumerate(ranked, start=1)}
        for item in sorted(all_candidates[category], key=lambda candidate: candidate.task_id):
            records.append(
                item.selection_record(
                    rank=rank_map.get(item.task_id),
                    selected=item.task_id in selected_ids,
                )
            )
        selected_category = [item for item in selected if item.quality_category == category]
        category_stats[category] = {
            "source_candidates": len(all_candidates[category]),
            "eligible_candidates": len(ranked),
            "rejected_candidates": len(all_candidates[category]) - len(ranked),
            "selected": len(selected_category),
            "selected_score_min": min(item.score for item in selected_category),
            "selected_score_max": max(item.score for item in selected_category),
            "selected_source_datasets": {
                dataset_name: sum(item.source_dataset == dataset_name for item in selected_category)
                for dataset_name in sorted({item.source_dataset for item in selected_category})
            },
        }

    with (output_root / "quality_selection_manifest.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    report = {
        "format": SELECTION_FORMAT,
        "adapter_version": ADAPTER_VERSION,
        "source_root": str(source_root),
        "quota_per_category": quota,
        "selected_task_count": len(selected),
        "categories": category_stats,
        "hard_rejection_policy": [
            "missing prompt/builder/verifier",
            "builder or verifier syntax error",
            "verifier missing workplace_score.json or details[*].max_score structure",
            "verifier required conservative fallback repair",
            "published validation issues",
            "known builder repair",
            "verifier failed builder-only zero-output smoke test",
            "pandas-dependent builder (compact subset dependency-risk reduction)",
        ],
        "ranking_policy": [
            "direct same-group verifier provenance",
            "deterministic rule verifier",
            "workspace-local score output",
            "canonical and deterministic builder",
            "stdlib/bundled builder dependencies",
            "bounded substantive prompt",
            "explicit requested output artifact",
            "stable task-id tie-break",
        ],
        "selected_task_ids": {
            category: [
                item.task_id
                for item in sorted(
                    (candidate for candidate in selected if candidate.quality_category == category),
                    key=lambda candidate: (-candidate.score, candidate.source_dataset, candidate.task_id),
                )
            ]
            for category in ("base", "hard")
        },
    }
    (output_root / "quality_selection_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    benchmark_manifest_path = output_root / "benchmark_manifest.json"
    benchmark_manifest = load_json(benchmark_manifest_path)
    for task_record in benchmark_manifest.get("tasks", []):
        if not isinstance(task_record, dict):
            continue
        selected_item = selected_by_id.get(str(task_record.get("task_id") or ""))
        if selected_item is None:
            continue
        task_record["source_category"] = selected_item.source_category
        task_record["quality_category"] = selected_item.quality_category
    benchmark_manifest.update(
        {
            "selection_format": SELECTION_FORMAT,
            "quality_categories": {"base": quota, "hard": quota},
            "quality_selection_report": "quality_selection_report.json",
            "quality_selection_manifest": "quality_selection_manifest.jsonl",
        }
    )
    benchmark_manifest_path.write_text(
        json.dumps(benchmark_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # The published dataset_index category is inconsistent with the
    # authoritative import_manifest group for parts of round-01. Correct the
    # copied task metadata while retaining the original index label for audit.
    for task_id, selected_item in selected_by_id.items():
        task_manifest_path = output_root / task_id / "manifest.json"
        task_manifest = load_json(task_manifest_path)
        task_manifest["source_index_category"] = task_manifest.get("source_category")
        task_manifest["source_category"] = selected_item.source_category
        task_manifest["quality_category"] = selected_item.quality_category
        task_manifest_path.write_text(
            json.dumps(task_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def build_quality_subset(source_root: Path, output_root: Path, *, quota: int, overwrite: bool) -> dict[str, Any]:
    source_root = source_root.expanduser().resolve()
    output_root = output_root.expanduser().resolve()
    candidates = collect_candidates(source_root)
    selected, by_category = select_candidates(candidates, quota=quota)
    selected_ids = {item.task_id for item in selected}
    if len(selected_ids) != quota * 2:
        raise RuntimeError(f"selected task IDs are not unique: expected={quota * 2}, got={len(selected_ids)}")

    if output_root.exists() and overwrite:
        shutil.rmtree(output_root)
    prepare_dataset(
        source_root,
        output_root,
        selected_task_ids=selected_ids,
        overwrite=False,
        skip_missing_prompts=False,
    )
    write_selection_files(
        output_root,
        source_root=source_root,
        quota=quota,
        selected=selected,
        all_candidates=by_category,
    )
    print(
        f"[clawbenchpro_quality_subset_done] output={output_root} base={quota} hard={quota} total={quota * 2}",
        flush=True,
    )
    return load_json(output_root / "quality_selection_report.json")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select a high-quality ClawBenchPro base/hard subset.")
    parser.add_argument("--source", required=True, type=Path, help="ClawBenchPro repository root.")
    parser.add_argument("--output", required=True, type=Path, help="Output directory for the flat selected subset.")
    parser.add_argument("--quota", type=int, default=DEFAULT_QUOTA, help="Tasks selected per category.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output directory.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.quota <= 0:
        raise ValueError("--quota must be positive")
    build_quality_subset(args.source, args.output, quota=args.quota, overwrite=args.overwrite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
