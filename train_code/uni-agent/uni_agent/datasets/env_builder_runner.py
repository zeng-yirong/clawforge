from __future__ import annotations

import builtins
import io
import os
import runpy
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


def _parent_dir_for_write(file: Any, mode: str | None) -> Path | None:
    if isinstance(file, int):
        return None
    if not isinstance(file, (str, bytes, os.PathLike)):
        return None

    mode = mode or "r"
    if not any(flag in mode for flag in ("w", "a", "x", "+")):
        return None

    parent = Path(file).parent
    if str(parent) in {"", "."}:
        return None
    return parent


@contextmanager
def _auto_create_parent_dirs() -> Iterator[None]:
    original_builtin_open = builtins.open
    original_io_open = io.open

    def _patched_builtin_open(file: Any, mode: str = "r", *args: Any, **kwargs: Any):
        parent = _parent_dir_for_write(file, mode)
        if parent is not None:
            parent.mkdir(parents=True, exist_ok=True)
        return original_builtin_open(file, mode, *args, **kwargs)

    def _patched_io_open(file: Any, mode: str = "r", *args: Any, **kwargs: Any):
        parent = _parent_dir_for_write(file, mode)
        if parent is not None:
            parent.mkdir(parents=True, exist_ok=True)
        return original_io_open(file, mode, *args, **kwargs)

    builtins.open = _patched_builtin_open
    io.open = _patched_io_open
    try:
        yield
    finally:
        builtins.open = original_builtin_open
        io.open = original_io_open


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        raise SystemExit("Usage: python -m uni_agent.datasets.env_builder_runner <env_builder.py> [args...]")

    script_path = Path(args[0]).expanduser().resolve()
    if not script_path.exists():
        raise FileNotFoundError(f"env_builder script not found: {script_path}")

    original_argv = sys.argv
    try:
        sys.argv = [str(script_path), *args[1:]]
        with _auto_create_parent_dirs():
            runpy.run_path(str(script_path), run_name="__main__")
    finally:
        sys.argv = original_argv

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
