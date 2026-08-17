import os
import json

def build_env():
    os.makedirs("ops", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)

    # --- runbook ---
    runbook_content = """# UPS and Service Outage Runbook

## Scope
This runbook covers incidents with categories:
- `ups_outage`
- `service_down`

## Triage Criteria
Only incidents with the following attributes require immediate remediation:
- status: `open`
- ticket_type: `risk_work_order`
- severity: `critical` or `high`

## Action
Extract incident IDs matching the criteria, sort by severity (critical first), then by incident ID alphabetically.
Write the sorted list as a JSON array to `ops/remediation_targets.json`.
Also produce a CSV summary with columns: incident_id, title, severity, service, saved at `ops/audit_summary.csv`.
"""
    with open("attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # --- incident pool (wrapper = "incidents") ---
    incidents = [
        {"incident_id": "inc-001", "title": "UPS故障-主库Billing API", "category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "db_ops", "ticket_type": "risk_work_order", "service": "billing-api", "opened_at": "2025-02-10T03:00:00Z", "updated_at": "2025-02-10T03:05:00Z", "description": "Primary datacenter UPS failure impacting billing API", "tags": ["power", "critical"]},
        {"incident_id": "inc-002", "title": "DB复制延迟", "category": "db_replica_lag", "severity": "high", "status": "open", "assigned_team": "db_ops", "ticket_type": "risk_work_order", "service": "analytics-mirror", "opened_at": "2025-02-10T02:00:00Z", "updated_at": "2025-02-10T02:10:00Z", "description": "Replica lag spike", "tags": ["replication"]},
        {"incident_id": "inc-003", "title": "Analytics Mirror服务降级", "category": "service_down", "severity": "high", "status": "open", "assigned_team": "app_ops", "ticket_type": "risk_work_order", "service": "analytics-mirror", "opened_at": "2025-02-10T03:10:00Z", "updated_at": "2025-02-10T03:12:00Z", "description": "Analytics mirror unreachable", "tags": ["service-down"]},
        {"incident_id": "inc-004", "title": "UPS波动-次要区域", "category": "ups_outage", "severity": "medium", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "edge-cluster-a12", "opened_at": "2025-02-10T03:20:00Z", "updated_at": "2025-02-10T03:22:00Z", "description": "Minor UPS fluctuation", "tags": ["power"]},
        {"incident_id": "inc-005", "title": "West4 Spine上行链路中断", "category": "service_down", "severity": "critical", "status": "open", "assigned_team": "network_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2025-02-10T03:30:00Z", "updated_at": "2025-02-10T03:35:00Z", "description": "West4 spine uplink down due to power surge", "tags": ["network", "critical"]},
        {"incident_id": "inc-006", "title": "UPS恢复-已确认", "category": "ups_outage", "severity": "high", "status": "triaged", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "billing-api", "opened_at": "2025-02-10T01:00:00Z", "updated_at": "2025-02-10T02:00:00Z", "description": "UPS event resolved", "tags": ["power", "resolved"]},
        {"incident_id": "inc-007", "title": "网络延迟-可观察", "category": "network_degradation", "severity": "critical", "status": "open", "assigned_team": "network_ops", "ticket_type": "watchlist", "service": "west4-spine-uplink", "opened_at": "2025-02-10T00:00:00Z", "updated_at": "2025-02-10T00:30:00Z", "description": "High latency observed", "tags": ["network"]},
        {"incident_id": "inc-008", "title": "UPS事件-监控中", "category": "ups_outage", "severity": "high", "status": "open", "assigned_team": "power_ops", "ticket_type": "watchlist", "service": "edge-cluster-a12", "opened_at": "2025-02-10T04:00:00Z", "updated_at": "2025-02-10T04:10:00Z", "description": "Monitored UPS event", "tags": ["power"]},
        {"incident_id": "inc-009", "title": "Inference Worker低优先级", "category": "service_down", "severity": "low", "status": "open", "assigned_team": "ml_platform", "ticket_type": "risk_work_order", "service": "inference-worker", "opened_at": "2025-02-10T05:00:00Z", "updated_at": "2025-02-10T05:10:00Z", "description": "Inference worker intermittent failure", "tags": ["ml"]},
        {"incident_id": "inc-010", "title": "Edge Cluster A12 UPS故障", "category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "edge-cluster-a12", "opened_at": "2025-02-10T03:40:00Z", "updated_at": "2025-02-10T03:45:00Z", "description": "UPS failure at edge cluster A12", "tags": ["power", "critical"]}
    ]
    with open("ops/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # --- 干扰：旧备份 ---
    old = [
        {"incident_id": "inc-001", "title": "Old UPS issue", "category": "ups_outage", "severity": "critical", "status": "resolved", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "billing-api", "opened_at": "2025-01-01T00:00:00Z", "updated_at": "2025-01-02T00:00:00Z", "description": "Old", "tags": []}
    ]
    with open("ops/incident_pool_backup.json", "w") as f:
        json.dump({"incidents": old}, f, indent=2)

if __name__ == "__main__":
    build_env()
