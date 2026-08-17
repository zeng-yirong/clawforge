import os
import json
import random

def build_env():
    # Ensure base directories exist
    for d in ["data/faults", "data", "attachments/logs", "ops", "raw_logs"]:
        os.makedirs(d, exist_ok=True)

    # ---- accounts.json (干扰项) ----
    accounts = {
        "accounts": [
            {"account_id": "acct_01", "display_name": "Alice", "department": "payment", "email": "alice@co.io", "permissions": ["read"]},
            {"account_id": "acct_02", "display_name": "Bob", "department": "order", "email": "bob@co.io", "permissions": ["write"]},
            {"account_id": "acct_03", "display_name": "Carol", "department": "infra", "email": "carol@co.io", "permissions": ["admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- contacts.json (正确联系人: payment-owner -> Alice) ----
    contacts = {
        "contacts": [
            {"contact_id": "contact_01", "name": "Bob", "role": "order-owner", "email": "bob@co.io"},
            {"contact_id": "contact_02", "name": "Carol", "role": "infra-oncall", "email": "carol@co.io"},
            {"contact_id": "contact_03", "name": "Alice", "role": "payment-owner", "email": "alice@co.io"},
            {"contact_id": "contact_04", "name": "Dave", "role": "payment-owner", "email": "dave@old.co.io"}  # 干扰：旧人但email无效
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---- attachments.json (多个附件，只有一个是fault_007相关的) ----
    attachments = {
        "attachments": [
            {"path": "attachments/logs/fault_007_stack.png", "title": "Fault 007 stack trace screenshot", "kind": "image", "description": "Thread dump showing deadlock"},
            {"path": "attachments/logs/fault_003_perf.png", "title": "Fault 003 perf graph", "kind": "image", "description": "CPU spike"},
            {"path": "attachments/docs/order_flow.pdf", "title": "Order flow design", "kind": "document", "description": "System design doc"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ---- fault_cases.json (核心数据) ----
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fault_001",
                "service_name": "order-service",
                "severity": "critical",
                "stack_trace": "at com.order.TransactionManager.doCommit(TransactionManager.java:88)",
                "call_chain": "api-gateway -> order-service -> inventory-db",
                "root_cause_hint": "Optimistic lock conflict in inventory",
                "repair_plan_hint": "Implement pessimistic lock and increase retries"
            },
            {
                "fault_id": "fault_007",  # 目标案例
                "service_name": "payment-service",
                "severity": "critical",
                "stack_trace": "at com.payment.TransactionManager.execute(TransactionManager.java:42)\nCaused by: java.sql.SQLException: Deadlock detected",
                "call_chain": "api-gateway -> payment-service -> payment-db",
                "root_cause_hint": "Deadlock in payment transaction",
                "repair_plan_hint": "Rollback and retry with timeout"
            },
            {
                "fault_id": "fault_012",
                "service_name": "payment-service",
                "severity": "warning",
                "stack_trace": "at com.payment.Validator.validate(Validator.java:21)",
                "call_chain": "payment-service -> risk-engine",
                "root_cause_hint": "Incomplete input validation",
                "repair_plan_hint": "Add input sanitization"
            },
            {
                # 脏数据：缺少 root_cause_hint 字段
                "fault_id": "fault_099",
                "service_name": "notification-service",
                "severity": "info",
                "stack_trace": "",
                "call_chain": "",
                "repair_plan_hint": ""
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f, indent=2)

    # ---- 其他干扰文件 ----
    with open("raw_logs/old_debug.log", "w") as f:
        f.write("[2025-01-15 03:12:44] fault_001 processed\n")
    with open("raw_logs/metrics.csv", "w") as f:
        f.write("timestamp,latency\n2025-01-15T03:00:00,2500\n")

if __name__ == "__main__":
    build_env()
