import os
import json
import shutil

def build_env():
    # 创建目录结构
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)  # 干扰目录
    os.makedirs("ops", exist_ok=True)        # 目标产物目录

    # ---------- 故障案例数据 ----------
    faults = [
        {
            "fault_id": "fault_001",
            "service_name": "order-service",
            "severity": "P1",
            "stack_trace": "java.lang.IllegalStateException: invalid state\n\tat com.example.order.OrderService.create(OrderService.java:23)",
            "call_chain": "api-gateway -> order-service -> inventory-service",
            "root_cause_hint": "Order state machine error",
            "repair_plan_hint": "Update order status transition logic"
        },
        {
            "fault_id": "fault_002",
            "service_name": "notification-service",
            "severity": "P2",
            "stack_trace": "java.lang.NullPointerException: null\n\tat com.example.notification.EmailSender.send(EmailSender.java:12)",
            "call_chain": "api-gateway -> payment-service -> notification-service",
            "root_cause_hint": "Null email address",
            "repair_plan_hint": "Add null check before sending"
        },
        {
            "fault_id": "fault_003",
            "service_name": "payment-gateway",
            "severity": "critical",
            "stack_trace": "java.lang.OutOfMemoryError: Java heap space\n\tat com.example.payment.PaymentGateway.process(PaymentGateway.java:45)\n\tat com.example.payment.PaymentGateway.handle(PaymentGateway.java:30)",
            "call_chain": "api-gateway -> payment-gateway -> notification-service",
            "root_cause_hint": "Memory leak in heap",
            "repair_plan_hint": "Increase heap size and flush logs"
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": faults}, f, indent=2)

    # ---------- 附件索引 ----------
    attachments = [
        {
            "path": "data/attachments/order_service_log.txt",
            "title": "Order service logs",
            "kind": "text",
            "description": "Logs around incident",
            "fault_id": "fault_001"
        },
        {
            "path": "data/attachments/payment_gateway_log.txt",
            "title": "Payment gateway crash logs",
            "kind": "text",
            "description": "Heap dump and GC logs",
            "fault_id": "fault_003"
        },
        {
            "path": "data/attachments/notification_debug.txt",
            "title": "Notification debug traces",
            "kind": "text",
            "description": "Debug output for null pointer",
            "fault_id": "fault_002"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---------- 创建具体附件文件 ----------
    # order_service_log.txt – 干扰文件
    with open("data/attachments/order_service_log.txt", "w") as f:
        f.write("2025-01-01 02:50:00 ERROR: IllegalStateException in order creation\n")
        f.write("2025-01-01 02:50:01 WARN: Retrying...\n")

    # payment_gateway_log.txt – 目标附件，包含根因和修复方案提示
    with open("data/attachments/payment_gateway_log.txt", "w") as f:
        f.write("2025-01-01 03:00:00 CRITICAL: OutOfMemoryError occurred at 2025-01-01 03:00:00. Solution: Increase heap to 2GB and enable garbage collection logging.\n")
        f.write("2025-01-01 03:00:01 INFO: Heap usage exceeded limit\n")
        f.write("2025-01-01 03:00:02 DEBUG: Thread dump taken\n")

    # notification_debug.txt – 干扰文件
    with open("data/attachments/notification_debug.txt", "w") as f:
        f.write("NullPointerException stack trace:\n")
        f.write("Email address is null\n")

    # ---------- 额外干扰：accounts.json, contacts.json (纯填充) ----------
    accounts = [
        {"account_id": "dev-01", "display_name": "Alice", "department": "platform", "email": "alice@example.com", "permissions": ["read"]},
        {"account_id": "dev-02", "display_name": "Bob", "department": "payment", "email": "bob@example.com", "permissions": ["write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "oncall", "email": "charlie@example.com"},
        {"contact_id": "c002", "name": "Diana", "role": "manager", "email": "diana@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- 垃圾目录 & 文件 ----------
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/unknown_crash.log", "w") as f:
        f.write("Some random crash\n")

if __name__ == "__main__":
    build_env()
