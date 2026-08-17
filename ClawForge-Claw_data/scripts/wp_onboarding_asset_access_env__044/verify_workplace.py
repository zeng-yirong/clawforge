import os
import json
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(os.path.join(workspace, path), "r") as f:
        return json.load(f)

def score_item(details, name, score, max_score, passed, reason):
    details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

def main():
    details = []
    total = 0

    # ---- 0. 目录结构检查 (10分) ----
    dirs = ["profiles", "access", "equipment/allocations", "slack"]
    dir_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in dirs)
    if dir_ok:
        score_item(details, "Required directories exist", 10, 10, True, "All 4 directories present")
        total += 10
    else:
        missing = [d for d in dirs if not os.path.isdir(os.path.join(workspace, d))]
        score_item(details, "Required directories exist", 0, 10, False, f"Missing: {missing}")
        # 如果目录不存在，后面的文件也无法存在，直接终止并提供硬错误
        # 但为了分数明细完整，继续但后续项给0分

    # ---- 1. profiles 文件 (20分) ----
    profile_path = os.path.join(workspace, "profiles", "alice_wang.json")
    profile_points = 0
    if os.path.isfile(profile_path):
        try:
            with open(profile_path) as f:
                profile = json.load(f)
            if isinstance(profile, dict):
                expected_fields = {"employee_id", "email", "display_name", "department"}
                if expected_fields.issubset(profile.keys()):
                    if profile.get("employee_id") == "E001" and profile.get("email") == "alice@company.com":
                        profile_points = 20
                        score_item(details, "Profile file content correct", 20, 20, True, "All fields and values match")
                    else:
                        score_item(details, "Profile file fields correct but values wrong", 10, 20, False,
                                   f"employee_id or email mismatch")
                else:
                    missing = expected_fields - set(profile.keys())
                    score_item(details, "Profile file missing fields", 5, 20, False, f"Missing: {missing}")
            else:
                score_item(details, "Profile file not a JSON object", 0, 20, False, "")
        except (json.JSONDecodeError, IOError):
            score_item(details, "Profile file invalid JSON", 0, 20, False, "")
    else:
        score_item(details, "Profile file missing", 0, 20, False, "Expected profiles/alice_wang.json")
    total += profile_points

    # ---- 2. access 文件 (20分) ----
    access_path = os.path.join(workspace, "access", "alice_wang.json")
    access_points = 0
    if os.path.isfile(access_path):
        try:
            with open(access_path) as f:
                access = json.load(f)
            if isinstance(access, dict):
                # 应该包含 employee_id 和 systems
                if "employee_id" in access and "systems" in access:
                    expected_systems = ["gitlab", "jenkins", "k8s-dev", "jira"]
                    if access["employee_id"] == "E001" and set(access["systems"]) == set(expected_systems):
                        access_points = 20
                        score_item(details, "Access file content correct", 20, 20, True, "Systems match Engineering pack")
                    else:
                        score_item(details, "Access file fields present but values wrong", 10, 20, False,
                                   f"employee_id or systems mismatch")
                else:
                    score_item(details, "Access file missing employee_id or systems", 5, 20, False, "")
            else:
                score_item(details, "Access file not a JSON object", 0, 20, False, "")
        except (json.JSONDecodeError, IOError):
            score_item(details, "Access file invalid JSON", 0, 20, False, "")
    else:
        score_item(details, "Access file missing", 0, 20, False, "Expected access/alice_wang.json")
    total += access_points

    # ---- 3. equipment 分配 (20分) ----
    equip_path = os.path.join(workspace, "equipment", "allocations", "alice_wang.json")
    equip_points = 0
    if os.path.isfile(equip_path):
        try:
            with open(equip_path) as f:
                equip = json.load(f)
            if isinstance(equip, dict):
                if "employee_id" in equip and "asset_tag" in equip:
                    if equip["employee_id"] == "E001" and equip["asset_tag"] == "LAP-001":
                        equip_points = 20
                        score_item(details, "Equipment allocation correct", 20, 20, True, "Assigned available laptop LAP-001")
                    else:
                        score_item(details, "Equipment allocation fields present but values wrong", 10, 20, False,
                                   f"employee_id or asset_tag mismatch")
                else:
                    score_item(details, "Equipment allocation missing employee_id or asset_tag", 5, 20, False, "")
            else:
                score_item(details, "Equipment allocation not a JSON object", 0, 20, False, "")
        except (json.JSONDecodeError, IOError):
            score_item(details, "Equipment allocation invalid JSON", 0, 20, False, "")
    else:
        score_item(details, "Equipment allocation file missing", 0, 20, False, "Expected equipment/allocations/alice_wang.json")
    total += equip_points

    # ---- 4. Slack 欢迎消息 (30分) ----
    slack_path = os.path.join(workspace, "slack", "welcome.json")
    slack_points = 0
    if os.path.isfile(slack_path):
        try:
            with open(slack_path) as f:
                slack = json.load(f)
            if isinstance(slack, dict):
                # 必须包含 recipient 和 message
                if "recipient" in slack and "message" in slack:
                    rec = slack["recipient"]
                    msg = slack["message"]
                    # recipient 应该为 alice@company.com 或 "Alice Wang"
                    if rec in ("alice@company.com", "Alice Wang", "E001"):
                        if "Welcome" in msg and "Alice" in msg:
                            slack_points = 30
                            score_item(details, "Slack welcome message correct", 30, 30, True, "Recipient and welcome text present")
                        else:
                            slack_points = 15
                            score_item(details, "Slack welcome message has recipient but missing welcome text", 15, 30, False,
                                       "Message should contain 'Welcome' and 'Alice'")
                    else:
                        slack_points = 10
                        score_item(details, "Slack welcome message wrong recipient", 10, 30, False, f"Expected alice@company.com got {rec}")
                else:
                    slack_points = 5
                    score_item(details, "Slack welcome file missing recipient or message", 5, 30, False, "")
            else:
                slack_points = 0
                score_item(details, "Slack welcome file not a JSON object", 0, 30, False, "")
        except (json.JSONDecodeError, IOError):
            slack_points = 0
            score_item(details, "Slack welcome file invalid JSON", 0, 30, False, "")
    else:
        slack_points = 0
        score_item(details, "Slack welcome file missing", 0, 30, False, "Expected slack/welcome.json")
    total += slack_points

    # 总分写入
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Total score: {total}/100")

if __name__ == "__main__":
    main()
