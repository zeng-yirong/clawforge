import sys, os, json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 检查 ops 目录存在
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    results.append({
        "item": "ops目录存在",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "ops目录存在" if dir_exists else "ops目录不存在"
    })
    if dir_exists:
        total_score += 5

    # 2. 检查目标文件存在
    summary_path = os.path.join(ops_path, "onboarding_summary.json")
    file_exists = os.path.isfile(summary_path)
    results.append({
        "item": "ops/onboarding_summary.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })
    if file_exists:
        total_score += 10
    else:
        # 如果文件不存在，后续项直接0分
        _finalize(results, total_score, workspace)
        return

    # 3. JSON 合法性
    try:
        with open(summary_path, "r") as f:
            data = json.load(f)
        json_valid = True
        json_reason = "JSON解析成功"
    except (json.JSONDecodeError, Exception) as e:
        json_valid = False
        json_reason = f"JSON解析失败: {e}"
    results.append({
        "item": "JSON格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": json_reason
    })
    if json_valid:
        total_score += 10
    else:
        _finalize(results, total_score, workspace)
        return

    # 4. 数据结构检查：允许对象或单元素数组
    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        records = []
    if len(records) != 1:
        results.append({
            "item": "记录数量",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"期望1条记录，实际{len(records)}条"
        })
        total_score += 0
        _finalize(results, total_score, workspace)
        return
    else:
        results.append({
            "item": "记录数量",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "正确1条记录"
        })
        total_score += 5

    record = records[0]

    # 5. 检查 employee_id
    emp_id = record.get("employee_id")
    emp_correct = (emp_id == "E001")
    results.append({
        "item": "员工ID正确",
        "score": 10 if emp_correct else 0,
        "max_score": 10,
        "passed": emp_correct,
        "reason": f"employee_id = {emp_id!r}" if not emp_correct else "正确"
    })
    if emp_correct:
        total_score += 10

    # 6. 检查 email_profile
    email_profile = record.get("email_profile")
    email_ok = False
    email_reason = ""
    if isinstance(email_profile, dict):
        addr = email_profile.get("address", "")
        if addr == "emily.chen@ourcompany.com":
            email_ok = True
            email_reason = "正确"
        else:
            email_reason = f"address 应为 emily.chen@ourcompany.com，实际为 {addr!r}"
    else:
        email_reason = f"email_profile 不是字典，类型 {type(email_profile).__name__}"
    results.append({
        "item": "邮箱地址正确",
        "score": 20 if email_ok else 0,
        "max_score": 20,
        "passed": email_ok,
        "reason": email_reason
    })
    if email_ok:
        total_score += 20

    # 7. 检查 system_access
    sys_access = record.get("system_access")
    sys_ok = False
    sys_reason = ""
    if isinstance(sys_access, dict):
        pack_id = sys_access.get("pack_id")
        systems = sys_access.get("systems")
        if pack_id == "P001" and systems == ["CRM", "ERP"]:
            sys_ok = True
            sys_reason = "正确"
        else:
            sys_reason = f"期望 pack_id=P001, systems=[CRM,ERP]，实际 pack_id={pack_id!r}, systems={systems!r}"
    else:
        sys_reason = f"system_access 不是字典，类型 {type(sys_access).__name__}"
    results.append({
        "item": "系统权限分配正确",
        "score": 20 if sys_ok else 0,
        "max_score": 20,
        "passed": sys_ok,
        "reason": sys_reason
    })
    if sys_ok:
        total_score += 20

    # 8. 检查 equipment
    equip = record.get("equipment")
    equip_ok = False
    equip_reason = ""
    if isinstance(equip, dict):
        tag = equip.get("asset_tag")
        atype = equip.get("asset_type")
        if tag == "LAPTOP-001" and atype == "laptop":
            equip_ok = True
            equip_reason = "正确"
        else:
            equip_reason = f"期望 asset_tag=LAPTOP-001, asset_type=laptop，实际 tag={tag!r}, type={atype!r}"
    else:
        equip_reason = f"equipment 不是字典，类型 {type(equip).__name__}"
    results.append({
        "item": "设备分配正确",
        "score": 15 if equip_ok else 0,
        "max_score": 15,
        "passed": equip_ok,
        "reason": equip_reason
    })
    if equip_ok:
        total_score += 15

    # 9. 检查 welcome_message
    welcome = record.get("welcome_message")
    welcome_ok = False
    welcome_reason = ""
    if isinstance(welcome, str) and "Emily" in welcome:
        welcome_ok = True
        welcome_reason = "包含员工姓名"
    else:
        welcome_reason = f"welcome_message 不存在或不包含 Emily，实际 {welcome!r}"
    results.append({
        "item": "欢迎消息包含员工姓名",
        "score": 5 if welcome_ok else 0,
        "max_score": 5,
        "passed": welcome_ok,
        "reason": welcome_reason
    })
    if welcome_ok:
        total_score += 5

    # 最终输出
    _finalize(results, total_score, workspace)

def _finalize(results, total_score, workspace):
    # 限制总分不超过100
    total_score = min(total_score, 100)
    output = {
        "total_score": total_score,
        "details": results
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
