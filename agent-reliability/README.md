# Agent Reliability — Four Defensive Layers

Companion code for the YouTube tutorial: *Tool Calling & Reliability — How Real Agents Handle Failure*.

The loop is the easy part. Making it work *every time* — when AWS throttles, when a tool gets bad input, when something has to retry — is what separates a demo from a system you can trust.

This repo bundles the four defensive layers from the video, plus a small runnable demo that exercises them all.

> 🎥 **Video:** *link when published*

## What's in this folder

| File | Layer | Purpose |
|---|---|---|
| `validation.py` | 1 | `validate_tool_input(...)` — schema check before the tool runs. |
| `safe_writes.py` | 2 | `write_file_safe(...)` — atomic temp-then-rename pattern. |
| `idempotent_s3.py` | 2 | `create_or_update_bucket(...)` — check-before-create. |
| `idempotent_charge.py` | 2 | `make_idempotency_key(...)` — hash-of-inputs idempotency keys. |
| `retry_decorator.py` | 3 | `@retry_with_backoff(...)` — write once, use anywhere. |
| `bedrock_call.py` | 3 | `invoke_claude(...)` — Bedrock invoke wrapped with the decorator. |
| `structured_logger.py` | 4 | `create_run_id()` + `log_tool_call(...)` — JSON logs CloudWatch can parse. |
| `agent.py` | all | Demo agent loop that runs all four layers together. |
| `requirements.txt` | | `boto3` (the only dependency). |
| `.env.example` | | Template for local AWS config. |

## Prerequisites

- Python 3.10+
- AWS CLI configured (only required if you want to run `bedrock_call.py` against real Bedrock)
- AWS account with Bedrock access to **Claude Sonnet 4.5** in `us-east-1` (only for `bedrock_call.py`)

The main `agent.py` demo works **without AWS** — it uses local mock tools so you can see all four layers in action immediately.

## Quickstart

```bash
# 1. clone + enter
git clone https://github.com/rayl15/youtube-tutorials.git
cd youtube-tutorials/agent-reliability

# 2. virtualenv + install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. run the demo
python agent.py
```

You should see five structured JSON log lines stream out, one per tool call, all tagged with the same `run_id`. The third line will show `success: false` because the demo includes a deliberate validation failure — that's the point.

## What you'll see

```
# starting agent run a3f9c1d2

{"ts":..., "run_id":"a3f9c1d2", "turn":1, "tool":"lookup_order", ..., "success":true}
{"ts":..., "run_id":"a3f9c1d2", "turn":2, "tool":"check_stock",  ..., "success":true}
{"ts":..., "run_id":"a3f9c1d2", "turn":3, "tool":"lookup_order", ..., "success":false}
{"ts":..., "run_id":"a3f9c1d2", "turn":4, "tool":"save_summary", ..., "success":true}
{"ts":..., "run_id":"a3f9c1d2", "turn":5, "tool":"save_summary", ..., "success":true}
```

Turn 3 was caught by the validation gate (missing required field). Turns 4 and 5 prove idempotency — calling `save_summary` twice with the same arguments produces the same final file (atomic writes via temp + rename).

## The four rules

1. **Validate before execute.** The LLM picks what to run. *You* decide if it's safe to run.
2. **Design tools that are safe to retry.** Twice should equal once. Atomic writes. Check-before-create. Idempotency keys.
3. **Know your failure types.** Transient → retry with backoff. Permanent → fail fast and tell the LLM clearly.
4. **Log everything with a `run_id`.** One ID per agent invocation. The trail is right there when something breaks.

## Mental model

> Your agent is only as reliable as its tools.
> The LLM can reason perfectly. If the tools are flaky, the agent is flaky.
> Your job isn't just to give the agent intelligence — it's to give it **reliable hands**.

## Stack

- **Python 3.10+** — standard library only (no extra deps for Layers 1, 2, 4)
- **boto3** — for the optional Layer 3 Bedrock demo
- **AWS Bedrock** — Claude Sonnet 4.5 via cross-region inference (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`)

## License

MIT — see the [top-level LICENSE](../LICENSE).
