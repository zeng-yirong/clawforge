"""
Verifier for wp_smart_home_envs__046: Smart Home Health Conflict Report.
Checks that agent produced ops/conflict_report.json with correct conflicts.
"""
import sys
import json
import os
from pathlib import Path

def verify(workspace):
    workspace = Path(workspace)
    detail = []
    total_score = 0
    max_total = 100

    # 1. 检查结果文件是否存在 (10分)
    report_path = workspace / "ops" / "conflict_report.json"
    if report_path.exists():
        detail.append({"item": "ops/conflict_report.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
        total_score += 10
    else:
        detail.append({"item": "ops/conflict_report.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing."})
        # 如果文件不存在，后续无法检查，直接返回
        final_score = 0
        output = {"total_score": final_score, "details": detail}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        return

    # 2. JSON合法性 (10分)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        detail.append({"item": "JSON parse valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON."})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        detail.append({"item": "JSON parse valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        final_score = 10  # 只有存在得分
        output = {"total_score": final_score, "details": detail}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        return

    # 3. 报告结构：必须是列表 (5分)
    if isinstance(report, list):
        detail.append({"item": "Report is a list", "score": 5, "max_score": 5, "passed": True, "reason": "Top-level list."})
        total_score += 5
    else:
        detail.append({"item": "Report is a list", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected list, got {type(report).__name__}."})

    # 4. 冲突条目数量：必须恰好2个 (20分)
    expected_conflicts = [
        {"device_id": "bd-hum-01", "conflict_type": "humidity", "current_value": 30, "recommended_range": "45-55"},
        {"device_id": "lr-ac-01", "conflict_type": "temperature", "current_value": 20, "recommended_range": "24-28"}
    ]
    # 宽松检查：允许字段名稍有不同，但核心信息必须匹配
    if len(report) != 2:
        detail.append({"item": "Number of conflicts is 2", "score": 0, "max_score": 20, "passed": False, "reason": f"Found {len(report)} conflicts, expected 2."})
    else:
        # 逐个比对，不要求顺序
        def match_entry(entry, target):
            # 检查device_id
            if entry.get("device_id") != target["device_id"]:
                return False
            # 检查冲突类型
            ct = entry.get("conflict_type") or entry.get("type") or ""
            if ct.lower() != target["conflict_type"]:
                return False
            # 检查当前值
            cv = entry.get("current_value")
            if cv is None:
                cv = entry.get("current")
            if cv is None:
                cv = entry.get("value")
            try:
                cv = float(cv)
            except:
                return False
            if abs(cv - target["current_value"]) > 0.5:
                return False
            # 检查推荐范围 (可以是字符串或列表)
            rec = entry.get("recommended_range") or entry.get("recommended") or entry.get("range") or ""
            # 期望包含数字45和55或24和28等
            if target["conflict_type"] == "humidity":
                if "45" not in str(rec) or "55" not in str(rec):
                    return False
            else:
                if "24" not in str(rec) or "28" not in str(rec):
                    return False
            return True

        matched = 0
        for t in expected_conflicts:
            for e in report:
                if match_entry(e, t):
                    matched += 1
                    break
        if matched == 2:
            detail.append({"item": "Conflict records match expected", "score": 20, "max_score": 20, "passed": True, "reason": "Both conflicts correctly identified."})
            total_score += 20
        else:
            detail.append({"item": "Conflict records match expected", "score": 0, "max_score": 20, "passed": False, "reason": f"Only {matched}/2 conflicts matched expected."})

    # 5. 没有额外无关冲突 (5分) — 检查是否包含了不应存在的设备
    valid_device_ids = {"bd-hum-01", "lr-ac-01"}
    extra = [e for e in report if e.get("device_id") not in valid_device_ids]
    if extra:
        detail.append({"item": "No extra devices in report", "score": 0, "max_score": 5, "passed": False, "reason": f"Found unexpected devices: {[e['device_id'] for e in extra]}"})
    else:
        detail.append({"item": "No extra devices in report", "score": 5, "max_score": 5, "passed": True, "reason": "All reported devices are expected."})
        total_score += 5

    # 6. 每个冲突记录包含必要字段：device_id, conflict_type, current_value, recommended_range (10分)
    required_fields = {"device_id", "conflict_type", "current_value", "recommended_range"}
    all_have = True
    for i, entry in enumerate(report):
        # 允许字段名变体
        fields = set(entry.keys())
        # 规范化检查
        has_device_id = "device_id" in fields
        has_ct = ("conflict_type" in fields) or ("type" in fields)
        has_cv = ("current_value" in fields) or ("current" in fields) or ("value" in fields)
        has_rec = ("recommended_range" in fields) or ("recommended" in fields) or ("range" in fields)
        if not (has_device_id and has_ct and has_cv and has_rec):
            all_have = False
            break
    if all_have:
        detail.append({"item": "Required fields present in all entries", "score": 10, "max_score": 10, "passed": True, "reason": "All entries have device_id, conflict_type, current_value, recommended_range."})
        total_score += 10
    else:
        detail.append({"item": "Required fields present in all entries", "score": 0, "max_score": 10, "passed": False, "reason": "Some entries missing required fields."})

    # 7. 其他：确保报告文件只包含这两个冲突，没有多余记录 (0分，但扣分)
    # 我们已经通过5检查了额外设备，这里不重复

    # 计算总分，确保不超过100
    final_score = min(total_score, 100)
    output = {"total_score": final_score, "details": detail}
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
