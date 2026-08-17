import json
import os
import sys

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def verify(workspace):
    score = 0
    details = []

    # 1. Check ops/clue_summary.json exists
    target = os.path.join(workspace, "ops", "clue_summary.json")
    if not os.path.isfile(target):
        return {
            "total_score": 0,
            "details": [{"item": "File existence", "score": 0, "max_score": 100, "passed": False, "reason": "ops/clue_summary.json not found"}]
        }
    details.append({"item": "File existence", "score": 5, "max_score": 5, "passed": True, "reason": "ops/clue_summary.json exists"})
    score += 5

    # 2. Parse JSON
    try:
        data = load_json(target)
    except Exception as e:
        return {
            "total_score": score,
            "details": details + [{"item": "JSON validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"}]
        }
    details.append({"item": "JSON validity", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
    score += 10

    if not isinstance(data, list):
        return {
            "total_score": score,
            "details": details + [{"item": "Data structure", "score": 0, "max_score": 5, "passed": False, "reason": "Top-level must be an array"}]
        }
    details.append({"item": "Data structure", "score": 5, "max_score": 5, "passed": True, "reason": "Top-level is a list"})
    score += 5

    # 3. Expected records based on env_builder:
    # Reports: RPT-2026-001, RPT-2026-002, RPT-2026-003 (skipping 004 and 005)
    # Presentations: PRES-2026-001, PRES-2026-002 (skipping 003)
    # Media samples: MED-2026-001 (last occurrence), MED-2026-002 (skipping 003)
    # Mapping: as per solution_matching_notes.md
    expected = [
        {"document_id": "RPT-2026-001", "document_type": "report", "clue_id": "HSEIF-REP-001"},
        {"document_id": "RPT-2026-002", "document_type": "report", "clue_id": "HSEIF-REP-002"},
        {"document_id": "RPT-2026-003", "document_type": "report", "clue_id": "HSEIF-REP-003"},
        {"document_id": "PRES-2026-001", "document_type": "presentation", "clue_id": "HSEIF-PRES-001"},
        {"document_id": "PRES-2026-002", "document_type": "presentation", "clue_id": "HSEIF-PRES-002"},
        {"document_id": "MED-2026-001", "document_type": "media_sample", "clue_id": "HSEIF-MED-001"},
        {"document_id": "MED-2026-002", "document_type": "media_sample", "clue_id": "HSEIF-MED-002"},
    ]

    # Check record count
    if len(data) != len(expected):
        details.append({"item": "Record count", "score": 0, "max_score": 20, "passed": False,
                        "reason": f"Expected {len(expected)} records, got {len(data)}"})
        score += 0
    else:
        details.append({"item": "Record count", "score": 20, "max_score": 20, "passed": True,
                        "reason": f"Correct count {len(data)}"})
        score += 20

    # Sort actual data by document_type then document_id for comparison
    sorted_actual = sorted(data, key=lambda x: (x.get("document_type",""), x.get("document_id","")))

    # Check each record
    matched = 0
    for e, a in zip(expected, sorted_actual):
        if (a.get("document_id") == e["document_id"] and
            a.get("document_type") == e["document_type"] and
            a.get("clue_id") == e["clue_id"]):
            matched += 1
    if matched == len(expected):
        details.append({"item": "Record content", "score": 50, "max_score": 50, "passed": True,
                        "reason": "All records match expected mapping exactly"})
        score += 50
    else:
        details.append({"item": "Record content", "score": 0, "max_score": 50, "passed": False,
                        "reason": f"Only {matched}/{len(expected)} records match expected mapping"})

    # Check no extra records
    if len(data) > len(expected):
        extra_count = len(data) - len(expected)
        details.append({"item": "No extra records", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"Found {extra_count} extra record(s)"})
    else:
        details.append({"item": "No extra records", "score": 10, "max_score": 10, "passed": True,
                        "reason": "No extra records present"})
        score += 10

    # Final score
    total = min(score, 100)
    return {
        "total_score": total,
        "details": details +
            [{"item": "Final score", "score": total, "max_score": 100, "passed": total >= 80,
              "reason": f"Total {total}/100"}]
    }

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
