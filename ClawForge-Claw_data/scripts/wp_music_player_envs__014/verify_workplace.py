#!/usr/bin/env python3
import sys
import os
import json

def verify_workplace(workspace):
    results = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (10分)
    dirs = ["data", "data/playlists", "data/songs", "session", "ops"]
    dir_ok = True
    for d in dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dir_ok = False
            break
    if dir_ok:
        results.append({"item": "目录结构存在", "score": 10, "max_score": 10, "passed": True, "reason": "所有必要目录均存在"})
        total_score += 10
    else:
        results.append({"item": "目录结构存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少目录: {d}"})

    # 2. 输入文件合法性 (10分)
    input_files = ["data/songs/songs.json", "data/playlists/playlists.json", "session/summary.json"]
    input_valid = True
    for fpath in input_files:
        f = os.path.join(workspace, fpath)
        if not os.path.isfile(f):
            input_valid = False
            reason = f"缺少文件 {fpath}"
            break
        try:
            with open(f, "r", encoding="utf-8") as fh:
                json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            input_valid = False
            reason = f"文件 {fpath} 解析错误: {e}"
            break
    if input_valid:
        results.append({"item": "输入文件合法性", "score": 10, "max_score": 10, "passed": True, "reason": "所有输入文件存在且JSON格式正确"})
        total_score += 10
    else:
        results.append({"item": "输入文件合法性", "score": 0, "max_score": 10, "passed": False, "reason": reason})

    # 3. 输出文件存在 (10分)
    output_file = os.path.join(workspace, "ops/next_song.json")
    if os.path.isfile(output_file):
        results.append({"item": "输出文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/next_song.json 已生成"})
        total_score += 10
    else:
        results.append({"item": "输出文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ops/next_song.json"})
        # 提前结束，无需继续检查内容
        results.append({"item": "输出内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": "输出文件缺失"})
        return write_score(workspace, results, total_score, max_total)

    # 4. 输出文件JSON格式与结构 (10分)
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            out_data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        results.append({"item": "输出文件格式", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        results.append({"item": "输出内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": "输出文件格式错误"})
        return write_score(workspace, results, total_score, max_total)

    if isinstance(out_data, dict) and "id" in out_data and isinstance(out_data["id"], str) and out_data["id"].startswith("song_"):
        results.append({"item": "输出文件格式与结构", "score": 10, "max_score": 10, "passed": True, "reason": "输出JSON包含id字段，类型正确"})
        total_score += 10
    else:
        results.append({"item": "输出文件格式与结构", "score": 0, "max_score": 10, "passed": False, "reason": "输出JSON缺少id字段或格式不正确"})
        # 尽管结构不对，仍然尝试解析id，但正确性项将得0分
        # 为简化，直接返回
        results.append({"item": "输出内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": "输出结构不符合要求"})
        return write_score(workspace, results, total_score, max_total)

    # 5. 内容正确性 (70分) - 核心逻辑：根据session和playlist计算正确的下一首
    # 5.1 读取session
    session_path = os.path.join(workspace, "session/summary.json")
    with open(session_path, "r", encoding="utf-8") as f:
        session = json.load(f)
    playlist_id = session.get("playlist_id")
    current_song_id = session.get("current_song_id")

    # 5.2 读取播放列表
    playlists_path = os.path.join(workspace, "data/playlists/playlists.json")
    with open(playlists_path, "r", encoding="utf-8") as f:
        playlists_data = json.load(f)
    playlists = playlists_data.get("playlists", [])
    target_playlist = None
    for pl in playlists:
        if pl.get("playlist_id") == playlist_id:
            target_playlist = pl
            break
    if target_playlist is None:
        results.append({"item": "输出内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": f"未找到playlist_id={playlist_id}"})
        return write_score(workspace, results, total_score, max_total)

    # 5.3 读取songs
    songs_path = os.path.join(workspace, "data/songs/songs.json")
    with open(songs_path, "r", encoding="utf-8") as f:
        songs_data = json.load(f)
    all_songs = songs_data.get("songs", [])
    valid_song_ids = set()
    for s in all_songs:
        sid = s.get("song_id")
        if sid:
            valid_song_ids.add(sid)

    # 5.4 从播放列表中去除无效ID和重复ID（保留第一次出现的顺序）
    raw_ids = target_playlist.get("song_ids", [])
    seen = set()
    cleaned_ids = []
    for sid in raw_ids:
        if sid in valid_song_ids and sid not in seen:
            cleaned_ids.append(sid)
            seen.add(sid)

    # 5.5 找到当前歌曲索引
    if current_song_id not in cleaned_ids:
        results.append({"item": "输出内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": f"当前歌曲 {current_song_id} 不在有效播放列表中"})
        return write_score(workspace, results, total_score, max_total)

    idx = cleaned_ids.index(current_song_id)
    if idx + 1 >= len(cleaned_ids):
        # 如果是最后一首，下一首应该是循环到第一首？不过任务描述没提，我们假定没有下一首则无解，但更合理是出题只给出非末尾的情况
        # 这里判断为错误
        results.append({"item": "输出内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": "当前歌曲是播放列表最后一首，无下一首"})
        return write_score(workspace, results, total_score, max_total)
    expected_next_id = cleaned_ids[idx + 1]

    # 5.6 比对
    agent_id = out_data["id"]
    if agent_id == expected_next_id:
        results.append({"item": "输出内容正确性", "score": 70, "max_score": 70, "passed": True, "reason": f"下一首歌曲ID正确: {expected_next_id}"})
        total_score += 70
    else:
        results.append({"item": "输出内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": f"期望ID={expected_next_id}，实际ID={agent_id}"})

    # 分项积分已累加，写入结果
    write_score(workspace, results, total_score, max_total)

def write_score(workspace, details, total_score, max_total):
    # 确保total_score整数
    total_score = min(total_score, max_total)
    score_data = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)
    print(f"Verification complete. Total score: {total_score}/{max_total}")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
