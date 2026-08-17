#!/usr/bin/env python3
import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score = 0
details = []

# 1. 目录结构检查 (10分)
required_dirs = ["policies", "platforms", "bookings", "ops", "logs"]
all_dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in required_dirs)
dir_score = 10 if all_dirs_exist else 0
details.append({
    "item": "Required directories exist",
    "score": dir_score,
    "max_score": 10,
    "passed": all_dirs_exist,
    "reason": "All required dirs present" if all_dirs_exist else f"Missing: {[d for d in required_dirs if not os.path.isdir(os.path.join(workspace, d))]}"
})

# 2. 检查 ops/pending_approvals.json 是否存在 (10分)
expected_path = os.path.join(workspace, "ops", "pending_approvals.json")
file_exists = os.path.isfile(expected_path)
file_score = 10 if file_exists else 0
details.append({
    "item": "ops/pending_approvals.json exists",
    "score": file_score,
    "max_score": 10,
    "passed": file_exists,
    "reason": "File found" if file_exists else "File not found"
})

if not file_exists:
    # 无法继续，总分
    total = sum(d["score"] for d in details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Total score: {total}")
    sys.exit(0)

# 3. JSON 合法性 (10分)
try:
    with open(expected_path, "r") as f:
        data = json.load(f)
    is_valid_json = True
    json_score = 10
    reason = "Valid JSON"
except (json.JSONDecodeError, ValueError):
    is_valid_json = False
    json_score = 0
    reason = "Invalid JSON"
details.append({
    "item": "JSON is valid",
    "score": json_score,
    "max_score": 10,
    "passed": is_valid_json,
    "reason": reason
})

if not is_valid_json:
    total = sum(d["score"] for d in details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Total score: {total}")
    sys.exit(0)

# 4. 必须是列表 (10分)
is_list = isinstance(data, list)
list_score = 10 if is_list else 0
details.append({
    "item": "Content is a list",
    "score": list_score,
    "max_score": 10,
    "passed": is_list,
    "reason": "Is a list" if is_list else f"Type is {type(data).__name__}"
})

if not is_list:
    total = sum(d["score"] for d in details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Total score: {total}")
    sys.exit(0)

# 5. 列表长度正确 (20分) 预期长度 4
expected_ids = {"BK-1001", "BK-1003", "BK-1007", "BK-1010"}
actual_ids = set(data)
length_correct = len(actual_ids) == 4
len_score = 20 if length_correct else 0
details.append({
    "item": "List contains exactly 4 booking IDs",
    "score": len_score,
    "max_score": 20,
    "passed": length_correct,
    "reason": f"Found {len(actual_ids)} unique IDs" if length_correct else f"Expected 4, got {len(actual_ids)}"
})

# 6. 内容精确匹配 (50分)
# 检查每个预期 ID 都在列表中，且没有多余 ID
missing = expected_ids - actual_ids
extra = actual_ids - expected_ids
content_correct = (len(missing) == 0 and len(extra) == 0)
content_score = 50 if content_correct else 0
reason = ""
if missing:
    reason += f"Missing: {missing}. "
if extra:
    reason += f"Extra: {extra}. "
if not reason:
    reason = "All IDs correctly present"
details.append({
    "item": "Booking IDs match expected set",
    "score": content_score,
    "max_score": 50,
    "passed": content_correct,
    "reason": reason
})

total_score = sum(d["score"] for d in details)
# 写入结果
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": details}, f, indent=2)

print(f"Total score: {total_score}")
