import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def score(passed, max_score):
    return (max_score if passed else 0)

details = []
total_score = 0

# 1. 检查 ops/launch_post.json 是否存在
post_path = os.path.join(workspace, "ops", "launch_post.json")
exists = os.path.isfile(post_path)
details.append({
    "item": "产物文件 ops/launch_post.json 存在",
    "score": score(exists, 10),
    "max_score": 10,
    "passed": exists,
    "reason": "文件存在" if exists else "文件不存在"
})
total_score += details[-1]["score"]

if not exists:
    # 后续检查无法进行，余下全0
    for item in ["JSON 格式合法", "platform 字段为 'x'", "title 字段正确", "content 字段正确"]:
        details.append({
            "item": item,
            "score": 0,
            "max_score": [10, 20, 30, 30][len(details)-1],
            "passed": False,
            "reason": "产物文件缺失"
        })
    total_score = 0
else:
    # 2. JSON 格式合法
    try:
        with open(post_path, "r") as f:
            data = json.load(f)
        valid_json = True
    except Exception as e:
        valid_json = False
        data = None
    details.append({
        "item": "JSON 格式合法",
        "score": score(valid_json, 10),
        "max_score": 10,
        "passed": valid_json,
        "reason": "JSON 解析成功" if valid_json else f"JSON 解析失败: {e}"
    })
    total_score += details[-1]["score"]

    if not valid_json:
        # 后续检查无法进行
        for item in ["platform 字段为 'x'", "title 字段正确", "content 字段正确"]:
            details.append({
                "item": item,
                "score": 0,
                "max_score": [20, 30, 30][len(details)-4],
                "passed": False,
                "reason": "JSON 解析失败"
            })
    else:
        # 3. platform 字段必须是 'x'
        platform_ok = data.get("platform") == "x"
        details.append({
            "item": "platform 字段为 'x'",
            "score": score(platform_ok, 20),
            "max_score": 20,
            "passed": platform_ok,
            "reason": f"platform = {data.get('platform')}" if not platform_ok else "正确"
        })
        total_score += details[-1]["score"]

        # 4. title 字段必须与附件 v3 中的 title 一致
        expected_title = "Orbital Dawn Launch Announcement"
        title_ok = data.get("title") == expected_title
        details.append({
            "item": "title 字段正确",
            "score": score(title_ok, 30),
            "max_score": 30,
            "passed": title_ok,
            "reason": f"title = {data.get('title')}" if not title_ok else "正确"
        })
        total_score += details[-1]["score"]

        # 5. content 字段必须与附件 v3 中的 post_content 一致
        expected_content = "Join us for the launch of Orbital Dawn on September 1st, 2025. This mission marks a milestone in space exploration. #OrbitalDawn"
        content_ok = data.get("content") == expected_content
        details.append({
            "item": "content 字段正确",
            "score": score(content_ok, 30),
            "max_score": 30,
            "passed": content_ok,
            "reason": f"content = {data.get('content')}" if not content_ok else "正确"
        })
        total_score += details[-1]["score"]

    # 额外检查：如果有其他多余字段，不扣分（允许）

# 写入结果
result = {
    "total_score": total_score,
    "details": details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
