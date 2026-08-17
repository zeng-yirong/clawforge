import json
import os
import sys
from datetime import datetime, timedelta

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # Helper to add score item
    def add_item(item, score, max_score, passed, reason):
        score_details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. Directory and context file existence (10 pts)
    points = 0
    reasons = []
    # Check ops directory
    if os.path.isdir(os.path.join(workspace, "ops")):
        points += 5
        reasons.append("ops/ directory exists")
    else:
        reasons.append("ops/ directory missing")
    # Check context.txt
    context_path = os.path.join(workspace, "ops", "context.txt")
    if os.path.isfile(context_path):
        points += 5
        reasons.append("ops/context.txt exists")
    else:
        reasons.append("ops/context.txt missing")
    total_score += add_item("Directory & context file existence", points, 10, points == 10, "; ".join(reasons))

    # Read context date
    try:
        with open(context_path, "r") as f:
            context_date_str = f.read().strip()
        context_date = datetime.strptime(context_date_str, "%Y-%m-%d")
    except:
        context_date = None

    # 2. Task result file existence and JSON validity (10 pts)
    result_path = os.path.join(workspace, "ops", "task_result.json")
    points = 0
    reasons = []
    if os.path.isfile(result_path):
        points += 5
        reasons.append("task_result.json exists")
        try:
            with open(result_path, "r") as f:
                result = json.load(f)
            points += 5
            reasons.append("Valid JSON")
        except json.JSONDecodeError:
            reasons.append("Invalid JSON content")
            result = None
    else:
        reasons.append("task_result.json missing")
        result = None
    total_score += add_item("Task result file", points, 10, points == 10, "; ".join(reasons))

    if result is None:
        # Cannot proceed further
        add_item("Added tags check", 0, 20, False, "No result file")
        add_item("Birthday reminders check", 0, 15, False, "No result file")
        add_item("Contacts modification check", 0, 15, False, "No result file")
        add_item("Tag definitions check", 0, 10, False, "No result file")
        add_item("Reminders update check", 0, 10, False, "No result file")
        # Write score and exit
        _write_score(total_score, score_details, workspace)
        return

    # 3. Added tags check (20 pts)
    # Expected contact_ids: ct_001 (active, TechCorp business), ct_003 (active, TechCorp business)
    # Exclude ct_002 (inactive), ct_006 (personal folder), ct_009 (duplicate email, but same company/folder? Actually ct_009 also TechCorp business, but duplicate email. The prompt doesn't say to dedup, so agent might include it? To avoid ambiguity, we design that ct_009 is a duplicate (same email, different id). The prompt intent is for "TechCorp business folder active contacts". ct_009 is also business folder and active. However, it's a duplicate; the agent should probably ignore it because it's a duplicate. But to make answer unique, we decide that the agent should treat it as a separate contact? Better to design ct_009 as having a different company (in data we set it as TechCorp). That would be ambiguous. Let's instead modify env_builder to make ct_009 belong to a different company so it's not a TechCorp contact. I'll adjust env_builder: ct_009 company_id = "comp_clientco". But I already wrote env_builder above; need to ensure consistency. I'll update env_builder later. For now, assume ct_009 belongs to ClientCo. So expected added_tags = ["ct_001", "ct_003"].
    expected_added = {"ct_001", "ct_003"}
    added = set(result.get("added_tags", []))
    points = 0
    reasons = []
    correct = added == expected_added
    if correct:
        points = 20
        reasons.append("Exactly contacts ct_001, ct_003 tagged")
    else:
        if added == expected_added:
            points = 20
            reasons.append("Correct set")
        else:
            common = added & expected_added
            points = len(common) * 10
            if points > 20: points = 20
            extra = added - expected_added
            missing = expected_added - added
            if len(common) == 2:
                points = 20
                reasons.append("All expected contacts present")
            elif len(common) == 1:
                points = 10
                reasons.append("Only one expected contact tagged")
            else:
                points = 0
                reasons.append("None of the expected contacts tagged")
            if extra:
                reasons.append(f"Unexpected contacts in added_tags: {extra}")
            if missing:
                reasons.append(f"Missing contacts: {missing}")
    total_score += add_item("Added tags correctness", points, 20, correct, "; ".join(reasons))

    # 4. Birthday reminders check (15 pts)
    # Expected: for contacts ct_001 (Alice Johnson) whose birthday in next month (April 2025)
    # Based on context date 2025-03-20, next month is April. Alice's birthday is 2025-04-15 -> yes.
    # Carol's birthday is 2025-03-10 already passed.
    expected_reminders = [{"contact_id": "ct_001", "reminder_date": "2025-04-15"}]
    actual_reminders = result.get("birthday_reminders", [])
    points = 0
    reasons = []
    # Convert to comparable form (list of dicts with contact_id and reminder_date)
    if not isinstance(actual_reminders, list):
        reasons.append("birthday_reminders is not a list")
        points = 0
    else:
        # Normalize actual: allow extra fields, but check contact_id and reminder_date
        actual_set = frozenset((r.get("contact_id"), r.get("reminder_date")) for r in actual_reminders)
        expected_set = frozenset((r["contact_id"], r["reminder_date"]) for r in expected_reminders)
        if actual_set == expected_set:
            points = 15
            reasons.append("Exactly ct_001 with date 2025-04-15")
        else:
            common = actual_set & expected_set
            points = len(common) * 15
            if points > 15: points = 15
            extra = actual_set - expected_set
            missing = expected_set - actual_set
            if len(common) == 1:
                points = 15
                reasons.append("Correct reminder present")
            else:
                points = 0
                reasons.append("No correct reminder")
            if extra:
                reasons.append(f"Unexpected reminders: {extra}")
            if missing:
                reasons.append(f"Missing reminders: {missing}")
    total_score += add_item("Birthday reminders in result", points, 15, points == 15, "; ".join(reasons))

    # 5. Contacts modification check (15 pts)
    # Check that contacts.json has tags updated for ct_001 and ct_003, and not for ct_002
    contacts_path = os.path.join(workspace, "data", "contacts.json")
    points = 0
    reasons = []
    try:
        with open(contacts_path, "r") as f:
            contacts_data = json.load(f)
        contacts_list = contacts_data.get("contacts", [])
        contact_map = {c["contact_id"]: c for c in contacts_list}

        # ct_001 should have 'key_account' in tags
        ct1 = contact_map.get("ct_001")
        ct3 = contact_map.get("ct_003")
        ct2 = contact_map.get("ct_002")
        ct6 = contact_map.get("ct_006")  # personal folder, should not have tag

        if ct1 and "key_account" in ct1.get("tags", []):
            points += 5
            reasons.append("ct_001 has key_account tag")
        else:
            reasons.append("ct_001 missing key_account tag")

        if ct3 and "key_account" in ct3.get("tags", []):
            points += 5
            reasons.append("ct_003 has key_account tag")
        else:
            reasons.append("ct_003 missing key_account tag")

        # Check ct_002 (inactive) should NOT have key_account
        if ct2 and "key_account" not in ct2.get("tags", []):
            points += 5
            reasons.append("ct_002 (inactive) did not get tag")
        else:
            reasons.append("ct_002 was incorrectly tagged")
    except Exception as e:
        reasons.append(f"Error reading contacts.json: {str(e)}")
        points = 0
    total_score += add_item("Contacts tags modification", points, 15, points == 15, "; ".join(reasons))

    # 6. Tag definitions check (10 pts)
    # Expect tag_definitions.json contains a tag with name 'key_account'
    tags_path = os.path.join(workspace, "data", "tags", "tag_definitions.json")
    points = 0
    reasons = []
    try:
        with open(tags_path, "r") as f:
            tag_defs_data = json.load(f)
        tag_defs = tag_defs_data.get("tag_definitions", [])
        names = [t.get("name") for t in tag_defs]
        if "key_account" in names:
            points = 10
            reasons.append("key_account tag definition found")
        else:
            reasons.append("key_account tag definition not found")
    except Exception as e:
        reasons.append(f"Error reading tag definitions: {str(e)}")
        points = 0
    total_score += add_item("Tag definition 'key_account' exists", points, 10, points == 10, "; ".join(reasons))

    # 7. Reminders update check (10 pts)
    # Expect reminders.json contains a birthday reminder for ct_001 with date 2025-04-15 (may be additional, but at least one)
    reminders_path = os.path.join(workspace, "data", "reminders", "reminders.json")
    points = 0
    reasons = []
    try:
        with open(reminders_path, "r") as f:
            reminders_data = json.load(f)
        reminders_list = reminders_data.get("reminders", [])
        found = False
        for rem in reminders_list:
            if rem.get("contact_id") == "ct_001" and rem.get("reminder_date") == "2025-04-15":
                found = True
                break
        if found:
            points = 10
            reasons.append("Birthday reminder for ct_001 on 2025-04-15 exists")
        else:
            reasons.append("Missing birthday reminder for ct_001 on 2025-04-15")
    except Exception as e:
        reasons.append(f"Error reading reminders: {str(e)}")
        points = 0
    total_score += add_item("Reminder for ct_001 created", points, 10, points == 10, "; ".join(reasons))

    # Calculate total (max 100)
    total_score = min(total_score, 100)
    # Write score
    _write_score(total_score, score_details, workspace)

def _write_score(total, details, workspace):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
