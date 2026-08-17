import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 故障案例列表（含干扰项）
    fault_cases = [
        {
            "fault_id": "fault-001",
            "service_name": "order-service",
            "severity": "critical",
            "stack_trace": """java.lang.NullPointerException: Cannot invoke method on null object
    at com.example.order.OrderService.processOrder(OrderService.java:42)
    at ...
Caused by: java.lang.NullPointerException: customer is null""",
            "call_chain": "api-gateway -> order-service -> customer-service",
            "root_cause_hint": "Null check missing in customer lookup",
            "repair_plan_hint": "Add null check before calling customer-service"
        },
        {
            "fault_id": "fault-002",
            "service_name": "payment-service",
            "severity": "high",
            "stack_trace": """java.util.concurrent.TimeoutException: Timed out waiting for response
    at com.example.payment.PaymentClient.callExternal(PaymentClient.java:88)
    at ...
Caused by: java.net.SocketTimeoutException: Read timed out""",
            "call_chain": "api-gateway -> payment-service -> external-bank-api",
            "root_cause_hint": "External bank API timeout",
            "repair_plan_hint": "Increase timeout and add retry logic"
        },
        {
            "fault_id": "fault-003",
            "service_name": "payment-service",
            "severity": "critical",
            "stack_trace": """java.sql.SQLException: Deadlock detected on table account_transaction
    at com.example.payment.TransactionManager.commit(TransactionManager.java:67)
    at ...
Caused by: com.mysql.cj.exceptions.MysqlError: Deadlock found when trying to get lock; try restarting transaction""",
            "call_chain": "api-gateway -> payment-service -> transaction-db",
            "root_cause_hint": "Database connection pool exhaustion",
            "repair_plan_hint": "Restart the database"
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # 附件清单
    attachments = [
        {"path": "logs/fault-001_slow.log", "title": "Order service slow log", "kind": "log", "description": "Shows slow queries for order-service"},
        {"path": "logs/fault-002_slow.log", "title": "Payment service timeout log", "kind": "log", "description": "Timeout details for payment-service fault-002"},
        {"path": "logs/fault-003_slow.log", "title": "Payment service deadlock log", "kind": "log", "description": "Deadlock details for payment-service fault-003"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 创建附件日志文件（干扰日志也包含，但只有 fault-003 的日志包含正确答案）
    log1 = """2024-01-15 10:23:45 [WARN] Slow query: SELECT * FROM orders WHERE customer_id = ? took 15s
2024-01-15 10:23:46 [ERROR] NullPointerException in order processing"""
    with open("logs/fault-001_slow.log", "w") as f:
        f.write(log1)

    log2 = """2024-01-15 10:24:00 [ERROR] External API call to bank-service timed out after 30s
2024-01-15 10:24:01 [INFO] Retry attempt 1..."""
    with open("logs/fault-002_slow.log", "w") as f:
        f.write(log2)

    log3 = """2024-01-15 10:25:30 [ERROR] Deadlock detected when inserting into account_transaction.
Last SQL: INSERT INTO account_transaction (account_id, amount, transaction_date) VALUES (?,?,?)
Missing index on account_transaction.transaction_date leads to table-level lock.
Add index on account_transaction.transaction_date."""
    with open("logs/fault-003_slow.log", "w") as f:
        f.write(log3)

    # 额外干扰数据
    accounts = [
        {"account_id": "acct-001", "display_name": "Alice", "department": "Engineering", "email": "alice@example.com", "permissions": ["read", "write"]},
        {"account_id": "acct-002", "display_name": "Bob", "department": "Operations", "email": "bob@example.com", "permissions": ["admin"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c-001", "name": "Charlie", "role": "DBA", "email": "charlie@example.com"},
        {"contact_id": "c-002", "name": "Diana", "role": "SRE", "email": "diana@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
