import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0

    # 1. 目录结构存在性 (10分)
    dirs_ok = True
    required_dirs = ["ops", "data/playlists", "data/songs"]
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失目录 {d}"})
            dirs_ok = False
            break
    if dirs_ok:
        details.append({"item": "目录结构", "score": 10, "max_score": 10, "passed": True, "reason": "所有必要目录存在"})
        total_score += 10

    # 2. 结果文件 ops/playlist_analysis.json 存在且合法JSON (20分)
    result_path = os.path.join(workspace, "ops", "playlist_analysis.json")
    if not os.path.isfile(result_path):
        details.append({"item": "结果文件存在", "score": 0, "max_score": 20, "passed": False, "reason": "ops/playlist_analysis.json 不存在"})
        # 跳过后续检查
        print(json.dumps({"total_score": total_score, "details": details}, ensure_ascii=False))
        return

    try:
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "结果文件合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 解析成功"})
        total_score += 20
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "结果文件合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        print(json.dumps({"total_score": total_score, "details": details}, ensure_ascii=False))
        return

    # 3. 检查字段完整性 (20分)
    if not isinstance(data, dict):
        details.append({"item": "结果格式", "score": 0, "max_score": 20, "passed": False, "reason": "结果不是 JSON 对象"})
        print(json.dumps({"total_score": total_score, "details": details}, ensure_ascii=False))
        return

    # 允许的字段键：playlist_id, count 或 song_count
    if "playlist_id" not in data:
        details.append({"item": "字段 playlist_id", "score": 0, "max_score": 20, "passed": False, "reason": "缺少 playlist_id 字段"})
        print(json.dumps({"total_score": total_score, "details": details}, ensure_ascii=False))
        return

    # 支持 count 或 song_count
    count_key = "count" if "count" in data else ("song_count" if "song_count" in data else None)
    if count_key is None:
        details.append({"item": "字段 count/song_count", "score": 0, "max_score": 20, "passed": False, "reason": "缺少 count 或 song_count 字段"})
        print(json.dumps({"total_score": total_score, "details": details}, ensure_ascii=False))
        return

    details.append({"item": "字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": f"包含 playlist_id 和 {count_key} 字段"})
    total_score += 20

    # 4. 数值正确性 (50分)
    correct_playlist_id = "PL05"
    correct_count = 12  # "速度与激情" 中 song_ids 长度

    pid = data["playlist_id"]
    cnt = data[count_key]

    if pid == correct_playlist_id and cnt == correct_count:
        details.append({"item": "核心数值正确", "score": 50, "max_score": 50, "passed": True, "reason": f"playlist_id={pid}, count={cnt}"})
        total_score += 50
    elif pid == correct_playlist_id and cnt != correct_count:
        details.append({"item": "playlist_id 正确但数量错误", "score": 25, "max_score": 50, "passed": False, "reason": f"playlist_id正确，但count={cnt}，预期{correct_count}"})
        total_score += 25
    elif pid != correct_playlist_id and cnt == correct_count:
        details.append({"item": "数量正确但 playlist_id 错误", "score": 30, "max_score": 50, "passed": False, "reason": f"count正确，但playlist_id={pid}，预期{correct_playlist_id}"})
        total_score += 30
    else:
        details.append({"item": "数值错误", "score": 0, "max_score": 50, "passed": False, "reason": f"playlist_id={pid}, count={cnt}，均不正确"})

    # 5. 额外奖励：不允许有多余字段（不扣分，但提示）
    expected_keys = {"playlist_id", count_key}
    extra_keys = set(data.keys()) - expected_keys
    if extra_keys:
        details.append({"item": "无多余字段", "score": 0, "max_score": 0, "passed": True, "reason": f"包含额外字段: {extra_keys}（无影响）"})

    # 写入评分结果
    score_report = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_report, f, ensure_ascii=False, indent=2)

    print(json.dumps(score_report, ensure_ascii=False))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
