import os
import json

def build_env():
    # Create data directories
    os.makedirs("data/incidents", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # Incident pool (10 incidents, 2 correct targets)
    incidents = [
        {
            "incident_id": "INC-001",
            "title": "West4 UPS Failure",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-15T02:30:00Z",
            "updated_at": "2025-03-15T02:45:00Z",
            "description": "Main UPS in West4 data center critical failure.",
            "tags": ["urgent", "west4"]
        },
        {
            "incident_id": "INC-002",
            "title": "North DC UPS Fluctuation",
            "category": "ups_outage",
            "severity": "high",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "edge-cluster-a12",
            "opened_at": "2025-03-15T01:00:00Z",
            "updated_at": "2025-03-15T01:10:00Z",
            "description": "Fluctuating UPS input voltage in north DC.",
            "tags": ["monitoring"]
        },
        {
            "incident_id": "INC-003",
            "title": "Billing API Service Down",
            "category": "service_down",
            "severity": "critical",
            "status": "open",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "billing-api",
            "opened_at": "2025-03-15T03:00:00Z",
            "updated_at": "2025-03-15T03:05:00Z",
            "description": "Billing API unresponsive, 5xx errors.",
            "tags": ["outage", "billing"]
        },
        {
            "incident_id": "INC-004",
            "title": "DB Replica Lag Analytics",
            "category": "db_replica_lag",
            "severity": "high",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-03-15T00:00:00Z",
            "updated_at": "2025-03-15T00:20:00Z",
            "description": "Replica lag > 30 minutes on analytics mirror.",
            "tags": ["performance"]
        },
        {
            "incident_id": "INC-005",
            "title": "Network Degradation West4 Spine",
            "category": "network_degradation",
            "severity": "medium",
            "status": "triaged",
            "assigned_team": "network_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-14T23:00:00Z",
            "updated_at": "2025-03-14T23:30:00Z",
            "description": "Intermittent packet loss on west4 spine uplink.",
            "tags": ["latency"]
        },
        {
            "incident_id": "INC-006",
            "title": "UPS Generator Test",
            "category": "ups_outage",
            "severity": "high",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-15T02:00:00Z",
            "updated_at": "2025-03-15T02:10:00Z",
            "description": "Scheduled UPS generator test.",
            "tags": ["test"]
        },
        {
            "incident_id": "INC-007",
            "title": "Inference Worker Degradation",
            "category": "service_down",
            "severity": "high",
            "status": "open",
            "assigned_team": "ml_platform",
            "ticket_type": "risk_work_order",
            "service": "inference-worker",
            "opened_at": "2025-03-15T02:20:00Z",
            "updated_at": "2025-03-15T02:25:00Z",
            "description": "Inference latency spiking, partial service down.",
            "tags": ["degraded"]
        },
        {
            "incident_id": "INC-008",
            "title": "Watchlist: UPS Precheck",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-15T00:30:00Z",
            "updated_at": "2025-03-15T00:35:00Z",
            "description": "Routine UPS precheck, no immediate issue.",
            "tags": ["watchlist"]
        },
        {
            "incident_id": "INC-009",
            "title": "Service Down: Edge Cluster",
            "category": "service_down",
            "severity": "high",
            "status": "triaged",
            "assigned_team": "app_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-03-14T22:00:00Z",
            "updated_at": "2025-03-14T22:10:00Z",
            "description": "Edge cluster service degraded, already triaged.",
            "tags": ["degraded"]
        },
        {
            "incident_id": "INC-010",
            "title": "UPS Overload Alert",
            "category": "ups_outage",
            "severity": "critical",
            "status": "triaged",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-15T01:50:00Z",
            "updated_at": "2025-03-15T02:00:00Z",
            "description": "UPS overload alert, already triaged.",
            "tags": ["triaged"]
        }
    ]

    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump({"incidents": incidents}, f, indent=2)

    # Runbook file
    runbook_content = """# UPS and Service Outage Runbook

## Remediation Actions

| Category | Severity | Action |
|----------|----------|--------|
| ups_outage | critical | Shutdown main power feed |
| service_down | critical | Restart service via failover |
| ups_outage | high | Monitor and notify |
| service_down | high | Call on-call team |
"""
    with open("data/attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

if __name__ == "__main__":
    build_env()
