import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，等待agent写入

    # 故障案例
    fault_cases = [
        {
            "fault_id": "fault_001",
            "service_name": "order-service",
            "severity": "high",
            "stack_trace": "at com.example.OrderService.process()\nCaused by: java.sql.SQLException: Timeout",
            "call_chain": "gateway -> order -> payment",
            "root_cause_hint": "数据库超时",
            "repair_plan_hint": "增加连接池"
        },
        {
            "fault_id": "fault_002",
            "service_name": "inventory-service",
            "severity": "critical",
            "stack_trace": "at com.example.InventoryService.updateStock()\nCaused by: java.lang.OutOfMemoryError",
            "call_chain": "gateway -> inventory -> warehouse",
            "root_cause_hint": "OOM",
            "repair_plan_hint": "增加内存"
        },
        {
            "fault_id": "fault_003",
            "service_name": "payment-service",
            "severity": "critical",
            "stack_trace": "at com.example.PaymentService.execute()\nCaused by: com.mysql.cj.jdbc.exceptions.MySQLTransactionRollbackException: Deadlock found when trying to get lock; try restarting transaction",
            "call_chain": "gateway -> payment -> ledger",
            "root_cause_hint": "死锁",
            "repair_plan_hint": "检查事务顺序"
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # 附件索引
    attachments = [
        {
            "path": "attachments/fault_001.log",
            "title": "order-timeout.log",
            "kind": "log",
            "description": "订单超时日志"
        },
        {
            "path": "attachments/fault_002.log",
            "title": "inventory-oom.log",
            "kind": "log",
            "description": "库存OOM日志"
        },
        {
            "path": "attachments/fault_003.log",
            "title": "payment-deadlock.log",
            "kind": "log",
            "description": "支付死锁日志"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 实际日志文件（干扰项 + 唯一答案）
    # fault_001.log – 超时相关，包含一个事务ID但并非死锁
    with open("attachments/fault_001.log", "w") as f:
        f.write("[2025-03-15 00:12:34] Transaction TXN-20250315-100 started\n")
        f.write("[2025-03-15 00:12:35] SQL timeout, connection pool exhausted\n")
        f.write("[2025-03-15 00:12:36] Rollback TXN-20250315-100\n")

    # fault_002.log – OOM相关，包含另一个事务ID
    with open("attachments/fault_002.log", "w") as f:
        f.write("[2025-03-15 01:23:45] Transaction TXN-20250315-200 started\n")
        f.write("[2025-03-15 01:23:46] OutOfMemoryError in heap allocation\n")
        f.write("[2025-03-15 01:23:47] Process killed\n")

    # fault_003.log – 死锁日志，仅此一个包含 Deadlock 关键字 + 真实事务ID
    with open("attachments/fault_003.log", "w") as f:
        f.write("[2025-03-15 02:34:56] Transaction TXN-20250315-999 started\n")
        f.write("[2025-03-15 02:34:57] Deadlock detected, transaction ID: TXN-20250315-001\n")
        f.write("[2025-03-15 02:34:57] Rolling back transaction TXN-20250315-999\n")

if __name__ == "__main__":
    build_env()
