import os
import json

def build_env():
    # Ensure base directories exist
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # --- incident_pool.json (main challenge) ---
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "Billing API down - 502 errors",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-07-15T03:12:00Z",
            "updated_at": "2025-07-15T03:15:00Z",
            "description": "Billing API returning 502, affecting all payment flows.",
            "tags": ["production", "urgent"]
        },
        {
            "incident_id": "INC-002",
            "title": "Edge cluster A12 unreachable",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-07-15T03:20:00Z",
            "updated_at": "2025-07-15T03:22:00Z",
            "description": "Edge cluster A12 not responding to health checks.",
            "tags": ["production", "edge"]
        },
        {
            "incident_id": "INC-003",
            "title": "UPS battery failure in DC-West",
            "category": "ups_outage",
            "severity": "high",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-07-15T02:45:00Z",
            "updated_at": "2025-07-15T03:00:00Z",
            "description": "UPS unit 4 battery replaced, monitoring.",
            "tags": ["infrastructure", "watch"]
        },
        {
            "incident_id": "INC-004",
            "title": "Inference worker degraded (already triaged)",
            "category": "service_down",
            "severity": "high",
            "status": "triaged",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-07-14T22:10:00Z",
            "updated_at": "2025-07-15T01:00:00Z",
            "description": "Inference worker node sporadic errors, team already patching.",
            "tags": ["ml", "triaged"]
        },
        {
            "incident_id": "INC-005",
            "title": "Network degradation on west4 spine",
            "category": "network_degradation",
            "severity": "medium",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-07-15T01:30:00Z",
            "updated_at": "2025-07-15T02:00:00Z",
            "description": "Spine uplink packet loss ~2%, under investigation.",
            "tags": ["network", "watch"]
        }
    ]
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"wrapper": "incidents", "incidents": incidents}, f, indent=2)

    # --- attachments.json ---
    attachments = [
        {
            "path": "runbook_ups_and_service.md",
            "title": "UPS and Service Outage Runbook",
            "kind": "runbook",
            "description": "Standard procedure for service-down incidents."
        },
        {
            "path": "supabase_write_contract.md",
            "kind": "write_contract",
            "title": "Simulated Supabase Write Contract",
            "description": "Contract for writing resolution records to the simulated Supabase table."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"wrapper": "attachments", "attachments": attachments}, f, indent=2)

    # --- contacts.json (distraction) ---
    contacts = [
        {"contact_id": "CT-01", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "CT-02", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "CT-03", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"wrapper": "contacts", "contacts": contacts}, f, indent=2)

    # --- accounts.json (distraction) ---
    accounts = [
        {"account_id": "ACC-01", "display_name": "Billing System", "department": "app_ops", "email": "billing@northstar.example.com", "permissions": ["read", "write"], "default_region": "us-east-1", "voice": ["text"]},
        {"account_id": "ACC-02", "display_name": "Edge Admin", "department": "infra", "email": "edge@northstar.example.com", "permissions": ["read", "write", "admin"], "default_region": "eu-west-1", "voice": ["text", "call"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"wrapper": "accounts", "accounts": accounts}, f, indent=2)

    # --- runbook file (the actual runbook content) ---
    runbook_content = """# UPS and Service Outage Runbook

## Immediate steps for service-down incidents

1. restart-service
2. verify-health
3. notify-oncall
"""
    with open("runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # --- write contract (distraction artifact) ---
    contract_content = """# Simulated Supabase Write Contract

This document describes the expected schema for writing resolution records.
It is not relevant to the current triage task.
"""
    with open("supabase_write_contract.md", "w") as f:
        f.write(contract_content)

if __name__ == "__main__":
    build_env()
