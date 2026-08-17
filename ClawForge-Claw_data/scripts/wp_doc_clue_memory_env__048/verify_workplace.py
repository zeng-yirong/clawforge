import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    workspace = workspace.rstrip("/")
    score_details = []
    total = 0

    # ---------- helper to add score item ----------
    def add_item(item: str, score: int, max_score: int, passed: bool, reason: str):
        nonlocal total
        total += score
        score_details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # ---------- 1. ops directory exists (5) ----------
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        add_item("ops/ directory exists", 5, 5, True, "ops directory found")
    else:
        add_item("ops/ directory exists", 0, 5, False, "ops directory not found")

    # ---------- 2. clue_list.json exists (5) ----------
    clue_path = os.path.join(ops_dir, "clue_list.json")
    if os.path.isfile(clue_path):
        add_item("clue_list.json exists", 5, 5, True, "file found")
    else:
        add_item("clue_list.json exists", 0, 5, False, "file not found")
        # if file missing, stop further checks (but still record remaining max scores as 0)
        # we'll just skip later checks by returning early? Better to continue giving 0 for rest.
        # So we assign 0 to all subsequent items manually.
        # For simplicity, we'll just set total and details as is and write early.
        # But to keep code clean, we'll return after writing missing scores for remaining.
        # Let's do it: assign 0 to remaining items.
        items_remaining = [
            ("JSON is valid", 10, 10),
            ("'clues' key exists and is a list", 10, 10),
            ("clues list length == 4", 20, 20),
            ("each clue has 'doc_id' and 'clue'", 10, 10),
            ("doc_id set matches expected IDs", 20, 20),
            ("clue strings match expected values", 20, 20)
        ]
        for item, max_s, _ in items_remaining:
            add_item(item, 0, max_s, False, "clue_list.json missing, cannot check")
        # Write score and exit
        result = {"total_score": total, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ---------- 3. JSON is valid (10) ----------
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
        add_item("JSON is valid", 10, 10, True, "valid JSON")
    except (json.JSONDecodeError, Exception) as e:
        add_item("JSON is valid", 0, 10, False, f"invalid JSON: {str(e)}")
        # No point continuing
        items_remaining = [
            ("'clues' key exists and is a list", 10, 10),
            ("clues list length == 4", 20, 20),
            ("each clue has 'doc_id' and 'clue'", 10, 10),
            ("doc_id set matches expected IDs", 20, 20),
            ("clue strings match expected values", 20, 20)
        ]
        for item, max_s, _ in items_remaining:
            add_item(item, 0, max_s, False, "JSON parse failed")
        result = {"total_score": total, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ---------- 4. 'clues' key exists and is a list (10) ----------
    if isinstance(data.get("clues"), list):
        add_item("'clues' key exists and is a list", 10, 10, True, "clues is a list")
    else:
        add_item("'clues' key exists and is a list", 0, 10, False, "missing or not a list")
        # still can continue but gives 0 for later list checks
        # better to continue but with 0 for length and content

    clues = data.get("clues")
    if not isinstance(clues, list):
        clues = []  # force empty for later checks

    # ---------- 5. clues list length == 4 (20) ----------
    expected_len = 4
    if len(clues) == expected_len:
        add_item(f"clues list length == {expected_len}", 20, 20, True, f"length is {len(clues)}")
    else:
        add_item(f"clues list length == {expected_len}", 0, 20, False, f"length is {len(clues)}")

    # ---------- 6. each clue has 'doc_id' and 'clue' (10) ----------
    all_have_keys = True
    for idx, entry in enumerate(clues):
        if not isinstance(entry, dict):
            all_have_keys = False
        elif "doc_id" not in entry or "clue" not in entry:
            all_have_keys = False
    if all_have_keys:
        add_item("each clue has 'doc_id' and 'clue'", 10, 10, True, "all entries have required keys")
    else:
        add_item("each clue has 'doc_id' and 'clue'", 0, 10, False, "some entries missing doc_id or clue")

    # ---------- 7. doc_id set matches expected IDs (20) ----------
    expected_ids = {"rpt-001", "rpt-003", "pres-002", "sample-001"}
    actual_ids = set()
    for entry in clues:
        if isinstance(entry, dict) and "doc_id" in entry:
            actual_ids.add(entry["doc_id"])
    if actual_ids == expected_ids:
        add_item("doc_id set matches expected IDs", 20, 20, True, f"IDs: {sorted(actual_ids)}")
    else:
        # partial credit? We'll give 0 for simplicity
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason = f"missing: {sorted(missing)}, extra: {sorted(extra)}"
        add_item("doc_id set matches expected IDs", 0, 20, False, reason)

    # ---------- 8. clue strings match expected values (20) ----------
    # Build dict from clues
    clue_map = {}
    for entry in clues:
        if isinstance(entry, dict) and "doc_id" in entry and "clue" in entry:
            clue_map[entry["doc_id"]] = entry["clue"]

    expected_clues = {
        "rpt-001": "CLUE:RPT001",
        "rpt-003": "CLUE:RPT003",
        "pres-002": "CLUE:PRES002",
        "sample-001": "CLUE:SAMPLE001"
    }
    all_clues_correct = True
    for doc_id, expected_clue in expected_clues.items():
        actual_clue = clue_map.get(doc_id)
        if actual_clue != expected_clue:
            all_clues_correct = False
            break
    if all_clues_correct:
        add_item("clue strings match expected values", 20, 20, True, "all clues correct")
    else:
        add_item("clue strings match expected values", 0, 20, False, "one or more clue values mismatch")

    # ---------- write final score ----------
    result = {"total_score": total, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
