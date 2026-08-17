import os
import json

def build_env():
    # 创建 data 目录
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)

    # 歌曲库 songs.json (注意 song_003 缺失，模拟脏数据)
    songs = {
        "songs": [
            {"song_id": "song_001", "title": "Speed", "artist": "A", "album": "X", "duration": 240, "language": "英文", "genre": "摇滚", "style": "快", "era": "2010s", "tags": ["drive"], "scene_tags": ["night"], "crowd_tags": ["adult"]},
            {"song_id": "song_002", "title": "Moonlight", "artist": "B", "album": "Y", "duration": 210, "language": "中文", "genre": "流行", "style": "舒缓", "era": "2000s", "tags": ["chill"], "scene_tags": ["night"], "crowd_tags": ["all"]},
            {"song_id": "song_004", "title": "Highway", "artist": "C", "album": "Z", "duration": 300, "language": "英文", "genre": "电子", "style": "动感", "era": "2020s", "tags": ["drive"], "scene_tags": ["night"], "crowd_tags": ["adult"]},
            {"song_id": "song_005", "title": "Rain", "artist": "D", "album": "W", "duration": 195, "language": "中文", "genre": "民谣", "style": "安静", "era": "2010s", "tags": ["rain"], "scene_tags": ["calm"], "crowd_tags": ["all"]},
        ]
    }
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

    # 播放列表 playlists.json (夜驾驶歌单包含 song_003 这个无效ID)
    playlists = {
        "playlists": [
            {
                "playlist_id": "night_drive",
                "name": "夜驾驶",
                "description": "夜晚开车听的歌",
                "song_ids": ["song_001", "song_002", "song_003", "song_004"],
                "created_at": "2024-01-01",
                "updated_at": "2024-06-01"
            },
            {
                "playlist_id": "hi_energy",
                "name": "嗨曲串烧",
                "description": "运动健身嗨曲",
                "song_ids": ["song_005", "song_001"],
                "created_at": "2024-02-01",
                "updated_at": "2024-05-01"
            }
        ]
    }
    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)

    # 标签定义 (干扰项)
    tag_defs = {
        "tag_definitions": [
            {"tag": "drive", "description": "适合开车"},
            {"tag": "night", "description": "夜晚场景"}
        ]
    }
    with open("data/tags/tag_definitions.json", "w", encoding="utf-8") as f:
        json.dump(tag_defs, f, ensure_ascii=False, indent=2)

    # 当前播放歌曲信息
    with open("current_song.txt", "w") as f:
        f.write("song_002\n")

    # 确保 ops 目录不存在 (让 agent 创建)
    if os.path.exists("ops"):
        import shutil
        shutil.rmtree("ops")

if __name__ == "__main__":
    build_env()
