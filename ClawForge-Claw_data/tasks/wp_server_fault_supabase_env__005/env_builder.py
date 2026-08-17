import os
import json
import csv

def build_env():
    # ---------- data/incidents/incident_pool.json ----------
    incidents = {
        "incidents": [
            {
                "incident_id": "INC-001",
                "title": "West4 Spine Uplink Packet Loss",
                "category": "network_degradation",
                "severity": "high",
                "status": "open",
                "assigned_team": "network_ops",
                "ticket_type": "risk_work_order",
                "service": "west4-spine-uplink",
                "opened_at": "2026-04-01T02:30:00Z",
                "updated_at": "2026-04-01T02:45:00Z",
                "description": "Link flapping detected. No runbook referenced.",
                "tags": ["network", "flapping"]
            },
            {
                "incident_id": "INC-002",
                "title": "UPS Battery Low in DC-7",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": "2026-04-01T02:50:00Z",
                "updated_at": "2026-04-01T03:00:00Z",
                "description": "Battery voltage dropping. Refer to runbooks/ups_outage_runbook.md for manual steps.",
                "tags": ["power", "ups"]
            },
            {
                "incident_id": "INC-003",
                "title": "Primary DB IO Spike",
                "category": "db_replica_lag",
                "severity": "critical",
                "status": "open",
                "assigned_team": "db_ops",
                "ticket_type": "risk_work_order",
                "service": "billing-api",
                "opened_at": "2026-04-01T03:00:00Z",
                "updated_at": "2026-04-01T03:10:00Z",
                "description": "Primary database CPU at 100%, IO wait 80%. Likely long-running transaction. Check runbook at runbooks/manage_long_txns.md for steps to resolve.",
                "tags": ["database", "performance", "blocking"]
            },
            {
                "incident_id": "INC-004",
                "title": "Analytics Mirror Lag",
                "category": "db_replica_lag",
                "severity": "medium",
                "status": "triaged",
                "assigned_team": "app_ops",
                "ticket_type": "watchlist",
                "service": "analytics-mirror",
                "opened_at": "2026-03-31T22:00:00Z",
                "updated_at": "2026-04-01T00:00:00Z",
                "description": "Replica lag 30s. No runbook mentioned.",
                "tags": ["database", "replication"]
            },
            {
                "incident_id": "INC-005",
                "title": "Billing API Latency Spike",
                "category": "service_down",
                "severity": "high",
                "status": "open",
                "assigned_team": "app_ops",
                "ticket_type": "risk_work_order",
                "service": "billing-api",
                "opened_at": "2026-04-01T03:05:00Z",
                "updated_at": "2026-04-01T03:12:00Z",
                "description": "P99 latency > 2s. Refer to runbooks/manage_long_txns.md for possible cause.",
                "tags": ["api", "latency"]
            }
        ]
    }
    os.makedirs("data/incidents", exist_ok=True)
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

    # ---------- data/attachments.json ----------
    attachments = {
        "attachments": [
            {
                "path": "runbooks/manage_long_txns.md",
                "title": "Simulated Supabase Write Contract",
                "kind": "runbook",
                "description": "Steps to identify and kill long-running transactions"
            },
            {
                "path": "runbooks/ups_outage_runbook.md",
                "title": "UPS and Service Outage Runbook",
                "kind": "runbook",
                "description": "Procedures for UPS failure recovery"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ---------- runbooks ----------
    os.makedirs("runbooks", exist_ok=True)
    manage_txn_content = """# Managing Long-Running Transactions

## Prerequisites
- Active transaction snapshot file: `logs/active_transactions.csv`

## Steps
1. Read the file `logs/active_transactions.csv`.
2. Filter rows where `duration_seconds` > 30 and `state` == "active".
3. Collect the `txn_id` values from the filtered rows.
4. Write the list of transaction IDs into `ops/kill_target.json` as a JSON object with key `"killed_ids"`.
5. Write a resolution record into `ops/resolution.json` with the following structure:
{
    "incident_id": "INC-003",
    "action": "kill_long_transactions",
    "killed_ids": <the same list as above>
}
Do not include any other fields.
"""
    with open("runbooks/manage_long_txns.md", "w") as f:
        f.write(manage_txn_content)

    ups_content = """# UPS Outage Runbook

## Steps
1. Check power distribution unit status.
2. Coordinate with facility team.
"""
    with open("runbooks/ups_outage_runbook.md", "w") as f:
        f.write(ups_content)

    # ---------- logs/active_transactions.csv ----------
    os.makedirs("logs", exist_ok=True)
    txn_rows = [
        ("txn_id", "duration_seconds", "state", "query"),
        ("txn-001", "15", "active", "SELECT * FROM orders"),
        ("txn-002", "45", "active", "UPDATE users SET balance = balance - 100"),
        ("txn-003", "60", "active", "DELETE FROM temp_data"),
        ("txn-004", "10", "idle", "COMMIT"),
        ("txn-005", "35", "active", "INSERT INTO audit_log VALUES (...)"),
        ("txn-006", "5", "active", "SELECT 1"),
        ("txn-007", "90", "active", "CREATE INDEX idx_orders_created_at ON orders(created_at)"),
        ("txn-008", "20", "active", "UPDATE inventory SET qty = qty - 1"),
        ("txn-009", "50", "idle", "BEGIN"),
        ("txn-010", "0", "active", "VACUUM")  # duration 0, not >30
    ]
    with open("logs/active_transactions.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for row in txn_rows:
            writer.writerow(row)

    # ---------- decoy files ----------
    # slow_queries.log (noisy)
    with open("logs/slow_queries.log", "w") as f:
        f.write("2026-04-01 02:55:00 | 12.3s | SELECT ...\n")
        f.write("2026-04-01 02:58:00 | 45.2s | UPDATE ...\n")
    # pg_stat_activity.txt (partial snapshot)
    with open("logs/pg_stat_activity.txt", "w") as f:
        f.write("pid | txn_id | state | duration\n")
        f.write("1234 | txn-002 | active | 40\n")
        f.write("5678 | txn-009 | idle | 50\n")

    # Empty ops directory (agent must create files)
    if not os.path.exists("ops"):
        os.makedirs("ops")

if __name__ == "__main__":
    build_env()
