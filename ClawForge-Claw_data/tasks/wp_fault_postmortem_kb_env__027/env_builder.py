import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 故障案例（干扰项 + 目标）
    fault_cases = [
        {
            "fault_id": "fault_001",
            "service_name": "payment",
            "severity": "critical",
            "stack_trace": "at PaymentService.processOrder...\nat DBConnection.execute",
            "call_chain": "gateway -> payment -> db",
            "root_cause_hint": "Deadlock on order table due to missing index",
            "repair_plan_hint": "Add composite index on (order_id, status)",
            "transaction_id": "tx_9a8b7c"
        },
        {
            "fault_id": "fault_002",
            "service_name": "user",
            "severity": "minor",
            "stack_trace": "at UserService.getProfile...\nat RedisCache.get",
            "call_chain": "api -> user -> cache",
            "root_cause_hint": "Cache miss after TTL expiry",
            "repair_plan_hint": "Increase default TTL to 600s",
            "transaction_id": "tx_000000"
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # 附件索引
    attachments = [
        {
            "path": "attachments/payment_slow_query.log",
            "title": "Payment Slow Query Log",
            "kind": "log",
            "description": "Slow queries captured from payment service during incident"
        },
        {
            "path": "attachments/user_slow_query.log",
            "title": "User Slow Query Log",
            "kind": "log",
            "description": "Slow queries from user service (unrelated)"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 实际附件文件（包含多个条目，只有一行匹配目标 transaction_id）
    payment_log_lines = [
        "2025-04-07 03:12:10.123 [payment] [tx_000001] SELECT * FROM orders WHERE status='pending'",
        "2025-04-07 03:15:23.456 [payment] [tx_9a8b7c] UPDATE orders SET status='completed' WHERE order_id=12345",
        "2025-04-07 03:18:45.678 [payment] [tx_000003] DELETE FROM temp"
    ]
    with open("attachments/payment_slow_query.log", "w") as f:
        f.write("\n".join(payment_log_lines))

    # 干扰附件
    user_log_lines = [
        "2025-04-07 04:00:00.000 [user] [tx_000004] SELECT * FROM users"
    ]
    with open("attachments/user_slow_query.log", "w") as f:
        f.write("\n".join(user_log_lines))

if __name__ == "__main__":
    build_env()
