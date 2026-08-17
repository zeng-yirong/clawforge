import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，等待agent填充

    # 写入干扰 accounts
    accounts = [
        {"account_id": "acc001", "display_name": "Alice", "department": "SRE", "email": "alice@corp.com", "permissions": ["read", "write"]},
        {"account_id": "acc002", "display_name": "Bob", "department": "Dev", "email": "bob@corp.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # 写入干扰 contacts
    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "oncall", "email": "charlie@corp.com"},
        {"contact_id": "c002", "name": "Diana", "role": "manager", "email": "diana@corp.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # 写入 fault_cases（三个case，第三个sev1是目标）
    fault_cases = [
        {
            "fault_id": "fault_001",
            "service_name": "auth-svc",
            "severity": "sev3",
            "stack_trace": "NullPointerException at line 42",
            "call_chain": "auth-svc -> db",
            "root_cause_hint": "Code bug in null check",
            "repair_plan_hint": "Add null validation"
        },
        {
            "fault_id": "fault_002",
            "service_name": "payment-svc",
            "severity": "sev2",
            "stack_trace": "TimeoutError: upstream bank gateway timeout",
            "call_chain": "payment-svc -> bank-gateway -> bank-core",
            "root_cause_hint": "Bank service unavailable",
            "repair_plan_hint": "Implement circuit breaker"
        },
        {
            "fault_id": "fault_003",
            "service_name": "payment-svc",
            "severity": "sev1",
            "stack_trace": "ConnectionPoolExhausted: cannot acquire connection from pool",
            "call_chain": "payment-svc -> db-pool",
            "root_cause_hint": "Network latency high",  # 误导
            "repair_plan_hint": "Increase pool size"    # 误导
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f)

    # 写入 attachments.json（三个附件，第三个对应目标，但只有它的日志包含真实根因）
    attachments = [
        {
            "path": "data/attachments/fault_001_log.txt",
            "title": "Auth error log",
            "kind": "log",
            "description": "Log from auth service showing NullPointer"
        },
        {
            "path": "data/attachments/fault_002_log.txt",
            "title": "Payment timeout log",
            "kind": "log",
            "description": "Log from payment timeout incident"
        },
        {
            "path": "data/attachments/fault_003_log.txt",
            "title": "Payment DB pool log",
            "kind": "log",
            "description": "Log showing connection pool exhaustion"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f)

    # 创建附件文件（干扰：前两个写错误信息，第三个写真实根因）
    with open("data/attachments/fault_001_log.txt", "w") as f:
        f.write("2025-04-01 03:00:00 ERROR NullPointerException in AuthService.login()\nRoot cause: Missing user object")
    with open("data/attachments/fault_002_log.txt", "w") as f:
        f.write("2025-04-01 03:05:00 ERROR Timeout after 30s calling bank-gateway\nRoot cause: Bank core maintenance window")
    with open("data/attachments/fault_003_log.txt", "w") as f:
        f.write("Root cause: Database connection pool exhausted\nRepair plan: Increase max connections from 10 to 50, and add connection timeout\nAffected services: payment-svc, db-pool\nFault ID: fault_003\n")

    # 添加一个无关干扰目录和文件
    os.makedirs("old_logs", exist_ok=True)
    with open("old_logs/archive.txt", "w") as f:
        f.write("This is an old log, ignore.")

if __name__ == "__main__":
    build_env()
