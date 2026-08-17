import json
import os
import sys

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查目录结构 (10分)
    required_dirs = ["ops"]
    for d in required_dirs:
        path = os.path.join(workspace, d)
        if os.path.isdir(path):
            details.append({"item": f"目录 {d} 存在", "score": 5, "max_score": 5, "passed": True, "reason": ""})
            total_score += 5
        else:
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 5, "passed": False, "reason": f"缺失目录 {d}"})

    # 2. 检查产物 ops/response.json 存在 (10分)
    response_path = os.path.join(workspace, "ops", "response.json")
    if not os.path.isfile(response_path):
        details.append({"item": "产物 ops/response.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        return finalize(details, total_score)

    details.append({"item": "产物 ops/response.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": ""})
    total_score += 10

    # 3. 检查 JSON 合法性 (10分)
    try:
        data = load_json(response_path)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        return finalize(details, total_score)

    # 4. 检查必要字段 (10分)
    required_fields = ["doors_to_lock", "zones_to_arm", "emergency_contact"]
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        details.append({"item": "包含必要字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {', '.join(missing_fields)}"})
        total_score += 0
    else:
        details.append({"item": "包含必要字段", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10

    # 5. 验证 doors_to_lock (20分)
    # 正确结果: 只有 zone_04 (Main Lobby) 触发了入侵，所以应锁的门是 zone_id 为 zone_04 且状态不为 decommissioned 的门
    # 只有 Front Door (door_04) 是活跃的，Service Entrance 已废弃，不应包含
    expected_doors = ["Front Door"]
    actual_doors = data.get("doors_to_lock", [])
    if isinstance(actual_doors, list) and sorted(actual_doors) == sorted(expected_doors):
        details.append({"item": "doors_to_lock 正确", "score": 20, "max_score": 20, "passed": True, "reason": ""})
        total_score += 20
    else:
        details.append({"item": "doors_to_lock 正确", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 {expected_doors}，实际 {actual_doors}"})

    # 6. 验证 zones_to_arm (20分)
    expected_zones = ["Main Lobby"]
    actual_zones = data.get("zones_to_arm", [])
    if isinstance(actual_zones, list) and sorted(actual_zones) == sorted(expected_zones):
        details.append({"item": "zones_to_arm 正确", "score": 20, "max_score": 20, "passed": True, "reason": ""})
        total_score += 20
    else:
        details.append({"item": "zones_to_arm 正确", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 {expected_zones}，实际 {actual_zones}"})

    # 7. 验证 emergency_contact (20分)
    # 账户 acc_001 包含 zone_04，其 emergency_contacts 是 ["contact_02", "contact_04"]
    # 注意干扰项中有一个重复的 contact_02（旧版），但应取第一个出现（或按规则取），此处我们规定应取 contact_02 和 contact_04
    # 但 prompt 要求输出一个紧急联系人？实际上账户有两个紧急联系人，我们让 Agent 选择哪个？为了唯一答案，我们设计
    # 取 role 为 "Security Manager" 的联系人，即 John Smith (contact_02)。或者取两个？但 prompt 说"紧急联系人"单数？
    # 为了确定性，我们设定应返回 role 为 "Security Manager" 的第一个有效联系人。
    # 从真实数据中 contact_02 是 John Smith, role Security Manager, phone +1-555-0199, email john.smith@example.com
    expected_contact = {
        "name": "John Smith",
        "phone": "+1-555-0199",
        "email": "john.smith@example.com"
    }
    actual_contact = data.get("emergency_contact", {})
    # 比较必要字段（允许额外字段）
    if isinstance(actual_contact, dict) and actual_contact.get("name") == expected_contact["name"] and \
       actual_contact.get("phone") == expected_contact["phone"] and \
       actual_contact.get("email") == expected_contact["email"]:
        details.append({"item": "emergency_contact 正确", "score": 20, "max_score": 20, "passed": True, "reason": ""})
        total_score += 20
    else:
        details.append({"item": "emergency_contact 正确", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 {expected_contact}，实际 {actual_contact}"})

    finalize(details, total_score)

def finalize(details, total_score):
    # 确保总分不超过100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    # 打印简要结果（可选）
    print(f"Score: {total_score}/100")
    sys.exit(0 if total_score >= 60 else 1)  # 60分为及格线

if __name__ == "__main__":
    verify()
