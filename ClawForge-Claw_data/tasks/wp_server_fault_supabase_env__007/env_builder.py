import os
import json

def build_env():
    # Create directories
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Lock analysis report
    lock_report = """\
[2025-03-21 03:14:22] PostgreSQL Lock Analysis Report
===========================================
Database: northstar_prod

Top Blocking Queries:
- PID 9876: Transaction TX-20250321-001, running for 45 minutes, holding AccessExclusiveLock on 'billing_api_transactions'.
  Waiting queries: 3 sessions blocked.

Recommendation: Kill transaction TX-20250321-001 immediately to resolve lock contention.
"""
    with open("db_dumps/lock_analysis.txt", "w") as f:
        f.write(lock_report)

    # Incidents pool (5 incidents, only inc-003 matches the lock TX)
    incidents = {
        "incidents": [
            {
                "incident_id": "inc-001",
                "title": "UPS Glitch Transient",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": "2025-03-20T22:10:00Z",
                "updated_at": "2025-03-21T00:05:00Z",
                "description": "UPS glitch caused transient network issue, no lock info.",
                "tags": ["ups", "fleeting"]
            },
            {
                "incident_id": "inc-002",
                "title": "Replication lag on analytics-mirror",
                "category": "db_replica_lag",
                "severity": "high",
                "status": "triaged",
                "assigned_team": "db_ops",
                "ticket_type": "risk_work_order",
                "service": "analytics-mirror",
                "opened_at": "2025-03-20T23:45:00Z",
                "updated_at": "2025-03-21T01:20:00Z",
                "description": "Replication lag due to long TX TX-20250321-002 on source.",
                "tags": ["replication", "lag"]
            },
            {
                "incident_id": "inc-003",
                "title": "Billing API down",
                "category": "service_down",
                "severity": "critical",
                "status": "open",
                "assigned_team": "app_ops",
                "ticket_type": "risk_work_order",
                "service": "billing-api",
                "opened_at": "2025-03-21T02:30:00Z",
                "updated_at": "2025-03-21T03:15:00Z",
                "description": "Billing API down, root cause: long-running transaction TX-20250321-001 holding lock on billing_api_transactions table. Impacting all billing requests.",
                "tags": ["service-down", "lock-contention"]
            },
            {
                "incident_id": "inc-004",
                "title": "West4 spine uplink flapping",
                "category": "network_degradation",
                "severity": "medium",
                "status": "open",
                "assigned_team": "network_ops",
                "ticket_type": "watchlist",
                "service": "west4-spine-uplink",
                "opened_at": "2025-03-20T20:00:00Z",
                "updated_at": "2025-03-20T22:30:00Z",
                "description": "West4 spine uplink flapping, no lock involvement.",
                "tags": ["network", "flapping"]
            },
            {
                "incident_id": "inc-005",
                "title": "Inference worker stalled",
                "category": "service_down",
                "severity": "high",
                "status": "triaged",
                "assigned_team": "ml_platform",
                "ticket_type": "risk_work_order",
                "service": "inference-worker",
                "opened_at": "2025-03-21T01:10:00Z",
                "updated_at": "2025-03-21T02:00:00Z",
                "description": "Inference worker stalled due to deadlock TX-20250321-003.",
                "tags": ["ml", "deadlock"]
            }
        ]
    }
    with open("data/incidents_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

if __name__ == "__main__":
    build_env()
