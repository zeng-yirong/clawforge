import sys
import os
import json
import math

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # 1. 检查 output 目录是否存在 (10分)
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        details.append({"item": "output目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "output目录已创建"})
        total += 10
    else:
        details.append({"item": "output目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "output目录未找到"})
        # 后面各项直接失败
        return finish(details)

    # 2. 检查 performance_profiles.json 是否存在 (10分)
    profile_path = os.path.join(output_dir, "performance_profiles.json")
    if os.path.isfile(profile_path):
        details.append({"item": "performance_profiles.json存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已找到"})
        total += 10
    else:
        details.append({"item": "performance_profiles.json存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        return finish(details)

    # 3. JSON 格式合法性 (10分)
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            records = data.get("employees") or data.get("profiles") or list(data.values())
            # 如果最外层是 dict，尝试找列表或转成列表
            if not isinstance(records, list):
                records = [records]
        elif isinstance(data, list):
            records = data
        else:
            raise ValueError("顶层不是数组或对象")
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败：{e}"})
        return finish(details)

    # 4. 员工数量正确（应该有3人：E001,E002,E004）(10分)
    expected_ids = {"E001", "E002", "E004"}
    actual_ids = set()
    for rec in records:
        eid = rec.get("employee_id")
        if eid:
            actual_ids.add(eid)
    if actual_ids == expected_ids:
        details.append({"item": "员工数量及ID正确", "score": 10, "max_score": 10, "passed": True, "reason": f"包含 {sorted(actual_ids)}"})
        total += 10
    else:
        details.append({"item": "员工数量及ID正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_ids}, 实际 {actual_ids}"})

    # 5. 每个员工字段完整性 (10分)
    required_fields = ["employee_id", "employee_name", "department", "total_score", "rating"]
    field_ok = True
    missing_in = []
    for rec in records:
        eid = rec.get("employee_id", "未知")
        for fld in required_fields:
            if fld not in rec:
                missing_in.append(f"{eid} 缺少字段 {fld}")
                field_ok = False
    if field_ok:
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有记录包含必需字段"})
        total += 10
    else:
        details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "；".join(missing_in)})

    # 6. 数值计算准确性 (40分) - 每个员工10分，计算具体数值
    expected = {
        "E001": {"total_score": 85.0, "rating": "B", "employee_name": "张三", "department": "Engineering"},
        "E002": {"total_score": 75.5, "rating": "B", "employee_name": "李四", "department": "Engineering"},
        "E004": {"total_score": 89.5, "rating": "B", "employee_name": "赵六", "department": "HR"}
    }
    score_pool = 40
    per_score = score_pool // 4   # 10 per field set, 4 sets
    # 先按ID索引
    by_id = {}
    for rec in records:
        eid = rec.get("employee_id")
        if eid:
            by_id[eid] = rec
    calc_ok = True
    calc_reasons = []
    for eid, exp in expected.items():
        if eid not in by_id:
            calc_ok = False
            calc_reasons.append(f"{eid} 缺失")
            continue
        actual = by_id[eid]
        # 比较 total_score (允许小数点后一位误差)
        exp_score = exp["total_score"]
        try:
            act_score = float(actual.get("total_score", "nan"))
        except:
            act_score = None
        if act_score is None or abs(act_score - exp_score) > 0.01:
            calc_ok = False
            calc_reasons.append(f"{eid} total_score: 期望 {exp_score}, 实际 {act_score}")
        # 比较 rating
        exp_rating = exp["rating"]
        act_rating = actual.get("rating", "")
        if act_rating != exp_rating:
            calc_ok = False
            calc_reasons.append(f"{eid} rating: 期望 {exp_rating}, 实际 {act_rating}")
        # 比较 name & department（可选）
        if actual.get("employee_name") != exp["employee_name"]:
            calc_ok = False
            calc_reasons.append(f"{eid} employee_name: 期望 {exp['employee_name']}, 实际 {actual.get('employee_name')}")
        if actual.get("department") != exp["department"]:
            calc_ok = False
            calc_reasons.append(f"{eid} department: 期望 {exp['department']}, 实际 {actual.get('department')}")
    if calc_ok:
        details.append({"item": "E001计算正确", "score": 10, "max_score": 10, "passed": True, "reason": "数值、评级、姓名部门一致"})
        details.append({"item": "E002计算正确", "score": 10, "max_score": 10, "passed": True, "reason": "数值、评级、姓名部门一致"})
        details.append({"item": "E004计算正确", "score": 10, "max_score": 10, "passed": True, "reason": "数值、评级、姓名部门一致"})
        details.append({"item": "无多余员工", "score": 10, "max_score": 10, "passed": True, "reason": "没有实习生或缺失员工被误纳入"})
        total += 40
    else:
        parts = set([r.split()[0] for r in calc_reasons])
        # 给部分分
        pts = 0
        for eid in ["E001","E002","E004"]:
            if eid not in parts:
                pts += 10
                details.append({"item": f"{eid}计算正确", "score": 10, "max_score": 10, "passed": True, "reason": "未涉及错误"})
            else:
                details.append({"item": f"{eid}计算正确", "score": 0, "max_score": 10, "passed": False, "reason": next((r for r in calc_reasons if r.startswith(eid)), "错误原因未记录")})
        # 多余员工检查
        extra = [eid for eid in by_id if eid not in expected]
        if extra:
            details.append({"item": "无多余员工", "score": 0, "max_score": 10, "passed": False, "reason": f"包含不应出现的员工ID: {extra}"})
        else:
            details.append({"item": "无多余员工", "score": 10, "max_score": 10, "passed": True, "reason": "没有多余员工"})
            pts += 10
        total += pts

    # 7. 额外多余字段检查（扣分项，但题目未要求，不扣分，仅提醒）
    # 可选项：检查没有多余字段
    finish(details)

def finish(details):
    total = sum(d["score"] for d in details)
    # 保证总分不超过100
    total = min(total, 100)
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if total >= 40 else 1)   # 非零也可以，但按规范输出

if __name__ == "__main__":
    verify()
