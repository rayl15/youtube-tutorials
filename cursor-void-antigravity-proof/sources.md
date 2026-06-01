# Verified Sources

Every claim in the video maps to one of these. All sources verified 2026-05-23.

---

## 1. Our `agent.py` — the 30-line baseline

**Location:** `../no-framework-agent/agent.py` (this repo)
**Length:** 30 lines exactly
**Key landmarks:**
- Line 1–3: imports (`openai`, `subprocess`, `json`)
- Lines 7–16: `tools` array — the hands (read_file, run_command)
- Line 18: read the user input
- Line 20: `while True:` — the loop
- Line 21: `client.chat.completions.create(...)` — the brain
- Lines 25–28: tool execution
- Line 24: exit on no tool calls

**Verbatim `read_file` description (from line 10):**
> "Read the full contents of a file from disk. Use when the user asks what is inside a file."

---

## 2. Void — TypeScript fork of VS Code

**Repo:** https://github.com/voideditor/void
**Language:** TypeScript (≥92% by GitHub's language stats)
**Total chatThreadService.ts length:** 1,884 lines
**Total toolsService.ts length:** 593 lines

### Critical file paths

- Agent loop: `src/vs/workbench/contrib/void/browser/chatThreadService.ts`
- Tools registry: `src/vs/workbench/contrib/void/browser/toolsService.ts`
- LLM message service: `src/vs/workbench/contrib/void/electron-main/llmMessage/sendLLMMessage.impl.ts`

### Verbatim landmarks inside `chatThreadService.ts`

| Line | Content | Why it matters |
|---|---|---|
| 770 | `// tool use loop` | Void's own developers call it the same thing we do |
| 771 | `while (shouldSendAnotherMessage) {` | Outer loop — same as our `while True` |
| 793 | `while (shouldRetryLLM) {` | Inner retry loop — polish around the core |
| 805 | `this._llmMessageService.sendLLMMessage({...})` | The brain call |
| 826 | metrics event `'Agent Loop Done (Aborted)'` | They explicitly name it "Agent Loop" |
| 889 | `await this._runToolCall(...)` | The hands execution |
| 900 | `} // end while (attempts)` | Inner loop close |
| 901 | `} // end while (send message)` | Outer loop close |

### To reproduce

```bash
git clone --depth 1 https://github.com/voideditor/void.git
code void/src/vs/workbench/contrib/void/browser/chatThreadService.ts
# Jump to line 770
```

---

## 3. Cursor — leaked system prompt

**Primary mirror:** https://github.com/jujumilk3/leaked-system-prompts/blob/main/cursor-ide-sonnet_20241224.md
**Backup mirror (more comprehensive):** https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools

### The 10 tools defined

1. `codebase_search` — semantic code search
2. `read_file` — read file contents with line ranges
3. `run_terminal_cmd` — propose terminal commands
4. `list_dir` — list directory contents
5. `grep_search` — ripgrep-backed regex search
6. `edit_file` — propose edits to existing files
7. `file_search` — fuzzy filename search
8. `delete_file` — delete a file
9. `reapply` — re-attempt a failed edit with a smarter model
10. `parallel_apply` — coordinate multiple file edits

### Verbatim `read_file` description

> "Read the contents of a file. the output of this tool call will be the 1-indexed file contents from start_line_one_indexed to end_line_one_indexed_inclusive, together with a summary of the lines outside start_line_one_indexed and end_line_one_indexed_inclusive."

### Verbatim system prompt rule #3 (the polish reveal)

> "NEVER refer to tool names when speaking to the USER. For example, instead of saying 'I need to use the edit_file tool to edit your file', just say 'I will edit your file'."

This is the moment in the video where we prove what $20/mo actually buys: UX polish wired into the prompt.

---

## 4. Antigravity — Google's agentic IDE

**Official docs:** https://ai.google.dev/gemini-api/docs/antigravity-agent
**Marketing page:** https://antigravity.google/

### The ONLY 3 named tools

1. `code_execution` — runs bash, Python, Node commands; stdout/stderr captured
2. `google_search` — searches the public web
3. `url_context` — fetches and reads web pages

### Filesystem handling

The agent can "read, write, edit, search, and list files in the sandbox" — but these operations are **part of the sandbox environment**, not exposed as named tools. The model writes code (via `code_execution`) that performs file operations.

### Tools currently UNAVAILABLE in Antigravity

Per the docs: `file_search`, `computer_use`, `google_maps`, `function_calling`, `mcp`

### Why this matters for the video

This is the "different hands, same loop" beat. Cursor exposes 10 granular tools. Antigravity exposes 3, bundling everything into `code_execution`. **Different hands. Identical loop pattern above them.**

---

## How the claims map to the video

| Video beat | Source | Verified verbatim? |
|---|---|---|
| Hook ("same agent loop in all three") | All four sources above | ✓ |
| Void section — line 770 comment | Section 2, line 770 | ✓ direct screen-record |
| Void section — nested whiles | Section 2, lines 771 + 793 | ✓ direct screen-record |
| Cursor — 10 tools list | Section 3 | ✓ direct quote |
| Cursor — `read_file` description | Section 3 | ✓ verbatim quote in script |
| Cursor — Rule #3 "NEVER refer to tool names" | Section 3 | ✓ verbatim quote in script |
| Antigravity — only 3 tools | Section 4 | ✓ direct quote from docs |
| Antigravity — filesystem is sandbox env | Section 4 | ✓ direct quote from docs |

If a viewer pauses any frame and challenges a claim, the answer is one of the four URLs above.
