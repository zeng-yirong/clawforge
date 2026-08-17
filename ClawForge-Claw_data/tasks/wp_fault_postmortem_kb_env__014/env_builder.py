import os
import json

def build_env():
    # fault_cases.json
    fault_cases = [
        {
            "fault_id": "fault_001",
            "service_name": "inventory-service",
            "severity": "high",
            "stack_trace": "Error: NullPointerException at ...",
            "call_chain": "svc-a -> svc-b",
            "root_cause_hint": "Missing cache entry",
            "repair_plan_hint": "Rebuild cache"
        },
        {
            "fault_id": "fault_002",
            "service_name": "notification-service",
            "severity": "medium",
            "stack_trace": "Timeout after 30s",
            "call_chain": "svc-c -> svc-d",
            "root_cause_hint": "External API latency",
            "repair_plan_hint": "Increase timeout"
        },
        {
            "fault_id": "fault_014",
            "service_name": "payment-service",
            "severity": "critical",
            "stack_trace": "Deadlock detected on table 'orders'",
            "call_chain": "svc-pay -> svc-db",
            "root_cause_hint": "Long-running transaction caused row lock escalation",
            "repair_plan_hint": "Kill the blocking transaction and restart service"
        }
    ]
    os.makedirs("faults", exist_ok=True)
    with open("faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # attachments.json
    attachments = [
        {
            "path": "attachments/incident_001_log.txt",
            "title": "Inventory incident log",
            "kind": "text",
            "description": "Log file for fault_001"
        },
        {
            "path": "attachments/incident_002_report.txt",
            "title": "Notification incident report",
            "kind": "text",
            "description": "Report for fault_002"
        },
        {
            "path": "attachments/incident_014_notes.txt",
            "title": "Payment incident analysis notes",
            "kind": "text",
            "description": "Root cause analysis notes for fault_014"
        }
    ]
    with open("attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # attachment files
    os.makedirs("attachments", exist_ok=True)
    with open("attachments/incident_001_log.txt", "w") as f:
        f.write("Transaction IDs encountered: TX-111, TX-222, TX-333\nNo specific root cause identified.\n")
    with open("attachments/incident_002_report.txt", "w") as f:
        f.write("This incident was caused by a timeout. No transaction details.\n")
    with open("attachments/incident_014_notes.txt", "w") as f:
        f.write("=== Root Cause Analysis ===\n")
        f.write("Root cause: Deadlock due to long-running transaction\n")
        f.write("Transaction ID: TX-2024-03-15-001\n")
        f.write("Impact: Payment processing halted for 12 minutes\n")

    # extra distractor: data/accounts.json (unrelated)
    os.makedirs("data", exist_ok=True)
    accounts = {
        "accounts": [
            {"account_id": "acc_01", "display_name": "Alice", "department": "Engineering", "email": "alice@example.com", "permissions": ["read"]},
            {"account_id": "acc_02", "display_name": "Bob", "department": "Ops", "email": "bob@example.com", "permissions": ["admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
