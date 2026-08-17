import os
import json

def build_env():
    # Ensure data/incidents exists
    os.makedirs("data/incidents", exist_ok=True)

    # === Incident pool (main data) ===
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "West4 UPS Battery Low",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-06-10T03:15:00Z",
            "updated_at": "2025-06-10T03:30:00Z",
            "description": "Battery voltage dropped below threshold.",
            "tags": ["ups", "power"]
        },
        {
            "incident_id": "INC-002",
            "title": "Billing API Service Down",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-06-10T03:20:00Z",
            "updated_at": "2025-06-10T03:25:00Z",
            "description": "All requests to billing-api are returning 503.",
            "tags": ["api", "outage"]
        },
        {
            "incident_id": "INC-003",
            "title": "Analytics DB Replica Lag",
            "category": "db_replica_lag",
            "severity": "medium",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "watchlist",
            "service": "analytics-mirror",
            "opened_at": "2025-06-09T22:00:00Z",
            "updated_at": "2025-06-10T01:00:00Z",
            "description": "Replica lag exceeds 5 minutes.",
            "tags": ["db", "lag"]
        },
        {
            "incident_id": "INC-004",
            "title": "Edge Cluster UPS Low Battery",
            "category": "ups_outage",
            "severity": "low",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "edge-cluster-a12",
            "opened_at": "2025-06-08T12:00:00Z",
            "updated_at": "2025-06-08T12:30:00Z",
            "description": "Battery at 70%, not critical.",
            "tags": ["ups", "low-priority"]
        },
        {
            "incident_id": "INC-005",
            "title": "West4 Spine Uplink Degradation",
            "category": "network_degradation",
            "severity": "high",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-06-10T02:00:00Z",
            "updated_at": "2025-06-10T02:10:00Z",
            "description": "Packet loss increased to 5%.",
            "tags": ["network"]
        }
    ]
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # === Attachments metadata ===
    attachments = [
        {
            "path": "data/runbook_ups_and_service.md",
            "title": "UPS and Service Outage Runbook",
            "kind": "runbook",
            "description": "Standard operating procedure for power and service outages."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # === Runbook file (markdown) ===
    runbook_content = """# UPS and Service Outage Runbook

## Scope
Only incidents with the following criteria should be actioned:
- Category: `ups_outage` or `service_down`
- Status: `open`
- Severity: `critical` or `high`

## Procedure
1. For each incident meeting the criteria, change its status to `remediated`.
2. Log the remediation action in the remediation log.
3. Write a resolution record to the Supabase resolution table with `incident_id` and `status: "remediated"`.
"""
    with open("data/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # === Distractors (unrelated files) ===
    accounts = {
        "accounts": [
            {
                "account_id": "acc-001",
                "display_name": "Admin",
                "department": "IT",
                "email": "admin@northstar.example.com",
                "permissions": ["admin"],
                "default_region": "us-west",
                "voice": []
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {
                "contact_id": "cont-001",
                "name": "Harper Zhou",
                "role": "Database Reliability Engineer",
                "email": "harper.zhou@northstar.example.com"
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
