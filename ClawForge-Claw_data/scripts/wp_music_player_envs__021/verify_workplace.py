import sys
import json
import os
import re

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify(workspace):
    score_details = []
    total_score = 0

    # ----- 1. 检查必要的目录结构 (10分) -----
    required_dirs = ['data/songs', 'data/playlists', 'data/rules', 'config', 'ops']
    passed_dirs = 0
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            passed_dirs += 1
    score_dirs = int(passed_dirs / len(required_dirs) * 10)
    total_score += score_dirs
    score_details.append({
        "item": "Required directories exist",
        "score": score_dirs,
        "max_score": 10,
        "passed": passed_dirs == len(required_dirs),
        "reason": f"Found {passed_dirs}/{len(required_dirs)} required directories."
    })

    # ----- 2. 检查产物文件存在 (10分) -----
    product_path = os.path.join(workspace, "ops/curated_playlist.json")
    if os.path.isfile(product_path):
        total_score += 10
        score_details.append({
            "item": "Output file ops/curated_playlist.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
    else:
        score_details.append({
            "item": "Output file ops/curated_playlist.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # 无法继续，直接返回
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        return

    # ----- 3. 检查JSON合法性 (10分) -----
    try:
        curated = load_json(product_path)
        score = 10
        total_score += 10
        score_details.append({
            "item": "Output JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON."
        })
    except Exception as e:
        score_details.append({
            "item": "Output JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        return

    # ----- 4. 检查字段完整性 (10分) -----
    required_fields = ["playlist_id", "name", "filtered_song_ids"]
    missing = [f for f in required_fields if f not in curated]
    if not missing:
        total_score += 10
        score_details.append({
            "item": "Required fields in output",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required fields present."
        })
    else:
        total_score += 0
        score_details.append({
            "item": "Required fields in output",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing fields: {missing}"
        })

    # ----- 5. 核心过滤逻辑正确性 (60分) 按照规则只保留中文歌曲 -----
    # 读取规则文件 (从config/active_rule.json中获取)
    active_rule_path = os.path.join(workspace, "config/active_rule.json")
    if not os.path.isfile(active_rule_path):
        total_score += 0
        score_details.append({
            "item": "Filter correctness (language=中文)",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "active_rule.json not found, cannot verify."
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        return

    try:
        active_rule_cfg = load_json(active_rule_path)
        rule_path = os.path.join(workspace, active_rule_cfg.get("active_rule_path", ""))
        if not os.path.isfile(rule_path):
            total_score += 0
            score_details.append({
                "item": "Filter correctness (language=中文)",
                "score": 0,
                "max_score": 60,
                "passed": False,
                "reason": f"Rule file {rule_path} not found."
            })
            output = {"total_score": total_score, "details": score_details}
            with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            return
        rule = load_json(rule_path)
    except Exception as e:
        total_score += 0
        score_details.append({
            "item": "Filter correctness (language=中文)",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": f"Error reading rule: {str(e)}"
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        return

    # 根据规则过滤：field, operator, value
    field = rule.get("field")
    operator = rule.get("operator")
    value = rule.get("value")
    if field != "language" or operator != "eq" or value != "中文":
        total_score += 0
        score_details.append({
            "item": "Filter correctness (language=中文)",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": f"Active rule is {rule}, expected language=中文."
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        return

    # 读取歌曲库
    songs_path = os.path.join(workspace, "data/songs/songs.json")
    if not os.path.isfile(songs_path):
        total_score += 0
        score_details.append({
            "item": "Filter correctness (language=中文)",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "songs.json not found."
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        return
    songs_data = load_json(songs_path)
    songs = {s["song_id"]: s for s in songs_data.get("songs", [])}

    # 读取“夜驾驶”播放列表的原始song_ids
    playlists_path = os.path.join(workspace, "data/playlists/playlists.json")
    if not os.path.isfile(playlists_path):
        total_score += 0
        score_details.append({
            "item": "Filter correctness (language=中文)",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "playlists.json not found."
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        return
    playlists_data = load_json(playlists_path)
    night_drive = None
    for pl in playlists_data.get("playlists", []):
        if pl["playlist_id"] == curated.get("playlist_id"):
            night_drive = pl
            break
    if night_drive is None:
        # 尝试按名称匹配
        for pl in playlists_data.get("playlists", []):
            if pl["name"] == "夜驾驶":
                night_drive = pl
                break
    if night_drive is None:
        total_score += 0
        score_details.append({
            "item": "Filter correctness (language=中文)",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "Could not find '夜驾驶' playlist in source."
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        return

    original_ids = set(night_drive["song_ids"])
    expected_filtered_ids = set(sid for sid in original_ids if songs.get(sid, {}).get("language") == "中文")
    actual_filtered_ids = set(curated.get("filtered_song_ids", []))

    # 比较
    if expected_filtered_ids == actual_filtered_ids:
        score = 60
        total_score += 60
        score_details.append({
            "item": "Filter correctness (language=中文)",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": f"Correct {len(expected_filtered_ids)} songs: {sorted(expected_filtered_ids)}"
        })
    else:
        # 部分正确？给部分分
        correct_ids = expected_filtered_ids & actual_filtered_ids
        wrong_ids = actual_filtered_ids - expected_filtered_ids
        missed_ids = expected_filtered_ids - actual_filtered_ids
        partial = len(correct_ids) / len(expected_filtered_ids) if expected_filtered_ids else 0
        score = int(partial * 60)
        total_score += score
        score_details.append({
            "item": "Filter correctness (language=中文)",
            "score": score,
            "max_score": 60,
            "passed": score == 60,
            "reason": f"Correct {len(correct_ids)}, wrong {len(wrong_ids)}, missed {len(missed_ids)}."
        })

    # 写结果
    output = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
