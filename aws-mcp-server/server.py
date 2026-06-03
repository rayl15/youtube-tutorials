"""
aws-mcp-server — give Claude READ-ONLY eyes on your AWS account.

Part 2 of "Build MCP Servers for DevOps". Five read-only tools so Claude
Code can audit an AWS account: list EC2, find wasted/idle resources, read
Cost Explorer, scan security groups, and list S3 buckets.

SAFETY: every tool only calls read-only AWS APIs (Describe*/List*/Get*).
Pair it with the read-only IAM policy in `iam-readonly-policy.json` so the
credentials *physically cannot* mutate anything — the AI can look, never touch.

Credentials come from the standard AWS chain (env vars, `~/.aws/credentials`,
or `AWS_PROFILE`). Set a region with AWS_REGION (defaults to us-east-1).

Run it:
    uv run server.py
"""

from __future__ import annotations

import os
from datetime import date

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("aws-readonly")

DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Ports we consider risky if a security group opens them to the whole internet.
SENSITIVE_PORTS = {22: "SSH", 3389: "RDP", 3306: "MySQL", 5432: "Postgres", 6379: "Redis"}


def _client(service: str, region: str = ""):
    """Make a boto3 client, surfacing a clear error if no creds are configured."""
    try:
        return boto3.client(service, region_name=region or DEFAULT_REGION)
    except NoCredentialsError:
        raise RuntimeError(
            "No AWS credentials found. Configure `aws configure`, an AWS_PROFILE, "
            "or env vars — and use the read-only IAM policy from the repo."
        )


@mcp.tool()
def list_ec2_instances(region: str = "") -> list[dict]:
    """List EC2 instances with id, type, state, Name tag, and availability zone.

    Use this to see what compute is actually running in an account — the
    starting point for "what do we have?" and "what's it costing us?".
    """
    ec2 = _client("ec2", region)
    out: list[dict] = []
    for res in ec2.describe_instances().get("Reservations", []):
        for i in res.get("Instances", []):
            name = next((t["Value"] for t in i.get("Tags", []) if t["Key"] == "Name"), "")
            out.append(
                {
                    "id": i["InstanceId"],
                    "type": i["InstanceType"],
                    "state": i["State"]["Name"],
                    "name": name,
                    "az": i["Placement"]["AvailabilityZone"],
                }
            )
    return out


@mcp.tool()
def find_idle_resources(region: str = "") -> dict:
    """Find likely-WASTED AWS resources you're probably still paying for.

    Surfaces three classic money leaks: stopped EC2 instances (you still pay
    for their disks), unattached EBS volumes (paying for storage nobody uses),
    and unassociated Elastic IPs (AWS bills idle EIPs). Use this to answer
    "where am I wasting money?".
    """
    ec2 = _client("ec2", region)

    stopped = [
        {"id": i["InstanceId"], "type": i["InstanceType"]}
        for r in ec2.describe_instances(
            Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
        ).get("Reservations", [])
        for i in r.get("Instances", [])
    ]

    unattached_volumes = [
        {"id": v["VolumeId"], "size_gb": v["Size"], "type": v["VolumeType"]}
        for v in ec2.describe_volumes(
            Filters=[{"Name": "status", "Values": ["available"]}]
        ).get("Volumes", [])
    ]

    unassociated_eips = [
        {"public_ip": a["PublicIp"]}
        for a in ec2.describe_addresses().get("Addresses", [])
        if "AssociationId" not in a
    ]

    return {
        "stopped_instances": stopped,
        "unattached_volumes": unattached_volumes,
        "unassociated_elastic_ips": unassociated_eips,
        "summary": (
            f"{len(stopped)} stopped instances, "
            f"{len(unattached_volumes)} unattached volumes, "
            f"{len(unassociated_eips)} idle Elastic IPs"
        ),
    }


@mcp.tool()
def get_monthly_cost(months: int = 3) -> dict:
    """Get AWS spend for the last N months, broken down by service (Cost Explorer).

    Use this to see where the money is actually going and what's driving the
    bill. Requires Cost Explorer to be enabled on the account.
    """
    ce = _client("ce", "us-east-1")  # Cost Explorer is a global endpoint.

    today = date.today()
    y, m = today.year, today.month
    for _ in range(max(1, months)):
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    start = date(y, m, 1).isoformat()
    end = today.isoformat()

    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    months_out = []
    for period in resp.get("ResultsByTime", []):
        services = sorted(
            (
                {
                    "service": g["Keys"][0],
                    "cost": round(float(g["Metrics"]["UnblendedCost"]["Amount"]), 2),
                }
                for g in period.get("Groups", [])
            ),
            key=lambda x: x["cost"],
            reverse=True,
        )
        total = round(sum(s["cost"] for s in services), 2)
        months_out.append(
            {
                "month": period["TimePeriod"]["Start"],
                "total": total,
                "top_services": services[:5],
            }
        )
    return {"period": f"{start} to {end}", "months": months_out}


@mcp.tool()
def scan_security_groups(region: str = "") -> list[dict]:
    """Scan security groups for rules open to the whole internet (0.0.0.0/0)
    on sensitive ports (SSH, RDP, databases).

    Use this to catch the classic mistake — a database or SSH port exposed to
    the entire world. Returns each risky rule with the group and port.
    """
    ec2 = _client("ec2", region)
    findings: list[dict] = []
    for sg in ec2.describe_security_groups().get("SecurityGroups", []):
        for rule in sg.get("IpPermissions", []):
            open_to_world = any(r.get("CidrIp") == "0.0.0.0/0" for r in rule.get("IpRanges", []))
            if not open_to_world:
                continue
            from_port = rule.get("FromPort")
            for port, label in SENSITIVE_PORTS.items():
                if from_port is None or (rule.get("FromPort", 0) <= port <= rule.get("ToPort", 0)):
                    findings.append(
                        {
                            "group_id": sg["GroupId"],
                            "group_name": sg.get("GroupName", ""),
                            "port": port,
                            "service": label,
                            "risk": "open to 0.0.0.0/0",
                        }
                    )
    return findings


@mcp.tool()
def list_s3_buckets() -> list[dict]:
    """List all S3 buckets in the account with name and creation date.

    Use this for a quick inventory of storage — old or forgotten buckets are
    common sources of cost and risk.
    """
    s3 = _client("s3")
    return [
        {"name": b["Name"], "created": b["CreationDate"].isoformat()}
        for b in s3.list_buckets().get("Buckets", [])
    ]


if __name__ == "__main__":
    mcp.run()
