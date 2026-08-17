import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0

    # 1. Check clue_list.json exists
    clue_path = os.path.join(workspace, "ops/clue_list.json")
    exists = os.path.isfile(clue_path)
    score_details.append({
        "item": "ops/clue_list.json exists",
        "max_score": 10,
        "score": 10 if exists else 0,
        "passed": exists,
        "reason": "File found" if exists else "Missing ops/clue_list.json"
    })
    if not exists:
        # No point continuing
        write_score(score_details)
        return

    # 2. Parse JSON
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
        json_ok = True
        reason = "Valid JSON"
    except (json.JSONDecodeError, Exception) as e:
        json_ok = False
        reason = f"Invalid JSON: {e}"
    score_details.append({
        "item": "JSON format valid",
        "max_score": 10,
        "score": 10 if json_ok else 0,
        "passed": json_ok,
        "reason": reason
    })
    if not json_ok:
        write_score(score_details)
        return

    # 3. solution field
    sol_ok = isinstance(data, dict) and data.get("solution") == "HelioSync Edge Inference Fabric"
    score_details.append({
        "item": "solution field correct",
        "max_score": 10,
        "score": 10 if sol_ok else 0,
        "passed": sol_ok,
        "reason": "Correct solution name" if sol_ok else f"Expected 'HelioSync Edge Inference Fabric', got {data.get('solution')}"
    })

    # 4. clues is a list
    if not isinstance(data.get("clues"), list):
        score_details.append({
            "item": "clues array present",
            "max_score": 20,
            "score": 0,
            "passed": False,
            "reason": "Missing 'clues' array"
        })
        write_score(score_details)
        return

    clues = data["clues"]

    # 5. count check
    # Expected clues: rpt_001, rpt_003, pres_101, med_201 (4 total)
    expected_ids = {"rpt_001", "rpt_003", "pres_101", "med_201"}
    found_ids = set()
    for c in clues:
        if isinstance(c, dict) and "source_id" in c:
            found_ids.add(c["source_id"])

    count_ok = len(clues) == len(expected_ids) and found_ids == expected_ids
    # Partial: count match gets half score
    count_score = 20 if count_ok else (10 if len(clues) == len(expected_ids) else 0)
    score_details.append({
        "item": "clue count and IDs match expected",
        "max_score": 20,
        "score": count_score,
        "passed": count_ok,
        "reason": f"Found {len(clues)} clues, expected {len(expected_ids)}; IDs: {found_ids}" if not count_ok else "All expected clues present, no extras"
    })

    # 6. Each clue has required fields
    field_ok = True
    for i, c in enumerate(clues):
        if not isinstance(c, dict):
            field_ok = False
            break
        if "source_type" not in c or "source_id" not in c or "summary" not in c:
            field_ok = False
            break
        allowed_types = {"report", "presentation", "media_sample"}
        if c["source_type"] not in allowed_types:
            field_ok = False
            break
    score_details.append({
        "item": "each clue contains source_type, source_id, summary",
        "max_score": 20,
        "score": 20 if field_ok else 0,
        "passed": field_ok,
        "reason": "All clues have required fields" if field_ok else "One or more clues missing required fields"
    })

    # 7. No extra unexpected clues (already covered by count check, but give remaining points)
    extra_ok = len(found_ids - expected_ids) == 0
    score_details.append({
        "item": "no extra clues (beyond expected set)",
        "max_score": 10,
        "score": 10 if extra_ok else 0,
        "passed": extra_ok,
        "reason": "No extra clues" if extra_ok else f"Extra unexpected IDs: {found_ids - expected_ids}"
    })

    # Compute total
    total = sum(d["score"] for d in score_details)
    write_score(score_details, total)

def write_score(details, total=0):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
