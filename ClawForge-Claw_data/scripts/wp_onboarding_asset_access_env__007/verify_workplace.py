import json
import os
import sys
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. 检查输出目录是否存在 (10分)
    output_dir = Path(workspace) / "output"
    if output_dir.exists() and output_dir.is_dir():
        details.append({"item": "output directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "output/ directory found"})
        total_score += 10
    else:
        details.append({"item": "output directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "output/ directory missing"})
        # 如果目录不存在，后续检查全部0分，直接返回
        return {"total_score": total_score, "details": details}

    # 2. 检查四个产物文件是否存在 (每个5分，共20分)
    required_files = ["email_profile.json", "system_access.json", "equipment_allocation.json", "welcome_message.json"]
    file_scores = 0
    for fname in required_files:
        fpath = output_dir / fname
        if fpath.exists() and fpath.is_file():
            file_scores += 5
            details.append({"item": f"file {fname} exists", "score": 5, "max_score": 5, "passed": True, "reason": "file present"})
        else:
            details.append({"item": f"file {fname} exists", "score": 0, "max_score": 5, "passed": False, "reason": f"file {fname} not found"})
    total_score += file_scores

    # 3. 检查各个文件JSON格式合法性 (每个2.5分，共10分)
    json_valid = True
    for fname in required_files:
        fpath = output_dir / fname
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("root not dict")
        except Exception as e:
            json_valid = False
            details.append({"item": f"{fname} JSON is valid", "score": 0, "max_score": 2.5, "passed": False, "reason": f"invalid JSON: {e}"})
            break
    if json_valid:
        for fname in required_files:
            details.append({"item": f"{fname} JSON is valid", "score": 2.5, "max_score": 2.5, "passed": True, "reason": "valid JSON"})
        total_score += 10

    # 4. 关键字段验证 (共60分)
    # 读取所有文件
    try:
        with open(output_dir / "email_profile.json") as f:
            email_profile = json.load(f)
        with open(output_dir / "system_access.json") as f:
            system_access = json.load(f)
        with open(output_dir / "equipment_allocation.json") as f:
            equip_alloc = json.load(f)
        with open(output_dir / "welcome_message.json") as f:
            welcome = json.load(f)
    except Exception:
        # 如果前面已报JSON无效，这里跳过
        pass
    else:
        # 4.1 email_profile 必须包含 employee_id, email, display_name, department (10分)
        ep_fields = ["employee_id", "email", "display_name", "department"]
        ep_ok = all(k in email_profile for k in ep_fields)
        if ep_ok:
            total_score += 10
            details.append({"item": "email_profile required fields", "score": 10, "max_score": 10, "passed": True, "reason": "all required fields present"})
        else:
            missing = [k for k in ep_fields if k not in email_profile]
            details.append({"item": "email_profile required fields", "score": 0, "max_score": 10, "passed": False, "reason": f"missing fields: {missing}"})

        # 4.2 email_profile 中 employee_id 必须是 EMP_007 (5分)
        if email_profile.get("employee_id") == "EMP_007":
            total_score += 5
            details.append({"item": "email_profile.employee_id correct", "score": 5, "max_score": 5, "passed": True, "reason": "employee_id is EMP_007"})
        else:
            details.append({"item": "email_profile.employee_id correct", "score": 0, "max_score": 5, "passed": False, "reason": f"got {email_profile.get('employee_id')}"})

        # 4.3 email_profile 中 email 必须为 emma.chen@company.com (5分)
        expected_email = "emma.chen@company.com"
        if email_profile.get("email") == expected_email:
            total_score += 5
            details.append({"item": "email_profile.email correct", "score": 5, "max_score": 5, "passed": True, "reason": "email matches"})
        else:
            details.append({"item": "email_profile.email correct", "score": 0, "max_score": 5, "passed": False, "reason": f"got {email_profile.get('email')}"})

        # 4.4 system_access 必须包含 employee_id, systems, access_granted (6分)
        sa_fields = ["employee_id", "systems", "access_granted"]
        sa_ok = all(k in system_access for k in sa_fields)
        if sa_ok:
            total_score += 6
            details.append({"item": "system_access required fields", "score": 6, "max_score": 6, "passed": True, "reason": "all required fields present"})
        else:
            missing = [k for k in sa_fields if k not in system_access]
            details.append({"item": "system_access required fields", "score": 0, "max_score": 6, "passed": False, "reason": f"missing fields: {missing}"})

        # 4.5 system_access.systems 必须是 engineering 权限包的系统列表 (6分)
        expected_systems = ["github", "jenkins", "aws", "k8s"]
        actual_systems = system_access.get("systems", [])
        if sorted(actual_systems) == sorted(expected_systems):
            total_score += 6
            details.append({"item": "system_access.systems correct", "score": 6, "max_score": 6, "passed": True, "reason": "systems match engineering pack"})
        else:
            details.append({"item": "system_access.systems correct", "score": 0, "max_score": 6, "passed": False, "reason": f"got {actual_systems}"})

        # 4.6 system_access.access_granted 必须为 true (3分)
        if system_access.get("access_granted") is True:
            total_score += 3
            details.append({"item": "system_access.access_granted true", "score": 3, "max_score": 3, "passed": True, "reason": "access_granted is true"})
        else:
            details.append({"item": "system_access.access_granted true", "score": 0, "max_score": 3, "passed": False, "reason": f"got {system_access.get('access_granted')}"})

        # 4.7 equipment_allocation 必须包含 employee_id, asset_tag, asset_type, allocated (6分)
        ea_fields = ["employee_id", "asset_tag", "asset_type", "allocated"]
        ea_ok = all(k in equip_alloc for k in ea_fields)
        if ea_ok:
            total_score += 6
            details.append({"item": "equipment_allocation required fields", "score": 6, "max_score": 6, "passed": True, "reason": "all required fields present"})
        else:
            missing = [k for k in ea_fields if k not in equip_alloc]
            details.append({"item": "equipment_allocation required fields", "score": 0, "max_score": 6, "passed": False, "reason": f"missing fields: {missing}"})

        # 4.8 equipment_allocation.asset_tag 必须是 LAPTOP-003 (6分)
        expected_tag = "LAPTOP-003"
        if equip_alloc.get("asset_tag") == expected_tag:
            total_score += 6
            details.append({"item": "equipment_allocation.asset_tag correct", "score": 6, "max_score": 6, "passed": True, "reason": "asset_tag is LAPTOP-003"})
        else:
            details.append({"item": "equipment_allocation.asset_tag correct", "score": 0, "max_score": 6, "passed": False, "reason": f"got {equip_alloc.get('asset_tag')}"})

        # 4.9 equipment_allocation.asset_type 必须是 laptop (3分)
        if equip_alloc.get("asset_type") == "laptop":
            total_score += 3
            details.append({"item": "equipment_allocation.asset_type laptop", "score": 3, "max_score": 3, "passed": True, "reason": "asset_type is laptop"})
        else:
            details.append({"item": "equipment_allocation.asset_type laptop", "score": 0, "max_score": 3, "passed": False, "reason": f"got {equip_alloc.get('asset_type')}"})

        # 4.10 equipment_allocation.allocated 必须为 true (3分)
        if equip_alloc.get("allocated") is True:
            total_score += 3
            details.append({"item": "equipment_allocation.allocated true", "score": 3, "max_score": 3, "passed": True, "reason": "allocated is true"})
        else:
            details.append({"item": "equipment_allocation.allocated true", "score": 0, "max_score": 3, "passed": False, "reason": f"got {equip_alloc.get('allocated')}"})

        # 4.11 welcome_message 必须包含 employee_id, channel, message (6分)
        wm_fields = ["employee_id", "channel", "message"]
        wm_ok = all(k in welcome for k in wm_fields)
        if wm_ok:
            total_score += 6
            details.append({"item": "welcome_message required fields", "score": 6, "max_score": 6, "passed": True, "reason": "all required fields present"})
        else:
            missing = [k for k in wm_fields if k not in welcome]
            details.append({"item": "welcome_message required fields", "score": 0, "max_score": 6, "passed": False, "reason": f"missing fields: {missing}"})

        # 4.12 welcome_message.channel 必须为 "#welcome" (2分)
        if welcome.get("channel") == "#welcome":
            total_score += 2
            details.append({"item": "welcome_message.channel correct", "score": 2, "max_score": 2, "passed": True, "reason": "channel is #welcome"})
        else:
            details.append({"item": "welcome_message.channel correct", "score": 0, "max_score": 2, "passed": False, "reason": f"got {welcome.get('channel')}"})

        # 4.13 welcome_message.message 必须包含 "emma.chen@company.com"、"LAPTOP-003" 以及 "github" 等系统 (5分，精确匹配太严格，用包含)
        msg = welcome.get("message", "")
        substrings = ["emma.chen@company.com", "LAPTOP-003", "github", "jenkins", "aws"]
        if all(s in msg for s in substrings):
            total_score += 5
            details.append({"item": "welcome_message.message contains key info", "score": 5, "max_score": 5, "passed": True, "reason": "message includes email, laptop tag, and system names"})
        else:
            missing_subs = [s for s in substrings if s not in msg]
            details.append({"item": "welcome_message.message contains key info", "score": 0, "max_score": 5, "passed": False, "reason": f"missing substrings: {missing_subs}"})

    # 确保总分不超过100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
