import os
import json
import shutil

def build_env():
    # 清理旧环境（如果存在）
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("logs"):
        shutil.rmtree("logs")
    if os.path.exists("ops"):
        shutil.rmtree("ops")

    # 创建目录
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # === 歌曲数据 ===
    songs = [
        {
            "song_id": "song_001",
            "title": "夜空中最亮的星",
            "artist": "逃跑计划",
            "album": "世界",
            "duration": 267,
            "language": "中文",
            "genre": "摇滚",
            "style": "流行摇滚",
            "era": "2010s",
            "tags": ["night", "driving"],
            "scene_tags": ["highway"],
            "crowd_tags": ["young"]
        },
        {
            "song_id": "song_002",
            "title": "Hotel California",
            "artist": "Eagles",
            "album": "Hotel California",
            "duration": 391,
            "language": "英文",
            "genre": "摇滚",
            "style": "经典摇滚",
            "era": "1970s",
            "tags": ["classic", "road"],
            "scene_tags": ["highway"],
            "crowd_tags": ["adult"]
        },
        {
            "song_id": "song_003",
            "title": "平凡之路",
            "artist": "朴树",
            "album": "猎户星座",
            "duration": 300,
            "language": "中文",
            "genre": "民谣",
            "style": "独立民谣",
            "era": "2010s",
            "tags": ["life", "driving"],
            "scene_tags": ["countryside"],
            "crowd_tags": ["young", "middle"]
        },
        {
            "song_id": "song_004",
            "title": "故障曲目",
            "artist": "未知",
            "album": "测试专辑",
            "duration": -1,
            "language": "中文",
            "genre": "流行",
            "style": "电子",
            "era": "2000s",
            "tags": ["night", "error"],
            "scene_tags": ["city"],
            "crowd_tags": ["all"]
        },
        {
            "song_id": "song_005",
            "title": "Speed of Sound",
            "artist": "Coldplay",
            "album": "X&Y",
            "duration": 295,
            "language": "英文",
            "genre": "流行",
            "style": "另类流行",
            "era": "2000s",
            "tags": ["speed", "driving"],
            "scene_tags": ["highway"],
            "crowd_tags": ["young"]
        }
    ]

    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump({"songs": songs}, f, ensure_ascii=False, indent=2)

    # === 播放列表数据 ===
    playlists = [
        {
            "playlist_id": "night_drive",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["song_001", "song_004", "song_005"],
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-03-20T23:00:00"
        },
        {
            "playlist_id": "classic_gold",
            "name": "怀旧金曲",
            "description": "80后90后回忆杀",
            "song_ids": ["song_002", "song_003"],
            "created_at": "2025-01-02T00:00:00",
            "updated_at": "2025-03-19T12:00:00"
        }
    ]

    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump({"playlists": playlists}, f, ensure_ascii=False, indent=2)

    # === 标签定义（干扰项） ===
    tag_definitions = [
        {"tag": "night", "description": "适合夜晚场景"},
        {"tag": "driving", "description": "驾驶场景"},
        {"tag": "error", "description": "异常曲目标记"},
    ]

    with open("data/tags/tag_definitions.json", "w", encoding="utf-8") as f:
        json.dump({"tag_definitions": tag_definitions}, f, ensure_ascii=False, indent=2)

    # === 错误日志 ===
    with open("logs/error.log", "w", encoding="utf-8") as f:
        f.write("2025-03-21 03:00:00 [ERROR] Player 'car_player' encountered invalid duration for song_id=song_004. Skipping.\n")
        f.write("2025-03-21 03:00:01 [INFO] Switched to next track.\n")

    # === 额外干扰文件 ===
    with open("logs/debug.log", "w") as f:
        f.write("2025-03-21 02:59:00 [DEBUG] System health check passed.\n")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
