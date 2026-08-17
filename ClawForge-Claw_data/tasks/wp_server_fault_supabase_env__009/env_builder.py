import os
import json

def build_env():
    # ----- Incidents pool -----
    incidents = {
        "incidents": [
            # Target incidents (risk_work_order, category ups_outage or service_down)
            {
                "incident_id": "INC-001",
                "title": "UPS failure in edge-cluster-a12",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": "2025-04-08T01:15:00Z",
                "updated_at": "2025-04-08T01:45:00Z",
                "description": "UPS battery drained, edge nodes power cycling",
                "tags": ["ups", "edge"]
            },
            {
                "incident_id": "INC-003",
                "title": "Service down – billing-api unresponsive",
                "category": "service_down",
                "severity": "high",
                "status": "triaged",
                "assigned_team": "app_ops",
                "ticket_type": "risk_work_order",
                "service": "billing-api",
                "opened_at": "2025-04-08T00:30:00Z",
                "updated_at": "2025-04-08T01:10:00Z",
                "description": "API returns 503 since UPS blip",
                "tags": ["service", "billing"]
            },
            # Distractors: watchlist items (same categories but not risk_work_order)
            {
                "incident_id": "INC-007",
                "title": "UPS test – watchlist only",
                "category": "ups_outage",
                "severity": "medium",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "watchlist",
                "service": "west4-spine-uplink",
                "opened_at": "2025-04-07T22:00:00Z",
                "updated_at": "2025-04-07T22:10:00Z",
                "description": "Scheduled UPS maintenance observation",
                "tags": ["ups", "maintenance"]
            },
            {
                "incident_id": "INC-009",
                "title": "Service degradation watch – inference-worker",
                "category": "service_down",
                "severity": "low",
                "status": "open",
                "assigned_team": "ml_platform",
                "ticket_type": "watchlist",
                "service": "inference-worker",
                "opened_at": "2025-04-07T20:00:00Z",
                "updated_at": "2025-04-07T20:05:00Z",
                "description": "Monitoring only, no action expected",
                "tags": ["service", "inference"]
            },
            # Distractors: other categories with risk_work_order
            {
                "incident_id": "INC-012",
                "title": "DB replica lag on analytics-mirror",
                "category": "db_replica_lag",
                "severity": "high",
                "status": "open",
                "assigned_team": "db_ops",
                "ticket_type": "risk_work_order",
                "service": "analytics-mirror",
                "opened_at": "2025-04-08T00:10:00Z",
                "updated_at": "2025-04-08T00:50:00Z",
                "description": "Replication delay 2 minutes",
                "tags": ["db", "replica"]
            },
            {
                "incident_id": "INC-015",
                "title": "Network degradation west4-spine-uplink",
                "category": "network_degradation",
                "severity": "critical",
                "status": "triaged",
                "assigned_team": "network_ops",
                "ticket_type": "risk_work_order",
                "service": "west4-spine-uplink",
                "opened_at": "2025-04-08T01:00:00Z",
                "updated_at": "2025-04-08T01:30:00Z",
                "description": "Packet loss 15% due to suspected UPS failure",
                "tags": ["network", "ups"]
            }
        ]
    }

    os.makedirs("data/incidents", exist_ok=True)
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

    # ----- Attachments (runbook) -----
    attachments = {
        "attachments": [
            {
                "path": "runbook_ups_and_service.md",
                "title": "UPS and Service Outage Runbook",
                "kind": "runbook",
                "description": "Standard operating procedure for UPS and service outages"
            },
            {
                "path": "supabase_write_contract.md",
                "title": "Simulated Supabase Write Contract",
                "kind": "write_contract",
                "description": "Contract for writing resolution data to Supabase"
            }
        ]
    }
    os.makedirs("data", exist_ok=True)
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # Write the actual runbook file
    runbook_content = (
        "# UPS and Service Outage Runbook\n\n"
        "## Incident Type: ups_outage\n"
        "Action: power_cycle\n"
        "Description: Perform a controlled power cycle of the affected UPS bank.\n\n"
        "## Incident Type: service_down\n"
        "Action: restart_service\n"
        "Description: Restart the primary service process on the affected node.\n\n"
        "## Other types\n"
        "Action: escalate\n"
    )
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # ----- Dry write contract (distractor) -----
    with open("data/attachments/supabase_write_contract.md", "w") as f:
        f.write("# Supabase Write Contract\nNot relevant for this task.\n")

    # ----- Contacts (distractor, not needed for task) -----
    contacts = {
        "contacts": [
            {"contact_id": "c-1", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
            {"contact_id": "c-2", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
            {"contact_id": "c-3", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ----- Accounts (distractor) -----
    accounts = {
        "accounts": [
            {"account_id": "a-001", "display_name": "Nikhil Rao", "department": "NOC", "email": "nikhil.rao@northstar.example.com", "permissions": ["admin", "remediation"], "default_region": "us-west-4", "voice": ["slack", "phone"]},
            {"account_id": "a-002", "display_name": "Lena Park", "department": "Facilities", "email": "lena.park@northstar.example.com", "permissions": ["read", "power"], "default_region": "us-west-4", "voice": ["phone"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ----- Create ops directory (empty, target for agent output) -----
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
