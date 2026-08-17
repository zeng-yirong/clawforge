import os
import json
import random

def build_env():
    # 创建目录结构
    dirs = ["faults", "attachments", "raw_logs", "postmortem"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 附件：知识库条目 (真正的答案附件)
    kb_attachment = {
        "path": "attachments/attach_kb001.json",
        "title": "Known Issue: NullPointer fix",
        "kind": "knowledge",
        "description": "Root cause: NullPointerException in getAccountBalance due to missing null check. Repair: add null check before invoking method."
    }
    with open("attachments/attach_kb001.json", "w") as f:
        json.dump(kb_attachment, f)

    # 干扰附件：无用的日志文件
    log_attachment = {
        "path": "attachments/attach_log001.json",
        "title": "Application logs 2025-03-10",
        "kind": "log",
        "description": "Standard application logs, no relevant info."
    }
    with open("attachments/attach_log001.json", "w") as f:
        json.dump(log_attachment, f)

    # 干扰附件：另一个知识条目（无关）
    other_kb = {
        "path": "attachments/attach_kb002.json",
        "title": "Deployment checklist",
        "kind": "knowledge",
        "description": "Steps to deploy new version."
    }
    with open("attachments/attach_kb002.json", "w") as f:
        json.dump(other_kb, f)

    # 故障案例主文件
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fault-001",
                "service_name": "AccountService",
                "severity": "critical",
                "stack_trace": "java.lang.NullPointerException at com.example.AccountService.getAccountBalance(AccountService.java:45)",
                "call_chain": "api-gateway -> account-service -> db",
                "root_cause_hint": "NullPointerException in AccountService.getAccountBalance",
                "repair_plan_hint": "Add null check for account object",
                "attachment_path": "attachments/attach_kb001.json"
            },
            {
                "fault_id": "fault-002",
                "service_name": "PaymentService",
                "severity": "low",
                "stack_trace": "java.lang.ArrayIndexOutOfBoundsException at PaymentService.process",
                "call_chain": "payment-service -> cache",
                "root_cause_hint": "Array index out of bounds in payment processing",
                "repair_plan_hint": "Validate array length",
                "attachment_path": "attachments/attach_log001.json"
            },
            {
                "fault_id": "fault-003",
                "service_name": "NotificationService",
                "severity": "info",
                "stack_trace": "java.net.SocketTimeoutException",
                "call_chain": "notification-service -> email",
                "root_cause_hint": "Timeout when sending email",
                "repair_plan_hint": "Increase timeout or retry",
                "attachment_path": "attachments/attach_kb002.json"
            }
        ]
    }
    with open("faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f, indent=2)

    # 干扰数据：accounts.json (无关)
    accounts = {
        "accounts": [
            {"account_id": "a001", "display_name": "Alice", "department": "engineering", "email": "alice@corp.com", "permissions": ["read"]},
            {"account_id": "a002", "display_name": "Bob", "department": "ops", "email": "bob@corp.com", "permissions": ["read","write"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # 干扰数据：contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Charlie", "role": "oncall", "email": "charlie@corp.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # 干扰数据：raw_logs 下的随机日志文件
    for i in range(3):
        with open(f"raw_logs/log_{i}.txt", "w") as f:
            f.write(f"2025-03-10 10:0{i}:00 INFO No issue.\n")
    
    # 确保 postmortem 目录存在（但不放任何文件）
    os.makedirs("postmortem", exist_ok=True)

if __name__ == "__main__":
    build_env()
