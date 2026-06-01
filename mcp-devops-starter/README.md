# mcp-devops-starter

Your **first MCP server**, DevOps edition. A tiny [Model Context Protocol](https://modelcontextprotocol.io) server that gives Claude four **read-only** tools to inspect a machine's health:

| Tool | What it does |
|------|--------------|
| `check_disk_usage` | Disk space for a path (total/used/free/%) |
| `check_memory` | RAM + swap usage |
| `list_top_processes` | Heaviest processes by CPU or memory |
| `tail_log` | Last N lines of a log file (allow-listed dirs only) |

Nothing here mutates your system. It's the safe starting point before you build servers that touch AWS, Kubernetes, or Terraform.

> 📺 Built step-by-step in the video: **"Claude as Your DevOps Assistant (Custom MCP Server)"** — part 1 of the *Build MCP Servers for DevOps* series.

## Quick start (uv — recommended)

```bash
git clone https://github.com/rayl15/youtube-tutorials.git && cd youtube-tutorials/mcp-devops-starter
uv sync
uv run server.py        # starts the server on stdio
```

Or with pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

## Connect it to Claude Code (CLI)

This repo ships a project-scoped `.mcp.json`, so the easiest path is:

```bash
cd mcp-devops-starter
claude                       # launch Claude Code from the repo folder
/mcp                         # confirm "devops-starter" is connected
```

Prefer to register it explicitly (any directory)? Use the CLI:

```bash
claude mcp add devops-starter -- uv run server.py        # local scope
# or share it with anyone who clones the repo:
claude mcp add --scope project devops-starter -- uv run server.py
claude mcp list              # verify it's registered
```

Then, inside the `claude` session, ask:

> "My server feels slow — can you check disk, memory, and the top processes?"

Watch it call the tools and reason over the results, right in your terminal.

## Inspect / debug without Claude

```bash
uv run mcp dev server.py     # opens the MCP Inspector in your browser
```

## Safety notes

- All tools are **read-only**.
- `tail_log` only reads files under allow-listed directories (`/var/log`, `/tmp`, `~/logs`) — edit `ALLOWED_LOG_DIRS` in `server.py` to change that.

## License

MIT — use it, fork it, ship your own tools on top.
