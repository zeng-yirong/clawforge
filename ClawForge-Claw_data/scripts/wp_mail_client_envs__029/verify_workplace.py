import sys
import os
import json
import pathlib

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."
BASE = pathlib.Path(WORKSPACE)

def score():
    details = []
    total = 0

    # ---- 1. Directory and file structure (25 pts) ----
    # 1a. ops/ exists (5)
    ops_dir = BASE / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found ops/ directory"})
        total += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ directory missing"})

    # 1b. reply_draft.json exists (10)
    reply_path = ops_dir / "reply_draft.json"
    if reply_path.is_file():
        details.append({"item": "reply_draft.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total += 10
    else:
        details.append({"item": "reply_draft.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})

    # 1c. todos.json exists (10)
    todos_path = ops_dir / "todos.json"
    if todos_path.is_file():
        details.append({"item": "todos.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total += 10
    else:
        details.append({"item": "todos.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})

    # ---- 2. reply_draft.json content (25 pts) ----
    if reply_path.is_file():
        try:
            with open(reply_path, "r", encoding="utf-8") as f:
                reply = json.load(f)
            if isinstance(reply, dict) and "to" in reply and "body" in reply:
                # 2a. to field correct (10)
                to_ok = reply["to"] == "alice@clientcorp.com"
                details.append({"item": "reply_draft.to = alice@clientcorp.com", "score": 10 if to_ok else 0, "max_score": 10, "passed": to_ok, "reason": f"Got '{reply['to']}'" if not to_ok else "Correct"})
                total += 10 if to_ok else 0

                # 2b. body field correct (15)
                body_ok = reply["body"] == "报价已确认，谢谢"
                details.append({"item": "reply_draft.body = '报价已确认，谢谢'", "score": 15 if body_ok else 0, "max_score": 15, "passed": body_ok, "reason": f"Got '{reply['body']}'" if not body_ok else "Correct"})
                total += 15 if body_ok else 0
            else:
                details.append({"item": "reply_draft.json valid JSON structure", "score": 0, "max_score": 25, "passed": False, "reason": "Not a dict with 'to' and 'body'"})
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "reply_draft.json valid JSON", "score": 0, "max_score": 25, "passed": False, "reason": f"Invalid JSON: {str(e)}"})

    # ---- 3. todos.json content (20 pts) ----
    if todos_path.is_file():
        try:
            with open(todos_path, "r", encoding="utf-8") as f:
                todos = json.load(f)
            if isinstance(todos, list) and len(todos) >= 1:
                task_item = todos[0]
                if isinstance(task_item, dict) and "task" in task_item:
                    task_ok = task_item["task"] == "请尽快支付发票 #123"
                    details.append({"item": "todos[0].task correct", "score": 20 if task_ok else 0, "max_score": 20, "passed": task_ok, "reason": f"Got '{task_item['task']}'" if not task_ok else "Correct"})
                    total += 20 if task_ok else 0
                else:
                    details.append({"item": "todos[0] has 'task' field", "score": 0, "max_score": 20, "passed": False, "reason": "First element missing 'task' key"})
            else:
                details.append({"item": "todos.json is a non-empty array", "score": 0, "max_score": 20, "passed": False, "reason": "Not a list or empty"})
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "todos.json valid JSON", "score": 0, "max_score": 20, "passed": False, "reason": f"Invalid JSON: {str(e)}"})

    # ---- 4. Archive results (20 pts) ----
    email_base = BASE / "data" / "emails"
    # 4a. email_003 folder = hr (10)
    email_003_path = email_base / "email_003.json"
    if email_003_path.is_file():
        try:
            with open(email_003_path, "r", encoding="utf-8") as f:
                email3 = json.load(f)
            if email3.get("folder") == "hr":
                details.append({"item": "email_003 folder = hr", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
                total += 10
            else:
                details.append({"item": "email_003 folder = hr", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{email3.get('folder')}'"})
        except Exception as e:
            details.append({"item": "email_003 readable JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Error: {str(e)}"})
    else:
        details.append({"item": "email_003 exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing (should not be deleted)"})

    # 4b. email_004 folder = work (10)
    email_004_path = email_base / "email_004.json"
    if email_004_path.is_file():
        try:
            with open(email_004_path, "r", encoding="utf-8") as f:
                email4 = json.load(f)
            if email4.get("folder") == "work":
                details.append({"item": "email_004 folder = work", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
                total += 10
            else:
                details.append({"item": "email_004 folder = work", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{email4.get('folder')}'"})
        except Exception as e:
            details.append({"item": "email_004 readable JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Error: {str(e)}"})
    else:
        details.append({"item": "email_004 exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing (should not be deleted)"})

    # ---- 5. Deletion of spam/newsletter (10 pts) ----
    spam_files = ["email_005.json", "email_006.json"]
    spam_score = 0
    for fname in spam_files:
        if not (email_base / fname).exists():
            spam_score += 5
    details.append({"item": "spam/newsletter emails deleted", "score": spam_score, "max_score": 10, "passed": spam_score == 10, "reason": f"Deleted {spam_score//5}/2 files"})
    total += spam_score

    # ---- 6. Read status of processed emails (10 pts) ----
    read_status_ok = True
    for eid, expected in [("email_001", True), ("email_002", True)]:
        e_path = email_base / f"{eid}.json"
        if e_path.is_file():
            with open(e_path, "r", encoding="utf-8") as f:
                em = json.load(f)
            if em.get("has_read") != expected:
                read_status_ok = False
                break
        else:
            read_status_ok = False
            break
    if read_status_ok:
        details.append({"item": "email_001 & email_002 marked as read", "score": 10, "max_score": 10, "passed": True, "reason": "Both have has_read=True"})
        total += 10
    else:
        details.append({"item": "email_001 & email_002 marked as read", "score": 0, "max_score": 10, "passed": False, "reason": "One or both missing or not marked read"})

    # ---- 7. Distractor not modified (5 pts) ----
    email_007_path = email_base / "email_007.json"
    if email_007_path.is_file():
        try:
            with open(email_007_path, "r", encoding="utf-8") as f:
                em7 = json.load(f)
            if em7.get("folder") == "inbox" and em7.get("has_read") == True:
                details.append({"item": "distractor email_007 unchanged", "score": 5, "max_score": 5, "passed": True, "reason": "Folder=inbox, has_read=True"})
                total += 5
            else:
                details.append({"item": "distractor email_007 unchanged", "score": 0, "max_score": 5, "passed": False, "reason": f"Modified: folder={em7.get('folder')}, has_read={em7.get('has_read')}"})
        except:
            details.append({"item": "distractor email_007 unchanged", "score": 0, "max_score": 5, "passed": False, "reason": "Unreadable JSON"})
    else:
        details.append({"item": "distractor email_007 unchanged", "score": 0, "max_score": 5, "passed": False, "reason": "File deleted or missing"})

    # Write score
    result = {"total_score": min(total, 100), "details": details}
    output_path = BASE / "workplace_score.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Total: {result['total_score']}/100")
    return result["total_score"]

if __name__ == "__main__":
    score()
