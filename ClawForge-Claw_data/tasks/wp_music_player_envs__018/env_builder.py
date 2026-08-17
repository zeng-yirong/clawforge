import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 创建歌曲数据（提供基础歌曲，可能部分不在播放列表中使用）
    songs = [
        {"song_id": "song_001", "title": "夜曲", "artist": "周杰伦", "album": "十一月的肖邦", "duration": 230, "language": "中文", "genre": "流行", "style": "抒情", "era": "2000s", "tags": ["经典"], "scene_tags": ["夜晚"], "crowd_tags": ["成年人"]},
        {"song_id": "song_002", "title": "漂移", "artist": "周杰伦", "album": "头文字D", "duration": 240, "language": "中文", "genre": "电子", "style": "动感", "era": "2000s", "tags": ["赛车"], "scene_tags": ["驾驶"], "crowd_tags": ["年轻人"]},
        {"song_id": "song_003", "title": "Glad You Came", "artist": "The Wanted", "album": "Battlefield", "duration": 210, "language": "英文", "genre": "流行", "style": "欢快", "era": "2010s", "tags": ["派对"], "scene_tags": ["聚会"], "crowd_tags": ["大众"]},
        {"song_id": "song_004", "title": "Life is a Highway", "artist": "Rascal Flatts", "album": "Cars", "duration": 260, "language": "英文", "genre": "摇滚", "style": "公路", "era": "2000s", "tags": ["电影"], "scene_tags": ["驾驶"], "crowd_tags": ["家庭"]},
        {"song_id": "song_005", "title": "Concerning Hobbits", "artist": "Howard Shore", "album": "The Lord of the Rings", "duration": 180, "language": "英文", "genre": "民谣", "style": "史诗", "era": "2000s", "tags": ["配乐"], "scene_tags": ["放松"], "crowd_tags": ["影迷"]},
        {"song_id": "song_006", "title": "千山万水", "artist": "周杰伦", "album": "2008奥运会", "duration": 200, "language": "中文", "genre": "流行", "style": "励志", "era": "2000s", "tags": ["奥运"], "scene_tags": ["运动"], "crowd_tags": ["运动员"]},
        {"song_id": "song_007", "title": "Danger Zone", "artist": "Kenny Loggins", "album": "Top Gun", "duration": 215, "language": "英文", "genre": "摇滚", "style": "激情", "era": "1980s", "tags": ["电影"], "scene_tags": ["驾驶"], "crowd_tags": ["飞行员"]},
    ]
    with open("data/songs/songs.json", "w") as f:
        json.dump({"songs": songs}, f, ensure_ascii=False, indent=2)

    # 创建播放列表数据（包含重复的歌曲ID）
    playlists = [
        {
            "playlist_id": "hi_qu_chuan_shao",
            "name": "嗨曲串烧",
            "description": "运动健身嗨曲",
            "song_ids": ["song_001", "song_002", "song_003"],
            "created_at": "2024-01-10 08:00:00",
            "updated_at": "2024-06-01 10:00:00"
        },
        {
            "playlist_id": "ye_jia_shi",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["song_001", "song_002", "song_001", "song_003"],  # 重复 song_001
            "created_at": "2024-02-15 12:00:00",
            "updated_at": "2024-05-20 15:00:00"
        },
        {
            "playlist_id": "huai_jiu_jin_qu",
            "name": "怀旧金曲",
            "description": "80后90后回忆杀",
            "song_ids": ["song_004", "song_005", "song_006"],
            "created_at": "2024-03-05 09:30:00",
            "updated_at": "2024-06-10 18:00:00"
        },
        {
            "playlist_id": "wo_de_shou_cang",
            "name": "我的收藏",
            "description": "我最喜欢的歌曲",
            "song_ids": ["song_005", "song_006", "song_005", "song_007"],  # 重复 song_005
            "created_at": "2024-04-20 16:00:00",
            "updated_at": "2024-07-01 20:00:00"
        },
        {
            "playlist_id": "su_du_yu_ji_qing",
            "name": "速度与激情",
            "description": "赛车电影主题曲",
            "song_ids": ["song_002", "song_004", "song_007"],
            "created_at": "2024-05-01 07:00:00",
            "updated_at": "2024-07-10 12:00:00"
        }
    ]
    with open("data/playlists/playlists.json", "w") as f:
        json.dump({"playlists": playlists}, f, ensure_ascii=False, indent=2)

    # 创建干扰数据——标签定义（正常，但agent不需要读）
    tag_defs = [
        {"tag": "经典", "description": "经过时间考验的歌曲"},
        {"tag": "赛车", "description": "与赛车相关的歌曲"},
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f, ensure_ascii=False, indent=2)

    # 创建干扰备份文件（旧版本播放列表，不同重复情况）
    backup_playlists = [
        {
            "playlist_id": "ye_jia_shi",
            "name": "夜驾驶",
            "song_ids": ["song_001", "song_002", "song_003"],  # 旧版无重复
        }
    ]
    with open("backups/playlists_backup_202402.json", "w") as f:
        json.dump({"playlists": backup_playlists}, f, ensure_ascii=False, indent=2)

    # 创建一些无关的日志文件
    with open("logs/info.log", "w") as f:
        f.write("2024-07-15 10:00:00 INFO Music service started\n")
    with open("logs/error.log", "w") as f:
        f.write("2024-07-15 10:05:00 ERROR Duplicate detection not implemented yet\n")

if __name__ == "__main__":
    build_env()
