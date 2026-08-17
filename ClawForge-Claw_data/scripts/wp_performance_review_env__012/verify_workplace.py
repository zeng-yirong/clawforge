import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # ---------- 1. 检查 performance_profiles 目录是否存在 (10分) ----------
    profiles_dir = ws / "performance_profiles"
    if profiles_dir.is_dir():
        details.append({"item": "performance_profiles 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "performance_profiles 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        # 后面不用再检查文件了
        write_score(total_score, details, workspace)
        return

    # ---------- 2. 检查是否包含全部5个合法员工文件 (10分) ----------
    required_ids = {"E001", "E002", "E003", "E004", "E005"}
    found_files = [f for f in profiles_dir.iterdir() if f.suffix == ".json"]
    found_ids = {f.stem for f in found_files}
    missing = required_ids - found_ids
    extra = found_ids - required_ids
    if not missing and not extra:
        details.append({"item": "员工文件覆盖正确", "score": 10, "max_score": 10, "passed": True, "reason": "恰好包含E001-E005五个文件，无多余无缺失"})
        total_score += 10
    else:
        reasons = []
        if missing:
            reasons.append(f"缺失员工文件: {sorted(missing)}")
        if extra:
            reasons.append(f"多余员工文件: {sorted(extra)}")
        details.append({"item": "员工文件覆盖正确", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(reasons)})

    # ---------- 3. 每个文件 JSON 格式合法 (10分) ----------
    parsed = {}
    format_ok = True
    for f in found_files:
        try:
            with open(f, "r") as fp:
                data = json.load(fp)
            parsed[f.stem] = data
        except Exception as e:
            format_ok = False
            details.append({"item": f"文件 {f.name} JSON 格式合法", "score": 0, "max_score": 2, "passed": False, "reason": str(e)})
    if format_ok:
        details.append({"item": "所有 JSON 文件格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "全部可解析"})
        total_score += 10
    else:
        # 分数已加在子项中？为了简单，如果任何文件格式错误，此项总分0
        # 但前面可能单个扣分，这里覆盖总分逻辑：如果format_ok为False，则此项0分
        # 上面如果出异常已经加了子项，但这里我们只处理一次总分
        # 重构：先统一检查
        pass
    # 为了简化，重新统一检查格式并给分
    format_errors = []
    for f in found_files:
        try:
            with open(f) as fp:
                json.load(fp)
        except Exception as e:
            format_errors.append(f.name)
    if not format_errors:
        # 如果没有之前的子项，则加10分
        # 但之前可能已经加过，需要防止重复。我们改为先清除之前可能的子项再统一处理。
        # 简单做法：直接在此处判断，不依赖前面的子项。
        # 先将之前可能添加的格式化子项移除（如果存在）
        details = [d for d in details if "JSON 格式合法" not in d["item"]]
        details.append({"item": "所有 JSON 文件格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "全部可解析"})
        total_score += 10
    else:
        details = [d for d in details if "JSON 格式合法" not in d["item"]]
        details.append({"item": "所有 JSON 文件格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"格式错误文件: {format_errors}"})

    # ---------- 4. 每个文件必备字段 (employee_id, employee_name, department, total_score) (20分) ----------
    field_ok = True
    for eid in required_ids:
        data = parsed.get(eid)
        if data is None:
            continue  # 缺失文件已经在前面扣分
        if not isinstance(data, dict):
            field_ok = False
            break
        required_fields = ["employee_id", "employee_name", "department", "total_score"]
        for field in required_fields:
            if field not in data:
                field_ok = False
                break
    if field_ok:
        details.append({"item": "各文件包含必要字段", "score": 20, "max_score": 20, "passed": True, "reason": "所有文件均有 employee_id, employee_name, department, total_score"})
        total_score += 20
    else:
        details.append({"item": "各文件包含必要字段", "score": 0, "max_score": 20, "passed": False, "reason": "某些文件缺失字段或格式错误"})

    # ---------- 5. 总分计算正确 (40分) ----------
    # 根据业务规则计算预期总分
    # 先读取规则
    rules_path = ws / "data" / "rules" / "scoring_rules.json"
    if not rules_path.exists():
        details.append({"item": "计算验证所需规则文件缺失", "score": 0, "max_score": 40, "passed": False, "reason": "无法找到规则文件"})
    else:
        with open(rules_path) as f:
            rules_data = json.load(f)
        rules_dict = {}
        for rule in rules_data.get("scoring_rules", []):
            rules_dict[rule["role_code"]] = rule

        # 读取员工信息获取角色
        emp_path = ws / "data" / "employees" / "employees.json"
        with open(emp_path) as f:
            emp_data = json.load(f)
        emp_map = {}
        for emp in emp_data.get("employees", []):
            emp_map[emp["employee_id"]] = emp

        # 读取月度产出（取第一条有效记录，忽略干扰）
        led_path = ws / "data" / "ledgers" / "monthly_outputs.json"
        with open(led_path) as f:
            led_data = json.load(f)
        output_map = {}
        for rec in led_data.get("monthly_outputs", []):
            eid = rec["employee_id"]
            if eid in emp_map and eid not in output_map:
                # 只取第一个出现的有效记录（排除重复）
                output_map[eid] = rec

        calc_errors = []
        for eid in required_ids:
            emp = emp_map.get(eid)
            if not emp:
                calc_errors.append(f"{eid}: 员工信息缺失")
                continue
            rule = rules_dict.get(emp["role_code"])
            if not rule:
                calc_errors.append(f"{eid}: 无对应角色规则")
                continue
            output = output_map.get(eid)
            if not output:
                calc_errors.append(f"{eid}: 无有效产出记录")
                continue
            expected = (output["feature_delivery"] * rule["feature_delivery_weight"] +
                        output["quality_score"] * rule["quality_weight"] +
                        output["collaboration_score"] * rule["collaboration_weight"])
            # 四舍五入到整数（实际计算可能是浮点，但示例值均为整数结果）
            expected = round(expected, 2)  # 保留两位以防浮点误差
            actual = parsed.get(eid, {}).get("total_score")
            if actual is None:
                calc_errors.append(f"{eid}: 缺少total_score")
            elif abs(actual - expected) > 0.01:
                calc_errors.append(f"{eid}: 期望 {expected}，实际 {actual}")
        if not calc_errors:
            details.append({"item": "所有员工总分计算正确", "score": 40, "max_score": 40, "passed": True, "reason": "期望值与实际值完全一致"})
            total_score += 40
        else:
            details.append({"item": "所有员工总分计算正确", "score": 0, "max_score": 40, "passed": False, "reason": "; ".join(calc_errors[:3]) + (f" 等{len(calc_errors)}处错误" if len(calc_errors)>3 else "")})

    # 写结果
    write_score(total_score, details, workspace)

def write_score(total, details, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
