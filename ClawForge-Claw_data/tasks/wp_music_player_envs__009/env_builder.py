import os
import json
import datetime
import random

def build_env():
    # 数据根目录
    data_dir = "data"
    songs_dir = os.path.join(data_dir, "songs")
    playlists_dir = os.path.join(data_dir, "playlists")
    tags_dir = os.path.join(data_dir, "tags")

    # 创建目录
    os.makedirs(songs_dir, exist_ok=True)
    os.makedirs(playlists_dir, exist_ok=True)
    os.makedirs(tags_dir, exist_ok=True)

    # 干扰文件：临时备份
    with open("backup_songs_old.json", "w") as f:
        f.write('{"songs": []}')

    # 生成歌曲数据 (20首，其中10首英文，10首中文)
    songs = []
    artists = ["Adele", "Ed Sheeran", "Taylor Swift", "Coldplay", "Eminem", "周杰伦", "林俊杰", "邓紫棋", "薛之谦", "李荣浩"]
    titles_en = ["Hello", "Shape of You", "Shake It Off", "Fix You", "Lose Yourself", "Rolling in the Deep", "Photograph", "Blank Space", "Viva la Vida", "The Real Slim Shady"]
    titles_cn = ["七里香", "江南", "泡沫", "丑八怪", "年少有为", "青花瓷", "小酒窝", "光年之外", "你还要我怎样", "成都"]
    durations = [180, 200, 220, 240, 260, 280, 300, 320, 340, 360]
    for i in range(10):
        song = {
            "song_id": f"S{100 + i:03d}",
            "title": titles_en[i],
            "artist": artists[i],
            "album": f"Album {chr(65+i)}",
            "duration": durations[i] + random.randint(0, 10),
            "language": "英文",
            "genre": random.choice(["摇滚", "民谣", "流行", "电子"]),
            "style": random.choice(["激昂", "舒缓", "动感", "伤感"]),
            "era": random.choice(["1970s", "1980s", "2000s", "2010s"]),
            "tags": ["road", "energy"],
            "scene_tags": ["night", "drive"],
            "crowd_tags": ["adult"]
        }
        songs.append(song)
    for i in range(10):
        song = {
            "song_id": f"S{200 + i:03d}",
            "title": titles_cn[i],
            "artist": artists[i],
            "album": f"Album {chr(75+i)}",
            "duration": durations[i] + random.randint(0, 10),
            "language": "中文",
            "genre": random.choice(["摇滚", "民谣", "流行", "电子"]),
            "style": random.choice(["轻柔", "抒情", "快节奏", "怀旧"]),
            "era": random.choice(["1970s", "1980s", "2000s", "2010s"]),
            "tags": ["night", "calm"],
            "scene_tags": ["home", "study"],
            "crowd_tags": ["youth"]
        }
        songs.append(song)

    # 写入 songs.json，混合一些干扰字段（extra字段）
    with open(os.path.join(songs_dir, "songs.json"), "w") as f:
        # 添加一个额外字段干扰
        song_list = []
        for s in songs:
            s_copy = s.copy()
            s_copy["internal_note"] = "do not use"  # 干扰字段
            song_list.append(s_copy)
        json.dump({"songs": song_list}, f, indent=2)

    # 生成播放列表
    playlists = [
        {
            "playlist_id": "pl_night_drive_001",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": [s["song_id"] for s in songs if s["language"] == "英文"] + [s["song_id"] for s in songs if s["language"] == "中文"][:3],  # 5首英文+3首中文 = 8首
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        },
        {
            "playlist_id": "pl_retro_002",
            "name": "怀旧金曲",
            "description": "80后90后回忆杀",
            "song_ids": [s["song_id"] for s in songs[:5]],
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        },
        {
            "playlist_id": "pl_speed_003",
            "name": "速度与激情",
            "description": "赛车电影主题曲",
            "song_ids": [s["song_id"] for s in songs if s["genre"] == "电子"],
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
    ]

    # 写入播放列表
    with open(os.path.join(playlists_dir, "playlists.json"), "w") as f:
        json.dump({"playlists": playlists}, f, indent=2)

    # 生成标签定义（干扰项）
    tag_defs = [
        {"tag": "road", "description": "适合道路行驶"},
        {"tag": "energy", "description": "充满能量的曲目"},
        {"tag": "night", "description": "夜间场景"},
        {"tag": "calm", "description": "平静放松"}
    ]
    with open(os.path.join(tags_dir, "tag_definitions.json"), "w") as f:
        json.dump({"tag_definitions": tag_defs}, f, indent=2)

    # 额外干扰：一个旧版本歌曲文件
    with open(os.path.join(songs_dir, "songs_backup_2024.json"), "w") as f:
        json.dump({"songs": []}, f, indent=2)

    # 干扰：一个readme.txt
    with open("readme.txt", "w") as f:
        f.write("This is a car music system data dump. Do not modify original files.")

    # 生成一个混合了脏数据的CSV文件（无关干扰）
    with open("parking_log.csv", "w") as f:
        f.write("date,spot,car_id\n2025-03-01,A12,ABC123\n2025-03-01,B45,DEF456")

if __name__ == "__main__":
    build_env()
