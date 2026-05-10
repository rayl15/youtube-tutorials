# No-Framework Agent — 29 Lines of Python

Companion code for the YouTube tutorial: *I Built an AI Agent Without Any Framework — Here's the Code*.

The whole pattern behind every agent — Devin, Cursor, Claude Code, CrewAI, LangGraph — is the same three things: **a brain (LLM), some hands (tools), and a loop**. This repo is the proof: a real, working AI agent in 29 lines of Python with **one dependency** and **no framework**. Plus the same task built with CrewAI, side by side, so you can see the wrapping for yourself.

> 🎥 **Video:** *link when published*

## What's in this folder

| File | Purpose |
|---|---|
| `agent.py` | The whole agent — 29 lines. Brain (OpenAI), hands (`read_file`, `run_command`), loop (`while True:`). One dependency. |
| `crew_agent.py` | The same task built with CrewAI. Same brain, same hands, same loop — just dressed up in classes. |
| `config.yaml` | Demo file the agent reads in the live demo. |
| `requirements.txt` | `openai` — the only dependency for `agent.py`. |
| `requirements-crewai.txt` | Optional — install if you also want to run `crew_agent.py`. |
| `.env.example` | Template for your OpenAI key. |

## Prerequisites

- Python 3.10+
- An OpenAI API key with access to `gpt-4o`

## Quickstart

```bash
# 1. clone + enter
git clone https://github.com/rayl15/youtube-tutorials.git
cd youtube-tutorials/no-framework-agent

# 2. virtualenv + install (the custom agent only needs openai)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. set your key (copy .env.example, fill in OPENAI_API_KEY, then export it)
cp .env.example .env
export OPENAI_API_KEY=sk-proj-...

# 4. run the agent
python agent.py
You: Read the file config.yaml and summarize it.
```

You'll see the model pick the right tool, call it, get the result back, reason about it, and answer.

Try a different question to exercise the second tool:

```bash
python agent.py
You: Check what Python packages are installed.
```

This time it picks `run_command`, runs `pip list`, and summarizes.

## The pattern

Three things. That's it.

1. **Brain** — `client.chat.completions.create(...)` — the model decides what to do.
2. **Hands** — the `tools` list — every tool is a `name`, a `description` (the model reads this to decide whether to fire it), and a `parameters` JSON Schema (so the model knows the arguments to pass).
3. **Loop** — `while True:` — keep going until `msg.tool_calls` is empty (the model is done thinking and just wants to talk to the user).

Read `agent.py` top-to-bottom. Every framework on Earth wraps the same three things in more classes.

## Side-by-side: CrewAI

The CrewAI version is for comparison, not for setup. If you want to run it:

```bash
pip install -r requirements-crewai.txt
python crew_agent.py
```

You'll get the same result. Notice it does the same three things — brain (the `Agent` with role/goal/backstory + `llm`), hands (the `@tool`-decorated functions), loop (`crew.kickoff()` runs the cycle). Just more code around it, and ~40 transitive dependencies instead of 1.

CrewAI isn't bad — it earns its keep when you have **multiple agents coordinating**, need **guardrails**, or need **production-grade error handling**. But it's not magic. It's engineering. Start from scratch, learn the pattern, then graduate to a framework when the problem actually demands it.

## Critical detail: the description string

The single most important sentence in the whole repo is the `"description"` field on each tool. The model **does not read your function**. It reads that string and decides whether to fire the tool based on what it says.

Bad description → wrong tool gets called → broken agent. So write them like this:

> Read the full contents of a file from disk. Use when the user asks what is inside a file.

Specific. Action-oriented. Tells the model *exactly* when to fire it.

## License

MIT — see [LICENSE](../LICENSE).
