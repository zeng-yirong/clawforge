import json
import os
import sys
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    score_details = []
    total = 0

    # 1. ops 目录是否存在 (10分)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        total += 10
        score_details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
    else:
        score_details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # 2. onboarding_result.json 是否存在 (10分)
    result_file = ops_dir / "onboarding_result.json"
    if result_file.is_file():
        total += 10
        score_details.append({"item": "onboarding_result.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file exists"})
    else:
        # 文件缺失，直接输出结果
        score_details.append({"item": "onboarding_result.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        final_score = {"total_score": total, "details": score_details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final_score, f, indent=2)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        total += 10
        score_details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
    except Exception as e:
        total += 0
        score_details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        final_score = {"total_score": total, "details": score_details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final_score, f, indent=2)
        return

    # 4. 必要字段完整性 (15分) – 检查八个字段是否存在
    required_fields = ["employee_id", "name", "email", "department", "contract_valid", "assigned_systems", "equipment_tag", "welcome_message"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        total += 0
        score_details.append({"item": "All required fields present", "score": 0, "max_score": 15, "passed": False, "reason": f"Missing fields: {missing}"})
    else:
        total += 15
        score_details.append({"item": "All required fields present", "score": 15, "max_score": 15, "passed": True, "reason": "all 8 fields found"})

    # 5-9. 基本值精确匹配 (每个5分)
    checks = [
        ("employee_id", "EMP014"),
        ("name", "Alice Wang"),
        ("email", "alice.wang@company.com"),
        ("department", "Engineering"),
        ("contract_valid", True),
    ]
    for field, expected in checks:
        actual = data.get(field)
        if actual == expected:
            total += 5
            score_details.append({"item": f"{field} == {expected!r}", "score": 5, "max_score": 5, "passed": True, "reason": f"matched"})
        else:
            score_details.append({"item": f"{field} == {expected!r}", "score": 0, "max_score": 5, "passed": False, "reason": f"got {actual!r}"})

    # 10. assigned_systems 集合相等 (10分)
    actual_systems = data.get("assigned_systems", [])
    expected_systems = {"github", "jira", "confluence"}
    if set(actual_systems) == expected_systems:
        total += 10
        score_details.append({"item": "assigned_systems set matches", "score": 10, "max_score": 10, "passed": True, "reason": "correct systems"})
    else:
        score_details.append({"item": "assigned_systems set matches", "score": 0, "max_score": 10, "passed": False, "reason": f"got {actual_systems}"})

    # 11. equipment_tag 精确匹配 (10分)
    actual_tag = data.get("equipment_tag")
    if actual_tag == "LT-2024-042":
        total += 10
        score_details.append({"item": "equipment_tag == LT-2024-042", "score": 10, "max_score": 10, "passed": True, "reason": "correct tag"})
    else:
        score_details.append({"item": "equipment_tag == LT-2024-042", "score": 0, "max_score": 10, "passed": False, "reason": f"got {actual_tag!r}"})

    # 12. welcome_message 精确匹配 (10分)
    expected_msg = "Welcome to the company, Alice! Your accounts are ready."
    actual_msg = data.get("welcome_message")
    if actual_msg == expected_msg:
        total += 10
        score_details.append({"item": "welcome_message matches", "score": 10, "max_score": 10, "passed": True, "reason": "correct message"})
    else:
        score_details.append({"item": "welcome_message matches", "score": 0, "max_score": 10, "passed": False, "reason": f"got {actual_msg!r}"})

    # 构造最终分数 (max 100)
    final_score = {"total_score": total, "details": score_details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(final_score, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
