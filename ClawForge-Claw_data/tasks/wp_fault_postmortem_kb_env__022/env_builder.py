import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)  # 干扰目录

    # 1. 创建故障案例文件 (包含多个干扰案例)
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fault_001",
                "service_name": "user-service",
                "severity": "critical",
                "stack_trace": "Exception: NullPointerException at UserController.java:45",
                "call_chain": "user-service -> auth-service -> db",
                "root_cause_hint": "Null email field in request",
                "repair_plan_hint": "Add input validation before processing"
            },
            {
                "fault_id": "fault_002",
                "service_name": "payment-service",
                "severity": "major",
                "stack_trace": "TimeoutException: Connection refused after 30s",
                "call_chain": "payment-service -> gateway -> external-bank",
                "root_cause_hint": "External bank API down",
                "repair_plan_hint": "Add circuit breaker and fallback"
            },
            {
                "fault_id": "fault_003",
                "service_name": "order-service",
                "severity": "critical",
                "stack_trace": "java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available, request timed out after 30000ms",
                "call_chain": "order-service -> inventory-service -> database (MySQL)",
                "root_cause_hint": "Database connection pool exhausted by long-running queries",
                "repair_plan_hint": "Monitor pool usage, increase max-pool-size to 100, and optimize slow queries"
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f, indent=2)

    # 2. 创建附件索引（包含真实附件路径和其他干扰项）
    attachments = {
        "attachments": [
            {
                "path": "data/attachments/slow_query.log",
                "title": "Slow Query Log (order-service)",
                "kind": "log",
                "description": "Collected during fault_003 incident"
            },
            {
                "path": "data/attachments/deployment_history.md",
                "title": "Deployment History",
                "kind": "markdown",
                "description": "Recent changes across services"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 3. 创建慢查询日志附件（关键线索）
    slow_query_log = """2025-02-18 23:14:23.456 [http-nio-8080-exec-12] DEBUG c.z.hikari.HikariPool - HikariPool-1 - Pool stats (total=20, active=20, idle=0, waiting=15)
2025-02-18 23:14:23.457 [http-nio-8080-exec-12] WARN  c.z.hikari.pool.ProxyConnection - Failed to obtain JDBC connection: connection not available, will try again in 30ms
2025-02-18 23:14:53.512 [http-nio-8080-exec-12] ERROR o.a.c.c.C.[.[.[.[dispatcherServlet] - Servlet.service() for servlet [dispatcherServlet] in context with path [] threw exception
java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available, request timed out after 30000ms
... (truncated)
# 以下为慢查询语句示例（模拟）
# SELECT * FROM orders WHERE status = 'PENDING' AND created_at < NOW() - INTERVAL 24 HOUR ORDER BY created_at DESC
# 该查询无索引，全表扫描约1200万行
"""
    with open("data/attachments/slow_query.log", "w") as f:
        f.write(slow_query_log)

    # 4. 创建干扰文件（无用的日志）
    import random, string
    for i in range(3):
        with open(f"raw_logs/app_log_{i}.log", "w") as f:
            f.write(''.join(random.choices(string.ascii_letters, k=200)))

    # 5. 创建其他 schema 数据（作为干扰）
    accounts = {
        "accounts": [
            {"account_id": "admin", "display_name": "Admin", "department": "SRE", "email": "admin@company.com", "permissions": ["read", "write", "admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Alice", "role": "oncall", "email": "alice@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
