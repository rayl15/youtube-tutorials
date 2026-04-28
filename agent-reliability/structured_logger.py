"""Layer 4 — structured logging with a run_id.

Every agent invocation gets a short unique ``run_id``. Every tool call
gets logged with that run_id, the inputs, the outputs, and how long it
took. When something breaks in production, you grep for the run_id and
the whole timeline is right there.

Why JSON? Because CloudWatch on AWS reads JSON natively. You can filter
by field — ``show me all calls where success=false``, or
``show me all calls slower than 5 seconds``. That's observability.
"""
import json
import secrets
import sys
import time
from typing import Any


def create_run_id() -> str:
    """Short unique ID for one agent invocation. 8 chars — easy to grep."""
    return secrets.token_hex(4)


def log_tool_call(
    run_id: str,
    turn: int,
    tool_name: str,
    inputs: dict,
    result: Any,
    duration_ms: int,
) -> None:
    """Write one structured JSON line per tool call.

    ``success`` is true unless the tool either raised (caught upstream and
    converted to an ERROR string) or returned a string starting with
    ``ERROR``. This is the silent-failure-detection pattern: tools return
    error strings instead of throwing, and the logger treats those as
    failures so they show up in CloudWatch metric filters.
    """
    success = not (isinstance(result, str) and result.startswith("ERROR"))
    record = {
        "ts": int(time.time() * 1000),
        "run_id": run_id,
        "turn": turn,
        "tool": tool_name,
        "inputs": inputs,
        "result_preview": str(result)[:200],
        "duration_ms": duration_ms,
        "success": success,
    }
    print(json.dumps(record), file=sys.stdout, flush=True)
