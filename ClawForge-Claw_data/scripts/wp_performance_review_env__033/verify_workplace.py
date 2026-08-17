import sys
import json
import os
import math

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def check_result(workspace):
    details = []
    total_score = 0

    # ---------- 1. 检查 ops/performance_profile.json 是否存在 ----------
    expected_file = os.path.join(workspace, "ops", "performance_profile.json")
    if not os.path.isfile(expected_file):
        details.append({
            "item": "目标文件 ops/performance_profile.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 直接结束，后面的检查无法进行
        return details, 0
    else:
        details.append({
            "item": "目标文件 ops/performance_profile.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10

    # ---------- 2. 解析 JSON 并检查格式 ----------
    try:
        data = load_json(expected_file)
    except json.JSONDecodeError as e:
        details.append({
            "item": "文件是合法 JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        return details, total_score  # 终止，后面的无法解析

    if not isinstance(data, list):
        details.append({
            "item": "JSON 顶层是列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层不是列表"
        })
        return details, total_score

    details.append({
        "item": "JSON 格式合法且为列表",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "合法 JSON 列表"
    })
    total_score += 10

    # ---------- 3. 检查每条记录的必要字段 ----------
    required_keys = {"employee_id", "employee_name", "department", "total_score"}
    expected_employees = {
        "E001": {"name": "Alice", "dept": "Engineering", "score": 83.0},
        "E002": {"name": "Bob", "dept": "QA", "score": 81.5},
        "E003": {"name": "Charlie", "dept": "Product", "score": 82.0}
    }

    field_ok = True
    for idx, rec in enumerate(data):
        if not isinstance(rec, dict):
            details.append({
                "item": f"第 {idx+1} 条记录是字典",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "不是字典"
            })
            field_ok = False
            continue
        missing = required_keys - set(rec.keys())
        if missing:
            details.append({
                "item": f"第 {idx+1} 条记录包含所有必要字段",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"缺少字段: {missing}"
            })
            field_ok = False
        else:
            details.append({
                "item": f"第 {idx+1} 条记录字段齐全",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "字段完整"
            })
            total_score += 5

    if not field_ok:
        # 字段不全继续检查没有意义，但可以继续看数量
        pass

    # ---------- 4. 检查记录数量 ----------
    # 应该只有三个有效员工（E001, E002, E003），不能包含 E004 或重复
    ids_in_result = {rec["employee_id"] for rec in data}
    expected_ids = {"E001", "E002", "E003"}
    if ids_in_result == expected_ids:
        details.append({
            "item": "结果包含且仅包含 E001, E002, E003",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "正确数量与 ID 集合"
        })
        total_score += 15
    else:
        extra = ids_in_result - expected_ids
        missing = expected_ids - ids_in_result
        reason_parts = []
        if extra:
            reason_parts.append(f"多余员工: {extra}")
        if missing:
            reason_parts.append(f"缺少员工: {missing}")
        details.append({
            "item": "结果包含且仅包含 E001, E002, E003",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # ---------- 5. 检查每条记录的数值准确性 ----------
    # 将结果按 employee_id 索引
    result_by_id = {}
    for rec in data:
        eid = rec.get("employee_id")
        if eid:
            result_by_id[eid] = rec

    score_accuracy_ok = True
    for eid, expected in expected_employees.items():
        if eid not in result_by_id:
            details.append({
                "item": f"员工 {eid} 的 total_score 正确",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"缺少记录"
            })
            score_accuracy_ok = False
            continue
        rec = result_by_id[eid]
        # 检查姓名
        name_ok = rec.get("employee_name") == expected["name"]
        dept_ok = rec.get("department") == expected["dept"]
        # 检查分数（允许误差 1e-6）
        score_val = rec.get("total_score")
        if not isinstance(score_val, (int, float)):
            score_ok = False
        else:
            score_ok = math.isclose(score_val, expected["score"], rel_tol=1e-6)

        if name_ok and dept_ok and score_ok:
            details.append({
                "item": f"员工 {eid} 的姓名、部门、分数正确",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"Score={score_val}"
            })
            total_score += 10
        else:
            reasons = []
            if not name_ok:
                reasons.append(f"姓名期望 {expected['name']} 实际 {rec.get('employee_name')}")
            if not dept_ok:
                reasons.append(f"部门期望 {expected['dept']} 实际 {rec.get('department')}")
            if not score_ok:
                reasons.append(f"分数期望 {expected['score']} 实际 {score_val}")
            details.append({
                "item": f"员工 {eid} 的姓名、部门、分数正确",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "; ".join(reasons)
            })
            score_accuracy_ok = False

    # ---------- 6. 额外检查：不允许包含冗余字段或 E004 ----------
    # 如果结果中有任何不在 expected_ids 中的 ID，之前已扣分。这里再确认一下没有多余字段
    # 我们整体已经检查过，这里可以再给一个额外扣分但总分已包含。为了细致，我们可以加一条检查重复记录。
    # 但我们的设计里，如果存在重复ID，结果列表长度>3，前面积分已扣除，这里不再重复。

    # 计算总分（满分100）
    # 前面已累加 total_score，但可能因为某些失败终止导致总分不准，我们需要用累加值。
    # 这里重新计算以确保正确（但之前已经加了）
    # 如果 total_score 超过 100 则截断，但通常不会。
    final_score = min(total_score, 100)

    return details, final_score


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details, total = check_result(workspace)
    result = {
        "total_score": total,
        "details": details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Score written to {output_path}: {total}/100")

if __name__ == "__main__":
    main()
