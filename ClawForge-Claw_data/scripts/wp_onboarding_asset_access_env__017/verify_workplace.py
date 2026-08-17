import os
import json
import sys

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def build_expected(workspace):
    # 读取原始数据
    contracts_path = os.path.join(workspace, "data/onboarding/contracts.json")
    equip_path = os.path.join(workspace, "data/onboarding/equipment_inventory.json")
    packs_path = os.path.join(workspace, "data/onboarding/permission_packs.json")

    contracts = load_json(contracts_path)["contracts"]
    equipment = load_json(equip_path)["equipment_inventory"]
    packs = load_json(packs_path)["permission_packs"]

    # 过滤：signed 且 department=Engineering
    target = [c for c in contracts if c["status"] == "signed" and c["department"] == "Engineering"]
    # 按 employee_id 排序保证顺序稳定
    target.sort(key=lambda x: x["employee_id"])

    # 找到 eng_pack 的 systems
    eng_systems = None
    for p in packs:
        if p["pack_id"] == "eng_pack":
            eng_systems = p["systems"]
            break
    if eng_systems is None:
        raise ValueError("eng_pack not found")

    # 可用笔记本电脑（按 asset_tag 排序）
    avail_laptops = [e for e in equipment if e["asset_type"] == "laptop" and e["status"] == "available"]
    avail_laptops.sort(key=lambda x: x["asset_tag"])

    expected = []
    for i, emp in enumerate(target):
        tag = avail_laptops[i]["asset_tag"] if i < len(avail_laptops) else None
        welcome = f"Welcome {emp['employee_name']}! Your assigned equipment is {tag}. Access to {', '.join(eng_systems)} has been granted."
        expected.append({
            "employee_id": emp["employee_id"],
            "email": emp["email"],
            "permissions": eng_systems,
            "equipment_tag": tag,
            "welcome_message": welcome
        })
    return expected

def verify(workspace):
    results = {
        "total_score": 0,
        "details": []
    }

    # 1. ops 目录存在
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    results["details"].append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    if not dir_exists:
        results["total_score"] = sum(d["score"] for d in results["details"])
        return results

    # 2. onboarding_plan.json 存在
    plan_path = os.path.join(workspace, "ops", "onboarding_plan.json")
    file_exists = os.path.isfile(plan_path)
    results["details"].append({
        "item": "onboarding_plan.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file missing"
    })
    if not file_exists:
        results["total_score"] = sum(d["score"] for d in results["details"])
        return results

    # 3. JSON 合法
    try:
        plan = load_json(plan_path)
        json_ok = True
        reason = "valid JSON"
    except Exception as e:
        json_ok = False
        reason = f"invalid JSON: {str(e)}"
    results["details"].append({
        "item": "valid JSON",
        "score": 10 if json_ok else 0,
        "max_score": 10,
        "passed": json_ok,
        "reason": reason
    })
    if not json_ok:
        results["total_score"] = sum(d["score"] for d in results["details"])
        return results

    # 4. 顶层是列表
    is_list = isinstance(plan, list)
    results["details"].append({
        "item": "top-level is list",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "top-level is list" if is_list else "top-level is not a list"
    })
    if not is_list:
        results["total_score"] = sum(d["score"] for d in results["details"])
        return results

    # 5. 列表长度
    expected = build_expected(workspace)
    len_ok = len(plan) == len(expected)
    results["details"].append({
        "item": "correct number of employees",
        "score": 20 if len_ok else 0,
        "max_score": 20,
        "passed": len_ok,
        "reason": f"expected {len(expected)} employees, got {len(plan)}" if not len_ok else "length matches"
    })
    if not len_ok:
        results["total_score"] = sum(d["score"] for d in results["details"])
        return results

    # 6. 逐字段比较
    field_score = 10.0 / (len(expected) * 5)  # 5个字段，总分10分（因为前面已80分，这里补20分? 调整权重）
    # 重新分配：总100分，已分配10+10+10+10+20=60，剩余40分给字段比较
    # 每个字段满分 = 40/(len*5)
    field_max_per = 40 / (len(expected) * 5)
    field_total_max = 40.0
    field_total_score = 0.0
    field_reasons = []
    for idx, (exp_item, act_item) in enumerate(zip(expected, plan)):
        fields = ["employee_id", "email", "permissions", "equipment_tag", "welcome_message"]
        for field in fields:
            exp_val = exp_item[field]
            act_val = act_item.get(field)
            if act_val == exp_val:
                field_total_score += field_max_per
                field_reasons.append(f"employee {idx} field '{field}' correct")
            else:
                field_reasons.append(f"employee {idx} field '{field}' expected {exp_val!r}, got {act_val!r}")
    field_passed = field_total_score == field_max_per * len(expected) * 5
    results["details"].append({
        "item": "all fields match expected values",
        "score": round(field_total_score),
        "max_score": 40,
        "passed": field_passed,
        "reason": "; ".join(field_reasons)
    })
    results["total_score"] = sum(d["score"] for d in results["details"])
    # 确保整数
    results["total_score"] = int(round(results["total_score"]))
    return results

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))
