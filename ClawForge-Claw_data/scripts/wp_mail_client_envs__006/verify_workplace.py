import sys, os, json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    def add(item, max_score, passed, reason):
        nonlocal score
        s = max_score if passed else 0
        score += s
        details.append({"item": item, "score": s, "max_score": max_score, "passed": passed, "reason": reason})

    ops_dir = os.path.join(workspace, "ops")
    # 1. ops 目录存在
    add("ops directory exists", 4, os.path.isdir(ops_dir), "Found" if os.path.isdir(ops_dir) else "Not found")

    reply_path = os.path.join(ops_dir, "reply_tasks.json")
    todo_path = os.path.join(ops_dir, "todo_tasks.json")

    # 2. reply_tasks.json 存在
    add("reply_tasks.json exists", 4, os.path.isfile(reply_path), "Found" if os.path.isfile(reply_path) else "Not found")
    # 3. todo_tasks.json 存在
    add("todo_tasks.json exists", 4, os.path.isfile(todo_path), "Found" if os.path.isfile(todo_path) else "Not found")

    reply_data = None
    todo_data = None

    # 4. reply_tasks.json 合法 JSON 且为列表
    if os.path.isfile(reply_path):
        try:
            with open(reply_path, 'r') as f:
                reply_data = json.load(f)
            if isinstance(reply_data, list):
                add("reply_tasks.json is valid JSON list", 6, True, "Valid list")
            else:
                add("reply_tasks.json is valid JSON list", 6, False, "Not a list, type: {}".format(type(reply_data).__name__))
        except Exception as e:
            add("reply_tasks.json is valid JSON list", 6, False, "Invalid JSON: {}".format(e))
    else:
        add("reply_tasks.json is valid JSON list", 6, False, "File missing")

    # 5. todo_tasks.json 合法 JSON 且为列表
    if os.path.isfile(todo_path):
        try:
            with open(todo_path, 'r') as f:
                todo_data = json.load(f)
            if isinstance(todo_data, list):
                add("todo_tasks.json is valid JSON list", 6, True, "Valid list")
            else:
                add("todo_tasks.json is valid JSON list", 6, False, "Not a list, type: {}".format(type(todo_data).__name__))
        except Exception as e:
            add("todo_tasks.json is valid JSON list", 6, False, "Invalid JSON: {}".format(e))
    else:
        add("todo_tasks.json is valid JSON list", 6, False, "File missing")

    # 6. reply_tasks 长度 == 1
    if reply_data is not None and isinstance(reply_data, list):
        length = len(reply_data)
        add("reply_tasks length is exactly 1", 10, length == 1, "Length = {}".format(length))
    else:
        add("reply_tasks length is exactly 1", 10, False, "Not available")

    # 7. reply_tasks 每个元素包含必要字段
    if reply_data is not None and isinstance(reply_data, list):
        required_reply = {"mail_id", "recipient", "subject", "reply_body"}
        all_ok = all(isinstance(item, dict) and required_reply.issubset(item.keys()) for item in reply_data)
        add("reply_tasks each item has mail_id, recipient, subject, reply_body", 10, all_ok,
            "All items have fields" if all_ok else "Missing fields in some items")
    else:
        add("reply_tasks each item has mail_id, recipient, subject, reply_body", 10, False, "Not available")

    # 8. reply_tasks recipient = alice@clientcorp.com
    if reply_data is not None and isinstance(reply_data, list):
        all_correct = any(True for item in reply_data if isinstance(item, dict) and item.get("recipient") == "alice@clientcorp.com")
        # 要求所有回复的 recipient 正确
        all_ok = all(isinstance(item, dict) and item.get("recipient") == "alice@clientcorp.com" for item in reply_data) if len(reply_data) > 0 else False
        add("reply_tasks all recipients are alice@clientcorp.com", 5, all_ok,
            "Correct" if all_ok else "Wrong recipient found")
    else:
        add("reply_tasks all recipients are alice@clientcorp.com", 5, False, "Not available")

    # 9. reply_tasks reply_body 非空
    if reply_data is not None and isinstance(reply_data, list):
        all_nonempty = all(isinstance(item, dict) and item.get("reply_body") and item["reply_body"].strip() for item in reply_data)
        add("reply_tasks each reply_body is non-empty", 5, all_nonempty,
            "All non-empty" if all_nonempty else "Empty reply_body found")
    else:
        add("reply_tasks each reply_body is non-empty", 5, False, "Not available")

    # 10. todo_tasks 至少一个项目
    if todo_data is not None and isinstance(todo_data, list):
        add("todo_tasks has at least 1 item", 6, len(todo_data) >= 1, "Length = {}".format(len(todo_data)))
    else:
        add("todo_tasks has at least 1 item", 6, False, "Not available")

    # 11. todo_tasks 每个元素包含必要字段
    if todo_data is not None and isinstance(todo_data, list):
        required_todo = {"source_mail_id", "description"}
        all_ok = all(isinstance(item, dict) and required_todo.issubset(item.keys()) for item in todo_data)
        add("todo_tasks each item has source_mail_id, description", 10, all_ok,
            "All items have fields" if all_ok else "Missing fields in some items")
    else:
        add("todo_tasks each item has source_mail_id, description", 10, False, "Not available")

    # 12. todo_tasks 包含 source_mail_id = mail_001
    if todo_data is not None and isinstance(todo_data, list):
        has_mail001 = any(item.get("source_mail_id") == "mail_001" for item in todo_data if isinstance(item, dict))
        add("todo_tasks contains source_mail_id = mail_001", 5, has_mail001,
            "Found mail_001" if has_mail001 else "Missing mail_001")
    else:
        add("todo_tasks contains source_mail_id = mail_001", 5, False, "Not available")

    # 13. description 包含 "quarterly review" 或 "prepare"
    if todo_data is not None and isinstance(todo_data, list):
        desc_ok = any(
            isinstance(item, dict) and isinstance(item.get("description"), str) and
            ("quarterly review" in item["description"].lower() or "prepare" in item["description"].lower())
            for item in todo_data
        )
        add("todo_tasks description includes 'quarterly review' or 'prepare'", 10, desc_ok,
            "Matched" if desc_ok else "No matching description")
    else:
        add("todo_tasks description includes 'quarterly review' or 'prepare'", 10, False, "Not available")

    # 14. 没有多余的回复任务（除了 mail_001）
    extra_reply = 0
    if reply_data is not None and isinstance(reply_data, list):
        valid_reply_ids = {"mail_001"}
        for item in reply_data:
            if isinstance(item, dict) and item.get("mail_id") not in valid_reply_ids:
                extra_reply += 1
        add("No extra reply tasks beyond mail_001", 8, extra_reply == 0,
            "No extra" if extra_reply == 0 else "{} extra tasks".format(extra_reply))
    else:
        add("No extra reply tasks beyond mail_001", 8, False, "Not available")

    # 15. 没有多余的待办（除了 mail_001）
    extra_todo = 0
    if todo_data is not None and isinstance(todo_data, list):
        valid_todo_sources = {"mail_001"}
        for item in todo_data:
            if isinstance(item, dict) and item.get("source_mail_id") not in valid_todo_sources:
                extra_todo += 1
        add("No extra todo tasks from other mails", 7, extra_todo == 0,
            "No extra" if extra_todo == 0 else "{} extra tasks".format(extra_todo))
    else:
        add("No extra todo tasks from other mails", 7, False, "Not available")

    # 确保总分 0-100
    total = min(100, max(0, score))
    result = {
        "total_score": int(total),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print("Scoring complete -> workplace_score.json")

if __name__ == "__main__":
    main()
