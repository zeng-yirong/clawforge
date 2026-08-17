import os
import sys
import json

def verify(workspace):
    errors = []
    details = []
    total_score = 0

    # ---------- 检查 ops 目录 ----------
    ops_path = os.path.join(workspace, "ops")
    if not os.path.isdir(ops_path):
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "目录 ops/ 不存在"})
        # 如果目录都不存在，直接返回
        return {"total_score": 0, "details": details}
    else:
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录存在"})
        total_score += 10

    # ---------- 检查 postmortem_report.json 是否存在 ----------
    report_path = os.path.join(workspace, "ops", "postmortem_report.json")
    if not os.path.isfile(report_path):
        details.append({"item": "report file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/postmortem_report.json 文件不存在"})
        return {"total_score": total_score, "details": details}
    else:
        details.append({"item": "report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件存在"})
        total_score += 10

    # ---------- 解析 JSON ----------
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        details.append({"item": "JSON 合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        return {"total_score": total_score, "details": details}
    else:
        details.append({"item": "JSON 合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式正确"})
        total_score += 10

    # ---------- 检查必填字段 ----------
    required_fields = ["fault_id", "root_cause", "repair_plan", "contact_name"]
    missing = [f for f in required_fields if f not in report]
    if missing:
        details.append({"item": "必填字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {', '.join(missing)}"})
        return {"total_score": total_score, "details": details}
    else:
        details.append({"item": "必填字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有必填字段存在"})
        total_score += 20

    # ---------- 检查 fault_id ----------
    if report["fault_id"] != "fault_007":
        details.append({"item": "fault_id 正确性", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 'fault_007'，实际 '{report['fault_id']}'"})
    else:
        details.append({"item": "fault_id 正确性", "score": 15, "max_score": 15, "passed": True, "reason": "故障 ID 正确"})
        total_score += 15

    # ---------- 检查 root_cause ----------
    expected_root_cause = "Deadlock in payment transaction"
    if report["root_cause"] != expected_root_cause:
        details.append({"item": "root_cause 准确性", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 '{expected_root_cause}'，实际 '{report['root_cause']}'"})
    else:
        details.append({"item": "root_cause 准确性", "score": 15, "max_score": 15, "passed": True, "reason": "根本原因正确"})
        total_score += 15

    # ---------- 检查 repair_plan ----------
    expected_repair = "Rollback and retry with timeout"
    if report["repair_plan"] != expected_repair:
        details.append({"item": "repair_plan 准确性", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 '{expected_repair}'，实际 '{report['repair_plan']}'"})
    else:
        details.append({"item": "repair_plan 准确性", "score": 15, "max_score": 15, "passed": True, "reason": "修复方案正确"})
        total_score += 15

    # ---------- 检查 contact_name ----------
    expected_contact = "Alice"
    if report["contact_name"] != expected_contact:
        details.append({"item": "contact_name 准确性", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 '{expected_contact}'，实际 '{report['contact_name']}'"})
    else:
        details.append({"item": "contact_name 准确性", "score": 10, "max_score": 10, "passed": True, "reason": "联系人正确"})
        total_score += 10

    # ---------- 不允许额外字段（可选，从严） ----------
    # 这里我们不扣分，仅记录合理性

    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {result['total_score']}")
