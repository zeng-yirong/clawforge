import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0
    max_total = 100

    # 1. 检查必要目录是否存在 (10分)
    dirs = ["email_profiles", "system_access", "equipment/assigned", "slack"]
    dir_score = 0
    for d in dirs:
        if os.path.isdir(d):
            dir_score += 2.5
    details.append({
        "item": "Required directories exist",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": f"Found {int(dir_score/2.5)}/4 directories"
    })
    total_score += dir_score

    # 2. 检查 email_profiles 下是否有 Alice 的档案 (15分)
    alice_profile_path = "email_profiles/Alice_Smith.json"
    profile_score = 0
    profile_reason = ""
    if os.path.isfile(alice_profile_path):
        try:
            with open(alice_profile_path) as f:
                profile = json.load(f)
            # 必须包含 employee_id, employee_name, email, department
            expected_fields = ["employee_id", "employee_name", "email", "department"]
            if all(field in profile for field in expected_fields):
                if profile.get("employee_name") == "Alice Smith":
                    if profile.get("email") == "alice.smith@company.com":
                        profile_score = 15
                        profile_reason = "Valid Alice profile with correct email"
                    else:
                        profile_score = 10
                        profile_reason = "Profile exists but email doesn't match expected format"
                else:
                    profile_score = 5
                    profile_reason = "Profile name mismatch"
            else:
                profile_score = 5
                profile_reason = "Missing required fields"
        except (json.JSONDecodeError, IOError):
            profile_reason = "File unreadable or invalid JSON"
    else:
        profile_reason = "File not found"
    details.append({
        "item": "Alice email profile",
        "score": profile_score,
        "max_score": 15,
        "passed": profile_score == 15,
        "reason": profile_reason
    })
    total_score += profile_score

    # 3. 检查 system_access 下 Alice 的权限文件 (20分)
    alice_access_path = "system_access/Alice_Smith_systems.json"
    access_score = 0
    access_reason = ""
    if os.path.isfile(alice_access_path):
        try:
            with open(alice_access_path) as f:
                access = json.load(f)
            # 必须包含 employee_id, systems 列表，且 systems 应与 Engineering 标准包一致
            if "employee_id" in access and "systems" in access:
                expected_systems = ["gitlab", "jenkins", "aws-dev", "jira"]
                actual_systems = access["systems"]
                if sorted(actual_systems) == sorted(expected_systems):
                    access_score = 20
                    access_reason = "Correct system permissions for Engineering"
                else:
                    access_score = 10
                    access_reason = f"Systems mismatch: got {actual_systems}, expected {expected_systems}"
            else:
                access_score = 5
                access_reason = "Missing fields employee_id or systems"
        except (json.JSONDecodeError, IOError):
            access_reason = "File unreadable"
    else:
        access_reason = "File not found"
    details.append({
        "item": "System access assignment",
        "score": access_score,
        "max_score": 20,
        "passed": access_score == 20,
        "reason": access_reason
    })
    total_score += access_score

    # 4. 检查 equipment/assigned 下 Alice 的设备 (20分)
    alice_equip_path = "equipment/assigned/Alice_Smith_laptop.json"
    equip_score = 0
    equip_reason = ""
    if os.path.isfile(alice_equip_path):
        try:
            with open(alice_equip_path) as f:
                equip = json.load(f)
            # 必须包含 asset_tag, asset_type, assigned_to
            if "asset_tag" in equip and "asset_type" in equip and "assigned_to" in equip:
                if equip["asset_type"] == "laptop" and equip["assigned_to"] == "Alice Smith":
                    # 检查 asset_tag 是否为第一台可用笔记本 LAP-001
                    if equip["asset_tag"] == "LAP-001":
                        equip_score = 20
                        equip_reason = "Correct laptop assignment (first available)"
                    else:
                        equip_score = 10
                        equip_reason = f"Wrong asset tag: {equip['asset_tag']}, expected LAP-001"
                else:
                    equip_score = 5
                    equip_reason = "Asset type or assignee incorrect"
            else:
                equip_score = 5
                equip_reason = "Missing required fields"
        except (json.JSONDecodeError, IOError):
            equip_reason = "File unreadable"
    else:
        equip_reason = "File not found"
    details.append({
        "item": "Equipment allocation",
        "score": equip_score,
        "max_score": 20,
        "passed": equip_score == 20,
        "reason": equip_reason
    })
    total_score += equip_score

    # 5. 检查 Slack 欢迎消息 (20分)
    slack_path = "slack/welcome_cache.json"
    slack_score = 0
    slack_reason = ""
    if os.path.isfile(slack_path):
        try:
            with open(slack_path) as f:
                slack_data = json.load(f)
            # 期望结构：{"channel": "#general", "message": "Welcome aboard, Alice Smith!"}
            if isinstance(slack_data, dict):
                if "channel" in slack_data and "message" in slack_data:
                    if slack_data["channel"] == "#general":
                        msg = slack_data["message"]
                        if "Alice Smith" in msg and "welcome" in msg.lower():
                            slack_score = 20
                            slack_reason = "Valid welcome message"
                        else:
                            slack_score = 10
                            slack_reason = "Message content incorrect"
                    else:
                        slack_score = 5
                        slack_reason = "Wrong channel"
                else:
                    slack_score = 5
                    slack_reason = "Missing channel/message fields"
            else:
                slack_score = 5
                slack_reason = "Not a dict"
        except (json.JSONDecodeError, IOError):
            slack_reason = "File unreadable"
    else:
        slack_reason = "File not found"
    details.append({
        "item": "Slack welcome message",
        "score": slack_score,
        "max_score": 20,
        "passed": slack_score == 20,
        "reason": slack_reason
    })
    total_score += slack_score

    # 6. 检查是否有多余的干扰文件 (5分) - 不允许在根目录创建未知文件
    extra_score = 5
    extra_reason = ""
    allowed_dirs = {"data", "email_profiles", "system_access", "equipment", "slack", "tasks", "scripts", "assets"}
    root_files = [f for f in os.listdir(".") if os.path.isfile(f)]
    forbidden = [f for f in root_files if f not in ["workplace_score.json"] and not f.startswith(".")]
    if forbidden:
        extra_score = 0
        extra_reason = f"Unexpected files in root: {forbidden}"
    else:
        extra_reason = "No extra files"
    details.append({
        "item": "No unintended root files",
        "score": extra_score,
        "max_score": 5,
        "passed": extra_score == 5,
        "reason": extra_reason
    })
    total_score += extra_score

    # 7. 检查 email_profiles 目录下是否只有 Alice 的档案 (5分)
    profile_dir_clean = True
    profile_dir_reason = ""
    profiles = [f for f in os.listdir("email_profiles") if f.endswith(".json")]
    if len(profiles) != 1 or profiles[0] != "Alice_Smith.json":
        profile_dir_clean = False
        profile_dir_reason = f"Expected only Alice_Smith.json, found {profiles}"
    else:
        profile_dir_reason = "Only Alice profile present"
    details.append({
        "item": "Email profile directory cleanliness",
        "score": 5 if profile_dir_clean else 0,
        "max_score": 5,
        "passed": profile_dir_clean,
        "reason": profile_dir_reason
    })
    total_score += 5 if profile_dir_clean else 0

    # 8. 检查 system_access 目录是否只有 Alice 的文件 (5分)
    access_dir_clean = True
    access_dir_reason = ""
    access_files = [f for f in os.listdir("system_access") if f.endswith(".json")]
    if len(access_files) != 1 or access_files[0] != "Alice_Smith_systems.json":
        access_dir_clean = False
        access_dir_reason = f"Expected only Alice_Smith_systems.json, found {access_files}"
    else:
        access_dir_reason = "Only Alice access file present"
    details.append({
        "item": "System access directory cleanliness",
        "score": 5 if access_dir_clean else 0,
        "max_score": 5,
        "passed": access_dir_clean,
        "reason": access_dir_reason
    })
    total_score += 5 if access_dir_clean else 0

    # 总分上限100
    final_score = min(total_score, 100)

    result = {
        "total_score": final_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {final_score}/100")

if __name__ == "__main__":
    main()
