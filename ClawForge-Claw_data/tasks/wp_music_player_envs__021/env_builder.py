import os
import json
import shutil

def build_env():
    # 创建目录结构
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 歌曲数据（10首）
    songs = [
        {"song_id": "S001", "title": "夜曲", "artist": "周杰伦", "album": "十一月的萧邦", "duration": 200, "language": "中文", "genre": "流行", "style": "抒情", "era": "2000s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S002", "title": "Hotel California", "artist": "Eagles", "album": "Hotel California", "duration": 390, "language": "英文", "genre": "摇滚", "style": "经典", "era": "1970s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S003", "title": "晴天", "artist": "周杰伦", "album": "叶惠美", "duration": 240, "language": "中文", "genre": "流行", "style": "校园", "era": "2000s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S004", "title": "Back in Black", "artist": "AC/DC", "album": "Back in Black", "duration": 255, "language": "英文", "genre": "摇滚", "style": "硬摇滚", "era": "1980s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S005", "title": "七里香", "artist": "周杰伦", "album": "七里香", "duration": 280, "language": "中文", "genre": "流行", "style": "民谣", "era": "2000s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S006", "title": "Stairway to Heaven", "artist": "Led Zeppelin", "album": "Led Zeppelin IV", "duration": 482, "language": "英文", "genre": "摇滚", "style": "经典", "era": "1970s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S007", "title": "稻香", "artist": "周杰伦", "album": "魔杰座", "duration": 210, "language": "中文", "genre": "流行", "style": "田园", "era": "2000s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S008", "title": "Yesterday", "artist": "The Beatles", "album": "Help!", "duration": 125, "language": "英文", "genre": "流行", "style": "经典", "era": "1960s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S009", "title": "告白气球", "artist": "周杰伦", "album": "周杰伦的床边故事", "duration": 220, "language": "中文", "genre": "流行", "style": "浪漫", "era": "2010s", "tags": [], "scene_tags": [], "crowd_tags": []},
        {"song_id": "S010", "title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "duration": 354, "language": "英文", "genre": "摇滚", "style": "前卫", "era": "1970s", "tags": [], "scene_tags": [], "crowd_tags": []},
    ]
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump({"songs": songs}, f, ensure_ascii=False, indent=2)

    # 播放列表（包含干扰项）
    playlists = [
        {
            "playlist_id": "night_drive",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008", "S009", "S010"],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-06-01T00:00:00"
        },
        {
            "playlist_id": "golden_oldies",
            "name": "怀旧金曲",
            "description": "80后90后回忆杀",
            "song_ids": ["S002", "S004", "S006", "S008", "S010"],
            "created_at": "2023-02-01T00:00:00",
            "updated_at": "2023-05-15T00:00:00"
        },
        {
            "playlist_id": "speed_fury",
            "name": "速度与激情",
            "description": "赛车电影主题曲",
            "song_ids": ["S002", "S004", "S006"],
            "created_at": "2023-03-01T00:00:00",
            "updated_at": "2023-04-20T00:00:00"
        }
    ]
    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump({"playlists": playlists}, f, ensure_ascii=False, indent=2)

    # 规则文件（三个版本，只有v3是当前生效）
    rules_v1 = {"field": "language", "operator": "eq", "value": "英文"}
    rules_v2 = {"field": "genre", "operator": "eq", "value": "摇滚"}
    rules_v3 = {"field": "language", "operator": "eq", "value": "中文"}

    with open("data/rules/rules_v1.json", "w", encoding="utf-8") as f:
        json.dump(rules_v1, f, indent=2)
    with open("data/rules/rules_v2.json", "w", encoding="utf-8") as f:
        json.dump(rules_v2, f, indent=2)
    with open("data/rules/rules_v3.json", "w", encoding="utf-8") as f:
        json.dump(rules_v3, f, indent=2)

    # 配置：指定当前生效的规则
    active_rule = {"active_rule_path": "data/rules/rules_v3.json"}
    with open("config/active_rule.json", "w", encoding="utf-8") as f:
        json.dump(active_rule, f, indent=2)

    # 干扰文件：备份旧规则
    os.makedirs("backup", exist_ok=True)
    with open("backup/rules_backup.json", "w", encoding="utf-8") as f:
        json.dump({"field": "era", "operator": "eq", "value": "1970s"}, f, indent=2)

    # 多余的空目录
    os.makedirs("tmp", exist_ok=True)

if __name__ == "__main__":
    build_env()
