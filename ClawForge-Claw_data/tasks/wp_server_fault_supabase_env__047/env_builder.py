import os
import json

def build_env():
    # Create directories
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Main incident pool
    incidents = [
        {"incident_id": "INC-2025-001", "title": "UPS failure in west4", "category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2025-03-10T08:30:00Z", "updated_at": "2025-03-10T09:00:00Z", "description": "UPS unit A tripped.", "tags": ["power"]},
        {"incident_id": "INC-2025-002", "title": "Network degradation on edge", "category": "network_degradation", "severity": "high", "status": "open", "assigned_team": "network_ops", "ticket_type": "watchlist", "service": "edge-cluster-a12", "opened_at": "2025-03-10T10:00:00Z", "updated_at": "2025-03-10T10:30:00Z", "description": "Latency spike.", "tags": ["network"]},
        {"incident_id": "INC-2025-003", "title": "Billing API down", "category": "service_down", "severity": "critical", "status": "open", "assigned_team": "app_ops", "ticket_type": "risk_work_order", "service": "billing-api", "opened_at": "2025-03-10T08:45:00Z", "updated_at": "2025-03-10T09:15:00Z", "description": "Service unreachable.", "tags": ["api"]},
        {"incident_id": "INC-2025-004", "title": "DB replica lag", "category": "db_replica_lag", "severity": "medium", "status": "triaged", "assigned_team": "db_ops", "ticket_type": "watchlist", "service": "analytics-mirror", "opened_at": "2025-03-10T07:00:00Z", "updated_at": "2025-03-10T07:30:00Z", "description": "Replica lag 500ms.", "tags": ["db"]},
        {"incident_id": "INC-2025-005", "title": "UPS outage in data center B", "category": "ups_outage", "severity": "critical", "status": "open", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2025-03-10T11:00:00Z", "updated_at": "2025-03-10T11:20:00Z", "description": "Backup UPS failed.", "tags": ["power"]},
        {"incident_id": "INC-2025-006", "title": "Old UPS outage resolved", "category": "ups_outage", "severity": "high", "status": "closed", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2025-03-09T14:00:00Z", "updated_at": "2025-03-09T16:00:00Z", "description": "Resolved yesterday.", "tags": ["power"]},
        {"incident_id": "INC-2025-007", "title": "Service down on inference", "category": "service_down", "severity": "high", "status": "triaged", "assigned_team": "ml_platform", "ticket_type": "watchlist", "service": "inference-worker", "opened_at": "2025-03-10T09:30:00Z", "updated_at": "2025-03-10T10:00:00Z", "description": "Inference worker offline.", "tags": ["ml"]}
    ]
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f)

    # Distractor: old archive (all closed)
    os.makedirs("data/incidents/archive", exist_ok=True)
    old_incidents = [
        {"incident_id": "INC-2024-001", "title": "UPS outage legacy", "category": "ups_outage", "severity": "medium", "status": "closed", "assigned_team": "power_ops", "ticket_type": "risk_work_order", "service": "west4-spine-uplink", "opened_at": "2024-12-01T00:00:00Z", "updated_at": "2024-12-02T00:00:00Z", "description": "Old", "tags": []}
    ]
    with open("data/incidents/archive/incident_pool_2024.json", "w") as f:
        json.dump({"incidents": old_incidents}, f)

    # Distractor: corrupt JSON
    with open("data/incidents/corrupt.json", "w") as f:
        f.write("{incidents: [")

    # Runbook
    runbook_content = """# UPS and Service Outage Runbook

## Remediation Steps for Active Outages

1. If the incident category is ups_outage:
   - Action: notify_facilities_and_activate_generator
2. If the incident category is service_down:
   - Action: restart_service_and_notify_team
"""
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # Decorative data
    accounts = [
        {"account_id": "acc-01", "display_name": "Nikhil Rao", "department": "NOC", "email": "nikhil.rao@northstar.example.com", "permissions": ["admin"], "default_region": "west4", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    contacts = [
        {"contact_id": "c-01", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build_env()
