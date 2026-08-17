import sys
import os
import json
import re

def verify(workspace):
    details = []
    total_score = 0

    # 1. 目录 ops 是否存在（10分）
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops/ directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/ directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2. 目标文件是否存在（10分）
    target_path = os.path.join(workspace, "ops", "launch_posts.json")
    if os.path.isfile(target_path):
        details.append({
            "item": "ops/launch_posts.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "file found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/launch_posts.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file not found"
        })
        # 后续检查无法进行，直接返回
        score_entry = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_entry, f, indent=2)
        return

    # 3. JSON 合法性（10分）
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "valid JSON"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"invalid JSON: {str(e)}"
        })
        # 无法继续
        score_entry = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_entry, f, indent=2)
        return

    # 4. 含有 x 和 reddit 字段（10分）
    has_x = "x" in data
    has_reddit = "reddit" in data
    if has_x and has_reddit:
        details.append({
            "item": "JSON contains 'x' and 'reddit' keys",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "both keys present"
        })
        total_score += 10
    else:
        missing = []
        if not has_x:
            missing.append("x")
        if not has_reddit:
            missing.append("reddit")
        details.append({
            "item": "JSON contains 'x' and 'reddit' keys",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"missing keys: {', '.join(missing)}"
        })

    # 5. x.text 正确性（25分）
    expected_x = "Reach Beyond the Stars – SkyLink Pro launches August 15. Pre-order at skylinkpro.io"
    actual_x = data.get("x", {}).get("text", "")
    if actual_x == expected_x:
        details.append({
            "item": "x.text content matches expected",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": "exact match"
        })
        total_score += 25
    else:
        details.append({
            "item": "x.text content matches expected",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"expected '{expected_x}', got '{actual_x}'"
        })

    # 6. reddit.title 正确性（15分）
    expected_reddit_title = "SkyLink Pro Official Launch"
    actual_title = data.get("reddit", {}).get("title", "")
    if actual_title == expected_reddit_title:
        details.append({
            "item": "reddit.title matches expected",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "exact match"
        })
        total_score += 15
    else:
        details.append({
            "item": "reddit.title matches expected",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"expected '{expected_reddit_title}', got '{actual_title}'"
        })

    # 7. reddit.text 正确性（20分）
    expected_reddit_text = "SkyLink Pro connects remote teams with zero latency. Available now. Pre-order at skylinkpro.io"
    actual_text = data.get("reddit", {}).get("text", "")
    if actual_text == expected_reddit_text:
        details.append({
            "item": "reddit.text matches expected",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "exact match"
        })
        total_score += 20
    else:
        details.append({
            "item": "reddit.text matches expected",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"expected '{expected_reddit_text}', got '{actual_text}'"
        })

    # 额外扣分：如果存在多余字段（如 platform），扣 5 分（不重复扣）
    allowed_keys = {"x", "reddit"}
    extra_keys = set(data.keys()) - allowed_keys
    if extra_keys:
        details.append({
            "item": "No extra keys in output",
            "score": 0,
            "max_score": 0,  # 不占满分，只是扣分项
            "passed": False,
            "reason": f"extra keys found: {extra_keys}"
        })
        total_score = max(0, total_score - 5)

    # 输出结果
    score_entry = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_entry, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
