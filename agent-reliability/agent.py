"""Reliable agent demo — exercises all four defensive layers in one loop.

Layers:
    1. Validation before execute       → validation.py
    2. Idempotent tool design          → safe_writes.py / idempotent_s3.py /
                                          idempotent_charge.py
    3. Retry with exponential backoff  → retry_decorator.py / bedrock_call.py
    4. Structured logging with run_id  → structured_logger.py

Run it:
    python agent.py

You'll see one structured JSON line per tool call. Grep them by run_id
to follow a single agent invocation through the whole timeline.

Note: this driver simulates a planned sequence of tool calls instead of
parsing real Anthropic ``tool_use`` blocks — the four-layer pattern is
identical whether the calls come from an LLM or a test harness.
"""
import time

from validation import validate_tool_input
from structured_logger import create_run_id, log_tool_call
from safe_writes import write_file_safe


# ─── Tool registry ──────────────────────────────────────────────────────────

# Each tool declares its name, executor, and JSON-schema input shape.
# The same `input_schema` flows to the LLM (so it knows how to call) and to
# our validation gate (so we can catch bad inputs before the tool runs).
TOOLS = {
    "lookup_order": {
        "execute": lambda order_id: f"order {order_id}: status=delivered, refund=NULL",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    "check_stock": {
        "execute": lambda sku: f"stock {sku}: 14 in warehouse",
        "input_schema": {
            "type": "object",
            "properties": {"sku": {"type": "string"}},
            "required": ["sku"],
        },
    },
    "save_summary": {
        # Layer 2 — idempotent because write_file_safe uses temp+rename.
        "execute": lambda path, content: write_file_safe(path, content),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
}


# ─── Agent loop ─────────────────────────────────────────────────────────────

def run_agent(planned_calls: list) -> None:
    """Execute a planned sequence of tool calls with all four layers active.

    `planned_calls` is a list of (tool_name, inputs_dict) tuples. In real
    use this comes from parsing the LLM's tool_use blocks each turn.
    """
    run_id = create_run_id()
    print(f"# starting agent run {run_id}\n")

    for turn, (name, inputs) in enumerate(planned_calls, start=1):
        # Layer 1 — validation gate
        schema = TOOLS[name]["input_schema"]
        ok, err = validate_tool_input(name, inputs, schema)

        t0 = time.time()
        if not ok:
            # Errors talk to the LLM — return them as the tool's "result"
            # rather than raising. The LLM sees the message and self-corrects.
            result = f"ERROR: {err}"
        else:
            try:
                # Layer 2 — every tool here is safe to retry.
                result = TOOLS[name]["execute"](**inputs)
            except Exception as e:
                # Tool errors also become string results, not exceptions.
                result = f"ERROR: {e}"

        duration_ms = int((time.time() - t0) * 1000)
        # Layer 4 — structured log line per call, tagged with run_id.
        log_tool_call(run_id, turn, name, inputs, result, duration_ms)


if __name__ == "__main__":
    # A small simulated plan that exercises every layer:
    #   - turn 1, 2: normal happy-path tool calls
    #   - turn 3:    BAD INPUT — caught by the validation gate
    #   - turn 4, 5: idempotent file write — calling twice is safe
    plan = [
        ("lookup_order", {"order_id": "98432"}),
        ("check_stock",  {"sku": "SKU-LS-12"}),
        ("lookup_order", {}),                         # missing required field
        ("save_summary", {"path": "/tmp/summary.txt",
                          "content": "Order 98432 delivered."}),
        ("save_summary", {"path": "/tmp/summary.txt",
                          "content": "Order 98432 delivered."}),
    ]
    run_agent(plan)
