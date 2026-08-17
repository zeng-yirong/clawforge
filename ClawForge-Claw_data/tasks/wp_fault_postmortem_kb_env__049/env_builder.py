import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("faults", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("kb", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("old_logs", exist_ok=True)

    # 干扰的旧日志（内含无关ID）
    for i in range(3):
        with open(f"old_logs/session_{i}.log", "w") as f:
            f.write(f"[{i}] TRX_ID: {10000 + random.randint(1, 9999)}\n")
            f.write(f"[{i}] state: RUNNING\n")

    # ============ 知识库条目 ============
    knowledge_entries = [
        {
            "entry_id": "KB-042",
            "title": "Payment DB deadlock caused by long transaction",
            "related_trx_id": "98765",
            "solution": "Kill the offending session (PID 3021) and reduce lock timeout to 5s."
        },
        {
            "entry_id": "KB-013",
            "title": "Order service timeout due to slow DB",
            "related_trx_id": None,
            "solution": "Increase connection pool and add missing index on orders.status."
        },
        {
            "entry_id": "KB-057",
            "title": "Billing API retry storm",
            "related_trx_id": "33442",
            "solution": "Implement exponential backoff jitter and rate limit 10 req/s."
        }
    ]
    with open("kb/knowledge_entries.json", "w") as f:
        json.dump({"entries": knowledge_entries}, f)

    # ============ 附件日志 ============
    # 主要嫌疑日志
    with open("attachments/order_payment.log", "w") as f:
        f.write("[10:23:45] INFO: Request received, tx START\n")
        f.write("[10:23:46] DEBUG: TRX_ID: 98765\n")
        f.write("[10:23:47] WARN: Lock wait timeout on index idx_payment_status\n")
        f.write("[10:23:50] ERROR: Deadlock detected, victim transaction: 98765\n")
        f.write("[10:23:51] INFO: Rollback completed.\n")

    # 干扰日志
    with open("attachments/dispatcher.log", "w") as f:
        f.write("[09:15:00] TRX_ID: 33442\n")
        f.write("[09:15:01] state: COMMITTED\n")

    # ============ 故障案例 ============
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fault_003",
                "service_name": "payment-service",
                "severity": "P1",
                "stack_trace": "java.lang.Exception: deadlock\n\tat com.payment.db.lock(LockManager.java:42)",
                "call_chain": "payment-service → payment-db (10.0.1.5:3306)",
                "root_cause_hint": "Transaction 98765 holds lock on idx_payment_status; another transaction waits."
            },
            {
                "fault_id": "fault_001",
                "service_name": "order-service",
                "severity": "P2",
                "stack_trace": "java.net.SocketTimeoutException: Read timed out",
                "call_chain": "order-service → legacy-api (10.0.2.10:8080)",
                "root_cause_hint": "Legacy API response slow due to missing index."
            },
            {
                "fault_id": "fault_002",
                "service_name": "billing-api",
                "severity": "P3",
                "stack_trace": "java.lang.OutOfMemoryError: Java heap space",
                "call_chain": "billing-api → internal-cache",
                "root_cause_hint": "Retry storm causes memory exhaustion."
            }
        ]
    }
    with open("faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f)

    # ============ 附件索引（供Agent参考）============
    attachments = {
        "attachments": [
            {"path": "attachments/order_payment.log", "title": "Payment service log", "kind": "application/octet-stream"},
            {"path": "attachments/dispatcher.log", "title": "Dispatcher log", "kind": "application/octet-stream"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f)


if __name__ == "__main__":
    build_env()
