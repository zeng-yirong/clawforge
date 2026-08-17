from __future__ import annotations

import argparse
import concurrent.futures
import json
import random
import shutil
import statistics
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from without_skill.server_fault_supabase_env import ServerFaultSupabaseEnvironment


SCENARIO_ID = "server_fault_triage_q2_2026"
TARGET_INCIDENT_IDS = ["inc_ups_001", "inc_srv_001", "inc_srv_003"]


@dataclass
class WorkerResult:
    session_id: str
    mode: str
    status: str
    elapsed_ms: float
    overall_score: float | None = None
    action_count: int | None = None
    supabase_rows_count: int | None = None
    audit_logs_count: int | None = None
    error: str | None = None


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = rank - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _perform_good_flow(env: ServerFaultSupabaseEnvironment, session_id: str) -> dict[str, Any]:
    env.view_task(session_id)
    env.screen_risk_incidents(
        session_id,
        categories=["ups_outage", "service_down"],
        statuses=["open", "triaged"],
        severities=["critical", "high"],
    )
    env.read_attachment(session_id, "runbook_ups_and_service.md")
    env.read_attachment(session_id, "supabase_write_contract.md")
    env.batch_remediate(
        session_id,
        TARGET_INCIDENT_IDS,
        remediation_mode="guided",
        operator_note="Applied incident runbook and validated recovery criteria.",
    )
    for incident_id in TARGET_INCIDENT_IDS:
        env.write_supabase_resolution(session_id, incident_id)
    env.list_audit_logs(session_id)
    return env.evaluate_session(session_id)


def _perform_partial_flow(env: ServerFaultSupabaseEnvironment, session_id: str) -> dict[str, Any]:
    env.view_task(session_id)
    env.screen_risk_incidents(
        session_id,
        categories=["ups_outage", "service_down"],
        statuses=["open", "triaged"],
        severities=["critical", "high"],
    )
    env.remediate_incident(
        session_id,
        "inc_srv_001",
        remediation_mode="manual",
        operator_note="Restarted service only.",
    )
    env.write_supabase_resolution(session_id, "inc_srv_001")
    return env.evaluate_session(session_id)


def _choose_behavior(index: int, behavior: str) -> str:
    if behavior != "mixed":
        return behavior
    table = ("good", "good", "partial", "good")
    return table[index % len(table)]


