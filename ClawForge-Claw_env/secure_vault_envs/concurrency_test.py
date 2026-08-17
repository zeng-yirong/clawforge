from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from secure_vault_envs.environment import SecureVaultEnvironment
from secure_vault_envs.repository import VaultRepository
from secure_vault_envs.store import SessionStore


def run_concurrent_test(num_sessions: int = 10) -> dict:
    data_root = Path(__file__).parent / "data"
    state_root = Path(__file__).parent / ".test_state_concurrent"
    state_root.mkdir(exist_ok=True)

    for d in state_root.iterdir():
        if d.is_dir():
            import shutil
            shutil.rmtree(d)

    repo = VaultRepository(data_root)
    env = SecureVaultEnvironment(data_root, state_root)
    sessions = []
    for i in range(num_sessions):
        result = env.prepare_rollout("credential_management_001")
        sessions.append(result["session_id"])

    errors = []
    lock = threading.Lock()

    def worker(session_id: str, idx: int):
        try:
            s_env = SecureVaultEnvironment(data_root, state_root)
            action_idx = 0

            gen_result = s_env.execute_action(session_id, "generate_password", action_idx, length=16, charset="complex", policy={"min_length": 12, "require_uppercase": True, "require_lowercase": True, "require_digits": True, "require_special": True})
            action_idx += 1
            if gen_result.get("status") != "success":
                with lock:
                    errors.append(f"Session {session_id}: generate_password failed")
                return

            time.sleep(0.01)

            password = gen_result.get("data", {}).get("password", "TestPass123!")
            store_result = s_env.execute_action(session_id, "store_credential", action_idx, credential_data={
                "platform": f"platform_{idx}",
                "username": f"user_{idx}@example.com",
                "password": password,
                "category_id": "work_email",
            })
            action_idx += 1
            if store_result.get("status") != "success":
                with lock:
                    errors.append(f"Session {session_id}: store_credential failed")
                return

            time.sleep(0.01)

            autofill_result = s_env.execute_action(session_id, "setup_autofill", action_idx, platform=f"platform_{idx}", field_mappings={"username": ["user", "login"], "password": ["pass", "pwd"]})
            action_idx += 1
            if autofill_result.get("status") != "success":
                with lock:
                    errors.append(f"Session {session_id}: setup_autofill failed")
                return

            time.sleep(0.01)

            cred_id = store_result.get("data", {}).get("credential_id", f"cred_{idx}")
            class_result = s_env.execute_action(session_id, "classify_credential", action_idx, credential_id=cred_id, category_id="work_email")
            action_idx += 1
            if class_result.get("status") != "success":
                with lock:
                    errors.append(f"Session {session_id}: classify_credential failed")
                return

            check_result = s_env.execute_action(session_id, "check_password_strength", action_idx, password=password, policy={"min_length": 12, "require_uppercase": True, "require_lowercase": True, "require_digits": True, "require_special": True})
            action_idx += 1
            if check_result.get("status") != "success":
                with lock:
                    errors.append(f"Session {session_id}: check_password_strength failed")
                return

            retrieved = s_env.execute_action(session_id, "retrieve_credential", action_idx, platform=f"platform_{idx}")
            action_idx += 1
            if retrieved.get("status") != "success":
                with lock:
                    errors.append(f"Session {session_id}: retrieve_credential failed")
                return

            retrieved_password = retrieved.get("data", {}).get("password", "")
            if retrieved_password != password:
                with lock:
                    errors.append(f"Session {session_id}: password mismatch (contaminated session)")

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
        if len(session.get("actions", [])) != 6:
            errors.append(f"Session {sid} has {len(session.get('actions', []))} actions, expected 6")

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
