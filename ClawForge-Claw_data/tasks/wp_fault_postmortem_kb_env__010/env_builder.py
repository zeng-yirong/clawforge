import os
import json

def build_env():
    # 创建目录结构
    dirs = [
        "data/faults",
        "data/attachments",
        "data",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # --- 故障案例 (fault_cases.json) ---
    fault_cases = [
        {
            "fault_id": "fault-001",
            "service_name": "payment",
            "severity": "critical",
            "stack_trace": "Signal 11 caught at 0x7f...",
            "call_chain": "payment.gateway → payment.processor → db.connector",
            "root_cause_hint": "",
            "repair_plan_hint": "",
            "responsible_contact_id": "c001"
        },
        {
            "fault_id": "fault-002",
            "service_name": "notification",
            "severity": "major",
            "stack_trace": "Timeout on queue write",
            "call_chain": "notify.push → notify.queue",
            "root_cause_hint": "Queue backlog",
            "repair_plan_hint": "Scale consumers",
            "responsible_contact_id": "c002"
        },
        {
            "fault_id": "fault-003",
            "service_name": "user-auth",
            "severity": "minor",
            "stack_trace": "Rate limit exceeded",
            "call_chain": "auth.login → auth.token",
            "root_cause_hint": "Token cache miss",
            "repair_plan_hint": "Increase cache TTL",
            "responsible_contact_id": "c003"
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # 干扰：备份文件
    backup_cases = [
        {
            "fault_id": "fault-001",
            "service_name": "payment",
            "severity": "critical",
            "stack_trace": "old stack",
            "call_chain": "old call chain",
            "root_cause_hint": "Old root cause",
            "repair_plan_hint": "Old repair plan",
            "responsible_contact_id": "c001"
        }
    ]
    with open("data/faults/fault_cases_backup.json", "w") as f:
        json.dump({"fault_cases": backup_cases}, f, indent=2)

    # --- 附件清单 (attachments.json) ---
    attachments = [
        {
            "path": "data/attachments/fault-001_analysis.txt",
            "title": "Fault-001 Analysis",
            "kind": "text",
            "description": "Root cause analysis for payment service fault"
        },
        {
            "path": "data/attachments/fault-001_weekly_report.txt",
            "title": "Weekly Report",
            "kind": "text",
            "description": "General weekly report, not related"
        },
        {
            "path": "data/attachments/fault-002_analysis.txt",
            "title": "Fault-002 Analysis",
            "kind": "text",
            "description": "Root cause analysis for notification fault"
        },
        {
            "path": "data/attachments/fault-001_analysis_old.txt",
            "title": "Fault-001 Analysis (old version)",
            "kind": "text",
            "description": "Stale version, should be ignored"
        }
    ]
    # 写入附件文件内容（只创建有效附件，忽略干扰的旧版本，但干扰文件不需要实际存在？旧版本文件要存在才能迷惑 agent）
    # 创建所有附件文件
    for att in attachments:
        filepath = att["path"]
        dirpath = os.path.dirname(filepath)
        os.makedirs(dirpath, exist_ok=True)
        if "fault-001_analysis.txt" in filepath and "old" not in filepath:
            content = "Root Cause: Database connection pool exhaustion due to missing timeout settings.\nRepair Plan: Add connection timeout (5s) and max pool size limit (100)."
        elif "fault-001_analysis_old.txt" in filepath:
            content = "Root Cause: Old disk I/O contention.\nRepair Plan: Upgrade to SSD."
        elif "fault-002_analysis.txt" in filepath:
            content = "Root Cause: Queue consumer lag.\nRepair Plan: Add more consumers."
        elif "fault-001_weekly_report.txt" in filepath:
            content = "Weekly progress: Deployed version 2.3.1, all good."
        else:
            content = ""
        with open(filepath, "w") as f:
            f.write(content)

    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # --- 联系人 (contacts.json) ---
    contacts = [
        {"contact_id": "c001", "name": "Alice", "role": "SRE", "email": "alice@example.com"},
        {"contact_id": "c002", "name": "Bob", "role": "Dev", "email": "bob@example.com"},
        {"contact_id": "c003", "name": "Charlie", "role": "QA", "email": "charlie@example.com"}
    ]
    # 额外添加一个无关联系人用于干扰
    contacts.append({"contact_id": "c999", "name": "Zara", "role": "Manager", "email": "zara@example.com"})
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- 干扰数据：accounts.json (完全无关) ---
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "Infra", "email": "alice@company.com", "permissions": ["read", "write"]},
        {"account_id": "a002", "display_name": "Bob", "department": "Dev", "email": "bob@company.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
