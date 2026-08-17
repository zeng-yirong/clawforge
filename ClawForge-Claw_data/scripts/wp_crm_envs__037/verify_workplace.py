import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def check_path(path, max_score, desc):
    full_path = os.path.join(workspace, path)
    exists = os.path.exists(full_path)
    points = max_score if exists else 0
    passed = exists
    reason = f"{desc}: file {'found' if exists else 'not found'}"
    score_details.append({
        "item": desc,
        "score": points,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return exists, full_path

# 1. 检查 ops/pending_birthdays.json 是否存在 (10)
exists_ops, ops_path = check_path("ops/pending_birthdays.json", 10, "Output file ops/pending_birthdays.json exists")
if not exists_ops:
    total_score = sum(item["score"] for item in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 2. 检查文件是否为合法 JSON (10)
try:
    with open(ops_path, "r") as f:
        data = json.load(f)
    score_details.append({
        "item": "Valid JSON format",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File can be parsed as JSON"
    })
except (json.JSONDecodeError, Exception) as e:
    score_details.append({
        "item": "Valid JSON format",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": f"Invalid JSON: {e}"
    })
    total_score = sum(item["score"] for item in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 3. 检查是否为 list (10)
if isinstance(data, list):
    score_details.append({
        "item": "JSON root is a list",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Root object is a list"
    })
else:
    score_details.append({
        "item": "JSON root is a list",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": f"Root is {type(data).__name__}, expected list"
    })
    total_score = sum(item["score"] for item in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 4. 预期唯一缺失的联系人是 contact_002 (Carol Williams)
expected_missing = "contact_002"
# 应包含的联系人集合
expected_set = {expected_missing}
# 检查是否包含正确元素 (20)
actual_set = set(data)
if expected_set == actual_set:
    score_details.append({
        "item": "Contains exactly the missing contact contact_002",
        "score": 20,
        "max_score": 20,
        "passed": True,
        "reason": f"List contains only {expected_missing}"
    })
else:
    # 给予部分分：包含正确元素给10，无多余给10
    part1 = 10 if expected_missing in actual_set else 0
    part2 = 0
    if part1 == 10:
        extra = actual_set - expected_set
        if not extra:
            part2 = 10
        else:
            part2 = 0
    total_part = part1 + part2
    reason_parts = []
    if expected_missing in actual_set:
        reason_parts.append("correct missing contact included")
    else:
        reason_parts.append("missing contact not found")
    extra = actual_set - expected_set
    if extra:
        reason_parts.append(f"unexpected contacts: {extra}")
    score_details.append({
        "item": "Contains exactly the missing contact contact_002",
        "score": total_part,
        "max_score": 20,
        "passed": total_part == 20,
        "reason": ". ".join(reason_parts) if reason_parts else "no clear reason"
    })

# 5. 检查是否包含不应有的联系人（如已有提醒的 contact_001 和 contact_003）(15)
unwanted = {"contact_001", "contact_003"}
if not (actual_set & unwanted):
    score_details.append({
        "item": "Does not include contacts with existing birthday reminders (contact_001, contact_003)",
        "score": 15,
        "max_score": 15,
        "passed": True,
        "reason": "No pre-existing birthday contacts in list"
    })
else:
    found_unwanted = actual_set & unwanted
    score_details.append({
        "item": "Does not include contacts with existing birthday reminders (contact_001, contact_003)",
        "score": 0,
        "max_score": 15,
        "passed": False,
        "reason": f"Included unwanted contacts: {found_unwanted}"
    })

# 6. 是否包含脏数据中的不存在的 contact_999 或公司不存在的 contact_006 (15)
invalid_set = {"contact_006", "contact_999"}
if not (actual_set & invalid_set):
    score_details.append({
        "item": "No invalid/orphan contacts included",
        "score": 15,
        "max_score": 15,
        "passed": True,
        "reason": "List does not contain orphan contacts"
    })
else:
    found_invalid = actual_set & invalid_set
    score_details.append({
        "item": "No invalid/orphan contacts included",
        "score": 0,
        "max_score": 15,
        "passed": False,
        "reason": f"Included invalid contacts: {found_invalid}"
    })

# 7. 列表长度是否正好为1（10）
if len(data) == 1:
    score_details.append({
        "item": "List length is exactly 1",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Only one missing contact expected"
    })
else:
    score_details.append({
        "item": "List length is exactly 1",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": f"Length is {len(data)}, expected 1"
    })

# 8. 额外项：检查 ops 目录是否被创建（但文件存在已暗示）不需要重复

# 计算总分
total_score = sum(item["score"] for item in score_details)

# 写入结果
result = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
