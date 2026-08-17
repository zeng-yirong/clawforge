#!/usr/bin/env python3
import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace).resolve()

    details = []
    total_score = 0
    max_total = 100

    # 1. ops/ 目录存在 (5分)
    ops_dir = ws / "ops"
    passed = ops_dir.is_dir()
    details.append({
        "item": "ops/ directory exists",
        "score": 5 if passed else 0,
        "max_score": 5,
        "passed": passed,
        "reason": "" if passed else "Directory ops/ not found"
    })
    total_score += 5 if passed else 0

    # 2. interview_invite.json 文件存在 (10分)
    invite_file = ops_dir / "interview_invite.json"
    passed = invite_file.is_file()
    details.append({
        "item": "interview_invite.json exists",
        "score": 10 if passed else 0,
        "max_score": 10,
        "passed": passed,
        "reason": "" if passed else "File not found"
    })
    total_score += 10 if passed else 0

    # 如果文件不存在，后续检查无法进行，直接输出结果
    if not passed:
        output = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        print(json.dumps(output, indent=2))
        return

    # 3. JSON 格式合法 (10分)
    try:
        with open(invite_file, "r") as f:
            data = json.load(f)
        passed = True
        details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": str(e)
        })
        output = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(output, f, indent=2)
        return

    # 4. 必需字段完整性 (每个5分，共25分)
    expected_fields = ["job_id", "candidate_id", "candidate_name", "interview_time", "reminder_time"]
    for field in expected_fields:
        present = field in data
        details.append({
            "item": f"Field '{field}' present",
            "score": 5 if present else 0,
            "max_score": 5,
            "passed": present,
            "reason": "" if present else f"Missing field '{field}'"
        })
        total_score += 5 if present else 0

    # 5. 字段值正确性 (每个10分，共50分)
    expected_values = {
        "job_id": "J001",
        "candidate_id": "C003",
        "candidate_name": "Alice",
        "interview_time": "2025-04-10T10:00",
        "reminder_time": "2025-04-10T09:00"
    }
    for field, expected in expected_values.items():
        actual = data.get(field)
        passed = actual == expected
        details.append({
            "item": f"Field '{field}' value correct",
            "score": 10 if passed else 0,
            "max_score": 10,
            "passed": passed,
            "reason": "" if passed else f"Expected '{expected}', got '{actual}'"
        })
        total_score += 10 if passed else 0

    # 6. 禁止多余字段 (扣分项，最多扣5分)
    extra = set(data.keys()) - set(expected_fields)
    if extra:
        penalty = min(5, len(extra) * 2)
        details.append({
            "item": "No extra fields",
            "score": -penalty,
            "max_score": 0,
            "passed": False,
            "reason": f"Extra fields: {extra}"
        })
        total_score -= penalty
        total_score = max(0, total_score)

    final_score = min(max_total, total_score)
    output = {"total_score": final_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
