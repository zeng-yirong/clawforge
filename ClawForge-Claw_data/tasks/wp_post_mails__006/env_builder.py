import os
import json
import random

POSTS_DATA = [
    {"post_id": "p001", "platform": "reddit", "community": "auroralabs", "needs_response": True, "content": "When is the launch?"},
    {"post_id": "p002", "platform": "x", "community": "auroralabs", "needs_response": False, "content": "Great work!"},
    {"post_id": "p003", "platform": "reddit", "community": "spacex", "needs_response": True, "content": "Will there be a livestream?"},
    {"post_id": "p004", "platform": "x", "community": "spacex", "needs_response": True, "content": "Any delay?"},
    {"post_id": "p005", "platform": "reddit", "community": "blueorigin", "needs_response": True, "content": "Where can I buy tickets?"},
    {"post_id": "p006", "platform": "x", "community": "blueorigin", "needs_response": False, "content": "Nice logo!"},
    {"post_id": "p007", "platform": "reddit", "community": "virgingalactic", "needs_response": True, "content": "Is it safe?"},
    {"post_id": "p008", "platform": "x", "community": "virgingalactic", "needs_response": True, "content": "Test flight status?"},
    {"post_id": "p009", "platform": "reddit", "community": "auroralabs", "needs_response": True, "content": "How to watch?"},
    {"post_id": "p010", "platform": "x", "community": "spacex", "needs_response": True, "content": "Delay confirmed?"},
    {"post_id": "p011", "platform": "reddit", "community": "blueorigin", "needs_response": False, "content": "Old news"},
    {"post_id": "p012", "platform": "x", "community": "auroralabs", "needs_response": False, "content": "Ignore"},
    {"post_id": "p013", "platform": "reddit", "community": "starhopper", "needs_response": True, "content": "Test schedule?"},
    {"post_id": "p014", "platform": "x", "community": "starhopper", "needs_response": True, "content": "Is it reusable?"},
]

def build_env():
    os.makedirs("data/social", exist_ok=True)
    for post in POSTS_DATA:
        file_path = f"data/social/{post['post_id']}.json"
        with open(file_path, "w") as f:
            json.dump(post, f)
    # 添加一个非 JSON 干扰文件
    with open("data/social/readme.txt", "w") as f:
        f.write("This is not a post file.")
    # 输出预期的正确答案（供 verify 使用，但不暴露给 agent）
    expected_counts = {}
    for post in POSTS_DATA:
        if post["needs_response"]:
            c = post["community"]
            expected_counts[c] = expected_counts.get(c, 0) + 1
    # 排序：按 count 降序，count 相同时按社区名升序
    sorted_communities = sorted(expected_counts.items(), key=lambda x: (-x[1], x[0]))
    expected_result = [{"community": comm, "count": cnt} for comm, cnt in sorted_communities]
    # 存入隐藏位置？不存，直接由 verify 自己计算。

if __name__ == "__main__":
    build_env()
