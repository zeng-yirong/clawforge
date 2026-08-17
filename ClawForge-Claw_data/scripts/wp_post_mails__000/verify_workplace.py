import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_total = 100
    details = []

    # helper
    def add_detail(item, score_obtained, max_score, passed, reason):
        details.append({
            "item": item,
            "score": score_obtained,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # 1. 检查 drafts 目录是否存在 (5分)
    drafts_dir = os.path.join(workspace, "drafts")
    if os.path.isdir(drafts_dir):
        add_detail("drafts directory exists", 5, 5, True, "")
        score += 5
    else:
        add_detail("drafts directory exists", 0, 5, False, "drafts/ directory not found")

    # 2. 检查 launch_draft.json 文件是否存在 (10分)
    target_file = os.path.join(drafts_dir, "launch_draft.json")
    if os.path.isfile(target_file):
        add_detail("launch_draft.json file exists", 10, 10, True, "")
        score += 10
    else:
        add_detail("launch_draft.json file exists", 0, 10, False, "drafts/launch_draft.json not found")
        # 无法继续，但仍输出部分分数
        final_score(score, details)
        return

    # 3. 检查是否为合法 JSON (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        add_detail("Valid JSON", 10, 10, True, "")
        score += 10
    except Exception as e:
        add_detail("Valid JSON", 0, 10, False, f"File is not valid JSON: {e}")
        final_score(score, details)
        return

    # 4. 检查必要字段存在: title, content, platforms, tags (每个5分)
    required_fields = ["title", "content", "platforms", "tags"]
    for field in required_fields:
        if field in data:
            add_detail(f"Field '{field}' exists", 5, 5, True, "")
            score += 5
        else:
            add_detail(f"Field '{field}' exists", 0, 5, False, f"Missing field: {field}")

    # 5. 检查标题是否包含 "Nova II" (5分)
    title = data.get("title", "")
    if "Nova II" in title:
        add_detail("Title contains 'Nova II'", 5, 5, True, "")
        score += 5
    else:
        add_detail("Title contains 'Nova II'", 0, 5, False, f"Title '{title}' does not contain 'Nova II'")

    # 6. 检查正文是否包含 tagline "Redefining the horizon" (10分)
    content = data.get("content", "")
    if "Redefining the horizon" in content:
        add_detail("Content includes correct tagline", 10, 10, True, "")
        score += 10
    else:
        add_detail("Content includes correct tagline", 0, 10, False, f"Content missing correct tagline. Got: {content}")

    # 7. 检查平台列表是否等于 ["x", "reddit"] (15分)
    platforms = data.get("platforms", [])
    if platforms == ["x", "reddit"]:
        add_detail("Platforms correct (x, reddit)", 15, 15, True, "")
        score += 15
    else:
        add_detail("Platforms correct (x, reddit)", 0, 15, False, f"Platforms are {platforms}, expected ['x', 'reddit']")

    # 8. 检查话题标签：至少3个，包含 "#NovaII" 和 "#launch" (15分)
    tags = data.get("tags", [])
    tag_ok = True
    if not isinstance(tags, list):
        add_detail("Tags is a list", 0, 15, False, "tags is not a list")
        tag_ok = False
    elif len(tags) < 3:
        add_detail("Tags count >= 3", 0, 15, False, f"Only {len(tags)} tags found")
        tag_ok = False
    else:
        if "#NovaII" in tags and "#launch" in tags:
            add_detail("Tags contain #NovaII and #launch", 10, 10, True, "")
            score += 10
            # 剩余5分给至少3个
            if len(tags) >= 3:
                add_detail("At least 3 tags", 5, 5, True, "")
                score += 5
            else:
                add_detail("At least 3 tags", 0, 5, False, "")
        else:
            add_detail("Tags contain #NovaII and #launch", 0, 10, False, f"Missing required hashtags. Tags: {tags}")
            tag_ok = False

    # 9. 检查没有多余字段 （即只有 title, content, platforms, tags） (10分)
    allowed_fields = {"title", "content", "platforms", "tags"}
    actual_fields = set(data.keys())
    extra = actual_fields - allowed_fields
    if not extra:
        add_detail("No extra fields", 10, 10, True, "")
        score += 10
    else:
        add_detail("No extra fields", 0, 10, False, f"Extra fields present: {extra}")

    # 10. 检查数据来源唯一性：确保没有使用旧版附件的错误数据 (15分)
    # 旧版 tagline 是 "Next-gen computing"，platforms 含 "linkedin"
    source_ok = True
    if "Next-gen computing" in content or "linkedin" in str(platforms):
        add_detail("Data from correct source", 0, 15, False, "Content or platforms from old draft detected")
        source_ok = False
    else:
        add_detail("Data from correct source", 15, 15, True, "")
        score += 15

    final_score(score, details)

def final_score(score, details):
    total = min(score, 100)
    output = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
