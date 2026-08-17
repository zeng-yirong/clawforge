import os
import sys
import json
import re

def check_file_exists(filepath):
    return os.path.isfile(filepath)

def parse_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def main():
    if len(sys.argv) > 1:
        workspace = sys.argv[1]
    else:
        workspace = "."
    os.chdir(workspace)

    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录是否存在 (5分)
    item = {"item": "ops 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if os.path.isdir("ops"):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops 目录已创建"
    else:
        item["reason"] = "缺少 ops 目录"
    total_score += item["score"]
    details.append(item)

    # 2. 检查 onboarding_result.json 是否存在 (10分)
    result_path = "ops/onboarding_result.json"
    item = {"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if check_file_exists(result_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "onboarding_result.json 存在"
    else:
        item["reason"] = "文件不存在"
    total_score += item["score"]
    details.append(item)

    # 3. JSON 合法性 (10分)
    item = {"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    data = parse_json(result_path)
    if data is not None:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "JSON 解析成功"
    else:
        item["reason"] = "JSON 解析失败或文件不可读"
    total_score += item["score"]
    details.append(item)

    if data is None:
        # 无法继续检查，直接输出
        final_score = total_score
        result = {"total_score": final_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result, indent=2))
        return

    # 4. 检查必填字段 (employee_id, employee_name, email, system_access, equipment, welcome_message) (20分)
    expected_fields = ["employee_id", "employee_name", "email", "system_access", "equipment", "welcome_message"]
    found_fields = [f for f in expected_fields if f in data]
    missing_fields = [f for f in expected_fields if f not in data]
    item = {"item": "必要字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if len(missing_fields) == 0:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"所有必要字段都存在: {', '.join(expected_fields)}"
    else:
        item["score"] = 20 - len(missing_fields) * 4
        item["reason"] = f"缺少字段: {', '.join(missing_fields)}"
    total_score += item["score"]
    details.append(item)

    # 5. 检查 employee_id 是否为 EMP003 (10分)
    item = {"item": "员工ID正确", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if data.get("employee_id") == "EMP003":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "employee_id 为 EMP003"
    else:
        item["reason"] = f"实际值: {data.get('employee_id', '未设置')}"
    total_score += item["score"]
    details.append(item)

    # 6. 检查 employee_name 为 "Jane Doe" (5分)
    item = {"item": "员工姓名正确", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if data.get("employee_name") == "Jane Doe":
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "employee_name 为 Jane Doe"
    else:
        item["reason"] = f"实际值: {data.get('employee_name', '未设置')}"
    total_score += item["score"]
    details.append(item)

    # 7. 检查 email 格式 (名.姓@company.com) (10分)
    item = {"item": "邮箱格式正确", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    email = data.get("email", "")
    if re.match(r"^[a-z]+\.[a-z]+@company\.com$", email):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"邮箱格式正确: {email}"
    else:
        item["reason"] = f"邮箱格式异常: {email}"
    total_score += item["score"]
    details.append(item)

    # 8. 检查 system_access 列表内容 (必须包含 Engineering 权限包内的所有系统) (15分)
    item = {"item": "系统访问列表完整", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    expected_systems = {"Jira", "GitLab", "Confluence", "AWS-Dev", "DockerHub"}
    actual_systems = set(data.get("system_access", []))
    if actual_systems == expected_systems:
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "系统访问列表完全匹配 Engineering 权限包"
    else:
        missing = expected_systems - actual_systems
        extra = actual_systems - expected_systems
        reasons = []
        if missing:
            reasons.append(f"缺少: {', '.join(missing)}")
        if extra:
            reasons.append(f"多余: {', '.join(extra)}")
        item["reason"] = "; ".join(reasons) if reasons else "列表不匹配"
    total_score += item["score"]
    details.append(item)

    # 9. 检查 equipment 资产标签 (必须是空闲的笔记本 LT-102 或 LT-103，但答案是 LT-102) (10分)
    item = {"item": "设备资产标签正确", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    asset_tag = data.get("equipment", "")
    # 预期是从空闲笔记本中选的，唯一确定的是 LT-102（因为 LT-103 也是空闲，但为了唯一性，我们要求 LT-102）
    if asset_tag == "LT-102":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "设备为 LT-102 (正确的空闲笔记本)"
    elif asset_tag == "LT-103":
        # 虽然也空闲，但不是期望值，算部分正确
        item["score"] = 5
        item["passed"] = False
        item["reason"] = "设备为 LT-103 (也是空闲笔记本，但标准选择为 LT-102)"
    else:
        item["reason"] = f"实际设备: {asset_tag}"
    total_score += item["score"]
    details.append(item)

    # 10. 检查 welcome_message 是否包含 Jane Doe 字符串 (5分)
    item = {"item": "欢迎消息包含员工名字", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    welcome = data.get("welcome_message", "")
    if "Jane Doe" in welcome:
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "欢迎消息中包含 'Jane Doe'"
    else:
        item["reason"] = f"欢迎消息中未找到 Jane Doe: {welcome[:50]}"
    total_score += item["score"]
    details.append(item)

    # 计算最终总分（确保不超过100）
    final_total = min(total_score, 100)
    result = {"total_score": final_total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
