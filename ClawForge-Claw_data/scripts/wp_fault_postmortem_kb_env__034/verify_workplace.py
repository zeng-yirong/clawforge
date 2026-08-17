import json
import sys
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace).resolve()

    details = []
    total_score = 0

    # ----- 1. Check ops/postmortem.json exists (10 pts) -----
    postmortem_path = workspace_path / "ops" / "postmortem.json"
    exists = postmortem_path.is_file()
    details.append({
        "item": "postmortem.json exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File found" if exists else "File not found at ops/postmortem.json"
    })
    if exists:
        total_score += 10
    else:
        # If file missing, no further checks possible
        output = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        print(json.dumps(output, indent=2))
        return

    # ----- 2. Valid JSON (10 pts) -----
    try:
        with open(postmortem_path, "r") as f:
            data = json.load(f)
        valid_json = True
    except (json.JSONDecodeError, Exception):
        valid_json = False
    details.append({
        "item": "valid JSON content",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": "JSON parses correctly" if valid_json else "Invalid JSON syntax"
    })
    if valid_json:
        total_score += 10
    else:
        output = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        print(json.dumps(output, indent=2))
        return

    # ----- 3. Required fields present (20 pts: 5 each) -----
    required_keys = ["fault_id", "root_cause", "call_chain", "repair_plan"]
    missing_keys = [k for k in required_keys if k not in data]
    present = len(missing_keys) == 0
    score_fields = 20 if present else 0
    details.append({
        "item": "all required keys (fault_id, root_cause, call_chain, repair_plan)",
        "score": score_fields,
        "max_score": 20,
        "passed": present,
        "reason": "All keys present" if present else f"Missing keys: {missing_keys}"
    })
    if present:
        total_score += 20
    else:
        output = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        print(json.dumps(output, indent=2))
        return

    # ----- 4. fault_id must be "fault-003" (10 pts) -----
    correct_fault_id = (data["fault_id"] == "fault-003")
    details.append({
        "item": "fault_id equals fault-003",
        "score": 10 if correct_fault_id else 0,
        "max_score": 10,
        "passed": correct_fault_id,
        "reason": "Correct fault ID" if correct_fault_id else f"Got '{data['fault_id']}', expected 'fault-003'"
    })
    if correct_fault_id:
        total_score += 10

    # ----- 5. root_cause contains required substrings (20 pts) -----
    rc = data.get("root_cause", "")
    has_null = "NullPointerException" in rc
    has_method = "PaymentService.processTransaction" in rc
    root_cause_ok = has_null and has_method
    details.append({
        "item": "root_cause identifies NullPointerException at PaymentService.processTransaction",
        "score": 20 if root_cause_ok else 0,
        "max_score": 20,
        "passed": root_cause_ok,
        "reason": "Root cause matches expected" if root_cause_ok else f"root_cause = '{rc}'"
    })
    if root_cause_ok:
        total_score += 20

    # ----- 6. call_chain exactly equal (15 pts) -----
    expected_chain = "api-gateway -> order-service -> payment-service"
    chain_ok = data.get("call_chain", "") == expected_chain
    details.append({
        "item": "call_chain is correct",
        "score": 15 if chain_ok else 0,
        "max_score": 15,
        "passed": chain_ok,
        "reason": "Correct call chain" if chain_ok else f"Got '{data.get('call_chain')}', expected '{expected_chain}'"
    })
    if chain_ok:
        total_score += 15

    # ----- 7. repair_plan exactly equal (15 pts) -----
    expected_repair = "Add null check for order object before processing payment."
    repair_ok = data.get("repair_plan", "") == expected_repair
    details.append({
        "item": "repair_plan matches attachment content",
        "score": 15 if repair_ok else 0,
        "max_score": 15,
        "passed": repair_ok,
        "reason": "Correct repair plan" if repair_ok else f"Got '{data.get('repair_plan')}', expected '{expected_repair}'"
    })
    if repair_ok:
        total_score += 15

    # ----- Final output -----
    output = {"total_score": total_score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
