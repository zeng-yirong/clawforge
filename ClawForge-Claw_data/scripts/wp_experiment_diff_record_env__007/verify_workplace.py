import sys
import os
import json
import csv
import math

def read_and_clean_csv(filepath):
    """
    Read experiment CSV, clean duplicates, missing, and non-numeric rows.
    Returns dict: {batch_id: {group_id: (accuracy, latency, cost)}}
    Uses first occurrence per (batch, group) after cleaning.
    """
    cleaned = {}
    seen = set()
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch = row.get('batch_id', '').strip()
            group = row.get('group_id', '').strip()
            acc_str = row.get('accuracy', '').strip()
            lat_str = row.get('latency_ms', '').strip()
            cost_str = row.get('cost_usd', '').strip()

            # Skip if any required field is empty
            if not batch or not group or not acc_str or not lat_str or not cost_str:
                continue

            # Try converting to float
            try:
                acc = float(acc_str)
                lat = float(lat_str)
                cost = float(cost_str)
            except ValueError:
                continue

            # Optional sanity checks (latency > 0, accuracy 0-1, cost > 0)
            if lat <= 0 or not (0 <= acc <= 1) or cost <= 0:
                continue

            key = (batch, group)
            if key in seen:
                continue  # skip duplicate
            seen.add(key)

            if batch not in cleaned:
                cleaned[batch] = {}
            cleaned[batch][group] = (acc, lat, cost)

    return cleaned

def compute_expected_diff(cleaned):
    """Compute diff record between exp_v2 and exp_v1 for common groups."""
    batch1 = 'exp_v1'
    batch2 = 'exp_v2'
    if batch1 not in cleaned or batch2 not in cleaned:
        return []  # missing batches -> no diff possible

    groups1 = set(cleaned[batch1].keys())
    groups2 = set(cleaned[batch2].keys())
    common = groups1 & groups2

    diffs = []
    for g in sorted(common):
        a1, l1, c1 = cleaned[batch1][g]
        a2, l2, c2 = cleaned[batch2][g]
        diffs.append({
            "group_id": g,
            "accuracy_diff": round(a2 - a1, 6),
            "latency_ms_diff": round(l2 - l1, 6),
            "cost_usd_diff": round(c2 - c1, 6)
        })
    return diffs

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    total = 0

    # 1. Check output directory and file exist (10 points)
    ops_dir = os.path.join(workspace, "ops")
    result_file = os.path.join(ops_dir, "experiment_diff.json")
    exists = os.path.isfile(result_file)
    scores.append({
        "item": "Output file ops/experiment_diff.json exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File found" if exists else "File not found"
    })
    if not exists:
        # If file missing, no further checks possible
        total = sum(s["score"] for s in scores)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        return

    # 2. Parse JSON (10 points)
    try:
        with open(result_file) as f:
            output = json.load(f)
        valid_json = True
        reason = "Valid JSON"
    except (json.JSONDecodeError, Exception) as e:
        valid_json = False
        reason = f"Invalid JSON: {e}"
    scores.append({
        "item": "Result file is valid JSON",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": reason
    })
    if not valid_json:
        total = sum(s["score"] for s in scores)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        return

    # 3. Check required fields in JSON (10 points)
    expected_keys = {"diff_records"}
    actual_keys = set(output.keys())
    has_records = "diff_records" in actual_keys
    records = output.get("diff_records", [])
    items_ok = has_records and isinstance(records, list) and len(records) > 0
    scores.append({
        "item": "JSON contains 'diff_records' list with at least one entry",
        "score": 10 if items_ok else 0,
        "max_score": 10,
        "passed": items_ok,
        "reason": "OK" if items_ok else f"Missing 'diff_records' or empty list"
    })

    # 4. Compare with expected diff (60 points: 20 for set correctness, 40 for values)
    csv_path = os.path.join(workspace, "data/experiments/experiment_results.csv")
    if not os.path.isfile(csv_path):
        # cannot compute expected -> fail
        scores.append({
            "item": "Source CSV exists (required to compute expected)",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "CSV not found, cannot verify"
        })
    else:
        cleaned = read_and_clean_csv(csv_path)
        expected_diffs = compute_expected_diff(cleaned)
        if not expected_diffs:
            scores.append({
                "item": "Expected diff could be computed",
                "score": 0,
                "max_score": 60,
                "passed": False,
                "reason": "Cannot find both exp_v1 and exp_v2 in cleaned data"
            })
        else:
            # Check set of group_ids
            expected_groups = {d["group_id"] for d in expected_diffs}
            actual_groups = {d.get("group_id") for d in records}
            set_match = expected_groups == actual_groups and len(actual_groups) == len(expected_diffs)
            scores.append({
                "item": "Group IDs in diff_records match expected set",
                "score": 20 if set_match else 0,
                "max_score": 20,
                "passed": set_match,
                "reason": f"Expected {sorted(expected_groups)}, got {sorted(actual_groups)}" if not set_match else "Match"
            })

            # Check numerical values for each group (40 points total, 13.33 per group, round to 13 each, 39+1?)
            # We'll allocate 40 points: 13 for first, 13 for second, 14 for third (total 40)
            value_scores = 0
            group_weights = [13, 13, 14]  # matches sorted common groups
            for i, g in enumerate(sorted(expected_groups)):
                expected = None
                for d in expected_diffs:
                    if d["group_id"] == g:
                        expected = d
                        break
                actual = None
                for d in records:
                    if d.get("group_id") == g:
                        actual = d
                        break
                if expected and actual:
                    ok = True
                    for key in ["accuracy_diff", "latency_ms_diff", "cost_usd_diff"]:
                        exp_val = expected[key]
                        act_val = actual.get(key)
                        if act_val is None or abs(exp_val - act_val) > 1e-6:
                            ok = False
                            break
                    pts = group_weights[i] if ok else 0
                    value_scores += pts
                else:
                    pts = 0
                scores.append({
                    "item": f"Numerical diffs for group '{g}'",
                    "score": pts,
                    "max_score": group_weights[i],
                    "passed": pts > 0,
                    "reason": f"Expected {expected}, got {actual}" if not (expected and actual) else ("Correct" if ok else "Mismatch")
                })
            # Add a combined item for value score (already recorded per group, so we can skip or just sum)
            # We already appended per group, so total will be computed from those.

    # Compute total score
    total = sum(s["score"] for s in scores)
    # Write score file
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump({"total_score": total, "details": scores}, f, indent=2)

if __name__ == "__main__":
    main()
