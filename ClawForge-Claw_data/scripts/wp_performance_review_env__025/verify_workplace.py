import json
import os
import sys
import math

def round_score(val):
    """四舍五入到两位小数"""
    return round(val, 2)

def compute_expected():
    """根据env_builder的数据计算预期结果"""
    # 有效员工
    employees = {
        "E001": {"name": "李明", "role": "ENG"},
        "E002": {"name": "王芳", "role": "SALES"},
        "E003": {"name": "张伟", "role": "MGR"},
    }
    # 有效产出
    outputs = {
        "E001": {"f": 85, "q": 90, "c": 78},
        "E002": {"f": 70, "q": 65, "c": 80},
        "E003": {"f": 92, "q": 88, "c": 95},
    }
    # 有效规则
    rules = {
        "ENG":  {"f": 0.5, "q": 0.3, "c": 0.2},
        "SALES":{"f": 0.2, "q": 0.3, "c": 0.5},
        "MGR":  {"f": 0.4, "q": 0.4, "c": 0.2},
    }
    expected = {}
    for eid, emp in employees.items():
        r = rules[emp["role"]]
        out = outputs[eid]
        score = out["f"] * r["f"] + out["q"] * r["q"] + out["c"] * r["c"]
        expected[eid] = {
            "employee_id": eid,
            "employee_name": emp["name"],
            "role_code": emp["role"],
            "total_score": round_score(score)
        }
    return expected

def verify(workspace):
    expected = compute_expected()
    expected_ids = {"E001", "E002", "E003"}
    
    details = []
    total_score = 0
    max_total = 100
    
    # 1. 检查 ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录已创建"})
        total_score += 10
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在"})
        # 如果目录都不存在，后续检查全失败
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录缺失"})
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "员工数量正确", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        details.append({"item": "分数计算正确", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在"})
        write_score(details, total_score, max_total, workspace)
        return

    # 2. 检查结果文件存在 (10分)
    result_file = os.path.join(ops_dir, "performance_summary.json")
    if os.path.isfile(result_file):
        details.append({"item": "结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "performance_summary.json 存在"})
        total_score += 10
    else:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "员工数量正确", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        details.append({"item": "分数计算正确", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在"})
        write_score(details, total_score, max_total, workspace)
        return

    # 3. 检查JSON格式合法 (10分)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        # 支持两种可能：直接列表，或者字典包含列表
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            # 常见包装 key 如 "performance_summary" 或 "results"
            for key in data:
                if isinstance(data[key], list):
                    records = data[key]
                    break
            else:
                records = []  # 无有效列表
        else:
            records = []
        if not isinstance(records, list):
            records = []
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可解析为JSON，包含数组"})
        total_score += 10
    except (json.JSONDecodeError, ValueError, TypeError):
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "JSON解析失败"})
        details.append({"item": "员工数量正确", "score": 0, "max_score": 30, "passed": False, "reason": "数据无法解析"})
        details.append({"item": "分数计算正确", "score": 0, "max_score": 40, "passed": False, "reason": "数据无法解析"})
        write_score(details, total_score, max_total, workspace)
        return

    # 4. 检查员工数量及字段正确性 (30分)
    # 提取有效员工ID集合
    found_ids = set()
    score_penalty = 0
    for rec in records:
        eid = rec.get("employee_id")
        if eid and eid in expected:
            found_ids.add(eid)
        else:
            # 包含干扰员工，扣分
            score_penalty += 5
    # 期望ID必须全部出现
    missing = expected_ids - found_ids
    extra = found_ids - expected_ids
    if len(missing) == 0 and len(extra) == 0:
        count_score = 30
        reason = "正好包含3个正确员工，无多余"
    else:
        # 每缺少一个扣10分，每多一个扣5分（最多扣到0）
        deductions = len(missing) * 10 + len(extra) * 5
        count_score = max(0, 30 - deductions)
        reason = f"缺少 {len(missing)} 个预期员工，多出 {len(extra)} 个无关员工"
    # 再加上字段完整性检查（每个员工必须包含四种字段）
    field_ok = True
    for rec in records:
        if rec.get("employee_id") in expected:
            if not all(k in rec for k in ["employee_id", "employee_name", "role_code", "total_score"]):
                field_ok = False
                reason += "；部分记录缺少必要字段"
                break
    if field_ok:
        details.append({"item": "员工数量与字段完整性", "score": count_score, "max_score": 30, "passed": count_score >= 20, "reason": reason})
    else:
        details.append({"item": "员工数量与字段完整性", "score": 0, "max_score": 30, "passed": False, "reason": "字段缺失"})
    total_score += count_score

    # 5. 分数计算正确性 (40分)
    calc_score = 0
    max_calc = 40
    per_correct = max_calc // len(expected_ids)  # 约13.33，我们按13、13、14分配
    per_scores = {eid: (13 if i < 2 else 14) for i, eid in enumerate(sorted(expected_ids))}  # 简单分配
    calc_pass = True
    for rec in records:
        eid = rec.get("employee_id")
        if eid in expected:
            exp = expected[eid]
            # tolerance 0.01
            if abs(rec.get("total_score", -1) - exp["total_score"]) <= 0.01:
                calc_score += per_scores[eid]
            else:
                calc_pass = False
                reason = f"{eid} 分数错误：期望 {exp['total_score']}，得到 {rec.get('total_score')}"
    for missing_eid in missing:
        calc_pass = False
        reason = f"缺少 {missing_eid} 的分数"
    if calc_score == max_calc:
        reason = "所有员工分数完全正确"
    else:
        reason = f"部分分数错误，得分 {calc_score}/{max_calc}"
    details.append({"item": "分数计算正确性", "score": calc_score, "max_score": max_calc, "passed": calc_score == max_calc, "reason": reason})
    total_score += calc_score

    # 写入结果
    write_score(details, total_score, max_total, workspace)

def write_score(details, total, max_total, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"评分完成：总分 {total}/{max_total}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
