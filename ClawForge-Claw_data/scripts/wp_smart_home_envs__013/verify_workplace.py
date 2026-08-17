import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. Check output file existence
    expected_path = os.path.join(workspace, "ops", "conflicts.json")
    item1 = {"item": "Output file existence (ops/conflicts.json)", "max_score": 10}
    if os.path.isfile(expected_path):
        score += 10
        details.append({**item1, "score": 10, "passed": True, "reason": "File found"})
    else:
        details.append({**item1, "score": 0, "passed": False, "reason": "File not found"})
        final_score = min(score, 100)
        res = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(res, f, indent=2)
        return

    # 2. Parse JSON and validate structure
    item2 = {"item": "JSON format and structure", "max_score": 15}
    conflicts = []
    try:
        with open(expected_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "conflicts" not in data:
            raise ValueError("Missing 'conflicts' key")
        conflicts = data["conflicts"]
        if not isinstance(conflicts, list):
            raise ValueError("'conflicts' is not a list")
        for entry in conflicts:
            if not isinstance(entry, dict):
                raise ValueError("Each conflict must be a dict")
            if "device_id" not in entry:
                raise ValueError("Missing device_id")
            if "reason" not in entry:
                raise ValueError("Missing reason")
        details.append({**item2, "score": 15, "passed": True, "reason": "Valid JSON with required fields"})
        score += 15
    except Exception as e:
        details.append({**item2, "score": 0, "passed": False, "reason": f"Parsing error: {e}"})
        conflicts = []

    # 3. Check correct device IDs
    item3 = {"item": "Correct device IDs (ac_bedroom_01, humidifier_bedroom_01)", "max_score": 60}
    expected_ids = {"ac_bedroom_01", "humidifier_bedroom_01"}
    actual_ids = {entry["device_id"] for entry in conflicts if isinstance(entry, dict)}
    if actual_ids == expected_ids:
        score += 60
        details.append({**item3, "score": 60, "passed": True, "reason": "Both required device IDs present, no extras"})
    elif not actual_ids:
        details.append({**item3, "score": 0, "passed": False, "reason": "No device IDs found"})
    else:
        correct = len(actual_ids & expected_ids)
        p_score = correct * 30
        extras = actual_ids - expected_ids
        reason = f"Correct: {correct}/2; Extra devices: {', '.join(extras) if extras else 'none'}"
        details.append({**item3, "score": p_score, "passed": p_score == 60, "reason": reason})
        score += p_score

    # 4. Check that reasons are non-empty
    item4 = {"item": "Reasons provided and non-empty", "max_score": 15}
    all_nonempty = all(entry.get("reason", "").strip() for entry in conflicts if isinstance(entry, dict))
    if all_nonempty and conflicts:
        score += 15
        details.append({**item4, "score": 15, "passed": True, "reason": "All reasons non-empty"})
    elif not conflicts:
        details.append({**item4, "score": 0, "passed": False, "reason": "No entries to check"})
    else:
        empty_count = sum(1 for entry in conflicts if not entry.get("reason", "").strip())
        details.append({**item4, "score": 0, "passed": False, "reason": f"{empty_count} entries with empty/missing reason"})

    # Finalize score
    final_score = min(score, 100)
    res = {"total_score": final_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(res, f, indent=2)

if __name__ == "__main__":
    main()
