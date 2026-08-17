import json
import os
import sys

def verify(workspace):
    details = []
    total = 0

    # 1. 检查结果文件是否存在 (10分)
    result_path = os.path.join(workspace, "ops", "onboarding_complete.json")
    if os.path.isfile(result_path):
        details.append({"item": "结果文件 ops/onboarding_complete.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total += 10
    else:
        details.append({"item": "结果文件 ops/onboarding_complete.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续检查跳过
        write_score(details, total)
        return

    # 2. 解析JSON合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(details, total)
        return

    # 3. 必填字段检查 (20分)
    required_fields = ["employee_id", "employee_name", "email", "systems", "asset_tag", "welcome_message"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({"item": "所有必填字段存在", "score": 20, "max_score": 20, "passed": True, "reason": "字段完整"})
        total += 20
    else:
        details.append({"item": "所有必填字段存在", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {missing}"})
        write_score(details, total)
        return

    # 4. 字段值精确验证 (共60分)
    # 4.1 employee_id (10分)
    if data["employee_id"] == "E046":
        details.append({"item": "employee_id == 'E046'", "score": 10, "max_score": 10, "passed": True, "reason": "正确"})
        total += 10
    else:
        details.append({"item": "employee_id == 'E046'", "score": 0, "max_score": 10, "passed": False, "reason": f"实际值: {data.get('employee_id')}"})

    # 4.2 employee_name (10分)
    if data["employee_name"] == "Alice Wang":
        details.append({"item": "employee_name == 'Alice Wang'", "score": 10, "max_score": 10, "passed": True, "reason": "正确"})
        total += 10
    else:
        details.append({"item": "employee_name == 'Alice Wang'", "score": 0, "max_score": 10, "passed": False, "reason": f"实际值: {data.get('employee_name')}"})

    # 4.3 email (10分) – 必须等于合同中的邮箱
    if data["email"] == "alice.wang@company.com":
        details.append({"item": "email == 'alice.wang@company.com'", "score": 10, "max_score": 10, "passed": True, "reason": "正确"})
        total += 10
    else:
        details.append({"item": "email == 'alice.wang@company.com'", "score": 0, "max_score": 10, "passed": False, "reason": f"实际值: {data.get('email')}"})

    # 4.4 systems (10分) – 必须包含 Engineering 权限包的全部系统
    expected_systems = ["jira", "github", "aws"]
    actual_systems = data.get("systems", [])
    if sorted(actual_systems) == sorted(expected_systems):
        details.append({"item": "systems 包含 jira, github, aws", "score": 10, "max_score": 10, "passed": True, "reason": "正确"})
        total += 10
    else:
        details.append({"item": "systems 包含 jira, github, aws", "score": 0, "max_score": 10, "passed": False, "reason": f"实际值: {actual_systems}"})

    # 4.5 asset_tag (10分) – 必须分配空闲的笔记本 LAPTOP-042
    if data["asset_tag"] == "LAPTOP-042":
        details.append({"item": "asset_tag == 'LAPTOP-042'", "score": 10, "max_score": 10, "passed": True, "reason": "正确"})
        total += 10
    else:
        details.append({"item": "asset_tag == 'LAPTOP-042'", "score": 0, "max_score": 10, "passed": False, "reason": f"实际值: {data.get('asset_tag')}"})

    # 4.6 welcome_message (10分) – 必须包含员工姓名
    msg = data.get("welcome_message", "")
    if "Alice Wang" in msg and len(msg) > 5:
        details.append({"item": "welcome_message 包含 'Alice Wang'", "score": 10, "max_score": 10, "passed": True, "reason": f"消息内容: {msg}"})
        total += 10
    else:
        details.append({"item": "welcome_message 包含 'Alice Wang'", "score": 0, "max_score": 10, "passed": False, "reason": f"实际内容: {msg}"})

    # 写入评分
    write_score(details, total)

def write_score(details, total_score):
    score_dict = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(score_dict, f, indent=2)
    print(f"评分完成，总分: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
