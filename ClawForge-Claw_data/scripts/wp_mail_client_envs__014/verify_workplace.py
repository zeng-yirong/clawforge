import os
import sys
import json
import re

def load_json_file(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. ops目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    ops_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if ops_exists else 0,
        "max_score": 10,
        "passed": ops_exists,
        "reason": "ops/ directory found" if ops_exists else "ops/ directory missing"
    })
    if ops_exists:
        total_score += 10

    # 2. reply_list.json (10分)
    reply_path = os.path.join(ops_dir, "reply_list.json")
    reply_data = load_json_file(reply_path)
    reply_valid = False
    reply_ids = []
    if reply_data is not None and isinstance(reply_data, dict) and "reply_ids" in reply_data and isinstance(reply_data["reply_ids"], list):
        reply_valid = True
        reply_ids = reply_data["reply_ids"]
    details.append({
        "item": "reply_list.json is valid",
        "score": 10 if reply_valid else 0,
        "max_score": 10,
        "passed": reply_valid,
        "reason": "valid JSON with reply_ids list" if reply_valid else "missing or invalid reply_list.json"
    })
    if reply_valid:
        total_score += 10

    # 3. archive_list.json (10分)
    archive_path = os.path.join(ops_dir, "archive_list.json")
    archive_data = load_json_file(archive_path)
    archive_valid = False
    archive_ids = []
    if archive_data is not None and isinstance(archive_data, dict) and "archive_ids" in archive_data and isinstance(archive_data["archive_ids"], list):
        archive_valid = True
        archive_ids = archive_data["archive_ids"]
    details.append({
        "item": "archive_list.json is valid",
        "score": 10 if archive_valid else 0,
        "max_score": 10,
        "passed": archive_valid,
        "reason": "valid JSON with archive_ids list" if archive_valid else "missing or invalid archive_list.json"
    })
    if archive_valid:
        total_score += 10

    # 4. todo_items.json (10分)
    todo_path = os.path.join(ops_dir, "todo_items.json")
    todo_data = load_json_file(todo_path)
    todo_valid = False
    todo_items = []
    if todo_data is not None and isinstance(todo_data, list):
        todo_valid = True
        todo_items = todo_data
    details.append({
        "item": "todo_items.json is valid",
        "score": 10 if todo_valid else 0,
        "max_score": 10,
        "passed": todo_valid,
        "reason": "valid JSON list" if todo_valid else "missing or invalid todo_items.json"
    })
    if todo_valid:
        total_score += 10

    # 如果关键文件不全，提前结束或继续计算预期答案以输出详细评分
    # 计算预期答案
    inbox_dir = os.path.join(workspace, "inbox")
    contacts_path = os.path.join(workspace, "data", "contacts.json")
    contacts_data = load_json_file(contacts_path)
    contact_role_map = {}
    if contacts_data and "contacts" in contacts_data:
        for c in contacts_data["contacts"]:
            contact_role_map[c["contact_id"]] = c.get("role", "")

    expected_reply_ids = set()
    expected_archive_ids = set()
    expected_todo_items = []

    if os.path.isdir(inbox_dir):
        for fname in os.listdir(inbox_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(inbox_dir, fname)
            email = load_json_file(fpath)
            if email is None:
                continue
            # 检查必要字段
            if not all(k in email for k in ("id", "sender_id", "importance", "body")):
                continue
            eid = email["id"]
            sender = email["sender_id"]
            importance = email["importance"]
            body = email["body"]
            role = contact_role_map.get(sender, None)
            # 规则：重要性high 且 角色不是Spammer（或角色不存在则视为非Spammer）
            is_reply = (importance == "high") and (role != "Spammer")
            if is_reply:
                expected_reply_ids.add(eid)
                # 提取TODO/Action
                for line in body.split('\n'):
                    line_stripped = line.strip()
                    # 匹配 "Action: ..." 或 "TODO: ..."（不区分大小写？我们严格匹配首字母大写）
                    if line_stripped.startswith("Action:") or line_stripped.startswith("TODO:"):
                        # 取冒号后的内容并去除前后空格
                        todo_text = line_stripped.split(':', 1)[1].strip()
                        expected_todo_items.append({"email_id": eid, "todo": todo_text})
            else:
                expected_archive_ids.add(eid)
    else:
        # inbox不存在则预期为空
        pass

    # 5. reply_ids 正确性 (20分)
    if reply_valid:
        actual_reply_set = set(reply_ids)
        if actual_reply_set == expected_reply_ids:
            reply_score = 20
            reply_pass = True
            reply_reason = "reply_ids exactly match expected"
        else:
            missing = expected_reply_ids - actual_reply_set
            extra = actual_reply_set - expected_reply_ids
            reply_score = max(0, 20 - 5 * (len(missing) + len(extra)))
            reply_pass = reply_score > 0
            reply_reason = f"mismatch: missing {missing}, extra {extra}" if reply_score > 0 else "completely wrong reply_ids"
        details.append({
            "item": "reply_ids correctness",
            "score": reply_score,
            "max_score": 20,
            "passed": reply_pass,
            "reason": reply_reason
        })
        total_score += reply_score
    else:
        details.append({
            "item": "reply_ids correctness",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "reply_list.json not available"
        })

    # 6. archive_ids 正确性 (20分)
    if archive_valid:
        actual_archive_set = set(archive_ids)
        if actual_archive_set == expected_archive_ids:
            archive_score = 20
            archive_pass = True
            archive_reason = "archive_ids exactly match expected"
        else:
            missing = expected_archive_ids - actual_archive_set
            extra = actual_archive_set - expected_archive_ids
            archive_score = max(0, 20 - 5 * (len(missing) + len(extra)))
            archive_pass = archive_score > 0
            archive_reason = f"mismatch: missing {missing}, extra {extra}" if archive_score > 0 else "completely wrong archive_ids"
        details.append({
            "item": "archive_ids correctness",
            "score": archive_score,
            "max_score": 20,
            "passed": archive_pass,
            "reason": archive_reason
        })
        total_score += archive_score
    else:
        details.append({
            "item": "archive_ids correctness",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "archive_list.json not available"
        })

    # 7. todo_items 正确性 (20分)
    if todo_valid:
        # 将预期todo_items转换为可比较的排序列表（忽略顺序）
        expected_todo_sorted = sorted(expected_todo_items, key=lambda x: (x["email_id"], x["todo"]))
        # 对agent输出进行相同排序
        try:
            actual_todo_sorted = sorted(todo_items, key=lambda x: (x["email_id"], x["todo"]))
        except (KeyError, TypeError):
            actual_todo_sorted = []
        if actual_todo_sorted == expected_todo_sorted:
            todo_score = 20
            todo_pass = True
            todo_reason = "todo_items exactly match expected"
        else:
            # 计算差异个数
            set_expected = set((item["email_id"], item["todo"]) for item in expected_todo_items)
            set_actual = set()
            for item in todo_items:
                if isinstance(item, dict) and "email_id" in item and "todo" in item:
                    set_actual.add((item["email_id"], item["todo"]))
            diff = set_expected.symmetric_difference(set_actual)
            todo_score = max(0, 20 - 5 * len(diff))
            todo_pass = todo_score > 0
            todo_reason = f"mismatch items: {diff}" if todo_score > 0 else "completely wrong todo_items"
        details.append({
            "item": "todo_items correctness",
            "score": todo_score,
            "max_score": 20,
            "passed": todo_pass,
            "reason": todo_reason
        })
        total_score += todo_score
    else:
        details.append({
            "item": "todo_items correctness",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "todo_items.json not available"
        })

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
