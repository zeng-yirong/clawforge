from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nanoclaw_recipe.common import find_verifier_path, read_manifest, score_summary

from .tools import workspace_subprocess_env


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run verify_workplace.py for existing Nanoclaw result dirs and persist score metadata.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--result-root", required=True, help="Existing result root produced by the runner.")
    parser.add_argument("--base-tasks", default=None, help="Optional base_tasks directory used to find missing verifier scripts.")
    parser.add_argument("--task-id", action="append", default=None, help="Score only this task id. Can repeat.")
    parser.add_argument("--task-glob", default="data_*", help="Task result directory glob under result-root.")
    parser.add_argument("--mock-api-base", default="http://127.0.0.1:8000/v1", help="OpenAI-compatible verifier API base URL.")
    parser.add_argument("--mock-model-name", default=None, help="Model name passed to verifier as MOCK_MODEL_NAME.")
    parser.add_argument("--mock-api-key", default="dummy_key", help="API key passed to verifier as MOCK_API_KEY.")
    parser.add_argument("--timeout", type=float, default=300.0, help="Per-task verifier timeout in seconds.")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit non-zero if any verifier fails.")
    parser.add_argument("--no-update-metadata", action="store_true", help="Do not update runner_metadata.json/conversation_history.json.")
    return parser.parse_args(argv)


def result_dir_task_id(result_dir: Path) -> str:
    metadata = load_json_file(result_dir / "runner_metadata.json")
    if isinstance(metadata, dict) and metadata.get("task_id"):
        return str(metadata["task_id"])
    name = result_dir.name
    marker = "_sample_"
    return name.split(marker, 1)[0] if marker in name else name


def discover_result_dirs(result_root: Path, *, task_glob: str, task_ids: set[str] | None) -> list[Path]:
    if not result_root.is_dir():
        raise FileNotFoundError(f"result root not found: {result_root}")
    candidates = list(result_root.glob(task_glob))
    candidates.extend(result_root.glob(f"step_*/{task_glob}_sample_*"))
    dirs = sorted({path.resolve() for path in candidates if path.is_dir() and (path / "workspace_after").is_dir()})
    if task_ids is not None:
        dirs = [path for path in dirs if result_dir_task_id(path) in task_ids or path.name in task_ids]
        found = {result_dir_task_id(path) for path in dirs} | {path.name for path in dirs}
        missing = sorted(task_ids - found)
        if missing:
            raise FileNotFoundError(f"requested result task ids not found: {missing}")
    if not dirs:
        raise FileNotFoundError(f"no result dirs matched {task_glob!r} under {result_root}")
    return dirs


