# YouTube Tutorials

Companion code for my YouTube videos on Agentic AI, AWS, and production ML engineering.

Each folder is a self-contained project paired with a video on the channel. Clone, follow along, ship your own version.

## Projects

| Folder | Topic | Video |
|---|---|---|
| [`crewai-aws-multi-agent/`](./crewai-aws-multi-agent) | Build a 3-agent research crew with CrewAI, deploy to AWS Lambda via Docker + ECR, trigger it from the terminal. | *link when published* |
| [`context-engineering-agent/`](./context-engineering-agent) | The piece nobody builds — a `ContextManager` for production agents on AWS Bedrock. Side-by-side with a naive version so you can see the difference. | *link when published* |
| [`agent-reliability/`](./agent-reliability) | Four defensive layers — validation, idempotent tools, retry with backoff, structured logging — that turn a demo agent into one you can actually trust in production. | *link when published* |
| [`no-framework-agent/`](./no-framework-agent) | A real, working AI agent in 29 lines of Python with one dependency and **no framework**. Plus the same task built with CrewAI, side by side, so you can see the wrapping for yourself. | *link when published* |
| [`free-claude-code/`](./free-claude-code) | `cc.py` — ~30 lines that do what Claude Code does, using a **free** model (MiniMax M2.5 via OpenRouter — 80.2% SWE-Bench Verified) instead of paid Sonnet. Side-by-side with paid Claude Code on the same 4-file refactor task. The 3 honest catches included. | *link when published* |
| [`cursor-void-antigravity-proof/`](./cursor-void-antigravity-proof) | A proof/investigation repo, not a tutorial. Maps the same brain-hands-loop pattern from our 30-line `agent.py` onto **Void** (1,884-line TypeScript fork — `chatThreadService.ts:770`), **Cursor** (10 tools from the leaked system prompt), and **Antigravity** (Google's 3-tool agentic IDE). Every claim links to a verifiable source. | *link when published* |
| [`mcp-devops-starter/`](./mcp-devops-starter) | Your first **MCP server** (Model Context Protocol), DevOps edition — four read-only tools (`check_disk_usage`, `check_memory`, `list_top_processes`, `tail_log`) that let Claude inspect a machine's health. No frameworks; plugs into Claude Code via `/mcp`. | *link when published* |

## Using this repo

```bash
git clone https://github.com/rayl15/youtube-tutorials.git
cd youtube-tutorials/<folder>
# each folder has its own README with setup + run instructions
```

## Stay in touch

- YouTube: [@rahulsharma_ytb](https://youtube.com/@rahulsharma_ytb)

## License

MIT — see [LICENSE](./LICENSE).
