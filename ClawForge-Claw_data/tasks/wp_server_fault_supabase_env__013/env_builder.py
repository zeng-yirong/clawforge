import os, json, random
from datetime import datetime, timedelta

def build_env():
    # 创建必要的子目录
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 1. 核心 incident_pool.json（包含干扰项，共25条）
    incidents = []
    base_time = datetime.now() - timedelta(days=1)

    # 定义满足条件的两个目标事故 (答案唯一)
    target_ids = ["INC-2026-04-12-001", "INC-2026-04-12-002"]
    for tid in target_ids:
        incidents.append({
            "incident_id": tid,
            "title": f"Replica lag spike on {tid}",
            "category": "db_replica_lag",
            "severity": "critical",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": (base_time - timedelta(hours=2)).isoformat(),
            "updated_at": (base_time - timedelta(minutes=30)).isoformat(),
            "description": "Long-running transaction blocking row-level locks.",
            "tags": ["replica", "lock", "urgent"]
        })

    # 干扰项 A: 同类型但已 triaged
    incidents.append({
        "incident_id": "INC-2026-04-12-003",
        "title": "Replica lag spike - already triaged",
        "category": "db_replica_lag",
        "severity": "critical",
        "status": "triaged",
        "assigned_team": "db_ops",
        "ticket_type": "risk_work_order",
        "service": "analytics-mirror",
        "opened_at": (base_time - timedelta(hours=4)).isoformat(),
        "updated_at": (base_time - timedelta(hours=1)).isoformat(),
        "description": "Resolved by kill signal.",
        "tags": ["replica", "lock"]
    })

    # 干扰项 B: 同类型但 severity=high
    incidents.append({
        "incident_id": "INC-2026-04-12-004",
        "title": "Replica lag moderate",
        "category": "db_replica_lag",
        "severity": "high",
        "status": "open",
        "assigned_team": "db_ops",
        "ticket_type": "risk_work_order",
        "service": "analytics-mirror",
        "opened_at": (base_time - timedelta(hours=6)).isoformat(),
        "updated_at": (base_time - timedelta(hours=2)).isoformat(),
        "description": "Elevated lag but not critical.",
        "tags": ["replica"]
    })

    # 干扰项 C: 完全不同的类别
    for i in range(5, 15):
        cat = random.choice(["ups_outage", "service_down", "network_degradation"])
        sev = random.choice(["high", "medium"])
        st = random.choice(["open", "triaged"])
        incidents.append({
            "incident_id": f"INC-2026-04-12-{i:03d}",
            "title": f"{cat} incident {i}",
            "category": cat,
            "severity": sev,
            "status": st,
            "assigned_team": random.choice(["power_ops", "network_ops", "app_ops"]),
            "ticket_type": "watchlist",
            "service": random.choice(["billing-api", "edge-cluster-a12", "west4-spine-uplink"]),
            "opened_at": (base_time - timedelta(hours=random.randint(1,12))).isoformat(),
            "updated_at": (base_time - timedelta(minutes=random.randint(10,120))).isoformat(),
            "description": "Random noise incident.",
            "tags": [cat]
        })

    # 干扰项 D: db_replica_lag 且 status=open 但 severity=medium
    incidents.append({
        "incident_id": "INC-2026-04-12-015",
        "title": "Minor replica lag",
        "category": "db_replica_lag",
        "severity": "medium",
        "status": "open",
        "assigned_team": "db_ops",
        "ticket_type": "risk_work_order",
        "service": "analytics-mirror",
        "opened_at": (base_time - timedelta(hours=8)).isoformat(),
        "updated_at": (base_time - timedelta(hours=3)).isoformat(),
        "description": "Not critical.",
        "tags": ["replica"]
    })

    # 额外干扰: 近似重复 ID 但条件不符
    for i in range(16, 25):
        st = "open" if i % 2 == 0 else "triaged"
        sev = "critical" if i % 3 == 0 else "high"
        incidents.append({
            "incident_id": f"INC-2026-04-12-{i:03d}",
            "title": f"Replica-like incident {i}",
            "category": "db_replica_lag" if i < 20 else "ups_outage",
            "severity": sev,
            "status": st,
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": (base_time - timedelta(hours=random.randint(1,10))).isoformat(),
            "updated_at": (base_time - timedelta(minutes=random.randint(10,90))).isoformat(),
            "description": "Tricky entry.",
            "tags": ["replica", "tricky"]
        })

    # 写入 incident pool
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # 2. 干扰性辅助文件（accounts, contacts, attachments）
    # accounts
    accounts = [
        {
            "account_id": "acc-001",
            "display_name": "Harper Zhou",
            "department": "Database Reliability",
            "email": "harper.zhou@northstar.example.com",
            "permissions": ["admin", "kill_transaction"],
            "default_region": "us-east-1",
            "voice": ["en"]
        }
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # contacts
    contacts = [
        {"contact_id": "c-001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "c-002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "c-003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # attachments
    attachments = [
        {"path": "data/attachments/runbook_ups_and_service.md", "title": "UPS and Service Outage Runbook", "kind": "runbook", "description": "Runbook for power and service recovery."},
        {"path": "data/attachments/supabase_write_contract.md", "title": "Simulated Supabase Write Contract", "kind": "write_contract", "description": "Contract for writing resolution to Supabase."}
    ]
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)
    # 创建占位附件文件
    for att in attachments:
        with open(att["path"], "w") as f:
            f.write(f"# {att['title']}\n\nPlaceholder content.\n")

if __name__ == "__main__":
    build_env()
