import os
import json
from datetime import datetime

def build_env():
    # 创建目录结构
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 干扰文件
    with open("data/README.txt", "w") as f:
        f.write("This folder contains the music player data.\n")

    # playlists 数据
    playlists = {
        "playlists": [
            {
                "playlist_id": "pl_001",
                "name": "嗨曲串烧",
                "description": "运动健身嗨曲",
                "song_ids": ["s001", "s005", "s009"],
                "created_at": "2024-01-10T08:00:00Z",
                "updated_at": "2024-02-15T12:30:00Z"
            },
            {
                "playlist_id": "pl_002",
                "name": "夜驾驶",
                "description": "夜晚开车听的歌",
                "song_ids": ["s002", "s003", "s004", "s006"],
                "created_at": "2024-01-12T10:00:00Z",
                "updated_at": "2024-03-01T09:00:00Z"
            },
            {
                "playlist_id": "pl_003",
                "name": "怀旧金曲",
                "description": "80后90后回忆杀",
                "song_ids": ["s007", "s008"],
                "created_at": "2024-01-15T14:00:00Z",
                "updated_at": "2024-02-28T18:00:00Z"
            }
        ]
    }
    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)

    # songs 数据
    songs = {
        "songs": [
            {"song_id": "s001", "title": "奔跑", "artist": "羽泉", "album": "热爱", "duration": 243, "language": "中文", "genre": "流行", "style": "励志", "era": "2000s", "tags": ["跑步", "正能量"], "scene_tags": ["运动"], "crowd_tags": ["青春"]},
            {"song_id": "s002", "title": "夜曲", "artist": "周杰伦", "album": "11月的萧邦", "duration": 210, "language": "中文", "genre": "流行", "style": "抒情", "era": "2000s", "tags": ["夜晚", "安静"], "scene_tags": ["驾驶"], "crowd_tags": ["80后"]},
            {"song_id": "s003", "title": "平凡之路", "artist": "朴树", "album": "猎户星座", "duration": 265, "language": "中文", "genre": "民谣", "style": "治愈", "era": "2010s", "tags": ["旅程", "思考"], "scene_tags": ["驾驶"], "crowd_tags": ["90后"]},
            {"song_id": "s004", "title": "光年之外", "artist": "邓紫棋", "album": "光年之外", "duration": 230, "language": "中文", "genre": "流行", "style": "高音", "era": "2010s", "tags": ["浪漫", "星空"], "scene_tags": ["驾驶"], "crowd_tags": ["00后"]},
            {"song_id": "s005", "title": "梦醒时分", "artist": "陈淑桦", "album": "跟你说听你说", "duration": 248, "language": "中文", "genre": "流行", "style": "经典", "era": "1980s", "tags": ["失恋", "回忆"], "scene_tags": ["怀旧"], "crowd_tags": ["70后"]},
            {"song_id": "s006", "title": "Stay", "artist": "Rihanna", "album": "Unapologetic", "duration": 240, "language": "英文", "genre": "流行", "style": "抒情", "era": "2010s", "tags": ["安静", "夜晚"], "scene_tags": ["驾驶"], "crowd_tags": ["国际"]},
            {"song_id": "s007", "title": "新不了情", "artist": "万芳", "album": "新不了情", "duration": 245, "language": "中文", "genre": "流行", "style": "深情", "era": "1990s", "tags": ["爱情", "经典"], "scene_tags": ["怀旧"], "crowd_tags": ["70后"]},
            {"song_id": "s008", "title": "海阔天空", "artist": "Beyond", "album": "乐与怒", "duration": 295, "language": "中文", "genre": "摇滚", "style": "励志", "era": "1990s", "tags": ["自由", "梦想"], "scene_tags": ["怀旧"], "crowd_tags": ["70后"]},
            {"song_id": "s009", "title": "We Will Rock You", "artist": "Queen", "album": "News of the World", "duration": 182, "language": "英文", "genre": "摇滚", "style": "激昂", "era": "1970s", "tags": ["运动", "经典"], "scene_tags": ["运动"], "crowd_tags": ["全年龄"]}
        ]
    }
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

    # current_state.json
    current_state = {
        "playlist_id": "pl_002",
        "song_id": "s003"
    }
    with open("ops/current_state.json", "w", encoding="utf-8") as f:
        json.dump(current_state, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
