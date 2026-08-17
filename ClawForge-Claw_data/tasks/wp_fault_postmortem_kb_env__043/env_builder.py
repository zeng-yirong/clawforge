import os
import json
import shutil

def build_env():
    # 创建目录结构
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，待 agent 写入

    # ---- 故障案例库 ----
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fault-042",
                "service_name": "payment-service",
                "severity": "medium",
                "stack_trace": "Error: Timeout on database connection",
                "call_chain": "payment -> db",
                "root_cause_hint": "Check the error log in attachments/error.log",
                "repair_plan_hint": "Restart the service and clear connection pool"
            },
            {
                "fault_id": "fault-043",
                "service_name": "inventory-service",
                "severity": "critical",
                "stack_trace": "Deadlock detected; transaction rolled back",
                "call_chain": "inventory -> db (lock wait)",
                "root_cause_hint": "Check the slow query log from 2023-10-01 in attachments/slow_query_2023-10-01.log",
                "repair_plan_hint": "Kill the blocking transaction"
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f, indent=2)

    # ---- 干扰附件 ----
    # 错误日志 (干扰)
    with open("attachments/error.log", "w") as f:
        f.write("2023-10-01 03:15:22 [ERROR] Connection timeout for service payment\n")
        f.write("2023-10-01 03:16:45 [ERROR] Retry exhausted\n")

    # 慢查询日志 - 错误的日期 (干扰)
    with open("attachments/slow_query_2023-09-30.log", "w") as f:
        f.write("Query: SELECT * FROM orders WHERE status='pending' -- took 15s\n")
        f.write("Blocking transaction ID: 99999\n")

    # 正确的慢查询日志 (唯一答案)
    with open("attachments/slow_query_2023-10-01.log", "w") as f:
        f.write("Query: UPDATE inventory SET quantity = quantity - 1 WHERE id = 12345 -- took 180s\n")
        f.write("Lock wait: transaction 12345 holding exclusive lock\n")
        f.write("Blocking transaction ID: 12345\n")

    # 另一个干扰日志
    with open("attachments/app.log", "w") as f:
        f.write("INFO: Service started\n")
        f.write("WARN: High memory usage\n")

    # ---- 可选：accounts & contacts (仅用于背景，不干扰) ----
    accounts = {
        "accounts": [
            {"account_id": "admin01", "display_name": "Alice", "department": "ops", "email": "alice@co.com", "permissions": ["admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Bob", "role": "DBA", "email": "bob@co.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

if __name__ == "__main__":
    build_env()
