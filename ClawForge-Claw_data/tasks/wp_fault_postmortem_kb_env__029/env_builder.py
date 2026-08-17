import os
import json
import random

def build_env():
    # Ensure required directories exist
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Fault cases (interference: two cases, only f-001 is critical)
    fault_cases = {
        "fault_cases": [
            {
                "fault_id": "f-001",
                "service_name": "payment-service",
                "severity": "critical",
                "stack_trace": (
                    "com.example.payment.PaymentService.processPayment(PaymentService.java:45)\n"
                    "  ... 5 more\n"
                    "Caused by: java.sql.SQLException: Deadlock detected when updating accounts"
                ),
                "call_chain": "payment-service -> order-service -> inventory-service",
                "root_cause_hint": "Check slow queries around 03:12; look for a deadlock on payment-service.",
                "repair_plan_hint": "Kill the blocking transaction ID from slow query logs."
            },
            {
                "fault_id": "f-002",
                "service_name": "notification-service",
                "severity": "warning",
                "stack_trace": "java.lang.NullPointerException at ...",
                "call_chain": "notification-service -> email-service",
                "root_cause_hint": "Misconfiguration in email template.",
                "repair_plan_hint": "Update config file."
            }
        ]
    }
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump(fault_cases, f, indent=2)

    # Attachments index
    attachments = {
        "attachments": [
            {
                "path": "logs/slow_queries.log",
                "title": "Slow Queries Log (payment-service)",
                "kind": "text",
                "description": "Contains slow query logs around the time of fault f-001, including potential deadlock transaction."
            },
            {
                "path": "logs/error_dump.log",
                "title": "Error Dump (notification-service)",
                "kind": "text",
                "description": "Error logs for notification-service, unrelated to f-001."
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # Slow queries log – only one deadlock record for payment-service, others are noise
    slow_queries_content = """\
2024-07-15 03:12:45 [DEADLOCK] transaction_id=tx_dl_payment_001 service=payment-service query=UPDATE accounts SET balance=balance-100 WHERE account_id=1234; WAITED FOR lock held by transaction_id=tx_dl_payment_001
2024-07-15 03:13:10 [SLOW] transaction_id=tx_slow_002 service=payment-service query=SELECT * FROM orders WHERE create_time > '2024-07-01' (took 12s)
2024-07-15 03:14:00 [DEADLOCK] transaction_id=tx_dl_other_003 service=notification-service query=UPDATE notifications SET sent=1 WHERE user_id=5678; WAITED FOR lock held by tx_dl_other_003
2024-07-15 03:15:30 [SLOW] transaction_id=tx_slow_004 service=inventory-service query=SELECT * FROM stock WHERE product_id=999 (took 8s)
"""
    with open("logs/slow_queries.log", "w") as f:
        f.write(slow_queries_content)

    # Error dump (completely irrelevant)
    with open("logs/error_dump.log", "w") as f:
        f.write("2024-07-15 03:20:00 [ERROR] notification-service: NullPointerException at EmailSender.send()\n")

if __name__ == "__main__":
    build_env()
