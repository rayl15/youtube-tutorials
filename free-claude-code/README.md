# Free Claude Code — 30 Lines of Python

Companion code for the YouTube tutorial: *Claude Code Is Now FREE. Here's the Catch No One Tells You.*

Claude Code Max costs $200/month. This repo is a 30-line Python file that does what Claude Code does — using a **free** model (MiniMax M2.5 via OpenRouter's free tier — 80.2% SWE-Bench Verified) instead of paid Claude Sonnet. Same three pieces from the `no-framework-agent` tutorial — **brain + hands + loop** — just with the model swapped. The honest catches are documented below.

> 🎥 **Video:** *link when published*
> 🧠 **Watch first:** [`no-framework-agent/`](../no-framework-agent) — the foundational brain/hands/loop pattern this builds on.

## What's in this folder

| File | Purpose |
|---|---|
| `cc.py` | The whole agent — ~30 lines. Brain (**MiniMax M2.5** via OpenRouter — same MiniMax that powers the video's voiceover), hands (`read_file`, `edit_file`, `run_command`), loop (`while True:`). One dependency. |
| `refactor_target/auth.py` `db.py` `api.py` `utils.py` | A 4-file sample project the agent has to refactor in the demo. No logging by default. |
| `refactor_target/test_logging.py` | Pre-refactor: **fails**. Post-refactor: **passes**. The agent's success criterion. |
| `requirements.txt` | `openai` — same single dependency as `no-framework-agent`. We just point it at a different base URL. |
| `.env.example` | Template for your OpenRouter key. |

## Prerequisites

- Python 3.10+
- A **free** OpenRouter API key from <https://openrouter.ai/keys> (no credit card required)

## Quickstart

```bash
# 1. clone + enter
git clone https://github.com/rayl15/youtube-tutorials.git
cd youtube-tutorials/free-claude-code

# 2. virtualenv + install (same one dependency as no-framework-agent)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. set your key (copy .env.example, fill in OPENROUTER_API_KEY, then export it)
cp .env.example .env
export OPENROUTER_API_KEY=sk-or-v1-...

# 4. verify the test fails BEFORE the agent runs (this is the "before" state)
python refactor_target/test_logging.py
#  → FAIL  auth.py: missing `logging.getLogger(__name__)`  (×8 failures)
#  → exit 1

# 5. run the agent
python cc.py
You: Add structured logging to every file in refactor_target/. Each module needs
     `import logging` and `logger = logging.getLogger(__name__)` at the top, plus
     at least one `logger.info(...)` call inside a function. Then run
     `python refactor_target/test_logging.py` from the project root to verify.
```

Watch the loop fire: `read_file` → `edit_file` → `run_command` → done. When you see `PASS  All 4 modules have logging wired up.` the agent has actually done the work.

## Model availability

OpenRouter's free-tier model IDs rotate. As of May 2026, `cc.py` ships with `minimax/minimax-m2.5:free` — a 1T-parameter MoE model that scores 80.2% on SWE-Bench Verified, free, with native function/tool calling. If that's no longer in the free tier, swap to any current free coding model at <https://openrouter.ai/models?max_price=0> — one line in `cc.py`:

```python
MODEL = "minimax/minimax-m2.5:free"  # ← change this
```

**Other strong free alternatives** (May 2026):
- `qwen/qwen3-coder:free` — 262k context, optimized for agentic coding
- `inclusionai/ring-2.6-1t:free` — 1T params, built for "coding agents, tool use, long-horizon"
- `openai/gpt-oss-120b:free` — OpenAI's open release, 131k context

## The pattern (same as no-framework-agent, model swapped)

1. **Brain** — `client.chat.completions.create(...)` pointed at `https://openrouter.ai/api/v1` instead of OpenAI's URL. The OpenAI SDK works against any OpenAI-compatible API; OpenRouter is one.
2. **Hands** — the `tools` list. Three tools this time: `read_file`, `edit_file`, `run_command`. The same toolset Claude Code itself ships with.
3. **Loop** — `while True:` — keep going until `msg.tool_calls` is empty.

Read `cc.py` top-to-bottom. It's the same pattern as `no-framework-agent/agent.py`, with two additions:
- A third tool (`edit_file`) so the agent can modify files, not just read them.
- A loud error in `_edit` when the model hallucinates an `old_string` — `"NOT FOUND in {path} — model must re-read the file"`. This is what lets the loop **self-correct** when the free model gets the substring slightly wrong.

That single error message is the difference between an agent that loops forever and one that recovers.

## The 3 catches (delivered at 8:00 in the video)

| # | Catch | When it bites |
|---|---|---|
| 1 | Free-tier rate limits | Heavy day → `429` errors. Paid OpenRouter tier is ~$5/mo — still 97% cheaper than Claude Code Max. |
| 2 | Smaller effective context window | Fine for 4-file refactors like this demo. Loses state on 100-file repo-wide refactors. |
| 3 | ~3× more hallucinated tool calls | `cc.py`'s `_edit` returns a loud `NOT FOUND` which lets the loop self-correct. Slower, not broken. |

## The deeper catch

This is **not** Claude Code. This is an agent loop with a free model swapped in.

The magic of Claude Code is half model, half harness. We replicated the harness (this is what `cc.py` is). We did **not** replicate Anthropic's prompt engineering on top of Sonnet's coding tune. For ~90% of real work, same result. For the hardest 10% — complex multi-file refactors, subtle architectural decisions — paid Claude Code still wins.

That gap is what you're paying $200/month for. Worth it for some people. Not worth it for most.

## When to use what

```
                Are you a daily heavy AI-coder?
                              │
                ┌─────────────┴─────────────┐
              YES                          NO
                │                            │
        Pay for Claude Code         Use cc.py
        Max ($200/mo)               Save ~$2,400/year
        Earns its money             Covers ~90% of real work
        on the hard 10%
```

## License

MIT — see [LICENSE](../LICENSE).
