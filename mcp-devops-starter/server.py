"""
mcp-devops-starter — your first MCP server, DevOps edition.

This server gives an AI assistant (like Claude) a small set of READ-ONLY
tools to inspect a machine's health: disk, memory, top processes, and log
tails. Nothing here mutates the system — it's the safe "first MCP server"
you can run on your laptop or a server with zero cloud credentials.

The docstring on each @mcp.tool() function IS the description the model
reads to decide when to call it. Write them like you're explaining the
tool to a junior engineer.

Run it:
    uv run server.py          # or: python server.py
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import psutil
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("devops-starter")

# Only allow log tails from directories we consider safe. Keeps the model
# (and a careless prompt) from reading arbitrary files like ~/.ssh/id_rsa.
ALLOWED_LOG_DIRS = ("/var/log", "/tmp", str(Path.home() / "logs"))


def _human_bytes(n: int) -> str:
    """Format a byte count as a human-readable string (e.g. '12.4 GB')."""
    step = 1024.0
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(n) < step:
            return f"{n:.1f} {unit}"
        n /= step
    return f"{n:.1f} EB"


@mcp.tool()
def check_disk_usage(path: str = "/") -> dict:
    """Check disk space usage for a filesystem path.

    Use this when someone asks why a server is "out of space", whether a
    disk is filling up, or how much free space is left. Returns total, used,
    free space and the percent used for the filesystem containing `path`.
    """
    usage = psutil.disk_usage(path)
    return {
        "path": path,
        "total": _human_bytes(usage.total),
        "used": _human_bytes(usage.used),
        "free": _human_bytes(usage.free),
        "percent_used": usage.percent,
    }


@mcp.tool()
def check_memory() -> dict:
    """Check current RAM and swap usage on this machine.

    Use this to diagnose memory pressure — a server that's slow, swapping,
    or at risk of the OOM killer. Returns total/used/available RAM, percent
    used, and swap usage.
    """
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "ram_total": _human_bytes(vm.total),
        "ram_used": _human_bytes(vm.used),
        "ram_available": _human_bytes(vm.available),
        "ram_percent_used": vm.percent,
        "swap_total": _human_bytes(swap.total),
        "swap_used": _human_bytes(swap.used),
        "swap_percent_used": swap.percent,
    }


@mcp.tool()
def list_top_processes(limit: int = 5, sort_by: str = "cpu") -> list[dict]:
    """List the heaviest running processes, sorted by CPU or memory.

    Use this to find what's eating a server's resources — "what's pegging
    the CPU?" or "which process is using all the RAM?". `sort_by` is either
    "cpu" or "memory". Returns up to `limit` processes with pid, name, and
    cpu/memory percentages.
    """
    if sort_by not in ("cpu", "memory"):
        raise ValueError("sort_by must be 'cpu' or 'memory'")

    # psutil's cpu_percent needs a baseline: the FIRST read is always 0.0.
    # So when sorting by CPU we prime every process, wait a beat, then read —
    # otherwise every process reports 0% and the tool looks broken.
    if sort_by == "cpu":
        for p in psutil.process_iter():
            try:
                p.cpu_percent(None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(0.3)

    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        info = p.info
        procs.append(
            {
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": round(info.get("cpu_percent") or 0.0, 1),
                "memory_percent": round(info.get("memory_percent") or 0.0, 1),
            }
        )

    key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
    procs.sort(key=lambda x: x[key], reverse=True)
    return procs[: max(1, limit)]


@mcp.tool()
def tail_log(path: str, lines: int = 50) -> str:
    """Read the last N lines of a log file (read-only).

    Use this to inspect recent log output when debugging an incident —
    e.g. the tail of /var/log/syslog or an application log. For safety,
    only files inside known log directories are allowed. Returns the last
    `lines` lines as text.
    """
    # Resolve BOTH sides so symlinks line up (e.g. macOS /tmp -> /private/tmp).
    # Comparing raw strings here would wrongly refuse legitimate files.
    resolved = Path(path).resolve()
    allowed = [Path(d).resolve() for d in ALLOWED_LOG_DIRS]
    if not any(resolved == d or resolved.is_relative_to(d) for d in allowed):
        raise PermissionError(
            f"Refusing to read {resolved}. Allowed dirs: {', '.join(ALLOWED_LOG_DIRS)}"
        )
    if not resolved.is_file():
        raise FileNotFoundError(f"No such file: {resolved}")

    # Read from the end so we don't load a multi-GB log into memory.
    with resolved.open("rb") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        block = 1024
        data = b""
        while end > 0 and data.count(b"\n") <= lines:
            step = min(block, end)
            end -= step
            f.seek(end)
            data = f.read(step) + data
    return b"\n".join(data.splitlines()[-lines:]).decode("utf-8", errors="replace")


if __name__ == "__main__":
    # Default transport is stdio — exactly what Claude Code launches and
    # talks to over stdin/stdout.
    mcp.run()
