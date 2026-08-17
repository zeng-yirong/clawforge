import sys
import os
import json
import glob

def verify(workspace: str):
    total_score = 0
    details = []

    def add_item(name, score, max_score, passed, reason):
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. 检查 ops/reports/ 目录是否存在 [10分]
    reports_dir = os.path.join(workspace, "ops", "reports")
    if os.path.isdir(reports_dir):
        add_item("ops/reports/ directory exists", 10, 10, True, "Directory found")
        total_score += 10
    else:
        add_item("ops/reports/ directory exists", 0, 10, False, "Directory not found")
        # 后续无法检查，直接写结果并返回
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 检查是否存在且只有一个 .json 文件 [10分]
    json_files = glob.glob(os.path.join(reports_dir, "*.json"))
    if len(json_files) == 0:
        add_item("Exactly one JSON file in reports/", 0, 10, False, "No JSON file found")
        total_score += 0
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return
    elif len(json_files) > 1:
        add_item("Exactly one JSON file in reports/", 0, 10, False, f"Found {len(json_files)} files: {[os.path.basename(f) for f in json_files]}")
        total_score += 0
        # 继续尝试读取第一个文件，但可能不准确，这里简单返回
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return
    else:
        add_item("Exactly one JSON file in reports/", 10, 10, True, f"Found: {os.path.basename(json_files[0])}")
        total_score += 10

    report_path = json_files[0]

    # 3. JSON 格式合法性 [10分]
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        add_item("Valid JSON", 10, 10, True, "Parsed successfully")
        total_score += 10
    except Exception as e:
        add_item("Valid JSON", 0, 10, False, f"Invalid JSON: {e}")
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 必需字段存在 [各5分，共20分]
    required_fields = ["fault_id", "root_cause", "repair_plan", "analyst_email"]
    fields_ok = True
    for field in required_fields:
        if field in data:
            add_item(f"Field '{field}' exists", 5, 5, True, f"Present, value: {data[field]}")
            total_score += 5
        else:
            add_item(f"Field '{field}' exists", 0, 5, False, "Missing")
            fields_ok = False
    if not fields_ok:
        # 缺少字段直接写结果
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 5. fault_id 必须是 fault-001 [10分]
    if data["fault_id"] == "fault-001":
        add_item("fault_id is fault-001", 10, 10, True, "Correct")
        total_score += 10
    else:
        add_item("fault_id is fault-001", 0, 10, False, f"Got {data['fault_id']}")
        # 即使错误，继续检查其他字段，但给0分

    # 6. root_cause 精确匹配 [20分]
    expected_root_cause = "Database connection pool exhaustion due to missing timeout settings."
    if data.get("root_cause") == expected_root_cause:
        add_item("Root cause exact match", 20, 20, True, "Correct")
        total_score += 20
    else:
        add_item("Root cause exact match", 0, 20, False, f"Expected: {expected_root_cause!r}, got: {data.get('root_cause')!r}")

    # 7. repair_plan 精确匹配 [20分]
    expected_repair_plan = "Add connection timeout (5s) and max pool size limit (100)."
    if data.get("repair_plan") == expected_repair_plan:
        add_item("Repair plan exact match", 20, 20, True, "Correct")
        total_score += 20
    else:
        add_item("Repair plan exact match", 0, 20, False, f"Expected: {expected_repair_plan!r}, got: {data.get('repair_plan')!r}")

    # 8. analyst_email 精确匹配 [10分]
    expected_email = "alice@example.com"
    if data.get("analyst_email") == expected_email:
        add_item("Analyst email exact match", 10, 10, True, "Correct")
        total_score += 10
    else:
        add_item("Analyst email exact match", 0, 10, False, f"Expected: {expected_email!r}, got: {data.get('analyst_email')!r}")

    # 最终总分
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
