import json
import os
import sys
from pathlib import Path

def grade(workspace: str) -> dict:
    score = 0
    details = []
    ws = Path(workspace)

    # 1. 目录与文件存在 (10分)
    report_path = ws / "reports" / "performance_scores.json"
    if report_path.exists():
        details.append({"item": "reports/performance_scores.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        score += 10
    else:
        details.append({"item": "reports/performance_scores.json exists", "score": 0, "max_score": 10, "passed": False, "reason": f"文件不存在 ({report_path})"})
        return {"total_score": 0, "details": details}

    # 2. JSON 合法性 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "合法 JSON"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        return {"total_score": score, "details": details}

    # 3. 必须是列表 (5分)
    if isinstance(data, list):
        details.append({"item": "根结构为列表", "score": 5, "max_score": 5, "passed": True, "reason": "是列表"})
        score += 5
    else:
        details.append({"item": "根结构为列表", "score": 0, "max_score": 5, "passed": False, "reason": f"类型为 {type(data).__name__}"})
        # 继续检查，但已扣分

    # 4. 包含的正确员工 (20分)
    # 预期三个员工：E001 Alice, E002 Bob, E003 Carol
    # 注意：E004 (David) 没有output, E005 没有员工记录，都不应出现
    expected_ids = {"E001", "E002", "E003"}
    if isinstance(data, list):
        actual_ids = {item.get("employee_id") for item in data if isinstance(item, dict)}
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        if not missing and not extra:
            details.append({"item": "包含正确的员工集合", "score": 20, "max_score": 20, "passed": True, "reason": "仅包含E001,E002,E003"})
            score += 20
        else:
            reason_parts = []
            if missing:
                reason_parts.append(f"缺少: {missing}")
            if extra:
                reason_parts.append(f"多余: {extra}")
            details.append({"item": "包含正确的员工集合", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reason_parts)})
    else:
        details.append({"item": "包含正确的员工集合", "score": 0, "max_score": 20, "passed": False, "reason": "data不是列表"})

    # 5. 每条记录字段完整性 (10分)
    if isinstance(data, list):
        missing_fields = []
        for item in data:
            if not isinstance(item, dict):
                continue
            for field in ("employee_id", "name", "department", "total_score", "grade"):
                if field not in item:
                    missing_fields.append(f"item {item.get('employee_id','?')} 缺少字段 {field}")
        if not missing_fields:
            details.append({"item": "所有记录包含必需字段", "score": 10, "max_score": 10, "passed": True, "reason": "字段齐全"})
            score += 10
        else:
            details.append({"item": "所有记录包含必需字段", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(missing_fields)})

    # 6. 计算得分与等级 (30分 + 10分 = 40分)
    # 预期结果：
    # Carol: 95*0.4 + 95*0.4 + 95*0.2 = 38+38+19 = 95 -> A
    # Alice: 90*0.4 + 90*0.4 + 90*0.2 = 36+36+18 = 90 -> A
    # Bob:   70*0.3 + 85*0.5 + 90*0.2 = 21+42.5+18 = 81.5 -> B
    # 排序：按总分降序 => Carol, Alice, Bob
    expected = [
        {"employee_id": "E003", "name": "Carol", "department": "Engineering", "total_score": 95.0, "grade": "A"},
        {"employee_id": "E001", "name": "Alice", "department": "Engineering", "total_score": 90.0, "grade": "A"},
        {"employee_id": "E002", "name": "Bob",   "department": "QA",         "total_score": 81.5, "grade": "B"},
    ]
    if isinstance(data, list) and len(data) == 3:
        # 先按employee_id建立映射
        actual_map = {}
        for item in data:
            if isinstance(item, dict):
                actual_map[item.get("employee_id")] = item

        # 检查每个预期员工
        calc_ok = True
        for exp in expected:
            act = actual_map.get(exp["employee_id"])
            if act is None:
                calc_ok = False
                continue
            # 检查总分（保留一位小数比较，允许微小浮点误差）
            try:
                actual_score = float(act["total_score"])
            except:
                calc_ok = False
                continue
            expected_score = exp["total_score"]
            if abs(actual_score - expected_score) > 0.01:
                calc_ok = False
            # 检查等级
            if act.get("grade") != exp["grade"]:
                calc_ok = False

        if calc_ok:
            details.append({"item": "总分与等级计算正确", "score": 30, "max_score": 30, "passed": True, "reason": "所有员工计算结果匹配"})
            score += 30
        else:
            details.append({"item": "总分与等级计算正确", "score": 0, "max_score": 30, "passed": False, "reason": "至少一个员工的分数或等级不符预期"})
    else:
        details.append({"item": "总分与等级计算正确", "score": 0, "max_score": 30, "passed": False, "reason": f"记录数量={len(data) if isinstance(data, list) else 0}, 预期3"})

    # 7. 排序 (10分)
    if isinstance(data, list) and len(data) >= 2:
        scores_order = []
        for item in data:
            try:
                scores_order.append(float(item.get("total_score", 0)))
            except:
                scores_order.append(0)
        sorted_ok = all(scores_order[i] >= scores_order[i+1] for i in range(len(scores_order)-1))
        if sorted_ok:
            details.append({"item": "按总分降序排序", "score": 10, "max_score": 10, "passed": True, "reason": "顺序正确"})
            score += 10
        else:
            details.append({"item": "按总分降序排序", "score": 0, "max_score": 10, "passed": False, "reason": "顺序不是降序"})
    else:
        details.append({"item": "按总分降序排序", "score": 0, "max_score": 10, "passed": False, "reason": "数据不足排序"})

    total = min(score, 100)
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = grade(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100 written to workplace_score.json")
