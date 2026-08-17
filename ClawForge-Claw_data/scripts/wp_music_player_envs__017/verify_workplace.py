import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0
max_total = 100

# 1. 检查 ops/problem_song.json 是否存在
target_path = os.path.join(workspace, "ops", "problem_song.json")
exists = os.path.isfile(target_path)
score_details.append({
    "item": "ops/problem_song.json exists",
    "score": 10 if exists else 0,
    "max_score": 10,
    "passed": exists,
    "reason": "File found" if exists else "File missing"
})
total_score += score_details[-1]["score"]

# 2. 检查文件是否为合法 JSON 对象
valid_json = False
parsed = None
if exists:
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            parsed = json.load(f)
        valid_json = isinstance(parsed, dict)
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass

score_details.append({
    "item": "JSON is valid dict",
    "score": 10 if valid_json else 0,
    "max_score": 10,
    "passed": valid_json,
    "reason": "Valid JSON dict" if valid_json else "Invalid or not a dict"
})
total_score += score_details[-1]["score"]

# 3. 检查是否包含 "song_id" 键
has_key = valid_json and "song_id" in parsed
score_details.append({
    "item": "Contains key 'song_id'",
    "score": 20 if has_key else 0,
    "max_score": 20,
    "passed": has_key,
    "reason": f"Key found: {parsed.get('song_id')}" if has_key else "Key missing"
})
total_score += score_details[-1]["score"]

# 4. 检查 song_id 值是否为字符串且等于 "song_004"
value_correct = False
if has_key:
    val = parsed["song_id"]
    if isinstance(val, str) and val == "song_004":
        value_correct = True

score_details.append({
    "item": "song_id value is 'song_004'",
    "score": 30 if value_correct else 0,
    "max_score": 30,
    "passed": value_correct,
    "reason": f"Correct value: {parsed['song_id']}" if value_correct else f"Wrong value: {parsed.get('song_id', 'N/A')}"
})
total_score += score_details[-1]["score"]

# 5. 检查 song_id 值是否为字符串类型（确保不是数字等）
type_ok = has_key and isinstance(parsed["song_id"], str)
score_details.append({
    "item": "song_id value is string",
    "score": 10 if type_ok else 0,
    "max_score": 10,
    "passed": type_ok,
    "reason": "Type is string" if type_ok else "Type is not string"
})
total_score += score_details[-1]["score"]

# 6. 数据一致性检查：读取 data/songs/songs.json 验证 song_004 的 duration == -1
data_consistent = False
songs_path = os.path.join(workspace, "data", "songs", "songs.json")
if os.path.isfile(songs_path):
    try:
        with open(songs_path, "r", encoding="utf-8") as f:
            songs_data = json.load(f)
        for song in songs_data.get("songs", []):
            if song.get("song_id") == "song_004":
                if song.get("duration") == -1:
                    data_consistent = True
                break
    except:
        pass

score_details.append({
    "item": "Data consistency: song_004 duration == -1",
    "score": 20 if data_consistent else 0,
    "max_score": 20,
    "passed": data_consistent,
    "reason": "Duration matches -1 in source" if data_consistent else "Duration mismatch or source missing"
})
total_score += score_details[-1]["score"]

# 总分
result = {
    "total_score": total_score,
    "details": score_details
}

out_path = os.path.join(workspace, "workplace_score.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Score: {total_score}/{max_total}")
