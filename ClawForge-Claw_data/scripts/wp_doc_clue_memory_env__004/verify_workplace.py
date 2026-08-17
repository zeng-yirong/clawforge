import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(workspace, rel_path)
    if not os.path.exists(full):
        return None, f"File not found: {rel_path}"
    try:
        with open(full, "r") as f:
            data = json.load(f)
        return data, None
    except (json.JSONDecodeError, Exception) as e:
        return None, f"Invalid JSON: {e}"

def main():
    details = []
    total_score = 0

    # 1. file exists (10 points)
    data, err = load_json("ops/clue_list.json")
    if data is not None:
        details.append({"item": "ops/clue_list.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        details.append({"item": "ops/clue_list.json exists", "score": 0, "max_score": 10, "passed": False, "reason": err})
        # No point continuing if file missing
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. is a list? (10 points)
    if isinstance(data, list):
        details.append({"item": "Top-level is a JSON list", "score": 10, "max_score": 10, "passed": True, "reason": "Valid list"})
        total_score += 10
    else:
        details.append({"item": "Top-level is a JSON list", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected list, got {type(data).__name__}"})
        # Can't proceed meaningfully
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. correct number of entries (10 points)
    expected_count = 4
    actual_count = len(data)
    if actual_count == expected_count:
        details.append({"item": f"Number of clue entries equals {expected_count}", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {actual_count}"})
        total_score += 10
    else:
        details.append({"item": f"Number of clue entries equals {expected_count}", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_count}, got {actual_count}"})

    # 4. each entry has 'id' and 'clue' fields (10 points)
    field_ok = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict) or "id" not in entry or "clue" not in entry:
            field_ok = False
            break
    if field_ok:
        details.append({"item": "All entries have 'id' and 'clue' fields", "score": 10, "max_score": 10, "passed": True, "reason": "Fields present"})
        total_score += 10
    else:
        details.append({"item": "All entries have 'id' and 'clue' fields", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required fields in some entries"})

    # 5. exact set of ids (20 points)
    expected_ids = {"report-001", "report-003", "presentation-002", "media-001"}
    actual_ids = {entry.get("id") for entry in data if isinstance(entry, dict)}
    if actual_ids == expected_ids:
        details.append({"item": "Set of document IDs matches expected", "score": 20, "max_score": 20, "passed": True, "reason": f"IDs: {sorted(actual_ids)}"})
        total_score += 20
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason = []
        if missing: reason.append(f"Missing: {missing}")
        if extra: reason.append(f"Extra: {extra}")
        details.append({"item": "Set of document IDs matches expected", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reason)})

    # 6. correct clue texts (30 points)
    expected_clues = {
        "report-001": "Analysis of HelioSync deployment patterns in manufacturing.",
        "report-003": "HelioSync used in smart factories for predictive maintenance.",
        "presentation-002": "Overview of HelioSync Edge Inference Fabric features.",
        "media-001": "Podcast transcript discussing HelioSync Edge Inference Fabric deployment."
    }
    clue_ok = True
    for entry in data:
        if isinstance(entry, dict):
            eid = entry.get("id")
            actual_clue = entry.get("clue")
            expected_clue = expected_clues.get(eid)
            if expected_clue is None or actual_clue != expected_clue:
                clue_ok = False
                break
    if clue_ok:
        details.append({"item": "All clue texts match expected summaries", "score": 30, "max_score": 30, "passed": True, "reason": "Exact match"})
        total_score += 30
    else:
        mismatches = []
        for entry in data:
            if isinstance(entry, dict):
                eid = entry.get("id")
                actual = entry.get("clue")
                expected = expected_clues.get(eid)
                if expected is not None and actual != expected:
                    mismatches.append(f"{eid}: got '{actual}', expected '{expected}'")
        details.append({"item": "All clue texts match expected summaries", "score": 0, "max_score": 30, "passed": False, "reason": "Mismatches: " + "; ".join(mismatches[:3])})

    # 7. no extra fields (10 points)
    extra_field_ok = True
    for entry in data:
        if isinstance(entry, dict):
            if set(entry.keys()) != {"id", "clue"}:
                extra_field_ok = False
                break
    if extra_field_ok:
        details.append({"item": "No extra fields in entries", "score": 10, "max_score": 10, "passed": True, "reason": "Only id and clue present"})
        total_score += 10
    else:
        details.append({"item": "No extra fields in entries", "score": 0, "max_score": 10, "passed": False, "reason": "Some entries contain unexpected fields"})

    # Clamp total to 100
    total_score = min(total_score, 100)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
