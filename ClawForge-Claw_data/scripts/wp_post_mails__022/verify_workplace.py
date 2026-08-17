import sys
import os
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # ------------------------------------------------------------------
    # 1. 目录结构检查 (10)
    # ------------------------------------------------------------------
    item = {"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops/ directory present"
    else:
        item["reason"] = "ops/ directory not found"
    results.append(item)
    total_score += item["score"]

    item = {"item": "ops directory contains exactly x_post.json and reddit_post.json", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    expected_files = {"x_post.json", "reddit_post.json"}
    if os.path.isdir(ops_path):
        files_in_ops = set(os.listdir(ops_path))
        if expected_files.issubset(files_in_ops):
            # 不允许多余文件（除了可能隐藏文件）
            extra = files_in_ops - expected_files
            if not extra:
                item["score"] = 5
                item["passed"] = True
                item["reason"] = "exactly the two required files"
            else:
                item["reason"] = f"extra files found: {extra}"
        else:
            missing = expected_files - files_in_ops
            item["reason"] = f"missing files: {missing}"
    else:
        item["reason"] = "ops/ not found"
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 2. JSON 合法性 (10)
    # ------------------------------------------------------------------
    def load_json(filepath, label):
        if not os.path.isfile(filepath):
            return None, f"{label} not found"
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data, None
        except json.JSONDecodeError as e:
            return None, f"{label} invalid JSON: {e}"

    x_data, err = load_json(os.path.join(ops_path, "x_post.json"), "x_post.json")
    reddit_data, err2 = load_json(os.path.join(ops_path, "reddit_post.json"), "reddit_post.json")

    item = {"item": "x_post.json is valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if x_data is not None:
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "valid JSON"
    else:
        item["reason"] = err
    results.append(item)
    total_score += item["score"]

    item = {"item": "reddit_post.json is valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if reddit_data is not None:
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "valid JSON"
    else:
        item["reason"] = err2
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 3. 字段存在性 (10)  -- 每个文件必须包含必要字段
    # ------------------------------------------------------------------
    required_fields_x = ["platform", "title", "content", "author_id", "tags"]
    required_fields_reddit = ["platform", "title", "content", "author_id", "community", "tags"]

    def check_fields(data, fields, label):
        if data is None:
            return False, f"{label} not loaded"
        missing = [f for f in fields if f not in data]
        if missing:
            return False, f"missing fields: {missing}"
        return True, "all required fields present"

    item = {"item": "x_post.json has required fields", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    ok, reason = check_fields(x_data, required_fields_x, "x_post.json")
    if ok:
        item["score"] = 5
        item["passed"] = True
        item["reason"] = reason
    else:
        item["reason"] = reason
    results.append(item)
    total_score += item["score"]

    item = {"item": "reddit_post.json has required fields", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    ok, reason = check_fields(reddit_data, required_fields_reddit, "reddit_post.json")
    if ok:
        item["score"] = 5
        item["passed"] = True
        item["reason"] = reason
    else:
        item["reason"] = reason
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 4. author_id 正确性 (20)  -- 必须为 ax_2024
    # ------------------------------------------------------------------
    item = {"item": "x_post.json author_id is ax_2024", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if x_data and x_data.get("author_id") == "ax_2024":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "author_id matches AuroraX account"
    else:
        item["reason"] = f"expected ax_2024, got {x_data.get('author_id') if x_data else 'N/A'}"
    results.append(item)
    total_score += item["score"]

    item = {"item": "reddit_post.json author_id is ax_2024", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if reddit_data and reddit_data.get("author_id") == "ax_2024":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "author_id matches AuroraX account"
    else:
        item["reason"] = f"expected ax_2024, got {reddit_data.get('author_id') if reddit_data else 'N/A'}"
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 5. 核心内容精确性 (30)  -- 必须包含简报中的 "AuroraX Launch: 2025-04-01" 和 "Mission: Beyond the Horizon"
    #      对于 X 帖，content 应包含第一个；对于 Reddit 帖，content 应包含第二个。
    #      注意：简报原文是 "AuroraX Launch: 2025-04-01" 和 "Mission: Beyond the Horizon"
    #      但简报.md中写的是 "Launch Date: 2025-04-01" 和 "Mission Statement: Beyond the Horizon"
    #      我们以实际写的内容为准：brief_v3.md 中有 "Launch Date: 2025-04-01" 和 "Mission Statement: Beyond the Horizon"
    #      为简化验证，我们要求 content 包含日期字符串 "2025-04-01" 和 "Beyond the Horizon"。
    #      更严格：必须同时包含两个关键短语，但考虑到X帖可能只包含一个，我们分开检查。
    #      这里我们要求每个帖子的content必须包含对应的至少一个关键短语。
    # 实际设计：让两个帖子都包含 "2025-04-01" 和 "Beyond the Horizon" 也不矛盾，因为brief中都有。
    # 但为了有区分度，我们让X帖必须包含日期，Reddit帖必须包含“Beyond the Horizon”。
    # 符合业务：X帖强调 launch date，Reddit帖强调 mission.
    # 所以检查：
    # - x_post.json content 必须包含 "2025-04-01"
    # - reddit_post.json content 必须包含 "Beyond the Horizon"
    # 每个15分，共30分。
    item = {"item": "x_post.json content includes launch date '2025-04-01'", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    if x_data and "2025-04-01" in x_data.get("content", ""):
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "launch date present"
    else:
        item["reason"] = f"content does not contain '2025-04-01'. Content: {x_data.get('content', '')[:50] if x_data else 'N/A'}"
    results.append(item)
    total_score += item["score"]

    item = {"item": "reddit_post.json content includes mission 'Beyond the Horizon'", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    if reddit_data and "Beyond the Horizon" in reddit_data.get("content", ""):
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "mission statement present"
    else:
        item["reason"] = f"content does not contain 'Beyond the Horizon'. Content: {reddit_data.get('content', '')[:50] if reddit_data else 'N/A'}"
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 6. 平台字段正确性 (10)
    # ------------------------------------------------------------------
    item = {"item": "x_post.json platform is 'x'", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if x_data and x_data.get("platform") == "x":
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "platform is x"
    else:
        item["reason"] = f"expected 'x', got {x_data.get('platform') if x_data else 'N/A'}"
    results.append(item)
    total_score += item["score"]

    item = {"item": "reddit_post.json platform is 'reddit'", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if reddit_data and reddit_data.get("platform") == "reddit":
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "platform is reddit"
    else:
        item["reason"] = f"expected 'reddit', got {reddit_data.get('platform') if reddit_data else 'N/A'}"
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 7. community 字段 (reddit) (5)  -- 必须为 "r/aurora"
    # ------------------------------------------------------------------
    item = {"item": "reddit_post.json community is 'r/aurora'", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    if reddit_data and reddit_data.get("community") == "r/aurora":
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "community matches default_reddit_community"
    else:
        item["reason"] = f"expected 'r/aurora', got {reddit_data.get('community') if reddit_data else 'N/A'}"
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 8. tags 存在且非空 (5)
    # ------------------------------------------------------------------
    item = {"item": "x_post.json tags is a non-empty list", "score": 0, "max_score": 2, "passed": False, "reason": ""}
    if x_data and isinstance(x_data.get("tags"), list) and len(x_data["tags"]) > 0:
        item["score"] = 2
        item["passed"] = True
        item["reason"] = "tags present and non-empty"
    else:
        item["reason"] = "tags missing or empty"
    results.append(item)
    total_score += item["score"]

    item = {"item": "reddit_post.json tags is a non-empty list", "score": 0, "max_score": 3, "passed": False, "reason": ""}
    if reddit_data and isinstance(reddit_data.get("tags"), list) and len(reddit_data["tags"]) > 0:
        item["score"] = 3
        item["passed"] = True
        item["reason"] = "tags present and non-empty"
    else:
        item["reason"] = "tags missing or empty"
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 最终总分
    # ------------------------------------------------------------------
    total_score = min(total_score, max_total)  # 防止溢出

    report = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(report, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/{max_total}")

if __name__ == "__main__":
    main()
