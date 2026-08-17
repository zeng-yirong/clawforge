import os
import json

def build_env():
    # Create required directories
    os.makedirs("data/playlists", exist_ok=True)
    os.makedirs("data/songs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # Create distractor directories
    os.makedirs("backups", exist_ok=True)
    os.makedirs("old_versions", exist_ok=True)

    # Songs data
    songs = [
        {"song_id": "song_001", "title": "Fly Away", "artist": "Lenny", "album": "Top Hits", "duration": 240, "language": "英文", "genre": "流行", "style": "upbeat", "era": "2010s", "tags": ["road trip"], "scene_tags": ["highway"], "crowd_tags": ["youth"]},
        {"song_id": "song_002", "title": "My Way", "artist": "Frank", "album": "Classics", "duration": 280, "language": "英文", "genre": "摇滚", "style": "slow", "era": "1970s", "tags": ["classic"], "scene_tags": ["night"], "crowd_tags": ["adult"]},
        {"song_id": "song_003", "title": "Racing Heart", "artist": "DJ Speed", "album": "Fast & Furious", "duration": 210, "language": "中文", "genre": "电子", "style": "fast", "era": "2000s", "tags": ["race"], "scene_tags": ["racing"], "crowd_tags": ["sport"]},
        {"song_id": "song_004", "title": "Drift", "artist": "Nitro", "album": "Street Racer", "duration": 195, "language": "英文", "genre": "电子", "style": "intense", "era": "2010s", "tags": ["drift"], "scene_tags": ["street"], "crowd_tags": ["sport"]},
        {"song_id": "song_005", "title": "Slow Down", "artist": "Chill", "album": "Relax", "duration": 300, "language": "中文", "genre": "民谣", "style": "soft", "era": "1980s", "tags": ["chill"], "scene_tags": ["park"], "crowd_tags": ["adult"]},
        # Distractor song (valid but not in the target playlist)
        {"song_id": "song_006", "title": "Old Song", "artist": "Vintage", "album": "Retro", "duration": 180, "language": "中文", "genre": "流行", "style": "calm", "era": "1970s", "tags": ["old"], "scene_tags": ["home"], "crowd_tags": ["adult"]}
    ]
    with open("data/songs/songs.json", "w", encoding="utf-8") as f:
        json.dump({"songs": songs}, f, ensure_ascii=False, indent=2)

    # Playlists data
    playlists = [
        {
            "playlist_id": "pl_high_energy",
            "name": "速度与激情",
            "description": "赛车电影主题曲",
            "song_ids": ["song_001", "song_002", "song_003", "song_004", "song_005"],
            "created_at": "2024-01-01",
            "updated_at": "2024-01-10"
        },
        {
            "playlist_id": "pl_chill",
            "name": "夜驾驶",
            "description": "夜晚开车听的歌",
            "song_ids": ["song_002", "song_005", "song_006"],
            "created_at": "2024-02-01",
            "updated_at": "2024-02-05"
        },
        # Distractor playlist with an invalid song_id (song_007 does not exist)
        {
            "playlist_id": "pl_old_backup",
            "name": "怀旧金曲（旧版）",
            "description": "旧数据，不要用",
            "song_ids": ["song_001", "song_002", "song_003", "song_007"],
            "created_at": "2023-12-01",
            "updated_at": "2023-12-10"
        }
    ]
    with open("data/playlists/playlists.json", "w", encoding="utf-8") as f:
        json.dump({"playlists": playlists}, f, ensure_ascii=False, indent=2)

    # Current playback state
    current = {
        "playlist_id": "pl_high_energy",
        "current_song_id": "song_003",
        "mode": "loop",  # loop mode ensures deterministic next song
        "timestamp": "2025-04-01T12:00:00"
    }
    with open("ops/current_playback.json", "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)

    # Distractor files
    backup = {
        "playlist_id": "pl_old_backup",
        "current_song_id": "song_002",
        "mode": "sequential"
    }
    with open("backups/old_state.json", "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)

    with open("old_versions/deprecated.txt", "w") as f:
        f.write("don't use this\n")

    with open("data/extra_info.csv", "w") as f:
        f.write("id,value\n1,abc\n")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
