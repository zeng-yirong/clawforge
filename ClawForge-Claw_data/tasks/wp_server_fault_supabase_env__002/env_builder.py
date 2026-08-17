import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    # ops 目录由 agent 自己创建，我们不预先创建

    # 创建干扰和脏数据丰富的工单池
    incidents = {
        "incidents": [
            # 满足条件的三个工单（ups_outage critical + service_down critical）
            {
                "incident_id": "INC-003",
                "title": "UPS Battery Failure - Rack A12",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": "2025-03-21T01:30:00Z",
                "updated_at": "2025-03-21T01:45:00Z",
                "description": "UPS in bay 3 reporting complete battery drain.",
                "tags": ["ups", "power", "critical"]
            },
            {
                "incident_id": "INC-008",
                "title": "Service Down – billing-api",
                "category": "service_down",
                "severity": "critical",
                "status": "open",
                "assigned_team": "app_ops",
                "ticket_type": "risk_work_order",
                "service": "billing-api",
                "opened_at": "2025-03-21T02:10:00Z",
                "updated_at": "2025-03-21T02:20:00Z",
                "description": "billing-api returns 503 for all requests.",
                "tags": ["api", "service-down", "critical"]
            },
            {
                "incident_id": "INC-012",
                "title": "UPS Overload – West Wing",
                "category": "ups_outage",
                "severity": "critical",
                "status": "triaged",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "west4-spine-uplink",
                "opened_at": "2025-03-20T23:55:00Z",
                "updated_at": "2025-03-21T00:10:00Z",
                "description": "UPS load exceeds 95%, imminent shutdown.",
                "tags": ["ups", "power", "overload"]
            },
            # 干扰: 类别匹配但 severity 不符合（大写、空格、不同值）
            {
                "incident_id": "INC-001",
                "title": "UPS Fuse Blown",
                "category": "ups_outage",
                "severity": "Critical",  # 首字母大写，应排除
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": "2025-03-20T10:00:00Z",
                "updated_at": "2025-03-20T10:15:00Z",
                "description": "Fuse on UPS unit 4 blown.",
                "tags": ["ups"]
            },
            {
                "incident_id": "INC-004",
                "title": "Service Down – inference-worker",
                "category": "service_down",
                "severity": "critical ",  # 尾部空格，应排除
                "status": "open",
                "assigned_team": "ml_platform",
                "ticket_type": "risk_work_order",
                "service": "inference-worker",
                "opened_at": "2025-03-21T00:30:00Z",
                "updated_at": "2025-03-21T00:40:00Z",
                "description": "Inference worker unreachable.",
                "tags": ["ml", "down"]
            },
            # 干扰: 其他类别且 severity 为 critical，但不匹配类别
            {
                "incident_id": "INC-007",
                "title": "DB Replica Lag – analytics-mirror",
                "category": "db_replica_lag",
                "severity": "critical",
                "status": "open",
                "assigned_team": "db_ops",
                "ticket_type": "watchlist",
                "service": "analytics-mirror",
                "opened_at": "2025-03-21T00:45:00Z",
                "updated_at": "2025-03-21T01:00:00Z",
                "description": "Replica lag > 300 seconds.",
                "tags": ["db", "replication"]
            },
            # 干扰: 匹配类别但 severity 为 high
            {
                "incident_id": "INC-011",
                "title": "Service Degraded – billing-api",
                "category": "service_down",
                "severity": "high",
                "status": "open",
                "assigned_team": "app_ops",
                "ticket_type": "watchlist",
                "service": "billing-api",
                "opened_at": "2025-03-21T01:00:00Z",
                "updated_at": "2025-03-21T01:10:00Z",
                "description": "billing-api response time > 5s.",
                "tags": ["api", "degraded"]
            },
            # 干扰: 匹配类别但 status 为 closed（不应考虑）
            {
                "incident_id": "INC-015",
                "title": "Past UPS Outage Resolved",
                "category": "ups_outage",
                "severity": "critical",
                "status": "closed",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "east-rack-b7",
                "opened_at": "2025-03-19T14:00:00Z",
                "updated_at": "2025-03-19T15:00:00Z",
                "description": "UPS was fixed earlier.",
                "tags": ["ups", "resolved"]
            },
            # 额外干扰: 正常工单，category/severity 均不匹配
            {
                "incident_id": "INC-002",
                "title": "Network Degradation – west4-spine-uplink",
                "category": "network_degradation",
                "severity": "medium",
                "status": "open",
                "assigned_team": "network_ops",
                "ticket_type": "watchlist",
                "service": "west4-spine-uplink",
                "opened_at": "2025-03-20T08:30:00Z",
                "updated_at": "2025-03-20T09:00:00Z",
                "description": "Packet loss 5% on uplink.",
                "tags": ["network", "uplink"]
            }
        ]
    }

    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

    # 标准操作手册（runbook），agent 必须读取并按照里面的规则执行
    runbook_content = """Standard Operating Procedure for Critical Incidents
================================================================
1. Identify all incidents with category 'ups_outage' or 'service_down' and severity 'critical'.
2. Sort them by incident_id alphabetically.
3. Write their incident_id values as a JSON array to ops/remediated_ids.json.

Note: Use exact string comparison (case-sensitive, no spaces)."""
    with open("data/attachments/runbook.md", "w") as f:
        f.write(runbook_content)

    # 额外干扰文件（不属于任务要求，但增加环境真实感）
    os.makedirs("data/contacts", exist_ok=True)
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Harper Zhou", "role": "Database Reliability Engineer",
             "email": "harper.zhou@northstar.example.com"},
            {"contact_id": "C002", "name": "Lena Park", "role": "Facilities Power Coordinator",
             "email": "lena.park@northstar.example.com"},
            {"contact_id": "C003", "name": "Nikhil Rao", "role": "NOC Lead",
             "email": "nikhil.rao@northstar.example.com"}
        ]
    }
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
