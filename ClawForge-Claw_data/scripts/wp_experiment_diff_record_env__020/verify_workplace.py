"""
verify_workplace.py for wp_experiment_diff_record_env__020
Checks that the agent produced diff_records/result.json with correct computed diffs.
Scoring: directory exist (5), file exist (5), valid JSON (10), correct structure (10),
        group count (10), each numeric field (15 each = 45), no extra fields (10),
        no spurious files (5). Total 100.
"""
import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0
    max_total = 100

    # 1. Directory diff_records exists
    dir_path = os.path.join(workspace, "diff_records")
    item = {"item": "diff_records directory exists", "max_score": 5}
    if os.path.isdir(dir_path):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "Found diff_records directory"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "Missing diff_records directory"
    details.append(item)

    # 2. result.json exists
    file_path = os.path.join(dir_path, "result.json")
    item = {"item": "result.json file exists", "max_score": 5}
    if os.path.isfile(file_path):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "Found result.json"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "Missing result.json"
        # Cannot proceed further, write score and exit
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return
    details.append(item)

    # 3. Valid JSON
    item = {"item": "Valid JSON format", "max_score": 10}
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Parsed as valid JSON"
    except (json.JSONDecodeError, Exception) as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Invalid JSON: {str(e)}"
        details.append(item)
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return
    details.append(item)

    # 4. Structure: must be a list of dicts with exactly the required fields
    item = {"item": "Structure: list of objects with group_id, accuracy_diff, latency_ms_diff, cost_usd_diff",
            "max_score": 10}
    if not isinstance(data, list):
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "Root is not a list"
    else:
        valid = True
        for rec in data:
            if not isinstance(rec, dict):
                valid = False
                break
            keys = set(rec.keys())
            required = {"group_id", "accuracy_diff", "latency_ms_diff", "cost_usd_diff"}
            if keys != required:
                valid = False
                break
        if valid and len(data) == 2:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "Two records with correct field set"
        elif valid and len(data) != 2:
            item["score"] = 5
            item["passed"] = False
            item["reason"] = f"Expected 2 records, got {len(data)}"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "Records missing or extra fields"
    details.append(item)

    # Now compute expected diffs (alpha - beta)
    # alpha: groupA (0.95,120,0.5) groupB (0.88,150,0.6)
    # beta:  groupA (0.92,130,0.55) groupB (0.90,140,0.58)
    expected = {
        "groupA": {"accuracy_diff": 0.03, "latency_ms_diff": -10.0, "cost_usd_diff": -0.05},
        "groupB": {"accuracy_diff": -0.02, "latency_ms_diff": 10.0, "cost_usd_diff": 0.02}
    }
    # Sort data by group_id
    data_sorted = sorted(data, key=lambda x: x["group_id"])

    # 5. Group IDs correct and in order
    item = {"item": "Group IDs: groupA, groupB in order", "max_score": 10}
    if len(data_sorted) == 2:
        gids = [r["group_id"] for r in data_sorted]
        if gids == ["groupA", "groupB"]:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "Correct group IDs and order"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"Got group IDs: {gids}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "Insufficient records"
    details.append(item)

    # 6-8. Numeric accuracy_diff, latency_ms_diff, cost_usd_diff for each group
    # We'll check each group separately, but combine scoring: 15 per field type across both groups
    # Simpler: check each group's three fields with tolerance, accumulate partial
    def check_field(rec, field, expected_val, tol=1e-6):
        val = rec.get(field)
        if val is None:
            return False, "missing"
        if not isinstance(val, (int, float)):
            return False, "not numeric"
        if abs(val - expected_val) <= tol:
            return True, f"{val} matches expected {expected_val}"
        else:
            return False, f"{val} differs from expected {expected_val}"

    # accuracy_diff total 15
    acc_score = 0
    acc_max = 15
    acc_reason = []
    for gid in ["groupA", "groupB"]:
        rec = next(r for r in data_sorted if r["group_id"] == gid)
        ok, msg = check_field(rec, "accuracy_diff", expected[gid]["accuracy_diff"])
        if ok:
            acc_score += 7.5
        acc_reason.append(f"{gid}: {msg}")
    item = {"item": "accuracy_diff values correct", "max_score": 15}
    if acc_score >= 15 - 1e-9:
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "All accuracy diffs correct: " + "; ".join(acc_reason)
    elif acc_score > 0:
        item["score"] = acc_score
        item["passed"] = False
        item["reason"] = "Partial accuracy: " + "; ".join(acc_reason)
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "None correct: " + "; ".join(acc_reason)
    details.append(item)

    # latency_ms_diff total 15
    lat_score = 0
    lat_max = 15
    lat_reason = []
    for gid in ["groupA", "groupB"]:
        rec = next(r for r in data_sorted if r["group_id"] == gid)
        ok, msg = check_field(rec, "latency_ms_diff", expected[gid]["latency_ms_diff"])
        if ok:
            lat_score += 7.5
        lat_reason.append(f"{gid}: {msg}")
    item = {"item": "latency_ms_diff values correct", "max_score": 15}
    if lat_score >= 15 - 1e-9:
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "All latency diffs correct: " + "; ".join(lat_reason)
    elif lat_score > 0:
        item["score"] = lat_score
        item["passed"] = False
        item["reason"] = "Partial latency: " + "; ".join(lat_reason)
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "None correct: " + "; ".join(lat_reason)
    details.append(item)

    # cost_usd_diff total 15
    cost_score = 0
    cost_max = 15
    cost_reason = []
    for gid in ["groupA", "groupB"]:
        rec = next(r for r in data_sorted if r["group_id"] == gid)
        ok, msg = check_field(rec, "cost_usd_diff", expected[gid]["cost_usd_diff"])
        if ok:
            cost_score += 7.5
        cost_reason.append(f"{gid}: {msg}")
    item = {"item": "cost_usd_diff values correct", "max_score": 15}
    if cost_score >= 15 - 1e-9:
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "All cost diffs correct: " + "; ".join(cost_reason)
    elif cost_score > 0:
        item["score"] = cost_score
        item["passed"] = False
        item["reason"] = "Partial cost: " + "; ".join(cost_reason)
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "None correct: " + "; ".join(cost_reason)
    details.append(item)

    # 9. No extra fields in any record (already checked above via set equality, but double-check)
    item = {"item": "No extra fields in records", "max_score": 10}
    extra = False
    for rec in data_sorted:
        if set(rec.keys()) != {"group_id", "accuracy_diff", "latency_ms_diff", "cost_usd_diff"}:
            extra = True
            break
    if not extra:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "All records have exactly the 4 required fields"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "Found records with extra or missing fields"
    details.append(item)

    # 10. No spurious files in diff_records (only result.json)
    item = {"item": "No extra files in diff_records", "max_score": 5}
    try:
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        if files == ["result.json"]:
            item["score"] = 5
            item["passed"] = True
            item["reason"] = "Only result.json present"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"Extra files found: {files}"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Could not list directory: {str(e)}"
    details.append(item)

    # Sum scores
    total = sum(d["score"] for d in details)
    # Clamp to max 100
    total = min(total, max_total)
    write_score(total, details)

def write_score(total, details):
    score_data = {
        "total_score": int(round(total)),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
