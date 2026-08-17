import os
import sys
import json
import math

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 profiles/ 目录是否存在 (5分)
    profiles_dir = os.path.join(workspace, "profiles")
    if os.path.isdir(profiles_dir):
        details.append({"item": "profiles 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "profiles 目录已创建"})
        total_score += 5
    else:
        details.append({"item": "profiles 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "profiles 目录不存在"})

    # 2. 检查 E001_profile.json 文件是否存在 (10分)
    profile_path = os.path.join(profiles_dir, "E001_profile.json") if os.path.isdir(profiles_dir) else os.path.join(workspace, "profiles", "E001_profile.json")
    if os.path.isfile(profile_path):
        details.append({"item": "E001_profile.json 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "目标文件已生成"})
        total_score += 10
    else:
        details.append({"item": "E001_profile.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未找到"})
        # 后续检查无法进行，直接写结果返回
        write_score(total_score, details)
        return

    # 3. 文件格式合法 (JSON) (5分)
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 5, "max_score": 5, "passed": True, "reason": "文件可解析为 JSON"})
        total_score += 5
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 5, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(total_score, details)
        return

    # 4. 包含必要字段 (20分) - employee_id, employee_name, department, role_code, score
    required_fields = ["employee_id", "employee_name", "department", "role_code", "score"]
    missing = [f for f in required_fields if f not in profile]
    if not missing:
        details.append({"item": "包含所有必要字段", "score": 20, "max_score": 20, "passed": True, "reason": "employee_id, employee_name, department, role_code, score 均存在"})
        total_score += 20
    else:
        details.append({"item": "包含所有必要字段", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {missing}"})
        # 不中断，继续检查可检查的

    # 5. 字段值正确性 (50分) - 重点
    field_correct = True
    reason_parts = []

    # 5.1 employee_id = "E001"
    if profile.get("employee_id") == "E001":
        field_correct = True
        reason_parts.append("employee_id 正确")
    else:
        field_correct = False
        reason_parts.append(f"employee_id 应为 E001，实际为 {profile.get('employee_id')}")

    # 5.2 employee_name = "Alice"
    if profile.get("employee_name") == "Alice":
        reason_parts.append("employee_name 正确")
    else:
        field_correct = False
        reason_parts.append(f"employee_name 应为 Alice，实际为 {profile.get('employee_name')}")

    # 5.3 department = "Engineering"
    if profile.get("department") == "Engineering":
        reason_parts.append("department 正确")
    else:
        field_correct = False
        reason_parts.append(f"department 应为 Engineering，实际为 {profile.get('department')}")

    # 5.4 role_code = "engineer"
    if profile.get("role_code") == "engineer":
        reason_parts.append("role_code 正确")
    else:
        field_correct = False
        reason_parts.append(f"role_code 应为 engineer，实际为 {profile.get('role_code')}")

    # 5.5 score 计算精确：总分 = 80*0.5 + 90*0.3 + 70*0.2 = 40+27+14 = 81
    expected_score = 81
    actual_score = profile.get("score")
    if isinstance(actual_score, (int, float)) and abs(actual_score - expected_score) < 0.01:
        reason_parts.append(f"score 计算正确: {expected_score}")
    else:
        field_correct = False
        reason_parts.append(f"score 应为 {expected_score}，实际为 {actual_score}")

    # 5.6 可选：检查是否包含明细字段，但不强制；如果有则加分鼓励（已包含在满分中）
    detail_fields = ["feature_delivery", "quality_score", "collaboration_score", "feature_delivery_weight", "quality_weight", "collaboration_weight"]
    has_detail = all(k in profile for k in detail_fields)
    if has_detail:
        reason_parts.append("包含计算明细字段")
    else:
        # 不扣分，但也不加分，但为了体现区分度，如果缺失明细则扣5分（从50分里扣）
        field_correct = False  # 标记为不完美，但具体扣分单独处理
        if not has_detail:
            reason_parts.append(f"缺少明细字段 (期望 {detail_fields})")
            # 扣5分
            # 我们稍后处理

    # 得分计算
    if field_correct and has_detail:
        score_field = 50
        reason = "; ".join(reason_parts)
    elif field_correct and not has_detail:
        score_field = 45  # 缺少明细扣5分
        reason = "; ".join(reason_parts) + " (缺少明细字段扣5分)"
    else:
        # 关键字段错误，最多给部分分
        # 统计正确项数
        correct_count = 0
        if profile.get("employee_id") == "E001": correct_count += 1
        if profile.get("employee_name") == "Alice": correct_count += 1
        if profile.get("department") == "Engineering": correct_count += 1
        if profile.get("role_code") == "engineer": correct_count += 1
        if isinstance(actual_score, (int, float)) and abs(actual_score - expected_score) < 0.01: correct_count += 1
        score_field = correct_count * 10  # 每个正确给10分，最多50
        reason = "; ".join(reason_parts) + f" (部分正确: {correct_count}/5 个关键字段正确)"

    details.append({"item": "字段值和分数计算正确性", "score": score_field, "max_score": 50, "passed": field_correct and has_detail, "reason": reason})
    total_score += score_field

    # 汇总
    write_score(min(total_score, 100), details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
