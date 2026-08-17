import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops", "launch_brief.json")
    details = []

    # 1. 文件存在性检查 (10分)
    if not os.path.exists(result_path):
        details.append({
            "item": "ops/launch_brief.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        write_score(0, details)
        return
    else:
        details.append({
            "item": "ops/launch_brief.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists"
        })

    # 2. JSON 合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully"
        })
    except Exception as e:
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        write_score(sum(d["score"] for d in details), details)
        return

    # 3. 字段存在且类型正确 (20分)
    required_fields = {
        "product_name": str,
        "launch_date": str,
        "key_message": str,
        "platforms": list
    }
    field_score = 0
    for field, field_type in required_fields.items():
        if field not in data:
            details.append({
                "item": f"Field '{field}' present",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Missing field '{field}'"
            })
        elif not isinstance(data[field], field_type):
            details.append({
                "item": f"Field '{field}' type correct",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Expected {field_type.__name__}, got {type(data[field]).__name__}"
            })
        else:
            details.append({
                "item": f"Field '{field}' present and correct type",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "OK"
            })
            field_score += 5
    # 如果字段有缺失或类型错误，累积扣分已体现

    # 4. 精确值验证 (共60分，每项15分)
    expected_values = {
        "product_name": "Aurora X1",
        "launch_date": "2025-04-12",
        "key_message": "The Future is Now"
    }
    value_score = 0
    for field, expected in expected_values.items():
        if field in data and data[field] == expected:
            details.append({
                "item": f"Value of '{field}' correct",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": f"Expected '{expected}', got '{data[field]}'"
            })
            value_score += 15
        else:
            actual = data.get(field, "N/A")
            details.append({
                "item": f"Value of '{field}' correct",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Expected '{expected}', got '{actual}'"
            })

    # 5. platforms 验证 (15分)
    expected_platforms = {"x", "reddit", "linkedin"}
    actual_platforms = set(data.get("platforms", []))
    if actual_platforms == expected_platforms:
        details.append({
            "item": "Platforms set correct",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"Platforms match: {expected_platforms}"
        })
        value_score += 15
    else:
        details.append({
            "item": "Platforms set correct",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Expected platforms {expected_platforms}, got {actual_platforms}"
        })

    total_score = 10 + 10 + field_score + value_score
    write_score(total_score, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
