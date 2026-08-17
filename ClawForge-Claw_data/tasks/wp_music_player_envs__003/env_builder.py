import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    # 注意：ops/ 留给 agent 创建，我们不预创建

    # 播放列表（包含干扰项和诱饵）
    playlists = [
        {
            "playlist_id": "pl001",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["s001", "s002", "s001", "s003", "s999"],
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        },
        {
            "playlist_id": "pl002",
            "name": "嗨曲串烧",
            "description": "运动健身嗨曲",
            "song_ids": ["s004", "s005"],
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        },
        {
            "playlist_id": "pl003",
            "name": "怀旧金曲",
            "description": "80后90后回忆杀",
            "song_ids": ["s006", "s007"],
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        },
        {
            "playlist_id": "pl004",
            "name": "午夜飙车",   # 干扰项：名字相似但不同
            "description": "赛车电影主题曲",
            "song_ids": ["s008", "s009", "s999"],
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    ]
    with open("data/playlists/playlists.json", "w") as f:
        json.dump({"playlists": playlists}, f, indent=2)

    # 歌曲库（包含有效歌曲和干扰歌曲）
    songs = [
        {
            "song_id": "s001",
            "title": "夜曲",
            "artist": "周杰伦",
            "album": "11月的萧邦",
            "duration": 240,
            "language": "中文",
            "genre": "流行",
            "style": "抒情",
            "era": "2000s",
            "tags": ["经典"],
            "scene_tags": ["夜晚"],
            "crowd_tags": ["年轻人"]
        },
        {
            "song_id": "s002",
            "title": "Shut Up and Dance",
            "artist": "Walk the Moon",
            "album": "Talking Is Hard",
            "duration": 210,
            "language": "英文",
            "genre": "摇滚",
            "style": "动感",
            "era": "2010s",
            "tags": ["派对"],
            "scene_tags": ["开车"],
            "crowd_tags": ["年轻人"]
        },
        {
            "song_id": "s003",
            "title": "平凡之路",
            "artist": "朴树",
            "album": "猎户星座",
            "duration": 300,
            "language": "中文",
            "genre": "民谣",
            "style": "清新",
            "era": "2010s",
            "tags": ["励志"],
            "scene_tags": ["公路"],
            "crowd_tags": ["所有人"]
        },
        {
            "song_id": "s004",
            "title": "Uptown Funk",
            "artist": "Mark Ronson ft. Bruno Mars",
            "album": "Uptown Special",
            "duration": 270,
            "language": "英文",
            "genre": "流行",
            "style": "放克",
            "era": "2010s",
            "tags": ["派对"],
            "scene_tags": ["运动"],
            "crowd_tags": ["年轻人"]
        },
        {
            "song_id": "s005",
            "title": "Sugar",
            "artist": "Maroon 5",
            "album": "V",
            "duration": 240,
            "language": "英文",
            "genre": "流行",
            "style": "流行摇滚",
            "era": "2010s",
            "tags": ["浪漫"],
            "scene_tags": ["约会"],
            "crowd_tags": ["情侣"]
        },
        {
            "song_id": "s006",
            "title": "光辉岁月",
            "artist": "Beyond",
            "album": "命运派对",
            "duration": 320,
            "language": "中文",
            "genre": "摇滚",
            "style": "经典",
            "era": "1990s",
            "tags": ["励志"],
            "scene_tags": ["怀旧"],
            "crowd_tags": ["所有人"]
        },
        {
            "song_id": "s007",
            "title": "海阔天空",
            "artist": "Beyond",
            "album": "乐与怒",
            "duration": 330,
            "language": "中文",
            "genre": "摇滚",
            "style": "经典",
            "era": "1990s",
            "tags": ["励志"],
            "scene_tags": ["怀旧"],
            "crowd_tags": ["所有人"]
        },
        {
            "song_id": "s008",
            "title": "Fast and Furious",
            "artist": "Various",
            "album": "The Fast and the Furious",
            "duration": 200,
            "language": "英文",
            "genre": "电子",
            "style": "舞曲",
            "era": "2000s",
            "tags": ["赛车"],
            "scene_tags": ["飙车"],
            "crowd_tags": ["车迷"]
        },
        {
            "song_id": "s009",
            "title": "Tokyo Drift",
            "artist": "Teriyaki Boyz",
            "album": "The Fast and the Furious: Tokyo Drift",
            "duration": 230,
            "language": "英文",
            "genre": "电子",
            "style": "嘻哈",
            "era": "2000s",
            "tags": ["赛车"],
            "scene_tags": ["飙车"],
            "crowd_tags": ["车迷"]
        }
    ]
    with open("data/songs/songs.json", "w") as f:
        json.dump({"songs": songs}, f, indent=2)

    # 标签定义（干扰项）
    tags = [
        {"tag": "经典", "description": "经久不衰的歌曲"},
        {"tag": "派对", "description": "适合派对的歌曲"},
        {"tag": "励志", "description": "鼓舞人心的歌曲"},
        {"tag": "赛车", "description": "与赛车相关的歌曲"}
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tags}, f, indent=2)

if __name__ == "__main__":
    build_env()
    print("Environment built successfully.")
