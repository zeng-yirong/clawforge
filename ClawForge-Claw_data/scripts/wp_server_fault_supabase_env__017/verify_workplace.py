import sys
import os
import json
from datetime import datetime

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 检查目录结构
    report_path = os.path.join(workspace, "ops/remediation_report.json")
    if os.path.exists(report_path):
        details.append({"item": "ops/remediation_report.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        score += 5
    else:
        details.append({"item": "ops/remediation_report.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})

    # 解析 JSON
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        details.append({"item": "JSON 合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON 合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        report = []

    if not isinstance(report, list):
        details.append({"item": "顶层是数组", "score": 0, "max_score": 5, "passed": False, "reason": "顶层不是数组"})
        score += 0
    else:
        details.append({"item": "顶层是数组", "score": 5, "max_score": 5, "passed": True, "reason": "顶层是数组"})
        score += 5
        # 检查数目：应该正好处理 3 个 open 的 ups_outage/service_down 工单 (INC-001, INC-002, INC-003, INC-007)
        # 注意：INC-006 是 service_down 但 status=triaged，不处理；INC-007 是 ups_outage open，要处理
        expected_ids = {"INC-001", "INC-002", "INC-003", "INC-007"}
        reported_ids = {item.get("incident_id") for item in report if isinstance(item, dict)}
        # 检查必须包含所有预期ID，且没有额外ID（干扰项不应出现）
        if reported_ids == expected_ids:
            details.append({"item": "ID集合正确", "score": 20, "max_score": 20, "passed": True, "reason": f"包含所有预期ID，无多余ID: {sorted(reported_ids)}"})
            score += 20
        elif reported_ids.issuperset(expected_ids):
            extra = reported_ids - expected_ids
            details.append({"item": "ID集合包含多余项", "score": 10, "max_score": 20, "passed": False, "reason": f"包含额外ID: {extra}"})
            score += 10
        else:
            missing = expected_ids - reported_ids
            details.append({"item": "ID集合缺失", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失ID: {missing}"})
            score += 0

        # 检查每个记录的必要字段
        field_checks = 0
        for item in report:
            if not isinstance(item, dict):
                continue
            # action 必须为 batch_remediate
            if item.get("action") == "batch_remediate":
                field_checks += 1
            # timestamp 必须是 ISO 格式
            try:
                ts = item.get("timestamp")
                if ts:
                    datetime.fromisoformat(ts)
                    field_checks += 1
            except:
                pass
            # runbook_applied 必须包含 runbook_ups_and_service.md
            if "runbook_ups_and_service.md" in item.get("runbook_applied", ""):
                field_checks += 1
            # status 必须为 resolved
            if item.get("status") == "resolved":
                field_checks += 1
        # 每个记录最多4个字段，4个记录最多16分
        valid_fields_score = min(field_checks * 2, 30)  # 给满分30
        if valid_fields_score == 30:
            details.append({"item": "字段完整性", "score": 30, "max_score": 30, "passed": True, "reason": "所有记录的action/timestamp/runbook_applied/status均符合要求"})
        else:
            details.append({"item": "字段完整性", "score": valid_fields_score, "max_score": 30, "passed": False, "reason": f"部分字段缺失或格式错误，检查通过{field_checks}次"})
        score += valid_fields_score

    # 检查是否存在 ops 目录
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录存在"})
        score += 5
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "不存在"})

    # 检查是否有多余的其他报告文件（可选惩罚）—— 不做惩罚，只扫描

    total = min(score, max_score)
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/{max_score}")

if __name__ == "__main__":
    verify()
