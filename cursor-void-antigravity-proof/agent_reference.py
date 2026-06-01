"""
agent_reference.py — copy of the 30-line agent.py from ../no-framework-agent/
Kept here for side-by-side comparison with Void/Cursor/Antigravity loops.

The brain: line 21 — client.chat.completions.create(...)
The hands: lines 7-16 — the `tools` array
The loop:  line 20 — while True

Compare against Void's chatThreadService.ts line 770 (// tool use loop) for the
"different language, same loop" reveal in the video.
"""
from openai import OpenAI
import subprocess
import json

client = OpenAI()

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read the full contents of a file from disk. Use when the user asks what is inside a file.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Execute a shell command and return stdout. Use for system inspection like 'ls' or 'pip list'.",
        "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]}}},
]

messages = [{"role": "user", "content": input("You: ")}]

while True:
    msg = client.chat.completions.create(model="gpt-4o", tools=tools, messages=messages).choices[0].message
    messages.append(msg.model_dump())
    if not msg.tool_calls:
        print(msg.content); break
    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments)
        out = open(args["path"]).read() if tc.function.name == "read_file" \
              else subprocess.run(args["cmd"], shell=True, capture_output=True, text=True).stdout
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": out})