def find_verifier(result_dir: Path, base_tasks: Path | None) -> Path | None:
    metadata = load_json_file(result_dir / "runner_metadata.json")
    if isinstance(metadata, dict):
        verifier_value = metadata.get("verifier_source_path") or metadata.get("verifier_path")
        if verifier_value:
            verifier_path = Path(str(verifier_value)).expanduser()
            if verifier_path.is_file():
                return verifier_path
    for copied_name in ("workplace_verifier.py", "verify_workplace.py"):
        copied = result_dir / copied_name
        if copied.is_file():
            return copied
    if base_tasks is None:
        return None
    task_dir = base_tasks / result_dir_task_id(result_dir)
    if task_dir.is_dir():
        manifest_files, _, manifest_task_id = read_manifest(task_dir)
        verifier = find_verifier_path(None, manifest_task_id or result_dir_task_id(result_dir), task_dir=task_dir, manifest_files=manifest_files)
        if verifier is not None:
            return verifier
    for scripts_dirname in ("scrips", "scripts"):
        scripts_root = base_tasks / scripts_dirname
        candidates = (
            scripts_root / result_dir_task_id(result_dir) / "verify_workplace.py",
            scripts_root / f"{result_dir_task_id(result_dir)}.py",
            scripts_root / "verify_workplace.py",
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate
    return find_verifier_path(base_tasks / "scripts", result_dir_task_id(result_dir)) or find_verifier_path(base_tasks / "scrips", result_dir_task_id(result_dir))


def load_json_file(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def dump_json_file(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_verifier(
    *,
    result_dir: Path,
    verifier_path: Path,
    workspace_after: Path,
    mock_api_base: str,
    mock_model_name: str | None,
    mock_api_key: str,
    timeout: float,
) -> dict[str, Any]:
    started_at = utc_now()
    started = time.time()
    env = workspace_subprocess_env(workspace_after)
    env["MOCK_API_BASE"] = mock_api_base
    env["MOCK_API_KEY"] = mock_api_key
    if mock_model_name:
        env["MOCK_MODEL_NAME"] = mock_model_name

    try:
        process = subprocess.run(
            [sys.executable, str(verifier_path), str(workspace_after)],
            cwd=verifier_path.parent,
            text=True,
            capture_output=True,
            env=env,
            timeout=timeout,
            check=False,
        )
        result: dict[str, Any] = {
            "task_id": result_dir.name,
            "status": "completed" if process.returncode == 0 else "failed",
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        result = {
            "task_id": result_dir.name,
            "status": "failed",
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "error": f"verifier timed out after {timeout:g}s",
        }

    score_path = workspace_after / "workplace_score.json"
    workplace_score = load_json_file(score_path)
    result.update(
        {
            "started_at": started_at,
            "finished_at": utc_now(),
            "elapsed_seconds": round(time.time() - started, 3),
            "result_dir": str(result_dir),
            "workspace_after": str(workspace_after),
            "verifier_path": str(verifier_path),
            "mock_api_base": mock_api_base,
            "mock_model_name": mock_model_name,
            "workplace_score_path": str(score_path) if score_path.is_file() else None,
            "workplace_score": workplace_score,
            "score_summary": score_summary(workplace_score),
        }
    )
    return result


def update_result_files(result_dir: Path, verifier_result: dict[str, Any]) -> None:
    verifier_result_path = result_dir / "verifier_result.json"
    dump_json_file(verifier_result_path, verifier_result)

    score_payload = {
        "task_id": verifier_result.get("task_id"),
        "status": verifier_result.get("status"),
        "returncode": verifier_result.get("returncode"),
        "score_summary": verifier_result.get("score_summary"),
        "workplace_score": verifier_result.get("workplace_score"),
        "workplace_score_path": verifier_result.get("workplace_score_path"),
        "verifier_result_path": str(verifier_result_path),
        "updated_at": utc_now(),
    }
    dump_json_file(result_dir / "score_summary.json", score_payload)

    metadata_path = result_dir / "runner_metadata.json"
    metadata = load_json_file(metadata_path)
    if isinstance(metadata, dict):
        metadata["verifier"] = verifier_result
        metadata["posthoc_verifier"] = verifier_result
        metadata["score_summary"] = verifier_result.get("score_summary")
        metadata["updated_at"] = utc_now()
        dump_json_file(metadata_path, metadata)

    history_path = result_dir / "conversation_history.json"
    history = load_json_file(history_path)
    if isinstance(history, dict):
        history["verifier"] = verifier_result
        history["score_summary"] = verifier_result.get("score_summary")
        history["updated_at"] = utc_now()
        dump_json_file(history_path, history)


def write_aggregate_files(result_root: Path, results: list[dict[str, Any]], *, started_at: str) -> None:
    scoring_results_path = result_root / "scoring_results.jsonl"
    scoring_results_path.write_text(iter_jsonl(results), encoding="utf-8")

    completed = [result for result in results if result.get("status") == "completed"]
    failed = [result for result in results if result.get("status") != "completed"]
    numeric_scores = [
        result.get("score_summary", {}).get("score")
        for result in results
        if isinstance(result.get("score_summary", {}).get("score"), (int, float))
    ]
    numeric_max_scores = [
        result.get("score_summary", {}).get("max_score")
        for result in results
        if isinstance(result.get("score_summary", {}).get("max_score"), (int, float))
    ]
    summary = {
        "started_at": started_at,
        "finished_at": utc_now(),
        "total": len(results),
        "completed": len(completed),
        "failed": len(failed),
        "score_total": sum(numeric_scores) if numeric_scores else None,
        "max_score_total": sum(numeric_max_scores) if numeric_max_scores else None,
        "score_ratio": (sum(numeric_scores) / sum(numeric_max_scores)) if numeric_scores and numeric_max_scores and sum(numeric_max_scores) else None,
        "results": [
            {
                "task_id": result.get("task_id"),
                "status": result.get("status"),
                "returncode": result.get("returncode"),
                "score_summary": result.get("score_summary"),
                "result_dir": result.get("result_dir"),
                "verifier_result": str(Path(str(result.get("result_dir"))) / "verifier_result.json") if result.get("result_dir") else None,
            }
            for result in results
        ],
    }
    dump_json_file(result_root / "scoring_summary.json", summary)

    main_summary_path = result_root / "summary.json"
    main_summary = load_json_file(main_summary_path)
    if isinstance(main_summary, dict):
        main_summary["scoring"] = summary
        main_summary["updated_at"] = utc_now()
        dump_json_file(main_summary_path, main_summary)


def iter_jsonl(results: Iterable[dict[str, Any]]) -> str:
    return "".join(json.dumps(result, ensure_ascii=False) + "\n" for result in results)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result_root = Path(args.result_root).expanduser().resolve()
    base_tasks = Path(args.base_tasks).expanduser().resolve() if args.base_tasks else None
    task_ids = set(args.task_id) if args.task_id else None
    result_dirs = discover_result_dirs(result_root, task_glob=args.task_glob, task_ids=task_ids)

    started_at = utc_now()
    results: list[dict[str, Any]] = []
    for result_dir in result_dirs:
        workspace_after = result_dir / "workspace_after"
        verifier_path = find_verifier(result_dir, base_tasks)
        if verifier_path is None:
            result = {
                "task_id": result_dir.name,
                "status": "failed",
                "result_dir": str(result_dir),
                "workspace_after": str(workspace_after),
                "error": "verifier script not found in metadata, result dir, or base_tasks",
                "score_summary": {"score": None, "max_score": None, "score_ratio": None, "passed": None},
            }
        elif not workspace_after.is_dir():
            result = {
                "task_id": result_dir.name,
                "status": "failed",
                "result_dir": str(result_dir),
                "workspace_after": str(workspace_after),
                "verifier_path": str(verifier_path),
                "error": "workspace_after not found",
                "score_summary": {"score": None, "max_score": None, "score_ratio": None, "passed": None},
            }
        else:
            print(f"[score] {result_dir.name}", file=sys.stderr)
            result = run_verifier(
                result_dir=result_dir,
                verifier_path=verifier_path,
                workspace_after=workspace_after,
                mock_api_base=args.mock_api_base,
                mock_model_name=args.mock_model_name,
                mock_api_key=args.mock_api_key,
                timeout=args.timeout,
            )

        results.append(result)
        if not args.no_update_metadata:
            update_result_files(result_dir, result)
        write_aggregate_files(result_root, results, started_at=started_at)

    failed_count = sum(1 for result in results if result.get("status") != "completed")
    print(
        f"[done] scored={len(results)} failed={failed_count} summary={result_root / 'scoring_summary.json'}",
        file=sys.stderr,
    )
    return 1 if failed_count and args.fail_on_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
