# Context Engineering — A Real Implementation

Companion code for the YouTube tutorial: *Context Engineering for AI Agents — The Thing Every Tutorial Skips*.

A working customer-support agent on AWS Bedrock that fixes the three failure modes most production agents hit: **bloated context**, **stale context**, **missing context**. Side by side with a naive version so you can see the difference in plain English.

> 🎥 **Video:** *link when published*

## What's in this folder

| File | Purpose |
|---|---|
| `context_manager.py` | The piece nobody builds — a 30-line `ContextManager` class with system prompt, recent-turns memory, fresh task context, and tool-result extraction. |
| `agent.py` | Customer-support agent that uses `ContextManager` properly. |
| `agent_naive.py` | The "raw, naive" version — generic prompt, no task context, full noisy history. Same model, same tools, much worse output. |
| `requirements.txt` | `boto3` + `anthropic`. |
| `.env.example` | Template for local AWS config. |

## Prerequisites

- Python 3.10+
- AWS CLI configured with credentials (`aws configure`)
- AWS account with Bedrock access to **Claude Sonnet 4.5** in `us-east-1`
  (request access in the Bedrock console if you don't have it)

## Quickstart

```bash
# 1. clone + enter
git clone https://github.com/rayl15/youtube-tutorials.git
cd youtube-tutorials/context-engineering-agent

# 2. create virtualenv + install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. make sure AWS credentials are configured
aws configure           # or export AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY

# 4. run the good version
python agent.py

# 5. run the naive version for contrast
python agent_naive.py
```

## What you'll see

`agent.py` (with `ContextManager`) — picks up the customer's name and order directly from injected task context:

> Hi Priya! Your order from last week is **Order #98432** (Laptop Stand), which was delivered on **April 18**. Is there anything else I can help you with regarding this order?

`agent_naive.py` (no context manager, generic prompt, noisy history) — admits it can't help and asks for everything the good agent already knew:

> I'd be happy to help you track your order from last week. However, I don't have access to order systems or your account information. To check on your order status, you would need to: …

Same model. Same tools. The context is better. **That's the whole thing.**

## The four jobs of a `ContextManager`

1. **System prompt** — defined once, injected at every turn, never decoration. Treat it like production code.
2. **Working memory** — keep only the last N turns (default `max_history_turns=10`). The model is not looking at something you said 50 turns ago.
3. **Task context** — fresh, task-specific data injected at every turn (customer ID, order, account status…). Never stale.
4. **Extract, don't dump** — when a tool returns a 5,000-token blob, slice the part that matters before it touches the context window.

## Three rules to take with you

1. **System prompt isn't decoration** — spend 80% of your context-engineering effort here.
2. **Summarize before you inject** — every tool result passes through a relevance filter.
3. **Task-specific, not generic** — a support agent and a research agent need completely different context shapes. Build per use case.

## Mental model

> **Context ≠ Memory.**
> Memory is what the model knows from training — you can't control that.
> Context is what you put in front of the model right now — you control it completely.
> That's your entire leverage surface as an engineer.

## Stack

- **AWS Bedrock** — Claude Sonnet 4.5 via cross-region inference (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`)
- **boto3** — Bedrock runtime client
- **anthropic** — Anthropic SDK (used for clean message types; you can use boto3-only if you prefer)

## License

MIT — see the [top-level LICENSE](../LICENSE).
