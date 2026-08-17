from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from itinerary_envs.environment import ItineraryEnvironment
from itinerary_envs.repository import ItineraryRepository
from itinerary_envs.store import SessionStore


def run_concurrent_test(num_sessions: int = 10) -> dict:
    data_root = Path(__file__).parent / "data"
    state_root = Path(__file__).parent / ".test_state_concurrent"
    state_root.mkdir(exist_ok=True)

    for d in state_root.iterdir():
        if d.is_dir():
            import shutil
            shutil.rmtree(d)

    repo = ItineraryRepository(data_root)
    env = ItineraryEnvironment(data_root, state_root)
    sessions = []
    for i in range(num_sessions):
        result = env.prepare_rollout("itinerary_planning_001")
        sessions.append(result["session_id"])

    errors = []
    lock = threading.Lock()

    def worker(session_id: str, idx: int):
        try:
            s_env = ItineraryEnvironment(data_root, state_root)
            action_idx = 0
            s_env.execute_action(session_id, "load_cities", action_idx)
            action_idx += 1
            time.sleep(0.01)
            s_env.execute_action(session_id, "search_routes", action_idx, origin="SHA", destination="BJS")
            action_idx += 1
            time.sleep(0.01)
            s_env.execute_action(session_id, "plan_transfer", action_idx, origin="SHA", destination="CDU", waypoints=["WHN"])
            action_idx += 1
            s_env.execute_action(session_id, "generate_itinerary", action_idx, routes={"status": "success", "data": {"stops": ["SHA", "WHN", "CDU"], "legs": []}}, preferences={"route_preference": "balanced"})
        except Exception as e:
            with lock:
                errors.append(f"Session {session_id}: {e}")

    threads = []
    for i, sid in enumerate(sessions):
        t = threading.Thread(target=worker, args=(sid, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    for sid in sessions:
        session = env.store.load_session(sid)
        if session is None:
            errors.append(f"Session {sid} not found after test")
            continue
        if len(session.get("actions", [])) != 4:
            errors.append(f"Session {sid} has {len(session.get('actions', []))} actions, expected 4")

    import shutil
    shutil.rmtree(state_root, ignore_errors=True)

    return {
        "total_sessions": num_sessions,
        "errors": errors,
        "passed": len(errors) == 0,
    }


if __name__ == "__main__":
    result = run_concurrent_test()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["passed"] else 1)
