import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查必备目录和文件是否存在（10分）
    required_paths = [
        "data/accounts.json",
        "data/onboarding/contracts.json",
        "data/onboarding/permission_packs.json",
        "data/onboarding/equipment_inventory.json"
    ]
    missing = []
    for p in required_paths:
        if not os.path.isfile(os.path.join(workspace, p)):
            missing.append(p)
    if missing:
        score_details.append({
            "item": "Required data files exist",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing files: {missing}"
        })
    else:
        score_details.append({
            "item": "Required data files exist",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required data files present"
        })

    # 2. 检查目标产物 onboarding_summary.json 是否存在且合法JSON（10分）
    result_path = os.path.join(workspace, "onboarding_summary.json")
    if not os.path.isfile(result_path):
        score_details.append({
            "item": "onboarding_summary.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 后续检查无法进行，直接写结果
        write_score(score_details, total_score)
        return

    try:
        with open(result_path) as f:
            summary = json.load(f)
        score_details.append({
            "item": "onboarding_summary.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully"
        })
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "onboarding_summary.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        write_score(score_details, total_score)
        return

    # 3. 检查必需字段是否存在（20分）—— 预期字段：employee_id, employee_name, email, permissions, equipment_asset_tag
    required_fields = ["employee_id", "employee_name", "email", "permissions", "equipment_asset_tag"]
    missing_fields = [f for f in required_fields if f not in summary]
    if missing_fields:
        score_details.append({
            "item": "Required fields in onboarding_summary.json",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing fields: {missing_fields}"
        })
    else:
        score_details.append({
            "item": "Required fields in onboarding_summary.json",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All required fields present"
        })

    # 4. 检查字段值的准确性（60分）—— 基于唯一正确答案
    # 正确答案：employee_id="EMP003", employee_name="Sarah Johnson", email="sarah.j@company.com",
    # permissions=["Marketo", "Google Analytics", "WordPress"], equipment_asset_tag="ASST-MKT-003"
    correct_values = {
        "employee_id": "EMP003",
        "employee_name": "Sarah Johnson",
        "email": "sarah.j@company.com",
        "permissions": ["Marketo", "Google Analytics", "WordPress"],
        "equipment_asset_tag": "ASST-MKT-003"
    }
    field_scores = {}
    for field, correct in correct_values.items():
        actual = summary.get(field)
        if actual == correct:
            field_scores[field] = 12  # 每个字段12分，5个字段共60分
        else:
            field_scores[field] = 0

    # 汇总字段得分
    field_total = sum(field_scores.values())
    if field_total == 60:
        passed = True
        reason = "All field values match expected"
    else:
        passed = False
        errors = [f"Field '{f}': expected {correct_values[f]}, got {summary.get(f)}" for f, s in field_scores.items() if s == 0]
        reason = "; ".join(errors)

    score_details.append({
        "item": "Field value correctness",
        "score": field_total,
        "max_score": 60,
        "passed": passed,
        "reason": reason
    })

    total_score = sum(d["score"] for d in score_details)
    write_score(score_details, total_score)


def write_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
