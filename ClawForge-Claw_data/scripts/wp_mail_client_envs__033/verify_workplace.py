import sys, os, json, re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score = 0
    details = []

    # 1. Check ops directory exists (5 pts)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found ops/"})
        score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing ops/"})

    # 2. Check pending_review.json exists (5 pts)
    target = os.path.join(ops_dir, "pending_review.json")
    if os.path.isfile(target):
        details.append({"item": "pending_review.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "File found"})
        score += 5
    else:
        details.append({"item": "pending_review.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "File not found"})
        # Write partial score and exit so other checks don't crash
        _write_score(score, details)
        return

    # 3. JSON is valid (5 pts)
    try:
        with open(target, "r") as f:
            data = json.load(f)
        details.append({"item": "Valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "parse OK"})
        score += 5
    except Exception as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": str(e)})
        _write_score(score, details)
        return

    # 4. JSON is a list (5 pts)
    if isinstance(data, list):
        details.append({"item": "Result is a list", "score": 5, "max_score": 5, "passed": True, "reason": "list"})
        score += 5
    else:
        details.append({"item": "Result is a list", "score": 0, "max_score": 5, "passed": False, "reason": f"got {type(data).__name__}"})
        _write_score(score, details)
        return

    # 5. Each item has required fields (id, subject, sender_id, urgency) (10 pts)
    required = {"id", "subject", "sender_id", "urgency"}
    all_fields_ok = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            all_fields_ok = False
            break
        missing = required - set(item.keys())
        if missing:
            all_fields_ok = False
            break
        if not isinstance(item["urgency"], bool):
            all_fields_ok = False
            break
    if all_fields_ok:
        details.append({"item": "Fields (id, subject, sender_id, urgency) correct", "score": 10, "max_score": 10, "passed": True, "reason": "all items have required fields and boolean urgency"})
        score += 10
    else:
        details.append({"item": "Fields (id, subject, sender_id, urgency) correct", "score": 0, "max_score": 10, "passed": False, "reason": "missing or invalid fields"})
        _write_score(score, details)
        return

    # 6. Compute expected result from the data files
    # Read contacts
    contacts_path = os.path.join(workspace, "data", "contacts.json")
    if not os.path.isfile(contacts_path):
        details.append({"item": "Compute expected result", "score": 0, "max_score": 70, "passed": False, "reason": "data/contacts.json missing"})
        _write_score(score, details)
        return

    with open(contacts_path) as f:
        contacts_list = json.load(f)
    hr_ids = {c["contact_id"] for c in contacts_list if c["role"] == "HR"}

    # Collect all emails from data/emails/
    emails_dir = os.path.join(workspace, "data", "emails")
    if not os.path.isdir(emails_dir):
        details.append({"item": "Compute expected result", "score": 0, "max_score": 70, "passed": False, "reason": "data/emails/ missing"})
        _write_score(score, details)
        return

    expected = []
    for fname in os.listdir(emails_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(emails_dir, fname)
        try:
            with open(fpath) as f:
                email = json.load(f)
        except:
            continue
        # Apply filters
        if email.get("sender_id") not in hr_ids:
            continue
        if email.get("has_read", False):
            continue
        if email.get("folder") == "archive":
            continue
        if email.get("auto_classify_suggestion") == "spam":
            continue
        importance = email.get("importance")
        if importance not in ("high", "normal"):
            continue
        # Determine urgency
        body = email.get("body", "")
        urgency = bool(re.search(r"urgent", body, re.IGNORECASE))
        expected.append({
            "id": email["id"],
            "subject": email["subject"],
            "sender_id": email["sender_id"],
            "urgency": urgency
        })

    # Sort expected by id for deterministic comparison
    expected.sort(key=lambda x: x["id"])
    # Sort agent result by id
    agent_sorted = sorted(data, key=lambda x: x["id"])

    # 7. Same number of items (30 pts)
    if len(agent_sorted) == len(expected):
        details.append({"item": "Correct number of items", "score": 30, "max_score": 30, "passed": True, "reason": f"found {len(expected)} items"})
        score += 30
    else:
        details.append({"item": "Correct number of items", "score": 0, "max_score": 30, "passed": False, "reason": f"expected {len(expected)} items, got {len(agent_sorted)}"})
        _write_score(score, details)
        return

    # 8. Content matches exactly (20 pts)
    match = True
    for a, e in zip(agent_sorted, expected):
        if a != e:
            match = False
            break
    if match:
        details.append({"item": "Content matches expected", "score": 20, "max_score": 20, "passed": True, "reason": "all fields identical"})
        score += 20
    else:
        details.append({"item": "Content matches expected", "score": 0, "max_score": 20, "passed": False, "reason": "items differ"})
        _write_score(score, details)
        return

    # 9. No extra items (bonus? already covered by count) but add a final sanity (15 pts)
    # Actually we gave full points above; let's add a check for no duplicates (optional, but safe)
    ids_set = {x["id"] for x in agent_sorted}
    if len(ids_set) == len(agent_sorted):
        details.append({"item": "No duplicate IDs", "score": 15, "max_score": 15, "passed": True, "reason": "all IDs unique"})
        score += 15
    else:
        details.append({"item": "No duplicate IDs", "score": 0, "max_score": 15, "passed": False, "reason": "duplicate IDs found"})
        _write_score(score, details)
        return

    _write_score(score, details)

def _write_score(score, details):
    result = {"total_score": score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
