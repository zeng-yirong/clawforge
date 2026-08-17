"""Verify the workplace output for wp_post_mails__049.

Checks that the agent correctly:
- Found the approved brief (orbital_brief_v5.json) via email em_003.
- Extracted launch_date (2025-07-16) and product_name (Aurora LV-9).
- Created ops/pub_x.json and ops/pub_reddit.json with correct content.
- Created ops/reply.json to reply to post_001 with the correct facts.
"""
import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score_details = []

def check(description, max_score, condition, reason_if_fail=""):
    passed = condition()
    score = max_score if passed else 0
    score_details.append({
        "item": description,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": "" if passed else reason_if_fail
    })
    return score

# 1. ops 目录存在（10分）
def ops_dir_exists():
    return os.path.isdir(os.path.join(workspace, "ops"))
check("ops directory exists", 10, ops_dir_exists, "ops/ directory not found")

# 2. pub_x.json 存在且合法 JSON（5分）
pub_x_path = os.path.join(workspace, "ops", "pub_x.json")
def pub_x_valid():
    if not os.path.isfile(pub_x_path):
        return False
    try:
        with open(pub_x_path) as f:
            json.load(f)
        return True
    except:
        return False
check("pub_x.json exists and is valid JSON", 5, pub_x_valid, "pub_x.json missing or malformed")

# 3. pub_reddit.json 存在且合法 JSON（5分）
pub_reddit_path = os.path.join(workspace, "ops", "pub_reddit.json")
def pub_reddit_valid():
    if not os.path.isfile(pub_reddit_path):
        return False
    try:
        with open(pub_reddit_path) as f:
            json.load(f)
        return True
    except:
        return False
check("pub_reddit.json exists and is valid JSON", 5, pub_reddit_valid, "pub_reddit.json missing or malformed")

# 4. reply.json 存在且合法 JSON（5分）
reply_path = os.path.join(workspace, "ops", "reply.json")
def reply_valid():
    if not os.path.isfile(reply_path):
        return False
    try:
        with open(reply_path) as f:
            json.load(f)
        return True
    except:
        return False
check("reply.json exists and is valid JSON", 5, reply_valid, "reply.json missing or malformed")

# 5. pub_x.json 内容检查（20分：平台、发射日期、产品名）
expected_launch_date = "2025-07-16"
expected_product = "Aurora LV-9"
def pub_x_content():
    if not os.path.isfile(pub_x_path):
        return False
    try:
        with open(pub_x_path) as f:
            data = json.load(f)
        # 必须包含 platform 字段为 "x"（不区分大小写？严格一点）
        if not isinstance(data, dict):
            return False
        platform_ok = data.get("platform", "").lower() == "x"
        content = data.get("content", "")
        date_ok = expected_launch_date in content
        product_ok = expected_product in content
        # 可选：tags 包含 #LaunchAlert 或 #AuroraLV9 等，但这里只检查核心数据。
        return platform_ok and date_ok and product_ok
    except:
        return False
check("pub_x.json contains correct platform, launch_date and product_name", 20, pub_x_content,
      "pub_x.json missing platform 'x', or content lacks launch_date / product_name")

# 6. pub_reddit.json 内容检查（20分：平台 reddit、发射日期、产品名）
def pub_reddit_content():
    if not os.path.isfile(pub_reddit_path):
        return False
    try:
        with open(pub_reddit_path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False
        platform_ok = data.get("platform", "").lower() == "reddit"
        content = data.get("content", "")
        date_ok = expected_launch_date in content
        product_ok = expected_product in content
        return platform_ok and date_ok and product_ok
    except:
        return False
check("pub_reddit.json contains correct platform, launch_date and product_name", 20, pub_reddit_content,
      "pub_reddit.json missing platform 'reddit', or content lacks launch_date / product_name")

# 7. reply.json 内容检查（15分：回复的 post_id 正确，包含发射日期和产品名）
def reply_content():
    if not os.path.isfile(reply_path):
        return False
    try:
        with open(reply_path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False
        post_id_ok = data.get("post_id") == "post_001"
        text = data.get("text", "")
        date_ok = expected_launch_date in text
        product_ok = expected_product in text
        return post_id_ok and date_ok and product_ok
    except:
        return False
check("reply.json correctly replies to post_001 with launch_date and product_name", 15, reply_content,
      "reply.json missing correct post_id or content lacks launch_date / product_name")

# 8. 额外检查：没有多余文件（降分？这里作为奖励或扣分，但按满分设计不加分。可以设一个检查项但不用分）
# 为了避免负分，不扣分。我们总分为10+5+5+5+20+20+15 = 80，还差20分，可以加一个精确日期数字匹配的10分和产品名精确匹配10分
# 补充：日期精确匹配（10分）产品名精确匹配（10分）
def exact_date_in_pub_x():
    if not os.path.isfile(pub_x_path):
        return False
    try:
        with open(pub_x_path) as f:
            data = json.load(f)
        return expected_launch_date in data.get("content", "")
    except:
        return False
check("launch_date '2025-07-16' appears in pub_x.json", 10, exact_date_in_pub_x, "pub_x.json does not contain correct launch_date")

def exact_product_in_pub_reddit():
    if not os.path.isfile(pub_reddit_path):
        return False
    try:
        with open(pub_reddit_path) as f:
            data = json.load(f)
        return expected_product in data.get("content", "")
    except:
        return False
check("product_name 'Aurora LV-9' appears in pub_reddit.json", 10, exact_product_in_pub_reddit, "pub_reddit.json does not contain correct product_name")

# 计算总分
total_score = sum(item["score"] for item in score_details)
# 写入结果
result = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"Total score: {total_score}/100")
