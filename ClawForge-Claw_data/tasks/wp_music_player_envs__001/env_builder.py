import json
import os
import random

def build_env():
    # 确保目录存在
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # 定义的歌曲（有效ID从song_001到song_010，song_016到song_020）
    songs = {}
    for i in range(1, 11):
        sid = f"song_{i:03d}"
        song = {
            "song_id": sid,
            "title": f"Track {i}",
            "artist": "Unknown",
            "album": "Album A",
            "duration": 180 + i * 10,
            "language": "中文",
            "genre": "流行",
            "style": "动感",
            "era": "2010s",
            "tags": [],
            "scene_tags": [],
            "crowd_tags": []
        }
        # 分配场景和受众标签
        if i == 1:
            song["scene_tags"] = ["夜驾驶"]
        elif i == 2:
            song["crowd_tags"] = ["驾驶"]
        elif i == 3:
            song["scene_tags"] = ["夜驾驶", "浪漫"]
        elif i == 4:
            song["crowd_tags"] = ["驾驶", "家庭"]
        elif i == 5:
            pass  # 不符合
        elif i == 6:
            song["scene_tags"] = ["驾驶"]  # 注意不是“夜驾驶”
        elif i == 7:
            song["scene_tags"] = ["夜驾驶"]
            song["crowd_tags"] = ["驾驶"]
        elif i == 8:
            song["crowd_tags"] = ["乘客"]
        elif i == 9:
            song["scene_tags"] = ["夜驾驶"]
            song["crowd_tags"] = ["家庭"]
        elif i == 10:
            pass
        songs[sid] = song

    # 添加 song_016 ~ song_020
    for i in range(16, 21):
        sid = f"song_{i:03d}"
        song = {
            "song_id": sid,
            "title": f"Track {i}",
            "artist": "Unknown",
            "album": "Album B",
            "duration": 200 + i,
            "language": "中文",
            "genre": "流行",
            "style": "舒缓",
            "era": "2010s",
            "tags": [],
            "scene_tags": [],
            "crowd_tags": []
        }
        if i == 16:
            song["scene_tags"] = ["运动"]
            song["crowd_tags"] = ["驾驶"]
        elif i == 17:
            pass
        elif i == 18:
            song["scene_tags"] = ["夜驾驶"]
        elif i == 19:
            song["crowd_tags"] = ["驾驶"]
        elif i == 20:
            song["scene_tags"] = ["旅行"]
            song["crowd_tags"] = ["家庭"]
        songs[sid] = song

    # 写入 songs.json
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump({"songs": list(songs.values())}, f, ensure_ascii=False, indent=2)

    # 播放列表（包含一些无效ID）
    playlists = [
        {
            "playlist_id": "pl_001",
            "name": "嗨曲串烧",
            "description": "运动健身嗨曲",
            "song_ids": ["song_001", "song_002", "song_011", "song_005", "song_012"],
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-10T00:00:00"
        },
        {
            "playlist_id": "pl_002",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["song_003", "song_004", "song_006", "song_013", "song_016", "song_010"],
            "created_at": "2025-01-02T00:00:00",
            "updated_at": "2025-01-11T00:00:00"
        },
        {
            "playlist_id": "pl_003",
            "name": "怀旧金曲",
            "description": "80后90后回忆杀",
            "song_ids": ["song_007", "song_008", "song_009", "song_014", "song_015", "song_017", "song_018", "song_019", "song_020"],
            "created_at": "2025-01-03T00:00:00",
            "updated_at": "2025-01-12T00:00:00"
        }
    ]
    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump({"playlists": playlists}, f, ensure_ascii=False, indent=2)

    # 干扰：标签定义
    tags_def = [
        {"tag": "夜驾驶", "description": "适合夜间驾驶的歌曲"},
        {"tag": "驾驶", "description": "驾驶场景相关"},
        {"tag": "浪漫", "description": "浪漫氛围"},
        {"tag": "运动", "description": "运动健身"},
        {"tag": "旅行", "description": "旅行途中"}
    ]
    with open("data/tags/tag_definitions.json", "w", encoding="utf-8") as f:
        json.dump({"tag_definitions": tags_def}, f, ensure_ascii=False, indent=2)

    # 干扰日志文件
    with open("logs/driving_log.txt", "w") as f:
        f.write("2025-01-15 23:00:01 INFO Playback started: song_001\n")
        f.write("2025-01-15 23:03:45 WARN Song song_011 not found in library\n")

    # 干扰备份文件
    with open("backup/songs_backup_old.json", "w", encoding="utf-8") as f:
        json.dump({"songs": []}, f)

if __name__ == "__main__":
    build_env()
