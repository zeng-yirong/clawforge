import json
import math
import os
import sys

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []

    # 1. 检查 profiles 目录
    profiles_dir = os.path.join(workspace, "profiles")
    if os.path.isdir(profiles_dir):
        total_score += 5
        details.append({
            "item": "Directory 'profiles' exists",
            "score": 5, "max_score": 5, "passed": True,
            "reason": "profiles directory found"
        })
    else:
        details.append({
            "item": "Directory 'profiles' exists",
            "score": 0, "max_score": 5, "passed": False,
            "reason": "profiles directory not found"
        })

    # 2. 检查目标文件
    target_file = os.path.join(profiles_dir, "performance_profiles.json")
    if os.path.isfile(target_file):
        total_score += 10
        details.append({
            "item": "File 'profiles/performance_profiles.json' exists",
            "score": 10, "max_score": 10, "passed": True,
            "reason": "target file found"
        })
    else:
        # 如果目录不存在也扣分
        details.append({
            "item": "File 'profiles/performance_profiles.json' exists",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "target file not found"
        })
        # 直接结束，后续无法检查
        _write_score(total_score, details)
        sys.exit(0)

    # 3. 解析 JSON 且必须是 list
    try:
        profiles = load_json(target_file)
        if isinstance(profiles, list):
            total_score += 10
            details.append({
                "item": "JSON is a list",
                "score": 10, "max_score": 10, "passed": True,
                "reason": "valid list"
            })
        else:
            total_score += 0
            details.append({
                "item": "JSON is a list",
                "score": 0, "max_score": 10, "passed": False,
                "reason": f"expected list, got {type(profiles).__name__}"
            })
    except Exception as e:
        total_score += 0
        details.append({
            "item": "JSON is a list",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"parse error: {e}"
        })
        _write_score(total_score, details)
        sys.exit(0)

    # 4. 加载原始数据并计算期望值
    try:
        emp_data = load_json(os.path.join(workspace, "data/employees/employees.json"))["employees"]
        output_data = load_json(os.path.join(workspace, "data/ledgers/monthly_outputs.json"))["monthly_outputs"]
        rule_data = load_json(os.path.join(workspace, "data/rules/scoring_rules.json"))["scoring_rules"]
    except Exception as e:
        total_score += 0
        details.append({
            "item": "Load original data",
            "score": 0, "max_score": 0, "passed": False,
            "reason": f"failed to load original data: {e}"
        })
        _write_score(total_score, details)
        sys.exit(0)

    # 构建权重映射
    weight_map = {r["role_code"]: r for r in rule_data}

    # 构建员工期望得分（只考虑 employees.json 中存在的员工，忽略 E999）
    expected = {}
    for emp in emp_data:
        eid = emp["employee_id"]
        output = None
        for o in output_data:
            if o["employee_id"] == eid:
                output = o
                break
        if output is None:
            continue  # 理论上不会，但安全
        role_code = emp["role_code"]
        weights = weight_map.get(role_code)
        if weights is None:
            continue
        score = (output["feature_delivery"] * weights["feature_delivery_weight"] +
                 output["quality_score"] * weights["quality_weight"] +
                 output["collaboration_score"] * weights["collaboration_weight"])
        expected[eid] = {
            "employee_name": emp["employee_name"],
            "department": emp["department"],
            "role_code": role_code,
            "total_score": round(score, 1)
        }

    # 5. 检查记录数量
    required_ids = set(expected.keys())
    provided_ids = set(p.get("employee_id") for p in profiles if isinstance(p, dict))
    if provided_ids == required_ids:
        total_score += 15
        details.append({
            "item": "Number of employees correct (3 active)",
            "score": 15, "max_score": 15, "passed": True,
            "reason": f"profiles contain {len(provided_ids)} employees exactly matching roster"
        })
    else:
        missing = required_ids - provided_ids
        extra = provided_ids - required_ids
        total_score += 0
        details.append({
            "item": "Number of employees correct (3 active)",
            "score": 0, "max_score": 15, "passed": False,
            "reason": f"missing: {missing}, extra: {extra}"
        })

    # 6. 检查字段完整性
    required_fields = {"employee_id", "employee_name", "department", "role_code", "total_score"}
    all_fields_ok = True
    for p in profiles:
        if not isinstance(p, dict):
            all_fields_ok = False
            continue
        if not required_fields.issubset(p.keys()):
            all_fields_ok = False
    if all_fields_ok:
        total_score += 15
        details.append({
            "item": "All profiles have required fields",
            "score": 15, "max_score": 15, "passed": True,
            "reason": "each profile contains employee_id, employee_name, department, role_code, total_score"
        })
    else:
        total_score += 0
        details.append({
            "item": "All profiles have required fields",
            "score": 0, "max_score": 15, "passed": False,
            "reason": "some profiles missing required fields"
        })

    # 7. 逐员工分数验证
    score_items = [
        ("E001", "Alice", 84.5, 20),
        ("E002", "Bob", 74.5, 15),
        ("E003", "Charlie", 89.0, 10)
    ]
    for eid, name, expected_score, pts in score_items:
        found = False
        for p in profiles:
            if isinstance(p, dict) and p.get("employee_id") == eid:
                found = True
                got = p.get("total_score")
                if isinstance(got, (int, float)) and math.isclose(got, expected_score, rel_tol=1e-6):
                    total_score += pts
                    details.append({
                        "item": f"{name} ({eid}) total_score = {expected_score}",
                        "score": pts, "max_score": pts, "passed": True,
                        "reason": f"got {got}"
                    })
                else:
                    details.append({
                        "item": f"{name} ({eid}) total_score = {expected_score}",
                        "score": 0, "max_score": pts, "passed": False,
                        "reason": f"expected {expected_score}, got {got}"
                    })
                break
        if not found:
            total_score += 0
            details.append({
                "item": f"{name} ({eid}) total_score = {expected_score}",
                "score": 0, "max_score": pts, "passed": False,
                "reason": "employee missing in profiles"
            })

    _write_score(total_score, details)

def _write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
