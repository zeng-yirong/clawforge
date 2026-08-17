import sys
import os
import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops/ directory found" if dir_exists else "ops/ directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 ops/customer_tiers.json 是否存在且合法 (10分)
    result_path = os.path.join(ops_dir, "customer_tiers.json")
    file_ok = False
    tiers_data = None
    if os.path.isfile(result_path):
        try:
            tiers_data = load_json(result_path)
            file_ok = True
        except Exception as e:
            details.append({
                "item": "customer_tiers.json is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {e}"
            })
    else:
        details.append({
            "item": "customer_tiers.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
    if file_ok:
        details.append({
            "item": "customer_tiers.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON"
        })
        total_score += 10
    else:
        details.append({
            "item": "customer_tiers.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Skipped because file missing or invalid"
        })

    # 如果文件不合法，直接返回
    if not file_ok:
        details.append({"item": "Customer C001 label", "score": 0, "max_score": 35, "passed": False, "reason": "Skipped"})
        details.append({"item": "Customer C002 label", "score": 0, "max_score": 35, "passed": False, "reason": "Skipped"})
        _write_score(total_score, details, workspace)
        return

    # 3. 检查数据结构：应为 dict，key=string, value=string (20分)
    structure_ok = isinstance(tiers_data, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in tiers_data.items())
    details.append({
        "item": "Result is a dict mapping customer_id (str) to tier (str)",
        "score": 20 if structure_ok else 0,
        "max_score": 20,
        "passed": structure_ok,
        "reason": "Structure correct" if structure_ok else "Expected dict of str->str"
    })
    if structure_ok:
        total_score += 20

    # 4. 计算预期标签
    # 加载规则文件和日志
    try:
        rules = load_json(os.path.join(workspace, "rules/segmentation_rules.json"))
        consumption = load_json(os.path.join(workspace, "data/logs/consumption_logs.json"))
        activity = load_json(os.path.join(workspace, "data/logs/activity_logs.json"))
    except Exception as e:
        # 如果无法读取，则跳过验证，但保留得分
        details.append({"item": "Customer C001 label", "score": 0, "max_score": 35, "passed": False, "reason": f"Cannot load source files: {e}"})
        details.append({"item": "Customer C002 label", "score": 0, "max_score": 35, "passed": False, "reason": f"Cannot load source files: {e}"})
        _write_score(total_score, details, workspace)
        return

    # 构建数据映射
    spend_map = {x["customer_id"]: x["quarter_spend_usd"] for x in consumption["consumption_logs"]}
    activity_map = {x["customer_id"]: x for x in activity["activity_logs"]}

    # 规则定义（按顺序应用）
    tier_defs = rules["tiers"]  # 列表，第一个匹配即选中

    expected_tiers = {}
    for cid in ["C001", "C002"]:
        spend = spend_map.get(cid)
        act = activity_map.get(cid)
        if spend is None or act is None:
            continue
        days = act["last_active_days"]
        risk = act["risk_level"]
        chosen = None
        for t in tier_defs:
            if (spend >= t["min_spend"] and
                days <= t["max_inactive_days"] and
                risk in t["allowed_risk"]):
                chosen = t["name"]
                break
        if chosen:
            expected_tiers[cid] = chosen

    # 5. 验证每个客户 (35分 each)
    def check_customer(cid, expected):
        actual = tiers_data.get(cid)
        passed = (actual == expected)
        reason = f"Expected '{expected}', got '{actual}'" if not passed else "Correct"
        return {"item": f"Customer {cid} label", "score": 35 if passed else 0, "max_score": 35, "passed": passed, "reason": reason}

    for cid, expected in expected_tiers.items():
        det = check_customer(cid, expected)
        details.append(det)
        if det["passed"]:
            total_score += 35

    # 如果缺少客户，也要扣分
    for cid in ["C001", "C002"]:
        if cid not in expected_tiers:
            details.append({"item": f"Customer {cid} label", "score": 0, "max_score": 35, "passed": False, "reason": "Customer data missing in source"})

    _write_score(total_score, details, workspace)

def _write_score(total, details, workspace):
    out = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
