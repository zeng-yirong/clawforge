"""
Verify the agent's output for music player duplicate detection task.
Checks:
- ops/duplicate_songs_report.json exists and is valid JSON.
- Contains correct list of playlists with duplicate song IDs.
- No extra playlists reported.
Scoring: 100 total.
"""
import sys
import json
import os
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total = 0

    # --- Ground truth (must match env_builder) ---
    expected = {
        "ye_jia_shi": ["song_001"],
        "wo_de_shou_cang": ["song_005"]
    }

    # 1. ops directory exists (10 points)
    ops_dir = Path(workspace) / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/"})
        total += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing ops/ directory"})
        # If no directory, can't check file, skip remaining
        return {"total_score": total, "details": details}

    # 2. duplicate_songs_report.json exists (10 points)
    report_path = ops_dir / "duplicate_songs_report.json"
    if report_path.is_file():
        details.append({"item": "report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found duplicate_songs_report.json"})
        total += 10
    else:
        details.append({"item": "report file exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        return {"total_score": total, "details": details}

    # 3. JSON is valid and has correct structure (10 points)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        return {"total_score": total, "details": details}

    # Expect a list of objects with playlist_id and duplicate_song_ids (or similar)
    # We allow flexibility: can be list of dicts or dict of lists? But prompt said "报告里只需要列出有问题的播放列表 ID 和对应的重复歌曲 ID 列表"
    # We'll accept a dict mapping playlist_id to list of duplicate song ids, or a list of {playlist_id, duplicate_song_ids}.
    # For robustness, detect both.
    if isinstance(data, dict):
        # e.g. {"ye_jia_shi": ["song_001"], ...}
        report_data = data
    elif isinstance(data, list):
        # e.g. [{"playlist_id": "ye_jia_shi", "duplicate_song_ids": ["song_001"]}, ...]
        report_data = {}
        for entry in data:
            if isinstance(entry, dict) and "playlist_id" in entry:
                pid = entry["playlist_id"]
                # key might be "duplicate_song_ids" or "duplicate_songs" or "repeated_ids"
                dup_ids = entry.get("duplicate_song_ids") or entry.get("duplicate_songs") or entry.get("repeated_ids") or []
                report_data[pid] = dup_ids
            else:
                # malformed entry
                details.append({"item": "valid JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "Unexpected list entry format"})
                return {"total_score": total, "details": details}
    else:
        details.append({"item": "valid JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "Top-level must be dict or list"})
        return {"total_score": total, "details": details}

    # Now validate
    # Check that expected keys are present and no extra keys
    expected_keys = set(expected.keys())
    actual_keys = set(report_data.keys())
    missing_keys = expected_keys - actual_keys
    extra_keys = actual_keys - expected_keys

    if missing_keys:
        details.append({"item": "all expected playlists present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing playlist IDs: {missing_keys}"})
        # Still compute partial score on duplicate detection?
        # We'll continue but cap later
    else:
        details.append({"item": "all expected playlists present", "score": 10, "max_score": 10, "passed": True, "reason": "All target playlists found"})
        total += 10

    if extra_keys:
        details.append({"item": "no extra playlists reported", "score": 0, "max_score": 10, "passed": False, "reason": f"Extra playlist IDs: {extra_keys}"})
    else:
        details.append({"item": "no extra playlists reported", "score": 10, "max_score": 10, "passed": True, "reason": "No unexpected playlists"})
        total += 10

    # 4. Exact duplicate song IDs for each playlist (50 points total)
    points_per_playlist = 50 // len(expected)  # 25 each for 2 playlists
    left_over = 50 % len(expected)  # 0
    for pid, expected_dups in expected.items():
        actual_dups = sorted(report_data.get(pid, []))
        expected_sorted = sorted(expected_dups)
        if actual_dups == expected_sorted:
            details.append({"item": f"duplicate song IDs for {pid}", "score": points_per_playlist, "max_score": points_per_playlist, "passed": True, "reason": f"Correct: {actual_dups}"})
            total += points_per_playlist
        else:
            details.append({"item": f"duplicate song IDs for {pid}", "score": 0, "max_score": points_per_playlist, "passed": False, "reason": f"Expected {expected_sorted}, got {actual_dups}"})

    # Total must be integer, cap at 100
    total = min(total, 100)
    return {"total_score": total, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    out_path = Path(workspace) / "workplace_score.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Score written to {out_path}: {result['total_score']}/100")

if __name__ == "__main__":
    main()
