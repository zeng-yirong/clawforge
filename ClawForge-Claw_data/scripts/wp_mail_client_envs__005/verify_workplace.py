import json, os, sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 目录 ops 存在 (10)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops directory found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops directory missing"})

    # 2. ops/urgent_clients.json 文件存在 (10)
    result_path = os.path.join(ops_dir, "urgent_clients.json")
    if os.path.isfile(result_path):
        details.append({"item": "urgent_clients.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "urgent_clients.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # 后续检查无法进行，直接输出
        write_score(total_score, details)
        return

    # 3. JSON 合法 (10)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
        total_score += 10
    except json.JSONDecodeError as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {str(e)}"})
        write_score(total_score, details)
        return

    # 4. 数据结构：应该是列表，或包含 ids 键的字典？允许任意，但要求包含所有正确 id
    # 我们允许 列表 或 包含 "ids" 键的字典，或 包含 "id" 键的字典列表。只要最终得到一组 ID。
    ids = None
    if isinstance(data, list):
        ids = set(data)  # 假设列表元素就是 ID 字符串
    elif isinstance(data, dict):
        if "ids" in data and isinstance(data["ids"], list):
            ids = set(data["ids"])
        elif "id" in data:
            ids = {data["id"]}
        elif "urgent_emails" in data and isinstance(data["urgent_emails"], list):
            ids = set(data["urgent_emails"])
    # 如果都匹配不上，给格式分低
    if ids is not None:
        details.append({"item": "Data format acceptable (list or dict with ids)", "score": 10, "max_score": 10, "passed": True, "reason": f"found {len(ids)} elements"})
        total_score += 10
    else:
        details.append({"item": "Data format acceptable", "score": 0, "max_score": 10, "passed": False, "reason": "unexpected format, expected a list of IDs or dict with 'ids' key"})
        write_score(total_score, details)
        return

    # 构建预期答案：Alice Client 的两封紧急未读邮件
    # 从 data/emails 中读取全部邮件，筛出 sender_id 为 c_alice 且 importance=high 且 has_read=false
    expected_ids = set()
    emails_dir = os.path.join(workspace, "data", "emails")
    if not os.path.isdir(emails_dir):
        details.append({"item": "Emails directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "data/emails missing, cannot verify"})
        write_score(total_score, details)
        return

    for fname in os.listdir(emails_dir):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(emails_dir, fname)) as f:
            try:
                email = json.load(f)
            except:
                continue
        if email.get("sender_id") == "c_alice" and email.get("importance") == "high" and email.get("has_read") is False:
            expected_ids.add(email["id"])

    # 5. 内容正确性 (60分)
    correct = len(ids & expected_ids)
    total_expected = len(expected_ids)
    false_positive = len(ids - expected_ids)

    if total_expected == 0:
        item_score = 60 if len(ids) == 0 else 0
    else:
        # 每正确一个得 60/total_expected, 错误一个扣 60/total_expected
        per = 60 / total_expected
        score = correct * per - false_positive * per
        item_score = max(0, round(score))

    details.append({
        "item": "Content matches expected urgent client emails",
        "score": item_score,
        "max_score": 60,
        "passed": item_score == 60,
        "reason": f"expected {expected_ids}, got {ids}, correct={correct}, false_positive={false_positive}"
    })
    total_score += item_score

    write_score(total_score, details)

def write_score(total, details):
    score = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(score, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
