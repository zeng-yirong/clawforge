from __future__ import annotations

import json
import os
import re
import shutil
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator


SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
DEFAULT_BASE_TIME = "2026-06-14T09:00:00"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.{os.getpid()}.{time.monotonic_ns()}.tmp")
    try:
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def _action_timestamp(base_time: str, action_index: int) -> str:
    normalized = base_time.replace("Z", "+00:00")
    base = datetime.fromisoformat(normalized)
    return (base + timedelta(minutes=action_index)).isoformat()


class SessionStore:
    def __init__(self, state_root: str | None = None):
        if state_root is None:
            state_root = os.environ.get(
                "TRAVEL_POLICY_STATE_ROOT",
                os.path.join(os.environ.get("TEMP", "/tmp"), "travel_policy_sessions"),
            )
        self.state_root = Path(state_root).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)

    def validate_session_id(self, session_id: str) -> str:
        if not SESSION_ID_RE.fullmatch(session_id):
            raise ValueError(
                "Invalid session_id. Use only letters, numbers, underscore, dot, or dash, max length 128."
            )
        return session_id

    def _session_dir(self, session_id: str) -> Path:
        return self.state_root / self.validate_session_id(session_id)

    def _session_file(self, session_id: str) -> Path:
        return self._session_dir(session_id) / "session.json"

    def _lock_file(self, session_id: str) -> Path:
        return self._session_dir(session_id) / ".lock"

    @contextmanager
    def session_lock(self, session_id: str, timeout_s: float = 5.0, poll_s: float = 0.05) -> Iterator[None]:
        session_dir = self._session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self._lock_file(session_id)
        started = time.monotonic()
        while True:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(str(os.getpid()))
                break
            except FileExistsError:
                if time.monotonic() - started >= timeout_s:
                    raise TimeoutError(f"Timed out waiting for session lock: {session_id}") from None
                time.sleep(poll_s)

        try:
            yield
        finally:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass

    def create_session(self, session_id: str, scenario_id: str, repo) -> dict[str, Any]:
        with self.session_lock(session_id):
            session_dir = self._session_dir(session_id)
            session_file = self._session_file(session_id)
            if session_file.exists():
                # Remove old session payload after the lock has been acquired.
                for child in session_dir.iterdir():
                    if child.name != ".lock":
                        if child.is_dir():
                            shutil.rmtree(child)
                        else:
                            child.unlink()
            scenario = repo.get_scenario(scenario_id)
            base_time = scenario.get("base_time") or scenario.get("current_time") or DEFAULT_BASE_TIME
            session = {
                "session_id": session_id,
                "scenario_id": scenario_id,
                "created_at": base_time,
                "meta": {
                    "base_time": base_time,
                    "action_index": 0,
                },
                "policy_ids": scenario.get("policy_ids", []),
                "platform_ids": scenario.get("platform_ids", []),
                "actions": [],
                "approvals": [],
                "bookings": [],
                "alerts": [],
                "reports": [],
            }
            _atomic_write_json(session_file, session)
            return session

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        session_file = self._session_file(session_id)
        if not session_file.exists():
            return None
        return json.loads(session_file.read_text(encoding="utf-8"))

    def _save_session(self, session_id: str, session: dict[str, Any]) -> None:
        _atomic_write_json(self._session_file(session_id), session)

    def record_action_unlocked(self, session_id: str, action: str, params: dict[str, Any], result: Any):
        session = self.get_session(session_id)
        if session is None:
            raise RuntimeError(f"Session {session_id} not found")
        action_index = len(session["actions"])
        base_time = session.get("meta", {}).get("base_time") or session.get("created_at") or DEFAULT_BASE_TIME
        action_record = {
            "action": action,
            "params": params,
            "result": result,
            "timestamp": _action_timestamp(base_time, action_index),
            "action_index": action_index,
        }
        session["actions"].append(action_record)
        session.setdefault("meta", {})["action_index"] = action_index + 1
        self._save_session(session_id, session)
        return action_record

    def record_action(self, session_id: str, action: str, params: dict[str, Any], result: Any):
        with self.session_lock(session_id):
            return self.record_action_unlocked(session_id, action, params, result)

    def reset_session(self, session_id: str, repo):
        session = self.get_session(session_id)
        if session is None:
            raise RuntimeError(f"Session {session_id} not found")
        scenario_id = session["scenario_id"]
        return self.create_session(session_id, scenario_id, repo)

    def delete_session(self, session_id: str):
        session_dir = self._session_dir(session_id)
        if session_dir.exists():
            shutil.rmtree(session_dir)
