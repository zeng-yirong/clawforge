import os
import json
import random

def build_env():
    # Ensure required directories
    for d in ['incidents', 'attachments', 'contacts', 'accounts', 'ops']:
        os.makedirs(d, exist_ok=True)

    # -------------------- incident pool (10 records) --------------------
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "West Rack UPS Output Failure",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-03-19T02:03:00Z",
            "updated_at": "2025-03-19T02:03:00Z",
            "description": "UPS output voltage dropped to 0V, entire rack A12 powered off.",
            "tags": ["emergency", "power"]
        },
        {
            "incident_id": "INC-002",
            "title": "Billing API Unreachable After Power Event",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-03-19T02:07:00Z",
            "updated_at": "2025-03-19T02:07:00Z",
            "description": "All billing-api pods CrashLoopBackOff likely due to dependent DB cold start.",
            "tags": ["down", "critical"]
        },
        {
            "incident_id": "INC-003",
            "title": "UPS Battery Aging Alert",
            "category": "ups_outage",
            "severity": "medium",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-18T14:30:00Z",
            "updated_at": "2025-03-18T14:30:00Z",
            "description": "Battery impedance exceeds threshold, no immediate outage.",
            "tags": ["preventive"]
        },
        {
            "incident_id": "INC-004",
            "title": "East Zone UPS Self-Test Failure",
            "category": "ups_outage",
            "severity": "critical",
            "status": "triaged",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-03-18T23:00:00Z",
            "updated_at": "2025-03-19T01:00:00Z",
            "description": "Self-test failed but load still on battery; team already investigating.",
            "tags": ["investigating"]
        },
        {
            "incident_id": "INC-005",
            "title": "Inference Worker Pods Crashing",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-03-19T01:50:00Z",
            "updated_at": "2025-03-19T01:50:00Z",
            "description": "OOM errors not related to power event.",
            "tags": ["memory"]
        },
        {
            "incident_id": "INC-006",
            "title": "Replica Lag on Analytics Mirror",
            "category": "db_replica_lag",
            "severity": "critical",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-03-19T00:30:00Z",
            "updated_at": "2025-03-19T00:30:00Z",
            "description": "Slave behind by 12 minutes, no link to UPS event.",
            "tags": ["lag"]
        },
        {
            "incident_id": "INC-007",
            "title": "West4 Spine Uplink Degraded",
            "category": "network_degradation",
            "severity": "high",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-19T01:10:00Z",
            "updated_at": "2025-03-19T01:10:00Z",
            "description": "Packet loss 3% on link, not correlated with power.",
            "tags": ["network"]
        },
        {
            "incident_id": "INC-008",
            "title": "Legacy UPS Breaker Trip (Resolved)",
            "category": "ups_outage",
            "severity": "critical",
            "status": "triaged",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "edge-cluster-a12",
            "opened_at": "2025-03-17T08:00:00Z",
            "updated_at": "2025-03-17T10:00:00Z",
            "description": "Breaker tripped, already bypassed yesterday.",
            "tags": ["resolved"]
        },
        {
            "incident_id": "INC-009",
            "title": "DB Connection Pool Exhaustion",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "watchlist",
            "service": "analytics-mirror",
            "opened_at": "2025-03-19T02:15:00Z",
            "updated_at": "2025-03-19T02:15:00Z",
            "description": "Connection pool spikes, not confirmed as service_down in ticket_type.",
            "tags": ["db"]
        },
        {
            "incident_id": "INC-010",
            "title": "Billing API Database Lag",
            "category": "db_replica_lag",
            "severity": "medium",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-03-19T02:00:00Z",
            "updated_at": "2025-03-19T02:00:00Z",
            "description": "Minor lag 30s, no impact.",
            "tags": ["lag"]
        }
    ]
    # Shuffle to avoid ordering hints
    random.shuffle(incidents)
    with open("incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # -------------------- attachments (runbook) --------------------
    runbook_content = """# UPS and Service Outage Runbook

## Critical thresholds
- UPS offline > 5 minutes → immediate switch to generator.
- Service down > 2 minutes → failover to DR site.

## Steps
1. Confirm UPS status via power_ops.
2. If service_down: restart pods in order: billing-api → inference-worker.
3. Log all actions to ops/resolution_audit.json.
"""
    with open("attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # -------------------- extra background files (distractors) --------------------
    contacts = [
        {"contact_id": "C-001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
        {"contact_id": "C-002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
        {"contact_id": "C-003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
    ]
    with open("contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    accounts = [
        {"account_id": "ACC-001", "display_name": "NorthStar Prod", "department": "Platform", "email": "ops@northstar.example.com", "permissions": ["admin"], "default_region": "us-east", "voice": ["sre"]},
        {"account_id": "ACC-002", "display_name": "NorthStar Staging", "department": "Dev", "email": "dev@northstar.example.com", "permissions": ["read"], "default_region": "us-west", "voice": []}
    ]
    with open("accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ensure ops directory is empty for agent output
    pass  # ops dir already created

if __name__ == "__main__":
    build_env()
