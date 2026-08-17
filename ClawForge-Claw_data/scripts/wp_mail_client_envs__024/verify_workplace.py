import json
import os
import sys
import re

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
    global total_score
    total_score += score

# 1. Check ops directory exists
ops_dir = os.path.join(workspace, "ops")
if os.path.isdir(ops_dir):
    add_item("ops directory exists", 10, 10, True, "ops/ directory present")
else:
    add_item("ops directory exists", 0, 10, False, "ops/ directory missing")
    # Cannot proceed further
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 2. Check reclassify.json exists and is valid JSON
reclassify_path = os.path.join(ops_dir, "reclassify.json")
if not os.path.isfile(reclassify_path):
    add_item("reclassify.json exists", 0, 15, False, "File not found")
    # skip rest reclassify checks
    reclassify_data = None
else:
    try:
        with open(reclassify_path, "r") as f:
            reclassify_data = json.load(f)
        add_item("reclassify.json valid JSON", 5, 5, True, "Parsed successfully")
    except (json.JSONDecodeError, Exception):
        add_item("reclassify.json valid JSON", 0, 5, False, "Invalid JSON")
        reclassify_data = None

# 3. Check todos.json exists and is valid JSON
todos_path = os.path.join(ops_dir, "todos.json")
if not os.path.isfile(todos_path):
    add_item("todos.json exists", 0, 10, False, "File not found")
    todos_data = None
else:
    try:
        with open(todos_path, "r") as f:
            todos_data = json.load(f)
        add_item("todos.json valid JSON", 5, 5, True, "Parsed successfully")
    except (json.JSONDecodeError, Exception):
        add_item("todos.json valid JSON", 0, 5, False, "Invalid JSON")
        todos_data = None

# 4. Validate reclassify.json content
# Expected: list of dicts with keys id, current_folder, recommended_folder
# Correct entries: email_001 (spam -> work), email_002 (spam -> work)
# No other entries allowed
if reclassify_data is not None:
    if not isinstance(reclassify_data, list):
        add_item("reclassify.json is a list", 0, 10, False, f"Expected list, got {type(reclassify_data).__name__}")
        reclassify_valid = False
    else:
        reclassify_valid = True
        # Check each item has required fields
        for i, item in enumerate(reclassify_data):
            if not isinstance(item, dict):
                add_item(f"reclassify item {i} is dict", 0, 5, False, f"Item {i} is not a dict")
                reclassify_valid = False
                continue
            for key in ["id", "current_folder", "recommended_folder"]:
                if key not in item:
                    add_item(f"reclassify item {i} has '{key}'", 0, 5, False, f"Missing '{key}'")
                    reclassify_valid = False
        if reclassify_valid:
            # Build dict of expected entries
            expected_entries = {
                "email_001": {"current_folder": "spam", "recommended_folder": "work"},
                "email_002": {"current_folder": "spam", "recommended_folder": "work"}
            }
            actual_entries = {item["id"]: item for item in reclassify_data if isinstance(item, dict) and "id" in item}
            # Check no extra ids
            extra_ids = set(actual_entries.keys()) - set(expected_entries.keys())
            if extra_ids:
                add_item("reclassify no extra entries", 0, 10, False, f"Unexpected ids: {extra_ids}")
                reclassify_valid = False
            else:
                add_item("reclassify no extra entries", 10, 10, True, "All ids are expected")
            # Check expected entries present and fields match
            all_match = True
            for eid, efields in expected_entries.items():
                if eid not in actual_entries:
                    add_item(f"reclassify includes {eid}", 0, 10, False, f"Missing {eid}")
                    all_match = False
                    continue
                aitem = actual_entries[eid]
                for field, expected_val in efields.items():
                    if aitem.get(field) != expected_val:
                        add_item(f"reclassify {eid}.{field}", 0, 10, False, f"Expected '{expected_val}', got '{aitem.get(field)}'")
                        all_match = False
            if all_match:
                add_item("reclassify all fields correct", 30, 30, True, "All expected entries and fields match")
            else:
                # Already added partial scores
                pass
    # If reclassify list had structural issues, give 0 for content part
    if not reclassify_valid:
        # deduct remaining content points (we already added some, but we can only assign 0 for subsequent)
        # We'll add a composite item to cover the missing points
        pass

# 5. Validate todos.json content
# Expected: list of dicts with id and subject
# Only email_001 (since it contains 'action required' in body)
expected_todos = [{"id": "email_001", "subject": "New project proposal - action required"}]
if todos_data is not None:
    if not isinstance(todos_data, list):
        add_item("todos.json is a list", 0, 10, False, f"Expected list, got {type(todos_data).__name__}")
    else:
        todos_valid = True
        # Check structure
        for i, item in enumerate(todos_data):
            if not isinstance(item, dict):
                add_item(f"todos item {i} is dict", 0, 5, False, f"Item {i} not dict")
                todos_valid = False
                continue
            for key in ["id", "subject"]:
                if key not in item:
                    add_item(f"todos item {i} has '{key}'", 0, 5, False, f"Missing '{key}'")
                    todos_valid = False
        if todos_valid:
            # Compare with expected
            actual_todos = {item["id"]: item for item in todos_data if isinstance(item, dict) and "id" in item}
            # Check no extra
            extra = set(actual_todos.keys()) - set(e["id"] for e in expected_todos)
            if extra:
                add_item("todos no extra entries", 0, 5, False, f"Unexpected ids: {extra}")
            else:
                add_item("todos no extra entries", 5, 5, True, "Only expected ids")
            # Check email_001 present and subject correct
            if "email_001" in actual_todos:
                if actual_todos["email_001"].get("subject") == "New project proposal - action required":
                    add_item("todos email_001 subject correct", 10, 10, True, "Subject matches")
                else:
                    add_item("todos email_001 subject correct", 0, 10, False, f"Subject mismatch: {actual_todos['email_001'].get('subject')}")
            else:
                add_item("todos includes email_001", 0, 10, False, "Missing email_001")
        else:
            # Deduct remaining points
            pass
        # Add a composite for correct content if not already full score
        # We'll just leave the above items

# Compute final total (capped at 100)
total_score = min(total_score, 100)
result = {"total_score": total_score, "details": score_details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

# Print for debug (optional)
print(f"Total score: {total_score}")
