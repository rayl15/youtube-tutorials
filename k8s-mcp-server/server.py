"""
k8s-mcp-server — give Claude READ-ONLY eyes on your Kubernetes cluster.

Part 3 of "Build MCP Servers for DevOps". Five read-only tools so Claude Code
can troubleshoot a cluster: list pods, read a pod's status (incl. crash
reasons + exit codes), pull a pod's events, tail container logs (including the
*previous* crashed container — the key to CrashLoopBackOff), and describe a
deployment.

SAFETY: every tool only calls read APIs (list/read). Pair it with the
read-only RBAC in `rbac-readonly.yaml` so the kubeconfig it uses *physically
cannot* mutate the cluster — the AI can look, never touch.

Uses your current kubeconfig context (KUBECONFIG env or ~/.kube/config).

Run it:
    uv run server.py
"""

from __future__ import annotations

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("k8s-readonly")

_loaded = False


def _load():
    """Load kubeconfig once (in-cluster if available, else local kubeconfig)."""
    global _loaded
    if _loaded:
        return
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
    _loaded = True


def _core() -> client.CoreV1Api:
    _load()
    return client.CoreV1Api()


def _apps() -> client.AppsV1Api:
    _load()
    return client.AppsV1Api()


@mcp.tool()
def list_pods(namespace: str = "default") -> list[dict]:
    """List pods in a namespace with name, phase, restart count, and node.

    Use this first — it's the "what's running and what's unhealthy?" view.
    A high restart count or a phase that isn't Running is your prime suspect.
    """
    pods = _core().list_namespaced_pod(namespace).items
    out = []
    for p in pods:
        restarts = sum((cs.restart_count or 0) for cs in (p.status.container_statuses or []))
        out.append(
            {
                "name": p.metadata.name,
                "phase": p.status.phase,
                "restarts": restarts,
                "node": p.spec.node_name,
            }
        )
    return out


@mcp.tool()
def get_pod_status(name: str, namespace: str = "default") -> dict:
    """Get the detailed status of one pod — the real crash reason lives here.

    Use this on a suspect pod. For a CrashLoopBackOff, this returns each
    container's state, the waiting reason (e.g. CrashLoopBackOff), and the
    LAST terminated state with its exit code and reason (e.g. Error, OOMKilled).
    That exit code + reason is usually the whole diagnosis.
    """
    p = _core().read_namespaced_pod(name, namespace)
    containers = []
    for cs in (p.status.container_statuses or []):
        state = cs.state
        waiting = state.waiting.reason if state and state.waiting else None
        last = cs.last_state.terminated if cs.last_state and cs.last_state.terminated else None
        containers.append(
            {
                "container": cs.name,
                "ready": cs.ready,
                "restarts": cs.restart_count,
                "waiting_reason": waiting,
                "last_terminated": (
                    {
                        "exit_code": last.exit_code,
                        "reason": last.reason,
                        "signal": last.signal,
                    }
                    if last
                    else None
                ),
            }
        )
    return {
        "name": p.metadata.name,
        "phase": p.status.phase,
        "containers": containers,
    }


@mcp.tool()
def get_pod_events(name: str, namespace: str = "default") -> list[dict]:
    """Get recent Kubernetes events for a pod (Warnings first).

    Use this to catch problems that never even reach the container — failed
    image pulls (ErrImagePull / ImagePullBackOff), failed scheduling, OOM
    kills, failed mounts. The event message often names the exact cause.
    """
    field = f"involvedObject.name={name}"
    events = _core().list_namespaced_event(namespace, field_selector=field).items
    rows = [
        {
            "type": e.type,
            "reason": e.reason,
            "message": e.message,
            "count": e.count,
        }
        for e in events
    ]
    # Warnings to the top — that's what you want to read first.
    rows.sort(key=lambda r: r["type"] != "Warning")
    return rows


@mcp.tool()
def tail_pod_logs(
    name: str, namespace: str = "default", container: str = "", lines: int = 50, previous: bool = True
) -> str:
    """Tail the last N log lines of a pod's container (read-only).

    Use this to see the error the app printed right before it died. For a
    crashing pod set previous=True (the default) to read logs from the
    *crashed* container instance — the live one may be too new to show
    anything. If the pod has multiple containers, pass `container`.
    """
    kwargs = {"namespace": namespace, "tail_lines": max(1, lines)}
    if container:
        kwargs["container"] = container
    try:
        if previous:
            try:
                return _core().read_namespaced_pod_log(name, previous=True, **kwargs)
            except ApiException:
                pass  # no previous instance yet — fall back to current
        return _core().read_namespaced_pod_log(name, **kwargs)
    except ApiException as e:
        return f"Could not read logs: {e.reason} (status {e.status})"


@mcp.tool()
def describe_deployment(name: str, namespace: str = "default") -> dict:
    """Describe a deployment — image, replica counts, and rollout conditions.

    Use this to compare desired vs available replicas and see why a rollout
    is stuck. Returns the container image (a bad tag is a common crash cause),
    desired/ready/available replicas, and the deployment conditions.
    """
    d = _apps().read_namespaced_deployment(name, namespace)
    images = [c.image for c in d.spec.template.spec.containers]
    conditions = [
        {"type": c.type, "status": c.status, "reason": c.reason}
        for c in (d.status.conditions or [])
    ]
    return {
        "name": d.metadata.name,
        "images": images,
        "desired": d.spec.replicas,
        "ready": d.status.ready_replicas or 0,
        "available": d.status.available_replicas or 0,
        "conditions": conditions,
    }


if __name__ == "__main__":
    mcp.run()
