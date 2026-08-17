#!/usr/bin/env python3
import json
import os
import sys

def write_score(score, details, workspace):
    result = {"total_score": score, "details": details}
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {score}/100")

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    json_path = os.path.join(workspace, "ops", "root_cause_report.json")
    details = []
    score = 0

    # 1. 文件存在 (10)
    if os.path.exists(json_path):
        score += 10
        details.append({
            "item": "File exists", "score": 10, "max_score": 10,
            "passed": True, "reason": "ops/root_cause_report.json found"
        })
    else:
        details.append({
            "item": "File exists", "score": 0, "max_score": 10,
            "passed": False, "reason": "File not found"
        })
        write_score(score, details, workspace)
        return

    # 2. JSON 合法性 (10)
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        score += 10
        details.append({
            "item": "JSON valid", "score": 10, "max_score": 10,
            "passed": True, "reason": "Successfully parsed"
        })
    except Exception as e:
        details.append({
            "item": "JSON valid", "score": 0, "max_score": 10,
            "passed": False, "reason": f"Parse error: {e}"
        })
        write_score(score, details, workspace)
        return

    # 3. 键集合正确 (10)
    expected_keys = {"fault_id", "root_cause_transaction_id", "repair_plan"}
    actual_keys = set(data.keys())
    if actual_keys == expected_keys:
        score += 10
        details.append({
            "item": "Key set correct", "score": 10, "max_score": 10,
            "passed": True, "reason": "Exactly the expected keys"
        })
    else:
        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys
        reason = f"Missing: {missing}, Extra: {extra}"
        details.append({
            "item": "Key set correct", "score": 0, "max_score": 10,
            "passed": False, "reason": reason
        })

    # 4. fault_id (15)
    fid = data.get("fault_id")
    if fid == "FP-2025-001":
        score += 15
        details.append({
            "item": "fault_id correct", "score": 15, "max_score": 15,
            "passed": True, "reason": "fault_id is FP-2025-001"
        })
    else:
        details.append({
            "item": "fault_id correct", "score": 0, "max_score": 15,
            "passed": False, "reason": f"Expected FP-2025-001, got {fid}"
        })

    # 5. root_cause_transaction_id (20)
    tid = data.get("root_cause_transaction_id")
    if tid == "TX-7890123456":
        score += 20
        details.append({
            "item": "root_cause_transaction_id correct", "score": 20, "max_score": 20,
            "passed": True, "reason": "Transaction ID matches"
        })
    else:
        details.append({
            "item": "root_cause_transaction_id correct", "score": 0, "max_score": 20,
            "passed": False, "reason": f"Expected TX-7890123456, got {tid}"
        })

    # 6. repair_plan (20)
    rp = data.get("repair_plan", "")
    contains_id = False
    contains_action = False
    rp_score = 0
    if isinstance(rp, str) and len(rp) > 0:
        contains_id = "TX-7890123456" in rp
        contains_action = any(w in rp.lower() for w in ["kill", "rollback", "abort"])
        if contains_id and contains_action:
            rp_score = 20
        elif contains_id or contains_action:
            rp_score = 10
        else:
            rp_score = 0
    score += rp_score
    details.append({
        "item": "repair_plan quality",
        "score": rp_score,
        "max_score": 20,
        "passed": rp_score == 20,
        "reason": (f"repair_plan length={len(rp) if isinstance(rp,str) else 0}, "
                   f"contains_id={contains_id}, contains_action={contains_action}")
    })

    write_score(score, details, workspace)

if __name__ == "__main__":
    main()
