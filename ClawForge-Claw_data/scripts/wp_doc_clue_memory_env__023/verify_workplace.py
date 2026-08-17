import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def check(condition, item, score, max_score, reason):
    global total_score
    if condition:
        total_score += score
        score_details.append({"item": item, "score": score, "max_score": max_score, "passed": True, "reason": reason})
    else:
        score_details.append({"item": item, "score": 0, "max_score": max_score, "passed": False, "reason": reason})

# --- Step 1: check existence of ops/final_clues.json
clues_path = os.path.join(workspace, "ops", "final_clues.json")
check(os.path.exists(clues_path), "ops/final_clues.json exists", 10, 10, "File found" if os.path.exists(clues_path) else "File missing")

if not os.path.exists(clues_path):
    # Cannot proceed further
    score_details.append({"item": "Further checks skipped (file missing)", "score": 0, "max_score": 90, "passed": False, "reason": "Output file missing"})
    total_score = total_score  # already 0
else:
    # --- Step 2: valid JSON
    try:
        with open(clues_path, "r") as f:
            clues_data = json.load(f)
        check(True, "JSON is valid", 10, 10, "Valid JSON")
    except (json.JSONDecodeError, ValueError) as e:
        check(False, "JSON is valid", 0, 10, f"Invalid JSON: {e}")
        # stop further parsing
        score_details.append({"item": "Further checks skipped (invalid JSON)", "score": 0, "max_score": 80, "passed": False, "reason": "JSON parse error"})
        total_score = total_score  # already 10 or 0
        # write result and exit
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": min(total_score,100), "details": score_details}, f, indent=2)
        sys.exit(0)

    # --- Step 3: structure – must be a list of dicts with 'id' and 'clue'
    structure_ok = isinstance(clues_data, list) and all(isinstance(item, dict) and "id" in item and "clue" in item for item in clues_data)
    check(structure_ok, "Data is list of objects with 'id' and 'clue'", 10, 10, "Structure OK" if structure_ok else "Structure invalid")

    if not structure_ok:
        # can't check further
        score_details.append({"item": "Further checks skipped (wrong structure)", "score": 0, "max_score": 70, "passed": False, "reason": "Structure invalid"})
        total_score = total_score  # already 20 or less
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": min(total_score,100), "details": score_details}, f, indent=2)
        sys.exit(0)

    # --- Step 4: length check – expected 9 entries
    expected_ids = set(["RPT-001","RPT-003","RPT-005","PRES-001","PRES-003","PRES-004","MED-001","MED-003","MED-004"])
    actual_ids = set(item["id"] for item in clues_data)
    length_ok = len(clues_data) == 9
    check(length_ok, "Exactly 9 entries", 20, 20, f"Found {len(clues_data)} entries" if length_ok else f"Found {len(clues_data)} entries, expected 9")

    # --- Step 5: content correctness – each id must have correct clue
    # load source data to get correct summaries
    def load_json(filename):
        with open(os.path.join(workspace, filename), "r") as f:
            data = json.load(f)["data"]
            return data

    source_data = {}
    # reports
    for rec in load_json("data/reports/reports.json"):
        try:
            aliases = rec.get("solution_aliases", [])
            if isinstance(aliases, list) and "HelioSync Edge Inference Fabric" in aliases:
                source_data[rec["report_id"]] = rec["summary"]
        except:
            pass
    # presentations
    for rec in load_json("data/presentations/presentations.json"):
        aliases = rec.get("solution_aliases", [])
        if isinstance(aliases, list) and "HelioSync Edge Inference Fabric" in aliases:
            source_data[rec["presentation_id"]] = rec["summary"]
    # media_samples
    for rec in load_json("data/media_samples/media_samples.json"):
        aliases = rec.get("solution_aliases", [])
        if isinstance(aliases, list) and "HelioSync Edge Inference Fabric" in aliases:
            source_data[rec["sample_id"]] = rec["summary"]

    content_ok = True
    for expected_id, expected_summary in source_data.items():
        found = False
        for item in clues_data:
            if item["id"] == expected_id:
                found = True
                if item["clue"] != expected_summary:
                    content_ok = False
                    break
        if not found:
            content_ok = False
            break

    # also check no extra ids
    extra_ids = actual_ids - set(source_data.keys())
    if extra_ids:
        content_ok = False

    check(content_ok, "All IDs and clues match source data", 30, 30, "Content correct" if content_ok else "Mismatch in IDs or clues")

    # --- Step 6: exclusion of decoys (records with "HelioSync Edge" but not full string)
    decoy_ids = set(["RPT-002", "PRES-002", "MED-002"])
    decoys_found = actual_ids & decoy_ids
    decoy_ok = len(decoys_found) == 0
    check(decoy_ok, "No decoy records included", 10, 10, "No decoys" if decoy_ok else f"Decoys found: {decoys_found}")

    # --- Step 7: exclusion of dirty/malformed records (RPT-DIRTY)
    dirty_ids = set(["RPT-DIRTY"])
    dirty_found = actual_ids & dirty_ids
    dirty_ok = len(dirty_found) == 0
    check(dirty_ok, "No malformed records included", 10, 10, "No dirty records" if dirty_ok else f"Dirty records found: {dirty_found}")

# --- Finalize
total_score = min(total_score, 100)
result = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"Verification complete. Score: {total_score}/100")
