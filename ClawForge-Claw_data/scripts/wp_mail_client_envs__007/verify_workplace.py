import os
import sys
import json

def verify(workspace):
    details = []
    total_score = 0

    # --- 1. Check required directories exist (10 points) ---
    ops_path = os.path.join(workspace, "ops")
    data_path = os.path.join(workspace, "data")
    emails_path = os.path.join(data_path, "emails")
    exists_ops = os.path.isdir(ops_path)
    exists_data = os.path.isdir(data_path)
    exists_emails = os.path.isdir(emails_path)
    dir_score = 0
    if exists_ops and exists_data and exists_emails:
        dir_score = 10
    details.append({
        "item": "Required directories (ops, data, data/emails)",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": "All required directories exist" if dir_score == 10 else "Missing one or more required directories"
    })
    total_score += dir_score

    # --- 2. Check output files exist and are parseable (10 points) ---
    replies_path = os.path.join(ops_path, "replies.json")
    todos_path = os.path.join(ops_path, "todos.json")
    archived_path = os.path.join(ops_path, "archived.txt")

    files_ok = True
    parse_errors = []
    replies_data = None
    todos_data = None
    archived_lines = None

    if not os.path.isfile(replies_path):
        files_ok = False
        parse_errors.append("ops/replies.json not found")
    else:
        try:
            with open(replies_path, "r") as f:
                replies_data = json.load(f)
            if not isinstance(replies_data, list):
                raise ValueError("replies.json must be a list")
        except Exception as e:
            files_ok = False
            parse_errors.append(f"replies.json parse error: {e}")

    if not os.path.isfile(todos_path):
        files_ok = False
        parse_errors.append("ops/todos.json not found")
    else:
        try:
            with open(todos_path, "r") as f:
                todos_data = json.load(f)
            if not isinstance(todos_data, list):
                raise ValueError("todos.json must be a list")
        except Exception as e:
            files_ok = False
            parse_errors.append(f"todos.json parse error: {e}")

    if not os.path.isfile(archived_path):
        files_ok = False
        parse_errors.append("ops/archived.txt not found")
    else:
        with open(archived_path, "r") as f:
            archived_lines = [line.strip() for line in f if line.strip()]

    if files_ok:
        format_score = 10
        reason = "All three output files exist and are parseable"
    else:
        format_score = 0
        reason = "; ".join(parse_errors)
    details.append({
        "item": "Output files exist and parseable",
        "score": format_score,
        "max_score": 10,
        "passed": format_score == 10,
        "reason": reason
    })
    total_score += format_score

    if not files_ok:
        # cannot proceed to content checks
        final_score = min(total_score, 100)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        return

    # --- 3. Verify replies.json content (30 points) ---
    # Expected replies: msg001 and msg002 (both high importance, unread, John's inbox)
    # Each reply must contain at least: email_id, to (recipient email), subject, body
    # We allow extra fields; we check required keys.
    expected_reply_ids = {"msg001", "msg002"}
    actual_reply_ids = set()
    reply_score = 0
    # Check each reply item
    valid_replies = 0
    for reply in replies_data:
        if not isinstance(reply, dict):
            continue
        # Must contain email_id
        eid = reply.get("email_id") or reply.get("id") or reply.get("emailId")
        if eid is None:
            continue
        # Must contain to, subject, body
        to = reply.get("to") or reply.get("recipient") or reply.get("email")
        subj = reply.get("subject") or reply.get("title")
        body = reply.get("body") or reply.get("text")
        if not all([to, subj, body]):
            continue
        actual_reply_ids.add(eid)

    # Check that we have exactly the two expected ids, and no extra from other accounts
    if actual_reply_ids == expected_reply_ids:
        reply_score = 30
        reason = f"Exactly the two expected replies (msg001, msg002) found."
    elif expected_reply_ids.issubset(actual_reply_ids) and len(actual_reply_ids) == 2:
        reply_score = 30
        reason = "Replies contain correct IDs but may have extra fields."
    elif len(actual_reply_ids.intersection(expected_reply_ids)) == 2:
        reply_score = 20
        reason = "Replies contain correct IDs but there are extra/missing entries."
    elif len(actual_reply_ids.intersection(expected_reply_ids)) == 1:
        reply_score = 10
        reason = "Only one of two expected replies present."
    else:
        reply_score = 0
        reason = f"No expected replies found. Found: {actual_reply_ids}"

    details.append({
        "item": "Replies content (email IDs: msg001, msg002)",
        "score": reply_score,
        "max_score": 30,
        "passed": reply_score == 30,
        "reason": reason
    })
    total_score += reply_score

    # --- 4. Verify todos.json content (30 points) ---
    # Expected TODO: from msg003 (unread high importance with 'action' label)
    expected_todo_ids = {"msg003"}
    actual_todo_ids = set()
    todo_score = 0
    for todo in todos_data:
        if not isinstance(todo, dict):
            continue
        eid = todo.get("email_id") or todo.get("id") or todo.get("emailId")
        if eid is None:
            continue
        title = todo.get("title") or todo.get("task") or todo.get("description")
        if not title:
            continue
        actual_todo_ids.add(eid)

    if actual_todo_ids == expected_todo_ids:
        todo_score = 30
        reason = "Correct TODO extracted (msg003)."
    elif expected_todo_ids.issubset(actual_todo_ids) and len(actual_todo_ids) == 1:
        todo_score = 30
        reason = "TODO from msg003 present."
    elif len(actual_todo_ids.intersection(expected_todo_ids)) == 1:
        todo_score = 20
        reason = "TODO contains msg003 but may have extra entries."
    else:
        todo_score = 0
        reason = f"No expected TODO found. Found: {actual_todo_ids}"

    details.append({
        "item": "TODO extraction (email ID: msg003)",
        "score": todo_score,
        "max_score": 30,
        "passed": todo_score == 30,
        "reason": reason
    })
    total_score += todo_score

    # --- 5. Verify archived.txt content (20 points) ---
    # Expected archived IDs: msg006 (read low importance), msg007 (spam)
    # Also note: msg005 is unread low, not to be archived; msg004 is read high, not to be archived.
    expected_archived_ids = {"msg006", "msg007"}
    actual_archived_ids = set(archived_lines) if archived_lines else set()
    archived_score = 0
    if actual_archived_ids == expected_archived_ids:
        archived_score = 20
        reason = "Archived list matches exactly (msg006, msg007)."
    elif expected_archived_ids.issubset(actual_archived_ids) and len(actual_archived_ids) == 2:
        archived_score = 20
        reason = "Correct two archived emails present."
    elif expected_archived_ids.issubset(actual_archived_ids) and len(actual_archived_ids) > 2:
        archived_score = 10
        reason = f"Extra archived emails: {actual_archived_ids - expected_archived_ids}"
    elif len(actual_archived_ids.intersection(expected_archived_ids)) >= 1:
        archived_score = 10
        reason = "Only partially correct archived emails."
    else:
        archived_score = 0
        reason = f"No expected archived emails. Found: {actual_archived_ids}"

    details.append({
        "item": "Archived email IDs (msg006, msg007)",
        "score": archived_score,
        "max_score": 20,
        "passed": archived_score == 20,
        "reason": reason
    })
    total_score += archived_score

    # Ensure total score <= 100
    final_score = min(total_score, 100)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
