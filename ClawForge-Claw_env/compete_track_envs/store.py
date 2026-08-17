from __future__ import annotations

import json
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.{os.getpid()}.{time.monotonic_ns()}.tmp")
    try:
        tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


class SessionStore:
    def __init__(self, state_root: str | Path):
        self.state_root = Path(state_root).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)

    def validate_session_id(self, session_id: str) -> str:
        if not SESSION_ID_RE.fullmatch(session_id):
            raise ValueError(
                "Invalid session_id. Use only letters, numbers, underscore, dot, or dash, max length 128."
            )
        return session_id

    def session_dir(self, session_id: str) -> Path:
        return self.state_root / self.validate_session_id(session_id)

    def session_file(self, session_id: str) -> Path:
        return self.session_dir(session_id) / "session.json"

    def lock_file(self, session_id: str) -> Path:
        return self.session_dir(session_id) / ".lock"

    def exists(self, session_id: str) -> bool:
        return self.session_file(session_id).exists()

    @contextmanager
    def session_lock(self, session_id: str, timeout_s: float = 5.0, poll_s: float = 0.05) -> Iterator[None]:
        session_dir = self.session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self.lock_file(session_id)
        started = time.monotonic()
        while True:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w", encoding="utf-8") as lock_handle:
                    lock_handle.write(str(os.getpid()))
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

    def load_session(self, session_id: str) -> dict[str, Any]:
        session_path = self.session_file(session_id)
        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        return json.loads(session_path.read_text(encoding="utf-8"))

    def save_session(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        _atomic_write_json(self.session_file(session_id), payload)
        return payload

    def save_session_unlocked(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        _atomic_write_json(self.session_file(session_id), payload)
        return payload

    def create_session(self, session_id: str, payload: dict[str, Any], overwrite: bool = False) -> dict[str, Any]:
        with self.session_lock(session_id):
            if self.exists(session_id) and not overwrite:
                raise FileExistsError(f"Session already exists: {session_id}")
            return self.save_session(session_id, payload)

    def delete_session(self, session_id: str) -> None:
        session_dir = self.session_dir(session_id)
        if session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)

    def list_sessions(self) -> list[str]:
        if not self.state_root.exists():
            return []
        return [d.name for d in self.state_root.iterdir() if d.is_dir() and d.name != ".locks"]
