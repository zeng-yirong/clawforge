import json
import os
import sys
import traceback

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    result = {"total_score": 0, "details": []}
    score_items = []

    # 1. 检查 onboarding_profile.json 是否存在
    profile_path = os.path.join(workspace, "onboarding_profile.json")
    exists = os.path.isfile(profile_path)
    score_items.append({
        "item": "onboarding_profile.json 文件存在",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "文件存在" if exists else "文件不存在"
    })

    if not exists:
        result["total_score"] = 0
        result["details"] = score_items
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 解析 JSON
    parsed = None
    json_valid = True
    json_error = ""
    try:
        with open(profile_path, "r") as f:
            parsed = json.load(f)
    except Exception as e:
        json_valid = False
        json_error = str(e)

    score_items.append({
        "item": "JSON 格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": "合法 JSON" if json_valid else f"解析失败: {json_error}"
    })

    if not json_valid:
        result["total_score"] = sum(s["score"] for s in score_items)
        result["details"] = score_items
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查必要字段
    expected_fields = ["employee_name", "email", "department", "permissions", "equipment", "status"]
    missing_fields = [f for f in expected_fields if f not in parsed]
    wrong_type_fields = []
    for f in expected_fields:
        if f in parsed:
            if f == "permissions" and not isinstance(parsed[f], list):
                wrong_type_fields.append(f)
            elif f in ("employee_name", "email", "department", "equipment", "status") and not isinstance(parsed[f], str):
                wrong_type_fields.append(f)

    fields_ok = len(missing_fields) == 0 and len(wrong_type_fields) == 0
    field_score = 30 if fields_ok else 0
    field_reason_parts = []
    if missing_fields:
        field_reason_parts.append(f"缺少字段: {', '.join(missing_fields)}")
    if wrong_type_fields:
        field_reason_parts.append(f"字段类型错误: {', '.join(wrong_type_fields)}")
    field_reason = "所有必需字段存在且类型正确" if fields_ok else "; ".join(field_reason_parts)

    score_items.append({
        "item": "必须字段（employee_name, email, department, permissions, equipment, status）存在且类型正确",
        "score": field_score,
        "max_score": 30,
        "passed": fields_ok,
        "reason": field_reason
    })

    # 4. 检查 permissions 内容（必须是 Engineering 部门的系统列表）
    expected_permissions = ["CRM", "ERP", "CodeRepo", "Jira"]
    permissions_ok = parsed.get("permissions") == expected_permissions
    score_items.append({
        "item": "permissions 内容正确（Engineering 部门权限包 systems）",
        "score": 20 if permissions_ok else 0,
        "max_score": 20,
        "passed": permissions_ok,
        "reason": f"正确: {parsed.get('permissions')}" if permissions_ok else f"期望 {expected_permissions}, 得到 {parsed.get('permissions')}"
    })

    # 5. 检查 equipment 内容（必须是 LAP-003）
    equipment_ok = parsed.get("equipment") == "LAP-003"
    score_items.append({
        "item": "equipment 值为 LAP-003（唯一可用的笔记本电脑）",
        "score": 20 if equipment_ok else 0,
        "max_score": 20,
        "passed": equipment_ok,
        "reason": f"正确: {parsed.get('equipment')}" if equipment_ok else f"期望 LAP-003, 得到 {parsed.get('equipment')}"
    })

    # 6. 检查 status 内容（必须是 onboarding_complete）
    status_ok = parsed.get("status") == "onboarding_complete"
    score_items.append({
        "item": "status 为 onboarding_complete",
        "score": 10 if status_ok else 0,
        "max_score": 10,
        "passed": status_ok,
        "reason": f"正确: {parsed.get('status')}" if status_ok else f"期望 onboarding_complete, 得到 {parsed.get('status')}"
    })

    result["total_score"] = sum(s["score"] for s in score_items)
    result["details"] = score_items

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
