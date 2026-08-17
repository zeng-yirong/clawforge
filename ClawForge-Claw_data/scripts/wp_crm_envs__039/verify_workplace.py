import json
import os
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

def load_json(rel_path):
    full = WORKSPACE / rel_path
    if not full.exists():
        return None
    with open(full, "r") as f:
        return json.load(f)

def main():
    details = []
    total = 0
    max_total = 100

    # 1. File existence (5)
    file_path = WORKSPACE / "ops" / "contact_updates.json"
    if file_path.exists():
        details.append({"item": "ops/contact_updates.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "File found"})
        total += 5
    else:
        details.append({"item": "ops/contact_updates.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "File missing"})
        # If missing, cannot check further content
        write_score(total, details)
        return

    # 2. Valid JSON (5)
    try:
        data = json.loads(file_path.read_text())
        details.append({"item": "Valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "Parsed OK"})
        total += 5
    except Exception as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": str(e)})
        write_score(total, details)
        return

    # 3. Structure check (10)
    if not isinstance(data, dict):
        details.append({"item": "Structure: top-level dict", "score": 0, "max_score": 10, "passed": False, "reason": "Top-level is not a dict"})
        write_score(total, details)
        return
    required_keys = {"create_reminders", "add_tags"}
    if not required_keys.issubset(data.keys()):
        missing = required_keys - data.keys()
        details.append({"item": "Structure: contains create_reminders and add_tags", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing keys: {missing}"})
        write_score(total, details)
        return
    if not isinstance(data["create_reminders"], list) or not isinstance(data["add_tags"], list):
        details.append({"item": "Structure: both lists", "score": 0, "max_score": 10, "passed": False, "reason": "create_reminders or add_tags is not a list"})
        write_score(total, details)
        return
    details.append({"item": "Structure: correct keys and types", "score": 10, "max_score": 10, "passed": True, "reason": "OK"})
    total += 10

    # Load reference data
    contacts = load_json("data/contacts.json")
    reminders = load_json("data/reminders/reminders.json")
    tag_defs = load_json("data/tags/tag_definitions.json")
    current_date_file = WORKSPACE / "current_date.txt"
    if contacts is None or reminders is None or tag_defs is None or not current_date_file.exists():
        details.append({"item": "Reference data available", "score": 0, "max_score": 0, "passed": False, "reason": "Missing reference data in workspace — cannot verify. Adjust workspace path."})
        write_score(total, details)
        return

    with open(current_date_file, "r") as f:
        current_date_str = f.read().strip()
    current_year = datetime.strptime(current_date_str, "%Y-%m-%d").year

    # Build expected create_reminders
    contacts_list = contacts["contacts"]
    reminders_list = reminders["reminders"]
    # Build a set of contact_ids that have at least one enabled reminder
    enabled_reminder_ids = {r["contact_id"] for r in reminders_list if r.get("enabled") is True}

    expected_create_reminders = []
    expected_add_tags = []

    for c in contacts_list:
        cid = c["contact_id"]
        ctype = c["contact_type"]
        folder = c["folder"]
        birthday = c.get("birthday", "")
        # birthday format: YYYY-MM-DD
        if not birthday or len(birthday) != 10:
            continue
        _, month, day = birthday.split("-")
        reminder_date = f"{current_year}-{month}-{day}"

        # Rule 1: business, not inactive, missing enabled reminder
        if ctype == "business" and folder != "inactive":
            if cid not in enabled_reminder_ids:
                expected_create_reminders.append({"contact_id": cid, "reminder_date": reminder_date})
                expected_add_tags.append({"contact_id": cid, "tag": "birthday-pending"})
        # Rule 2: inactive and personal
        if folder == "inactive" and ctype == "personal":
            expected_add_tags.append({"contact_id": cid, "tag": "inactive-personal"})

    # Sort expected for comparison (order independent)
    def sort_key(d):
        return (d.get("contact_id", ""), d.get("reminder_date", ""), d.get("tag", ""))
    expected_create_reminders.sort(key=sort_key)
    expected_add_tags.sort(key=sort_key)

    agent_create = data["create_reminders"]
    agent_add = data["add_tags"]

    # 4. create_reminders correctness (35)
    score_create = 0
    max_create = 35
    reasons_create = []

    # Check length first
    if len(agent_create) != len(expected_create_reminders):
        reasons_create.append(f"Expected {len(expected_create_reminders)} reminder(s), got {len(agent_create)}")
    else:
        # Deep compare after sorting
        agent_sorted = sorted(agent_create, key=lambda x: (x.get("contact_id",""), x.get("reminder_date","")))
        match = True
        for exp, act in zip(expected_create_reminders, agent_sorted):
            if exp["contact_id"] != act.get("contact_id") or exp["reminder_date"] != act.get("reminder_date"):
                match = False
                reasons_create.append(f"Mismatch: expected {exp}, got {{'contact_id': '{act.get('contact_id')}', 'reminder_date': '{act.get('reminder_date')}'}}")
                break
        if match:
            score_create = max_create
        else:
            score_create = max_create // 2  # partial for correct length but wrong content

    if not reasons_create:
        reasons_create.append("All reminder entries correct")
    details.append({
        "item": "create_reminders correctness",
        "score": score_create,
        "max_score": max_create,
        "passed": score_create == max_create,
        "reason": "; ".join(reasons_create)
    })
    total += score_create

    # 5. add_tags correctness (35)
    score_add = 0
    max_add = 35
    reasons_add = []

    # Check tag definitions exist (penalty for unknown tags)
    known_tags = {t["name"] for t in tag_defs["tag_definitions"]}
    for entry in agent_add:
        tagname = entry.get("tag", "")
        if tagname and tagname not in known_tags:
            reasons_add.append(f"Tag '{tagname}' is not defined in tag_definitions")
            score_add -= 3  # penalty per unknown tag (capped)

    if len(agent_add) != len(expected_add_tags):
        reasons_add.append(f"Expected {len(expected_add_tags)} tag operation(s), got {len(agent_add)}")
    else:
        agent_sorted = sorted(agent_add, key=lambda x: (x.get("contact_id",""), x.get("tag","")))
        match = True
        for exp, act in zip(expected_add_tags, agent_sorted):
            if exp["contact_id"] != act.get("contact_id") or exp["tag"] != act.get("tag"):
                match = False
                reasons_add.append(f"Mismatch: expected {exp}, got {{'contact_id': '{act.get('contact_id')}', 'tag': '{act.get('tag')}'}}")
                break
        if match:
            score_add = max_add
        else:
            score_add = max_add // 2

    # cap and ensure non-negative
    score_add = max(0, min(score_add, max_add))
    if not reasons_add:
        reasons_add.append("All tag entries correct")
    details.append({
        "item": "add_tags correctness",
        "score": score_add,
        "max_score": max_add,
        "passed": score_add == max_add,
        "reason": "; ".join(reasons_add)
    })
    total += score_add

    # Summary
    write_score(total, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    output_path = WORKSPACE / "workplace_score.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {output_path}: {total}/100")

if __name__ == "__main__":
    main()
