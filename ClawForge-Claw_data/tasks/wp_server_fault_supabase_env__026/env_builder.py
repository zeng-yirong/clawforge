import os
import json
import shutil

def build_env():
    # 清理并创建目录结构
    if os.path.exists("incidents"):
        shutil.rmtree("incidents")
    if os.path.exists("attachments"):
        shutil.rmtree("attachments")
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    os.makedirs("incidents")
    os.makedirs("attachments")
    os.makedirs("ops")

    # 构建攻击性事件池（含干扰项）
    incidents = [
        # 真正的目标：ups_outage, status=open (2个)
        {"incident_id": "I-2024-0001", "title": "UPS west4 rack A12 power drop", "category": "ups_outage",
         "severity": "critical", "status": "open", "assigned_team": "power_ops",
         "ticket_type": "risk_work_order", "service": "west4-spine-uplink",
         "opened_at": "2024-11-18T01:30:00Z", "updated_at": "2024-11-18T01:30:00Z",
         "description": "UPS output voltage below threshold", "tags": ["ups", "west4"]},
        {"incident_id": "I-2024-0002", "title": "UPS west4 rack B07 battery failure", "category": "ups_outage",
         "severity": "critical", "status": "open", "assigned_team": "power_ops",
         "ticket_type": "risk_work_order", "service": "west4-spine-uplink",
         "opened_at": "2024-11-18T00:15:00Z", "updated_at": "2024-11-18T00:15:00Z",
         "description": "Battery backup failed", "tags": ["ups", "west4", "battery"]},

        # 干扰项：ups_outage 但状态已经是 triaged
        {"incident_id": "I-2024-0003", "title": "UPS east3 rack C02 surge", "category": "ups_outage",
         "severity": "high", "status": "triaged", "assigned_team": "power_ops",
         "ticket_type": "risk_work_order", "service": "analytics-mirror",
         "opened_at": "2024-11-17T22:10:00Z", "updated_at": "2024-11-17T22:10:00Z",
         "description": "Transient spike resolved", "tags": ["ups", "east3"]},
        {"incident_id": "I-2024-0004", "title": "UPS main hall PDU overload", "category": "ups_outage",
         "severity": "medium", "status": "triaged", "assigned_team": "power_ops",
         "ticket_type": "watchlist", "service": "billing-api",
         "opened_at": "2024-11-17T20:00:00Z", "updated_at": "2024-11-17T20:05:00Z",
         "description": "Load balanced manually", "tags": ["ups", "main"]},

        # 干扰项：其他类别的事件
        {"incident_id": "I-2024-0005", "title": "DB replica lag on analytics-mirror", "category": "db_replica_lag",
         "severity": "critical", "status": "open", "assigned_team": "db_ops",
         "ticket_type": "risk_work_order", "service": "analytics-mirror",
         "opened_at": "2024-11-17T19:00:00Z", "updated_at": "2024-11-17T19:10:00Z",
         "description": "Replication lag > 5min", "tags": ["db", "replica"]},
        {"incident_id": "I-2024-0006", "title": "west4 spine uplink packet loss", "category": "network_degradation",
         "severity": "high", "status": "open", "assigned_team": "network_ops",
         "ticket_type": "risk_work_order", "service": "west4-spine-uplink",
         "opened_at": "2024-11-18T00:30:00Z", "updated_at": "2024-11-18T00:35:00Z",
         "description": "0.5% packet loss detected", "tags": ["network"]},

        # 重复ID干扰（但id唯一，这里故意放一个假字段缺失项-无incident_id）
        {"title": "Missing ID fake", "category": "ups_outage", "severity": "critical", "status": "open",
         "opened_at": "2024-11-18T02:00:00Z", "description": "no id field"}
    ]

    with open("incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents, "wrapper": "incidents", "key": "incident_id"}, f, indent=2)

    # 创建一份runbook附件（仅做干扰，不用于验证）
    runbook_content = """# UPS and Service Outage Runbook

## 1. Confirm UPS status via monitoring dashboard
## 2. For open incidents, escalate to power_ops if critical
## 3. Contact:
   - Facilities Power Coordinator: lena.park@northstar.example.com
   - NOC Lead: nikhil.rao@northstar.example.com
## 4. After resolution, update status to triaged in incident_pool.json
"""
    with open("attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # 再创建一个无关附件
    with open("attachments/supabase_write_contract.md", "w") as f:
        f.write("# Simulated Supabase Write Contract\n(This is not needed for this task)")

if __name__ == "__main__":
    build_env()
