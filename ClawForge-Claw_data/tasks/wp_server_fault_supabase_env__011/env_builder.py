import os
import json

def build_env():
    # Ensure base directories exist
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # === accounts.json ===
    accounts = {
        "accounts": [
            {
                "account_id": "acc-001",
                "display_name": "Nikhil Rao",
                "department": "NOC",
                "email": "nikhil.rao@northstar.example.com",
                "permissions": ["read", "write", "admin"],
                "default_region": "us-east-1",
                "voice": ["en-US"]
            },
            {
                "account_id": "acc-002",
                "display_name": "Lena Park",
                "department": "Facilities",
                "email": "lena.park@northstar.example.com",
                "permissions": ["read"],
                "default_region": "us-west-2",
                "voice": ["en-US"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # === contacts.json ===
    contacts = {
        "contacts": [
            {
                "contact_id": "con-001",
                "name": "Nikhil Rao",
                "role": "NOC Lead",
                "email": "nikhil.rao@northstar.example.com"
            },
            {
                "contact_id": "con-002",
                "name": "Harper Zhou",
                "role": "Database Reliability Engineer",
                "email": "harper.zhou@northstar.example.com"
            },
            {
                "contact_id": "con-003",
                "name": "Lena Park",
                "role": "Facilities Power Coordinator",
                "email": "lena.park@northstar.example.com"
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # === attachments.json ===
    attachments = {
        "attachments": [
            {
                "path": "runbook_ups_and_service.md",
                "title": "UPS and Service Outage Runbook",
                "kind": "runbook",
                "description": "Runbook for UPS failure recovery"
            },
            {
                "path": "supabase_write_contract.md",
                "title": "Simulated Supabase Write Contract",
                "kind": "write_contract",
                "description": "Contract for writing resolutions to Supabase"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # === runbook_ups_and_service.md ===
    runbook_content = """# UPS and Service Outage Runbook

## Step 1: Screen incidents
Filter incidents from `data/incidents/incident_pool.json` where:
- category == "ups_outage"
- severity == "critical"
- status == "open"
- tags does NOT contain "false_alarm"
- service in ["inference-worker", "edge-cluster-a12"]

## Step 2: For each screened incident, prepare a remediation target.
Create a JSON object for each incident with these fields:
- incident_id
- title
- category
- severity
- status
- assigned_team
- service
- remediation_action: must be exactly "initiate_ups_failover"

Collect all objects into an array and write to `ops/remediation_targets.json`.

## Step 3: Write audit trail
For each target incident, create an audit log entry with:
- timestamp: read from `ops/current_timestamp.txt` (strip whitespace)
- user: the email of contact "Nikhil Rao" from data/contacts.json
- action: "remediate_and_write"
- target: incident_id

Write the array to `ops/audit_trail.json`.
"""
    with open("data/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # === supabase_write_contract.md (distractor) ===
    contract_content = "# Simulated Supabase Write Contract\n\nThis contract defines the schema for writing resolution data to the Supabase table. It is not needed for this task."
    with open("data/supabase_write_contract.md", "w") as f:
        f.write(contract_content)

    # === incident_pool.json ===
    incidents = {
        "incidents": [
            {
                "incident_id": "INC-001",
                "title": "UPS fault on west4-spine-uplink",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "network_ops",
                "ticket_type": "risk_work_order",
                "service": "west4-spine-uplink",
                "opened_at": "2025-04-10T22:00:00Z",
                "updated_at": "2025-04-11T01:00:00Z",
                "description": "UPS alarm on network spine uplink",
                "tags": []
            },
            {
                "incident_id": "INC-002",
                "title": "Inference worker pod crash due to UPS failure",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "ml_platform",
                "ticket_type": "risk_work_order",
                "service": "inference-worker",
                "opened_at": "2025-04-10T23:30:00Z",
                "updated_at": "2025-04-11T02:15:00Z",
                "description": "All inference workers lost power, pods in CrashLoopBackOff",
                "tags": ["production"]
            },
            {
                "incident_id": "INC-003",
                "title": "UPS battery low on edge-cluster",
                "category": "ups_outage",
                "severity": "high",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "watchlist",
                "service": "edge-cluster-a12",
                "opened_at": "2025-04-11T00:00:00Z",
                "updated_at": "2025-04-11T01:30:00Z",
                "description": "Battery charge below 30%, not critical yet",
                "tags": []
            },
            {
                "incident_id": "INC-004",
                "title": "Database replica lag spike",
                "category": "db_replica_lag",
                "severity": "critical",
                "status": "open",
                "assigned_team": "db_ops",
                "ticket_type": "risk_work_order",
                "service": "analytics-mirror",
                "opened_at": "2025-04-11T00:15:00Z",
                "updated_at": "2025-04-11T03:00:00Z",
                "description": "Replica lag > 120s on analytics mirror",
                "tags": []
            },
            {
                "incident_id": "INC-005",
                "title": "Edge cluster A12 down after UPS outage",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "app_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": "2025-04-10T23:45:00Z",
                "updated_at": "2025-04-11T02:30:00Z",
                "description": "Entire edge cluster unreachable, UPS failed over but service not restored",
                "tags": ["production"]
            },
            {
                "incident_id": "INC-006",
                "title": "UPS maintenance window mismatch",
                "category": "ups_outage",
                "severity": "critical",
                "status": "triaged",
                "assigned_team": "power_ops",
                "ticket_type": "watchlist",
                "service": "inference-worker",
                "opened_at": "2025-04-10T20:00:00Z",
                "updated_at": "2025-04-10T22:00:00Z",
                "description": "Scheduled maintenance overlapped with peak hours",
                "tags": []
            },
            {
                "incident_id": "INC-007",
                "title": "False alarm: UPS sensor glitch",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "watchlist",
                "service": "inference-worker",
                "opened_at": "2025-04-11T01:00:00Z",
                "updated_at": "2025-04-11T01:10:00Z",
                "description": "Sensor reported voltage dip but no actual outage",
                "tags": ["false_alarm"]
            },
            {
                "incident_id": "INC-008",
                "title": "Billing API latency degradation",
                "category": "service_down",
                "severity": "critical",
                "status": "open",
                "assigned_team": "app_ops",
                "ticket_type": "risk_work_order",
                "service": "billing-api",
                "opened_at": "2025-04-11T02:00:00Z",
                "updated_at": "2025-04-11T03:00:00Z",
                "description": "P99 latency > 5s, unrelated to power events",
                "tags": []
            }
        ]
    }
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

    # === current_timestamp.txt ===
    with open("ops/current_timestamp.txt", "w") as f:
        f.write("2025-04-11T03:15:00Z\n")

if __name__ == "__main__":
    build_env()
