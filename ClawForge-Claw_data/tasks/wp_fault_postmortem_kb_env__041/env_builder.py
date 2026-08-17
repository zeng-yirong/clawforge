import os
import json

def build_env():
    # 创建目录结构
    dirs = ["data/faults", "data", "attachments", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    # 1. 创建 accounts.json（占位，不会被考核）
    accounts = {
        "accounts": [
            {"account_id": "a001", "display_name": "Alice", "department": "SRE", "email": "alice@co.com", "permissions": ["read", "write"]},
            {"account_id": "a002", "display_name": "Bob", "department": "Dev", "email": "bob@co.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)
    
    # 2. 创建 contacts.json（占位）
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Charlie", "role": "oncall", "email": "charlie@co.com"},
            {"contact_id": "c002", "name": "Diana", "role": "manager", "email": "diana@co.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)
    
    # 3. 创建 fault_cases.json（核心数据）
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fault_001",
                "service_name": "billing",
                "severity": "low",
                "stack_trace": "Stack trace A...",
                "call_chain": "billing -> db",
                "root_cause_hint": "Low disk space on db node",
                "repair_plan_hint": "Clean old logs"
            },
            {
                "fault_id": "fault_041",
                "service_name": "payment",
                "severity": "critical",
                "stack_trace": "Stack trace P...",
                "call_chain": "payment -> pool -> db",
                "root_cause_hint": "Connection pool exhausted",
                "repair_plan_hint": "Increase pool size and optimize slow queries"
            },
            {
                "fault_id": "fault_088",
                "service_name": "notification",
                "severity": "warning",
                "stack_trace": "Stack trace N...",
                "call_chain": "notif -> queue",
                "root_cause_hint": "Queue backlog due to slow consumer",
                "repair_plan_hint": "Add more consumers"
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f)
    
    # 4. 创建 attachments.json（指向真实附件文件）
    attachments = {
        "attachments": [
            {
                "path": "attachments/billing_metrics.json",
                "title": "Billing perf dump",
                "kind": "perf",
                "description": "Billing service metrics"
            },
            {
                "path": "attachments/payment_metrics.json",
                "title": "Payment perf dump",
                "kind": "perf",
                "description": "Payment service metrics including connection pool"
            },
            {
                "path": "attachments/notification_metrics.json",
                "title": "Notification perf dump",
                "kind": "perf",
                "description": "Notification service metrics"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f)
    
    # 5. 创建附件文件（每个附件是一个 JSON）
    # billing_metrics.json（干扰）
    billing_metrics = {
        "peak_connections": 200,
        "connection_limit": 300,
        "note": "Normal operation"
    }
    with open("attachments/billing_metrics.json", "w") as f:
        json.dump(billing_metrics, f)
    
    # payment_metrics.json（目标附件）
    payment_metrics = {
        "peak_connections": 512,
        "connection_limit": 400,
        "note": "Connection pool exhausted"
    }
    with open("attachments/payment_metrics.json", "w") as f:
        json.dump(payment_metrics, f)
    
    # notification_metrics.json（干扰）
    notification_metrics = {
        "peak_connections": 80,
        "connection_limit": 200,
        "note": "Within limits"
    }
    with open("attachments/notification_metrics.json", "w") as f:
        json.dump(notification_metrics, f)
    
    # 6. 创建空的 ops 目录（待 agent 写入结果）
    # ops 目录已在上方创建，无需额外操作
    
    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
