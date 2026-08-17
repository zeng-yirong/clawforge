import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    max_total = 100

    # 1. 目录结构检查：output 存在 (10 pts)
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        details.append({"item": "output directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "output/ found"})
        score += 10
    else:
        details.append({"item": "output directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "output/ missing"})

    # 2. 目标文件存在 (20 pts)
    target_file = os.path.join(output_dir, "launch_brief_summary.json")
    if os.path.isfile(target_file):
        details.append({"item": "launch_brief_summary.json exists", "score": 20, "max_score": 20, "passed": True, "reason": "file present"})
        score += 20
    else:
        details.append({"item": "launch_brief_summary.json exists", "score": 0, "max_score": 20, "passed": False, "reason": "file not found"})
        # 如果文件不存在，后续检查无法进行，直接返回
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}

    # 3. JSON 合法性 (10 pts)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
        score += 10
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}

    # 4. 字段精确匹配 (每字段15分，共60分)
    expected = {
        "mission": "Orbital Messenger",
        "launch_date": "2025-04-20",
        "tagline": "Your messages, beyond the clouds.",
        "approved_by": "Mira Chen"
    }
    # 可选检查 status 字段，但不是强制（防止过度约束），但可以加分？不，按设计必须包含 status 且为 "Approved"
    # 但 prompt 要求了五个字段：mission, launch_date, tagline, approved_by, status
    # 所以强制检查 status = "Approved"
    expected["status"] = "Approved"

    for field, val in expected.items():
        if field in data and data[field] == val:
            details.append({"item": f"field '{field}' matches", "score": 15, "max_score": 15, "passed": True, "reason": f"value is '{val}'"})
            score += 15
        elif field in data:
            details.append({"item": f"field '{field}' mismatch", "score": 0, "max_score": 15, "passed": False, "reason": f"got '{data.get(field)}', expected '{val}'"})
        else:
            details.append({"item": f"field '{field}' missing", "score": 0, "max_score": 15, "passed": False, "reason": "field not present"})

    # 额外扣分：如果包含多余字段，扣一点分以示严谨（可选）但为简化不扣，只提示
    # 总分上限100，如果满了就100
    total = min(score, max_total)
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    result = verify()
    with open(sys.argv[1] + "/workplace_score.json", "w") if len(sys.argv) > 1 else open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
