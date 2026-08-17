import json
import os
import sys
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_possible = 100

    workspace_path = Path(workspace)

    # 1. 检查 ops 目录存在 (10分)
    ops_dir = workspace_path / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops directory found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops directory not found"
        })

    # 2. 检查 finance_mails.json (5分存在)
    finance_path = ops_dir / "finance_mails.json"
    if finance_path.is_file():
        details.append({
            "item": "finance_mails.json exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "file found"
        })
        total_score += 5
    else:
        details.append({
            "item": "finance_mails.json exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "file not found"
        })
        # 如果文件不存在，后续无法检查，直接返回
        return {"total_score": total_score, "details": details}

    # 3. 检查 scam_ids.json (5分存在)
    scam_path = ops_dir / "scam_ids.json"
    if scam_path.is_file():
        details.append({
            "item": "scam_ids.json exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "file found"
        })
        total_score += 5
    else:
        details.append({
            "item": "scam_ids.json exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "file not found"
        })
        # 继续检查但 scam 部分不得分

    # 4. 解析 finance_mails.json (10分合法)
    try:
        with open(finance_path) as f:
            finance_data = json.load(f)
        finance_valid = True
        reason = "valid JSON"
    except (json.JSONDecodeError, Exception) as e:
        finance_valid = False
        reason = f"invalid JSON: {e}"
    if finance_valid:
        details.append({
            "item": "finance_mails.json valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": reason
        })
        total_score += 10
    else:
        details.append({
            "item": "finance_mails.json valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": reason
        })
        finance_data = {}  # 避免后续报错

    # 5. 解析 scam_ids.json (10分合法)
    scam_valid = False
    if scam_path.is_file():
        try:
            with open(scam_path) as f:
                scam_data = json.load(f)
            scam_valid = True
            reason = "valid JSON"
        except (json.JSONDecodeError, Exception) as e:
            reason = f"invalid JSON: {e}"
    else:
        reason = "file missing"
    if scam_valid:
        details.append({
            "item": "scam_ids.json valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": reason
        })
        total_score += 10
    else:
        details.append({
            "item": "scam_ids.json valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": reason
        })
        scam_data = {}

    # 6. 检查 finance_mails.json 内容 (30分 ids + 20分 earliest_due_date)
    expected_finance_ids = {"f001", "f002", "f003"}
    actual_ids = set(finance_data.get("ids", [])) if isinstance(finance_data.get("ids"), list) else set()
    # id 完全匹配 (每个10分, 共30)
    if actual_ids == expected_finance_ids:
        details.append({
            "item": "finance ids correct (exact set)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"ids correctly include f001, f002, f003"
        })
        total_score += 30
    else:
        # 部分得分: 每个正确 id 10分
        correct_count = len(actual_ids & expected_finance_ids)
        score_ids = correct_count * 10
        missing = expected_finance_ids - actual_ids
        extra = actual_ids - expected_finance_ids
        reason = f"correct: {correct_count}, missing: {missing if missing else 'none'}, extra: {extra if extra else 'none'}"
        details.append({
            "item": "finance ids correct",
            "score": score_ids,
            "max_score": 30,
            "passed": correct_count == 3,
            "reason": reason
        })
        total_score += score_ids

    # earliest_due_date (20分)
    expected_date = "2024-12-15"
    actual_date = finance_data.get("earliest_due_date")
    if actual_date == expected_date:
        details.append({
            "item": "earliest due date correct",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"found '{expected_date}'"
        })
        total_score += 20
    else:
        details.append({
            "item": "earliest due date correct",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"expected '{expected_date}', got '{actual_date}'"
        })

    # 7. 检查 scam_ids.json 内容 (20分)
    expected_scam_ids = {"s001"}
    actual_scam_ids = set(scam_data.get("ids", [])) if isinstance(scam_data.get("ids"), list) else set()
    if actual_scam_ids == expected_scam_ids:
        details.append({
            "item": "scam ids correct",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "contains only s001"
        })
        total_score += 20
    else:
        correct_scam = len(actual_scam_ids & expected_scam_ids)
        score_scam = correct_scam * 20
        details.append({
            "item": "scam ids correct",
            "score": score_scam,
            "max_score": 20,
            "passed": correct_scam == 1,
            "reason": f"correct: {correct_scam}, extra: {actual_scam_ids - expected_scam_ids}"
        })
        total_score += score_scam

    # 确保总分不超过100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
