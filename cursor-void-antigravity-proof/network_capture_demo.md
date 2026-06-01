# Capturing Cursor's DevTools Network Traffic

How to capture the proof footage of Cursor calling the OpenAI tool-calling API — the visual evidence that Cursor's agent loop is just the same chat-completions-with-tools loop you can write in 30 lines.

This is for the Cursor Beat C section of the video. The goal: viewer sees a real network request from Cursor with a `tools` array and a `tool_calls` response, proving that Cursor uses the standard OpenAI tool-calling API (or Anthropic equivalent — they support both).

## Steps

1. **Open Cursor**. Be on a project with at least one Python or Markdown file you can ask about.

2. **Open DevTools.** In Cursor:
   - `Cmd+Shift+P` → search "Toggle Developer Tools"
   - Or: `Help` menu → `Toggle Developer Tools`
   - This opens the embedded Chromium DevTools (Cursor is an Electron app)

3. **Switch to the Network tab.** Filter for `Fetch/XHR` only. Clear existing entries.

4. **Optional but cleaner:** filter by URL containing `api.cursor` or `chat` to drop noise.

5. **Start recording your screen** in 1080p, frame-rate ~30fps. Use the recording app of your choice — QuickTime works fine, OBS works better.

6. **In Cursor's chat panel:** open agent mode if available, then type a simple task:
   > "What's in agent_reference.py?"
   
   Hit enter.

7. **Watch the Network panel.** You should see one or more requests:
   - First request: `POST` to the Cursor API endpoint with payload containing `messages`, `tools`, `system` prompt
   - Response: contains a `tool_calls` array (e.g., `[{name: "read_file", arguments: {path: "agent_reference.py"}}]`)
   - Second request: same endpoint, payload now includes the previous assistant message + a `tool` role message with the file contents
   - Second response: the assistant's final summary text

8. **Capture key frames for the video:**
   - Frame A: outgoing request payload — highlight `tools: [...]` array and the system prompt
   - Frame B: response payload — highlight `tool_calls`
   - Frame C: follow-up request payload — highlight the appended `{role: "tool", ...}` message

## Visual annotations for editing

When you composite this into the Remotion timeline:

- Box `tools: [...]` array in orange (same color code as our hands)
- Box `tool_calls` response in green (same as brain output)
- Box the `{role: "tool", content: ...}` follow-up in purple (loop continuation)

That visual mapping — same three colors as the `agent.py` annotation — is what makes the side-by-side reveal land.

## Fallback if Cursor obfuscates the payload

Some Cursor builds obfuscate or batch the request to their own gateway. If you see only a single opaque POST to `api.cursor.sh` with no readable JSON:

1. Try the older non-agent mode chat — sometimes that goes through a less-obfuscated path.
2. Use `mitmproxy` to intercept and pretty-print: install with `brew install mitmproxy`, route Cursor through `http://localhost:8080`, capture the request, save the JSON.
3. Worst case: fall back to **only** the leaked system prompt as the proof source. The leak has the tool definitions in OpenAI-function-calling format, which is itself the proof. The network capture is bonus visual.

## What NOT to show

- Any API keys or auth tokens in the request headers — blur or crop them
- Any proprietary code from your own project that happens to be in the messages context — use a sample project for the recording
- The full system prompt if you're capturing live — Cursor's TOS may or may not allow rebroadcast. The jujumilk3 leak is already public; use that for the verbatim quotes and use the live capture only for the API shape (tools array + tool_calls response).
