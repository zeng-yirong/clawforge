import os
import json
import shutil
import random

def build_env():
    # 确保工作目录干净
    for d in ['data', 'ops']:
        os.makedirs(d, exist_ok=True)
        # 清理残留
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if os.path.isfile(fp):
                os.remove(fp)
    ops_dir = 'ops'
    os.makedirs(ops_dir, exist_ok=True)

    # ===== 歌曲库 (songs.json) =====
    songs = [
        {"song_id": "S001", "title": "速度与激情", "artist": "A", "album": "X", "duration": 240, "language": "中文", "genre": "电子", "style": "嗨曲", "era": "2010s", "tags": ["赛车"], "scene_tags": ["驾驶"], "crowd_tags": ["车友"]},
        {"song_id": "S002", "title": "夜空中最亮的星", "artist": "B", "album": "Y", "duration": 300, "language": "中文", "genre": "民谣", "style": "安静", "era": "2000s", "tags": ["经典"], "scene_tags": ["夜晚"], "crowd_tags": ["80后"]},
        {"song_id": "S003", "title": "Hotel California", "artist": "Eagles", "album": "Z", "duration": 390, "language": "英文", "genre": "摇滚", "style": "经典", "era": "1970s", "tags": ["摇滚"], "scene_tags": ["旅行"], "crowd_tags": ["所有人"]},
        {"song_id": "S004", "title": "平凡之路", "artist": "C", "album": "W", "duration": 280, "language": "中文", "genre": "民谣", "style": "励志", "era": "2010s", "tags": ["青春"], "scene_tags": ["驾驶"], "crowd_tags": ["90后"]},
        # 故意增加一个冗余但存在的ID，用于干扰
        {"song_id": "S005", "title": "晴天", "artist": "D", "album": "V", "duration": 260, "language": "中文", "genre": "流行", "style": "校园", "era": "2000s", "tags": ["怀旧"], "scene_tags": ["回忆"], "crowd_tags": ["80后"]},
    ]
    song_ids_valid = {s["song_id"] for s in songs}

    # 写入歌曲库
    songs_dict = {"songs": songs}
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump(songs_dict, f, ensure_ascii=False, indent=2)

    # ===== 歌单列表 (playlists.json) =====
    playlists = [
        {
            "playlist_id": "PL001",
            "name": "嗨曲串烧",
            "description": "运动健身嗨曲",
            "song_ids": ["S001", "S002", "S003"],
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-02T10:00:00"
        },
        {
            "playlist_id": "PL002",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["S002", "S004", "S999", "S000"],  # S999和S000是幽灵曲目
            "created_at": "2024-01-03T20:00:00",
            "updated_at": "2024-01-04T20:00:00"
        },
        {
            "playlist_id": "PL003",
            "name": "怀旧金曲",
            "description": "80后90后回忆杀",
            "song_ids": ["S005", "S003", "S001", "S005"],  # 重复S005，但有效；无幽灵
            "created_at": "2024-02-01T08:00:00",
            "updated_at": "2024-02-02T08:00:00"
        },
        {
            "playlist_id": "PL004",
            "name": "我的收藏",
            "description": "我最喜欢的歌曲",
            "song_ids": ["S001", "S777"],  # S777是幽灵曲目
            "created_at": "2024-03-01T12:00:00",
            "updated_at": "2024-03-02T12:00:00"
        },
        {
            "playlist_id": "PL005",
            "name": "速度与激情",
            "description": "赛车电影主题曲",
            "song_ids": ["S001", "S002", "S003", "S004", "S005"],  # 全部有效
            "created_at": "2024-04-01T18:00:00",
            "updated_at": "2024-04-02T18:00:00"
        }
    ]

    # 写入歌单
    playlists_dict = {"playlists": playlists}
    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump(playlists_dict, f, ensure_ascii=False, indent=2)

    # ===== 标签定义 (tag_definitions.json) 可选干扰 =====
    tag_defs = [
        {"tag": "赛车", "description": "与赛车相关的歌曲"},
        {"tag": "经典", "description": "经典歌曲"},
        {"tag": "摇滚", "description": "摇滚风格"},
    ]
    with open("data/tags/tag_definitions.json", "w", encoding="utf-8") as f:
        json.dump({"tag_definitions": tag_defs}, f, ensure_ascii=False, indent=2)

    # ===== 额外干扰文件 =====
    # 旧版本歌单（过期，但仍需处理？提示中只说了data/playlists/下的文件，但这里放一个备份目录干扰）
    old_dir = "data/old_backups"
    os.makedirs(old_dir, exist_ok=True)
    old_playlists = [
        {"playlist_id": "PL_OLD", "name": "old", "song_ids": ["S001", "S999"]}
    ]
    with open(os.path.join(old_dir, "playlists_old.json"), "w", encoding="utf-8") as f:
        json.dump(old_playlists, f, ensure_ascii=False, indent=2)
    # 一个无关的日志文件
    with open("system.log", "w") as f:
        f.write("error: song S999 not found\n")

    print("环境构建完成。")

if __name__ == "__main__":
    build_env()
