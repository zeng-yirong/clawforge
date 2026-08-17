import os
import json
import random
import datetime

def build_env():
    # 创建目录
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 歌曲数据：共20首，中文+英文混合
    songs = [
        {"song_id": "S001", "title": "极速狂飙", "artist": "王炸", "album": "速度之魂", "duration": 215, "language": "中文", "genre": "摇滚", "style": "激情", "era": "2010s", "tags": ["赛车", "热血"], "scene_tags": ["驾驶"], "crowd_tags": ["年轻人"]},
        {"song_id": "S002", "title": "午夜霓虹", "artist": "李魅", "album": "夜行", "duration": 248, "language": "中文", "genre": "电子", "style": "迷幻", "era": "2010s", "tags": ["夜晚", "都市"], "scene_tags": ["夜晚驾驶"], "crowd_tags": ["夜猫子"]},
        {"song_id": "S003", "title": "怀旧列车", "artist": "赵时光", "album": "八零回忆", "duration": 302, "language": "中文", "genre": "民谣", "style": "抒情", "era": "1980s", "tags": ["怀旧", "老歌"], "scene_tags": ["回忆"], "crowd_tags": ["80后"]},
        {"song_id": "S004", "title": "漂移时刻", "artist": "速度侠", "album": "赛道传说", "duration": 195, "language": "中文", "genre": "摇滚", "style": "劲爆", "era": "2010s", "tags": ["漂移", "赛车"], "scene_tags": ["驾驶"], "crowd_tags": ["赛车爱好者"]},
        {"song_id": "S005", "title": "星空漫游", "artist": "张宇宙", "album": "星际旅行", "duration": 281, "language": "中文", "genre": "电子", "style": "空灵", "era": "2000s", "tags": ["星空", "放松"], "scene_tags": ["夜晚"], "crowd_tags": ["所有"]},
        {"song_id": "S006", "title": "Night Drive", "artist": "DJ Miles", "album": "Nocturne", "duration": 265, "language": "英文", "genre": "电子", "style": "Deep House", "era": "2010s", "tags": ["night", "drive"], "scene_tags": ["night driving"], "crowd_tags": ["young adult"]},
        {"song_id": "S007", "title": "Summer Breeze", "artist": "Ocean", "album": "Beach Vibes", "duration": 232, "language": "英文", "genre": "流行", "style": "轻松", "era": "2010s", "tags": ["summer", "breeze"], "scene_tags": ["daytime"], "crowd_tags": ["all"]},
        {"song_id": "S008", "title": "Firestorm", "artist": "Metal God", "album": "Inferno", "duration": 318, "language": "英文", "genre": "摇滚", "style": "Heavy", "era": "1970s", "tags": ["fire", "storm"], "scene_tags": ["workout"], "crowd_tags": ["athlete"]},
        {"song_id": "S009", "title": "黄昏漫步", "artist": "陈夕阳", "album": "暮色", "duration": 240, "language": "中文", "genre": "民谣", "style": "温暖", "era": "2010s", "tags": ["黄昏", "悠闲"], "scene_tags": ["休闲"], "crowd_tags": ["情侣"]},
        {"song_id": "S010", "title": "速度之翼", "artist": "闪电", "album": "极速", "duration": 207, "language": "中文", "genre": "摇滚", "style": "快节奏", "era": "2010s", "tags": ["速度", "激情"], "scene_tags": ["驾驶"], "crowd_tags": ["飙车族"]},
        {"song_id": "S011", "title": "Moonlight Sonata", "artist": "Luna", "album": "Classical", "duration": 420, "language": "英文", "genre": "流行", "style": "古典", "era": "1970s", "tags": ["moon", "classic"], "scene_tags": ["sleep"], "crowd_tags": ["senior"]},
        {"song_id": "S012", "title": "电音狂潮", "artist": "DJ 爆", "album": "夜店之王", "duration": 198, "language": "中文", "genre": "电子", "style": "重低音", "era": "2010s", "tags": ["电音", "嗨曲"], "scene_tags": ["派对"], "crowd_tags": ["年轻人"]},
        {"song_id": "S013", "title": "Desert Roar", "artist": "Dusty", "album": "Sandstorm", "duration": 290, "language": "英文", "genre": "摇滚", "style": "西部", "era": "2000s", "tags": ["desert", "roar"], "scene_tags": ["road trip"], "crowd_tags": ["adventurer"]},
        {"song_id": "S014", "title": "初恋的旋律", "artist": "甜甜", "album": "青涩", "duration": 215, "language": "中文", "genre": "流行", "style": "甜美", "era": "2010s", "tags": ["初恋", "回忆"], "scene_tags": ["约会"], "crowd_tags": ["学生"]},
        {"song_id": "S015", "title": "暴走引擎", "artist": "轰鸣", "album": "机械之音", "duration": 185, "language": "中文", "genre": "摇滚", "style": "金属", "era": "2010s", "tags": ["引擎", "金属"], "scene_tags": ["驾驶"], "crowd_tags": ["赛车爱好者"]},
        {"song_id": "S016", "title": "Fly Away", "artist": "Eagle", "album": "Sky", "duration": 255, "language": "英文", "genre": "流行", "style": "励志", "era": "2000s", "tags": ["fly", "freedom"], "scene_tags": ["早晨"], "crowd_tags": ["all"]},
        {"song_id": "S017", "title": "寂静之夜", "artist": "沉默者", "album": "深夜", "duration": 310, "language": "中文", "genre": "民谣", "style": "静谧", "era": "2000s", "tags": ["夜晚", "安静"], "scene_tags": ["睡前"], "crowd_tags": ["失眠者"]},
        {"song_id": "S018", "title": "Turbo Boost", "artist": "Racer", "album": "Afterburner", "duration": 220, "language": "英文", "genre": "电子", "style": "高能", "era": "2010s", "tags": ["turbo", "boost"], "scene_tags": ["加速"], "crowd_tags": ["赛车爱好者"]},
        {"song_id": "S019", "title": "蓝色忧郁", "artist": "蓝调", "album": "忧郁", "duration": 278, "language": "中文", "genre": "民谣", "style": "伤感", "era": "1980s", "tags": ["忧郁", "经典"], "scene_tags": ["雨天"], "crowd_tags": ["文艺青年"]},
        {"song_id": "S020", "title": "Ride or Die", "artist": "Nomad", "album": "Road Life", "duration": 198, "language": "英文", "genre": "摇滚", "style": "硬核", "era": "2000s", "tags": ["ride", "die"], "scene_tags": ["公路旅行"], "crowd_tags": ["冒险家"]}
    ]

    # 写入 songs.json
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump({"songs": songs}, f, ensure_ascii=False, indent=2)

    # 播放列表：保证"速度与激情"拥有最多歌曲（12首），其他均为9首以下，干扰项包括一个不存在的song_id
    playlists = [
        {
            "playlist_id": "PL01",
            "name": "嗨曲串烧",
            "description": "运动健身嗨曲",
            "song_ids": ["S001", "S002", "S003", "S004", "S005", "S006"],  # 6首
            "created_at": "2024-01-10T10:00:00Z",
            "updated_at": "2024-06-01T12:00:00Z"
        },
        {
            "playlist_id": "PL02",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["S002", "S006", "S009", "S011", "S017"],  # 5首
            "created_at": "2024-02-15T08:30:00Z",
            "updated_at": "2024-05-20T14:00:00Z"
        },
        {
            "playlist_id": "PL03",
            "name": "怀旧金曲",
            "description": "80后90后回忆杀",
            "song_ids": ["S003", "S005", "S007", "S009", "S014", "S019"],  # 6首
            "created_at": "2024-03-01T09:00:00Z",
            "updated_at": "2024-06-10T16:00:00Z"
        },
        {
            "playlist_id": "PL04",
            "name": "我的收藏",
            "description": "我最喜欢的歌曲",
            "song_ids": ["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008", "S009"],  # 9首
            "created_at": "2024-04-10T11:00:00Z",
            "updated_at": "2024-07-01T18:00:00Z"
        },
        {
            "playlist_id": "PL05",
            "name": "速度与激情",
            "description": "赛车电影主题曲",
            "song_ids": ["S001", "S004", "S006", "S008", "S010", "S012", "S013", "S015", "S016", "S018", "S020", "S999"],  # 12首（包含一个不存在的S999）
            "created_at": "2024-05-05T14:00:00Z",
            "updated_at": "2024-07-05T20:00:00Z"
        }
    ]

    # 写入 playlists.json
    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump({"playlists": playlists}, f, ensure_ascii=False, indent=2)

    # 标签定义（干扰项）
    tags = [
        {"tag": "赛车", "description": "与赛车相关的歌曲"},
        {"tag": "夜晚", "description": "适合夜晚听的歌"},
        {"tag": "怀旧", "description": "怀旧金曲"},
        {"tag": "电子", "description": "电子音乐"},
        {"tag": "摇滚", "description": "摇滚音乐"}
    ]
    with open("data/tags/tag_definitions.json", "w", encoding="utf-8") as f:
        json.dump({"tag_definitions": tags}, f, ensure_ascii=False, indent=2)

    # 额外干扰：一个损坏的json文件（格式不对）
    with open("data/playlists/broken.json", "w") as f:
        f.write("not json content")

    # 创建一个额外的无关目录
    os.makedirs("logs", exist_ok=True)
    with open("logs/system.log", "w") as f:
        f.write("2024-07-10 03:15:23 ERROR memory allocation failed\n")

if __name__ == "__main__":
    build_env()
