import sys
import json
import os
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. Directory structure: ops directory must exist (10 pts)
    ops_dir = Path(workspace) / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory missing"})

    # 2. Result file exists and is valid JSON (10 pts)
    result_file = ops_dir / "contact_updates.json"
    if result_file.is_file():
        try:
            with open(result_file) as f:
                data = json.load(f)
            if not isinstance(data, list):
                details.append({"item": "contact_updates.json is a list", "score": 0, "max_score": 5, "passed": False, "reason": "Not a list"})
            else:
                details.append({"item": "contact_updates.json is a list", "score": 5, "max_score": 5, "passed": True, "reason": "Valid list"})
                total_score += 5
            details.append({"item": "JSON parseable", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
            total_score += 5
        except (json.JSONDecodeError, IOError) as e:
            details.append({"item": "JSON parseable", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {str(e)}"})
            # Can't continue
            finalize(details, total_score, workspace)
            return
    else:
        details.append({"item": "contact_updates.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        finalize(details, total_score, workspace)
        return

    # 3. Each entry must have contact_id, folder, tags fields (10 pts)
    field_ok = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            details.append({"item": f"Entry {i} is a dict", "score": 0, "max_score": 1, "passed": False, "reason": "Not a dict"})
            field_ok = False
            continue
        if not all(k in entry for k in ("contact_id", "folder", "tags")):
            details.append({"item": f"Entry {i} has required fields", "score": 0, "max_score": 1, "passed": False, "reason": f"Missing fields, got {list(entry.keys())}"})
            field_ok = False
        else:
            details.append({"item": f"Entry {i} has required fields", "score": 1, "max_score": 1, "passed": True, "reason": "OK"})
    if field_ok:
        total_score += 10

    # 4. Correctness: exactly 3 contacts must be in the result (ct_101, ct_102, ct_103)
    #    Each must have folder="business" and tags=["priority"]
    expected_updates = {
        "ct_101": {"folder": "business", "tags": ["priority"]},
        "ct_102": {"folder": "business", "tags": ["priority"]},
        "ct_103": {"folder": "business", "tags": ["priority"]},
    }
    found_ids = {e["contact_id"] for e in data if isinstance(e, dict)}
    correct_count = 0
    max_correct = 70  # total weight for correctness

    # Check for extra contacts (penalty: -10 each up to -30)
    extra = found_ids - set(expected_updates.keys())
    if extra:
        penalty = min(len(extra) * 10, 30)
        details.append({"item": "No extra contacts", "score": 0, "max_score": 30, "passed": False, "reason": f"Unexpected contacts: {extra}"})
        total_score -= penalty  # apply later
    else:
        details.append({"item": "No extra contacts", "score": 30, "max_score": 30, "passed": True, "reason": "All contacts are expected"})
        total_score += 30

    # Check missing contacts
    missing = set(expected_updates.keys()) - found_ids
    if missing:
        details.append({"item": "All required contacts present", "score": 0, "max_score": 40, "passed": False, "reason": f"Missing contacts: {missing}"})
        # each missing costs 13 points (approx)
        penalty_missing = len(missing) * 13
        total_score -= penalty_missing
    else:
        details.append({"item": "All required contacts present", "score": 40, "max_score": 40, "passed": True, "reason": "All present"})
        total_score += 40

    # Check values for each found contact
    for entry in data:
        if not isinstance(entry, dict):
            continue
        cid = entry.get("contact_id")
        if cid in expected_updates:
            exp = expected_updates[cid]
            correct = True
            reason_parts = []
            if entry.get("folder") != exp["folder"]:
                correct = False
                reason_parts.append(f"folder expected {exp['folder']} got {entry.get('folder')}")
            if entry.get("tags") != exp["tags"]:
                correct = False
                reason_parts.append(f"tags expected {exp['tags']} got {entry.get('tags')}")
            if correct:
                # already counted in presence, but we can add bonus
                pass
            else:
                # reduce score
                total_score -= 10  # each wrong value costs 10
                details.append({"item": f"{cid} values correct", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(reason_parts)})
        else:
            # extra contact already penalized
            pass

    # Clamp total to [0,100]
    final_score = max(0, min(100, total_score))
    finalize(details, final_score, workspace)

def finalize(details, total_score, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification done. Score: {total_score}/100")

if __name__ == "__main__":
    verify()
