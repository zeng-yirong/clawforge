from __future__ import annotations

import json
import os
import shutil
import tempfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .environment import MailClientEnvironment


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_isolated_session(session_id: str, data_root: Path, state_root: Path) -> dict[str, Any]:
    env = MailClientEnvironment(data_root=data_root, state_root=state_root)
    scenario_id = "email_inbox_automation"
    env.create_session(session_id, scenario_id)

    env.read_email(session_id, "mc_001")
    env.read_email(session_id, "mc_004")
    env.read_attachment(session_id, "mcatt_001")
    env.read_attachment(session_id, "mcatt_003")

    env.classify_email(session_id, "mc_001", "work", ["work", "urgent"])
    env.classify_email(session_id, "mc_002", "finance", ["finance"])
    env.classify_email(session_id, "mc_005", "archive", ["newsletter"])
    env.classify_email(session_id, "mc_007", "trash", ["spam"])

    env.archive_email(session_id, "mc_005")
    env.delete_email(session_id, "mc_007")

    env.create_todo(
        session_id,
        source_email_id="mc_001",
        title="Review Q3 Planning Document",
        description="Review the Q3 planning document for roadmap, resource allocation, and timeline adjustment",
        priority="high",
    )
    env.create_todo(
        session_id,
        source_email_id="mc_004",
        title="Client Feedback Changes",
        description="Update dashboard colors, add export functionality, improve performance",
        priority="normal",
    )

    env.create_reply(
        session_id,
        target_email_id="mc_004",
        content="Thank you for the feedback. We acknowledge the change requests and will provide a timeline by end of week.",
    )
    env.create_reply(
        session_id,
        target_email_id="mc_003",
        content="I will review the code PR today and provide feedback.",
    )

    result = env.evaluate_session(session_id)
    return result


def run_partial_flow(session_id: str, data_root: Path, state_root: Path) -> dict[str, Any]:
    env = MailClientEnvironment(data_root=data_root, state_root=state_root)
    scenario_id = "email_inbox_automation"
    env.create_session(session_id, scenario_id)

    env.classify_email(session_id, "mc_001", "work", ["work"])
    env.archive_email(session_id, "mc_005")

    result = env.evaluate_session(session_id)
    return result


def run_contention_worker(shared_session_id: str, data_root: Path, state_root: Path, worker_id: int, loops: int) -> dict[str, Any]:
    env = MailClientEnvironment(data_root=data_root, state_root=state_root)
    results = []

    for i in range(loops):
        try:
            env.read_email(shared_session_id, f"mc_{(i % 3) + 1:03d}")
            env.classify_email(shared_session_id, f"mc_{(i % 3) + 1:03d}", "work", ["work"])
            results.append({"worker_id": worker_id, "loop": i, "success": True})
        except Exception as e:
            results.append({"worker_id": worker_id, "loop": i, "success": False, "error": str(e)})

    return {"worker_id": worker_id, "results": results}


def run_concurrency_test(
    data_root: Path,
    num_workers: int = 4,
    use_processes: bool = False,
) -> dict[str, Any]:
    ExecutorClass = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    with tempfile.TemporaryDirectory() as tmpdir:
        state_root = Path(tmpdir) / "state"
        state_root.mkdir(parents=True, exist_ok=True)

        isolated_sessions = []
        with ExecutorClass(max_workers=num_workers) as executor:
            futures = []
            for i in range(num_workers):
                session_id = f"mc-isolated-{_utc_stamp()}-{i}"
                future = executor.submit(run_isolated_session, session_id, data_root, state_root)
                futures.append((session_id, future))

            for session_id, future in futures:
                try:
                    result = future.result(timeout=30)
                    isolated_sessions.append({"session_id": session_id, "result": result, "success": True})
                except Exception as e:
                    isolated_sessions.append({"session_id": session_id, "success": False, "error": str(e)})

        contention_session_id = f"mc-contention-{_utc_stamp()}"
        env = MailClientEnvironment(data_root=data_root, state_root=state_root)
        env.create_session(contention_session_id, "email_inbox_automation")

        with ExecutorClass(max_workers=num_workers) as executor:
            futures = []
            for i in range(num_workers):
                future = executor.submit(run_contention_worker, contention_session_id, data_root, state_root, i, 3)
                futures.append(future)

            contention_results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    contention_results.append(result)
                except Exception as e:
                    contention_results.append({"success": False, "error": str(e)})

    return {
        "isolated_sessions": isolated_sessions,
        "contention_session_id": contention_session_id,
        "contention_results": contention_results,
        "all_passed": all(s.get("success", False) for s in isolated_sessions),
    }


if __name__ == "__main__":
    data_root = Path(__file__).parent / "data"
    result = run_concurrency_test(data_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
