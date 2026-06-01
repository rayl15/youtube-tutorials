# Cursor, Void, Antigravity — All Run the Same 30-Line Agent Loop

— Companion repo for the YouTube video proving four AI coding tools (ours, Void, Cursor, Antigravity) share the same brain-hands-loop pattern.

🎥 **Video:** *link goes here once the video publishes (Sun 2026-05-24, 21:00 IST)*

This is a **proof/investigation** repo, not a build tutorial. The video walks through three popular AI coding tools (Void, Cursor, Antigravity) and shows that each one runs the same agent loop pattern as the 30-line `agent.py` from the [no-framework-agent](../no-framework-agent/) folder.

## What's in this folder

| File | Purpose |
|---|---|
| `README.md` | You are here |
| `sources.md` | Every claim in the video mapped to its verified source URL and exact line/section |
| `agent_reference.py` | Copy of the 30-line `agent.py` from `../no-framework-agent/` for side-by-side comparison |
| `network_capture_demo.md` | How to capture Cursor's DevTools network traffic during an agent task |

## Prerequisites

To follow along or reproduce the proof yourself:

1. Git installed (to clone Void)
2. A web browser (to view the leaked Cursor prompt and Antigravity docs)
3. Cursor installed (free tier is fine — to capture the network traffic)
4. Antigravity access (optional — preview tier via Google AI Studio)

## Quickstart — reproduce the proof

```bash
# 1. Clone Void and find the agent loop file
git clone --depth 1 https://github.com/voideditor/void.git
# Open: void/src/vs/workbench/contrib/void/browser/chatThreadService.ts
# Jump to line 770 — the comment literally reads `// tool use loop`

# 2. View Cursor's leaked system prompt
open https://github.com/jujumilk3/leaked-system-prompts/blob/main/cursor-ide-sonnet_20241224.md
# Look at: the 10 <function> definitions and rule #3 ("NEVER refer to tool names")

# 3. View Antigravity's tool API
open https://ai.google.dev/gemini-api/docs/antigravity-agent
# Look at: code_execution, google_search, url_context — the only 3 named tools

# 4. Run our 30-line agent.py for the baseline
cd ../no-framework-agent
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...     # or point at OpenRouter
python agent.py
```

## The pattern (verified across all four)

Every one of these tools — ours, Void, Cursor, Antigravity — runs the same loop:

```
1. Send messages to the LLM (brain)
2. Get back a response — text and/or tool calls
3. If no tool calls → return the text, exit
4. Otherwise → execute each tool call (hands), append result to messages
5. Goto 1
```

The differences are everything else:

| Tool | Language | Agent loop location | # of tools | Pricing |
|---|---|---|---|---|
| Our `agent.py` | Python | `agent.py` (30 lines) | 2 (`read_file`, `run_command`) | Free (Open Router free tier) |
| Void | TypeScript | `chatThreadService.ts` lines 770–901 (1,800+ lines incl. polish) | ~10 + MCP | Free + open source |
| Cursor | Closed source | Inferred from leaked prompt + network calls | 10 (codebase_search, read_file, run_terminal_cmd, list_dir, grep_search, edit_file, file_search, delete_file, reapply, parallel_apply) | $20/mo Pro |
| Antigravity | Closed source | Managed via Gemini API Interactions API | 3 (code_execution, google_search, url_context) + sandbox env | Google pricing (preview) |

## What you're actually paying for (the Catch)

Three things, none of them the loop:

1. **Prompt-engineering polish.** Cursor's leaked prompt has rules like *"NEVER refer to tool names when speaking to the USER. For example, instead of saying 'I need to use the edit_file tool to edit your file', just say 'I will edit your file'."* — UX engineering wired into the system prompt. Two years of refinement.
2. **IDE integration.** Diff view, chat panel, inline suggestions. That's the editor, not the agent.
3. **Inference cost subsidy.** They pay for the model calls so you don't see the bill.

## Related videos

- [I Built an AI Agent From Scratch | No Framework Required](https://www.youtube.com/watch?v=SDUNPtYosJU) — the 30-line `agent.py` we found in all three tools
- [Your AI Agent Crashes Because of These 5 Real Mistakes](https://www.youtube.com/watch?v=e67rqO0K4xk) — the production audit

## License

See [../LICENSE](../LICENSE).
