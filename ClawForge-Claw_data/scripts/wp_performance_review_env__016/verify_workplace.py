import sys
import json
import os
from pathlib import Path

def score() -> dict:
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace)
    details = []
    total = 0

    # ===== 1. 目录结构 (10分) =====
    ops_dir = base / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops/目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/目录已创建"})
        total += 10
    else:
        details.append({"item": "ops/目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/目录缺失"})

    # ===== 2. 产物文件存在且合法 (20分) =====
    profile_path = ops_dir / "performance_profiles.json"
    if not profile_path.is_file():
        details.append({"item": "performance_profiles.json存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件未找到"})
        return {"total_score": total, "details": details}

    try:
        with open(profile_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 20, "passed": False, "reason": f"解析失败: {str(e)}"})
        return {"total_score": total, "details": details}

    if not isinstance(data, list) and not isinstance(data, dict):
        details.append({"item": "JSON顶层结构", "score": 0, "max_score": 10, "passed": False, "reason": "顶层应为list或dict"})
        return {"total_score": total, "details": details}

    # 接受两种形式：列表[{...}] 或 { "profiles": [...] }
    if isinstance(data, dict):
        profiles = data.get("profiles", data)
        if not isinstance(profiles, list):
            details.append({"item": "JSON顶层结构", "score": 0, "max_score": 10, "passed": False, "reason": "字典内未找到profiles列表"})
            return {"total_score": total, "details": details}
    else:
        profiles = data

    if not profiles:
        details.append({"item": "文件合法性", "score": 0, "max_score": 10, "passed": False, "reason": "profile列表为空"})
        return {"total_score": total, "details": details}

    details.append({"item": "文件存在且JSON合法", "score": 20, "max_score": 20, "passed": True, "reason": "performance_profiles.json可解析"})
    total += 20

    # ===== 3. 数据正确性 (70分) =====
    # 提取profile
    id_map = {}
    for p in profiles:
        eid = p.get("employee_id")
        if eid:
            id_map[eid] = p

    # 期望的两个员工
    expected_employees = {
        "E001": {
            "employee_name": "Zhang Wei",
            "role_code": "dev",
            "total_score": 9.2,   # 10*0.5 + 8*0.3 + 9*0.2 = 5+2.4+1.8=9.2
            "weights": {"feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2}
        },
        "E002": {
            "employee_name": "Li Na",
            "role_code": "qa",
            "total_score": 7.6,   # 7*0.4 + 9*0.4 + 6*0.2 = 2.8+3.6+1.2=7.6
            "weights": {"feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2}
        }
    }

    for eid, exp in expected_employees.items():
        if eid not in id_map:
            details.append({"item": f"员工 {eid} 存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少employee_id={eid}"})
            continue

        p = id_map[eid]

        # 检查必要字段
        missing = []
        for field in ["employee_id", "employee_name", "role_code", "total_score"]:
            if field not in p:
                missing.append(field)
        if missing:
            details.append({"item": f"员工 {eid} 字段完整性", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少字段 {missing}"})
            continue

        # 判别员工姓名
        name_ok = p.get("employee_name") == exp["employee_name"]
        role_ok = p.get("role_code") == exp["role_code"]
        if not name_ok or not role_ok:
            details.append({"item": f"员工 {eid} 标识信息", "score": 0, "max_score": 5, "passed": False,
                            "reason": f"姓名={p.get('employee_name')}(期望{exp['employee_name']}) 或 角色={p.get('role_code')}(期望{exp['role_code']})"})
            continue

        # 总分检查（允许 ±0.005）
        actual_score = p.get("total_score")
        if not isinstance(actual_score, (int, float)):
            details.append({"item": f"员工 {eid} 总分类型", "score": 0, "max_score": 5, "passed": False, "reason": "total_score不是数值"})
            continue
        if abs(actual_score - exp["total_score"]) > 0.01:
            details.append({"item": f"员工 {eid} 总分", "score": 0, "max_score": 15, "passed": False,
                            "reason": f"总分 {actual_score:.2f}，期望 {exp['total_score']:.2f}"})
            continue
        else:
            details.append({"item": f"员工 {eid} 总分", "score": 15, "max_score": 15, "passed": True, "reason": f"总分 {actual_score:.2f} 正确"})
            total += 15

        # 组件分数 (component_scores) — 可选但加分
        comp = p.get("component_scores", {})
        if isinstance(comp, dict):
            has_raw = all(k in comp for k in ["feature_delivery", "quality_score", "collaboration_score"])
            has_weight = all(k in comp for k in ["feature_delivery_weight", "quality_weight", "collaboration_weight"])
            if has_raw and has_weight:
                # 验证权重是否匹配规则
                w = exp["weights"]
                w_ok = (
                    abs(comp.get("feature_delivery_weight", 0) - w["feature_delivery_weight"]) < 0.01 and
                    abs(comp.get("quality_weight", 0) - w["quality_weight"]) < 0.01 and
                    abs(comp.get("collaboration_weight", 0) - w["collaboration_weight"]) < 0.01
                )
                if w_ok:
                    details.append({"item": f"员工 {eid} 组件权重", "score": 5, "max_score": 5, "passed": True, "reason": "组件分数和权重正确"})
                    total += 5
                else:
                    details.append({"item": f"员工 {eid} 组件权重", "score": 2, "max_score": 5, "passed": False, "reason": "权重与规则不符"})
                    total += 2
            else:
                details.append({"item": f"员工 {eid} 组件分数", "score": 0, "max_score": 5, "passed": False, "reason": "component_scores缺少必要子字段"})
        else:
            details.append({"item": f"员工 {eid} 组件分数", "score": 0, "max_score": 5, "passed": False, "reason": "component_scores字段非dict"})

    # 确保没有多余的员工（只允许E001, E002）
    extra = [eid for eid in id_map if eid not in expected_employees]
    if extra:
        details.append({"item": "无多余员工", "score": 0, "max_score": 5, "passed": False, "reason": f"包含不应出现的员工: {extra}"})
    else:
        details.append({"item": "无多余员工", "score": 5, "max_score": 5, "passed": True, "reason": "只包含E001和E002"})
        total += 5

    # 补齐总分（避免因为部分缺失导致总分偏小）
    total = min(total, 100)
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    result = score()
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
