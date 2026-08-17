import os
import json
import random
import string

def build_env():
    # === 清理旧文件（如果存在），确保环境纯净 ===
    for root, dirs, files in os.walk("."):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))
        break

    # === 创建目录结构 ===
    os.makedirs("data")
    os.makedirs("data/faults")
    os.makedirs("data/attachments")  # 附件存放目录
    os.makedirs("db_dumps")
    os.makedirs("ops")  # 虽然prompt要求写入ops/，但这里可以预先创建空目录增加迷惑性

    # === 1. 创建 accounts.json（干扰数据） ===
    accounts = [
        {"account_id": "acc_001", "display_name": "Alice", "department": "DBA", "email": "alice@example.com", "permissions": ["read", "write", "admin"]},
        {"account_id": "acc_002", "display_name": "Bob", "department": "SRE", "email": "bob@example.com", "permissions": ["read"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # === 2. 创建 contacts.json（干扰数据） ===
    contacts = [
        {"contact_id": "ct_001", "name": "Carol", "role": "oncall", "email": "carol@example.com"},
        {"contact_id": "ct_002", "name": "Dave", "role": "engineer", "email": "dave@example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # === 3. 创建慢查询日志文件（附件，包含目标事务ID） ===
    slow_log_path = "data/attachments/slow_query.log"
    # 生成一些干扰日志行，真实目标行嵌入其中
    log_lines = []
    for i in range(10):
        fake_tx_id = f"TX-{random.randint(20240101, 20241231)}-{random.randint(100, 999)}"
        time_sec = round(random.uniform(1.0, 30.0), 2)
        log_lines.append(f"# Time: 2024-03-15T03:{random.randint(0,59):02d}:{random.randint(0,59):02d}Z")
        log_lines.append(f"# User@Host: root[root] @ localhost []  Id: {random.randint(100,500)}")
        log_lines.append(f"# Query_time: {time_sec}  Lock_time: {round(random.uniform(0,2),2)}  Rows_sent: 0  Rows_examined: 0")
        log_lines.append(f"SET timestamp=171047{random.randint(1000,9999)};")
        log_lines.append(f"UPDATE accounts SET balance = balance - 100 WHERE account_id = 'acc_{random.randint(1,500)}';")
        log_lines.append("")
    # 目标事务行 - 特殊的锁持有者
    target_log = "# Time: 2024-03-15T03:12:34Z\n"
    target_log += "# User@Host: app_user[app_user] @ [10.0.0.5]  Id: 256\n"
    target_log += "# Query_time: 82.73  Lock_time: 81.50  Rows_sent: 0  Rows_examined: 0\n"
    target_log += "SET timestamp=1710471554;\n"
    target_log += "-- TRANSACTION ID: TX-20240315-001\n"  # 这是我们要找的ID
    target_log += "BEGIN;\n"
    target_log += "UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 'P100';\n"
    target_log += "# 等待表级锁释放...\n"
    log_lines.insert(5, target_log)  # 插入到中间
    with open(slow_log_path, "w") as f:
        f.writelines("\n".join(log_lines))

    # === 4. 创建另一个附件（干扰附件） ===
    fake_attachment_path = "data/attachments/innodb_status.txt"
    with open(fake_attachment_path, "w") as f:
        f.write("InnoDB Status\n")
        f.write("0 lock transactions, 0 lock structs\n")
        f.write("No active transactions\n")

    # === 5. 创建 attachments.json 清单 ===
    attachments = [
        {"path": "data/attachments/slow_query.log", "title": "Slow Query Log 2024-03-15", "kind": "log", "description": "Post-mortem slow query log extract"},
        {"path": "data/attachments/innodb_status.txt", "title": "InnoDB Status Dump", "kind": "status", "description": "Manual InnoDB engine status snapshot"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # === 6. 创建 fault_cases.json（包含两个故障，其中一个关联到慢查询附件） ===
    fault_cases = [
        {
            "fault_id": "F401",
            "service_name": "inventory-service",
            "severity": "critical",
            "stack_trace": "at com.example.InventoryService.updateStock(InventoryService.java:45)\nCaused by: java.sql.SQLTimeoutException: Lock wait timeout exceeded",
            "call_chain": "payment-gateway -> order-service -> inventory-service",
            "root_cause_hint": "Long-running transaction holding table-level lock on `inventory` table; transaction ID found in slow query log.",
            "repair_plan_hint": "Kill the blocking transaction via `KILL QUERY <thread_id>` or kill the transaction ID."
        },
        {
            "fault_id": "F402",
            "service_name": "account-service",
            "severity": "warning",
            "stack_trace": "NullPointerException at com.example.AccountService.getBalance",
            "call_chain": "web-api -> account-service",
            "root_cause_hint": "Missing null check for account balance.",
            "repair_plan_hint": "Add null check and default value."
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # === 7. 创建 db_dumps 下的快照文件（干扰） ===
    with open("db_dumps/innodb_metadata.sql", "w") as f:
        f.write("-- InnoDB metadata snapshot\n")
        f.write("SELECT * FROM information_schema.INNODB_TRX;\n")
        f.write("-- (empty result set, all transactions already committed)\n")
    with open("db_dumps/lock_info.txt", "w") as f:
        f.write("TABLE LOCKS:\n")
        f.write("Table: `inventory`  Waiters: 0  Holders: THREAD_ID=256, TRANSACTION_ID=TX-20240315-001\n")

    print("Environment built successfully. Target transaction ID: TX-20240315-001")

if __name__ == "__main__":
    build_env()
