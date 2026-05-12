"""Claude Code, free, in ~30 lines. Companion to the YouTube video.

Run:
    export OPENROUTER_API_KEY=sk-or-v1-...
    python cc.py
"""
import os, json, subprocess
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
MODEL = "minimax/minimax-m2.5:free"  # 80.2% SWE-Bench Verified, free tier (May 2026); verify at https://openrouter.ai/models?max_price=0

tools = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read the full contents of a file from disk. Use when the user asks about, edits, or refactors code.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "edit_file",
        "description": "Replace one exact substring in a file. Use for surgical edits. Fails loudly if old_string is not found.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}
        }, "required": ["path", "old_string", "new_string"]}}},
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Execute a shell command and return stdout. Use for tests, git, pip, ls.",
        "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]}}},
]

def _edit(path, old_string, new_string):
    content = open(path).read()
    if old_string not in content:
        return f"NOT FOUND in {path} — model must re-read the file"
    open(path, "w").write(content.replace(old_string, new_string, 1))
    return f"edited {path}"

TOOLS = {
    "read_file":   lambda path: open(path).read(),
    "edit_file":   _edit,
    "run_command": lambda cmd: subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout[:2000],
}

messages = [
    {"role": "system", "content": "You are a coding agent. Always read files before editing them. Use run_command to verify your changes."},
    {"role": "user", "content": input("You: ")},
]

while True:
    msg = client.chat.completions.create(model=MODEL, messages=messages, tools=tools).choices[0].message
    messages.append(msg.model_dump(exclude_none=True))
    if not msg.tool_calls:
        print(msg.content); break
    for c in msg.tool_calls:
        args = json.loads(c.function.arguments)
        out  = TOOLS[c.function.name](**args)
        messages.append({"role": "tool", "tool_call_id": c.id, "content": str(out)})
