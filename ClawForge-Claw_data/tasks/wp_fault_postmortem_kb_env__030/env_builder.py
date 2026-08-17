import os
import json

def build_env():
    # 数据目录
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # 干扰性 accounts.json
    accounts = {
        "accounts": [
            {"account_id": "admin", "display_name": "Admin", "department": "IT", "email": "admin@corp.com", "permissions": ["read","write"]},
            {"account_id": "ops1", "display_name": "OPS User", "department": "Ops", "email": "ops1@corp.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 干扰性 contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Alice", "role": "DBA", "email": "alice@corp.com"},
            {"contact_id": "C002", "name": "Bob", "role": "Dev", "email": "bob@corp.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 故障案例（含唯一答案）
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "FP-2025-001",
                "service_name": "payment-service",
                "severity": "critical",
                "stack_trace": "java.lang.ThreadDeath: null\n at com.payment.service.PaymentProcessor.process(PaymentProcessor.java:45)\n at com.payment.service.PaymentService.handleRequest(PaymentService.java:22)\n ... (truncated)",
                "call_chain": "api-gateway -> payment-service -> database",
                "root_cause_hint": "Long-running INSERT transaction",
                "repair_plan_hint": "Kill the transaction and review the batch insert logic"
            },
            {
                "fault_id": "FP-2025-002",
                "service_name": "notification-service",
                "severity": "warning",
                "stack_trace": "java.lang.OutOfMemoryError: Java heap space\n at ...",
                "call_chain": "internal-scheduler -> notification-service -> cache",
                "root_cause_hint": "Memory leak in cache refresh",
                "repair_plan_hint": "Increase heap size and fix cache eviction"
            },
            {
                "fault_id": "FP-2025-003",
                "service_name": "auth-service",
                "severity": "low",
                "stack_trace": "java.security.AccessControlException\n at ...",
                "call_chain": "gateway -> auth-service",
                "root_cause_hint": "Misconfigured permissions",
                "repair_plan_hint": "Update IAM policy"
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f, indent=2)

    # 附件索引
    attachments = {
        "attachments": [
            {
                "path": "attachments/slow_query_fp001.log",
                "title": "Slow Query Log for FP-2025-001",
                "kind": "log",
                "description": "Captured during the incident"
            },
            {
                "path": "attachments/error_log_fp002.txt",
                "title": "Error Log for FP-2025-002",
                "kind": "log",
                "description": "Notification service error traces"
            },
            {
                "path": "attachments/dump_fp001.txt",
                "title": "Thread Dump for FP-2025-001",
                "kind": "dump",
                "description": "Thread dump from payment-service"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 附件文件
    # 正确答案所在附件
    slow_log = """# Slow Query Log - captured at 2025-04-10 03:15:23
# Database: payments_db
# Query: INSERT INTO payments (amount, status) VALUES (?, ?)
# Duration: 8934ms
# Transaction ID: TX-7890123456
# Thread: qtp123456
# Explanation: This transaction is blocked by a long-running INSERT.
# Additional line to confuse: transaction_id=TX-0000000000
"""
    with open("attachments/slow_query_fp001.log", "w") as f:
        f.write(slow_log)

    # 干扰附件
    error_log = """# Error Log - notification-service crash
# Transaction ID: TX-0000000000
# Details: OutOfMemoryError
"""
    with open("attachments/error_log_fp002.txt", "w") as f:
        f.write(error_log)

    dump = """# Thread Dump
"http-nio-8080-exec-10" #10 prio=5 os_prio=0 tid=0x00007f... nid=0x1e23 waiting for monitor entry
  java.lang.Thread.State: BLOCKED (on object monitor)
  at com.payment.service.PaymentProcessor.process(PaymentProcessor.java:45)
  ...
"""
    with open("attachments/dump_fp001.txt", "w") as f:
        f.write(dump)

if __name__ == "__main__":
    build_env()
