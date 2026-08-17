import sys
import os
import json

def check_file_exists(path):
    return os.path.isfile(path)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    total = 0

    # 1) 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    scores.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    if dir_exists:
        total += 10

    # 2) 检查 ops/next_song.json 是否存在 (20分)
    result_path = os.path.join(ops_dir, "next_song.json")
    file_exists = check_file_exists(result_path)
    scores.append({
        "item": "ops/next_song.json exists",
        "score": 20 if file_exists else 0,
        "max_score": 20,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file missing"
    })
    if file_exists:
        total += 20

    # 3) JSON 格式合法性 (15分)
    json_valid = False
    data = None
    if file_exists:
        try:
            data = load_json(result_path)
            json_valid = True
            total += 15
            scores.append({
                "item": "JSON format validity",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "valid JSON"
            })
        except (json.JSONDecodeError, Exception) as e:
            scores.append({
                "item": "JSON format validity",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"invalid JSON: {e}"
            })
    else:
        scores.append({
            "item": "JSON format validity",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "file not found, cannot check"
        })

    # 4) 键名 next_song_id 存在且值为字符串 (15分)
    key_correct = False
    if json_valid and isinstance(data, dict):
        if "next_song_id" in data and isinstance(data["next_song_id"], str):
            key_correct = True
            total += 15
            scores.append({
                "item": "key next_song_id present and string type",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "correct key and type"
            })
        else:
            scores.append({
                "item": "key next_song_id present and string type",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "missing key or wrong type"
            })
    else:
        scores.append({
            "item": "key next_song_id present and string type",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "previous checks failed"
        })

    # 5) 值必须为 "song_004" (40分)
    value_correct = False
    if key_correct:
        if data["next_song_id"] == "song_004":
            value_correct = True
            total += 40
            scores.append({
                "item": "next_song_id value is song_004",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": "exact match"
            })
        else:
            scores.append({
                "item": "next_song_id value is song_004",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"got '{data['next_song_id']}', expected 'song_004'"
            })
    else:
        scores.append({
            "item": "next_song_id value is song_004",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "previous checks failed"
        })

    # 最终总分
    result = {
        "total_score": total,
        "details": scores
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Total score: {total}/100")
    return total

if __name__ == "__main__":
    main()
