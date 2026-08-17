import os
import json
import random

def build_env():
    # ------------------------------------------------------------------
    # 1. 创建目录结构
    # ------------------------------------------------------------------
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ------------------------------------------------------------------
    # 2. 创建多个干扰故障案例（包含脏数据、过期版本、格式错误等）
    # ------------------------------------------------------------------
    fault_cases = [
        {
            "fault_id": "fault_001",
            "service_name": "auth-service",
            "severity": "low",
            "stack_trace": "dummy trace 1",
            "call_chain": "gateway -> auth -> user",
            "root_cause_hint": "expired token cache",
            "repair_plan_hint": "flush cache and rotate keys"
        },
        {
            "fault_id": "fault_002",
            "service_name": "inventory-service",
            "severity": "medium",
            "stack_trace": "dummy trace 2",
            "call_chain": "api -> inventory -> db",
            "root_cause_hint": "connection pool exhausted",
            "repair_plan_hint": "increase pool size, add read replicas"
        },
        {
            "fault_id": "fault_003",   # 脏数据：缺少必要字段
            "service_name": "payment-service",
            "severity": "critical"
        },
        {
            "fault_id": "fault_004",
            "service_name": "notification-service",
            "severity": "high",
            "stack_trace": "trace 4",
            "call_chain": "web -> notify -> smtp",
            "root_cause_hint": "SMTP server timeout",
            "repair_plan_hint": "switch to backup SMTP"
        },
        {
            "fault_id": "fault_005",
            "service_name": "payment-service",
            "severity": "low",
            "stack_trace": "trace 5",
            "call_chain": "api -> payment -> legacy",
            "root_cause_hint": "legacy endpoint deprecated",
            "repair_plan_hint": "migrate to new API"
        },
        {
            "fault_id": "fault_006",
            "service_name": "payment-service",
            "severity": "medium",
            "stack_trace": "trace 6",
            "call_chain": "api -> payment -> db",
            "root_cause_hint": "deadlock on table locks",
            "repair_plan_hint": "optimize queries, use NOWAIT"
        },
        {
            "fault_id": "fault_007",   # 目标故障
            "service_name": "payment-service",
            "severity": "critical",
            "stack_trace": "FATAL: out of shared memory\nPID 1234, query timeout\nCall chain: gateway -> payment -> payment-db",
            "call_chain": "gateway -> payment -> payment-db",
            "root_cause_hint": "Main database IO saturation due to unoptimized full-table scan from payment service's nightly batch job. The job's query lacked index on transaction_date, causing sequential scan on 50M rows.",
            "repair_plan_hint": "1. Add composite index on (transaction_date, status) for the batch query. 2. Schedule batch during low-traffic window (04:00-05:00). 3. Implement query timeout and circuit breaker in payment service. 4. Add read replica for reporting queries."
        },
        {
            "fault_id": "fault_008",
            "service_name": "user-service",
            "severity": "high",
            "stack_trace": "trace 8",
            "call_chain": "api -> user -> cache",
            "root_cause_hint": "redis eviction storm",
            "repair_plan_hint": "increase maxmemory, use LRU"
        }
    ]

    # 写入 fault_cases.json（带干扰：部分记录格式破损，但fault_007完好）
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # ------------------------------------------------------------------
    # 3. 创建附件：目标故障的附件，内容包含根因和修复计划（纯文本）
    # ------------------------------------------------------------------
    attachment_target = (
        "=== Fault Postmortem Attachment ===\n"
        "Fault ID: fault_007\n"
        "Service: payment-service\n"
        "Severity: critical\n"
        "\n"
        "Root Cause:\n"
        "Main database IO saturation due to unoptimized full-table scan from payment service's nightly batch job. "
        "The job's query lacked index on transaction_date, causing sequential scan on 50M rows.\n"
        "\n"
        "Repair Plan:\n"
        "1. Add composite index on (transaction_date, status) for the batch query.\n"
        "2. Schedule batch during low-traffic window (04:00-05:00).\n"
        "3. Implement query timeout and circuit breaker in payment service.\n"
        "4. Add read replica for reporting queries.\n"
        "\n"
        "Call Chain: gateway -> payment -> payment-db\n"
        "Stack Trace (last 10 lines): ... (omitted for brevity)\n"
    )
    with open("data/attachments/crash_log_007.txt", "w") as f:
        f.write(attachment_target)

    # 创建干扰附件
    for i in [1, 2, 3, 4, 5, 6, 8]:
        content = f"Dummy attachment for fault_{i:03d}, no useful info.\n"
        with open(f"data/attachments/crash_log_{i:03d}.txt", "w") as f:
            f.write(content)

    # 额外干扰：一个损坏的附件（非文本）
    with open("data/attachments/crash_log_009.bin", "wb") as f:
        f.write(b"\x00\x01\x02\x03")

    # ------------------------------------------------------------------
    # 4. 在 db_dumps 中创建一些干扰文件
    # ------------------------------------------------------------------
    with open("db_dumps/2025-03-21_full.sql", "w") as f:
        f.write("-- dummy sql dump\n")
    with open("db_dumps/slow_queries.log", "w") as f:
        f.write("2025-03-21 03:00:00 | query_time=300s | ...\n")

    # ------------------------------------------------------------------
    # 5. 创建一个同名但错误的 ops/postmortem_report.json 作为诱饵（已存在，但内容错误）
    # ------------------------------------------------------------------
    bait = {
        "service": "payment-service",
        "severity": "low",
        "root_cause": "fake root cause",
        "repair_plan": "fake plan"
    }
    with open("ops/postmortem_report.json", "w") as f:
        json.dump(bait, f, indent=2)

if __name__ == "__main__":
    build_env()
