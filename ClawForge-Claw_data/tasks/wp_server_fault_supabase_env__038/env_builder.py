import os
import json
from datetime import datetime, timezone

def build_env():
    # 创建目录
    for d in ["data/incidents", "data/attachments", "data"]:
        os.makedirs(d, exist_ok=True)

    # ----- 干扰文件：accounts.json -----
    accounts = {
        "accounts": [
            {"account_id": "acc_001", "display_name": "db-prod", "department": "db_ops", "email": "db@example.com", "permissions": ["read"], "default_region": "us-east-1", "voice": []},
            {"account_id": "acc_002", "display_name": "app-prod", "department": "app_ops", "email": "app@example.com", "permissions": ["read","write"], "default_region": "us-west-2", "voice": []},
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # ----- 干扰文件：contacts.json -----
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
            {"contact_id": "c002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
            {"contact_id": "c003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"},
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # ----- 主要事件池（带干扰项） -----
    incidents = [
        # 目标：3个 open + ups_outage + critical
        {"incident_id": "UPS-001", "title": "UPS main breaker tripped", "category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2025-04-14T02:30:00Z", "updated_at": "2025-04-14T02:31:00Z", "description": "PDU A phase loss", "tags": ["ups","critical"]},
        {"incident_id": "UPS-002", "title": "Battery bank temperature high", "category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2025-04-14T02:35:00Z", "updated_at": "2025-04-14T02:36:00Z", "description": "Battery room temp >40C", "tags": ["ups","critical"]},
        {"incident_id": "UPS-003", "title": "UPS overload alarm", "category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "edge-cluster-a12", "opened_at": "2025-04-14T02:40:00Z", "updated_at": "2025-04-14T02:41:00Z", "description": "Load > 95%", "tags": ["ups","critical"]},

        # 干扰：ups_outage 但 status = triaged
        {"incident_id": "UPS-004", "title": "UPS battery test failed", "category": "ups_outage", "severity": "critical", "status": "triaged", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2025-04-14T01:00:00Z", "updated_at": "2025-04-14T01:05:00Z", "description": "Scheduled test failure", "tags": ["ups","critical"]},

        # 干扰：ups_outage 但 severity = medium
        {"incident_id": "UPS-005", "title": "UPS fan noise", "category": "ups_outage", "severity": "medium", "status": "open", "assigned_team": "power_ops", "ticket_type": "watchlist", "service": "edge-cluster-a12", "opened_at": "2025-04-14T00:00:00Z", "updated_at": "2025-04-14T00:10:00Z", "description": "Audible fan bearing wear", "tags": ["ups","medium"]},

        # 干扰：其他类别 critical
        {"incident_id": "NET-001", "title": "West4 spine packet loss", "category": "network_degradation", "severity": "critical", "status": "open", "assigned_team": "network_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2025-04-14T02:00:00Z", "updated_at": "2025-04-14T02:05:00Z", "description": "5% packet loss", "tags": ["network","critical"]},
        {"incident_id": "DB-001", "title": "Replica lag spike", "category": "db_replica_lag", "severity": "critical", "status": "open", "assigned_team": "db_ops", "ticket_type": "risk_work_order", "service": "analytics-mirror", "opened_at": "2025-04-14T02:10:00Z", "updated_at": "2025-04-14T02:12:00Z", "description": "Lag > 300s", "tags": ["db","critical"]},
        {"incident_id": "SVC-001", "title": "billing-api down", "category": "service_down", "severity": "critical", "status": "open", "assigned_team": "app_ops", "ticket_type": "risk_work_order", "service": "billing-api", "opened_at": "2025-04-14T02:20:00Z", "updated_at": "2025-04-14T02:21:00Z", "description": "HTTP 503", "tags": ["service","critical"]},

        # 脏数据：缺少 severity 字段
        {"incident_id": "JUNK-001", "title": "Weird sensor reading", "category": "ups_outage", "status": "open", "assigned_team": "power_ops", "ticket_type": "watchlist", "service": "edge-cluster-a12", "opened_at": "2025-04-14T03:00:00Z", "updated_at": "2025-04-14T03:01:00Z", "description": "Unknown", "tags": []},

        # 脏数据：category 拼写错误
        {"incident_id": "UPS-xxx", "title": "UPS comm lost", "category": "ups-outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "edge-cluster-a12", "opened_at": "2025-04-14T03:05:00Z", "updated_at": "2025-04-14T03:06:00Z", "description": "SNMP timeout", "tags": ["ups","critical"]},
    ]
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f)

    # ----- 附件 -----
    runbook_content = """# UPS and Service Outage Runbook

## Scope
This runbook covers UPS power outages and critical service failures.

## Steps for UPS Outage (category=ups_outage, severity=critical)
1. Acknowledge the incident.
2. Dispatch power team (contact Lena Park).
3. Initiate failover to backup UPS if available.
4. Set incident status to resolved.

## Output format for remediation results
All processed incidents must be written to `ops/remediation_results.json` as a JSON array.
Each entry must contain the following fields:
- incident_id: string
- action: string (must be "remediated")
- status: string (must be "resolved")

Example:
[
    {"incident_id": "UPS-001", "action": "remediated", "status": "resolved"},
    {"incident_id": "UPS-002", "action": "remediated", "status": "resolved"}
]
"""
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    contract_content = """# Simulated Supabase Write Contract
This document defines the contract for writing resolution data to Supabase.
Not applicable for this runbook exercise.
"""
    with open("data/attachments/supabase_write_contract.md", "w") as f:
        f.write(contract_content)

    # 附件索引（干扰）
    attachments_meta = {
        "attachments": [
            {"path": "data/attachments/runbook_ups_and_service.md", "title": "UPS and Service Outage Runbook", "kind": "runbook", "description": "Runbook for UPS and service outage handling"},
            {"path": "data/attachments/supabase_write_contract.md", "title": "Simulated Supabase Write Contract", "kind": "write_contract", "description": "Contract for writing to Supabase"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments_meta, f)

    # 确保 ops 目录不存在（让 agent 创建）
    # 我们不提前创建 ops，agent 必须自己创建

if __name__ == "__main__":
    build_env()
