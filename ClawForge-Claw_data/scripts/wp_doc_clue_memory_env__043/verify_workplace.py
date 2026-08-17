import json
import os
import sys

def verify(workspace: str) -> dict:
    details = []
    total = 0

    # 1. ops directory exists (5 points)
    ops_path = os.path.join(workspace, "ops")
    item = {"item": "ops directory exists", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    if os.path.isdir(ops_path):
        item["passed"] = True
        item["score"] = 5
        item["reason"] = "ops/ present"
    else:
        item["reason"] = "ops/ not found"
    details.append(item)
    total += item["score"]

    # 2. ops/clue_list.json exists (10 points)
    clue_path = os.path.join(workspace, "ops", "clue_list.json")
    item = {"item": "clue_list.json exists", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.isfile(clue_path):
        item["passed"] = True
        item["score"] = 10
        item["reason"] = "file found"
    else:
        item["reason"] = "file missing"
    details.append(item)
    total += item["score"]

    if not os.path.isfile(clue_path):
        return {"total_score": total, "details": details}

    # 3. JSON is valid (10 points)
    item = {"item": "valid JSON", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
        item["passed"] = True
        item["score"] = 10
        item["reason"] = "parsed without error"
    except Exception as e:
        item["reason"] = f"JSON parse error: {e}"
        details.append(item)
        return {"total_score": total, "details": details}
    details.append(item)
    total += item["score"]

    # 4. The top-level structure is a list (or a dict containing a list?) – we expect a list
    # From prompt: "clue list" – we accept either a list or a dict with a single key "clues"
    item = {"item": "clue list structure", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    clues = None
    if isinstance(data, list):
        clues = data
    elif isinstance(data, dict):
        # allow common wrappers
        for key in ("clues", "clue_list", "items", "results"):
            if key in data and isinstance(data[key], list):
                clues = data[key]
                break
    if clues is not None:
        item["passed"] = True
        item["score"] = 5
        item["reason"] = f"found list with {len(clues)} entries"
    else:
        item["reason"] = "top-level neither list nor dict with list value"
    details.append(item)
    total += item["score"]

    if clues is None:
        return {"total_score": total, "details": details}

    # 5. Each clue entry has required fields: document_id, title, summary, type (15 points)
    required_fields = {"document_id", "title", "summary", "type"}
    field_ok = True
    missing_fields = set()
    for i, entry in enumerate(clues):
        if not isinstance(entry, dict):
            field_ok = False
            missing_fields.add(f"entry_{i}_not_dict")
            continue
        for f in required_fields:
            if f not in entry:
                field_ok = False
                missing_fields.add(f)
    item = {"item": "all entries contain required fields (document_id, title, summary, type)", "max_score": 15, "score": 0, "passed": False, "reason": ""}
    if field_ok and not missing_fields:
        item["passed"] = True
        item["score"] = 15
        item["reason"] = "all entries have all fields"
    else:
        item["reason"] = f"missing fields: {missing_fields}"
    details.append(item)
    total += item["score"]

    # 6. The set of document IDs matches the ground truth (30 points)
    # Ground truth: R-2026-001, R-2026-003, PPT-2026-002, MS-2026-001, MS-2026-004, MS-2026-005
    expected_ids = {"R-2026-001", "R-2026-003", "PPT-2026-002", "MS-2026-001", "MS-2026-004", "MS-2026-005"}
    actual_ids = set()
    for entry in clues:
        doc_id = entry.get("document_id")
        if doc_id:
            actual_ids.add(doc_id)
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids
    item = {"item": "correct set of document IDs (no missing, no extra)", "max_score": 30, "score": 0, "passed": False, "reason": ""}
    if not missing and not extra:
        item["passed"] = True
        item["score"] = 30
        item["reason"] = f"all {len(expected_ids)} IDs matched exactly"
    else:
        reasons = []
        if missing:
            reasons.append(f"missing: {sorted(missing)}")
        if extra:
            reasons.append(f"extra: {sorted(extra)}")
        item["reason"] = "; ".join(reasons)
        # Partial credit: 5 points per correct ID, up to 30
        correct_count = len(expected_ids & actual_ids)
        item["score"] = min(correct_count * 5, 30)
    details.append(item)
    total += item["score"]

    # 7. No duplicate document IDs (5 points)
    item = {"item": "no duplicate document IDs", "max_score": 5, "score": 0, "passed": False, "reason": ""}
    seen = set()
    dup = False
    for entry in clues:
        doc_id = entry.get("document_id")
        if doc_id in seen:
            dup = True
            break
        seen.add(doc_id)
    if not dup:
        item["passed"] = True
        item["score"] = 5
        item["reason"] = "all IDs unique"
    else:
        item["reason"] = "duplicate found"
    details.append(item)
    total += item["score"]

    # 8. The 'type' field for each entry is one of 'report', 'presentation', 'media_sample' (10 points)
    valid_types = {"report", "presentation", "media_sample"}
    bad_types = []
    for entry in clues:
        t = entry.get("type", "")
        if t not in valid_types:
            bad_types.append(t)
    item = {"item": "all types are valid (report/presentation/media_sample)", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if not bad_types:
        item["passed"] = True
        item["score"] = 10
        item["reason"] = "all types valid"
    else:
        item["reason"] = f"invalid types: {bad_types}"
    details.append(item)
    total += item["score"]

    # 9. The summary field is non-empty for all entries (10 points)
    empty_summaries = [entry.get("document_id") for entry in clues if not entry.get("summary","").strip()]
    item = {"item": "summary field non-empty for all entries", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if not empty_summaries:
        item["passed"] = True
        item["score"] = 10
        item["reason"] = "all summaries present"
    else:
        item["reason"] = f"empty summaries for IDs: {empty_summaries}"
    details.append(item)
    total += item["score"]

    # Round total to int
    total = min(int(total), 100)
    return {"total_score": total, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
