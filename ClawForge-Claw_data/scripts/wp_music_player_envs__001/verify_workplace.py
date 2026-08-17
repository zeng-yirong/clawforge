import json
import sys
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace).resolve()
    score_details = []
    total_score = 0

    # 1. 检查结果文件是否存在 (10分)
    result_file = workspace_path / "result.json"
    if result_file.is_file():
        score_details.append({
            "item": "result.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "result.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接写评分并退出
        _write_score(workspace_path, total_score, score_details)
        return

    # 2. 解析JSON格式 (10分)
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score_details.append({
            "item": "result.json 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON有效"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "result.json 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {str(e)}"
        })
        _write_score(workspace_path, total_score, score_details)
        return

    # 3. 检查必需字段 (valid_song_count, night_driving_song_count, night_driving_song_ids) (10分)
    required_keys = ["valid_song_count", "night_driving_song_count", "night_driving_song_ids"]
    missing = [k for k in required_keys if k not in data]
    if not missing:
        score_details.append({
            "item": "必需字段齐全",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "包含所有必需的三个字段"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "必需字段齐全",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少字段: {missing}"
        })

    # 4. 验证 valid_song_count (20分)
    expected_valid_count = 15
    actual_valid_count = data.get("valid_song_count")
    if actual_valid_count == expected_valid_count:
        score_details.append({
            "item": "valid_song_count 正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"数值为 {actual_valid_count}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "valid_song_count 正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 {expected_valid_count}，实际 {actual_valid_count}"
        })

    # 5. 验证 night_driving_song_count (20分)
    expected_night_count = 9
    actual_night_count = data.get("night_driving_song_count")
    if actual_night_count == expected_night_count:
        score_details.append({
            "item": "night_driving_song_count 正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"数值为 {actual_night_count}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "night_driving_song_count 正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 {expected_night_count}，实际 {actual_night_count}"
        })

    # 6. 验证 night_driving_song_ids 内容 (30分)
    expected_ids = sorted([
        "song_001", "song_002", "song_003", "song_004",
        "song_007", "song_009", "song_016", "song_018", "song_019"
    ])
    actual_ids = data.get("night_driving_song_ids")
    if not isinstance(actual_ids, list):
        score_details.append({
            "item": "night_driving_song_ids 内容正确",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "类型不是列表"
        })
    else:
        sorted_actual = sorted(actual_ids)
        if sorted_actual == expected_ids:
            score_details.append({
                "item": "night_driving_song_ids 内容正确",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": f"包含正确的 {len(expected_ids)} 个ID"
            })
            total_score += 30
        else:
            score_details.append({
                "item": "night_driving_song_ids 内容正确",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": f"期望 {expected_ids}，实际 {sorted_actual}"
            })

    # 写入评分
    _write_score(workspace_path, total_score, score_details)

def _write_score(workspace_path, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    score_file = workspace_path / "workplace_score.json"
    with open(score_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
