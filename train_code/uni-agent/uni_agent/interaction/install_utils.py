import shlex
from pathlib import PurePath


def normalize_uploaded_text_file_cmd(path: str | PurePath) -> str:
    """Return a runtime command that strips CRLF line endings in-place."""
    path_str = PurePath(path).as_posix() if isinstance(path, PurePath) else str(path)
    script = (
        "from pathlib import Path; "
        f"p = Path({path_str!r}); "
        "p.write_bytes(p.read_bytes().replace(b'\\r\\n', b'\\n'))"
    )
    return f"python3 -c {shlex.quote(script)}"