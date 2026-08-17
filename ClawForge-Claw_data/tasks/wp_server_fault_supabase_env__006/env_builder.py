import os
import json

def build_env():
    # incidents pool with 8 incidents
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "billing-api service down after UPS fault",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-03-20T03:18:00Z",
            "updated_at": "2025-03-20T03:18:00Z",
            "description": "Billing API completely unreachable",
            "tags": ["service_down", "urgent"]
        },
        {
            "incident_id": "INC-002",
            "title": "edge-cluster-a12 high latency",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "watchlist",
            "service": "edge-cluster-a12",
            "opened_at": "2025-03-20T03:25:00Z",
            "updated_at": "2025-03-20T03:25:00Z",
            "description": "Latency spike but still serving",
            "tags": ["network", "degradation"]
        },
        {
            "incident_id": "INC-003",
            "title": "inference-worker offline",
            "category": "service_down",
            "severity": "critical",
            "status": "triaged",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-03-20T03:20:00Z",
            "updated_at": "2025-03-20T03:45:00Z",
            "description": "Inference worker node crashed and cannot restart",
            "tags": ["service_down", "ml"]
        },
        {
            "incident_id": "INC-004",
            "title": "west4-spine-uplink packet loss",
            "category": "db_replica_lag",
            "severity": "critical",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-20T02:55:00Z",
            "updated_at": "2025-03-20T03:15:00Z",
            "description": "Replication lag critical due to network issue",
            "tags": ["db", "replication"]
        },
        {
            "incident_id": "INC-005",
            "title": "analytics-mirror unreachable",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-03-20T03:22:00Z",
            "updated_at": "2025-03-20T03:22:00Z",
            "description": "Analytics mirror down, no sync",
            "tags": ["service_down", "analytics"]
        },
        {
            "incident_id": "INC-006",
            "title": "billing-api resumed (closed)",
            "category": "service_down",
            "severity": "critical",
            "status": "closed",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-03-20T03:18:00Z",
            "updated_at": "2025-03-20T05:00:00Z",
            "description": "Auto-recovered after UPS switchover",
            "tags": ["service_down", "resolved"]
        },
        {
            "incident_id": "INC-007",
            "title": "UPS battery test",
            "category": "ups_outage",
            "severity": "medium",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-20T01:00:00Z",
            "updated_at": "2025-03-20T01:30:00Z",
            "description": "Scheduled battery test, no impact",
            "tags": ["ups", "maintenance"]
        },
        {
            "incident_id": "INC-008",
            "title": "edge-cluster-a12 partial outage",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-03-20T03:30:00Z",
            "updated_at": "2025-03-20T03:30:00Z",
            "description": "50% pods crashed, services degraded",
            "tags": ["service_down", "edge"]
        }
    ]

    # Create directories
    os.makedirs("incidents", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty initially, agent should create file here
    os.makedirs("data", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)

    # Write incident pool
    with open("incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # Distractor files
    accounts = [
        {"account_id": "a001", "display_name": "Harper Zhou", "department": "DBRE", "email": "harper.zhou@northstar.example.com", "permissions": ["root"], "default_region": "us-west4", "voice": ["en"]},
        {"account_id": "a002", "display_name": "Lena Park", "department": "Facilities", "email": "lena.park@northstar.example.com", "permissions": ["power"], "default_region": "us-west4", "voice": ["ko"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "c002", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Distractor attachment (runbook, not needed for task)
    runbook_content = """# UPS and Service Outage Runbook

## Step 1: Identify critical service_down incidents with severity critical and status != closed.
## Step 2: Escalate to NOC.
"""
    with open("attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

if __name__ == "__main__":
    build_env()
