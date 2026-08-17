import os
import json

def build_env():
    # Core directories
    for d in ("incidents", "attachments", "old_backups", "monitoring", "logs"):
        os.makedirs(d, exist_ok=True)

    # ---- Main incident pool (with distractors) ----
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "UPS failure in west4",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-10T02:15:00Z",
            "updated_at": "2025-04-10T02:30:00Z",
            "description": "Power supply interrupted",
            "tags": ["urgent", "power"]
        },
        {
            "incident_id": "INC-002",
            "title": "DB replica lag spike",
            "category": "db_replica_lag",
            "severity": "high",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-04-09T14:00:00Z",
            "updated_at": "2025-04-09T16:00:00Z",
            "description": "Replica lag exceeding 300s",
            "tags": ["database"]
        },
        {
            "incident_id": "INC-003",
            "title": "Billing API down",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-04-10T03:00:00Z",
            "updated_at": "2025-04-10T03:15:00Z",
            "description": "Service unresponsive",
            "tags": ["critical", "api"]
        },
        {
            "incident_id": "INC-004",
            "title": "Network degradation on edge-cluster",
            "category": "network_degradation",
            "severity": "critical",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-04-08T12:00:00Z",
            "updated_at": "2025-04-08T12:30:00Z",
            "description": "Latency increase",
            "tags": ["network"]
        },
        {
            "incident_id": "INC-005",
            "title": "UPS low battery warning",
            "category": "ups_outage",
            "severity": "medium",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-09T10:00:00Z",
            "updated_at": "2025-04-09T10:10:00Z",
            "description": "Battery capacity below 30%",
            "tags": ["power"]
        },
        {
            "incident_id": "INC-006",
            "title": "Inference worker service down (already triaged)",
            "category": "service_down",
            "severity": "critical",
            "status": "triaged",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-04-07T20:00:00Z",
            "updated_at": "2025-04-07T21:00:00Z",
            "description": "Service crashed",
            "tags": ["ml"]
        },
        #  Distractor: missing category field
        {
            "incident_id": "INC-007",
            "title": "Strange network symptom",
            "severity": "high",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-04-09T22:00:00Z",
            "updated_at": "2025-04-09T23:00:00Z",
            "description": "Intermittent packet loss",
            "tags": ["network"]
        },
        #  Distractor: unknown category
        {
            "incident_id": "INC-008",
            "title": "Unknown issue",
            "category": "unknown",
            "severity": "critical",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-04-08T08:00:00Z",
            "updated_at": "2025-04-08T09:00:00Z",
            "description": "Unspecified",
            "tags": []
        }
    ]
    with open("incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # ---- Attachments index ----
    attachments = [
        {
            "path": "attachments/runbook_ups_and_service.md",
            "title": "UPS and Service Outage Runbook",
            "kind": "runbook",
            "description": "Standard operating procedures for UPS outage and service down incidents."
        }
    ]
    with open("attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---- Actual runbook (source of truth for actions) ----
    runbook_content = """# UPS and Service Outage Runbook

## Overview
This runbook contains procedures for handling UPS power failures and service down events.

### UPS Outage Action
Activate backup generator and notify facilities team.

### Service Down Action
Restart service on the affected host. Verify health after restart.

### Other Information
- Always escalate to NOC if unresponsive.
- Contact Lena Park for power coordination.
"""
    with open("attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # ---- Distractor files ----
    with open("old_backups/incident_pool_backup.json", "w") as f:
        json.dump([{"id": "INC-OLD", "type": "ups_outage", "priority": 1}], f)

    with open("monitoring/fake_metrics.csv", "w") as f:
        f.write("timestamp,cpu,mem\n2025-04-10T00:00:00,85,72\n")

    with open("logs/cpu_usage.log", "w") as f:
        f.write("2025-04-10 02:00:00 HIGH CPU 100%\n")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
