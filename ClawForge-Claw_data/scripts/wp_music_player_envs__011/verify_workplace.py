import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []

    # ========================
    # 1. 检查 ops 目录 (5分)
    # ========================
    ops_path = os.path.join(workspace, "ops")
    if not os.path.isdir(ops_path):
        details.append({"item":"ops目录存在","score":0,"max_score":5,"passed":False,"reason":"ops目录不存在"})
    else:
        details.append({"item":"ops目录存在","score":5,"max_score":5,"passed":True,"reason":"ops目录存在"})

    # ==================================================
    # 2. 检查 ops/curated_playlist.json 文件存在 (5分)
    # ==================================================
    curated_path = os.path.join(workspace, "ops", "curated_playlist.json")
    if not os.path.isfile(curated_path):
        details.append({"item":"curated_playlist.json文件存在","score":0,"max_score":5,"passed":False,"reason":"文件不存在"})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return
    else:
        details.append({"item":"curated_playlist.json文件存在","score":5,"max_score":5,"passed":True,"reason":"文件存在"})

    # ============================================
    # 3. 解析 agent 输出，检查 JSON 合法性 (10分)
    # ============================================
    try:
        with open(curated_path, "r") as f:
            agent_data = json.load(f)
        if not isinstance(agent_data, list):
            details.append({"item":"输出格式（顶层必须是数组）","score":0,"max_score":10,"passed":False,"reason":"顶层不是数组"})
            total = sum(d["score"] for d in details)
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump({"total_score": total, "details": details}, f, indent=2)
            return
        details.append({"item":"输出格式（顶层必须是数组）","score":10,"max_score":10,"passed":True,"reason":"是合法JSON数组"})
    except Exception as e:
        details.append({"item":"JSON合法性","score":0,"max_score":10,"passed":False,"reason":str(e)})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # ==============================
    # 4. 读取原始数据，计算期望结果
    # ==============================
    try:
        with open(os.path.join(workspace, "data", "songs", "songs.json"), "r") as f:
            songs_data = json.load(f)["songs"]
        with open(os.path.join(workspace, "data", "playlists", "playlists.json"), "r") as f:
            playlists_data = json.load(f)["playlists"]
    except Exception as e:
        details.append({"item":"读取原始数据","score":0,"max_score":0,"passed":False,"reason":"无法读取原始数据: " + str(e)})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # 找到夜驾驶播放列表
    target_playlist = None
    for pl in playlists_data:
        if pl["name"] == "夜驾驶":
            target_playlist = pl
            break
    if target_playlist is None:
        details.append({"item":"查找目标播放列表","score":0,"max_score":0,"passed":False,"reason":"未找到名称为'夜驾驶'的播放列表"})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # 播放列表去重（保持原顺序）
    ordered_ids = []
    seen = set()
    for sid in target_playlist["song_ids"]:
        if sid not in seen:
            seen.add(sid)
            ordered_ids.append(sid)

    # 构建歌曲索引（song_id -> 歌曲对象，若重复取第一条）
    song_map = {}
    for s in songs_data:
        if s["song_id"] not in song_map:
            song_map[s["song_id"]] = s

    # 判断歌曲是否 “所有字段都填写完毕”
    def is_complete(song):
        required_fields = ["song_id","title","artist","album","duration","language","genre","style","era","tags","scene_tags","crowd_tags"]
        for field in required_fields:
            val = song.get(field)
            if val is None:
                return False
            if isinstance(val, str) and val.strip() == "":
                return False
        if not isinstance(song.get("duration"), (int, float)):
            return False
        return True

    expected = []
    for sid in ordered_ids:
        song = song_map.get(sid)
        if song is None:
            continue
        if not is_complete(song):
            continue
        if song["duration"] <= 180:   # 超过3分钟 => >180
            continue
        if song["language"] != "英文":
            continue
        expected.append({
            "song_id": song["song_id"],
            "title": song["title"],
            "artist": song["artist"],
            "duration": song["duration"]
        })

    # 期望结果：5条（S001, S005, S006, S007, S010）
    expected_sorted = sorted(expected, key=lambda x: x["song_id"])

    # ================
    # 5. 歌曲数量 (10分)
    # ================
    if len(agent_data) != len(expected):
        details.append({"item":"歌曲数量","score":0,"max_score":10,"passed":False,"reason":f"期望 {len(expected)} 条，实际 {len(agent_data)} 条"})
    else:
        details.append({"item":"歌曲数量","score":10,"max_score":10,"passed":True,"reason":f"共 {len(expected)} 条"})

    # ======================
    # 6. 字段完整性 (20分)
    # ======================
    required_keys = {"song_id","title","artist","duration"}
    all_fields_ok = True
    for idx, item in enumerate(agent_data):
        if not isinstance(item, dict):
            all_fields_ok = False
            reason = f"第 {idx+1} 项不是字典"
            break
        if set(item.keys()) != required_keys:
            all_fields_ok = False
            reason = f"第 {idx+1} 项字段为 {set(item.keys())}，期望 {required_keys}"
            break
    if all_fields_ok:
        details.append({"item":"字段完整性","score":20,"max_score":20,"passed":True,"reason":"每条记录字段正确"})
    else:
        details.append({"item":"字段完整性","score":0,"max_score":20,"passed":False,"reason":reason})

    # ======================
    # 7. 内容精确匹配 (40分)
    # ======================
    agent_sorted = sorted(agent_data, key=lambda x: x["song_id"])
    if agent_sorted == expected_sorted:
        details.append({"item":"内容精确匹配","score":40,"max_score":40,"passed":True,"reason":"所有字段值完全正确"})
    else:
        details.append({"item":"内容精确匹配","score":0,"max_score":40,"passed":False,"reason":"值与期望不符"})

    # ======================
    # 8. 去重检查 (10分)
    # ======================
    id_set = set()
    dup = False
    for item in agent_data:
        sid = item.get("song_id")
        if sid in id_set:
            dup = True
            break
        id_set.add(sid)
    if dup:
        details.append({"item":"去重检查","score":0,"max_score":10,"passed":False,"reason":"存在重复 song_id"})
    else:
        details.append({"item":"去重检查","score":10,"max_score":10,"passed":True,"reason":"无重复"})

    # ======================
    # 总分与输出
    # ======================
    total = sum(d["score"] for d in details)
    result = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
