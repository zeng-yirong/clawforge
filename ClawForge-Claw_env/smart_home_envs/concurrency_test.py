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

from claw_envs.smart_home_envs import SmartHomeEnvironment


GOOD_AC_SETTING = {"temperature": 22, "mode": "cool", "fan_speed": "auto"}
GOOD_HUMIDIFIER_SETTING = {"humidity_level": 45, "mode": "auto"}
GOOD_PLUG_SETTING = True


@dataclass
class WorkerResult:
    session_id: str
    mode: str
    status: str
    elapsed_ms: float
    overall_score: float | None = None
    action_count: int | None = None
    device_adjustments: int | None = None
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


def _perform_optimal_flow(env: SmartHomeEnvironment, session_id: str) -> dict[str, Any]:
    weather = env.get_weather(session_id)
    weather_data = weather["data"]
    temp = weather_data.get("temperature", 25)
    humidity = weather_data.get("humidity", 50)

    env.analyze_weather_comfort(session_id, temp, humidity)
    env.get_electricity_rate(session_id)
    env.get_daily_rate_schedule(session_id)
    env.get_weather_forecast(session_id, hours_ahead=24)
    env.check_extreme_weather(session_id)

    devices = env.get_all_devices(session_id)
    device_list = devices["data"]

    ac_devices = [d for d in device_list if d["type"] == "air_conditioner"]
    if ac_devices:
        env.set_air_conditioner(
            session_id,
            device_id=ac_devices[0]["device_id"],
            temperature=22,
            mode="cool",
            fan_speed="auto",
        )

    humidifier_devices = [d for d in device_list if d["type"] == "humidifier"]
    if humidifier_devices:
        env.set_humidifier(
            session_id,
            device_id=humidifier_devices[0]["device_id"],
            humidity_level=45,
            mode="auto",
        )

    env.calculate_recommended_temperature(session_id, current_temp=temp, current_humidity=humidity)
    env.check_cost_saving_opportunity(session_id, device_type="air_conditioner", current_setting=GOOD_AC_SETTING)

    for device in device_list:
        env.get_device_status(session_id, device["device_id"])

    return env.evaluate_session(session_id)


def _perform_suboptimal_flow(env: SmartHomeEnvironment, session_id: str) -> dict[str, Any]:
    env.get_weather(session_id)
    devices = env.get_all_devices(session_id)
    device_list = devices["data"]

    ac_devices = [d for d in device_list if d["type"] == "air_conditioner"]
    if ac_devices:
        env.set_air_conditioner(
            session_id,
            device_id=ac_devices[0]["device_id"],
            temperature=18,
            mode="cool",
            fan_speed="high",
        )

    return env.evaluate_session(session_id)


def _perform_partial_flow(env: SmartHomeEnvironment, session_id: str) -> dict[str, Any]:
    env.get_weather(session_id)
    return env.evaluate_session(session_id)


def _choose_behavior(index: int, behavior: str) -> str:
    if behavior != "mixed":
        return behavior
    table = ("optimal", "optimal", "optimal", "partial", "suboptimal")
    return table[index % len(table)]


