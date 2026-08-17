import os
import json
from datetime import datetime

def build_env():
    # Ensure directories exist
    os.makedirs("incidents", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # create empty dir, agent will fill it

    # ---- incident pool ----
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "UPS failure in rack A",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2026-01-14T22:15:00Z",
            "updated_at": "2026-01-14T23:00:00Z",
            "description": "Main UPS unit stopped delivering power to rack A.",
            "tags": ["urgent", "infra"]
        },
        {
            "incident_id": "INC-002",
            "title": "billing-api service down",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2026-01-14T22:20:00Z",
            "updated_at": "2026-01-14T22:45:00Z",
            "description": "500 errors on all billing endpoints.",
            "tags": ["severe"]
        },
        {
            "incident_id": "INC-003",
            "title": "UPS low battery in rack B",
            "category": "ups_outage",
            "severity": "high",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2026-01-14T22:30:00Z",
            "updated_at": "2026-01-14T23:10:00Z",
            "description": "Battery charge dropped below 20%.",
            "tags": ["battery"]
        },
        {
            "incident_id": "INC-004",
            "title": "UPS overload already triaged",
            "category": "ups_outage",
            "severity": "medium",
            "status": "triaged",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2026-01-14T21:00:00Z",
            "updated_at": "2026-01-14T21:30:00Z",
            "description": "Load was high but team already acknowledged.",
            "tags": ["triaged"]
        },
        {
            "incident_id": "INC-005",
            "title": "West4 network degradation",
            "category": "network_degradation",
            "severity": "high",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2026-01-14T22:10:00Z",
            "updated_at": "2026-01-14T22:50:00Z",
            "description": "Packet loss on west4 uplink.",
            "tags": ["latency"]
        }
    ]
    with open("incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # ---- attachments ----
    attachments = [
        {
            "path": "data/runbook_ups_and_service.json",
            "title": "UPS and Service Outage Runbook",
            "kind": "runbook",
            "description": "Runbook defining actions for UPS and service outage categories."
        },
        {
            "path": "data/supabase_write_contract.md",
            "title": "Simulated Supabase Write Contract",
            "kind": "write_contract",
            "description": "Contract schema for writing resolution records to Supabase."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---- runbook (JSON so it's machine‑parseable) ----
    runbook = {
        "runbook": {
            "description": "Actions for UPS and service outage scenarios.",
            "action_mapping": {
                "ups_outage": {
                    "critical": "power_cycle_ups",
                    "high": "transfer_to_backup",
                    "medium": "monitor_only"
                },
                "service_down": {
                    "critical": "restart_service",
                    "high": "isolate_node"
                }
            }
        }
    }
    with open("data/runbook_ups_and_service.json", "w") as f:
        json.dump(runbook, f, indent=2)

    # ---- decoy contacts (not used in this task) ----
    contacts = [
        {"contact_id": "ct-001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "ct-002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "ct-003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
