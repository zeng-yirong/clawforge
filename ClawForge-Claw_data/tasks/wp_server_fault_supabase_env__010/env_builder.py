import os
import json
from datetime import datetime, timedelta

def build_env():
    # 创建必要的目录（ops 留给 agent 创建）
    os.makedirs("incidents", exist_ok=True)
    os.makedirs("ops", exist_ok=False)  # 故意不创建，agent 需自己创建

    # 构造 contacts.json（干扰用）
    contacts = [
        {"contact_id": "c001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "c002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "c003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"},
    ]
    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 构造 incident_pool.json 含干扰项
    base_time = datetime(2025, 6, 15, 8, 0, 0)

    incidents = [
        # 目标：两个 ups_outage + critical，按时间升序
        {
            "incident_id": "INC-2025-06-15-001",
            "title": "west4 UPS primary failure – Billing API down",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": (base_time + timedelta(minutes=5)).isoformat(),
            "updated_at": (base_time + timedelta(minutes=10)).isoformat(),
            "description": "UPS unit A in west4 tripped at 08:05. Billing API unreachable.",
            "tags": ["urgent", "power"]
        },
        {
            "incident_id": "INC-2025-06-15-002",
            "title": "Inference Worker power loss – UPS overload",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": (base_time + timedelta(minutes=3)).isoformat(),  # 更早，排序应在第一个
            "updated_at": (base_time + timedelta(minutes=8)).isoformat(),
            "description": "Inference worker cluster lost power due to UPS overload at 08:03.",
            "tags": ["urgent", "power"]
        },
        # 干扰：ups_outage 但 severity 不是 critical
        {
            "incident_id": "INC-2025-06-15-003",
            "title": "UPS battery test – minor dip",
            "category": "ups_outage",
            "severity": "medium",
            "status": "triaged",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "edge-cluster-a12",
            "opened_at": (base_time + timedelta(minutes=20)).isoformat(),
            "updated_at": (base_time + timedelta(minutes=25)).isoformat(),
            "description": "Routine battery test caused voltage dip, no service impact.",
            "tags": ["test"]
        },
        # 干扰：category 拼写错误（ups_outage 写成 ups-outage）
        {
            "incident_id": "INC-2025-06-15-004",
            "title": "west4 UPS flicker",
            "category": "ups-outage",  # 拼写错误
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": (base_time + timedelta(minutes=30)).isoformat(),
            "updated_at": (base_time + timedelta(minutes=35)).isoformat(),
            "description": "UPS flicker observed on west4 spine uplink.",
            "tags": ["power"]
        },
        # 干扰：缺少 title 字段
        {
            "incident_id": "INC-2025-06-15-005",
            # title 缺失
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": (base_time + timedelta(minutes=40)).isoformat(),
            "updated_at": (base_time + timedelta(minutes=45)).isoformat(),
            "description": "Unknown UPS issue on analytics mirror.",
            "tags": ["power"]
        },
        # 干扰：其他类别 critical 工单
        {
            "incident_id": "INC-2025-06-15-006",
            "title": "Network degradation on west4 spine",
            "category": "network_degradation",
            "severity": "critical",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": (base_time + timedelta(minutes=1)).isoformat(),
            "updated_at": (base_time + timedelta(minutes=2)).isoformat(),
            "description": "High packet loss on west4 spine uplink.",
            "tags": ["network"]
        },
        # 干扰：缺少 incident_id
        {
            "title": "Missing ID record",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "watchlist",
            "service": "billing-api",
            "opened_at": (base_time + timedelta(minutes=50)).isoformat(),
            "updated_at": (base_time + timedelta(minutes=55)).isoformat(),
            "description": "No incident_id, should be ignored.",
            "tags": []
        },
    ]

    with open("incidents/incident_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

if __name__ == "__main__":
    build_env()
