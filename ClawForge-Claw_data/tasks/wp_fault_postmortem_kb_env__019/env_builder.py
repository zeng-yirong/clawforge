import os
import json
import random
import string

def build_env():
    # 创建目录结构
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ----- 干扰: accounts.json -----
    accounts = []
    for i in range(3):
        accounts.append({
            "account_id": f"ACC-{100+i}",
            "display_name": f"User {i}",
            "department": random.choice(["Engineering", "Support", "SRE"]),
            "email": f"user{i}@company.com",
            "permissions": random.sample(["read", "write", "admin"], k=random.randint(1,3))
        })
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ----- 干扰: contacts.json -----
    contacts = []
    for i in range(2):
        contacts.append({
            "contact_id": f"C-{200+i}",
            "name": f"Contact {i}",
            "role": random.choice(["oncall", "manager"]),
            "email": f"contact{i}@company.com"
        })
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ----- 目标附件文件内容 -----
    stack_trace_content = """java.lang.RuntimeException: Connection pool exhausted
    at com.payment.service.PaymentProcessor.process(PaymentProcessor.java:42)
    at com.payment.service.PaymentController.handle(PaymentController.java:18)
    at org.apache.tomcat.util.net.NioEndpoint$SocketProcessor.doRun(NioEndpoint.java:1234)
    ... 5 more
Caused by: java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available, request timed out after 30000ms
    at com.zaxxer.hikari.pool.HikariPool.createTimeoutException(HikariPool.java:689)
    at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:195)"""

    call_chain_content = """payment-service -> accounting-service (timeout)
payment-service -> inventory-service (timeout)
payment-service -> user-service (OK 200ms)"""

    # 写入目标附件文件
    with open("data/attachments/stack_trace_f003.txt", "w") as f:
        f.write(stack_trace_content)
    with open("data/attachments/call_chain_f003.txt", "w") as f:
        f.write(call_chain_content)

    # ----- attachments.json (包含目标和干扰附件) -----
    attachments = [
        {
            "path": "data/attachments/stack_trace_f003.txt",
            "title": "Stack Trace for F-003",
            "kind": "stack_trace",
            "description": "Full stack trace of the payment-service crash. fault_id: F-003"
        },
        {
            "path": "data/attachments/call_chain_f003.txt",
            "title": "Call Chain for F-003",
            "kind": "call_chain",
            "description": "Service call chain during the incident. fault_id: F-003"
        },
        {
            "path": "data/attachments/debug_log_jan01.txt",
            "title": "Debug Log 2025-01-01",
            "kind": "log",
            "description": "Routine debug logs for payment-service"
        },
        {
            "path": "data/attachments/monitor_snapshot.png",
            "title": "Monitor Snapshot",
            "kind": "image",
            "description": "CPU usage graph from monitoring"
        }
    ]
    # 为干扰附件创建空文件（保证路径存在）
    for att in attachments[2:]:
        open(att["path"], "w").close()
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ----- fault_cases.json (包含目标和干扰) -----
    fault_cases = [
        {
            "fault_id": "F-001",
            "service_name": "user-service",
            "severity": "warning",
            "stack_trace": "irrelevant stack",
            "call_chain": "user-service -> db (OK)",
            "root_cause_hint": "偶尔慢查询",
            "repair_plan_hint": "增加索引"
        },
        {
            "fault_id": "F-002",
            "service_name": "inventory-service",
            "severity": "critical",
            "stack_trace": "irrelevant stack",
            "call_chain": "inventory-service -> cache (timeout)",
            "root_cause_hint": "缓存击穿",
            "repair_plan_hint": "布隆过滤+限流"
        },
        {
            "fault_id": "F-003",
            "service_name": "payment-service",
            "severity": "critical",
            "stack_trace": stack_trace_content,
            "call_chain": call_chain_content,
            "root_cause_hint": "数据库连接池耗尽导致请求超时",
            "repair_plan_hint": "增加连接池大小至200并重启服务"
        },
        {
            "fault_id": "F-004",
            "service_name": "notification-service",
            "severity": "minor",
            "stack_trace": "no",
            "call_chain": "no",
            "root_cause_hint": "配置错误",
            "repair_plan_hint": "修正配置文件"
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

if __name__ == "__main__":
    build_env()
