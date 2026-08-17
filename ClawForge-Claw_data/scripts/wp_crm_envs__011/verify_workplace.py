import os
import sys
import json

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. Directory structure (10 pts)
    dir_score = 0
    dir_max = 10
    data_dir = os.path.join(workspace, "data")
    tags_dir = os.path.join(workspace, "data", "tags")
    required_dirs = [data_dir, tags_dir]
    dir_ok = all(os.path.isdir(d) for d in required_dirs)
    if dir_ok:
        dir_score = dir_max
        details.append({"item": "Directory structure: data/ and data/tags/ exist", "score": dir_score, "max_score": dir_max, "passed": True, "reason": "All required directories found"})
    else:
        missing = [d for d in required_dirs if not os.path.isdir(d)]
        details.append({"item": "Directory structure: data/ and data/tags/ exist", "score": 0, "max_score": dir_max, "passed": False, "reason": f"Missing directories: {missing}"})
    total_score += dir_score

    # 2. JSON files parseable and have correct wrapper keys (10 pts)
    json_score = 0
    json_max = 10
    files_to_check = {
        "data/companies.json": "companies",
        "data/contacts.json": "contacts",
        "data/tags/tag_definitions.json": "tag_definitions"
    }
    json_errors = []
    for rel_path, wrapper in files_to_check.items():
        full_path = os.path.join(workspace, rel_path)
        if not os.path.isfile(full_path):
            json_errors.append(f"{rel_path} not found")
            continue
        try:
            with open(full_path, "r") as f:
                data = json.load(f)
            if wrapper not in data or not isinstance(data[wrapper], list):
                json_errors.append(f"{rel_path}: missing or invalid wrapper '{wrapper}'")
        except json.JSONDecodeError as e:
            json_errors.append(f"{rel_path}: parse error - {e}")
    if not json_errors:
        json_score = json_max
        details.append({"item": "JSON files valid with correct wrapper", "score": json_score, "max_score": json_max, "passed": True, "reason": "All three JSON files parse and contain the expected list wrapper"})
    else:
        details.append({"item": "JSON files valid with correct wrapper", "score": 0, "max_score": json_max, "passed": False, "reason": "; ".join(json_errors)})
    total_score += json_score

    # 3. Load data for further checks
    with open(os.path.join(workspace, "data/companies.json")) as f:
        companies = json.load(f)["companies"]
    with open(os.path.join(workspace, "data/contacts.json")) as f:
        contacts = json.load(f)["contacts"]
    with open(os.path.join(workspace, "data/tags/tag_definitions.json")) as f:
        tags_def = json.load(f)["tag_definitions"]

    # Identify consulting company ids
    consulting_ids = {c["company_id"] for c in companies if c.get("industry") == "Consulting"}
    # Expected consulting contacts: those with company_id in consulting_ids and company_id not None
    relevant_contacts = [
        c for c in contacts
        if c.get("company_id") is not None and c["company_id"] in consulting_ids
    ]
    # Also we know there are exactly 3 such contacts: Bob (ct_002), Carol (ct_003), John (ct_008)
    expected_ids = {"ct_002", "ct_003", "ct_008"}
    actual_ids = {c["contact_id"] for c in relevant_contacts}
    # 4. Correctness of selection (30 pts)
    select_score = 0
    select_max = 30
    if actual_ids == expected_ids:
        select_score = select_max
        details.append({"item": "Correctly identified consulting contacts (Bob, Carol, John)", "score": select_score, "max_score": select_max, "passed": True, "reason": f"Exactly the 3 expected contacts: {expected_ids}"})
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason_parts = []
        if missing:
            reason_parts.append(f"Missing contacts: {missing}")
        if extra:
            reason_parts.append(f"Unexpected contacts: {extra}")
        details.append({"item": "Correctly identified consulting contacts (Bob, Carol, John)", "score": 0, "max_score": select_max, "passed": False, "reason": "; ".join(reason_parts) if reason_parts else "No relevant contacts found"})
    total_score += select_score

    # 5. Tag definition check: 'consulting-partner' must exist (10 pts)
    tag_def_score = 0
    tag_def_max = 10
    tag_found = any(t.get("name") == "consulting-partner" and t.get("tag_id") == "tag_consulting_partner" for t in tags_def)
    if tag_found:
        tag_def_score = tag_def_max
        details.append({"item": "Consulting partner tag defined (name=consulting-partner, tag_id=tag_consulting_partner)", "score": tag_def_score, "max_score": tag_def_max, "passed": True, "reason": "Tag definition found in data/tags/tag_definitions.json"})
    else:
        # Check if any tag with that name exists even if id mismatched (partial credit)
        name_exists = any(t.get("name") == "consulting-partner" for t in tags_def)
        if name_exists:
            tag_def_score = 5
            details.append({"item": "Consulting partner tag defined (name correct, id may be wrong)", "score": 5, "max_score": tag_def_max, "passed": False, "reason": "Tag name found but tag_id does not match expected 'tag_consulting_partner'"})
        else:
            details.append({"item": "Consulting partner tag defined (name=consulting-partner)", "score": 0, "max_score": tag_def_max, "passed": False, "reason": "No tag with name 'consulting-partner' found"})
    total_score += tag_def_score

    # 6. For each relevant contact, check folder and tags (40 pts total)
    # 2 items per contact: folder=20, tag=20 -> but can split per contact
    # We'll assign 20 pts for folder correctness (all must be business) and 20 pts for tag inclusion.
    folder_score = 0
    tag_score = 0
    folder_max = 20
    tag_max = 20

    folder_ok = all(c.get("folder") == "business" for c in relevant_contacts)
    tag_ok = all("consulting-partner" in c.get("tags", []) for c in relevant_contacts)

    if folder_ok:
        folder_score = folder_max
    else:
        bad_folder = [c["contact_id"] for c in relevant_contacts if c.get("folder") != "business"]
        details.append({"item": "All consulting contacts have folder='business'", "score": 0, "max_score": folder_max, "passed": False, "reason": f"Contacts with wrong folder: {bad_folder}"})
    if tag_ok:
        tag_score = tag_max
    else:
        no_tag = [c["contact_id"] for c in relevant_contacts if "consulting-partner" not in c.get("tags", [])]
        details.append({"item": "All consulting contacts have tag 'consulting-partner'", "score": 0, "max_score": tag_max, "passed": False, "reason": f"Contacts missing tag: {no_tag}"})

    # Record the combined detail for folder
    details.append({"item": "All consulting contacts have folder='business'", "score": folder_score, "max_score": folder_max, "passed": folder_ok, "reason": "All folders correct" if folder_ok else "See above"})
    details.append({"item": "All consulting contacts have tag 'consulting-partner'", "score": tag_score, "max_score": tag_max, "passed": tag_ok, "reason": "All tags present" if tag_ok else "See above"})
    total_score += folder_score + tag_score

    # Final scoring (ensure 0-100)
    total_score = min(total_score, max_total)
    total_score = max(total_score, 0)

    # Write score file
    score_info = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_info, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
