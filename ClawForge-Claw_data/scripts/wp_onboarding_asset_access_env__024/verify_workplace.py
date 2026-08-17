import os
import sys
import json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录存在性（ops 和 slack_cache）
    ops_path = os.path.join(workspace, "ops")
    slack_path = os.path.join(workspace, "slack_cache")
    points_dir = 5
    dir_ok = os.path.isdir(ops_path) and os.path.isdir(slack_path)
    details.append({
        "item": "Output directories exist",
        "score": points_dir if dir_ok else 0,
        "max_score": points_dir,
        "passed": dir_ok,
        "reason": "Both ops/ and slack_cache/ directories found" if dir_ok else "Missing ops/ or slack_cache/"
    })
    if dir_ok:
        total_score += points_dir

    # 2. 检查 ops/onboarding_complete.json 存在且合法 JSON
    complete_path = os.path.join(ops_path, "onboarding_complete.json")
    points_json = 10
    complete_data = None
    if os.path.isfile(complete_path):
        try:
            with open(complete_path, "r") as f:
                complete_data = json.load(f)
            details.append({
                "item": "ops/onboarding_complete.json is valid JSON",
                "score": points_json,
                "max_score": points_json,
                "passed": True,
                "reason": "File exists and parsed successfully"
            })
            total_score += points_json
        except json.JSONDecodeError:
            details.append({
                "item": "ops/onboarding_complete.json is valid JSON",
                "score": 0,
                "max_score": points_json,
                "passed": False,
                "reason": "File exists but is not valid JSON"
            })
    else:
        details.append({
            "item": "ops/onboarding_complete.json exists",
            "score": 0,
            "max_score": points_json,
            "passed": False,
            "reason": "File not found"
        })

    # 3. 检查 slack_cache/onboarding_welcome.json 存在且合法 JSON
    welcome_path = os.path.join(slack_path, "onboarding_welcome.json")
    points_welcome = 10
    welcome_data = None
    if os.path.isfile(welcome_path):
        try:
            with open(welcome_path, "r") as f:
                welcome_data = json.load(f)
            details.append({
                "item": "slack_cache/onboarding_welcome.json is valid JSON",
                "score": points_welcome,
                "max_score": points_welcome,
                "passed": True,
                "reason": "File exists and parsed successfully"
            })
            total_score += points_welcome
        except json.JSONDecodeError:
            details.append({
                "item": "slack_cache/onboarding_welcome.json is valid JSON",
                "score": 0,
                "max_score": points_welcome,
                "passed": False,
                "reason": "File exists but is not valid JSON"
            })
    else:
        details.append({
            "item": "slack_cache/onboarding_welcome.json exists",
            "score": 0,
            "max_score": points_welcome,
            "passed": False,
            "reason": "File not found"
        })

    # 若核心文件缺失，后续检查跳过并给0分
    if complete_data is None:
        # 后续项直接给0
        for item_name, max_s in [("employee_id field", 10), ("email field", 15), ("systems field", 15), 
                                  ("asset_tag field", 10), ("welcome_message field", 10), 
                                  ("welcome message contains key info", 15)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "Core file missing"
            })
        # 返回总分
        return {"total_score": total_score, "details": details}

    # 4. 检查 complete_data 中的字段
    # 4.1 employee_id
    points_eid = 10
    eid = complete_data.get("employee_id")
    if eid == "E2024-024":
        details.append({
            "item": "employee_id field",
            "score": points_eid,
            "max_score": points_eid,
            "passed": True,
            "reason": "Correct employee_id E2024-024"
        })
        total_score += points_eid
    else:
        details.append({
            "item": "employee_id field",
            "score": 0,
            "max_score": points_eid,
            "passed": False,
            "reason": f"Expected E2024-024, got {eid}"
        })

    # 4.2 email 必须为 zhang.wei@company.com
    points_email = 15
    email = complete_data.get("email")
    if email == "zhang.wei@company.com":
        details.append({
            "item": "email field",
            "score": points_email,
            "max_score": points_email,
            "passed": True,
            "reason": "Correct email format"
        })
        total_score += points_email
    else:
        details.append({
            "item": "email field",
            "score": 0,
            "max_score": points_email,
            "passed": False,
            "reason": f"Expected zhang.wei@company.com, got {email}"
        })

    # 4.3 systems 必须排序后等于 ["crm","erp","hr"]
    points_sys = 15
    systems = complete_data.get("systems")
    if isinstance(systems, list) and sorted(systems) == ["crm", "erp", "hr"]:
        details.append({
            "item": "systems field",
            "score": points_sys,
            "max_score": points_sys,
            "passed": True,
            "reason": "Systems list correct (crm, erp, hr)"
        })
        total_score += points_sys
    else:
        details.append({
            "item": "systems field",
            "score": 0,
            "max_score": points_sys,
            "passed": False,
            "reason": f"Expected ['crm','erp','hr'], got {systems}"
        })

    # 4.4 asset_tag 必须为 LAPTOP-042
    points_tag = 10
    tag = complete_data.get("asset_tag")
    if tag == "LAPTOP-042":
        details.append({
            "item": "asset_tag field",
            "score": points_tag,
            "max_score": points_tag,
            "passed": True,
            "reason": "Correct asset_tag LAPTOP-042"
        })
        total_score += points_tag
    else:
        details.append({
            "item": "asset_tag field",
            "score": 0,
            "max_score": points_tag,
            "passed": False,
            "reason": f"Expected LAPTOP-042, got {tag}"
        })

    # 4.5 welcome_message 字段存在且包含关键信息
    points_msg_field = 10
    msg = complete_data.get("welcome_message")
    if msg and isinstance(msg, str):
        details.append({
            "item": "welcome_message field",
            "score": points_msg_field,
            "max_score": points_msg_field,
            "passed": True,
            "reason": "Field exists and is a string"
        })
        total_score += points_msg_field
    else:
        details.append({
            "item": "welcome_message field",
            "score": 0,
            "max_score": points_msg_field,
            "passed": False,
            "reason": "Missing or non-string welcome_message"
        })

    # 4.6 welcome_message 内容必须包含员工名字、邮箱、设备标签和系统列表
    points_msg_content = 15
    content_ok = True
    checks = {
        "employee_name": "Zhang Wei",
        "email": "zhang.wei@company.com",
        "asset_tag": "LAPTOP-042",
        "systems": "crm"  # 至少包含一个系统名即可
    }
    missing = []
    if msg:
        if "Zhang Wei" not in msg:
            missing.append("employee name")
            content_ok = False
        if "zhang.wei@company.com" not in msg:
            missing.append("email")
            content_ok = False
        if "LAPTOP-042" not in msg:
            missing.append("asset tag")
            content_ok = False
        # 检查是否至少出现一个系统
        if not any(s in msg for s in ["crm", "erp", "hr"]):
            missing.append("any system name")
            content_ok = False
    else:
        content_ok = False
        missing.append("welcome_message not available")
    if content_ok:
        details.append({
            "item": "welcome message contains key info",
            "score": points_msg_content,
            "max_score": points_msg_content,
            "passed": True,
            "reason": "Message includes employee name, email, asset tag, and systems"
        })
        total_score += points_msg_content
    else:
        details.append({
            "item": "welcome message contains key info",
            "score": 0,
            "max_score": points_msg_content,
            "passed": False,
            "reason": f"Missing in message: {', '.join(missing)}"
        })

    # 5. 检查 slack 缓存文件内容是否与 complete 一致（至少包含 employee_id 和简单匹配）
    points_welcome_content = 10
    if welcome_data:
        w_eid = welcome_data.get("employee_id")
        w_msg = welcome_data.get("message") or welcome_data.get("welcome_message") 
        # 灵活兼容不同字段名
        if w_msg is None:
            # 尝试找任何字符串值
            for v in welcome_data.values():
                if isinstance(v, str) and "Zhang Wei" in v:
                    w_msg = v
                    break
        if w_eid == "E2024-024" and w_msg and "Zhang Wei" in str(w_msg):
            details.append({
                "item": "slack_cache onboarding_welcome.json content",
                "score": points_welcome_content,
                "max_score": points_welcome_content,
                "passed": True,
                "reason": "Contains employee_id and meaningful message"
            })
            total_score += points_welcome_content
        else:
            details.append({
                "item": "slack_cache onboarding_welcome.json content",
                "score": 0,
                "max_score": points_welcome_content,
                "passed": False,
                "reason": f"Missing correct employee_id or message content. Got eid={w_eid}, msg={w_msg}"
            })
    else:
        details.append({
            "item": "slack_cache onboarding_welcome.json content",
            "score": 0,
            "max_score": points_welcome_content,
            "passed": False,
            "reason": "No welcome file available"
        })

    # 总分上限100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
