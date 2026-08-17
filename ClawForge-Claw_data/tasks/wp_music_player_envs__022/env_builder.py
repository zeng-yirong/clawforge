import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 歌曲数据 (包含干扰项: 无效时长、无关歌曲)
    songs = {
        "songs": [
            {
                "song_id": "s001",
                "title": "引擎轰鸣",
                "artist": "未知",
                "album": "赛车之夜",
                "duration": 210,
                "language": "中文",
                "genre": "摇滚",
                "style": "硬核",
                "era": "2010s",
                "tags": ["赛车", "速度"],
                "scene_tags": ["赛车", "竞速"],
                "crowd_tags": ["车迷"]
            },
            {
                "song_id": "s002",
                "title": "急速狂飙",
                "artist": "J.D.",
                "album": "速度与激情",
                "duration": 195,
                "language": "中文",
                "genre": "摇滚",
                "style": "重金属",
                "era": "2010s",
                "tags": ["赛车"],
                "scene_tags": ["赛车", "竞速"],
                "crowd_tags": ["车迷"]
            },
            {
                "song_id": "s003",
                "title": "午夜飞驰",
                "artist": "DJ Night",
                "album": "夜行",
                "duration": 240,
                "language": "中文",
                "genre": "电子",
                "style": "迷幻",
                "era": "2000s",
                "tags": ["夜晚", "驾驶"],
                "scene_tags": ["夜晚", "驾驶"],
                "crowd_tags": ["夜猫"]
            },
            {
                "song_id": "s004",
                "title": "引擎咆哮",
                "artist": "重金属乐队",
                "album": "飙车",
                "duration": 0,
                "language": "中文",
                "genre": "摇滚",
                "style": "硬核",
                "era": "2010s",
                "tags": ["赛车"],
                "scene_tags": ["赛车"],
                "crowd_tags": ["车迷"]
            },
            {
                "song_id": "s005",
                "title": "超速行驶",
                "artist": "X",
                "album": "危险驾驶",
                "duration": -5,
                "language": "中文",
                "genre": "电子",
                "style": "快节奏",
                "era": "2010s",
                "tags": ["赛车"],
                "scene_tags": ["赛车"],
                "crowd_tags": ["车迷"]
            },
            {
                "song_id": "s006",
                "title": "街头竞速",
                "artist": "Y",
                "album": "地下赛车",
                "duration": 180,
                "language": "中文",
                "genre": "摇滚",
                "style": "朋克",
                "era": "2010s",
                "tags": ["赛车", "竞速"],
                "scene_tags": ["赛车", "竞速"],
                "crowd_tags": ["车迷"]
            },
            {
                "song_id": "s007",
                "title": "休闲驾驶",
                "artist": "Z",
                "album": "旅行",
                "duration": 200,
                "language": "中文",
                "genre": "民谣",
                "style": "舒缓",
                "era": "2000s",
                "tags": ["休闲"],
                "scene_tags": ["休闲", "驾驶"],
                "crowd_tags": ["家庭"]
            }
        ]
    }

    # 播放列表 (包含重复ID和无效歌曲ID)
    playlists = {
        "playlists": [
            {
                "playlist_id": "pl_speed_fury",
                "name": "速度与激情",
                "description": "赛车电影主题曲",
                "song_ids": ["s001", "s002", "s001", "s004", "s005", "s006"],
                "created_at": "2025-01-01T10:00:00",
                "updated_at": "2025-01-10T15:30:00"
            },
            {
                "playlist_id": "pl_night_drive",
                "name": "夜间驾驶",
                "description": "夜晚开车听的歌",
                "song_ids": ["s003", "s007"],
                "created_at": "2025-01-02T08:00:00",
                "updated_at": "2025-01-05T12:00:00"
            }
        ]
    }

    # 标签定义（干扰项，不参与主要逻辑）
    tag_definitions = {
        "tag_definitions": [
            {"tag": "赛车", "description": "与赛车运动相关"},
            {"tag": "竞速", "description": "竞速类音乐"},
            {"tag": "驾驶", "description": "驾驶场景音乐"},
            {"tag": "夜晚", "description": "适合夜晚聆听"}
        ]
    }

    # 写入文件
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)

    with open("data/tags/tag_definitions.json", "w", encoding="utf-8") as f:
        json.dump(tag_definitions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
