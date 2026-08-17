import os
import json

def build_env():
    # 创建所需目录
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops/postmortem", exist_ok=True)

    # —— 故障案例（含干扰项）——
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fault_001",
                "service_name": "user-service",
                "severity": "high",
                "stack_trace": "java.lang.NullPointerException at com.example.UserController.getUser",
                "call_chain": "gateway -> user-service",
                "root_cause_hint": "Null pointer due to missing user id",
                "repair_plan_hint": "Add null check"
            },
            {
                "fault_id": "fault_007",
                "service_name": "order-service",
                "severity": "critical",
                "stack_trace": "java.lang.Thread deadlock at com.example.OrderService.updateOrder",
                "call_chain": "api-gateway -> order-service -> payment-service -> inventory-service",
                "root_cause_hint": "",
                "repair_plan_hint": ""
            },
            {
                "fault_id": "fault_003",
                "service_name": "inventory-service",
                "severity": "medium",
                "stack_trace": "java.lang.OutOfMemoryError at com.example.InventoryService.listItems",
                "call_chain": "order-service -> inventory-service",
                "root_cause_hint": "Memory leak in cache",
                "repair_plan_hint": "Increase heap size and review cache"
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f, indent=2)

    # —— 附件索引（含干扰项）——
    attachments = {
        "attachments": [
            {
                "path": "data/attachments/deadlock_info.txt",
                "title": "Deadlock Info",
                "kind": "log",
                "description": "Database deadlock report related to fault_007",
                "fault_id": "fault_007"
            },
            {
                "path": "data/attachments/slow_query.log",
                "title": "Slow Query Log",
                "kind": "log",
                "description": "Slow queries around the time of fault_007",
                "fault_id": "fault_007"
            },
            {
                "path": "data/attachments/error_log.txt",
                "title": "User Service Error Log",
                "kind": "log",
                "description": "Error log for user-service fault",
                "fault_id": "fault_001"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # —— 附件文件内容（关键信息在 deadlock_info.txt）——
    deadlock_content = """Deadlock Analysis:
- Two transactions attempted to update the same order (order_id=12345) concurrently.
- Both used UPDATE statement without selecting with FOR UPDATE.
- Result: deadlock.
- Root cause: Deadlock on table orders due to concurrent updates without proper locking.
- Recommendation: Use SELECT ... FOR UPDATE NOWAIT and add retry logic for order updates.
"""
    with open("data/attachments/deadlock_info.txt", "w") as f:
        f.write(deadlock_content)

    slow_query_content = """Time: 2025-04-10 02:59:00
Query: SELECT * FROM orders WHERE customer_id=42 ORDER BY created_at;
Duration: 23.4s
Missing index on customer_id.
"""
    with open("data/attachments/slow_query.log", "w") as f:
        f.write(slow_query_content)

    error_log_content = """2025-04-10 02:45:12 ERROR NullPointerException at UserController.getUser
"""
    with open("data/attachments/error_log.txt", "w") as f:
        f.write(error_log_content)

    # —— 干扰的非必需数据——
    accounts = {
        "accounts": [
            {"account_id": "alice", "display_name": "Alice", "department": "ops", "email": "alice@example.com", "permissions": ["admin"]},
            {"account_id": "bob", "display_name": "Bob", "department": "dev", "email": "bob@example.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Charlie", "role": "oncall", "email": "charlie@example.com"},
            {"contact_id": "c002", "name": "Diana", "role": "dba", "email": "diana@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # —— 模板报告（agent 应仿此格式）——
    example_report = {
        "fault_id": "fault_000",
        "service_name": "example-service",
        "root_cause": "Example root cause",
        "repair_plan": "Example repair plan"
    }
    with open("ops/postmortem/example.json", "w") as f:
        json.dump(example_report, f, indent=2)

if __name__ == "__main__":
    build_env()
