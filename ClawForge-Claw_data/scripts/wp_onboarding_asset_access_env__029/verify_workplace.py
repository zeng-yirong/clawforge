import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 定义预期的文件路径和内容
    expected_output_files = [
        "output/email_profile.json",
        "output/system_access.json",
        "output/equipment_allocation.json",
        "output/welcome_message.json"
    ]

    # ---------- 1. 目录结构检查 (5分) ----------
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        details.append({"item": "output directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "output/ exists"})
        total_score += 5
    else:
        details.append({"item": "output directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "output/ not found"})
        # 如果目录不存在，后续文件检查会全错，但先记录
        for fname in expected_output_files:
            details.append({"item": f"File {fname} exists", "score": 0, "max_score": 5, "passed": False, "reason": "output dir missing"})
        # 跳过后续检查
        write_score(details, total_score, workspace)
        return

    # ---------- 2. 文件存在性检查 (5分 * 4 = 20分) ----------
    for fpath in expected_output_files:
        full_path = os.path.join(workspace, fpath)
        if os.path.isfile(full_path):
            details.append({"item": f"File {fpath} exists", "score": 5, "max_score": 5, "passed": True, "reason": "File present"})
            total_score += 5
        else:
            details.append({"item": f"File {fpath} exists", "score": 0, "max_score": 5, "passed": False, "reason": "File not found"})

    # 如果存在性有缺失，仍然尝试解析已有文件，但失分项已记录
    # ---------- 3. JSON 格式合法性 (5分 * 4 = 20分) ----------
    json_files = {}
    for fpath in expected_output_files:
        full_path = os.path.join(workspace, fpath)
        if not os.path.isfile(full_path):
            details.append({"item": f"JSON format {fpath}", "score": 0, "max_score": 5, "passed": False, "reason": "File missing, cannot validate format"})
            continue
        try:
            with open(full_path, "r") as f:
                data = json.load(f)
            json_files[fpath] = data
            details.append({"item": f"JSON format {fpath}", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
            total_score += 5
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": f"JSON format {fpath}", "score": 0, "max_score": 5, "passed": False, "reason": f"Invalid JSON: {str(e)[:50]}"})

    # ---------- 4. 关键字段内容检查 (50分) ----------
    # 4.1 email_profile.json (15分)
    email_data = json_files.get("output/email_profile.json")
    if email_data is not None:
        # 检查必含字段
        expected_fields = ["email", "display_name", "department"]
        missing_fields = [f for f in expected_fields if f not in email_data]
        if missing_fields:
            details.append({"item": "email_profile.json required fields", "score": 0, "max_score": 15, "passed": False, "reason": f"Missing fields: {missing_fields}"})
        else:
            # 检查具体值
            correct_email = "alex.johnson@company.com"
            correct_name = "Alex Johnson"
            correct_dept = "Engineering"
            e_score = 0
            field_reasons = []
            if email_data.get("email") == correct_email:
                e_score += 5
            else:
                field_reasons.append(f"email expected {correct_email}, got {email_data.get('email')}")
            if email_data.get("display_name") == correct_name:
                e_score += 5
            else:
                field_reasons.append(f"display_name expected {correct_name}, got {email_data.get('display_name')}")
            if email_data.get("department") == correct_dept:
                e_score += 5
            else:
                field_reasons.append(f"department expected {correct_dept}, got {email_data.get('department')}")
            reason = "; ".join(field_reasons) if field_reasons else "All fields correct"
            passed = e_score == 15
            details.append({"item": "email_profile.json field values", "score": e_score, "max_score": 15, "passed": passed, "reason": reason})
            total_score += e_score
    else:
        details.append({"item": "email_profile.json field values", "score": 0, "max_score": 15, "passed": False, "reason": "File not loadable"})

    # 4.2 system_access.json (15分)
    sys_data = json_files.get("output/system_access.json")
    if sys_data is not None:
        expected_fields = ["employee_id", "pack_id", "systems"]
        missing = [f for f in expected_fields if f not in sys_data]
        if missing:
            details.append({"item": "system_access.json required fields", "score": 0, "max_score": 15, "passed": False, "reason": f"Missing fields: {missing}"})
        else:
            s_score = 0
            s_reasons = []
            if sys_data.get("employee_id") == "E-1001":
                s_score += 5
            else:
                s_reasons.append(f"employee_id expected 'E-1001', got {sys_data.get('employee_id')}")
            if sys_data.get("pack_id") == "pack_engineering":
                s_score += 5
            else:
                s_reasons.append(f"pack_id expected 'pack_engineering', got {sys_data.get('pack_id')}")
            # systems 必须与包中完全一致，顺序忽略
            expected_systems = ["jenkins", "jira", "github"]
            actual_systems = sys_data.get("systems")
            if isinstance(actual_systems, list) and sorted(actual_systems) == sorted(expected_systems):
                s_score += 5
            else:
                s_reasons.append(f"systems expected {expected_systems}, got {actual_systems}")
            passed = s_score == 15
            reason = "; ".join(s_reasons) if s_reasons else "All fields correct"
            details.append({"item": "system_access.json field values", "score": s_score, "max_score": 15, "passed": passed, "reason": reason})
            total_score += s_score
    else:
        details.append({"item": "system_access.json field values", "score": 0, "max_score": 15, "passed": False, "reason": "File not loadable"})

    # 4.3 equipment_allocation.json (10分)
    equip_data = json_files.get("output/equipment_allocation.json")
    if equip_data is not None:
        expected_fields = ["asset_tag", "asset_type", "assigned_to"]
        missing = [f for f in expected_fields if f not in equip_data]
        if missing:
            details.append({"item": "equipment_allocation.json required fields", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields: {missing}"})
        else:
            eq_score = 0
            eq_reasons = []
            # asset_tag 必须是 "LT-001"
            if equip_data.get("asset_tag") == "LT-001":
                eq_score += 4
            else:
                eq_reasons.append(f"asset_tag expected 'LT-001', got {equip_data.get('asset_tag')}")
            # asset_type 必须是 "laptop"
            if equip_data.get("asset_type") == "laptop":
                eq_score += 3
            else:
                eq_reasons.append(f"asset_type expected 'laptop', got {equip_data.get('asset_type')}")
            # assigned_to 可以是员工名或员工邮箱，这里我们接受 "Alex Johnson" 或 "alex.johnson@company.com" 结合前面
            assigned = equip_data.get("assigned_to")
            if assigned in ("Alex Johnson", "alex.johnson@company.com"):
                eq_score += 3
            else:
                eq_reasons.append(f"assigned_to expected 'Alex Johnson' or 'alex.johnson@company.com', got {assigned}")
            passed = eq_score == 10
            reason = "; ".join(eq_reasons) if eq_reasons else "All fields correct"
            details.append({"item": "equipment_allocation.json field values", "score": eq_score, "max_score": 10, "passed": passed, "reason": reason})
            total_score += eq_score
    else:
        details.append({"item": "equipment_allocation.json field values", "score": 0, "max_score": 10, "passed": False, "reason": "File not loadable"})

    # 4.4 welcome_message.json (10分)
    welcome_data = json_files.get("output/welcome_message.json")
    if welcome_data is not None:
        expected_fields = ["recipient", "message"]
        missing = [f for f in expected_fields if f not in welcome_data]
        if missing:
            details.append({"item": "welcome_message.json required fields", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields: {missing}"})
        else:
            w_score = 0
            w_reasons = []
            # recipient 必须是 "alex.johnson@company.com"
            if welcome_data.get("recipient") == "alex.johnson@company.com":
                w_score += 4
            else:
                w_reasons.append(f"recipient expected 'alex.johnson@company.com', got {welcome_data.get('recipient')}")
            # message 必须包含 "Alex" 和 "Engineering"（忽略大小写）
            msg = welcome_data.get("message", "")
            if not isinstance(msg, str):
                w_reasons.append("message is not a string")
            else:
                if "Alex" in msg:
                    w_score += 3
                else:
                    w_reasons.append("message missing 'Alex'")
                if "Engineering" in msg:
                    w_score += 3
                else:
                    w_reasons.append("message missing 'Engineering'")
            passed = w_score == 10
            reason = "; ".join(w_reasons) if w_reasons else "All fields correct"
            details.append({"item": "welcome_message.json field values", "score": w_score, "max_score": 10, "passed": passed, "reason": reason})
            total_score += w_score
    else:
        details.append({"item": "welcome_message.json field values", "score": 0, "max_score": 10, "passed": False, "reason": "File not loadable"})

    # 额外扣分：不允许出现非预期的额外输出文件（除了四个文件之外的文件在output/内）
    extra_files = []
    if os.path.isdir(output_dir):
        for fname in os.listdir(output_dir):
            full = os.path.join(output_dir, fname)
            if os.path.isfile(full) and fname not in ["email_profile.json", "system_access.json", "equipment_allocation.json", "welcome_message.json"]:
                extra_files.append(fname)
    if extra_files:
        # 每个多余文件扣3分，最多扣9分
        penalty = min(len(extra_files) * 3, 9)
        total_score = max(0, total_score - penalty)
        details.append({"item": "No extra files in output/", "score": -penalty, "max_score": 0, "passed": False, "reason": f"Extra files: {extra_files}"})
    else:
        details.append({"item": "No extra files in output/", "score": 0, "max_score": 0, "passed": True, "reason": "Only expected files"})

    # 最终总分写入
    total_score = min(total_score, 100)
    write_score(details, total_score, workspace)


def write_score(details, total, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")


if __name__ == "__main__":
    main()
