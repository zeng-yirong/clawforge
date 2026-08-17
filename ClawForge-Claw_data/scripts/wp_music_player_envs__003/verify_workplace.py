import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws_path = Path(workspace)

    details = []
    total_score = 0

    # 1. 检查 ops/play_queue.json 是否存在（10分）
    queue_path = ws_path / "ops" / "play_queue.json"
    if queue_path.exists():
        details.append({
            "item": "ops/play_queue.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/play_queue.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接输出结果
        output_score(total_score, details)
        return

    # 2. JSON 合法性检查（10分）
    try:
        with open(queue_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        output_score(total_score, details)
        return

    # 3. 检查必需字段 playlist_name 和 song_ids（10分）
    if not isinstance(data, dict):
        details.append({
            "item": "输出是字典类型",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "不是字典"
        })
        total_score += 0
    else:
        if "playlist_name" in data and "song_ids" in data:
            details.append({
                "item": "包含 playlist_name 和 song_ids",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "字段存在"
            })
            total_score += 10
        else:
            missing = []
            if "playlist_name" not in data: missing.append("playlist_name")
            if "song_ids" not in data: missing.append("song_ids")
            details.append({
                "item": "包含 playlist_name 和 song_ids",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"缺少字段: {', '.join(missing)}"
            })

    # 4. playlist_name 是否正确（10分）
    if data.get("playlist_name") == "夜驾驶":
        details.append({
            "item": "playlist_name = 夜驾驶",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "正确"
        })
        total_score += 10
    else:
        details.append({
            "item": "playlist_name = 夜驾驶",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际值: {data.get('playlist_name')}"
        })

    # 5. song_ids 长度检查（20分）
    song_ids = data.get("song_ids", [])
    if not isinstance(song_ids, list):
        details.append({
            "item": "song_ids 是列表",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "不是列表"
        })
    elif len(song_ids) == 3:
        details.append({
            "item": "song_ids 长度 = 3",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "长度正确"
        })
        total_score += 20
    else:
        details.append({
            "item": "song_ids 长度 = 3",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"实际长度: {len(song_ids)}"
        })

    # 6. song_ids 内容及顺序精确匹配（50分）
    expected = ["s001", "s002", "s003"]
    if song_ids == expected:
        details.append({
            "item": "song_ids 内容与顺序正确",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": "完全匹配"
        })
        total_score += 50
    else:
        # 部分匹配给分，减少到最后
        reason = f"期望 {expected}，实际 {song_ids}"
        # 计算有多少元素正确且位置正确
        correct_count = sum(1 for i, s in enumerate(song_ids) if i < len(expected) and s == expected[i])
        partial_score = int(50 * correct_count / len(expected))
        details.append({
            "item": "song_ids 内容与顺序正确",
            "score": partial_score,
            "max_score": 50,
            "passed": False,
            "reason": reason
        })
        total_score += partial_score

    # 输出最终得分
    output_score(total_score, details)

def output_score(total_score, details):
    # 确保总分不超过100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    # 写入 workplace_score.json
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
