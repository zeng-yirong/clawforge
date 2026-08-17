import os
import sys
import json
from pathlib import Path
from datetime import datetime

def verify(workspace: str):
    scores = []
    total_max = 100

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = Path(workspace) / "ops"
    if ops_dir.is_dir():
        scores.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
    else:
        scores.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})
        # 如果目录不存在，后续检查直接给0分并返回
        result = {"total_score": 0, "details": scores}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 2. 检查 report.json 是否存在 (10分)
    report_file = ops_dir / "report.json"
    if report_file.is_file():
        scores.append({"item": "report.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "report.json found"})
    else:
        scores.append({"item": "report.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "report.json not found"})
        result = {"total_score": sum(s["score"] for s in scores), "details": scores}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(report_file, "r") as f:
            data = json.load(f)
        scores.append({"item": "report.json is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parsed OK"})
    except Exception as e:
        scores.append({"item": "report.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON error: {e}"})
        result = {"total_score": sum(s["score"] for s in scores), "details": scores}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 4. 检查必要字段 (4个字段各5分，共20分)
    required_fields = ["competitor", "year", "channel", "total_acquisition_cost"]
    field_scores = []
    for field in required_fields:
        if field in data:
            field_scores.append({"item": f"field '{field}' present", "score": 5, "max_score": 5, "passed": True, "reason": "found"})
        else:
            field_scores.append({"item": f"field '{field}' present", "score": 0, "max_score": 5, "passed": False, "reason": "missing"})
    scores.extend(field_scores)

    # 5. 检查字段值类型 (部分类型检查)
    type_checks = [
        ("competitor", str),
        ("year", int),
        ("channel", str),
        ("total_acquisition_cost", (int, float)),  # 允许int或float
    ]
    for field, expected_type in type_checks:
        if field in data:
            val = data[field]
            if isinstance(val, expected_type):
                scores.append({"item": f"field '{field}' type correct", "score": 5, "max_score": 5, "passed": True, "reason": f"type {type(val).__name__}"})
            else:
                scores.append({"item": f"field '{field}' type correct", "score": 0, "max_score": 5, "passed": False, "reason": f"expected {expected_type}, got {type(val).__name__}"})
        else:
            # 如果前面已扣分，这里也给0
            scores.append({"item": f"field '{field}' type correct", "score": 0, "max_score": 5, "passed": False, "reason": "field missing"})

    # 6. 关键计算：目标竞品 CloudMajor，年份2025，渠道 referral，总成本 = 500+800 = 1300 (40分)
    expected_competitor = "CloudMajor"
    expected_year = 2025
    expected_channel = "referral"
    expected_cost = 1300  # 500 + 800

    # 先从竞争文件列表中找出CloudMajor的ID（这里我们硬编码cm001，但Agent可能通过查找得到）
    # 但验证只关心最终数值，不关心Agent如何得到ID。我们只检查最终report.json中的数值。
    # 但为了严谨，我们可以允许不同的路径：只要数值正确即可。
    # 直接比对
    correct = True
    calc_reason = []

    # 检查 competitor 名称
    if data.get("competitor") != expected_competitor:
        correct = False
        calc_reason.append(f"competitor expected '{expected_competitor}', got '{data.get('competitor')}'")
    if data.get("year") != expected_year:
        correct = False
        calc_reason.append(f"year expected {expected_year}, got {data.get('year')}")
    if data.get("channel") != expected_channel:
        correct = False
        calc_reason.append(f"channel expected '{expected_channel}', got '{data.get('channel')}'")
    # 数值允许浮点数，但必须等于1300
    cost_val = data.get("total_acquisition_cost")
    if cost_val != expected_cost:
        correct = False
        calc_reason.append(f"total_acquisition_cost expected {expected_cost}, got {cost_val}")

    if correct:
        scores.append({"item": "final calculated values match expected", "score": 40, "max_score": 40, "passed": True, "reason": "all fields correct"})
    else:
        scores.append({"item": "final calculated values match expected", "score": 0, "max_score": 40, "passed": False, "reason": "; ".join(calc_reason)})

    # 计算总分
    total_score = sum(s["score"] for s in scores)
    result = {"total_score": total_score, "details": scores}
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
