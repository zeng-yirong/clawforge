import sys
import json
import os
import pathlib

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0

    # ------------------------------------------------------------------
    # 1) Check that ops/clue_list.json exists
    # ------------------------------------------------------------------
    clue_path = "ops/clue_list.json"
    if not os.path.isfile(clue_path):
        details.append({
            "item": "File existence",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"File {clue_path} not found."
        })
        # Stop early – missing file = zero total
        total_score = 0
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    else:
        details.append({
            "item": "File existence",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"{clue_path} exists."
        })
        total_score += 10

    # ------------------------------------------------------------------
    # 2) JSON is valid
    # ------------------------------------------------------------------
    data = load_json(clue_path)
    if data is None:
        details.append({
            "item": "JSON validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"{clue_path} is not valid JSON."
        })
        total_score = 10  # only file existence
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    else:
        details.append({
            "item": "JSON validity",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON is valid."
        })
        total_score += 10

    # ------------------------------------------------------------------
    # 3) Contains key "clues" and it's a list
    # ------------------------------------------------------------------
    if not isinstance(data, dict) or "clues" not in data:
        details.append({
            "item": "Structure (clues key)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Top-level must be dict with 'clues' key."
        })
        total_score = 20
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    clues = data["clues"]
    if not isinstance(clues, list):
        details.append({
            "item": "Structure (clues is list)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "'clues' must be a list."
        })
        total_score = 20
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    details.append({
        "item": "Structure (clues key & list)",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "'clues' key present and is a list."
    })
    total_score += 10

    # ------------------------------------------------------------------
    # Build expected list from original files
    # ------------------------------------------------------------------
    target = "HelioSync Edge Inference Fabric"
    expected = []   # list of dicts with keys: source_type, document_id, title, clue_summary

    # Reports
    reports_data = load_json("data/reports/reports.json")
    if reports_data and "reports" in reports_data:
        for r in reports_data["reports"]:
            aliases = r.get("solution_aliases")
            if isinstance(aliases, list) and target in aliases:
                expected.append({
                    "source_type": "report",
                    "document_id": r["report_id"],
                    "title": r["title"],
                    "clue_summary": r["summary"]
                })

    # Presentations
    pres_data = load_json("data/presentations/presentations.json")
    if pres_data and "presentations" in pres_data:
        for p in pres_data["presentations"]:
            aliases = p.get("solution_aliases")
            if isinstance(aliases, list) and target in aliases:
                expected.append({
                    "source_type": "presentation",
                    "document_id": p["presentation_id"],
                    "title": p["title"],
                    "clue_summary": p["summary"]
                })

    # Media samples
    media_data = load_json("data/media_samples/media_samples.json")
    if media_data and "media_samples" in media_data:
        for m in media_data["media_samples"]:
            aliases = m.get("solution_aliases")
            if isinstance(aliases, list) and target in aliases:
                expected.append({
                    "source_type": "media_sample",
                    "document_id": m["sample_id"],
                    "title": m["title"],
                    "clue_summary": m["summary"]
                })

    # Build lookup by document_id
    expected_by_id = {e["document_id"]: e for e in expected}
    expected_ids = set(expected_by_id.keys())

    # ------------------------------------------------------------------
    # 4) Number of clues matches expected
    # ------------------------------------------------------------------
    if len(clues) != len(expected):
        details.append({
            "item": "Number of clues",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected {len(expected)} clues, found {len(clues)}."
        })
        total_score += 0
    else:
        details.append({
            "item": "Number of clues",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Correct number of clues ({len(expected)})."
        })
        total_score += 10

    # ------------------------------------------------------------------
    # 5) Each clue has required fields
    # ------------------------------------------------------------------
    required_fields = ["source_type", "document_id", "title", "clue_summary"]
    field_check_passed = True
    for i, clue in enumerate(clues):
        if not isinstance(clue, dict):
            field_check_passed = False
            continue
        missing = [f for f in required_fields if f not in clue]
        if missing:
            field_check_passed = False
    if field_check_passed:
        details.append({
            "item": "Required fields in each clue",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All clues contain required fields."
        })
        total_score += 20
    else:
        details.append({
            "item": "Required fields in each clue",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Some clues are missing required fields (source_type, document_id, title, clue_summary)."
        })
        total_score += 0

    # ------------------------------------------------------------------
    # 6) Field values match original data (only if fields present)
    # ------------------------------------------------------------------
    value_match_passed = True
    value_errors = []
    for clue in clues:
        if not isinstance(clue, dict):
            value_match_passed = False
            continue
        doc_id = clue.get("document_id")
        if doc_id not in expected_by_id:
            value_errors.append(f"document_id {doc_id} not expected.")
            value_match_passed = False
            continue
        exp = expected_by_id[doc_id]
        # compare all fields
        for key in required_fields:
            if clue.get(key) != exp[key]:
                value_errors.append(f"Field '{key}' for doc {doc_id}: expected '{exp[key]}', got '{clue.get(key)}'.")
                value_match_passed = False

    if value_match_passed:
        details.append({
            "item": "Field values match original documents",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "All clue field values exactly match the source documents."
        })
        total_score += 30
    else:
        details.append({
            "item": "Field values match original documents",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Field value mismatches: {'; '.join(value_errors[:3])}"
        })
        total_score += 0

    # ------------------------------------------------------------------
    # 7) No extra clues (clues not in expected)
    # ------------------------------------------------------------------
    extra_ids = []
    for clue in clues:
        if isinstance(clue, dict):
            doc_id = clue.get("document_id")
            if doc_id not in expected_ids:
                extra_ids.append(doc_id)
    if extra_ids:
        details.append({
            "item": "No extra clues",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found unexpected document_ids: {extra_ids}."
        })
        total_score += 0
    else:
        details.append({
            "item": "No extra clues",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "No extra clues present."
        })
        total_score += 10

    # ------------------------------------------------------------------
    # Write final score
    # ------------------------------------------------------------------
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
