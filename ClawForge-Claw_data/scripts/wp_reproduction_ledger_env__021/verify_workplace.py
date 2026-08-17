import sys
import json
import os
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # ------------------------------------------------------------
    # 1. Directory structure (10 pts)
    # ------------------------------------------------------------
    required_dirs = ["data", "data/drafts", "ledger"]
    dir_ok = True
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dir_ok = False
            break
    score_dir = 10 if dir_ok else 0
    details.append({
        "item": "Directory structure (data/, data/drafts/, ledger/)",
        "score": score_dir,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "All required directories exist" if dir_ok else "Missing one or more directories"
    })
    total_score += score_dir

    # ------------------------------------------------------------
    # 2. Output file exists (10 pts)
    # ------------------------------------------------------------
    output_path = os.path.join(workspace, "ledger/reproduction_ledger.json")
    file_exists = os.path.isfile(output_path)
    score_file = 10 if file_exists else 0
    details.append({
        "item": "Output file ledger/reproduction_ledger.json exists",
        "score": score_file,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File missing"
    })
    if not file_exists:
        total_score += score_file
        return {"total_score": total_score, "details": details}
    total_score += score_file

    # ------------------------------------------------------------
    # 3. JSON validity & structure (10 pts)
    # ------------------------------------------------------------
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON format validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        return {"total_score": total_score, "details": details}

    if not isinstance(data, dict) or "ledger_entries" not in data:
        details.append({
            "item": "Top-level structure with 'ledger_entries' key",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing top-level 'ledger_entries' key or not a dict"
        })
        return {"total_score": total_score, "details": details}
    entries = data["ledger_entries"]
    if not isinstance(entries, list):
        details.append({
            "item": "Top-level structure with 'ledger_entries' key",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "'ledger_entries' is not a list"
        })
        return {"total_score": total_score, "details": details}
    score_json = 10
    details.append({
        "item": "JSON format validity & top-level structure",
        "score": score_json,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON with 'ledger_entries' list"
    })
    total_score += score_json

    # ------------------------------------------------------------
    # 4. Field completeness (20 pts)
    # ------------------------------------------------------------
    required_fields = {"doc_id", "project_id", "title", "path"}
    field_errors = 0
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            field_errors += 1
            continue
        missing = [f for f in required_fields if f not in entry or not isinstance(entry[f], str) or entry[f] == ""]
        if missing:
            field_errors += 1
    score_fields = max(0, 20 - 5 * field_errors)  # -5 per offending entry, min 0
    details.append({
        "item": "Field completeness (all entries have non-empty doc_id, project_id, title, path)",
        "score": score_fields,
        "max_score": 20,
        "passed": field_errors == 0,
        "reason": f"All {len(entries)} entries have required fields" if field_errors == 0 else f"{field_errors} entries have missing/invalid fields"
    })
    total_score += score_fields

    # ------------------------------------------------------------
    # 5. Duplicate removal & timestamp logic (25 pts)
    # ------------------------------------------------------------
    # Expected correct set: doc_ids 001,002,004,006,007 (5 unique)
    # strict check: no duplicate doc_id, and the kept one for 001 should be the one with timestamp 2025-03-20
    expected_ids = {"001", "002", "004", "006", "007"}
    actual_ids = [e.get("doc_id") for e in entries if isinstance(e, dict)]
    id_set = set(actual_ids)

    # Check count
    count_ok = len(actual_ids) == 5
    # Check correct IDs
    ids_ok = id_set == expected_ids

    # Check that for doc_id 001, the path is "docs/proj-alpha/install_v2.md" (newer timestamp)
    entry_001 = None
    for e in entries:
        if isinstance(e, dict) and e.get("doc_id") == "001":
            entry_001 = e
            break
    path_001_ok = entry_001 is not None and entry_001.get("path") == "docs/proj-alpha/install_v2.md"

    dup_errors = 0
    if not count_ok:
        dup_errors += 1
    if not ids_ok:
        dup_errors += 1
    if not path_001_ok:
        dup_errors += 1

    score_dup = max(0, 25 - 10 * dup_errors)  # -10 per check failure
    details.append({
        "item": "Duplicate removal & correct timestamp selection",
        "score": score_dup,
        "max_score": 25,
        "passed": dup_errors == 0,
        "reason": f"5 unique entries, correct IDs, doc_id 001 uses latest timestamp" if dup_errors == 0 else f"Count={len(actual_ids)} (expected 5), IDs={id_set}, path_001={entry_001.get('path') if entry_001 else 'missing'}"
    })
    total_score += score_dup

    # ------------------------------------------------------------
    # 6. Sorting (10 pts)
    # ------------------------------------------------------------
    sorted_ids = sorted(actual_ids)
    is_sorted = actual_ids == sorted_ids
    score_sort = 10 if is_sorted else 0
    details.append({
        "item": "Entries sorted by doc_id ascending",
        "score": score_sort,
        "max_score": 10,
        "passed": is_sorted,
        "reason": "Correctly sorted" if is_sorted else f"Order: {actual_ids}"
    })
    total_score += score_sort

    # ------------------------------------------------------------
    # 7. Obsolete / invalid rejection (15 pts)
    # ------------------------------------------------------------
    # Ensure no entries with status "obsolete" or missing required field
    forbidden = 0
    for e in entries:
        if isinstance(e, dict):
            if e.get("status") == "obsolete":
                forbidden += 1
            # also check invalid entries (should already be caught above, but double-check)
            if not all(k in e and isinstance(e[k], str) and e[k] != "" for k in required_fields):
                forbidden += 1
    # also ensure the obsolete.json records (doc_id 009,010) are absent
    obsolete_ids = {"009", "010"}
    actual_obsolete = [e["doc_id"] for e in entries if isinstance(e, dict) and e.get("doc_id") in obsolete_ids]
    if actual_obsolete:
        forbidden += len(actual_obsolete)

    score_reject = max(0, 15 - 5 * min(forbidden, 3))  # -5 per found invalid/obsolete entry
    details.append({
        "item": "Rejection of obsolete entries and invalid records",
        "score": score_reject,
        "max_score": 15,
        "passed": forbidden == 0,
        "reason": "No obsolete or invalid entries found" if forbidden == 0 else f"Found {forbidden} disallowed entries"
    })
    total_score += score_reject

    # ------------------------------------------------------------
    # Final
    # ------------------------------------------------------------
    return {"total_score": min(total_score, 100), "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    result["total_score"] = min(result["total_score"], 100)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {result['total_score']}/100")
