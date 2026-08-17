import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(os.path.join(workspace, path), "r") as f:
        return json.load(f)

def check_file_exists(path):
    return os.path.isfile(os.path.join(workspace, path))

def verify():
    details = []
    total_score = 0

    # 1. 检查 ops/urgent_replies.json 是否存在 (10分)
    item = {"item": "Target file exists", "max_score": 10}
    if check_file_exists("ops/urgent_replies.json"):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops/urgent_replies.json found."
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "Missing ops/urgent_replies.json"
        details.append(item)
        # 文件不存在，后续无法检查
        total_score = 0
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return
    details.append(item)
    total_score += item["score"]

    # 2. 格式合法性 (20分)
    item = {"item": "JSON format validity", "max_score": 20}
    try:
        data = load_json("ops/urgent_replies.json")
        if not isinstance(data, list):
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "Root is not a list."
        else:
            valid = True
            for i, entry in enumerate(data):
                if not isinstance(entry, dict):
                    valid = False
                    item["reason"] = f"Entry {i} is not a dict."
                    break
                if not all(k in entry for k in ("id", "subject", "sender_name")):
                    valid = False
                    item["reason"] = f"Entry {i} missing one of id/subject/sender_name."
                    break
                if not isinstance(entry["id"], str) or not isinstance(entry["subject"], str) or not isinstance(entry["sender_name"], str):
                    valid = False
                    item["reason"] = f"Entry {i} has non-string field."
                    break
            if valid:
                item["score"] = 20
                item["passed"] = True
                item["reason"] = "Valid JSON array with required string fields."
            else:
                item["score"] = 0
                item["passed"] = False
    except (json.JSONDecodeError, IOError) as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Parse error: {e}"
    details.append(item)
    total_score += item["score"]

    if not item["passed"]:
        # 格式有问题，后续检查无意义，直接输出
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 记录数正确 (20分)
    item = {"item": "Correct number of records", "max_score": 20}
    expected_count = 3
    if len(data) == expected_count:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"Contains {expected_count} records."
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Expected {expected_count} records, got {len(data)}."
    details.append(item)
    total_score += item["score"]

    # 4. 每条记录内容完全正确 (30分) —— 每个正确匹配10分，共3条
    item = {"item": "Correct record contents", "max_score": 30}
    expected_set = {
        ("email_001", "Invoice payment pending", "Alice Client"),
        ("email_002", "Urgent: server down", "Bob Vendor"),
        ("email_006", "Code review request", "Sarah Developer"),
    }
    actual_set = {(e["id"], e["subject"], e["sender_name"]) for e in data}
    matched = actual_set & expected_set
    match_count = len(matched)
    if match_count == 3:
        item["score"] = 30
        item["passed"] = True
        item["reason"] = "All three records match precisely."
    else:
        # 部分匹配：每个正确给10分
        partial = match_count * 10
        item["score"] = partial
        item["passed"] = False
        missing = expected_set - actual_set
        extra = actual_set - expected_set
        reasons = []
        if missing:
            reasons.append(f"Missing: {missing}")
        if extra:
            reasons.append(f"Unexpected: {extra}")
        item["reason"] = "; ".join(reasons)
    details.append(item)
    total_score += item["score"]

    # 5. 无多余字段 (10分)
    item = {"item": "No extra fields in any entry", "max_score": 10}
    allowed_fields = {"id", "subject", "sender_name"}
    has_extra = False
    for entry in data:
        if set(entry.keys()) != allowed_fields:
            has_extra = True
            item["reason"] = f"Entry with id={entry.get('id')} has extra fields: {set(entry.keys()) - allowed_fields}"
            break
    if not has_extra:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "All entries contain only id, subject, sender_name."
    else:
        item["score"] = 0
        item["passed"] = False
    details.append(item)
    total_score += item["score"]

    # 6. 无多余记录 (10分) —— 实际已在记录数中体现，但作为独立项强化
    item = {"item": "No extraneous records (exact set)", "max_score": 10}
    if actual_set == expected_set:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Produced exactly the required records."
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Set mismatch: got {actual_set}, expected {expected_set}"
    details.append(item)
    total_score += item["score"]

    # 写入结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
