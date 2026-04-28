"""Layer 2 — atomic file writes (idempotency pattern #1).

Naive ``open(path, "w")`` is not safe to retry. If the process crashes
mid-write you get a half-written file. If another part of the agent
reads the file before the write finishes it sees garbage.

Fix: write to a temp file in the *same directory*, fsync, then rename.
``os.replace`` is atomic on every major operating system: either the
target file has the new content completely, or it has the old content.
There is no halfway state.
"""
import os
import tempfile


def write_file_safe(path: str, content: str) -> str:
    """Write atomically. Calling this twice with the same arguments
    produces the same final file every time."""
    # 1. write to a temp file in the same directory (rename must be on the same FS)
    dir_ = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_, prefix=".tmp.", suffix=".part")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # force the bytes to disk
        # 2. rename — atomic on every major OS
        os.replace(tmp_path, path)
        return f"OK: wrote {len(content)} chars to {path}"
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
