import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Songs 数据（包含干扰项）
    songs = [
        {"song_id":"S001","title":"Song1","artist":"Artist1","album":"Album1","duration":240,"language":"英文","genre":"摇滚","style":"慢摇","era":"2000s","tags":["classic"],"scene_tags":["drive"],"crowd_tags":["adult"]},
        {"song_id":"S002","title":"Song2","artist":"","album":"Album2","duration":200,"language":"英文","genre":"流行","style":"","era":"2010s","tags":[],"scene_tags":[],"crowd_tags":[]},
        {"song_id":"S003","title":"Song3","artist":"Artist3","album":"Album3","duration":300,"language":"中文","genre":"民谣","style":"怀旧","era":"1980s","tags":["old"],"scene_tags":["night"],"crowd_tags":["all"]},
        {"song_id":"S004","title":"Song4","artist":"Artist4","album":"Album4","duration":120,"language":"英文","genre":"电子","style":"舞曲","era":"2000s","tags":["party"],"scene_tags":["club"],"crowd_tags":["young"]},
        {"song_id":"S005","title":"Song5","artist":"Artist5","album":"Album5","duration":190,"language":"英文","genre":"流行","style":"轻快","era":"2010s","tags":["happy"],"scene_tags":["drive"],"crowd_tags":["adult"]},
        {"song_id":"S006","title":"Song6","artist":"Artist6","album":"Album6","duration":250,"language":"英文","genre":"摇滚","style":"激情","era":"2000s","tags":["power"],"scene_tags":["sport"],"crowd_tags":["young"]},
        {"song_id":"S007","title":"Song7","artist":"Artist7","album":"Album7","duration":400,"language":"英文","genre":"摇滚","style":"重金属","era":"1970s","tags":["metal"],"scene_tags":["live"],"crowd_tags":["fan"]},
        {"song_id":"S008","title":"Song8","artist":"Artist8","album":"Album8","duration":200,"language":"英文","genre":"民谣","style":"安静","era":"1980s","tags":["soft"],"scene_tags":["night"],"crowd_tags":["all"]},
        {"song_id":"S009","title":"Song9","artist":"Artist9","album":"Album9","duration":180,"language":"英文","genre":"流行","style":"轻快","era":"2010s","tags":["dance"],"scene_tags":["party"],"crowd_tags":["young"]},
        {"song_id":"S010","title":"Song10","artist":"Artist10","album":"Album10","duration":220,"language":"英文","genre":"电子","style":"迷幻","era":"2000s","tags":["chill"],"scene_tags":["night"],"crowd_tags":["adult"]},
        {"song_id":"S011","title":"Song11","artist":None,"album":"Album11","duration":300,"language":"英文","genre":"摇滚","style":"硬核","era":"1970s","tags":["hard"],"scene_tags":["live"],"crowd_tags":["fan"]}
    ]
    with open("data/songs/songs.json","w") as f:
        json.dump({"songs":songs}, f, indent=2, ensure_ascii=False)

    # Playlists 数据（目标“夜驾驶”包含重复ID）
    playlists = [
        {"playlist_id":"pl001","name":"嗨曲串烧","description":"运动健身嗨曲","song_ids":["S008","S003"],"created_at":"2024-01-01","updated_at":"2024-01-10"},
        {"playlist_id":"pl002","name":"夜驾驶","description":"夜晚开车听的歌","song_ids":["S001","S001","S002","S003","S004","S005","S006","S007","S009","S010","S011"],"created_at":"2024-02-01","updated_at":"2024-02-15"},
        {"playlist_id":"pl003","name":"怀旧金曲","description":"80后90后回忆杀","song_ids":["S003","S007"],"created_at":"2024-03-01","updated_at":"2024-03-20"},
        {"playlist_id":"pl004","name":"我的收藏","description":"我最喜欢的歌曲","song_ids":["S001","S005","S010"],"created_at":"2024-04-01","updated_at":"2024-04-25"},
        {"playlist_id":"pl005","name":"速度与激情","description":"赛车电影主题曲","song_ids":["S006","S008"],"created_at":"2024-05-01","updated_at":"2024-05-10"}
    ]
    with open("data/playlists/playlists.json","w") as f:
        json.dump({"playlists":playlists}, f, indent=2, ensure_ascii=False)

    # 干扰：旧版备份
    with open("data/playlists/playlists_old.json","w") as f:
        json.dump({"playlists":[{"playlist_id":"pl002","name":"夜驾驶","description":"旧版","song_ids":["S001","S003","S005"]}]}, f, indent=2)

    # Tags 数据
    tags = [{"tag":"classic","description":"经典"},{"tag":"happy","description":"快乐"}]
    with open("data/tags/tag_definitions.json","w") as f:
        json.dump({"tag_definitions":tags}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    build_env()
