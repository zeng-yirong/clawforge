from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fcntl
    _HAS_FCNTL = True
except ImportError:
    _HAS_FCNTL = False


class SessionStore:
    _LOCK_TIMEOUT = 5

    def __init__(self, state_root: Path | str):
        self.state_root = Path(state_root)

    def _session_dir(self, session_id: str) -> Path:
        return self.state_root / session_id

    def _session_file(self, session_id: str) -> Path:
        return self._session_dir(session_id) / "session.json"

    def _lock_file(self, session_id: str) -> Path:
        return self._session_dir(session_id) / ".lock"

    def _acquire_lock(self, lock_fd: int) -> bool:
        if not _HAS_FCNTL:
            return True
        start = time.time()
        while True:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except BlockingIOError:
                if time.time() - start > self._LOCK_TIMEOUT:
                    return False
                time.sleep(0.05)

    def _release_lock(self, lock_fd: int) -> None:
        if not _HAS_FCNTL:
            return
        fcntl.flock(lock_fd, fcntl.LOCK_UN)

    def create_session(
        self,
        session_id: str,
        scenario_id: str,
        base_time: str,
        workspace_account: dict[str, Any],
    ) -> dict[str, Any]:
        session_dir = self._session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)

        session = {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "meta": {
                "base_time": base_time,
                "action_index": 0,
            },
            "workspace_account": workspace_account,
            "expense_state": {
                "policy_tier": None,
                "destination": None,
                "duration_days": 0,
                "calculated_budget": None,
                "loaded_consumption": None,
                "analysis_result": None,
                "report_generated": False,
            },
            "actions": [],
        }

        self._atomic_write(session_id, session)
        return session

    def _atomic_write(self, session_id: str, session: dict[str, Any]) -> None:
        session_file = self._session_file(session_id)
        lock_file = self._lock_file(session_id)
        lock_fd = os.open(lock_file, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            if not self._acquire_lock(lock_fd):
                raise RuntimeError(f"Failed to acquire lock for session {session_id}")
            self._release_lock(lock_fd)
        finally:
            os.close(lock_fd)

        temp_fd, temp_path = tempfile.mkstemp(dir=session_file.parent, suffix=".tmp")
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
            shutil.move(temp_path, session_file)
        except Exception:
            Path(temp_path).unlink(missing_ok=True)
            raise

    def load_session(self, session_id: str) -> dict[str, Any] | None:
        session_file = self._session_file(session_id)
        if not session_file.exists():
            return None
        with open(session_file, encoding="utf-8") as f:
            return json.load(f)

    def save_session(self, session_id: str, session: dict[str, Any]) -> None:
        self._atomic_write(session_id, session)

    def update_session(self, session_id: str, updater: callable) -> dict[str, Any]:
        session = self.load_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        updated = updater(session)
        self.save_session(session_id, updated)
        return updated

    def delete_session(self, session_id: str) -> None:
        session_dir = self._session_dir(session_id)
        if session_dir.exists():
            shutil.rmtree(session_dir)

    def session_exists(self, session_id: str) -> bool:
        return self._session_file(session_id).exists()
