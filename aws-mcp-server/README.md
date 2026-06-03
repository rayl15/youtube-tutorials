# aws-mcp-server

Give Claude **read-only eyes** on your AWS account. Part 2 of *Build MCP Servers for DevOps*.

Five tools so Claude Code can **audit** an account — and nothing more:

| Tool | What it does |
|------|--------------|
| `list_ec2_instances` | Running compute: id, type, state, Name, AZ |
| `find_idle_resources` | Money leaks: stopped instances, unattached EBS volumes, idle Elastic IPs |
| `get_monthly_cost` | Last N months of spend by service (Cost Explorer) |
| `scan_security_groups` | Rules open to `0.0.0.0/0` on SSH/RDP/DB ports |
| `list_s3_buckets` | Bucket inventory |

> 🔒 **Every tool is read-only** (`Describe*`/`List*`/`Get*`). Pair it with the
> `iam-readonly-policy.json` so the credentials *physically cannot* change anything.

> 📺 Built in: **"Claude Just Exposed Every Inefficiency in My AWS Setup"** — part 2 of the series.
> New here? Start with part 1: [`mcp-devops-starter`](../01-mcp-starter).

## 1. Lock down credentials FIRST (do not skip)

Create a dedicated IAM user/role used **only** by this server and attach the
read-only policy:

```bash
aws iam create-user --user-name claude-readonly
aws iam put-user-policy --user-name claude-readonly \
  --policy-name claude-readonly --policy-document file://iam-readonly-policy.json
# create access keys for that user, then:
aws configure --profile claude-readonly
export AWS_PROFILE=claude-readonly
export AWS_REGION=us-east-1
```

Now the worst Claude can do is *look*.

## 2. Run it

```bash
uv sync
uv run server.py      # starts on stdio (blocks — that's correct for a server)
```

## 3. Connect to Claude Code

```bash
claude mcp add aws-readonly -- uv run server.py
claude mcp list
claude            # then inside the session:
/mcp              # confirm aws-readonly + its 5 tools
```

(Or launch `claude` from this folder and approve the bundled `.mcp.json`.)

Then ask:

> "Audit my AWS account — what am I wasting money on, and is anything exposed to the internet?"

## Inspect without Claude

```bash
uv run mcp dev server.py     # MCP Inspector in the browser
```

## Notes
- Cost Explorer must be enabled on the account for `get_monthly_cost`.
- Read-only by design. To let Claude *act* on findings, that's a separate
  (carefully-scoped) server — not this one.

## License
MIT.
