"""
Concurrency test for LogisticsEnvironment.

Validates session isolation and locking under parallel execution.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))


def _run_worker(args: tuple[str, str, str, int]) -> dict[str, Any]:
    session_id, scenario_id, state_root, worker_id = args
    os.environ["LOGISTICS_SESSION_ID"] = session_id
    os.environ["LOGISTICS_STATE_ROOT"] = state_root
    os.environ["LOGISTICS_SCENARIO_ID"] = scenario_id

    from logistics_envs.environment import LogisticsEnvironment

    env = LogisticsEnvironment(state_root=state_root)
    results = []

    try:
        for i in range(3):
            action_index = i + worker_id * 10
            try:
                returns = env.list_returns(session_id)
                results.append({"worker_id": worker_id, "action": "list_returns", "success": True})
                time.sleep(random.uniform(0.01, 0.05))
            except Exception as e:
                results.append({"worker_id": worker_id, "action": "list_returns", "success": False, "error": str(e)})

    except Exception as e:
        results.append({"worker_id": worker_id, "action": "error", "success": False, "error": str(e)})

    return {"worker_id": worker_id, "session_id": session_id, "results": results}


def _run_isolated_session_test(args: tuple[str, str, str, int, int]) -> dict[str, Any]:
    session_id, scenario_id, state_root, worker_id, num_actions = args
    os.environ["LOGISTICS_SESSION_ID"] = session_id
    os.environ["LOGISTICS_STATE_ROOT"] = state_root
    os.environ["LOGISTICS_SCENARIO_ID"] = scenario_id

    from logistics_envs.environment import LogisticsEnvironment

    env = LogisticsEnvironment(state_root=state_root)
    successes = 0
    failures = 0

    try:
        for i in range(num_actions):
            try:
                inventory = env.list_inventory(session_id, limit=5)
                if inventory.get("data"):
                    successes += 1
            except Exception:
                failures += 1
            time.sleep(random.uniform(0.005, 0.02))
    except Exception as e:
        failures += 1

    return {
        "worker_id": worker_id,
        "session_id": session_id,
        "successes": successes,
        "failures": failures,
    }


def run_contention_test(
    sessions: int = 16,
    workers: int = 8,
    contention_loops: int = 4,
    state_root: str = ".tmp/logistics_contention",
) -> dict[str, Any]:
    from logistics_envs.environment import LogisticsEnvironment

    base_path = Path(state_root)
    base_path.mkdir(parents=True, exist_ok=True)

    session_ids = [f"contention-test-{i}" for i in range(sessions)]
    scenario_id = "fulfillment_inventory_reconcile"

    env = LogisticsEnvironment(state_root=str(base_path))
    for sid in session_ids:
        try:
            env.create_session(sid, scenario_id)
        except FileExistsError:
            pass

    tasks = []
    for session_id in session_ids:
        for worker_id in range(workers):
            tasks.append((session_id, scenario_id, str(base_path), worker_id))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(_run_worker, tasks))

    failures = sum(1 for r in results if not all(a["success"] for a in r["results"]))
    return {
        "test": "contention",
        "sessions": sessions,
        "workers": workers,
        "total_tasks": len(tasks),
        "failures": failures,
        "results": results,
    }


def run_isolation_test(
    sessions: int = 16,
    workers: int = 8,
    state_root: str = ".tmp/logistics_isolation",
) -> dict[str, Any]:
    from logistics_envs.environment import LogisticsEnvironment

    base_path = Path(state_root)
    base_path.mkdir(parents=True, exist_ok=True)

    session_ids = [f"isolation-test-{i}" for i in range(sessions)]
    scenario_id = "fulfillment_inventory_reconcile"

    env = LogisticsEnvironment(state_root=str(base_path))
    for sid in session_ids:
        try:
            env.create_session(sid, scenario_id)
        except FileExistsError:
            pass

    tasks = []
    for session_id in session_ids:
        for worker_id in range(workers):
            tasks.append((session_id, scenario_id, str(base_path), worker_id, 3))

    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(_run_isolated_session_test, tasks))

    total_successes = sum(r["successes"] for r in results)
    total_failures = sum(r["failures"] for r in results)
    return {
        "test": "isolation",
        "sessions": sessions,
        "workers": workers,
        "total_successes": total_successes,
        "total_failures": total_failures,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Concurrency test for LogisticsEnvironment")
    parser.add_argument("--mode", choices=["both", "contention", "isolation"], default="both")
    parser.add_argument("--executor", choices=["threads", "processes"], default="threads")
    parser.add_argument("--sessions", type=int, default=16)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--contention-loops", type=int, default=4)
    parser.add_argument("--report-json", type=str, default=None)

    args = parser.parse_args()

    contention_result = None
    isolation_result = None

    if args.mode in {"both", "contention"}:
        contention_result = run_contention_test(
            sessions=args.sessions,
            workers=args.workers,
            contention_loops=args.contention_loops,
        )
        print(f"Contention test: {contention_result['failures']} failures out of {contention_result['total_tasks']} tasks")

    if args.mode in {"both", "isolation"}:
        isolation_result = run_isolation_test(
            sessions=args.sessions,
            workers=args.workers,
        )
        print(f"Isolation test: {isolation_result['total_failures']} failures, {isolation_result['total_successes']} successes")

    if args.mode == "both":
        combined = {"contention": contention_result, "isolation": isolation_result}
    elif args.mode == "contention":
        combined = {"contention": contention_result}
    else:
        combined = {"isolation": isolation_result}

    if args.report_json:
        Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_json).write_text(json.dumps(combined, indent=2))
        print(f"Report written to: {args.report_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
