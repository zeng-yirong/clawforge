import sys
import json
import os
from pathlib import Path

def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def compute_expected(workspace):
    """基于工作区中 env_builder 生成的数据计算唯一正确答案。"""
    # 加载 zones
    zones_path = Path(workspace) / "data/zones/zones.json"
    zones = load_json(zones_path)

    # 加载 accounts
    accounts_path = Path(workspace) / "data/accounts/accounts.json"
    accounts = load_json(accounts_path)

    # 加载 contacts
    contacts_path = Path(workspace) / "data/contacts/contacts.json"
    contacts = load_json(contacts_path)

    # 构建映射
    zone_map = {z["zone_id"]: z for z in zones}
    account_map = {a["account_id"]: a for a in accounts}
    contact_map = {c["contact_id"]: c for c in contacts}

    # 筛选 active 且 intrusion_detected 为 True 的 (account, zone) 配对
    results = []
    for acc in accounts:
        if not acc.get("active", False):
            continue
        for zid in acc.get("zones", []):
            zone = zone_map.get(zid)
            if zone and zone.get("intrusion_detected") is True:
                for cid in acc.get("emergency_contacts", []):
                    contact = contact_map.get(cid)
                    if contact:
                        results.append({
                            "zone_id": zone["zone_id"],
                            "zone_name": zone["zone_name"],
                            "account_name": acc["account_name"],
                            "contact_name": contact["name"],
                            "phone": contact["phone"]
                        })
    # 按 zone_id, contact_name 排序保证顺序稳定（便于比较）
    results.sort(key=lambda x: (x["zone_id"], x["contact_name"]))
    return results

def verify(workspace):
    details = []
    total_score = 0

    # ----- 1. 目录 ops 存在 (10分) -----
    ops_dir = Path(workspace) / "ops"
    dir_exists = ops_dir.is_dir()
    if dir_exists:
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})
        # 后续检查都需要 ops 目录，如果不存在直接结束
        return {"total_score": total_score, "details": details}

    # ----- 2. 文件 ops/confirmed_alerts.json 存在 (10分) -----
    target_file = ops_dir / "confirmed_alerts.json"
    file_exists = target_file.is_file()
    if file_exists:
        details.append({"item": "confirmed_alerts.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file present"})
        total_score += 10
    else:
        details.append({"item": "confirmed_alerts.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        return {"total_score": total_score, "details": details}

    # ----- 3. JSON 格式合法 (10分) -----
    try:
        agent_data = load_json(target_file)
        details.append({"item": "JSON parseable", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON parseable", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        return {"total_score": total_score, "details": details}

    # ----- 4. 记录数量正确 (20分) -----
    expected = compute_expected(workspace)
    expected_count = len(expected)
    agent_count = len(agent_data)
    count_correct = agent_count == expected_count
    if count_correct:
        details.append({"item": "record count", "score": 20, "max_score": 20, "passed": True, "reason": f"expected {expected_count}, got {agent_count}"})
        total_score += 20
    else:
        details.append({"item": "record count", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_count}, got {agent_count}"})
        # 即使数量不对，后续仍可检查字段，但这里记0分；后续检查得分可独立

    # ----- 5. 每条记录字段完整性 (20分) -----
    required_fields = {"zone_id", "zone_name", "account_name", "contact_name", "phone"}
    field_score = 0
    field_max = 20
    field_issues = []
    for i, rec in enumerate(agent_data):
        missing = required_fields - set(rec.keys())
        if missing:
            field_issues.append(f"record {i} missing fields: {missing}")
        else:
            field_score += 1
    # 按比例给分，最多20分
    if field_issues:
        details.append({"item": "all records have required fields", "score": field_score, "max_score": field_max, "passed": field_score == len(agent_data), "reason": "; ".join(field_issues)})
    else:
        details.append({"item": "all records have required fields", "score": field_max, "max_score": field_max, "passed": True, "reason": "all fields present"})
    total_score += field_score

    # ----- 6. 字段值完全匹配预期 (30分) -----
    # 转换为可哈希集合进行比较（忽略顺序）
    def record_to_tuple(rec):
        return (rec.get("zone_id"), rec.get("zone_name"), rec.get("account_name"), rec.get("contact_name"), rec.get("phone"))

    expected_set = {record_to_tuple(r) for r in expected}
    agent_set = {record_to_tuple(r) for r in agent_data}

    # 计算正确匹配的数量（交集）
    correct_matches = len(expected_set & agent_set)
    extra = len(agent_set - expected_set)
    missing = len(expected_set - agent_set)

    if correct_matches == expected_count and extra == 0 and missing == 0:
        details.append({"item": "field values match expected", "score": 30, "max_score": 30, "passed": True, "reason": "exact match"})
        total_score += 30
    else:
        # 按正确比例给分，最多30分，每个错误（额外或缺失）扣5分，直到0
        penalty = (extra + missing) * 5
        value_score = max(0, 30 - penalty)
        reason_parts = []
        if extra > 0:
            reason_parts.append(f"{extra} unexpected records")
        if missing > 0:
            reason_parts.append(f"{missing} missing records")
        details.append({"item": "field values match expected", "score": value_score, "max_score": 30, "passed": value_score == 30, "reason": "; ".join(reason_parts) if reason_parts else "partial mismatch"})
        total_score += value_score

    # 确保总分不超过100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")

if __name__ == "__main__":
    main()
