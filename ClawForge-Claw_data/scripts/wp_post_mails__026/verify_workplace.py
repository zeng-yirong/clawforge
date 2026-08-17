import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    results = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    dirs_ok = True
    required_dirs = ["ops", "data/emails", "data/attachments", "data/social"]
    for d in required_dirs:
        if not os.path.isdir(d):
            dirs_ok = False
            results.append({
                "item": f"Required directory '{d}' exists",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Directory '{d}' not found"
            })
            break
    if dirs_ok:
        results.append({
            "item": "Required directories exist",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required directories present"
        })

    # 2. 产物文件存在且合法JSON (10分)
    prod_path = "ops/launch_posts.json"
    if not os.path.isfile(prod_path):
        results.append({
            "item": "ops/launch_posts.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
    else:
        try:
            with open(prod_path, "r") as f:
                data = json.load(f)
            if not isinstance(data, list):
                results.append({
                    "item": "ops/launch_posts.json is a list",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "Root is not a list"
                })
            else:
                results.append({
                    "item": "ops/launch_posts.json valid and is list",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "File valid JSON, root is list"
                })
        except Exception as e:
            results.append({
                "item": "ops/launch_posts.json valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {e}"
            })
            data = []

    # 如果文件不合法，后续检查跳过或得0分
    if not isinstance(data, list):
        # 补全剩余检查，给0分
        for item_name in ["Contains exactly 2 posts", "One for X platform", "One for Reddit platform", "X post content includes approved facts", "Reddit content includes approved facts", "Reddit community matches account default", "CTA phrase used in at least one post", "No unapproved facts"]:
            results.append({
                "item": item_name,
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Root is not a list"
            })
        results.append({"item": "Total", "score": 0, "max_score": 100, "passed": False, "reason": "See details"})
        total_score = sum(r["score"] for r in results if r["item"] != "Total")
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2)
        return

    # 3. 帖子数量正确 (10分)
    if len(data) != 2:
        results.append({
            "item": "Contains exactly 2 posts",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 2, got {len(data)}"
        })
    else:
        results.append({
            "item": "Contains exactly 2 posts",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct number of posts"
        })

    # 4. 平台识别 (15分)
    platforms = [post.get("platform", "").lower() for post in data if isinstance(post, dict)]
    has_x = "x" in platforms
    has_reddit = "reddit" in platforms
    x_score = 7 if has_x else 0
    reddit_score = 8 if has_reddit else 0
    results.append({
        "item": "One for X platform",
        "score": x_score,
        "max_score": 7,
        "passed": has_x,
        "reason": "X post found" if has_x else "No X platform post"
    })
    results.append({
        "item": "One for Reddit platform",
        "score": reddit_score,
        "max_score": 8,
        "passed": has_reddit,
        "reason": "Reddit post found" if has_reddit else "No Reddit platform post"
    })

    # 5. 内容事实准确性 (40分)
    # 从附件中读取正确的简报v4
    with open("data/attachments/att_brief_v4.json", "r") as f:
        brief = json.load(f)
    approved_facts = brief["approved_facts"]
    mission_name = brief["mission_name"]
    launch_date = brief["launch_date"]
    payload = brief["payload"]
    target_orbit = brief["target_orbit"]
    booster_recovery = brief["booster_recovery"]

    # 将帖子内容拼接
    all_text = ""
    for post in data:
        if isinstance(post, dict):
            all_text += post.get("content", "") + " " + post.get("title", "") + " "
    all_text_lower = all_text.lower()

    # 检查关键事实
    facts_ok = True
    fact_checks = []
    # 任务名称 Aurora Dawn
    if mission_name.lower() not in all_text_lower:
        fact_checks.append(("Mission name 'Aurora Dawn'", 0))
        facts_ok = False
    else:
        fact_checks.append(("Mission name 'Aurora Dawn'", 5))
    # 发射日期 2025-05-15
    if "may 15, 2025" in all_text_lower or "2025-05-15" in all_text:
        fact_checks.append(("Launch date 'May 15, 2025'", 5))
    else:
        fact_checks.append(("Launch date 'May 15, 2025'", 0))
        facts_ok = False
    # payload: 60 Starlink v2 satellites
    if "60" in all_text and "starlink" in all_text_lower and "v2" in all_text_lower:
        fact_checks.append(("Payload '60 Starlink v2 satellites'", 8))
    else:
        fact_checks.append(("Payload '60 Starlink v2 satellites'", 0))
        facts_ok = False
    # target orbit: 550 km, 53°
    if "550 km" in all_text_lower and "53" in all_text:
        fact_checks.append(("Target orbit '550 km, 53°'", 7))
    else:
        fact_checks.append(("Target orbit '550 km, 53°'", 0))
        facts_ok = False
    # booster recovery: Just Read The Instructions
    if "just read the instructions" in all_text_lower:
        fact_checks.append(("Booster recovery 'Just Read The Instructions'", 7))
    else:
        fact_checks.append(("Booster recovery 'Just Read The Instructions'", 0))
        facts_ok = False
    # 检查是否使用了未批准事实（比如 v2 中的 17200 kg 或 v1 satellites）
    if "17200" in all_text or "v1" in all_text_lower:
        fact_checks.append(("No unapproved facts (v2/v1 data)", 0))
        facts_ok = False
    else:
        fact_checks.append(("No unapproved facts (v2/v1 data)", 8))

    for label, score in fact_checks:
        results.append({
            "item": label,
            "score": score,
            "max_score": 8,
            "passed": score > 0,
            "reason": f"Fact {'found' if score>0 else 'not found or incorrect'}"
        })

    # 6. Reddit帖子社区匹配 (5分)
    reddit_post = next((p for p in data if isinstance(p, dict) and p.get("platform","").lower() == "reddit"), None)
    if reddit_post:
        community = reddit_post.get("community", "")
        if community == "r/SpaceX":
            results.append({
                "item": "Reddit community matches account default (r/SpaceX)",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Correct community"
            })
        else:
            results.append({
                "item": "Reddit community matches account default (r/SpaceX)",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Got '{community}', expected 'r/SpaceX'"
            })
    else:
        results.append({
            "item": "Reddit community matches account default (r/SpaceX)",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Reddit post missing"
        })

    # 7. CTA 短语 (5分)
    cta = "Join the future of space."
    if cta.lower() in all_text_lower:
        results.append({
            "item": "CTA phrase used in at least one post",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "CTA found"
        })
    else:
        results.append({
            "item": "CTA phrase used in at least one post",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "CTA not found"
        })

    # 8. 格式要求：每个post必须有 platform, content, (Reddit需要 community) (5分)
    format_ok = True
    for i, post in enumerate(data):
        if not isinstance(post, dict):
            format_ok = False
            continue
        if "platform" not in post or "content" not in post:
            format_ok = False
        if post.get("platform","").lower() == "reddit" and "community" not in post:
            format_ok = False
    results.append({
        "item": "Each post has required fields (platform, content; Reddit also community)",
        "score": 5 if format_ok else 0,
        "max_score": 5,
        "passed": format_ok,
        "reason": "Format OK" if format_ok else "Missing fields in one or more posts"
    })

    # 汇总总分（忽略总分项）
    total_score = sum(r["score"] for r in results if r["item"] != "Total")
    results.append({
        "item": "Total",
        "score": total_score,
        "max_score": 100,
        "passed": total_score >= 80,
        "reason": f"Total score {total_score}/100"
    })

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    main()