def run_isolated_session(job: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    env = SmartHomeEnvironment(data_root=job.get("data_root"), state_root=job["state_root"])
    session_id = job["session_id"]
    behavior = _choose_behavior(job["job_index"], job["behavior"])

    try:
        env.create_session(session_id, job["scenario_id"], overwrite=False)
        if behavior == "optimal":
            evaluation = _perform_optimal_flow(env, session_id)
        elif behavior == "suboptimal":
            evaluation = _perform_suboptimal_flow(env, session_id)
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
            overall_score=evaluation.get("overall_score", evaluation.get("total_score")),
            action_count=summary["action_count"],
            device_adjustments=summary["active_devices_count"],
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
    env = SmartHomeEnvironment(data_root=job.get("data_root"), state_root=job["state_root"])
    session_id = job["session_id"]
    worker_id = job["worker_id"]
    loops = job["loops"]

    try:
        for loop_idx in range(loops):
            env.get_weather(session_id)
            env.get_electricity_rate(session_id)

            devices = env.get_all_devices(session_id)
            device_list = devices["data"]

            ac_devices = [d for d in device_list if d["type"] == "air_conditioner"]
            if ac_devices and loop_idx % 2 == 0:
                env.set_air_conditioner(
                    session_id,
                    device_id=ac_devices[0]["device_id"],
                    temperature=22 + (loop_idx % 3),
                    mode="cool",
                    fan_speed="auto",
                )

            humidifier_devices = [d for d in device_list if d["type"] == "humidifier"]
            if humidifier_devices and loop_idx % 2 == 1:
                env.set_humidifier(
                    session_id,
                    device_id=humidifier_devices[0]["device_id"],
                    humidity_level=40 + (loop_idx % 10),
                    mode="auto",
                )

        summary = env.session_summary(session_id)
        result = WorkerResult(
            session_id=session_id,
            mode="contention",
            status="ok",
            elapsed_ms=(time.perf_counter() - started) * 1000,
            action_count=summary["action_count"],
            device_adjustments=summary["active_devices_count"],
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
    return {
        "summary": summary,
        "results": results,
    }


def run_contention_batch(
    *,
    state_root: str,
    data_root: str | None,
    scenario_id: str,
    workers: int,
    loops_per_worker: int,
    executor_kind: str,
    run_prefix: str,
) -> dict[str, Any]:
    env = SmartHomeEnvironment(data_root=data_root, state_root=state_root)
    shared_session_id = f"{run_prefix}-shared"
    env.create_session(shared_session_id, scenario_id, overwrite=True)

    jobs = [
        {
            "session_id": shared_session_id,
            "state_root": state_root,
            "data_root": data_root,
            "worker_id": idx,
            "loops": loops_per_worker,
        }
        for idx in range(workers)
    ]

    executor_cls = _executor_class(executor_kind)
    with executor_cls(max_workers=workers) as executor:
        results = list(executor.map(run_contention_worker, jobs))

    shared_summary = env.session_summary(shared_session_id)
    shared_eval = env.evaluate_session(shared_session_id)
    expected_actions = workers * loops_per_worker * 2

    summary = _summarize_worker_results(results)
    summary.update(
        {
            "mode": "contention",
            "shared_session_id": shared_session_id,
            "expected_actions": expected_actions,
            "actual_actions": shared_summary["action_count"],
            "action_count_match": shared_summary["action_count"] == expected_actions,
            "overall_score": shared_eval.get("overall_score", shared_eval.get("total_score")),
        }
    )
    return {
        "summary": summary,
        "results": results,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Concurrent stress test for the smart_home_envs environment.")
    parser.add_argument("--scenario-id", default="energy_aware_climate", help="Scenario to execute.")
    parser.add_argument("--data-root", default=None, help="Optional override for the smart_home_envs data directory.")
    parser.add_argument("--state-root", default=None, help="Optional persistent state root. Default is a temp dir.")
    parser.add_argument("--executor", choices=["threads", "processes"], default="processes")
    parser.add_argument("--mode", choices=["isolated", "contention", "both"], default="both")
    parser.add_argument("--sessions", type=int, default=32, help="Number of isolated sessions to run.")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent workers.")
    parser.add_argument(
        "--behavior",
        choices=["optimal", "suboptimal", "partial", "mixed"],
        default="optimal",
        help="Behavior pattern for isolated sessions.",
    )
    parser.add_argument(
        "--contention-loops",
        type=int,
        default=4,
        help="Number of action loops each contention worker performs against the shared session.",
    )
    parser.add_argument("--keep-state", action="store_true", help="Keep the state root after the run.")
    parser.add_argument("--report-json", default=None, help="Optional path for a JSON report.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.sessions < 1:
        raise SystemExit("--sessions must be >= 1")
    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")
    if args.contention_loops < 1:
        raise SystemExit("--contention-loops must be >= 1")

    run_prefix = f"smh-{_utc_stamp()}-{random.randint(1000, 9999)}"
    cleanup_state_root = False
    if args.state_root:
        state_root = Path(args.state_root).resolve()
        state_root.mkdir(parents=True, exist_ok=True)
    else:
        state_root = Path(tempfile.mkdtemp(prefix="smart_home_concurrency_")).resolve()
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
            isolated_summary = report["isolated"]["summary"]
            if isolated_summary["errors"] > 0:
                exit_code = 1

        if args.mode in {"contention", "both"}:
            report["contention"] = run_contention_batch(
                state_root=str(state_root),
                data_root=args.data_root,
                scenario_id=args.scenario_id,
                workers=args.workers,
                loops_per_worker=args.contention_loops,
                executor_kind=args.executor,
                run_prefix=run_prefix,
            )
            contention_summary = report["contention"]["summary"]
            if contention_summary["errors"] > 0 or not contention_summary["action_count_match"]:
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
