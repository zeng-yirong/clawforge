"""
Verifier for wp_mail_client_envs__027
Checks that the agent has correctly:
  1. Created ops/todos.json with 3 TODO items (title, description) for the high/unread mails.
  2. Created ops/replies.json with 3 reply drafts (to, subject, body with exact phrase).
  3. Created ops/processed.json with the 3 mail IDs.
All scores are derived objectively from the file contents.
"""
import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # ------------------------------------------------------------------
    # 1. Check ops/ directory exists (5 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        results.append({"item": "ops/ directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found ops/ directory"})
        total_score += 5
    else:
        results.append({"item": "ops/ directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing ops/ directory"})
        # If ops/ missing, all subsequent checks will fail, but we still attempt to load files with fallback
        print(json.dumps({"total_score": total_score, "details": results}, indent=2))
        # Early exit with partial score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": results}, f)
        return

    # ------------------------------------------------------------------
    # Helper to load JSON from absolute path inside workspace
    def load_json(name):
        path = os.path.join(ops_dir, name)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # 2. Check each file exists and is valid JSON (5 points each)
    todos_data = load_json("todos.json")
    replies_data = load_json("replies.json")
    processed_data = load_json("processed.json")

    for fname, data, label in [
        ("todos.json", todos_data, "ops/todos.json exists and valid JSON"),
        ("replies.json", replies_data, "ops/replies.json exists and valid JSON"),
        ("processed.json", processed_data, "ops/processed.json exists and valid JSON"),
    ]:
        if data is not None:
            results.append({"item": label, "score": 5, "max_score": 5, "passed": True, "reason": f"{fname} present and parseable"})
            total_score += 5
        else:
            results.append({"item": label, "score": 0, "max_score": 5, "passed": False, "reason": f"{fname} missing or invalid JSON"})

    # If any of the three files missing, we still continue but most checks will fail
    # ------------------------------------------------------------------
    # 3. Validate todos.json (15 points for count, 15 for structure)
    if isinstance(todos_data, list):
        todo_count = len(todos_data)
        if todo_count == 3:
            results.append({"item": "todos.json contains exactly 3 items", "score": 15, "max_score": 15, "passed": True, "reason": "Found 3 TODO items"})
            total_score += 15
        else:
            results.append({"item": "todos.json contains exactly 3 items", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected 3, got {todo_count}"})
        # Check each item has title and description (non-empty)
        struct_ok = True
        for idx, todo in enumerate(todos_data):
            if not isinstance(todo, dict) or "title" not in todo or "description" not in todo:
                struct_ok = False
                break
            if not todo["title"] or not todo["description"]:
                struct_ok = False
                break
        if struct_ok:
            results.append({"item": "Each TODO has non-empty 'title' and 'description'", "score": 15, "max_score": 15, "passed": True, "reason": "All TODO items contain required fields"})
            total_score += 15
        else:
            results.append({"item": "Each TODO has non-empty 'title' and 'description'", "score": 0, "max_score": 15, "passed": False, "reason": "One or more TODO items missing or empty title/description"})
    else:
        results.append({"item": "todos.json contains exactly 3 items", "score": 0, "max_score": 15, "passed": False, "reason": "todos.json is not a list"})
        results.append({"item": "Each TODO has non-empty 'title' and 'description'", "score": 0, "max_score": 15, "passed": False, "reason": "todos.json is not a list, cannot check structure"})

    # ------------------------------------------------------------------
    # 4. Validate replies.json (10 points for count, 10 for content)
    if isinstance(replies_data, list):
        reply_count = len(replies_data)
        if reply_count == 3:
            results.append({"item": "replies.json contains exactly 3 items", "score": 10, "max_score": 10, "passed": True, "reason": "Found 3 reply drafts"})
            total_score += 10
        else:
            results.append({"item": "replies.json contains exactly 3 items", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 3, got {reply_count}"})
        # Check each reply has 'to', 'subject', and body == exact string
        body_ok = True
        fields_ok = True
        for idx, reply in enumerate(replies_data):
            if not isinstance(reply, dict):
                fields_ok = False
                break
            if not all(k in reply for k in ("to", "subject", "body")):
                fields_ok = False
                break
            # Body must be exactly the required phrase
            if reply.get("body") != "Thanks for your email. I will get back to you soon.":
                body_ok = False
        if fields_ok:
            results.append({"item": "Each reply has 'to', 'subject', 'body' fields", "score": 5, "max_score": 5, "passed": True, "reason": "All replies have required fields"})
            total_score += 5
        else:
            results.append({"item": "Each reply has 'to', 'subject', 'body' fields", "score": 0, "max_score": 5, "passed": False, "reason": "One or more replies missing required fields"})
        if body_ok:
            results.append({"item": "Each reply body matches the exact required phrase", "score": 5, "max_score": 5, "passed": True, "reason": "All reply bodies are correct"})
            total_score += 5
        else:
            results.append({"item": "Each reply body matches the exact required phrase", "score": 0, "max_score": 5, "passed": False, "reason": "One or more reply bodies differ from required string"})
    else:
        results.append({"item": "replies.json contains exactly 3 items", "score": 0, "max_score": 10, "passed": False, "reason": "replies.json is not a list"})
        results.append({"item": "Each reply has 'to', 'subject', 'body' fields", "score": 0, "max_score": 5, "passed": False, "reason": "replies.json is not a list"})
        results.append({"item": "Each reply body matches the exact required phrase", "score": 0, "max_score": 5, "passed": False, "reason": "replies.json is not a list"})

    # ------------------------------------------------------------------
    # 5. Validate processed.json (15 points for correct IDs)
    # Expected mail IDs: email_002, email_005, email_008 (the three high, unread)
    expected_ids = {"email_002", "email_005", "email_008"}
    if isinstance(processed_data, list):
        actual_ids = set(item.strip() if isinstance(item, str) else str(item) for item in processed_data)
        if actual_ids == expected_ids:
            results.append({"item": "processed.json contains exactly the 3 correct mail IDs", "score": 15, "max_score": 15, "passed": True, "reason": "IDs match expected set"})
            total_score += 15
        else:
            results.append({"item": "processed.json contains exactly the 3 correct mail IDs", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {sorted(expected_ids)}, got {sorted(actual_ids)}"})
    else:
        results.append({"item": "processed.json contains exactly the 3 correct mail IDs", "score": 0, "max_score": 15, "passed": False, "reason": "processed.json is not a list"})

    # ------------------------------------------------------------------
    # Ensure total_score does not exceed max_total (in case of rounding)
    total_score = min(total_score, max_total)

    # Write result
    output = {
        "total_score": total_score,
        "details": results
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
