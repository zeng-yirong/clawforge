import os
import json
from datetime import datetime, timezone

def build_env():
    # Ensure base directories
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== Incident Pool ==========
    # 10 incidents, only 2 should pass final filter (ups_outage/service_down, open, risk_work_order, opened_at >= 2025-04-10T00:00:00Z)
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "Main UPS overload in DC-A",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-08T09:15:00Z",   # earlier than threshold
            "updated_at": "2025-04-08T11:00:00Z",
            "description": "Primary UPS voltage drop",
            "tags": ["dc-a", "power"]
        },
        {
            "incident_id": "INC-002",
            "title": "Billing API service down",
            "category": "service_down",
            "severity": "critical",
            "status": "closed",   # wrong status
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-04-12T08:00:00Z",
            "updated_at": "2025-04-12T10:00:00Z",
            "description": "Payment endpoint unresponsive",
            "tags": ["payment", "critical"]
        },
        {
            "incident_id": "INC-003",
            "title": "West4 spine uplink packet loss",
            "category": "network_degradation",  # wrong category
            "severity": "medium",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-09T14:00:00Z",
            "updated_at": "2025-04-09T16:30:00Z",
            "description": "Intermittent drops on west4",
            "tags": ["network", "spine"]
        },
        {
            "incident_id": "INC-004",
            "title": "Secondary UPS battery failure",
            "category": "ups_outage",
            "severity": "high",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",   # wrong ticket_type
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-11T10:00:00Z",
            "updated_at": "2025-04-11T12:00:00Z",
            "description": "Battery pack draining",
            "tags": ["dc-b", "power"]
        },
        {
            "incident_id": "INC-005",
            "title": "Analytics mirror service down",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-04-12T06:30:00Z",
            "updated_at": "2025-04-12T08:00:00Z",
            "description": "Replication lag spike caused outage",
            "tags": ["analytics", "db"]
        },
        {
            "incident_id": "INC-006",
            "title": "Inference worker GPU crash",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-04-10T01:00:00Z",  # exactly at threshold (>= included)
            "updated_at": "2025-04-10T03:00:00Z",
            "description": "GPU node kernel panic",
            "tags": ["ml", "gpu"]
        },
        {
            "incident_id": "INC-007",
            "title": "Main UPS overload in DC-B",
            "category": "ups_outage",
            "severity": "high",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-11T15:00:00Z",
            "updated_at": "2025-04-11T17:00:00Z",
            "description": "Secondary breaker tripped",
            "tags": ["dc-b", "power"]
        },
        {
            "incident_id": "INC-008",
            "title": "West4 spine uplink redundancy test",
            "category": "network_degradation",
            "severity": "low",
            "status": "triaged",   # wrong status
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-13T00:00:00Z",
            "updated_at": "2025-04-13T01:00:00Z",
            "description": "Planned failover test",
            "tags": ["network", "test"]
        },
        {
            "incident_id": "INC-009",
            "title": "Billing API latency spike",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-04-09T23:00:00Z",  # earlier than threshold
            "updated_at": "2025-04-10T01:00:00Z",
            "description": "High latency due to DB lock",
            "tags": ["payment", "db"]
        },
        {
            "incident_id": "INC-010",
            "title": "UPS firmware update rollback",
            "category": "ups_outage",
            "severity": "medium",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-14T08:00:00Z",
            "updated_at": "2025-04-14T09:00:00Z",
            "description": "Firmware patch failure",
            "tags": ["power", "firmware"]
        }
    ]
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # ========== Runbook attachment ==========
    runbook_content = """# UPS and Service Outage Runbook

## Scope
Applies to any incident categorized as `ups_outage` or `service_down` with ticket type `risk_work_order` and status `open`.

## Time Constraint
Only process incidents opened after **2025-04-10T00:00:00Z**. Incidents opened before this date are considered non-critical backlog.

## Remediation Steps
- For UPS outages: contact Facilities Power Coordinator via pager.
- For service-down: escalate to application team with incident ID.

## Notes
Do not modify incidents assigned to `watchlist`.
"""
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # ========== Decoy files (other attachments, contacts, accounts) ==========
    # Contacts (not needed for task, but adds realism)
    contacts = [
        {"contact_id": "C-001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "C-002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "C-003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    accounts = [
        {"account_id": "ACC-001", "display_name": "NorthStar DC-A", "department": "Infrastructure", "email": "dc-a@northstar.example.com", "permissions": ["read", "write"], "default_region": "us-east", "voice": ["ops-channel"]},
        {"account_id": "ACC-002", "display_name": "NorthStar DC-B", "department": "Infrastructure", "email": "dc-b@northstar.example.com", "permissions": ["read"], "default_region": "us-west", "voice": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # Another runbook (decoy)
    decoy_runbook = "# Restore from Snapshot\nSnapshot retention policy: 7 days.\n"
    with open("data/attachments/supabase_write_contract.md", "w") as f:
        f.write(decoy_runbook)

if __name__ == "__main__":
    build_env()
