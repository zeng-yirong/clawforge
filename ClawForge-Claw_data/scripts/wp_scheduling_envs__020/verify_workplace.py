import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops", "humidifier_fix.json")
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查文件是否存在 (10分)
    if os.path.isfile(result_path):
        details.append({
            "item": "Result file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/humidifier_fix.json found"
        })
        total_score += 10
    else:
        details.append({
            "item": "Result file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/humidifier_fix.json not found"
        })
        # 如果文件不存在，后续检查跳过（分数设为0）
        # 但我们仍需要写出详细信息
        details.append({
            "item": "JSON validity and content",
            "score": 0,
            "max_score": 90,
            "passed": False,
            "reason": "Skipped because file missing"
        })
        write_score(total_score, details, max_total)
        sys.exit(0)

    # 2. 解析 JSON (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        # 后续无法继续，剩余80分置0
        for remaining in ["Field 'bad_schedule_ids' exists", "Correct schedule ID", "No extra IDs", "Output structure clean"]:
            details.append({
                "item": remaining,
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Skipped due to invalid JSON"
            })
        write_score(total_score, details, max_total)
        sys.exit(0)

    # 3. 检查字段存在 (20分)
    if "bad_schedule_ids" in data:
        details.append({
            "item": "Field 'bad_schedule_ids' exists",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "bad_schedule_ids key present"
        })
        total_score += 20
    else:
        details.append({
            "item": "Field 'bad_schedule_ids' exists",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Missing 'bad_schedule_ids' key"
        })
        # 后续检查跳过
        for remaining in ["Correct schedule ID", "No extra IDs", "Output structure clean"]:
            details.append({
                "item": remaining,
                "score": 0,
                "max_score": 20 if remaining != "No extra IDs" else 10,
                "passed": False,
                "reason": "Skipped due to missing field"
            })
        write_score(total_score, details, max_total)
        sys.exit(0)

    ids = data["bad_schedule_ids"]
    if not isinstance(ids, list):
        details.append({
            "item": "bad_schedule_ids is a list",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Value is not a list"
        })
        # 后续跳过
        for remaining in ["Correct schedule ID", "No extra IDs", "Output structure clean"]:
            details.append({
                "item": remaining,
                "score": 0,
                "max_score": 20 if remaining != "No extra IDs" else 10,
                "passed": False,
                "reason": "Skipped due to wrong type"
            })
        write_score(total_score, details, max_total)
        sys.exit(0)

    # 4. 检查正确的调度ID (50分)
    correct_id = "sch-002"
    if correct_id in ids:
        # 视作主要正确
        details.append({
            "item": "Correct schedule ID found",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": f"Contains expected ID '{correct_id}'"
        })
        total_score += 50
    else:
        details.append({
            "item": "Correct schedule ID found",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"Expected ID '{correct_id}' not in list; got {ids}"
        })

    # 5. 检查没有多余的ID (10分)
    allowed = {correct_id}
    extra = [i for i in ids if i not in allowed]
    if not extra:
        details.append({
            "item": "No extra schedule IDs",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only expected IDs present"
        })
        total_score += 10
    else:
        details.append({
            "item": "No extra schedule IDs",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra IDs found: {extra}"
        })

    write_score(total_score, details, max_total)

def write_score(total, details, max_total):
    # 确保总分不大于100
    total = min(total, max_total)
    result = {
        "total_score": total,
        "details": details
    }
    # 写入 workplace_score.json 到当前工作目录
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
