import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score_details = []
total_score = 0
max_total = 100

def check(condition, item_name, score, max_score, reason=""):
    global total_score
    detail = {
        "item": item_name,
        "score": score if condition else 0,
        "max_score": max_score,
        "passed": condition,
        "reason": reason if condition else f"Failed: {reason}"
    }
    score_details.append(detail)
    if condition:
        total_score += score

# 1. 检查必要目录是否存在 (10%)
dirs_to_check = ["ops"]
all_dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in dirs_to_check)
check(all_dirs_exist, "Required directories exist", 10, 10,
      "All mandatory directories (ops) found." if all_dirs_exist else "Missing ops/ directory")

# 2. 检查报告文件是否存在 (10%)
report_path = os.path.join(workspace, "ops", "postmortem_fault_003.json")
file_exists = os.path.isfile(report_path)
check(file_exists, "Report file ops/postmortem_fault_003.json exists", 10, 10,
      "File exists." if file_exists else "File not found.")

if not file_exists:
    # 提前结束，后面无法检查内容
    check(False, "Report content checks (skipped)", 0, 80, "File missing, cannot verify content.")
else:
    # 3. JSON 合法性 (10%)
    try:
        with open(report_path, "r") as f:
            report_data = json.load(f)
        check(True, "Report is valid JSON", 10, 10, "Valid JSON.")
    except (json.JSONDecodeError, Exception) as e:
        check(False, "Report is valid JSON", 0, 10, f"Invalid JSON: {e}")
        report_data = {}

    # 4. 报告字段完整性 (30%)
    required_fields = ["fault_id", "transaction_id", "repair_plan"]
    missing_fields = [f for f in required_fields if f not in report_data]
    fields_complete = len(missing_fields) == 0
    check(fields_complete, "Report has all required fields (fault_id, transaction_id, repair_plan)", 30, 30,
          f"All required fields present." if fields_complete else f"Missing fields: {missing_fields}")

    # 5. transaction_id 精确匹配 (30%)
    trx_ok = bool(report_data.get("transaction_id") == "98765")
    check(trx_ok, "transaction_id equals '98765'", 30, 30,
          f"transaction_id is {report_data.get('transaction_id')} (expected '98765')" if not trx_ok else "Correct transaction_id.")

    # 6. repair_plan 内容正确 (10%)
    if fields_complete:
        plan = report_data.get("repair_plan", "")
        # 验证方案是否来自知识库条目 KB-042 的核心内容
        expected_keywords = ["Kill", "session", "lock timeout"]
        plan_ok = all(kw.lower() in plan.lower() for kw in expected_keywords)
        check(plan_ok, "repair_plan contains appropriate solution from knowledge base", 10, 10,
              f"Repair plan: {plan[:80]}..." if not plan_ok else "Repair plan matches KB entry.")
    else:
        check(False, "repair_plan content check", 0, 10, "Fields incomplete, cannot verify plan.")

total_score = min(total_score, max_total)
output = {
    "total_score": total_score,
    "details": score_details
}

output_path = os.path.join(workspace, "workplace_score.json")
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)
