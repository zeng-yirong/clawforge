import os
import json
import datetime

def build_env():
    # 创建目录结构
    dirs = ["data/playlists", "data/songs", "session", "ops", "data/backup", "data/tags"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 创建干扰的空文件
    open("data/backup/songs_old.json", "w").close()
    open("data/backup/playlists_bak.json", "w").close()

    # 创建 tags 定义（无用但存在）
    tag_defs = {"tag_definitions": [
        {"tag": "night_drive", "description": "适合夜间驾驶"},
        {"tag": "chill", "description": "放松"},
        {"tag": "electronic", "description": "电子"}
    ]}
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tag_defs, f, ensure_ascii=False)

    # 创建歌曲库
    songs_data = {"songs": [
        {"song_id": "song_001", "title": "速度与激情", "artist": "张伟", "album": "嗨曲", "duration": 240, "language": "中文", "genre": "摇滚", "style": "激昂", "era": "2000s", "tags": ["car", "fast"], "scene_tags": ["highway"], "crowd_tags": ["driver"]},
        {"song_id": "song_002", "title": "夜曲", "artist": "周杰伦", "album": "十一月的萧邦", "duration": 213, "language": "中文", "genre": "流行", "style": "忧郁", "era": "2000s", "tags": ["night", "rain"], "scene_tags": ["city"], "crowd_tags": ["youth"]},
        {"song_id": "song_003", "title": "Bad Guy", "artist": "Billie Eilish", "album": "When We All Fall Asleep", "duration": 194, "language": "英文", "genre": "电子", "style": "暗黑", "era": "2010s", "tags": ["dark", "bass"], "scene_tags": ["party"], "crowd_tags": ["teen"]},
        {"song_id": "song_004", "title": "引擎启动", "artist": "王磊", "album": "驾行", "duration": 220, "language": "中文", "genre": "电子", "style": "动感", "era": "2010s", "tags": ["driving", "fast"], "scene_tags": ["track"], "crowd_tags": ["racer"]},
        {"song_id": "song_005", "title": "City Lights", "artist": "DJ Snake", "album": "Encore", "duration": 207, "language": "英文", "genre": "电子", "style": "迷幻", "era": "2010s", "tags": ["night", "lights"], "scene_tags": ["city"], "crowd_tags": ["night_owl"]},
        {"song_id": "song_006", "title": "午夜骑士", "artist": "刘一", "album": "夜行", "duration": 198, "language": "中文", "genre": "摇滚", "style": "激昂", "era": "1980s", "tags": ["motorcycle", "night"], "scene_tags": ["highway"], "crowd_tags": ["biker"]},
        {"song_id": "song_007", "title": "Neon", "artist": "John Legend", "album": "Love in the Future", "duration": 235, "language": "英文", "genre": "流行", "style": "浪漫", "era": "2010s", "tags": ["night", "romance"], "scene_tags": ["city"], "crowd_tags": ["couple"]},
        {"song_id": "song_008", "title": "漂移", "artist": "林峰", "album": "极速", "duration": 215, "language": "中文", "genre": "电子", "style": "刺激", "era": "2000s", "tags": ["drift", "fast"], "scene_tags": ["track"], "crowd_tags": ["racer"]},
        {"song_id": "song_009", "title": "After Hours", "artist": "The Weeknd", "album": "After Hours", "duration": 300, "language": "英文", "genre": "电子", "style": "迷幻", "era": "2020s", "tags": ["night", "party"], "scene_tags": ["club"], "crowd_tags": ["party_animal"]},
        {"song_id": "song_010", "title": "归途", "artist": "赵雷", "album": "吉姆餐厅", "duration": 267, "language": "中文", "genre": "民谣", "style": "抒情", "era": "2010s", "tags": ["home", "night"], "scene_tags": ["highway"], "crowd_tags": ["commuter"]}
    ]}
    with open("data/songs/songs.json", "w") as f:
        json.dump(songs_data, f, ensure_ascii=False, indent=2)

    # 创建播放列表（包含脏数据）
    playlists_data = {"playlists": [
        {
            "playlist_id": "pl_hi_qu",
            "name": "嗨曲串烧",
            "description": "运动健身嗨曲",
            "song_ids": ["song_001", "song_002", "song_003"],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-15T00:00:00"
        },
        {
            "playlist_id": "pl_night_drive",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": [
                "song_004",
                "song_005",
                "song_006",
                "song_invalid",    # 无效ID（不存在于songs.json）
                "song_007",
                "song_008",
                "song_004",        # 重复ID（与 song_004 重复）
                "song_009",
                "song_010"
            ],
            "created_at": "2024-02-10T00:00:00",
            "updated_at": "2024-03-01T00:00:00"
        }
    ]}
    with open("data/playlists/playlists.json", "w") as f:
        json.dump(playlists_data, f, ensure_ascii=False, indent=2)

    # 创建 session 摘要
    session_summary = {
        "session_id": "sess_014",
        "playlist_id": "pl_night_drive",
        "current_song_id": "song_006",
        "played_songs": ["song_004", "song_005", "song_006"],
        "last_updated": datetime.datetime.now().isoformat()
    }
    with open("session/summary.json", "w") as f:
        json.dump(session_summary, f, ensure_ascii=False, indent=2)

    # 创建一些干扰文件（空 log）
    with open("data/backup/old_session.json", "w") as f:
        f.write('{"playlist_id":"pl_hi_qu","current_song":"song_001"}')

if __name__ == "__main__":
    build_env()
