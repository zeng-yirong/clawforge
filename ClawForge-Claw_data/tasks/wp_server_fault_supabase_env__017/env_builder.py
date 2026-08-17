import os
import json
import uuid
from datetime import datetime, timedelta

def build_env():
    # 创建目录结构
    os.makedirs("incidents", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("contacts", exist_ok=True)

    # 联系人
    contacts = [
        {"contact_id": "ct-001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "ct-002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "ct-003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"},
    ]
    with open("contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 附件
    attachments = [
        {
            "path": "attachments/runbook_ups_and_service.md",
            "title": "UPS and Service Outage Runbook",
            "kind": "runbook",
            "description": "Standard operating procedure for UPS and service-down incidents."
        },
        {
            "path": "attachments/supabase_write_contract.md",
            "title": "Simulated Supabase Write Contract",
            "kind": "write_contract",
            "description": "Contract describing how to write resolved incidents to Supabase."
        },
    ]
    with open("attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 创建 runbook 内容
    runbook_content = """# UPS and Service Outage Runbook

## Steps
1. Identify all open incidents with category `ups_outage` or `service_down`.
2. For each incident, execute the following remediation:
   - Acknowledge incident (set status to `triaged`).
   - Apply power failover or service restart according to severity.
   - Mark incident as `resolved` after verification.
3. Record all actions in a structured report.
"""
    with open("attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # 无关的附件
    with open("attachments/supabase_write_contract.md", "w") as f:
        f.write("# Supabase Write Contract\n\nThis is a placeholder contract for writing to Supabase.\n")

    # 工单池 - 包含大量干扰项
    base_time = datetime(2025, 6, 15, 2, 0, 0)
    incidents = [
        # 目标：2个UPS中断 + 2个服务宕机（但只有open的才需要处理，这里设三个open一个triaged）
        {"incident_id": "INC-001", "title": "UPS in west wing tripped", "category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "edge-cluster-a12", "opened_at": (base_time - timedelta(hours=2)).isoformat(), "updated_at": base_time.isoformat(), "description": "UPS failure in west data center", "tags": ["power", "urgent"]},
        {"incident_id": "INC-002", "title": "Main UPS battery drained", "category": "ups_outage", "severity": "high", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "billing-api", "opened_at": (base_time - timedelta(hours=5)).isoformat(), "updated_at": base_time.isoformat(), "description": "Battery backup below threshold", "tags": ["power", "battery"]},
        {"incident_id": "INC-003", "title": "Billing API unreachable", "category": "service_down", "severity": "critical", "status": "open", "assigned_team": "app_ops", "ticket_type": "risk_work_order", "service": "billing-api", "opened_at": (base_time - timedelta(hours=1)).isoformat(), "updated_at": base_time.isoformat(), "description": "Billing service returns 503", "tags": ["api", "downtime"]},
        {"incident_id": "INC-004", "title": "Analytics mirror lag", "category": "db_replica_lag", "severity": "medium", "status": "open", "assigned_team": "db_ops", "ticket_type": "watchlist", "service": "analytics-mirror", "opened_at": (base_time - timedelta(hours=6)).isoformat(), "updated_at": base_time.isoformat(), "description": "Replica lag 30 seconds", "tags": ["db", "replication"]},
        {"incident_id": "INC-005", "title": "West spine uplink flapping", "category": "network_degradation", "severity": "high", "status": "open", "assigned_team": "network_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": (base_time - timedelta(hours=3)).isoformat(), "updated_at": base_time.isoformat(), "description": "Link flaps every 30 seconds", "tags": ["network", "flapping"]},
        {"incident_id": "INC-006", "title": "Inference worker OOM", "category": "service_down", "severity": "high", "status": "triaged", "assigned_team": "ml_platform", "ticket_type": "risk_work_order", "service": "inference-worker", "opened_at": (base_time - timedelta(hours=4)).isoformat(), "updated_at": base_time.isoformat(), "description": "OOM killed multiple workers", "tags": ["ml", "memory"]},
        # 这个服务宕机但已 triaged 不应该被处理（prompt说“open”工单）
        {"incident_id": "INC-007", "title": "UPS maintenance window expired", "category": "ups_outage", "severity": "medium", "status": "open", "assigned_team": "power_ops", "ticket_type": "watchlist", "service": "west4-spine-uplink", "opened_at": (base_time - timedelta(hours=8)).isoformat(), "updated_at": base_time.isoformat(), "description": "Scheduled maintenance not completed", "tags": ["power", "maintenance"]},
    ]
    with open("incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # 账户（备用，但此处不严格要求使用）
    accounts = [
        {"account_id": "acc-01", "display_name": "nikhil.rao@northstar.example.com", "department": "NOC", "email": "nikhil.rao@northstar.example.com", "permissions": ["ops_admin"], "default_region": "us-east", "voice": ["internal"]},
        {"account_id": "acc-02", "display_name": "harper.zhou@northstar.example.com", "department": "DBRE", "email": "harper.zhou@northstar.example.com", "permissions": ["read"], "default_region": "us-east", "voice": ["internal"]},
    ]
    with open("accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
