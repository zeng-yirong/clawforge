import sys
import os
import json
import re

def verify(workspace):
    details = []
    total_score = 0

    # 1. 目录结构检查：ops 目录存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # 2. 目标文件存在 (10分)
    report_path = os.path.join(workspace, "ops", "root_cause.json")
    if os.path.isfile(report_path):
        details.append({"item": "root_cause.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/root_cause.json exists"})
        total_score += 10
    else:
        details.append({"item": "root_cause.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/root_cause.json not found"})
        # 后续检查跳过
        final = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. JSON 合法 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        final = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 4. 必要字段存在 (20分，每个5分)
    fields = ["fault_id", "root_cause", "repair_plan", "transaction_id"]
    field_scores = 0
    for fname in fields:
        if fname in data:
            field_scores += 5
            details.append({"item": f"Field '{fname}' present", "score": 5, "max_score": 5, "passed": True, "reason": f"'{fname}' found"})
        else:
            details.append({"item": f"Field '{fname}' present", "score": 0, "max_score": 5, "passed": False, "reason": f"'{fname}' missing"})
    total_score += field_scores

    # 5. fault_id 正确 (15分)
    if data.get("fault_id") == "fault-043":
        details.append({"item": "fault_id is correct", "score": 15, "max_score": 15, "passed": True, "reason": "fault_id is fault-043"})
        total_score += 15
    else:
        details.append({"item": "fault_id is correct", "score": 0, "max_score": 15, "passed": False, "reason": f"expected fault-043, got {data.get('fault_id')}"})

    # 6. transaction_id 正确 (25分)
    txn = data.get("transaction_id")
    if isinstance(txn, int) and txn == 12345:
        details.append({"item": "transaction_id is correct", "score": 25, "max_score": 25, "passed": True, "reason": "transaction_id is 12345"})
        total_score += 25
    elif isinstance(txn, int):
        details.append({"item": "transaction_id is correct", "score": 0, "max_score": 25, "passed": False, "reason": f"expected 12345, got {txn}"})
    else:
        details.append({"item": "transaction_id is correct", "score": 0, "max_score": 25, "passed": False, "reason": f"transaction_id is not an integer, got {type(txn).__name__}"})

    # 分值总计
    if total_score > 100:
        total_score = 100
    final = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
