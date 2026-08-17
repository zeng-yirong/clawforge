import os
import json

def build_env():
    # Ensure base directories exist
    os.makedirs("data/faults", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/old", exist_ok=True)

    # ---- Fault Cases ----
    fault_cases = [
        {
            "fault_id": "fault-001",
            "service_name": "order-service",
            "severity": "warning",
            "stack_trace": "data/attachments/stack_trace_fault001.txt",
            "call_chain": "data/attachments/call_chain_fault001.txt",
            "root_cause_hint": "",
            "repair_plan_hint": ""
        },
        {
            "fault_id": "fault-002",
            "service_name": "payment-service",
            "severity": "info",
            "stack_trace": "data/attachments/stack_trace_fault002.txt",
            "call_chain": "data/attachments/call_chain_fault002.txt",
            "root_cause_hint": "",
            "repair_plan_hint": ""
        },
        {
            "fault_id": "fault-003",
            "service_name": "payment-service",
            "severity": "critical",
            "stack_trace": "data/attachments/stack_trace_fault003.txt",
            "call_chain": "data/attachments/call_chain_fault003.txt",
            "root_cause_hint": "",
            "repair_plan_hint": ""
        }
    ]
    with open("data/faults/fault_cases.json", "w") as f:
        json.dump({"fault_cases": fault_cases}, f, indent=2)

    # ---- Attachments Index ----
    attachments = [
        {"path": "data/attachments/stack_trace_fault001.txt", "title": "Stack Trace fault-001", "kind": "stack_trace", "description": "IndexOutOfBounds stack trace"},
        {"path": "data/attachments/call_chain_fault001.txt", "title": "Call Chain fault-001", "kind": "call_chain", "description": "order-service internal call chain"},
        {"path": "data/attachments/stack_trace_fault002.txt", "title": "Stack Trace fault-002", "kind": "stack_trace", "description": "Timeout exception stack trace"},
        {"path": "data/attachments/call_chain_fault002.txt", "title": "Call Chain fault-002", "kind": "call_chain", "description": "payment-service normal call chain"},
        {"path": "data/attachments/stack_trace_fault003.txt", "title": "Stack Trace fault-003", "kind": "stack_trace", "description": "NullPointer stack trace"},
        {"path": "data/attachments/call_chain_fault003.txt", "title": "Call Chain fault-003", "kind": "call_chain", "description": "payment-service crash call chain"},
        {"path": "data/attachments/repair_note_fault003.txt", "title": "Repair Note fault-003", "kind": "repair_note", "description": "Suggested fix for the payment crash"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---- Actual Attachment Files ----
    # fault-001 (distractor)
    with open("data/attachments/stack_trace_fault001.txt", "w") as f:
        f.write("java.lang.IndexOutOfBoundsException: Index 5 out of bounds for length 3\n    at com.order.OrderService.getItem(OrderService.java:17)")
    with open("data/attachments/call_chain_fault001.txt", "w") as f:
        f.write("order-service -> inventory-service")

    # fault-002 (distractor, same service but not critical)
    with open("data/attachments/stack_trace_fault002.txt", "w") as f:
        f.write("java.util.concurrent.TimeoutException: Timed out waiting for response\n    at com.payment.PaymentGateway.connect(PaymentGateway.java:91)")
    with open("data/attachments/call_chain_fault002.txt", "w") as f:
        f.write("api-gateway -> payment-service -> external-provider")

    # fault-003 (target)
    with open("data/attachments/stack_trace_fault003.txt", "w") as f:
        f.write("NullPointerException at PaymentService.processTransaction line 42\n    at com.payment.PaymentService.processTransaction(PaymentService.java:42)\n    at com.payment.PaymentController.handleRequest(PaymentController.java:78)")
    with open("data/attachments/call_chain_fault003.txt", "w") as f:
        f.write("api-gateway -> order-service -> payment-service")
    with open("data/attachments/repair_note_fault003.txt", "w") as f:
        f.write("Add null check for order object before processing payment.")

    # ---- Distractor: old / irrelevant files ----
    with open("data/old/old_stack_trace.txt", "w") as f:
        f.write("obsolete trace from last week")
    with open("data/old/notes.txt", "w") as f:
        f.write("Meeting notes, not relevant")

if __name__ == "__main__":
    build_env()
