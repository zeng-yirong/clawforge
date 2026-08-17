import os
import json
import random
import string
from datetime import datetime, timedelta

def build_env():
    # 确保工作目录是 
    # 不要添加绝对前缀

    # 创建必要的目录
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    # ops 目录让 agent 自己创建，我们这里不预创建

    # 生成 incident_pool.json —— 包含正确工单 + 大量干扰
    incidents = []
    now = datetime.utcnow()

    # 辅助函数：随机整数
    def rand_id():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # 1. 目标工单：category=ups_outage, severity=critical
    target_ids = ["INC-UPS-001", "INC-UPS-002", "INC-UPS-003"]
    for i, tid in enumerate(target_ids):
        incidents.append({
            "incident_id": tid,
            "title": f"UPS failure west4 spine uplink {i+1}",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": (now - timedelta(hours=2, minutes=random.randint(0,59))).isoformat(),
            "updated_at": now.isoformat(),
            "description": f"UPS module {rand_id()} malfunction leading to connectivity loss.",
            "tags": ["ups", "west4", "critical"]
        })

    # 2. 干扰工单1：category=ups_outage, severity=high (不应处理)
    incidents.append({
        "incident_id": "INC-UPS-004",
        "title": "UPS battery low warning west4",
        "category": "ups_outage",
        "severity": "high",
        "status": "open",
        "assigned_team": "power_ops",
        "ticket_type": "watchlist",
        "service": "west4-spine-uplink",
        "opened_at": (now - timedelta(hours=5)).isoformat(),
        "updated_at": (now - timedelta(hours=1)).isoformat(),
        "description": "UPS battery level dropped below threshold.",
        "tags": ["ups", "warning"]
    })

    # 3. 干扰工单2：category=service_down, severity=critical (不是ups_outage)
    incidents.append({
        "incident_id": "INC-SRV-001",
        "title": "billing-api unreachable",
        "category": "service_down",
        "severity": "critical",
        "status": "triaged",
        "assigned_team": "app_ops",
        "ticket_type": "risk_work_order",
        "service": "billing-api",
        "opened_at": (now - timedelta(hours=3)).isoformat(),
        "updated_at": now.isoformat(),
        "description": "Billing API returning 503 errors.",
        "tags": ["api", "down"]
    })

    # 4. 干扰工单3：category=ups_outage, severity=critical, status=closed (不应处理)
    incidents.append({
        "incident_id": "INC-UPS-005",
        "title": "UPS test incident (already closed)",
        "category": "ups_outage",
        "severity": "critical",
        "status": "closed",
        "assigned_team": "power_ops",
        "ticket_type": "risk_work_order",
        "service": "west4-spine-uplink",
        "opened_at": (now - timedelta(days=1)).isoformat(),
        "updated_at": (now - timedelta(hours=20)).isoformat(),
        "description": "False alarm.",
        "tags": ["test"]
    })

    # 5. 干扰工单4：category=db_replica_lag, severity=critical (完全无关)
    incidents.append({
        "incident_id": "INC-DB-001",
        "title": "analytics-mirror replica lag 180s",
        "category": "db_replica_lag",
        "severity": "critical",
        "status": "open",
        "assigned_team": "db_ops",
        "ticket_type": "watchlist",
        "service": "analytics-mirror",
        "opened_at": (now - timedelta(hours=1)).isoformat(),
        "updated_at": now.isoformat(),
        "description": "Replication lag exceeding threshold.",
        "tags": ["db", "replica"]
    })

    # 6. 干扰工单5：category=network_degradation, severity=high (无关)
    incidents.append({
        "incident_id": "INC-NET-001",
        "title": "Edge cluster A12 packet loss 5%",
        "category": "network_degradation",
        "severity": "high",
        "status": "triaged",
        "assigned_team": "network_ops",
        "ticket_type": "risk_work_order",
        "service": "edge-cluster-a12",
        "opened_at": (now - timedelta(minutes=45)).isoformat(),
        "updated_at": now.isoformat(),
        "description": "5% packet loss detected on cluster interconnect.",
        "tags": ["network", "packetloss"]
    })

    # 写入工单池
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # 创建 attachments.json —— 包含 runbook 和 write_contract 作为辅助
    attachments = [
        {
            "path": "attachments/runbook_ups_and_service.md",
            "title": "UPS and Service Outage Runbook",
            "kind": "runbook",
            "description": "Steps to remediate UPS outage incidents: 1. verify power feed, 2. restart affected service, 3. confirm connectivity."
        },
        {
            "path": "attachments/supabase_write_contract.md",
            "title": "Simulated Supabase Write Contract",
            "kind": "write_contract",
            "description": "Schema for writing resolution records: must contain 'incidents' array each with incident_id, status, action."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 创建 runbook 文件本身（供 agent 阅读）
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write("# UPS and Service Outage Runbook\n\n1. Verify power feed status\n2. Restart affected service (west4-spine-uplink)\n3. Confirm connectivity\n4. Mark incident as resolved\n")
    with open("data/attachments/supabase_write_contract.md", "w") as f:
        f.write("# Simulated Supabase Write Contract\n\nResolution object must have:\n```json\n{\n  \"incidents\": [\n    {\n      \"incident_id\": \"string\",\n      \"status\": \"resolved\",\n      \"action\": \"batch_remediate\"\n    }\n  ]\n}\n```\n")

    # 额外干扰文件：accounts.json, contacts.json
    accounts = [
        {"account_id": "acc-001", "display_name": "John Doe", "department": "power_ops", "email": "john.doe@northstar.example.com", "permissions": ["ops"], "default_region": "west4", "voice": ["en"]},
        {"account_id": "acc-002", "display_name": "Jane Smith", "department": "db_ops", "email": "jane.smith@northstar.example.com", "permissions": ["admin"], "default_region": "east1", "voice": ["en","es"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "con-001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "con-002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "con-003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 创建一些脏数据文件（干扰）
    with open("data/incidents/old_pool.json", "w") as f:
        f.write("this is not valid json")
    with open("data/temp.log", "w") as f:
        f.write("2025-03-21 03:15:00 UPS alarm triggered\n")
        f.write("2025-03-21 03:16:00 west4 spine uplink down\n")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
