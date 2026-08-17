import os
import json
from datetime import datetime, timedelta

BASE = "."

def build_env():
    # ----- accounts (decoy) -----
    os.makedirs(f"{BASE}/data", exist_ok=True)
    accounts = {
        "accounts": [
            {"account_id": "a1", "display_name": "west4-alerts", "department": "infra", "email": "alerts@northstar.example.com", "permissions": ["read"], "default_region": "west4", "voice": []},
            {"account_id": "a2", "display_name": "ops-bot", "department": "ops", "email": "ops@northstar.example.com", "permissions": ["write"], "default_region": "east1", "voice": []}
        ]
    }
    with open(f"{BASE}/data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ----- contacts (decoy) -----
    contacts = {
        "contacts": [
            {"contact_id": "c1", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
            {"contact_id": "c2", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
            {"contact_id": "c3", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
        ]
    }
    with open(f"{BASE}/data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ----- attachments -----
    os.makedirs(f"{BASE}/data/attachments", exist_ok=True)

    # Correct runbook (the one agent must read)
    runbook_content = """# UPS and Service Outage Runbook

| Category        | Action                           |
|-----------------|----------------------------------|
| ups_outage      | Power cycle the UPS and verify   |
| service_down    | Roll back last deployment        |
| db_replica_lag  | Monitor (no immediate action)    |

**Important**: Always confirm the ticket status before acting.
"""
    with open(f"{BASE}/data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # Decoy (old version)
    old_runbook = """# Old UPS Runbook (deprecated)
| Category   | Action               |
|------------|----------------------|
| ups_outage | Call the electrician |
"""
    with open(f"{BASE}/data/attachments/old_runbook.md", "w") as f:
        f.write(old_runbook)

    # Decoy (unrelated)
    with open(f"{BASE}/data/attachments/service_notes.txt", "w") as f:
        f.write("Misc notes – not the runbook.")

    # ----- incidents -----
    os.makedirs(f"{BASE}/data/incidents", exist_ok=True)
    base_time = datetime(2025, 6, 1, 10, 0, 0)

    incidents = {
        "incidents": [
            {
                "incident_id": "INC-001",
                "title": "West4 UPS battery failure",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": (base_time).isoformat(),
                "updated_at": (base_time + timedelta(minutes=5)).isoformat(),
                "description": "Battery voltage dropped below threshold.",
                "tags": ["power", "west4"]
            },
            {
                "incident_id": "INC-002",
                "title": "billing-api 503 spike",
                "category": "service_down",
                "severity": "high",
                "status": "triaged",
                "assigned_team": "app_ops",
                "ticket_type": "watchlist",
                "service": "billing-api",
                "opened_at": (base_time + timedelta(hours=1)).isoformat(),
                "updated_at": (base_time + timedelta(hours=1, minutes=10)).isoformat(),
                "description": "Service unreachable for 8 minutes.",
                "tags": ["api", "billing"]
            },
            {
                "incident_id": "INC-003",
                "title": "UPS load unbalanced",
                "category": "ups_outage",
                "severity": "high",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "west4-spine-uplink",
                "opened_at": (base_time + timedelta(hours=2)).isoformat(),
                "updated_at": (base_time + timedelta(hours=2, minutes=5)).isoformat(),
                "description": "Phase B over 90%.",
                "tags": ["power"]
            },
            {
                "incident_id": "INC-004",
                "title": "Replica lag analytics-mirror",
                "category": "db_replica_lag",
                "severity": "critical",
                "status": "open",
                "assigned_team": "db_ops",
                "ticket_type": "risk_work_order",
                "service": "analytics-mirror",
                "opened_at": (base_time + timedelta(hours=3)).isoformat(),
                "updated_at": (base_time + timedelta(hours=3, minutes=20)).isoformat(),
                "description": "Lag exceeding 300s.",
                "tags": ["db", "replication"]
            },
            {
                "incident_id": "INC-005",
                "title": "Network degradation west4 spine",
                "category": "network_degradation",
                "severity": "medium",
                "status": "open",
                "assigned_team": "network_ops",
                "ticket_type": "watchlist",
                "service": "west4-spine-uplink",
                "opened_at": (base_time + timedelta(hours=4)).isoformat(),
                "updated_at": (base_time + timedelta(hours=4, minutes=15)).isoformat(),
                "description": "Packet loss 0.5%.",
                "tags": ["network"]
            },
            {
                "incident_id": "INC-006",
                "title": "UPS test routine (closed)",
                "category": "ups_outage",
                "severity": "medium",
                "status": "closed",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": (base_time - timedelta(days=1)).isoformat(),
                "updated_at": (base_time - timedelta(hours=6)).isoformat(),
                "description": "Scheduled test, resolved.",
                "tags": ["power", "test"]
            },
            {
                "incident_id": "INC-007",
                "title": "inference-worker crash loop",
                "category": "service_down",
                "severity": "critical",
                "status": "triaged",
                "assigned_team": "ml_platform",
                "ticket_type": "risk_work_order",
                "service": "inference-worker",
                "opened_at": (base_time + timedelta(hours=5)).isoformat(),
                "updated_at": (base_time + timedelta(hours=5, minutes=3)).isoformat(),
                "description": "Process restarts every 90s.",
                "tags": ["ml", "crash"]
            }
        ]
    }
    with open(f"{BASE}/data/incidents/incident_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

    # ----- ops directory (empty, agent must create file inside) -----
    os.makedirs(f"{BASE}/ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
