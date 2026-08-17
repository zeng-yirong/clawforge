import sys
import json
import os
from pathlib import Path

EXPECTED = {
    "version": "3.2.1",
    "release_date": "2025-06-15",
    "x_post": "🚀 OrbitalLaunch v3.2.1 is live! Full Linux support & new telemetry API. Update now!",
    "reddit_post": "We are thrilled to announce OrbitalLaunch v3.2.1! This release brings native Linux support and a powerful telemetry API. See changelog in comments.",
    "replies": [
        {"post_id": "post_002", "reply_content": "Yes, Linux support is confirmed in v3.2.1!"},
        {"post_id": "post_005", "reply_content": "The telemetry API documentation has been updated. Check the dev portal."}
    ]
}

def check_structure(data):
    """检查必要字段是否存在"""
    required = ["version", "release_date", "x_post", "reddit_post", "replies"]
    missing = [k for k in required if k not in data]
    if missing:
        return False, f"Missing fields: {missing}"
    return True, ""

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score_details = []
    total = 0
    max_total = 100

    # 1. 目录结构 (10分)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        score_details.append({"item": "ops/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        total += 10
    else:
        score_details.append({"item": "ops/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # 2. release_plan.json 存在 (10分)
    plan_file = ops_dir / "release_plan.json"
    if plan_file.is_file():
        score_details.append({"item": "ops/release_plan.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total += 10
    else:
        score_details.append({"item": "ops/release_plan.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 无法继续，给出总分并写入
        final_score = {"total_score": total, "details": score_details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final_score, f, indent=2)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(plan_file, "r") as f:
            data = json.load(f)
        score_details.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Parse successful"})
        total += 10
    except Exception as e:
        score_details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        # 仍要写入
        final_score = {"total_score": total, "details": score_details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final_score, f, indent=2)
        return

    # 4. 字段完整性 (20分)
    ok, msg = check_structure(data)
    if ok:
        score_details.append({"item": "Required fields present", "score": 20, "max_score": 20, "passed": True, "reason": "All required fields found"})
        total += 20
    else:
        score_details.append({"item": "Required fields present", "score": 0, "max_score": 20, "passed": False, "reason": msg})
        # 缺失字段，后面无法精确匹配，直接结束
        final_score = {"total_score": total, "details": score_details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final_score, f, indent=2)
        return

    # 5. 精确匹配各项 (50分，每项10分)
    match_score = 0
    # 5a. version
    if data.get("version") == EXPECTED["version"]:
        match_score += 10
        score_details.append({"item": "version match", "score": 10, "max_score": 10, "passed": True, "reason": "Correct version"})
    else:
        score_details.append({"item": "version match", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {EXPECTED['version']}, got {data.get('version')}"})

    # 5b. release_date
    if data.get("release_date") == EXPECTED["release_date"]:
        match_score += 10
        score_details.append({"item": "release_date match", "score": 10, "max_score": 10, "passed": True, "reason": "Correct date"})
    else:
        score_details.append({"item": "release_date match", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {EXPECTED['release_date']}, got {data.get('release_date')}"})

    # 5c. x_post
    if data.get("x_post") == EXPECTED["x_post"]:
        match_score += 10
        score_details.append({"item": "x_post match", "score": 10, "max_score": 10, "passed": True, "reason": "Correct X post"})
    else:
        score_details.append({"item": "x_post match", "score": 0, "max_score": 10, "passed": False, "reason": f"Mismatch"})

    # 5d. reddit_post
    if data.get("reddit_post") == EXPECTED["reddit_post"]:
        match_score += 10
        score_details.append({"item": "reddit_post match", "score": 10, "max_score": 10, "passed": True, "reason": "Correct Reddit post"})
    else:
        score_details.append({"item": "reddit_post match", "score": 0, "max_score": 10, "passed": False, "reason": f"Mismatch"})

    # 5e. replies
    actual_replies = data.get("replies", [])
    if actual_replies == EXPECTED["replies"]:
        match_score += 10
        score_details.append({"item": "replies match", "score": 10, "max_score": 10, "passed": True, "reason": "Correct replies list"})
    else:
        score_details.append({"item": "replies match", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {EXPECTED['replies']}, got {actual_replies}"})

    total += match_score

    final_score = {"total_score": total, "details": score_details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(final_score, f, indent=2)

if __name__ == "__main__":
    main()
