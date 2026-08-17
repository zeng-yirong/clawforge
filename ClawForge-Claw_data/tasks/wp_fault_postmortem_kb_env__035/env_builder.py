import os
import json
import shutil

def build_env():
    # 确保工作区干净
    for item in os.listdir('.'):
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)

    # 创建必要的目录
    os.makedirs('data/faults', exist_ok=True)
    os.makedirs('data/attachments', exist_ok=True)
    os.makedirs('ops/postmortems', exist_ok=True)
    os.makedirs('old_reports', exist_ok=True)

    # ---------- 故障案例表（含干扰项） ----------
    fault_cases = [
        {
            "fault_id": "F-20250321-001",
            "service_name": "order-service",
            "severity": "critical",
            "stack_trace": "java.lang.NullPointerException at com.example.order.OrderProcessor.process(OrderProcessor.java:42)",
            "call_chain": "web -> auth -> order -> payment",
            "root_cause_hint": "Null pointer due to missing payment method in order payload",
            "repair_plan_hint": "Add validation for payment_method before processing order; notify frontend to enforce field"
        },
        {
            "fault_id": "F-20250321-002",
            "service_name": "inventory-service",
            "severity": "major",
            "stack_trace": "java.lang.OutOfMemoryError at com.example.inventory.StockManager.updateStock(StockManager.java:88)",
            "call_chain": "web -> order -> inventory",
            "root_cause_hint": "Memory leak in bulk update operation; large result set not closed",
            "repair_plan_hint": "Add try-with-resources for database cursors; limit batch size to 1000"
        },
        {
            "fault_id": "F-20250321-003",
            "service_name": "notification-service",
            "severity": "minor",
            "stack_trace": "java.lang.IllegalArgumentException at com.example.notification.EmailSender.send(EmailSender.java:25)",
            "call_chain": "web -> notification",
            "root_cause_hint": "Invalid email address format in recipient list",
            "repair_plan_hint": "Add email validation before sending; log invalid addresses for manual review"
        }
    ]
    with open('data/faults/fault_cases.json', 'w') as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # ---------- 附件索引（部分指向目标故障） ----------
    attachments = [
        {
            "path": "data/attachments/order_thread_dump.txt",
            "title": "Order Service Thread Dump",
            "kind": "thread_dump",
            "description": "Thread dump captured at incident time, showing blocked threads in order-service",
            "fault_id": "F-20250321-001"
        },
        {
            "path": "data/attachments/order_heap_dump.hprof",
            "title": "Order Heap Dump",
            "kind": "heap_dump",
            "description": "Heap dump from order-service JVM; contains null references in payment objects",
            "fault_id": "F-20250321-001"
        },
        {
            "path": "data/attachments/inventory_log.txt",
            "title": "Inventory Service Error Log",
            "kind": "error_log",
            "description": "OutOfMemoryError occurrences in inventory-service",
            "fault_id": "F-20250321-002"
        }
    ]
    with open('data/attachments.json', 'w') as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---------- 干扰：accounts 和 contacts ----------
    accounts = [
        {
            "account_id": "acc-001",
            "display_name": "Alice Wang",
            "department": "SRE",
            "email": "alice@example.com",
            "permissions": ["read", "write", "admin"]
        },
        {
            "account_id": "acc-002",
            "display_name": "Bob Li",
            "department": "Backend",
            "email": "bob@example.com",
            "permissions": ["read", "write"]
        }
    ]
    with open('data/accounts.json', 'w') as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {
            "contact_id": "c-001",
            "name": "Charlie Zhang",
            "role": "on-call engineer",
            "email": "charlie@example.com"
        }
    ]
    with open('data/contacts.json', 'w') as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- 干扰：旧报告目录 ----------
    old_report = {
        "fault_id": "F-20250320-001",
        "root_cause": "Disk full on /var/log",
        "repair_plan": "Add log rotation",
        "generated_by": "old_script"
    }
    with open('old_reports/F-20250320-001.json', 'w') as f:
        json.dump(old_report, f, indent=2)

if __name__ == '__main__':
    build_env()
