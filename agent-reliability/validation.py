"""Layer 1 — validate tool inputs BEFORE the tool runs.

The LLM picks what to run. We decide whether it's safe to run.
Every tool call passes through this gate before execution.
"""
from typing import Tuple


def validate_tool_input(
    tool_name: str,
    inputs: dict,
    schema: dict,
) -> Tuple[bool, str]:
    """Check inputs against the tool's schema BEFORE the tool runs.

    Returns ``(ok, error_message)``. On failure, the message is meant to be
    sent back to the LLM as the tool's "result" — not raised — so the LLM
    can correct itself and try again.
    """
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # 1. Required fields present?
    for field in required:
        if field not in inputs:
            return False, f"Missing required field: {field}"

    # 2. Types match?
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    for field, value in inputs.items():
        if field not in properties:
            continue  # extra fields are fine; we don't punish those
        expected = properties[field].get("type")
        if expected and expected in type_map:
            if not isinstance(value, type_map[expected]):
                return False, (
                    f"Field '{field}' should be {expected}, "
                    f"got {type(value).__name__}"
                )

    return True, ""
