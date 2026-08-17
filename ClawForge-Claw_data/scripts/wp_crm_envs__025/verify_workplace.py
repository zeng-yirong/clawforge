import json, os, sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0

    # 1. ops directory exists
    ops_dir = os.path.join(workspace, "ops")
    item = {"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if os.path.isdir(ops_dir):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops/ directory found"
    else:
        item["reason"] = "ops/ directory not found"
    score_details.append(item)

    # 2. vip_contacts.json exists
    filepath = os.path.join(ops_dir, "vip_contacts.json") if os.path.isdir(ops_dir) else os.path.join(workspace, "ops", "vip_contacts.json")
    item2 = {"item": "vip_contacts.json exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if os.path.isfile(filepath):
        item2["score"] = 10
        item2["passed"] = True
        item2["reason"] = "file found"
    else:
        item2["reason"] = "file not found"
    score_details.append(item2)

    if not item2["passed"]:
        # cannot proceed
        total = sum(d["score"] for d in score_details)
        write_score(total, score_details, workspace)
        return

    # 3. JSON validity
    item3 = {"item": "JSON is valid and is a list", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            item3["score"] = 10
            item3["passed"] = True
            item3["reason"] = "valid JSON array"
        else:
            item3["reason"] = "root element is not a list"
    except Exception as e:
        item3["reason"] = f"JSON parse error: {e}"
    score_details.append(item3)

    if not item3["passed"]:
        total = sum(d["score"] for d in score_details)
        write_score(total, score_details, workspace)
        return

    # 4. Each entry has required fields: contact_id, full_name, company_name
    item4 = {"item": "required fields present in each entry", "score": 0, "max_score": 15, "passed": False, "reason": ""}
    required_keys = {"contact_id", "full_name", "company_name"}
    all_ok = True
    missing_any = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            missing_any.append(f"entry {i} is not a dict")
            all_ok = False
            continue
        missing = required_keys - set(entry.keys())
        if missing:
            missing_any.append(f"entry {i} missing {missing}")
            all_ok = False
    if all_ok:
        item4["score"] = 15
        item4["passed"] = True
        item4["reason"] = "all entries have required keys"
    else:
        item4["reason"] = "; ".join(missing_any)
    score_details.append(item4)

    # 5. Correct VIP contacts (expected: Alice, David, Frank, Grace)
    item5 = {"item": "correct selection of VIP contacts", "score": 0, "max_score": 40, "passed": False, "reason": ""}
    expected_ids = {"ct_101", "ct_104", "ct_106", "ct_107"}
    actual_ids = set()
    for entry in data:
        if isinstance(entry, dict) and "contact_id" in entry:
            actual_ids.add(entry["contact_id"])
    # also reject any extra ids
    extra = actual_ids - expected_ids
    missing = expected_ids - actual_ids
    if not extra and not missing:
        item5["score"] = 40
        item5["passed"] = True
        item5["reason"] = f"exactly the expected {len(expected_ids)} contacts"
    else:
        reasons = []
        if missing:
            reasons.append(f"missing: {missing}")
        if extra:
            reasons.append(f"extra: {extra}")
        # partial credit: 10 points per correct id (max 40), minus 10 per extra
        correct = len(actual_ids & expected_ids)
        penalty = len(extra) * 10
        score = min(40, correct * 10) - penalty
        if score < 0:
            score = 0
        item5["score"] = score
        item5["reason"] = "; ".join(reasons)
    score_details.append(item5)

    # 6. Bonus: no extra unrequested fields? not required. But we can check if contact names match expected (consistency check)
    # We'll add a small consistency check for full_name (optional, 0-5)
    item6 = {"item": "full_name matches known records (bonus)", "score": 0, "max_score": 5, "passed": False, "reason": ""}
    # We know expected mappings from env_builder
    expected_names = {
        "ct_101": "Alice Johnson",
        "ct_104": "David Brown",
        "ct_106": "Frank Miller",
        "ct_107": "Grace Wilson",
    }
    name_ok = True
    for entry in data:
        if isinstance(entry, dict) and entry.get("contact_id") in expected_names:
            if entry.get("full_name") != expected_names[entry["contact_id"]]:
                name_ok = False
                break
    if name_ok and actual_ids == expected_ids:
        item6["score"] = 5
        item6["passed"] = True
        item6["reason"] = "all names match known data"
    else:
        item6["reason"] = "some names incorrect or incomplete selection"
    score_details.append(item6)

    total = sum(d["score"] for d in score_details)
    write_score(total, score_details, workspace)

def write_score(total, details, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
