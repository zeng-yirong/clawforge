import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 创建故障案例文件 (fault_cases.json)
    fault_cases = [
        {
            "fault_id": "F037",
            "service_name": "InventoryService",
            "severity": "critical",
            "stack_trace": "LockAcquisitionException: could not obtain lock on inventory_lock\n\tat com.example.InventoryService.updateStock(InventoryService.java:85)",
            "call_chain": "OrderService -> PaymentService -> InventoryService",
            "root_cause_hint": "",
            "repair_plan_hint": ""
        },
        {
            "fault_id": "F012",
            "service_name": "UserService",
            "severity": "major",
            "stack_trace": "NullPointerException at UserService.getProfile(UserService.java:42)",
            "call_chain": "API -> UserService",
            "root_cause_hint": "Missing user object",
            "repair_plan_hint": "Add null check"
        },
        {
            "fault_id": "F089",
            "service_name": "LegacyBatch",
            "severity": "warning",
            "stack_trace": "OutOfMemoryError: Java heap space",
            "call_chain": "Scheduler -> BatchProcessor",
            "root_cause_hint": "Memory leak in batch loop",
            "repair_plan_hint": "Increase heap or fix leak"
        }
    ]

    wrapper = {
        "fault_cases": fault_cases
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(wrapper, f, indent=2)

    # 创建附件索引 (attachments.json)
    attachments = [
        {
            "path": "attachments/incident_F037.log",
            "title": "Deadlock trace for fault F037",
            "kind": "log",
            "description": "MySQL deadlock log captured during incident"
        },
        {
            "path": "attachments/old_incident_F012.txt",
            "title": "Old incident F012 log",
            "kind": "log",
            "description": "Unrelated log for fault F012"
        },
        {
            "path": "attachments/legacy_batch_heapdump.hprof",
            "title": "Heap dump for F089",
            "kind": "dump",
            "description": "Not relevant to current deadlock"
        }
    ]
    wrapper_att = {"attachments": attachments}
    with open("data/attachments.json", "w") as f:
        json.dump(wrapper_att, f, indent=2)

    # 创建实际的附件日志文件
    deadlock_log_content = (
        "2024-03-12 03:15:22 - Transaction: txn_8899 requested lock on inventory_lock (mode: X)\n"
        "2024-03-12 03:15:23 - Transaction: txn_8900 blocked by txn_8899 on inventory_lock\n"
        "2024-03-12 03:15:25 - Deadlock detected, victim selected: txn_8900\n"
        "2024-03-12 03:15:26 - Transaction txn_8899 committed\n"
        "2024-03-12 03:15:27 - Rollback for txn_8900 initiated\n"
    )
    with open("attachments/incident_F037.log", "w") as f:
        f.write(deadlock_log_content)

    # 创建干扰附件
    with open("attachments/old_incident_F012.txt", "w") as f:
        f.write("F012 log: no lock info here\n")
    with open("attachments/legacy_batch_heapdump.hprof", "w") as f:
        f.write("binary heap dump placeholder\n")

    # 创建额外的干扰文件 (旧版本或无关数据)
    os.makedirs("db_dumps", exist_ok=True)
    with open("db_dumps/backup_20240311.sql", "w") as f:
        f.write("-- old backup not needed\n")
    with open("ops/old_postmortem_F012.json", "w") as f:
        json.dump({"fault_id": "F012", "root_cause": "NullPointer"}, f)

if __name__ == "__main__":
    build_env()
