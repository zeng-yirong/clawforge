import os
import json

def build_env():
    # 创建目录
    os.makedirs("ops", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 故障案例列表，包含干扰项
    fault_cases = [
        {
            "fault_id": "F-2025-001",
            "service_name": "user-service",
            "severity": "major",
            "stack_trace": "TimeoutException at com.example.UserService.getUser",
            "call_chain": "A -> B (timeout)",
            "root_cause_hint": "network latency",
            "repair_plan_hint": "increase timeout to 5s",
            "attachments": ["attachments/fault_001_call_chain.txt"]
        },
        {
            "fault_id": "F-2025-002",
            "service_name": "inventory-service",
            "severity": "minor",
            "stack_trace": "NullPointerException at com.example.InventoryService.updateStock",
            "call_chain": "X -> Y -> Z",
            "root_cause_hint": "null reference",
            "repair_plan_hint": "add null check",
            "attachments": ["attachments/fault_002_stack.txt"]
        },
        {
            "fault_id": "F-2025-003",
            "service_name": "payment-gateway",
            "severity": "critical",
            "stack_trace": "java.util.concurrent.TimeoutException: pool exhausted\n  at com.zaxxer.hikari.pool.HikariPool.getConnection",
            "call_chain": "PaymentService -> DB (deadlock detected)\n  acquire connection failed after 30s",
            "root_cause_hint": "connection pool deadlock",
            "repair_plan_hint": "increase pool size to 50, add retry with backoff",
            "attachments": [
                "attachments/fault_003_call_chain.txt",
                "attachments/fault_003_stack.txt"
            ]
        }
    ]
    with open("ops/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # 附件内容
    # 干扰附件1：模糊的调用链
    with open("attachments/fault_001_call_chain.txt", "w") as f:
        f.write("call chain: A -> B (timeout after 2s)\nno further detail")
    # 干扰附件2：空指针堆栈
    with open("attachments/fault_002_stack.txt", "w") as f:
        f.write("java.lang.NullPointerException\n  at com.example.InventoryService.updateStock(InventoryService.java:42)")
    # 正确故障的调用链附件（详细描述死锁）
    with open("attachments/fault_003_call_chain.txt", "w") as f:
        f.write("Call chain analysis for fault F-2025-003 (payment-gateway):\n"
                "1. PaymentService receives request\n"
                "2. PaymentService calls OrderService (via HTTP) -> success\n"
                "3. PaymentService attempts to get DB connection from HikariPool\n"
                "4. All 20 connections are held by stalled threads (transaction not committed)\n"
                "5. Threads block indefinitely, causing a deadlock on the connection pool\n"
                "Root cause confirmed: connection pool exhaustion leading to deadlock")
    # 正确故障的堆栈附件
    with open("attachments/fault_003_stack.txt", "w") as f:
        f.write("Stack trace from thread dump:\n"
                "\"http-nio-8080-exec-12\" #24 daemon prio=5 os_prio=0 tid=0x00007f8a1c01e800 nid=0x3e3b waiting on condition\n"
                "  java.lang.Thread.State: TIMED_WAITING (parking)\n"
                "   at sun.misc.Unsafe.park(Native Method)\n"
                "   - parking to wait for  <0x000000076b5a3b28> (a java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject)\n"
                "   at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:197)\n"
                "   at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:148)\n"
                "   ... 24 more\n"
                "HikariPool-1 - Pool stats (total=20, active=20, idle=0, waiting=12)")

    # 可选的附件索引（干扰项，但不影响主要任务）
    attachments_index = [
        {"path": "attachments/fault_001_call_chain.txt", "title": "F-001 Call Chain", "kind": "text", "description": "call chain log for user-service fault"},
        {"path": "attachments/fault_002_stack.txt", "title": "F-002 Stack Trace", "kind": "text", "description": "stack trace for inventory-service fault"},
        {"path": "attachments/fault_003_call_chain.txt", "title": "F-003 Call Chain", "kind": "text", "description": "call chain showing deadlock"},
        {"path": "attachments/fault_003_stack.txt", "title": "F-003 Stack Dump", "kind": "text", "description": "thread dump showing pool exhaustion"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments_index}, f, indent=2)

    # 其他干扰数据
    accounts = [
        {"account_id": "acc-001", "display_name": "Alice", "department": "SRE", "email": "alice@co.io", "permissions": ["read", "write"]},
        {"account_id": "acc-002", "display_name": "Bob", "department": "Dev", "email": "bob@co.io", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
