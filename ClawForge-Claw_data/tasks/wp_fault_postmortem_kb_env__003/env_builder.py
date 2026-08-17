import os
import json

def build_env():
    # ---- 目录结构 ----
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- 故障案例（三个，只有 fc_001 是目标） ----
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "fc_001",
                "service_name": "api-gateway,user-service",
                "severity": "critical",
                "stack_trace": "... pool exhausted ...",
                "call_chain": "gateway -> user-service -> database",
                "root_cause_hint": "",
                "repair_plan_hint": ""
            },
            {
                "fault_id": "fc_002",
                "service_name": "payment-service",
                "severity": "warning",
                "stack_trace": "... null pointer ...",
                "call_chain": "payment-service -> redis",
                "root_cause_hint": "NullPointerException in DiscountModule",
                "repair_plan_hint": "Add null check for discount config"
            },
            {
                "fault_id": "fc_003",
                "service_name": "notification-service",
                "severity": "info",
                "stack_trace": "... timeout ...",
                "call_chain": "notification -> sms-provider",
                "root_cause_hint": "SMS provider timeout",
                "repair_plan_hint": "Increase timeout to 10s"
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f, indent=2)

    # ---- 附件索引 ----
    attachments = {
        "attachments": [
            {
                "path": "data/attachments/stack_trace_fc_001.txt",
                "title": "Stack Trace - fc_001",
                "kind": "stack_trace",
                "description": "Full stack trace for critical fault fc_001"
            },
            {
                "path": "data/attachments/call_chain_fc_001.txt",
                "title": "Call Chain - fc_001",
                "kind": "call_chain",
                "description": "Call chain snapshot for fc_001"
            },
            {
                "path": "data/attachments/normal_log.txt",
                "title": "Normal Operation Log",
                "kind": "log",
                "description": "Log from a healthy service, irrelevant"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ---- 附件内容 ----
    # fc_001 堆栈附件中包含根因和修复方案（唯一答案来源）
    with open("data/attachments/stack_trace_fc_001.txt", "w") as f:
        f.write("""[ERROR] 2025-04-10 03:14:22.001 - Thread pool exhausted, all 200 connections in use.
Root cause: Database connection pool exhaustion
Repair: Increase max_connections and reduce timeout
Related knowledge entry: ke_001
""")
    with open("data/attachments/call_chain_fc_001.txt", "w") as f:
        f.write("api-gateway -> user-service -> database (timeout after 30s)")
    with open("data/attachments/normal_log.txt", "w") as f:
        f.write("[INFO] 2025-04-10 02:00:00 - All services healthy")

    # ---- 知识库条目 ----
    knowledge_entries = {
        "knowledge_entries": [
            {
                "entry_id": "ke_001",
                "title": "Database Connection Pool Tuning",
                "description": "How to properly size connection pools and handle exhaustion.",
                "keywords": ["pool", "database", "connection"]
            },
            {
                "entry_id": "ke_002",
                "title": "Load Balancer Health Check",
                "description": "Configuring health check intervals for backend services.",
                "keywords": ["load balancer", "health"]
            },
            {
                "entry_id": "ke_003",
                "title": "Circuit Breaker Pattern",
                "description": "Implementing circuit breaker for external dependencies.",
                "keywords": ["circuit breaker", "resilience"]
            }
        ]
    }
    with open("data/knowledge_entries.json", "w") as f:
        json.dump(knowledge_entries, f, indent=2)

if __name__ == "__main__":
    build_env()
