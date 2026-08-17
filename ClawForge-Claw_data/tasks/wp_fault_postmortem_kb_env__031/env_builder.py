import os
import json
import random

def build_env():
    # 确保基础目录存在
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("archive", exist_ok=True)

    # ---------- 干扰账户 ----------
    accounts = {
        "accounts": [
            {"account_id": "acc_100", "display_name": "Alice", "department": "engineering", "email": "alice@corp.io", "permissions": ["admin"]},
            {"account_id": "acc_101", "display_name": "Bob", "department": "sre", "email": "bob@corp.io", "permissions": ["read", "write"]},
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # ---------- 干扰联系人 ----------
    contacts = {
        "contacts": [
            {"contact_id": "c_001", "name": "Carol", "role": "oncall", "email": "carol@corp.io"},
            {"contact_id": "c_002", "name": "Dave", "role": "dba", "email": "dave@corp.io"},
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # ---------- 附件元数据 ----------
    attachments = {
        "attachments": [
            {
                "path": "data/logs/slow_query_20240321.log",
                "title": "Slow Query Log for fault_002",
                "kind": "log",
                "description": "Captured from order-service during the IO spike. Linked to fault_002."
            },
            {
                "path": "data/logs/app_errors.log",
                "title": "General Application Errors",
                "kind": "log",
                "description": "Unrelated application error dump from last week."
            },
            {
                "path": "archive/old_report.txt",
                "title": "Historical Postmortem",
                "kind": "report",
                "description": "A previous incident report, not relevant now."
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f)

    # ---------- 慢查询日志 (正确答案来源) ----------
    slow_log_content = """2024-03-21 03:12:01 [WARN] Query took 45.2s: SELECT * FROM orders WHERE status='pending' ORDER BY created_at DESC;
2024-03-21 03:14:33 [FATAL] Deadlock detected on orders table. Transaction 0x7f4a3b2c rolled back.
FINAL_ROOT_CAUSE: Missing composite index on orders (status, created_at) causing full table scans and lock escalation.
Repair: Create index idx_orders_status_created_at on orders(status, created_at); also add retry logic for deadlock.
2024-03-21 03:15:01 [INFO] Auto-recovery attempted but failed due to high contention.
"""
    with open("data/logs/slow_query_20240321.log", "w") as f:
        f.write(slow_log_content)

    # ---------- 干扰日志 ----------
    app_err_log = """2024-03-20 22:10:00 [ERROR] NullPointerException in payment-service
    at com.payment.PaymentProcessor.process(PaymentProcessor.java:42)
"""
    with open("data/logs/app_errors.log", "w") as f:
        f.write(app_err_log)

    # ---------- 干扰存档 ----------
    with open("archive/old_report.txt", "w") as f:
        f.write("Old incident: network partition, resolved by adding redundant links.\n")

    # ---------- 故障案例 (包含干扰项) ----------
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fault_001",
                "service_name": "payment-service",
                "severity": "low",
                "stack_trace": "java.lang.Exception at com.payment.PaymentProcessor.process(PaymentProcessor.java:42)",
                "call_chain": "gateway -> payment-service -> database",
                "root_cause_hint": "Transient network issue (likely a red herring)",
                "repair_plan_hint": "Restart pod and monitor"
            },
            {
                "fault_id": "fault_002",
                "service_name": "order-service",
                "severity": "critical",
                "stack_trace": "SQL Error: deadlock detected; transaction rolled back\n    at org.springframework.jdbc.support.SQLErrorCodeSQLExceptionTranslator.translate(SQLErrorCodeSQLExceptionTranslator.java:54)",
                "call_chain": "gateway -> order-service -> db-shard-3",
                "root_cause_hint": "Possibly overloaded CPU (misleading)",
                "repair_plan_hint": "Scale out more pods"
            },
            {
                "fault_id": "fault_003",
                "service_name": "inventory-service",
                "severity": "medium",
                "stack_trace": "TimeoutException: upstream read timed out",
                "call_chain": "inventory-service -> redis",
                "root_cause_hint": "Redis cluster split-brain",
                "repair_plan_hint": "Restart redis nodes"
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f)

    # ---------- 额外干扰文件 ----------
    # 一个看似相关的报告但内容错误
    with open("ops/preliminary_analysis.txt", "w") as f:
        f.write("初步分析：怀疑是网络问题，建议重试。\n")

    # 一个重复的附件路径（诱饵）
    with open("data/logs/slow_query_bak.log", "w") as f:
        f.write("This is a backup copy, not the actual slow query log.\n")

    # 一个空的目录
    os.makedirs("temp", exist_ok=True)

if __name__ == "__main__":
    build_env()
