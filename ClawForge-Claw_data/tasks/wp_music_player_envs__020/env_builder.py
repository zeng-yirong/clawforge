import os
import json

def build_env():
    # Ensure output directory exists but is empty
    os.makedirs("output", exist_ok=True)
    # Create data directories
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)

    # Playlists
    playlists = [
        {
            "playlist_id": "speed_and_fury",
            "name": "速度与激情",
            "description": "赛车电影主题曲",
            "song_ids": ["s001", "s002", "s003", "s004", "s005", "s006", "s007"],
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-03-15T14:30:00Z"
        },
        {
            "playlist_id": "night_drive",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["s008", "s009", "s010", "s011"],
            "created_at": "2024-02-10T08:00:00Z",
            "updated_at": "2024-02-10T08:00:00Z"
        },
        {
            "playlist_id": "my_favorites",
            "name": "我的收藏",
            "description": "我最喜欢的歌曲",
            "song_ids": ["s001", "s012", "s013", "s014"],
            "created_at": "2024-01-20T12:00:00Z",
            "updated_at": "2024-04-01T09:00:00Z"
        }
    ]
    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump({"playlists": playlists}, f, ensure_ascii=False, indent=2)

    # Songs with deliberate data quality issues
    songs = [
        {"song_id": "s001", "title": "Ride the Lightning", "artist": "Metallica", "album": "Ride the Lightning", "duration": 398, "language": "英文", "genre": "摇滚", "style": "重金属", "era": "1980s", "tags": ["经典", "重金属"], "scene_tags": ["驾驶"], "crowd_tags": ["成人"]},
        {"song_id": "s002", "title": "Highway Star", "artist": "Deep Purple", "album": "Machine Head", "duration": 372, "language": "英文", "genre": "摇滚", "style": "硬摇滚", "era": "1970s", "tags": ["经典"], "scene_tags": ["驾驶", "激情"], "crowd_tags": ["成人"]},
        {"song_id": "s003", "title": "追梦赤子心", "artist": "GALA", "album": "追梦痴子心", "duration": 254, "language": "中文", "genre": "摇滚", "style": "流行摇滚", "era": "2010s", "tags": ["励志", "中文"], "scene_tags": ["运动"], "crowd_tags": ["青年"]},
        {"song_id": "s004", "title": "Numb", "artist": "Linkin Park", "album": "Meteora", "duration": 187, "language": "英文", "genre": "摇滚", "style": "新金属", "era": "2000s", "tags": ["经典", "摇滚"], "scene_tags": ["驾驶", "运动"], "crowd_tags": ["青年", "成人"]},
        # Missing language field (should be excluded or handled)
        {"song_id": "s005", "title": "Eye of the Tiger", "artist": "Survivor", "album": "Eye of the Tiger", "duration": 244, "language": "English", "genre": "摇滚", "style": "硬摇滚", "era": "1980s", "tags": ["经典", "电影"], "scene_tags": ["运动", "驾驶"], "crowd_tags": ["成人"]},
        # Language is "English" (non-standard) – agent should treat as invalid
        {"song_id": "s006", "title": "Born to Be Wild", "artist": "Steppenwolf", "album": "Steppenwolf", "duration": 209, "language": "英文", "genre": "摇滚", "style": "硬摇滚", "era": "1970s", "tags": ["经典", "电影"], "scene_tags": ["驾驶", "公路"], "crowd_tags": ["成人"]},
        # Valid English
        {"song_id": "s007", "title": "Speed Demon", "artist": "Michael Jackson", "album": "Bad", "duration": 322, "language": "英文", "genre": "流行", "style": "流行舞曲", "era": "1980s", "tags": ["流行", "舞曲"], "scene_tags": ["驾驶"], "crowd_tags": ["青年"]},
        # Valid English – this song is in "夜驾驶" but not in target playlist
        {"song_id": "s008", "title": "Hotel California", "artist": "Eagles", "album": "Hotel California", "duration": 391, "language": "英文", "genre": "摇滚", "style": "软摇滚", "era": "1970s", "tags": ["经典", "乡村"], "scene_tags": ["夜晚", "驾驶"], "crowd_tags": ["成人"]},
        # 中文歌（distractor）
        {"song_id": "s009", "title": "平凡之路", "artist": "朴树", "album": "猎户星座", "duration": 235, "language": "中文", "genre": "民谣", "style": "独立", "era": "2010s", "tags": ["中文", "电影"], "scene_tags": ["旅行"], "crowd_tags": ["青年"]},
        # 缺失 song_id? 不，我们还需要 s010 s011 等
        {"song_id": "s010", "title": "Take Me Home, Country Roads", "artist": "John Denver", "album": "Poems, Prayers & Promises", "duration": 187, "language": "英文", "genre": "民谣", "style": "乡村", "era": "1970s", "tags": ["经典", "乡村"], "scene_tags": ["旅行"], "crowd_tags": ["家庭"]},
        # 英文歌但不属于任何播放列表
        {"song_id": "s011", "title": "Purple Rain", "artist": "Prince", "album": "Purple Rain", "duration": 511, "language": "英文", "genre": "流行", "style": "放克摇滚", "era": "1980s", "tags": ["经典", "电影"], "scene_tags": ["夜晚"], "crowd_tags": ["成人"]},
        # 用于"我的收藏"的歌曲
        {"song_id": "s012", "title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "duration": 355, "language": "英文", "genre": "摇滚", "style": "前卫摇滚", "era": "1970s", "tags": ["经典", "艺术"], "scene_tags": ["独处"], "crowd_tags": ["所有"]},
        # 中文歌干扰
        {"song_id": "s013", "title": "夜空中最亮的星", "artist": "逃跑计划", "album": "世界", "duration": 287, "language": "中文", "genre": "流行", "style": "独立", "era": "2010s", "tags": ["中文", "励志"], "scene_tags": ["夜晚", "驾驶"], "crowd_tags": ["青年"]},
        # 重复的 song_id 测试？不，唯一
        {"song_id": "s014", "title": "Counting Stars", "artist": "OneRepublic", "album": "Native", "duration": 257, "language": "英文", "genre": "流行", "style": "流行摇滚", "era": "2010s", "tags": ["流行", "舞曲"], "scene_tags": ["驾驶", "运动"], "crowd_tags": ["青年"]}
    ]
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump({"songs": songs}, f, ensure_ascii=False, indent=2)

    # Tags (decoy)
    tags = [
        {"tag": "经典", "description": "经典老歌"},
        {"tag": "驾驶", "description": "适合驾驶时听的歌"},
        {"tag": "英文", "description": "英语歌曲"}
    ]
    with open("data/tags/tag_definitions.json", "w", encoding="utf-8") as f:
        json.dump({"tag_definitions": tags}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
