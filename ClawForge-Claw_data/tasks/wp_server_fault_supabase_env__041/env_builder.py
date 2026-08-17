import os
import json
from datetime import datetime, timezone

def build_env():
    # Ensure necessary directories
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty directory, agent will write into it

    # ---- incident_pool.json (with distractors) ----
    incidents = [
        {
            "incident_id": "incident-001",
            "title": "UPS failure at west4",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-11T03:00:00Z",
            "updated_at": "2025-04-11T03:10:00Z",
            "description": "Main UPS unit offline",
            "tags": ["power", "urgent"]
        },
        {
            "incident_id": "incident-002",
            "title": "billing-api unreachable",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-04-11T03:05:00Z",
            "updated_at": "2025-04-11T03:15:00Z",
            "description": "HTTP 503 from all endpoints",
            "tags": ["service"]
        },
        {
            "incident_id": "incident-003",
            "title": "UPS battery depleted",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-11T02:55:00Z",
            "updated_at": "2025-04-11T03:05:00Z",
            "description": "Battery voltage below threshold",
            "tags": ["power", "urgent"]
        },
        {
            "incident_id": "incident-004",
            "title": "analytics-mirror lag spike",
            "category": "db_replica_lag",
            "severity": "critical",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-04-11T02:45:00Z",
            "updated_at": "2025-04-11T02:50:00Z",
            "description": "Replication lag > 30s",
            "tags": ["database"]
        },
        {
            "incident_id": "incident-005",
            "title": "inference-worker crashed",
            "category": "service_down",
            "severity": "critical",
            "status": "triaged",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-04-11T02:30:00Z",
            "updated_at": "2025-04-11T02:40:00Z",
            "description": "Process exited with OOM",
            "tags": ["ml"]
        },
        {
            "incident_id": "incident-006",
            "title": "edge-cluster-a12 power drop",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-11T03:20:00Z",
            "updated_at": "2025-04-11T03:25:00Z",
            "description": "Voltage sag detected",
            "tags": ["power"]
        }
    ]
    with open("data/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # ---- runbook_ups_and_service.md ----
    runbook_content = """# UPS & Service Outage Runbook

## Priority rules
- Only incidents with severity **critical** or **high** are actionable.
- Within actionable incidents, sort by severity: critical before high.
- For incidents with the same severity, sort by **opened_at** ascending (oldest first).
- Do not include incidents that are not `open` or have a `ticket_type` other than `risk_work_order`.

> This runbook is authoritative for all UPS and service-down escalations.
"""
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # ---- optional distracting file (contacts.json) ----
    contacts = [
        {"contact_id": "c1", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "c2", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "c3", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
