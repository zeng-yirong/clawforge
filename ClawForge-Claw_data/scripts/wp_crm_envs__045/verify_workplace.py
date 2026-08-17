import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(workspace, rel_path)
    if not os.path.exists(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

def main():
    details = []
    total = 0

    # ----- 1. Directory exists -----
    reminders_dir = os.path.join(workspace, "reminders")
    dir_exists = os.path.isdir(reminders_dir)
    details.append({
        "item": "reminders directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Directory found" if dir_exists else "reminders/ directory missing"
    })

    # ----- 2. Output file exists -----
    out_path = os.path.join(workspace, "reminders", "new_birthday_reminders.json")
    file_exists = os.path.isfile(out_path)
    details.append({
        "item": "new_birthday_reminders.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "reminders/new_birthday_reminders.json not found"
    })
    if not file_exists:
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # ----- 3. JSON validity -----
    try:
        with open(out_path, "r") as f:
            output = json.load(f)
        json_valid = True
    except Exception as e:
        json_valid = False
        details.append({
            "item": "output file is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    details.append({
        "item": "output file is valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON"
    })

    # ----- 4. Output is a list -----
    is_list = isinstance(output, list)
    details.append({
        "item": "output is a JSON array",
        "score": 5 if is_list else 0,
        "max_score": 5,
        "passed": is_list,
        "reason": "Array detected" if is_list else "Root element is not a list"
    })
    if not is_list:
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # ----- 5. Load reference data -----
    contacts_data = load_json("data/contacts.json")
    reminders_data = load_json("reminders/reminders.json")
    if contacts_data is None or reminders_data is None:
        details.append({
            "item": "reference data load",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Could not load contacts.json or reminders.json"
        })
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    contacts = contacts_data.get("contacts", [])
    existing_reminders = reminders_data.get("reminders", [])

    # Build expected set of contact_ids that need a new reminder
    expected_ids = set()
    for c in contacts:
        if c.get("contact_type") != "business":
            continue
        bday = c.get("birthday")
        if not bday:
            continue
        month = bday.split("-")[1] if "-" in str(bday) else ""
        if month != "07":
            continue
        # Check if already in existing reminders
        already = any(r.get("contact_id") == c["contact_id"] for r in existing_reminders)
        if not already:
            expected_ids.add(c["contact_id"])

    expected_ids_sorted = sorted(expected_ids)

    # ----- 6. Extract contact_ids from output -----
    output_ids = []
    errors = []
    for i, item in enumerate(output):
        cid = item.get("contact_id") if isinstance(item, dict) else None
        if cid is None:
            errors.append(f"Item {i} missing 'contact_id'")
        else:
            output_ids.append(cid)

    # Check for duplicates in output
    dup_count = len(output_ids) - len(set(output_ids))
    if dup_count > 0:
        errors.append(f"Output contains {dup_count} duplicate contact_id(s)")

    output_ids_sorted = sorted(output_ids)

    # ----- 7. Score correctness -----
    # Compare sorted lists
    matched = output_ids_sorted == expected_ids_sorted
    correct_count = sum(1 for cid in output_ids if cid in expected_ids)
    extra_count = sum(1 for cid in output_ids if cid not in expected_ids)
    missing_count = sum(1 for cid in expected_ids if cid not in output_ids)

    # Detailed field checks for each output item that corresponds to an expected one
    field_issues = []
    for item in output:
        cid = item.get("contact_id")
        if cid not in expected_ids:
            continue
        # Find contact info
        contact = next((c for c in contacts if c["contact_id"] == cid), None)
        if not contact:
            continue
        # Check required fields
        required = ["reminder_id", "contact_id", "reminder_type", "title", "description",
                     "reminder_date", "days_before", "is_recurring", "enabled"]
        for field in required:
            if field not in item:
                field_issues.append(f"Contact {cid} missing field '{field}'")
        # Check specific values
        if item.get("reminder_type") != "birthday":
            field_issues.append(f"Contact {cid} reminder_type should be 'birthday'")
        if item.get("contact_id") != cid:
            field_issues.append(f"Contact {cid} contact_id mismatch")
        if item.get("days_before") != 1:
            field_issues.append(f"Contact {cid} days_before should be 1")
        if item.get("is_recurring") != True:
            field_issues.append(f"Contact {cid} is_recurring should be true")
        if item.get("enabled") != True:
            field_issues.append(f"Contact {cid} enabled should be true")
        # Check title/description pattern
        expected_title = f"{contact['full_name']}'s Birthday"
        expected_desc = f"Birthday reminder for {contact['full_name']}"
        if item.get("title") != expected_title:
            field_issues.append(f"Contact {cid}: title should be '{expected_title}', got '{item.get('title')}'")
        if item.get("description") != expected_desc:
            field_issues.append(f"Contact {cid}: description should be '{expected_desc}', got '{item.get('description')}'")
        # Check reminder_date matches birthday
        if item.get("reminder_date") != contact["birthday"]:
            field_issues.append(f"Contact {cid}: reminder_date should be '{contact['birthday']}', got '{item.get('reminder_date')}'")

    # Scoring
    correctness_score = 0
    if matched and not errors and not field_issues:
        correctness_score = 100  # max for this section is 100 but we allocate 70 out of total 100
        # Actually we have already 10+10+10+5=35 from previous, so 65 left for correctness. We'll allocate 65.
    else:
        # partial
        base = 30  # for having something
        deduction = 0
        if extra_count > 0:
            deduction += 10 * extra_count
        if missing_count > 0:
            deduction += 10 * missing_count
        if dup_count > 0:
            deduction += 10 * dup_count
        if errors:
            deduction += 5 * len(errors)
        if field_issues:
            deduction += 3 * len(field_issues)
        correctness_score = max(0, base - deduction)

    details.append({
        "item": "Correct contact IDs and no extras/missing/duplicates",
        "score": min(35, correctness_score),  # cap at 35
        "max_score": 35,
        "passed": matched and not errors,
        "reason": f"Expected {len(expected_ids)} IDs, got {len(output_ids)}. Correct:{correct_count}, Extra:{extra_count}, Missing:{missing_count}, Dups:{dup_count}. Field issues: {len(field_issues)}"
    })

    # Field correctness (max 30)
    field_score = 0
    if field_issues:
        field_score = max(0, 30 - 3 * len(field_issues))
    else:
        field_score = 30
    details.append({
        "item": "Field values correctness (title, description, reminder_date, type, days_before, recurring, enabled)",
        "score": field_score,
        "max_score": 30,
        "passed": len(field_issues) == 0,
        "reason": f"{len(field_issues)} field issues" if field_issues else "All fields correct"
    })

    total = sum(d["score"] for d in details)
    # Scale to 0-100 (current max possible is 10+10+10+5+35+30 = 100)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
