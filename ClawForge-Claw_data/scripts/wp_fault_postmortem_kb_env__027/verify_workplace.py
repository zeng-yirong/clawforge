import os
import sys
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # Paths
    report_path = os.path.join(workspace, "ops", "postmortem.json")
    fault_cases_path = os.path.join(workspace, "data", "faults", "fault_cases.json")
    payment_log_path = os.path.join(workspace, "attachments", "payment_slow_query.log")

    # ---------- 1. 检查报告文件存在 (10分) ----------
    item = {"item": "Report file exists", "max_score": 10}
    if os.path.isfile(report_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Found ops/postmortem.json"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "File ops/postmortem.json not found"
        results.append(item)
        # 如果文件不存在，直接结束，后续无法验证
        total_score = 0
        dump_score(total_score, results)
        return
    results.append(item)
    total_score += 10

    # ---------- 2. 解析报告 JSON 合法性 (10分) ----------
    item = {"item": "Report JSON is valid and has required fields", "max_score": 10}
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Invalid JSON: {e}"
        results.append(item)
        dump_score(total_score, results)
        return

    required_fields = ["fault_id", "root_cause", "repair_plan", "triggered_at"]
    missing = [f for f in required_fields if f not in report]
    if missing:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Missing fields: {', '.join(missing)}"
        results.append(item)
        dump_score(total_score, results)
        return
    else:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "All required fields present"
    results.append(item)
    total_score += 10

    # ---------- 3. 从原始数据中提取正确答案 ----------
    # 读取 fault_cases.json 找到目标 case (service_name = "payment")
    try:
        with open(fault_cases_path, "r") as f:
            fault_data = json.load(f)
    except Exception as e:
        item = {"item": "Read fault cases", "max_score": 0, "score": 0, "passed": False,
                "reason": f"Cannot read fault cases: {e}"}
        results.append(item)
        dump_score(total_score, results)
        return

    target_case = None
    for case in fault_data.get("fault_cases", []):
        if case.get("service_name") == "payment":
            target_case = case
            break
    if target_case is None:
        item = {"item": "Find payment case", "max_score": 0, "score": 0, "passed": False,
                "reason": "No payment fault case found"}
        results.append(item)
        dump_score(total_score, results)
        return

    expected_fault_id = target_case["fault_id"]
    expected_root_cause = target_case["root_cause_hint"]
    expected_repair_plan = target_case["repair_plan_hint"]
    expected_transaction_id = target_case["transaction_id"]

    # 从 payment_slow_query.log 中提取与 transaction_id 对应的行的时间戳
    try:
        with open(payment_log_path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        item = {"item": "Read payment log", "max_score": 0, "score": 0, "passed": False,
                "reason": f"Cannot read payment log: {e}"}
        results.append(item)
        dump_score(total_score, results)
        return

    expected_triggered_at = None
    pattern = re.compile(r'^(\S+\s+\S+)\s+\[payment\]\s+\[(' + re.escape(expected_transaction_id) + r')\]')
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            expected_triggered_at = match.group(1)
            break
    if expected_triggered_at is None:
        item = {"item": "Extract timestamp from log", "max_score": 0, "score": 0, "passed": False,
                "reason": f"Could not find line with transaction_id {expected_transaction_id}"}
        results.append(item)
        dump_score(total_score, results)
        return

    # ---------- 4. 逐个字段比对 (每个20分, 共80分) ----------
    field_checks = [
        ("fault_id", expected_fault_id, report.get("fault_id")),
        ("root_cause", expected_root_cause, report.get("root_cause")),
        ("repair_plan", expected_repair_plan, report.get("repair_plan")),
        ("triggered_at", expected_triggered_at, report.get("triggered_at")),
    ]
    for field_name, expected, actual in field_checks:
        item = {"item": f"Field '{field_name}' correct", "max_score": 20}
        if actual == expected:
            item["score"] = 20
            item["passed"] = True
            item["reason"] = f"Exact match: {repr(expected)}"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"Expected {repr(expected)}, got {repr(actual)}"
        results.append(item)
        total_score += item["score"]

    # 写入最终结果
    dump_score(total_score, results)

def dump_score(total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    print(json.dumps(output, indent=2))
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
