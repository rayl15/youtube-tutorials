# k8s-mcp-server

Give Claude **read-only eyes** on your Kubernetes cluster. Part 3 of *Build MCP Servers for DevOps*.

Five tools so Claude Code can **troubleshoot** a cluster — and nothing more:

| Tool | What it does |
|------|--------------|
| `list_pods` | Pods in a namespace: phase, restart count, node |
| `get_pod_status` | One pod's container states + **last crash reason & exit code** |
| `get_pod_events` | Pod events, Warnings first (ImagePullBackOff, OOMKilled, scheduling) |
| `tail_pod_logs` | Last N log lines — incl. the **previous crashed container** |
| `describe_deployment` | Image, desired/ready replicas, rollout conditions |

> 🔒 **Every tool is read-only** (`get`/`list`/`watch`). Pair it with `rbac-readonly.yaml`
> so the credentials *physically cannot* change the cluster.

> 📺 Built in: **"Build a Kubernetes MCP Server for Claude Code — It Found Why My Pods Keep Crashing"**.
> New here? Start with [Part 1](../mcp-devops-starter) and [Part 2](../aws-mcp-server).

## 1. Apply the read-only RBAC (don't skip)

```bash
kubectl apply -f rbac-readonly.yaml
```

This creates a `claude-readonly` ServiceAccount with get/list/watch only. To run
the server *as* that account locally, generate a kubeconfig for it (a token-based
context), or run the server inside the cluster — see PREP.md. The simplest local
path is to keep your normal context but verify the RBAC limits with:

```bash
kubectl auth can-i delete pods --as=system:serviceaccount:default:claude-readonly   # -> no
kubectl auth can-i get pods    --as=system:serviceaccount:default:claude-readonly   # -> yes
```

## 2. Run it

```bash
uv sync
uv run server.py      # starts on stdio (blocks — correct for a server)
```

## 3. Connect to Claude Code

```bash
claude mcp add k8s-readonly -- uv run server.py
claude mcp list
claude          # inside the session:
/mcp            # confirm k8s-readonly + its 5 tools
```

(Or launch `claude` from this folder and approve the bundled `.mcp.json`.)

Then ask:

> "A pod in the default namespace keeps crashing. Find out which one and why."

## Inspect without Claude

```bash
uv run mcp dev server.py     # MCP Inspector in the browser
```

## Notes
- Needs a reachable cluster + a kubeconfig context (kind / minikube / k3s / EKS…).
- For CrashLoopBackOff, `tail_pod_logs(previous=True)` is the key — it reads the
  log from the container instance that actually died.

## License
MIT.
