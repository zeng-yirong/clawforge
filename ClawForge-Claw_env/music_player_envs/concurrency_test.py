from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

from .environment import MusicEnvironment
from .repository import MusicRepository


def run_concurrent_test(num_sessions: int = 10) -> dict:
    data_root = Path(__file__).parent / "data"
    state_root = Path(__file__).parent / ".test_state_concurrent"
    state_root.mkdir(exist_ok=True)

    for d in state_root.iterdir():
        if d.is_dir():
            import shutil
            shutil.rmtree(d)

    repo = MusicRepository(data_root)
    scenario = repo.get_scenario("music_in_car")

    env = MusicEnvironment(data_root, state_root)
    sessions = []
    for i in range(num_sessions):
        result = env.prepare_rollout("music_in_car")
        sessions.append(result["session_id"])

    errors = []
    lock = threading.Lock()

    def worker(session_id: str, idx: int):
        try:
            s_env = MusicEnvironment(data_root, state_root)
            action_idx = 0
            s_env.execute_action(session_id, "play", action_idx, song_id="song_001")
            action_idx += 1
            time.sleep(0.01)
            s_env.execute_action(session_id, "pause", action_idx)
            action_idx += 1
            time.sleep(0.01)
            s_env.execute_action(session_id, "resume", action_idx)
            action_idx += 1
            time.sleep(0.01)
            s_env.execute_action(session_id, "next", action_idx)
            action_idx += 1
            s_env.execute_action(session_id, "status", action_idx)
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
        if len(session.get("actions", [])) != 5:
            errors.append(f"Session {sid} has {len(session.get('actions', []))} actions, expected 5")

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
