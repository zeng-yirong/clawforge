import os
import json
import random
import datetime

def build_env():
    # ── 目录结构 ──
    dirs = ["data/incidents", "data/attachments", "db_dumps", "raw_logs"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ── incident_pool.json (主数据) ──
    incidents = [
        # 真实目标1：ups_outage, critical, open, risk_work_order
        {
            "incident_id": "INC-001",
            "title": "UPS #3 battery failure in cage 7",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-01T03:00:00Z",
            "updated_at": "2025-04-01T03:15:00Z",
            "description": "UPS battery bank tripped, partial power loss to networking gear.",
            "tags": ["power", "urgent"]
        },
        # 真实目标2：service_down, critical, open, watchlist
        {
            "incident_id": "INC-002",
            "title": "Billing API unreachable after core switch restart",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "watchlist",
            "service": "billing-api",
            "opened_at": "2025-04-01T02:45:00Z",
            "updated_at": "2025-04-01T03:20:00Z",
            "description": "Service down, engineers already on site.",
            "tags": ["networking", "critical"]
        },
        # 干扰项：ups_outage 但 severity 不是 critical
        {
            "incident_id": "INC-003",
            "title": "UPS #1 low battery alert",
            "category": "ups_outage",
            "severity": "medium",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-01T01:00:00Z",
            "updated_at": "2025-04-01T03:00:00Z",
            "description": "Routine battery degradation, not critical.",
            "tags": ["power", "scheduled"]
        },
        # 干扰项：service_down 但 status 不是 open
        {
            "incident_id": "INC-004",
            "title": "Inference worker latency spike (already triaged)",
            "category": "service_down",
            "severity": "high",
            "status": "triaged",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-03-31T23:00:00Z",
            "updated_at": "2025-04-01T01:00:00Z",
            "description": "Resolved by restart, waiting for post-mortem.",
            "tags": ["ml", "done"]
        },
        # 干扰项：完全无关的类别
        {
            "incident_id": "INC-005",
            "title": "Replica lag on analytics-mirror",
            "category": "db_replica_lag",
            "severity": "medium",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "watchlist",
            "service": "analytics-mirror",
            "opened_at": "2025-04-01T02:00:00Z",
            "updated_at": "2025-04-01T03:30:00Z",
            "description": "Lag has been decreasing, no action needed.",
            "tags": ["db", "monitoring"]
        }
    ]
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # ── attachments.json ──
    attachments = [
        {
            "path": "data/attachments/runbook_ups_and_service.md",
            "title": "UPS and Service Outage Runbook",
            "kind": "runbook",
            "description": "Contains remediation rules for ups_outage and service_down incidents."
        },
        {
            "path": "data/attachments/supabase_write_contract.md",
            "title": "Simulated Supabase Write Contract",
            "kind": "write_contract",
            "description": "Template for writing resolutions to Supabase, not needed now."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ── 真实 runbook 内容 ──
    runbook_content = """# UPS and Service Outage Runbook

## Remediation Rules

- **ups_outage**, severity **critical**, status **open**, ticket_type **risk_work_order** → action: `remediate`
- **service_down**, severity **critical**, status **open**, ticket_type **watchlist** → action: `remediate`

## Resolution Template

Place file at `ops/resolution.json` with the following structure:

[
    {
        "incident_id": "<id>",
        "action": "remediate"
    },
    ...
]
"""
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # ── 干扰 runbook 的内容 ──
    contract_content = """# Supabase Write Contract
This document describes the schema for writing resolutions to the Supabase table.
Not needed for this task.
"""
    with open("data/attachments/supabase_write_contract.md", "w") as f:
        f.write(contract_content)

    # ── 其他干扰文件 ──
    # db_dumps 目录放两个假 dump
    for i in range(2):
        dump = {
            "dump_id": f"dump_{i}",
            "table": "incidents",
            "rows": [
                {"id": f"fake_{j}", "data": "garbage"}
                for j in range(3)
            ]
        }
        with open(f"db_dumps/backup_{i}.json", "w") as f:
            json.dump(dump, f, indent=2)
    # raw_logs 目录放慢查询日志（干扰）
    with open("raw_logs/slow_query.log", "w") as f:
        for _ in range(20):
            f.write(f"# Time: 2025-04-01T03:00:0{random.randint(0,9)}\n")
            f.write("# Query_time: 12.3  Lock_time: 5.6\n")
            f.write("SELECT * FROM incidents WHERE category='ups_outage';\n")

    # ── contacts.json ── 不需要用到但加一个
    contacts = [
        {"contact_id": "C001", "name": "Harper Zhou", "role": "DRE", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "C002", "name": "Lena Park", "role": "FPC", "email": "lena.park@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ── accounts.json ── 干扰
    accounts = [
        {"account_id": "A001", "display_name": "Power Ops", "department": "Facilities", "email": "power@northstar.example.com", "permissions": ["read", "write"], "default_region": "us-east-1", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
