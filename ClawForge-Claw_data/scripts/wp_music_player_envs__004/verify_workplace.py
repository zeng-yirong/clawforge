import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0

    # 1. Check required directories (10 points)
    required_dirs = ["data/playlists", "data/songs", "ops"]
    dir_score = 0
    dir_errors = []
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 3
        else:
            dir_errors.append(f"Missing directory: {d}")
    # Rounding for the last point (10 total)
    if dir_score == 9:
        dir_score = 10
    details.append({
        "item": "Directory structure",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": "; ".join(dir_errors) if dir_errors else "All required directories present"
    })
    total_score += dir_score

    # 2. Check ops/current_playback.json validity (10 points)
    cp_path = os.path.join(workspace, "ops", "current_playback.json")
    cp_data = None
    if os.path.isfile(cp_path):
        try:
            with open(cp_path, "r") as f:
                cp_data = json.load(f)
            required_fields = ["playlist_id", "current_song_id", "mode"]
            if all(field in cp_data for field in required_fields):
                details.append({
                    "item": "Current playback JSON valid",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "File exists and contains required fields"
                })
                total_score += 10
            else:
                details.append({
                    "item": "Current playback JSON missing fields",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"Missing one of {required_fields}"
                })
        except json.JSONDecodeError:
            details.append({
                "item": "Current playback JSON parse error",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Invalid JSON format"
            })
    else:
        details.append({
            "item": "Current playback JSON missing",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })

    # 3. Load songs and playlists (10 points)
    songs_path = os.path.join(workspace, "data", "songs", "songs.json")
    playlists_path = os.path.join(workspace, "data", "playlists", "playlists.json")
    songs = {}
    playlists = {}
    if os.path.isfile(songs_path) and os.path.isfile(playlists_path):
        try:
            with open(songs_path, "r") as f:
                songs_data = json.load(f)
                for s in songs_data.get("songs", []):
                    songs[s["song_id"]] = s
            with open(playlists_path, "r") as f:
                pl_data = json.load(f)
                for pl in pl_data.get("playlists", []):
                    playlists[pl["playlist_id"]] = pl
            details.append({
                "item": "Load songs and playlists",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Both files parsed successfully"
            })
            total_score += 10
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            details.append({
                "item": "Load songs and playlists",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Parse error: {str(e)}"
            })
    else:
        details.append({
            "item": "Load songs and playlists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "One or both data files missing"
        })

    # 4. Compute expected next song (50 points)
    expected_next = None
    if cp_data and playlists and songs:
        pl_id = cp_data.get("playlist_id")
        current_song = cp_data.get("current_song_id")
        mode = cp_data.get("mode")
        if pl_id and current_song and pl_id in playlists:
            pl = playlists[pl_id]
            song_ids = pl.get("song_ids", [])
            if current_song in song_ids:
                idx = song_ids.index(current_song)
                if mode == "loop":
                    expected_next = song_ids[(idx + 1) % len(song_ids)]
                elif mode == "sequential":
                    if idx + 1 < len(song_ids):
                        expected_next = song_ids[idx + 1]
                    else:
                        expected_next = None   # no next song
                # other modes not defined – leave as None

    # 5. Check ops/next_song.json (50 points)
    next_path = os.path.join(workspace, "ops", "next_song.json")
    next_score = 0
    next_reason = ""
    if os.path.isfile(next_path):
        try:
            with open(next_path, "r") as f:
                next_data = json.load(f)
            if isinstance(next_data, dict) and "next_song_id" in next_data:
                provided = next_data["next_song_id"]
                if provided == expected_next:
                    next_score = 50
                    next_reason = f"Correct next_song_id: {provided}"
                else:
                    next_reason = f"Expected {expected_next}, got {provided}"
            else:
                next_reason = "Missing key 'next_song_id' or invalid structure"
        except json.JSONDecodeError:
            next_reason = "Invalid JSON in next_song.json"
    else:
        next_reason = "File ops/next_song.json not found"

    details.append({
        "item": "Next song ID",
        "score": next_score,
        "max_score": 50,
        "passed": next_score == 50,
        "reason": next_reason
    })
    total_score += next_score

    # Write result
    result = {"total_score": total_score, "details": details}
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
