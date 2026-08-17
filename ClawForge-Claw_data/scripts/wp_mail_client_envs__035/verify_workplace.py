#!/usr/bin/env python3
import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_item(name, score, max_score, passed, reason):
    score_details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# ----------------------------------------------------------------------
# 1. Check required directory structure (10 points)
# ----------------------------------------------------------------------
try:
    emdir = os.path.join(workspace, "data", "emails")
    if os.path.isdir(emdir):
        add_item("data/emails directory exists", 10, 10, True, "Found")
    else:
        add_item("data/emails directory exists", 0, 10, False, "Missing")
except Exception as e:
    add_item("data/emails directory exists", 0, 10, False, f"Error: {e}")

# ----------------------------------------------------------------------
# 2. Check todos.json exists and is valid JSON (10 points)
# ----------------------------------------------------------------------
todos_path = os.path.join(workspace, "todos.json")
if os.path.exists(todos_path):
    try:
        with open(todos_path, "r") as f:
            todos_data = json.load(f)
        # Must be a list or dict with "todos" key; allow either
        if isinstance(todos_data, list):
            todos_list = todos_data
        elif isinstance(todos_data, dict) and "todos" in todos_data:
            todos_list = todos_data["todos"]
        else:
            todos_list = None
        if todos_list is None:
            add_item("todos.json has valid structure", 0, 10, False, "Not a list or missing 'todos' key")
        else:
            # Check each entry has email_id and todo
            valid = True
            for item in todos_list:
                if not isinstance(item, dict) or "email_id" not in item or "todo" not in item:
                    valid = False
                    break
            if valid:
                add_item("todos.json valid JSON and structure", 10, 10, True, "Format OK")
            else:
                add_item("todos.json valid JSON and structure", 0, 10, False, "Entries missing email_id or todo")
    except json.JSONDecodeError:
        add_item("todos.json valid JSON and structure", 0, 10, False, "Invalid JSON")
    except Exception as e:
        add_item("todos.json valid JSON and structure", 0, 10, False, f"Error: {e}")
else:
    add_item("todos.json valid JSON and structure", 0, 10, False, "File not found")

# ----------------------------------------------------------------------
# 3. Check todos.json content correctness (30 points)
# ----------------------------------------------------------------------
if os.path.exists(todos_path):
    try:
        with open(todos_path, "r") as f:
            todos_data = json.load(f)
        if isinstance(todos_data, list):
            todos_list = todos_data
        elif isinstance(todos_data, dict) and "todos" in todos_data:
            todos_list = todos_data["todos"]
        else:
            todos_list = []
        
        # Expected TODO items (order irrelevant)
        expected = [
            {"email_id": "email-001", "todo": "Prepare Q3 budget report"},
            {"email_id": "email-002", "todo": "Schedule team meeting"}
        ]
        # Build lookup from actual
        actual = {item["email_id"]: item["todo"] for item in todos_list if isinstance(item, dict) and "email_id" in item and "todo" in item}
        passed = True
        reason_parts = []
        # Check both expected are present with correct text
        for exp in expected:
            eid = exp["email_id"]
            if eid not in actual:
                passed = False
                reason_parts.append(f"Missing {eid}")
            elif actual[eid] != exp["todo"]:
                passed = False
                reason_parts.append(f"{eid} has '{actual[eid]}' instead of '{exp['todo']}'")
        # Check no extra entries (optional, but can penalize)
        extra = [eid for eid in actual if eid not in [exp["email_id"] for exp in expected]]
        if extra:
            passed = False
            reason_parts.append(f"Extra entries: {extra}")
        if passed:
            add_item("todos.json content correct", 30, 30, True, "All expected TODO items found with correct text")
        else:
            reason = "; ".join(reason_parts) if reason_parts else "Content mismatch"
            add_item("todos.json content correct", 0, 30, False, reason)
    except Exception as e:
        add_item("todos.json content correct", 0, 30, False, f"Error: {e}")
else:
    add_item("todos.json content correct", 0, 30, False, "File not found, cannot check content")

# ----------------------------------------------------------------------
# 4. Check target emails modifications (30 points: 15 each)
# ----------------------------------------------------------------------
# Expected initial states
initial_states = {
    "email-001": {"has_read": False, "folder": "inbox"},
    "email-002": {"has_read": False, "folder": "inbox"},
    "email-003": {"has_read": False, "folder": "work"},
    "email-004": {"has_read": True, "folder": "inbox"},
    "email-005": {"has_read": False, "folder": "work"}
}
target_ids = ["email-001", "email-002"]

def load_email(eid):
    path = os.path.join(workspace, "data", "emails", f"{eid}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

# Check each target email
for eid in target_ids:
    email = load_email(eid)
    if email is None:
        add_item(f"Email {eid} modification", 0, 15, False, "File missing")
        continue
    has_read_ok = email.get("has_read") is True
    folder_ok = email.get("folder") == "archive"
    if has_read_ok and folder_ok:
        add_item(f"Email {eid} modification", 15, 15, True, "has_read=True, folder='archive'")
    elif not has_read_ok and not folder_ok:
        add_item(f"Email {eid} modification", 0, 15, False, f"has_read={email.get('has_read')}, folder={email.get('folder')}")
    elif not has_read_ok:
        add_item(f"Email {eid} modification", 5, 15, False, f"folder='archive' ok, but has_read={email.get('has_read')}")
    else:
        add_item(f"Email {eid} modification", 10, 15, False, f"has_read=True ok, but folder={email.get('folder')}")

# ----------------------------------------------------------------------
# 5. Check that non-target emails were NOT changed (20 points)
# ----------------------------------------------------------------------
non_target_ids = [eid for eid in initial_states if eid not in target_ids]
non_target_ok = True
errors = []
for eid in non_target_ids:
    email = load_email(eid)
    if email is None:
        errors.append(f"{eid} missing")
        non_target_ok = False
        continue
    exp = initial_states[eid]
    hr_change = email.get("has_read") != exp["has_read"]
    folder_change = email.get("folder") != exp["folder"]
    if hr_change or folder_change:
        non_target_ok = False
        changes = []
        if hr_change:
            changes.append(f"has_read changed from {exp['has_read']} to {email.get('has_read')}")
        if folder_change:
            changes.append(f"folder changed from {exp['folder']} to {email.get('folder')}")
        errors.append(f"{eid}: {'; '.join(changes)}")
if non_target_ok:
    add_item("Non-target emails unchanged", 20, 20, True, "All non-target emails preserved initial has_read and folder")
else:
    add_item("Non-target emails unchanged", 0, 20, False, " | ".join(errors))

# ----------------------------------------------------------------------
# Compute total
# ----------------------------------------------------------------------
total_score = sum(item["score"] for item in score_details)
# Ensure integer
total_score = min(100, max(0, total_score))

result = {
    "total_score": total_score,
    "details": score_details
}

output_path = os.path.join(workspace, "workplace_score.json")
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)
