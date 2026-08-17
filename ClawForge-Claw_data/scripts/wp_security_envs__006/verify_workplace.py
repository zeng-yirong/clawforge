import json
import os
import sys

CWD = sys.argv[1] if len(sys.argv) > 1 else "."

def read_json(rel_path):
    full = os.path.join(CWD, rel_path)
    if not os.path.exists(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

def check_file_exists(rel_path):
    return os.path.isfile(os.path.join(CWD, rel_path))

def main():
    details = []
    total = 0

    # 1. Directory structure (10 points)
    score_dir = 0
    if os.path.isdir(os.path.join(CWD, "ops")):
        score_dir = 10
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ok"})
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "missing ops/ directory"})
    total += score_dir

    # 2. Target file exists and is valid JSON (10 points)
    target_rel = "ops/acknowledge.json"
    target_data = read_json(target_rel)
    if target_data is not None and isinstance(target_data, list):
        details.append({"item": "ops/acknowledge.json exists and is a JSON list", "score": 10, "max_score": 10, "passed": True, "reason": "valid"})
        total += 10
    else:
        details.append({"item": "ops/acknowledge.json exists and is a JSON list", "score": 0, "max_score": 10, "passed": False, "reason": "missing or not a list"})
        # cannot proceed
        _write_score(total, details)
        return

    # 3. Structural correctness – each entry must have zone_id and phone (10 points)
    entry_ok = True
    for idx, entry in enumerate(target_data):
        if not isinstance(entry, dict) or "zone_id" not in entry or "phone" not in entry:
            entry_ok = False
            details.append({"item": f"Entry {idx} has required fields", "score": 0, "max_score": 10, "passed": False, "reason": f"missing zone_id or phone in entry {idx}"})
            break
    else:
        if entry_ok:
            details.append({"item": "All entries have zone_id and phone", "score": 10, "max_score": 10, "passed": True, "reason": "ok"})
            total += 10

    # 4. Content accuracy (70 points: 30 for correct filtering, 40 for exact match)
    # Load ground truth from data files
    zones = read_json("data/zones.json")
    accounts = read_json("data/accounts.json")
    contacts = read_json("data/contacts/contacts.json")
    if None in (zones, accounts, contacts):
        details.append({"item": "source data accessible", "score": 0, "max_score": 70, "passed": False, "reason": "cannot read source data"})
        _write_score(total, details)
        return

    # Build zone->account mapping
    zone_to_account = {}
    for acc in accounts.get("accounts", []):
        for zid in acc.get("zones", []):
            zone_to_account[zid] = acc

    # Build contact lookup
    contact_map = {}
    for c in contacts.get("contacts", []):
        contact_map[c["contact_id"]] = c

    # Compute expected list
    expected = []
    for zone in zones.get("zones", []):
        if not zone.get("intrusion_detected"):
            continue
        zid = zone["zone_id"]
        acc = zone_to_account.get(zid)
        if not acc:
            continue
        for cid in acc.get("emergency_contacts", []):
            c = contact_map.get(cid)
            if c and c.get("role") in ("Police", "Police Non-Emergency"):
                expected.append({"zone_id": zid, "phone": c["phone"]})
                break  # take first police contact per zone
    expected.sort(key=lambda x: x["zone_id"])

    # Compare sorted actual
    actual = sorted(target_data, key=lambda x: x.get("zone_id", ""))
    if len(actual) != len(expected):
        details.append({"item": f"Correct number of entries (expected {len(expected)}, got {len(actual)})", "score": 0, "max_score": 30, "passed": False, "reason": f"count mismatch"})
        total += 0
    else:
        details.append({"item": f"Correct number of entries", "score": 30, "max_score": 30, "passed": True, "reason": f"found {len(actual)} as expected"})
        total += 30

    # Exact match
    match = actual == expected
    if match:
        details.append({"item": "Exact content match (sorted by zone_id)", "score": 40, "max_score": 40, "passed": True, "reason": "all entries correct"})
        total += 40
    else:
        diff = []
        for i, (a, e) in enumerate(zip(actual, expected)):
            if a != e:
                diff.append(f"index {i}: got {a}, expected {e}")
        reason = "; ".join(diff) if diff else "lengths differ"
        details.append({"item": "Exact content match (sorted by zone_id)", "score": 0, "max_score": 40, "passed": False, "reason": reason})

    # Write score
    _write_score(min(total, 100), details)

def _write_score(total, details):
    result = {"total_score": total, "details": details}
    outpath = os.path.join(CWD, "workplace_score.json")
    with open(outpath, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
