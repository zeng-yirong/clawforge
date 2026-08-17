import json, os, shutil

def build_env():
    # 清理旧目录（如有）
    for d in ['data', 'ops', 'archive']:
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs('data/playlists')
    os.makedirs('data/songs')
    os.makedirs('data/tags')
    os.makedirs('archive')

    # 歌曲数据（含脏数据——song_010 duration=null）
    songs = [
        {"song_id": "song_001", "title": "觉醒", "artist": "汪峰", "album": "生来彷徨", "duration": 240, "language": "中文", "genre": "摇滚", "style": "励志", "era": "2010s", "tags": ["摇滚", "励志"], "scene_tags": ["飙车"], "crowd_tags": ["年轻人"]},
        {"song_id": "song_002", "title": "Break Free", "artist": "Ariana Grande", "album": "My Everything", "duration": 220, "language": "英文", "genre": "流行", "style": "舞曲", "era": "2010s", "tags": ["流行", "舞曲"], "scene_tags": ["派对"], "crowd_tags": ["大众"]},
        {"song_id": "song_003", "title": "平凡之路", "artist": "朴树", "album": "猎户星座", "duration": 185, "language": "中文", "genre": "民谣", "style": "安静", "era": "2010s", "tags": ["民谣", "安静"], "scene_tags": ["旅行"], "crowd_tags": ["文艺"]},
        {"song_id": "song_004", "title": "Fade", "artist": "Alan Walker", "album": "Fade", "duration": 210, "language": "英文", "genre": "电子", "style": "电子", "era": "2010s", "tags": ["电子", "动感"], "scene_tags": ["夜店"], "crowd_tags": ["年轻人"]},
        {"song_id": "song_005", "title": "追梦赤子心", "artist": "GALA", "album": "追梦赤子心", "duration": 260, "language": "中文", "genre": "摇滚", "style": "热血", "era": "2010s", "tags": ["摇滚", "热血"], "scene_tags": ["运动"], "crowd_tags": ["学生"]},
        {"song_id": "song_006", "title": "See You Again", "artist": "Wiz Khalifa", "album": "Furious 7", "duration": 230, "language": "英文", "genre": "说唱", "style": "抒情", "era": "2010s", "tags": ["说唱", "电影"], "scene_tags": ["纪念"], "crowd_tags": ["粉丝"]},
        {"song_id": "song_007", "title": "海阔天空", "artist": "Beyond", "album": "乐与怒", "duration": 320, "language": "中文", "genre": "摇滚", "style": "经典", "era": "1990s", "tags": ["摇滚", "经典"], "scene_tags": ["励志"], "crowd_tags": ["怀旧"]},
        {"song_id": "song_008", "title": "Stairway to Heaven", "artist": "Led Zeppelin", "album": "Led Zeppelin IV", "duration": 480, "language": "英文", "genre": "摇滚", "style": "史诗", "era": "1970s", "tags": ["摇滚", "经典"], "scene_tags": ["现场"], "crowd_tags": ["乐迷"]},
        {"song_id": "song_009", "title": "逆战", "artist": "张杰", "album": "逆战", "duration": 200, "language": "中文", "genre": "流行", "style": "励志", "era": "2010s", "tags": ["流行", "励志"], "scene_tags": ["运动"], "crowd_tags": ["年轻人"]},
        {"song_id": "song_010", "title": "无敌", "artist": "邓超", "album": "无敌", "duration": None, "language": "中文", "genre": "流行", "style": "搞笑", "era": "2010s", "tags": ["流行", "搞笑"], "scene_tags": ["喜剧"], "crowd_tags": ["大众"]}
    ]
    with open('data/songs/songs.json', 'w') as f:
        json.dump({"songs": songs}, f, indent=2, ensure_ascii=False)

    # 播放列表数据
    playlists = [
        {"playlist_id": "playlist_01", "name": "嗨曲串烧", "description": "运动健身嗨曲", "song_ids": ["song_005", "song_009"], "created_at": "2024-01-01", "updated_at": "2024-06-01"},
        {"playlist_id": "playlist_02", "name": "夜驾驶", "description": "夜晚开车听的歌", "song_ids": ["song_001", "song_004", "song_006", "song_010"], "created_at": "2024-02-01", "updated_at": "2024-06-01"},
        {"playlist_id": "playlist_03", "name": "怀旧金曲", "description": "80后90后回忆杀", "song_ids": ["song_003", "song_007", "song_008"], "created_at": "2024-03-01", "updated_at": "2024-06-01"},
        {"playlist_id": "playlist_04", "name": "速度与激情", "description": "赛车电影主题曲", "song_ids": ["song_001", "song_002", "song_003", "song_005", "song_007", "song_009", "song_010"], "created_at": "2024-04-01", "updated_at": "2024-06-01"},
        {"playlist_id": "playlist_05", "name": "我的收藏", "description": "我最喜欢的歌曲", "song_ids": ["song_001", "song_005", "song_009"], "created_at": "2024-05-01", "updated_at": "2024-06-01"}
    ]
    with open('data/playlists/playlists.json', 'w') as f:
        json.dump({"playlists": playlists}, f, indent=2, ensure_ascii=False)

    # 标签定义（干扰项）
    tags = [
        {"tag": "摇滚", "description": "摇滚风格"},
        {"tag": "经典", "description": "经典老歌"},
        {"tag": "励志", "description": "激励人心的歌曲"}
    ]
    with open('data/tags/tag_definitions.json', 'w') as f:
        json.dump({"tag_definitions": tags}, f, indent=2, ensure_ascii=False)

    # 额外干扰文件
    # 旧版歌曲（不完整）
    old_songs = [{"song_id": "song_old001", "title": "老歌"}]
    with open('archive/old_songs.json', 'w') as f:
        json.dump(old_songs, f)

    # 无用csv
    with open('archive/notes.txt', 'w') as f:
        f.write("仅供内部参考\n")

if __name__ == "__main__":
    build_env()
