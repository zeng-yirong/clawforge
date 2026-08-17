import json
import os
import sys
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. 检查结果文件是否存在 (10分)
    result_path = ws / "reports" / "performance_summary.json"
    if result_path.exists():
        details.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "reports/performance_summary.json 存在"})
        total_score += 10
    else:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查无法进行，直接输出
        _write_score(ws, total_score, details)
        return

    # 2. 检查JSON合法性 (10分)
    try:
        with open(result_path) as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        _write_score(ws, total_score, details)
        return

    # 3. 检查结果是否为数组 (5分)
    if isinstance(data, list):
        details.append({"item": "结果类型为数组", "score": 5, "max_score": 5, "passed": True, "reason": "顶层是数组"})
        total_score += 5
    else:
        details.append({"item": "结果类型为数组", "score": 0, "max_score": 5, "passed": False, "reason": f"顶层类型 {type(data).__name__}"})

    # 4. 检查员工数量（应为4，不包括无产出记录的E005） (10分)
    expected_count = 4
    if len(data) == expected_count:
        details.append({"item": "员工数量正确", "score": 10, "max_score": 10, "passed": True, "reason": f"包含 {expected_count} 名员工"})
        total_score += 10
    else:
        details.append({"item": "员工数量正确", "score": 0, "max_score": 10, "passed": False, "reason": f"实际 {len(data)} 人，期望 {expected_count} 人"})

    # 5. 检查每个条目的字段完整性 (10分)
    field_ok = True
    for idx, entry in enumerate(data):
        if not all(k in entry for k in ("employee_id", "total_score", "grade")):
            field_ok = False
            details.append({"item": f"条目 {idx} 字段完整", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少必要字段: {entry.keys()}"})
            break
    if field_ok:
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有条目包含 employee_id, total_score, grade"})
        total_score += 10
    else:
        # 已经添加了失败明细，但确保分数为0
        details = [d for d in details if d["item"] != "字段完整性"] + [{"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "部分条目缺少字段"}]

    # 6. 读取原始数据并计算期望结果 (50分，分布到每个员工)
    # 加载员工
    emp_path = ws / "data" / "employees" / "employees.json"
    with open(emp_path) as f:
        emp_data = json.load(f)["employees"]
    emp_map = {e["employee_id"]: e for e in emp_data}

    # 加载产出记录
    out_path = ws / "data" / "ledgers" / "monthly_outputs.json"
    with open(out_path) as f:
        out_data = json.load(f)["monthly_outputs"]
    out_map = {o["employee_id"]: o for o in out_data}

    # 加载规则
    rule_path = ws / "data" / "rules" / "scoring_rules.json"
    with open(rule_path) as f:
        rule_data = json.load(f)["scoring_rules"]
    rule_map = {r["role_code"]: r for r in rule_data}

    # 计算期望结果（只计算有产出记录的员工）
    expected = {}
    for eid, emp in emp_map.items():
        if eid not in out_map:
            continue
        out = out_map[eid]
        rule = rule_map[emp["role_code"]]
        total = (out["feature_delivery"] * rule["feature_delivery_weight"] +
                 out["quality_score"] * rule["quality_weight"] +
                 out["collaboration_score"] * rule["collaboration_weight"])
        total_rounded = round(total, 1)
        if total_rounded >= 80:
            grade = "优秀"
        elif total_rounded >= 60:
            grade = "良好"
        else:
            grade = "待改进"
        expected[eid] = {"total_score": total_rounded, "grade": grade}

    # 将结果数据转为 dict 以便比对
    actual = {e["employee_id"]: e for e in data}

    # 逐员工检查分数和等级
    staff_score_total = 0
    for eid, exp in expected.items():
        if eid not in actual:
            details.append({"item": f"员工 {eid} 结果存在", "score": 0, "max_score": 12.5, "passed": False, "reason": "缺失"})
            continue
        act = actual[eid]
        # 分数匹配（允许 0.01 浮点误差）
        if abs(act.get("total_score", -1) - exp["total_score"]) < 0.01:
            score_score = 10
        else:
            score_score = 0
        # 等级匹配
        if act.get("grade") == exp["grade"]:
            grade_score = 2.5
        else:
            grade_score = 0
        item_score = score_score + grade_score
        staff_score_total += item_score
        passed = (item_score == 12.5)
        reason = f"期望 total_score={exp['total_score']}, grade={exp['grade']}; 实际 total_score={act.get('total_score')}, grade={act.get('grade')}"
        details.append({
            "item": f"员工 {eid} 结果正确",
            "score": item_score,
            "max_score": 12.5,
            "passed": passed,
            "reason": reason
        })
        total_score += item_score

    # 检查是否有额外员工（不应该有 E005 或其他）
    extra_ids = set(actual.keys()) - set(expected.keys())
    if extra_ids:
        details.append({
            "item": "无多余员工",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"出现了未预期的员工ID: {extra_ids}"
        })
        # 不扣分（因为我们已经从字段完整性和数量上限制了），但记录

    # 写入最终得分
    final_score = round(total_score)
    final_score = min(final_score, 100)
    _write_score(ws, final_score, details)

def _write_score(ws: Path, total: int, details: list):
    result = {
        "total_score": total,
        "details": details
    }
    score_path = ws / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
