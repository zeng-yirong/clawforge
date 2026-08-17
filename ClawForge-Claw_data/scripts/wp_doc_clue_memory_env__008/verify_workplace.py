#!/usr/bin/env python3
"""Verify agent output for wp_doc_clue_memory_env__008.

Checks:
- ops/clue_list.json exists and is valid JSON
- Contains exactly the expected documents (3 reports, 2 presentations? Wait, we had:
  reports: rpt_101 (HelioSync), rpt_102 (HelioSync + AeroMind) -> should be included because solution_aliases includes HelioSync. rpt_103 (QuantumSafe) excluded.
  presentations: pres_201 (HelioSync) included; pres_202 (AeroMind) excluded; pres_203 (QuantumSafe) excluded.
  media_samples: media_301, media_302 (HelioSync) included; media_303 excluded.
  So total: 1 report? Actually rpt_101 and rpt_102 both have HelioSync → 2 reports.
  1 presentation (pres_201), 2 media samples → total 5 document entries.
- Each entry has 'type', 'document_id', 'clues' (list of strings).
- The clues must match exactly the four bullets defined in solution_matching_notes.md for HelioSync.
- No extra entries for other solutions.
- Score breakdown.

Usage: python verify_workplace.py [workspace_path]
"""
import sys
import json
import os
import re

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        return None

def main():
    details = []
    total_score = 0
    max_score_total = 100

    # 1. File existence (10 pts)
    clue_path = os.path.join(WORKSPACE, "ops/clue_list.json")
    if not os.path.isfile(clue_path):
        details.append({"item": "ops/clue_list.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        print(json.dumps({"total_score": 0, "details": details}))
        return
    details.append({"item": "ops/clue_list.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File present"})
    total_score += 10

    # 2. Valid JSON (10 pts)
    data = load_json(clue_path)
    if data is None:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "Could not parse JSON"})
        print(json.dumps({"total_score": total_score, "details": details}))
        return
    details.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully"})
    total_score += 10

    # 3. Structure: must be a list of entries (10 pts)
    if not isinstance(data, list):
        details.append({"item": "Top-level list", "score": 0, "max_score": 10, "passed": False, "reason": "Expected list, got " + str(type(data))})
        print(json.dumps({"total_score": total_score, "details": details}))
        return
    details.append({"item": "Top-level list", "score": 10, "max_score": 10, "passed": True, "reason": "Is a list"})
    total_score += 10

    # 4. Each entry has required fields (10 pts)
    required_fields = {"type", "document_id", "clues"}
    all_entries_valid = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            all_entries_valid = False
            break
        missing = required_fields - set(entry.keys())
        if missing:
            all_entries_valid = False
            break
        if not isinstance(entry.get("clues"), list):
            all_entries_valid = False
            break
    if not all_entries_valid:
        details.append({"item": "Each entry has type, document_id, clues (list)", "score": 0, "max_score": 10, "passed": False, "reason": "Some entry missing required fields or clues not list"})
        total_score += 0
    else:
        details.append({"item": "Each entry has type, document_id, clues (list)", "score": 10, "max_score": 10, "passed": True, "reason": "All entries well-formed"})
        total_score += 10

    # 5. Correct number of entries (exactly 5) (20 pts)
    expected_count = 5  # 2 reports + 1 presentation + 2 media
    actual_count = len(data)
    if actual_count == expected_count:
        details.append({"item": "Number of entries", "score": 20, "max_score": 20, "passed": True, "reason": f"Found {actual_count} entries"})
        total_score += 20
    else:
        details.append({"item": "Number of entries", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_count}, got {actual_count}"})

    # 6. All expected document IDs present and no extras (25 pts)
    # Build mapping from type+id to clues from matching notes.
    expected_entries = {
        ("report", "rpt_101"): [
            "Latency under 5ms at edge",
            "Supports ONNX Runtime 1.17+",
            "Native ARM NEON acceleration",
            "Integrated with Kubeless v2.3"
        ],
        ("report", "rpt_102"): [
            "Latency under 5ms at edge",
            "Supports ONNX Runtime 1.17+",
            "Native ARM NEON acceleration",
            "Integrated with Kubeless v2.3"
        ],
        ("presentation", "pres_201"): [
            "Latency under 5ms at edge",
            "Supports ONNX Runtime 1.17+",
            "Native ARM NEON acceleration",
            "Integrated with Kubeless v2.3"
        ],
        ("media_sample", "media_301"): [
            "Latency under 5ms at edge",
            "Supports ONNX Runtime 1.17+",
            "Native ARM NEON acceleration",
            "Integrated with Kubeless v2.3"
        ],
        ("media_sample", "media_302"): [
            "Latency under 5ms at edge",
            "Supports ONNX Runtime 1.17+",
            "Native ARM NEON acceleration",
            "Integrated with Kubeless v2.3"
        ]
    }
    # Build actual mapping
    actual_dict = {}
    for entry in data:
        key = (entry.get("type"), entry.get("document_id"))
        actual_dict[key] = entry.get("clues", [])

    passed6 = True
    missing = []
    extra = []
    clue_mismatch = []
    for key, expected_clues in expected_entries.items():
        if key not in actual_dict:
            missing.append(key)
            passed6 = False
        else:
            # Compare clues as sets (order doesn't matter)
            if set(actual_dict[key]) != set(expected_clues):
                clue_mismatch.append(key)
                passed6 = False
    for key in actual_dict:
        if key not in expected_entries:
            extra.append(key)
            passed6 = False

    if passed6:
        details.append({"item": "All expected documents with correct clues, no extras", "score": 25, "max_score": 25, "passed": True, "reason": "Perfect match"})
        total_score += 25
    else:
        reasons = []
        if missing:
            reasons.append(f"missing: {missing}")
        if extra:
            reasons.append(f"extra: {extra}")
        if clue_mismatch:
            reasons.append(f"clue mismatch: {clue_mismatch}")
        details.append({"item": "All expected documents with correct clues, no extras", "score": 0, "max_score": 25, "passed": False, "reason": "; ".join(reasons)})

    # 7. Bonus: no duplicate entries (we didn't penalize earlier, but check)
    # Actually duplicate would have caused extra detection, already covered.
    # Additional: clues must not contain other solution clues (e.g., "Flight endurance") – that would be extra entry or wrong clues.
    # Already covered because we compare sets. So fine.

    # 8. (already counted) Output score
    # Clamp to 100
    total_score = min(total_score, 100)
    score_data = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)
    print(json.dumps(score_data))

if __name__ == "__main__":
    main()
