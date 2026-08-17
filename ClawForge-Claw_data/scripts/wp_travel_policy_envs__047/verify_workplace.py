import json
import os
import sys
import datetime
from pathlib import Path

def check_file_exists(ws: Path, rel_path: str) -> bool:
    return (ws / rel_path).exists()

def load_json(ws: Path, rel_path: str):
    with open(ws / rel_path, 'r') as f:
        return json.load(f)

def main():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (10分)
    dirs_ok = True
    for d in ["policies", "requests", "ops"]:
        if not (workspace / d).is_dir():
            details.append({"item": f"Directory '{d}' exists", "score": 0, "max_score": 3, "passed": False, "reason": f"Missing directory {d}"})
            total_score += 0
            dirs_ok = False
        else:
            details.append({"item": f"Directory '{d}' exists", "score": 3, "max_score": 3, "passed": True, "reason": "Exists"})
            total_score += 3
    # 额外：ops 下应该没有 temp_notes.txt (已经在env里创建了，但agent不应该删除，但我们不检查agent删除，只检查报告存在)
    # 这里我们不扣分。

    # 2. 产物文件 ops/compliance_report.json 存在且合法JSON (15分)
    report_path = workspace / "ops" / "compliance_report.json"
    if not report_path.exists():
        details.append({"item": "ops/compliance_report.json exists", "score": 0, "max_score": 15, "passed": False, "reason": "File not found"})
        total_score += 0
        print_score(details, total_score, max_total)
        return
    else:
        # 尝试解析JSON
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            details.append({"item": "ops/compliance_report.json is valid JSON", "score": 15, "max_score": 15, "passed": True, "reason": "Valid JSON"})
            total_score += 15
        except json.JSONDecodeError as e:
            details.append({"item": "ops/compliance_report.json is valid JSON", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON parse error: {e}"})
            total_score += 0
            print_score(details, total_score, max_total)
            return

    # 3. 检查 report 格式：必须是 list 或 dict。我们期望list of violation objects (灵活)
    if not isinstance(report, list) and not isinstance(report, dict):
        details.append({"item": "Report structure is list or dict", "score": 0, "max_score": 5, "passed": False, "reason": "Invalid structure type"})
        total_score += 0
    else:
        details.append({"item": "Report structure is list or dict", "score": 5, "max_score": 5, "passed": True, "reason": "Valid structure"})
        total_score += 5

    # 4. 提取不合规请求ID列表 (需要从report中解析，支持两种格式)
    # 如果report是dict，取键；如果是list，每个元素应有request_id或类似键
    violations = []
    if isinstance(report, list):
        for item in report:
            if isinstance(item, dict) and "request_id" in item:
                violations.append(item["request_id"])
            elif isinstance(item, dict) and "id" in item:
                violations.append(item["id"])
    elif isinstance(report, dict):
        # 假设键是request_id
        violations = list(report.keys())

    # 预期不合规列表：基于env_builder数据计算
    # 我们手动计算——当前政策 v2.1:
    # max_cost_per_booking = 3500
    # max_single_booking_cost = 1800
    # allowed_cabin_classes = ["economy", "premium_economy", "business"]
    # min_advance_booking_days = 7  (假设当前日期为2026-05-20)
    # restricted_routes: [["JFK","LHR"]] 但政策未明确禁止，只是需要特殊审批？这里为了简化，我们不认为它是违反。
    # 违反条件：
    #   - total_cost > 3500 (per booking) 或 > 1800 (single?)
    #   - cabin_class not in allowed
    #   - (departure_date - today) < 7 days
    #   - 注意：单次预订成本 max_single_booking_cost 似乎也是限制项，我们视为单个行程费用上限。REQ-002 total=2000>1800违反；REQ-009 total=4000>3500违反；REQ-003 departure 2026-05-25 提前5天 <7违反；REQ-005 cabin first_class 不允许；REQ-008 departure 2026-05-22 提前2天 <7违反；其他合规。
    # 所以期望违规: REQ-002, REQ-003, REQ-005, REQ-008, REQ-009
    expected_violations = {"REQ-002", "REQ-003", "REQ-005", "REQ-008", "REQ-009"}
    # 额外：REQ-006 航线受限但未明确禁止，不视为违规；REQ-004 total=3500 == max_cost，合规。
    # 注意：REQ-001 cabin business允许，且total<1800，提前12天>7，合规。

    # 检查是否包含所有预期违规并且没有多余违规（允许有多余？但验证严格，多余扣分，缺少扣分）
    found_set = set(violations)
    missing = expected_violations - found_set
    extra = found_set - expected_violations
    # 先检查缺失 (最重要)
    if missing:
        details.append({"item": "Correctly identifies all violating requests", "score": 0, "max_score": 30, "passed": False, "reason": f"Missing violations: {missing}"})
        total_score += 0
    else:
        if extra:
            # 有额外违规，扣部分分
            details.append({"item": "Correctly identifies all violating requests", "score": 20, "max_score": 30, "passed": False, "reason": f"Extra violations found: {extra}"})
            total_score += 20
        else:
            details.append({"item": "Correctly identifies all violating requests", "score": 30, "max_score": 30, "passed": True, "reason": "Exact match"})
            total_score += 30

    # 5. 每个违规条目至少包含一个reason字段或描述理由 (10分)
    reason_count = 0
    if isinstance(report, list):
        for item in report:
            if isinstance(item, dict) and ("reason" in item or "violation" in item or "description" in item):
                reason_count += 1
    elif isinstance(report, dict):
        for k, v in report.items():
            if isinstance(v, dict) and ("reason" in v or "violation" in v or "description" in v):
                reason_count += 1
    if reason_count >= len(expected_violations):
        details.append({"item": "Each violation entry includes a reason", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {reason_count} reasons"})
        total_score += 10
    else:
        details.append({"item": "Each violation entry includes a reason", "score": 0, "max_score": 10, "passed": False, "reason": f"Only {reason_count} entries have reason"})
        total_score += 0

    # 6. 没有使用旧政策文件 (检查是否引用了非current policy, 但报告里不包含政策ID? 我们不做严格检查)
    # 额外项：检查是否没有把合规的REQ-001等误报
    false_positives = found_set - expected_violations
    if false_positives:
        details.append({"item": "No false positives (compliant requests wrongly flagged)", "score": 0, "max_score": 10, "passed": False, "reason": f"False positives: {false_positives}"})
        total_score += 0
    else:
        details.append({"item": "No false positives", "score": 10, "max_score": 10, "passed": True, "reason": "No extra violations"})
        total_score += 10

    # 7. 报告中的请求ID格式应为REQ-XXX (5分)
    id_format_ok = all(isinstance(v, str) and v.startswith("REQ-") for v in violations)
    if id_format_ok:
        details.append({"item": "Request ID format is REQ-XXX", "score": 5, "max_score": 5, "passed": True, "reason": "All IDs match pattern"})
        total_score += 5
    else:
        details.append({"item": "Request ID format is REQ-XXX", "score": 0, "max_score": 5, "passed": False, "reason": "Some IDs do not match pattern"})
        total_score += 0

    # 计算剩余分数（如果前面有缺失严重，最多只能到70+，但我们尽量给满）
    # 此外，还有一些可选的扣分项：比如目录里不应该有temp_notes.txt（但agent不负责删除，不检查）
    # 写入结果
    final_score = min(total_score, 100)
    output = {
        "total_score": final_score,
        "details": details
    }
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score: {final_score}/100")

def print_score(details, total, max_total):
    output = {"total_score": total, "details": details}
    with open(Path(".") / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score: {total}/{max_total}")

if __name__ == "__main__":
    main()
