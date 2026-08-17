import json
import sys
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace)

    result_path = workspace_path / "data" / "clean_contacts.json"
    details = []
    total_score = 0

    # 1. File existence (5 points)
    if result_path.exists():
        details.append({"item": "clean_contacts.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "File found"})
        total_score += 5
    else:
        details.append({"item": "clean_contacts.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "File not found"})
        # cannot continue
        details.append({"item": "Overall", "score": 0, "max_score": 100, "passed": False, "reason": "Missing output file"})
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return

    # 2. JSON validity (10 points)
    try:
        contacts = load_json(result_path)
        if not isinstance(contacts, list):
            raise ValueError("Not a list")
        details.append({"item": "clean_contacts.json is valid JSON and a list", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON array"})
        total_score += 10
    except Exception as e:
        details.append({"item": "clean_contacts.json is valid JSON and a list", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid: {e}"})
        # cannot continue further
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # Build expected contacts (sorted by contact_id for comparison)
    expected_contacts = [
        # Alice (corrected folder)
        {"contact_id": "ct_001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
         "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001",
         "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "business",
         "tags": ["vip"]},
        # Bob (added tag)
        {"contact_id": "ct_002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith",
         "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "comp_002",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "business",
         "tags": ["needs-review"]},
        # Carol (corrected folder, tags unchanged)
        {"contact_id": "ct_003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams",
         "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp_003",
         "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "business",
         "tags": ["lead"]},
        # David (added tag)
        {"contact_id": "ct_004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown",
         "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp_004",
         "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "inactive",
         "tags": ["needs-review"]},
        # Emma (added tag)
        {"contact_id": "ct_005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis",
         "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_005",
         "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business",
         "folder": "personal", "tags": ["needs-review"]},
        # Frank (unchanged)
        {"contact_id": "ct_006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller",
         "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_006",
         "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business",
         "folder": "business", "tags": ["important"]},
        # Grace (unchanged)
        {"contact_id": "ct_007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson",
         "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_005",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "business",
         "tags": ["vip"]},
        # Henry (added tag)
        {"contact_id": "ct_008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor",
         "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp_001",
         "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "personal",
         "tags": ["needs-review"]},
    ]

    # Sort both by contact_id
    contacts_sorted = sorted(contacts, key=lambda c: c.get("contact_id", ""))
    expected_sorted = sorted(expected_contacts, key=lambda c: c.get("contact_id", ""))

    # 3. Correct number of records (10 points)
    if len(contacts_sorted) == 8:
        details.append({"item": "Correct record count (8)", "score": 10, "max_score": 10, "passed": True, "reason": "8 contact records"})
        total_score += 10
    else:
        details.append({"item": "Correct record count (8)", "score": 0, "max_score": 10, "passed": False, "reason": f"Found {len(contacts_sorted)} records, expected 8"})

    # 4. Invalid record removed (10 points)
    # check that no contact_id is empty or missing
    invalid_found = any(c.get("contact_id") in (None, "") for c in contacts_sorted)
    if not invalid_found:
        details.append({"item": "Invalid record removed", "score": 10, "max_score": 10, "passed": True, "reason": "No empty contact_id"})
        total_score += 10
    else:
        details.append({"item": "Invalid record removed", "score": 0, "max_score": 10, "passed": False, "reason": "Found record with empty contact_id"})

    # 5. Duplicate removed (15 points)
    # Check that contact_id ct_009 is not present
    dup_present = any(c.get("contact_id") == "ct_009" for c in contacts_sorted)
    if not dup_present:
        details.append({"item": "Duplicate record removed", "score": 15, "max_score": 15, "passed": True, "reason": "ct_009 not present"})
        total_score += 15
    else:
        details.append({"item": "Duplicate record removed", "score": 0, "max_score": 15, "passed": False, "reason": "Duplicate ct_009 still present"})

    # 6. Folder corrections (2 contacts each 10 points = 20)
    folder_correct = 0
    for exp in expected_sorted:
        if exp["contact_id"] in ("ct_001", "ct_003"):
            actual = next((c for c in contacts_sorted if c.get("contact_id") == exp["contact_id"]), None)
            if actual and actual.get("folder") == "business":
                folder_correct += 1
    if folder_correct == 2:
        details.append({"item": "Folder corrections (Alice & Carol) to business", "score": 20, "max_score": 20, "passed": True, "reason": "Both folder changed"})
        total_score += 20
    else:
        details.append({"item": "Folder corrections (Alice & Carol) to business", "score": 0, "max_score": 20, "passed": False, "reason": f"Only {folder_correct}/2 corrected"})

    # 7. Tag additions (4 contacts each 7.5 points = 30)
    tag_correct = 0
    for exp in expected_sorted:
        if exp["contact_id"] in ("ct_002", "ct_004", "ct_005", "ct_008"):
            actual = next((c for c in contacts_sorted if c.get("contact_id") == exp["contact_id"]), None)
            if actual and "needs-review" in actual.get("tags", []):
                tag_correct += 1
    if tag_correct == 4:
        details.append({"item": "Tag additions (Bob, David, Emma, Henry) have 'needs-review'", "score": 30, "max_score": 30, "passed": True, "reason": "All four have tag"})
        total_score += 30
    else:
        details.append({"item": "Tag additions (Bob, David, Emma, Henry) have 'needs-review'", "score": 0, "max_score": 30, "passed": False, "reason": f"Only {tag_correct}/4 have tag"})

    # 8. Ensure other contacts unchanged (bonus check integrated into above; if we missed something, deduct)
    # Already covered by record count and field checks, but we explicitly check no extra modifications.
    # We'll consider it passed if all previous checks are fine; otherwise penalty implicit.
    # For completeness add a small item (0 points but can adjust)
    extra_mods = []
    for exp in expected_sorted:
        actual = next((c for c in contacts_sorted if c.get("contact_id") == exp["contact_id"]), None)
        if actual:
            # For contacts not in the correction/tag list, verify they match exactly
            if exp["contact_id"] not in ("ct_001", "ct_002", "ct_003", "ct_004", "ct_005", "ct_008"):
                # compare all fields except contact_id (already used)
                for key in exp:
                    if exp[key] != actual.get(key):
                        extra_mods.append(f"{exp['contact_id']}:{key} expected {exp[key]}, got {actual.get(key)}")
    if not extra_mods:
        details.append({"item": "No unintended modifications on other contacts", "score": 0, "max_score": 0, "passed": True, "reason": "All other fields unchanged"})
    else:
        details.append({"item": "No unintended modifications on other contacts", "score": 0, "max_score": 0, "passed": False, "reason": "Unexpected changes: " + "; ".join(extra_mods[:3])})

    total_score = min(total_score, 100)  # cap
    details.append({"item": "Overall", "score": total_score, "max_score": 100, "passed": total_score >= 80, "reason": f"Final score {total_score}/100"})

    # Write score file
    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
