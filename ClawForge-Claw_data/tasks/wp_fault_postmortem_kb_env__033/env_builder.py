import os
import json

def build_env():
    # 创建 data 子目录
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，agent 将写入

    # 故障案例列表（包含干扰项）
    fault_cases = [
        {
            "fault_id": "fault_001",
            "service_name": "order-service",
            "severity": "critical",
            "stack_trace": "ERROR: transaction id 7330 aborted\n in OrderService.process()",
            "call_chain": "api-gateway -> order-service -> database",
            "root_cause_hint": "transaction 7330 timeout",
            "repair_plan_hint": "kill session 7330"
        },
        {
            "fault_id": "fault_002",
            "service_name": "inventory-service",
            "severity": "warning",
            "stack_trace": "WARN: slow query detected, tid=5522",
            "call_chain": "order-service -> inventory-service -> database",
            "root_cause_hint": "missing index",
            "repair_plan_hint": "add index on product_id"
        },
        {
            "fault_id": "fault_003",
            "service_name": "payment-service",
            "severity": "critical",
            "stack_trace": "FATAL: deadlock detected, victim transaction id 7331\n in PaymentProcessor.execute()",
            "call_chain": "order-service -> payment-service -> database",
            "root_cause_hint": "transaction 7331 holding row lock",
            "repair_plan_hint": "kill transaction 7331"
        },
        {
            "fault_id": "fault_004",
            "service_name": "notification-service",
            "severity": "info",
            "stack_trace": "INFO: retry 3/3, tid=8819",
            "call_chain": "payment-service -> notification-service -> sms-gateway",
            "root_cause_hint": "timeout on sms provider",
            "repair_plan_hint": "increase retry interval"
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # 附件索引（每个故障对应一个附件，干扰附件只关联无关故障）
    attachments_data = {
        "attachments": [
            {
                "path": "attachments/payment.log",
                "title": "payment-service log excerpt",
                "kind": "log",
                "description": "Logs from payment-service during the fault window"
            },
            {
                "path": "attachments/order.log",
                "title": "order-service slow query log",
                "kind": "log",
                "description": "Order service stack traces"
            },
            {
                "path": "attachments/inventory.log",
                "title": "inventory-service performance log",
                "kind": "log",
                "description": "Inventory service warnings"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments_data, f, indent=2)

    # 创建附件日志文件，每个包含多行，只有 payment.log 包含目标事务 ID 7331
    # payment.log：包含多个事务 ID 行，但只有一个匹配堆栈中的 7331
    payment_log_content = """[03:00:01] PROCESS: starting payment for order 1001
[03:00:02] QUERY: update payments set status='pending' where id=1001
[03:00:03] ERROR: deadlock detected, victim transaction id 7331
[03:00:04] INFO: retrying transaction
[03:00:05] ERROR: transaction id 7330 already aborted (干扰)
[03:00:06] WARN: lock wait timeout exceeded for transaction 7332
"""
    with open("attachments/payment.log", "w") as f:
        f.write(payment_log_content)

    # 干扰附件：order.log 包含另一个事务 ID 7340
    order_log_content = """[02:59:50] PROCESS: order 2001
[02:59:51] QUERY: insert into orders ...
[02:59:52] ERROR: transaction id 7340 timeout
"""
    with open("attachments/order.log", "w") as f:
        f.write(order_log_content)

    # 干扰附件：inventory.log 完全不相关
    inventory_log_content = """[03:00:10] WARN: slow query on product_id index
[03:00:11] INFO: cache miss for SKU 8832
"""
    with open("attachments/inventory.log", "w") as f:
        f.write(inventory_log_content)


if __name__ == "__main__":
    build_env()
