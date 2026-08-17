import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    checklist_path = os.path.join(workspace, "ops", "handover_checklist.json")
    details = []
    total_score = 0
    max_total = 100

    # 1. File existence (10 points)
    if os.path.isfile(checklist_path):
        details.append({
            "item": "handover_checklist.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "handover_checklist.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # Cannot proceed further – write result and exit
        _write_score(total_score, details)
        return

    # 2. Valid JSON (10 points)
    try:
        with open(checklist_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 解析合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "合法 JSON"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 解析合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        _write_score(total_score, details)
        return

    # 3. Key fields present (20 points)
    required_fields = ["employee_id", "employee_name", "revoked_systems", "reclaimed_equipment", "manual_actions"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        details.append({
            "item": "关键字段齐全",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"缺失字段: {missing}"
        })
    else:
        details.append({
            "item": "关键字段齐全",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有必需字段存在"
        })
        total_score += 20

    # 4. employee_id correctness (10 points)
    if data.get("employee_id") == "EMP-042":
        details.append({
            "item": "employee_id 正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "值为 EMP-042"
        })
        total_score += 10
    else:
        details.append({
            "item": "employee_id 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 EMP-042，实际 {data.get('employee_id')}"
        })

    # 5. employee_name correctness (10 points)
    if data.get("employee_name") == "Li Xue":
        details.append({
            "item": "employee_name 正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "值为 Li Xue"
        })
        total_score += 10
    else:
        details.append({
            "item": "employee_name 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 Li Xue，实际 {data.get('employee_name')}"
        })

    # 6. revoked_systems correctness (15 points)
    revoked = data.get("revoked_systems", [])
    expected_systems = {"Admin Portal", "CRM"}
    actual_systems = {r.get("system_name") for r in revoked if r.get("status") == "revoked"}
    if actual_systems == expected_systems and len(revoked) == 2:
        details.append({
            "item": "revoked_systems 内容正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"包含 {sorted(expected_systems)}，状态均为 revoked"
        })
        total_score += 15
    else:
        details.append({
            "item": "revoked_systems 内容正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"期望系统 {sorted(expected_systems)} 且全部 revoked，实际 systems={actual_systems}，数量={len(revoked)}"
        })

    # 7. reclaimed_equipment correctness (15 points)
    reclaimed = data.get("reclaimed_equipment", [])
    expected_tags = {"BG-8821", "LT-2041"}
    actual_tags = {r.get("asset_tag") for r in reclaimed if r.get("status") == "reclaimed"}
    if actual_tags == expected_tags and len(reclaimed) == 2:
        details.append({
            "item": "reclaimed_equipment 内容正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"包含 {sorted(expected_tags)}，状态均为 reclaimed"
        })
        total_score += 15
    else:
        details.append({
            "item": "reclaimed_equipment 内容正确",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"期望资产 {sorted(expected_tags)} 且全部 reclaimed，实际 tags={actual_tags}，数量={len(reclaimed)}"
        })

    # 8. manual_actions correctness (10 points)
    manual = data.get("manual_actions", [])
    # We expect at least "delete_email_account" (or a similar token)
    found = any("delete" in str(action).lower() and "email" in str(action).lower() for action in manual)
    if found and len(manual) >= 1:
        details.append({
            "item": "manual_actions 包含邮箱删除操作",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"找到类似 'delete_email_account' 的条目"
        })
        total_score += 10
    else:
        details.append({
            "item": "manual_actions 包含邮箱删除操作",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"未找到包含 'delete' 和 'email' 的条目，实际 manual_actions={manual}"
        })

    _write_score(total_score, details)


def _write_score(total_score, details):
    # Ensure total is an integer between 0 and 100
    result = {
        "total_score": min(max(total_score, 0), 100),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