def run_isolated_session(job: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    env = ServerFaultSupabaseEnvironment(data_root=job.get("data_root"), state_root=job["state_root"])
    session_id = job["session_id"]
    behavior = _choose_behavior(job["job_index"], job["behavior"])

    try:
        env.create_session(session_id, job["scenario_id"], overwrite=False)
        if behavior == "good":
            evaluation = _perform_good_flow(env, session_id)
        elif behavior == "partial":
            evaluation = _perform_partial_flow(env, session_id)
        else:
            raise ValueError(f"Unknown behavior: {behavior}")
        summary = env.session_summary(session_id)
        result = WorkerResult(
            session_id=session_id,
            mode=f"isolated:{behavior}",
            status="ok",
            elapsed_ms=(time.perf_counter() - started) * 1000,
            overall_score=evaluation.get("overall_score"),
            action_count=summary.get("action_count"),
            supabase_rows_count=summary.get("supabase_rows_count"),
            audit_logs_count=summary.get("audit_logs_count"),
        )
    except Exception as exc:
        result = WorkerResult(
            session_id=session_id,
            mode=f"isolated:{behavior}",
            status="error",
            elapsed_ms=(time.perf_counter() - started) * 1000,
            error=f"{type(exc).__name__}: {exc}",
        )
    return asdict(result)


def run_contention_worker(job: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    env = ServerFaultSupabaseEnvironment(data_root=job.get("data_root"), state_root=job["state_root"])
    session_id = job["session_id"]
    incident = job["incident"]

    try:
        env.remediate_incident(
            session_id,
            incident["incident_id"],
            remediation_mode="contention",
            operator_note=f"contention remediation for {incident['incident_id']}",
        )
        env.write_supabase_resolution(session_id, incident["incident_id"])
        summary = env.session_summary(session_id)
        result = WorkerResult(
            session_id=session_id,
            mode="contention",
            status="ok",
            elapsed_ms=(time.perf_counter() - started) * 1000,
            action_count=summary.get("action_count"),
            supabase_rows_count=summary.get("supabase_rows_count"),
            audit_logs_count=summary.get("audit_logs_count"),
        )
    except Exception as exc:
        result = WorkerResult(
            session_id=session_id,
            mode="contention",
            status="error",
            elapsed_ms=(time.perf_counter() - started) * 1000,
            error=f"{type(exc).__name__}: {exc}",
        )
    return asdict(result)


def _executor_class(kind: str):
    if kind == "threads":
        return concurrent.futures.ThreadPoolExecutor
    if kind == "processes":
        return concurrent.futures.ProcessPoolExecutor
    raise ValueError(f"Unknown executor kind: {kind}")


def _summarize_worker_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    ok_results = [item for item in results if item["status"] == "ok"]
    err_results = [item for item in results if item["status"] != "ok"]
    elapsed = [item["elapsed_ms"] for item in ok_results]
    scores = [item["overall_score"] for item in ok_results if item.get("overall_score") is not None]
    return {
        "total": len(results),
        "ok": len(ok_results),
        "errors": len(err_results),
        "error_examples": err_results[:5],
        "elapsed_ms": {
            "mean": round(statistics.fmean(elapsed), 2) if elapsed else 0.0,
            "p50": round(_percentile(elapsed, 0.50), 2) if elapsed else 0.0,
            "p95": round(_percentile(elapsed, 0.95), 2) if elapsed else 0.0,
            "max": round(max(elapsed), 2) if elapsed else 0.0,
        },
        "score": {
            "mean": round(statistics.fmean(scores), 4) if scores else None,
            "min": round(min(scores), 4) if scores else None,
            "max": round(max(scores), 4) if scores else None,
        },
    }


def run_isolated_batch(
    *,
    state_root: str,
    data_root: str | None,
    scenario_id: str,
    sessions: int,
    workers: int,
    executor_kind: str,
    behavior: str,
    run_prefix: str,
) -> dict[str, Any]:
    jobs = [
        {
            "session_id": f"{run_prefix}-iso-{idx:04d}",
            "state_root": state_root,
            "data_root": data_root,
            "scenario_id": scenario_id,
            "behavior": behavior,
            "job_index": idx,
        }
        for idx in range(sessions)
    ]
    executor_cls = _executor_class(executor_kind)
    with executor_cls(max_workers=workers) as executor:
        results = list(executor.map(run_isolated_session, jobs))
    summary = _summarize_worker_results(results)
    summary["mode"] = "isolated"
    summary["behavior"] = behavior
    summary["sessions_requested"] = sessions
    return {"summary": summary, "results": results}


def run_contention_batch(
    *,
    state_root: str,
    data_root: str | None,
    scenario_id: str,
    workers: int,
    executor_kind: str,
    run_prefix: str,
) -> dict[str, Any]:
    env = ServerFaultSupabaseEnvironment(data_root=data_root, state_root=state_root)
    shared_session_id = f"{run_prefix}-shared"
    env.create_session(shared_session_id, scenario_id, overwrite=True)
    jobs = [
        {
            "session_id": shared_session_id,
            "state_root": state_root,
            "data_root": data_root,
            "incident": {
                "incident_id": TARGET_INCIDENT_IDS[idx],
            },
        }
        for idx in range(workers)
    ]
    executor_cls = _executor_class(executor_kind)
    with executor_cls(max_workers=workers) as executor:
        results = list(executor.map(run_contention_worker, jobs))

    shared_summary = env.session_summary(shared_session_id)
    expected_actions = workers * 2
    expected_rows = workers
    expected_audits = workers * 2
    summary = _summarize_worker_results(results)
    summary.update(
        {
            "mode": "contention",
            "shared_session_id": shared_session_id,
            "expected_actions": expected_actions,
            "actual_actions": shared_summary.get("action_count", 0),
            "action_count_match": shared_summary.get("action_count", 0) == expected_actions,
            "expected_rows": expected_rows,
            "actual_rows": shared_summary.get("supabase_rows_count", 0),
            "row_count_match": shared_summary.get("supabase_rows_count", 0) == expected_rows,
            "expected_audits": expected_audits,
            "actual_audits": shared_summary.get("audit_logs_count", 0),
            "audit_count_match": shared_summary.get("audit_logs_count", 0) == expected_audits,
        }
    )
    return {"summary": summary, "results": results}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Concurrent stress test for the server_fault_supabase_env environment.")
    parser.add_argument("--scenario-id", default=SCENARIO_ID, help="Scenario to execute.")
    parser.add_argument("--data-root", default=None, help="Optional override for the environment data directory.")
    parser.add_argument("--state-root", default=None, help="Optional persistent state root. Default is a temp dir.")
    parser.add_argument("--executor", choices=["threads", "processes"], default="processes")
    parser.add_argument("--mode", choices=["isolated", "contention", "both"], default="both")
    parser.add_argument("--sessions", type=int, default=16, help="Number of isolated sessions to run.")
    parser.add_argument("--workers", type=int, default=3, help="Number of concurrent workers.")
    parser.add_argument("--behavior", choices=["good", "partial", "mixed"], default="good")
    parser.add_argument("--keep-state", action="store_true", help="Keep the state root after the run.")
    parser.add_argument("--report-json", default=None, help="Optional path for a JSON report.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.sessions < 1:
        raise SystemExit("--sessions must be >= 1")
    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")
    if args.mode in {"contention", "both"} and args.workers > len(TARGET_INCIDENT_IDS):
        raise SystemExit(f"--workers must be <= {len(TARGET_INCIDENT_IDS)} for contention mode")

    run_prefix = f"server-fault-{_utc_stamp()}-{random.randint(1000, 9999)}"
    cleanup_state_root = False
    if args.state_root:
        state_root = Path(args.state_root).resolve()
        state_root.mkdir(parents=True, exist_ok=True)
    else:
        state_root = Path(tempfile.mkdtemp(prefix="server_fault_supabase_env_concurrency_")).resolve()
        cleanup_state_root = not args.keep_state

    started = time.perf_counter()
    report: dict[str, Any] = {
        "run_prefix": run_prefix,
        "scenario_id": args.scenario_id,
        "executor": args.executor,
        "mode": args.mode,
        "state_root": str(state_root),
    }

    exit_code = 0
    try:
        if args.mode in {"isolated", "both"}:
            report["isolated"] = run_isolated_batch(
                state_root=str(state_root),
                data_root=args.data_root,
                scenario_id=args.scenario_id,
                sessions=args.sessions,
                workers=args.workers,
                executor_kind=args.executor,
                behavior=args.behavior,
                run_prefix=run_prefix,
            )
            if report["isolated"]["summary"]["errors"] > 0:
                exit_code = 1

        if args.mode in {"contention", "both"}:
            report["contention"] = run_contention_batch(
                state_root=str(state_root),
                data_root=args.data_root,
                scenario_id=args.scenario_id,
                workers=args.workers,
                executor_kind=args.executor,
                run_prefix=run_prefix,
            )
            contention_summary = report["contention"]["summary"]
            if (
                contention_summary["errors"] > 0
                or not contention_summary["action_count_match"]
                or not contention_summary["row_count_match"]
                or not contention_summary["audit_count_match"]
            ):
                exit_code = 1

        report["elapsed_s"] = round(time.perf_counter() - started, 3)
        print(json.dumps(report, indent=2, ensure_ascii=False))

        if args.report_json:
            report_path = Path(args.report_json).resolve()
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    finally:
        if cleanup_state_root:
            shutil.rmtree(state_root, ignore_errors=True)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
