import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 辅助函数：读取JSON文件
    def read_json(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    # 1. 检查ops目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops目录存在"})
        total_score += 10
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops目录不存在"})
        # 后续依赖ops目录，直接返回
        write_score(total_score, details)
        return

    # 2. 检查ops/next_song.json文件是否存在 (10分)
    next_song_path = os.path.join(ops_dir, "next_song.json")
    if os.path.isfile(next_song_path):
        details.append({"item": "next_song.json文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "next_song.json文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        write_score(total_score, details)
        return

    # 3. 解析next_song.json，检查是否为合法JSON (10分)
    agent_output = read_json(next_song_path)
    if agent_output is None:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件无法解析为合法JSON"})
        write_score(total_score, details)
        return
    else:
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "合法JSON"})
        total_score += 10

    # 4. 计算正确答案
    current_state = read_json(os.path.join(ops_dir, "current_state.json"))
    if current_state is None:
        details.append({"item": "读取current_state.json", "score": 0, "max_score": 10, "passed": False, "reason": "无法读取当前状态文件"})
        write_score(total_score, details)
        return

    playlists_data = read_json(os.path.join(workspace, "data/playlists/playlists.json"))
    songs_data = read_json(os.path.join(workspace, "data/songs/songs.json"))
    if playlists_data is None or songs_data is None:
        details.append({"item": "数据文件完整性", "score": 0, "max_score": 10, "passed": False, "reason": "无法读取playlists或songs数据"})
        write_score(total_score, details)
        return

    # 查找当前播放列表
    playlist_id = current_state.get("playlist_id")
    target_playlist = None
    for pl in playlists_data["playlists"]:
        if pl["playlist_id"] == playlist_id:
            target_playlist = pl
            break
    if target_playlist is None:
        details.append({"item": "当前播放列表存在", "score": 0, "max_score": 10, "passed": False, "reason": f"未找到playlist_id={playlist_id}"})
        write_score(total_score, details)
        return

    current_song_id = current_state.get("song_id")
    song_ids = target_playlist["song_ids"]
    try:
        idx = song_ids.index(current_song_id)
    except ValueError:
        details.append({"item": "当前歌曲在播放列表中", "score": 0, "max_score": 10, "passed": False, "reason": f"song_id={current_song_id}不在播放列表中"})
        write_score(total_score, details)
        return

    # 计算下一首
    next_idx = idx + 1
    if next_idx >= len(song_ids):
        # 不循环，无下一首
        expected_next_id = None
        expected_song = None
    else:
        expected_next_id = song_ids[next_idx]
        # 从songs中找到该歌曲
        song_map = {s["song_id"]: s for s in songs_data["songs"]}
        expected_song = song_map.get(expected_next_id)

    # 5. 检查必需字段是否存在 (30分，每个字段10分)
    required_fields = ["song_id", "title", "artist"]
    field_scores = 0
    field_details = []
    for field in required_fields:
        if field in agent_output and agent_output[field] is not None:
            field_scores += 10
            field_details.append({"field": field, "passed": True})
        else:
            field_details.append({"field": field, "passed": False})
    details.append({"item": "必需字段存在", "score": field_scores, "max_score": 30, "passed": field_scores == 30, "reason": f"song_id:{'有' if field_details[0]['passed'] else '无'}, title:{'有' if field_details[1]['passed'] else '无'}, artist:{'有' if field_details[2]['passed'] else '无'}"})
    total_score += field_scores

    # 6. 字段值正确性 (30分)
    value_scores = 0
    if expected_song is not None:
        # 需要输出下一首歌曲的信息
        if agent_output.get("song_id") == expected_song["song_id"]:
            value_scores += 10
        if agent_output.get("title") == expected_song["title"]:
            value_scores += 10
        if agent_output.get("artist") == expected_song["artist"]:
            value_scores += 10
    else:
        # 无下一首，期望agent输出null或空对象，我们要求song_id为None或其他特殊标记
        # 简单的：如果song_id字段存在且为None/空字符串，或者整个对象为空字典
        # 这里我们设定当无下一首时，agent应输出 {"song_id": null, "title": null, "artist": null}
        # 为了测试，我们确保不是这种情况，所以这段代码不会触发
        if agent_output.get("song_id") is None:
            value_scores += 30
        else:
            value_scores = 0

    details.append({"item": "字段值与预期一致", "score": value_scores, "max_score": 30, "passed": value_scores == 30, "reason": f"song_id:{agent_output.get('song_id')} vs {expected_song['song_id'] if expected_song else 'None'}, title对比, artist对比"})
    total_score += value_scores

    # 7. 无多余顶级字段 (10分)
    allowed = set(required_fields)
    extra = set(agent_output.keys()) - allowed
    if not extra:
        details.append({"item": "无多余顶级字段", "score": 10, "max_score": 10, "passed": True, "reason": "没有额外字段"})
        total_score += 10
    else:
        details.append({"item": "无多余顶级字段", "score": 0, "max_score": 10, "passed": False, "reason": f"包含额外字段: {sorted(extra)}"})
        # 不扣分？我们给0分

    # 总分限制在0-100，四舍五入取整
    total_score = min(total_score, 100)
    total_score = int(round(total_score))

    write_score(total_score, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"总得分: {total}/100")
    sys.exit(0 if total >= 60 else 1)  # 可根据需要调整

if __name__ == "__main__":
    main()
