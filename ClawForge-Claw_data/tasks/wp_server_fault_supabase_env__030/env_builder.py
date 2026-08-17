import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # --- incident_pool.json ---
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "west4-spine uplink degraded",
            "category": "network_degradation",
            "severity": "high",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-07T02:15:00Z",
            "updated_at": "2025-04-07T02:15:00Z",
            "description": "Packet loss on west4 core",
            "tags": ["network", "spine"]
        },
        {
            "incident_id": "INC-002",
            "title": "billing-api replica lag",
            "category": "db_replica_lag",
            "severity": "medium",
            "status": "triaged",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-04-07T03:00:00Z",
            "updated_at": "2025-04-07T03:30:00Z",
            "description": "Replication delay >5min",
            "tags": ["database", "replica"]
        },
        {
            "incident_id": "INC-003",
            "title": "UPS fault at edge-cluster-a12",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-07T01:00:00Z",
            "updated_at": "2025-04-07T01:10:00Z",
            "description": "UPS battery depleted, cluster offline",
            "tags": ["power", "ups", "watchlist"]
        },
        {
            "incident_id": "INC-004",
            "title": "inference-worker service down",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-04-07T01:05:00Z",
            "updated_at": "2025-04-07T01:15:00Z",
            "description": "Inference worker unreachable after UPS event",
            "tags": ["ml", "outage"]
        },
        {
            "incident_id": "INC-005",
            "title": "UPS failure analytics-mirror",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-04-07T00:50:00Z",
            "updated_at": "2025-04-07T01:20:00Z",
            "description": "UPS tripped, mirror lost power",
            "tags": ["power", "ups", "risk"]
        },
        {
            "incident_id": "INC-006",
            "title": "edge-cluster-a12 backup generator test",
            "category": "ups_outage",
            "severity": "medium",
            "status": "triaged",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-06T10:00:00Z",
            "updated_at": "2025-04-06T12:00:00Z",
            "description": "Generator test, no real outage",
            "tags": ["test", "power"]
        },
        {
            "incident_id": "INC-007",
            "title": "Main UPS failure – all edge services impacted",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-07T00:30:00Z",
            "updated_at": "2025-04-07T01:30:00Z",
            "description": "Primary UPS failed, entire edge cluster down. Runbook attached.",
            "tags": ["power", "ups", "critical", "runbook"]
        }
    ]
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # --- attachments.json ---
    attachments = [
        {
            "path": "data/attachments/runbook_ups_and_service.md",
            "title": "UPS and Service Outage Runbook",
            "kind": "runbook",
            "description": "Step-by-step recovery for UPS-related service outages."
        },
        {
            "path": "data/attachments/supabase_write_contract.md",
            "title": "Simulated Supabase Write Contract",
            "kind": "write_contract",
            "description": "Schema and behavior contract for Supabase writes."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # --- attachment files ---
    # runbook with the hidden transaction ID
    runbook_content = """# UPS and Service Outage Runbook

## Step 1: Identify the hanging transaction
Check `pg_stat_activity` for queries blocked by the UPS-induced lock storm.

## Step 2: Kill the transaction
The problematic transaction ID is: `tx_ab12cd34`
Use `SELECT pg_terminate_backend(<pid>)` after mapping the ID.

## Step 3: Restart services
Restart the edge cluster services once the lock is cleared.
"""
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # write contract (decoy, no transaction ID)
    contract_content = """# Simulated Supabase Write Contract

This document defines the expected behavior of write operations to Supabase tables.

- Table: `incident_resolutions`
- Required fields: incident_id, resolved_by, resolution_time
- No transaction IDs are referenced here.
"""
    with open("data/attachments/supabase_write_contract.md", "w") as f:
        f.write(contract_content)

    # --- optional decoy contacts (not used in task but adds realism) ---
    os.makedirs("data/contacts", exist_ok=True)
    contacts = [
        {"contact_id": "C001", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"},
        {"contact_id": "C002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "C003", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"}
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
