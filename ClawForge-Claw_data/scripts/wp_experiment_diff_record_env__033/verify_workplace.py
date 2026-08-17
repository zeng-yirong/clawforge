import sys
import json
import csv
import os
import math
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score = 0
    details = []

    # ------------------------------------------------------------
    # 1. Check directory structure (10 points)
    # ------------------------------------------------------------
    item = {"item": "ops directory exists", "max_score": 5}
    if (ws / "ops").is_dir():
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops directory found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops directory missing"
    details.append(item)
    score += item["score"]

    item = {"item": "data/experiments directory exists", "max_score": 5}
    if (ws / "data" / "experiments").is_dir():
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "experiments directory found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "experiments directory missing"
    details.append(item)
    score += item["score"]

    # ------------------------------------------------------------
    # 2. Check output file existence (15 points)
    # ------------------------------------------------------------
    output_path = ws / "ops" / "diff_analysis.json"
    item = {"item": "ops/diff_analysis.json exists", "max_score": 15}
    if output_path.is_file():
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "output file present"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "output file not found"
    details.append(item)
    score += item["score"]

    # ------------------------------------------------------------
    # 3. Validate JSON structure (15 points)
    # ------------------------------------------------------------
    item = {"item": "valid JSON with required keys", "max_score": 15}
    try:
        with open(output_path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("root must be dict")
        required_keys = {"groups", "top_diff_group"}
        if not required_keys.issubset(data.keys()):
            raise ValueError(f"missing keys: {required_keys - set(data.keys())}")
        # Check groups is a dict keyed by group_id
        groups = data["groups"]
        if not isinstance(groups, dict):
            raise ValueError("groups must be dict")
        # Check each group entry has required diff fields
        for gid, entry in groups.items():
            if not isinstance(entry, dict):
                raise ValueError(f"group {gid} entry not dict")
            for k in ["accuracy_diff", "latency_ms_diff", "cost_usd_diff"]:
                if k not in entry:
                    raise ValueError(f"group {gid} missing key {k}")
                if not isinstance(entry[k], (int, float)):
                    raise ValueError(f"group {gid} {k} not numeric")
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "valid JSON structure"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Invalid JSON: {str(e)}"
    details.append(item)
    score += item["score"]

    # ------------------------------------------------------------
    # 4. Compute expected diffs from source CSVs (40 points)
    # ------------------------------------------------------------
    item = {"item": "correct diffs for all valid groups", "max_score": 40}
    try:
        # Read batch_b1.csv (skip dirty rows)
        def read_clean_csv(name):
            path = ws / "data" / "experiments" / name
            rows = []
            with open(path) as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    return rows
                for row in reader:
                    # skip empty rows
                    if not row:
                        continue
                    # must have exactly 4 columns
                    if len(row) != 4:
                        continue
                    try:
                        group = row[0].strip()
                        acc = float(row[1])
                        lat = float(row[2])
                        cost = float(row[3])
                    except (ValueError, IndexError):
                        continue
                    rows.append((group, acc, lat, cost))
            return rows

        b1 = read_clean_csv("batch_b1.csv")
        b3 = read_clean_csv("batch_b3.csv")

        # Build dicts
        b1_dict = {g: (a, l, c) for g, a, l, c in b1}
        b3_dict = {g: (a, l, c) for g, a, l, c in b3}

        # Groups present in both (intersection)
        common_groups = set(b1_dict.keys()) & set(b3_dict.keys())
        expected_groups = {}
        for g in sorted(common_groups):
            a1, l1, c1 = b1_dict[g]
            a2, l2, c2 = b3_dict[g]
            expected_groups[g] = {
                "accuracy_diff": round(a2 - a1, 4),
                "latency_ms_diff": round(l2 - l1, 2),
                "cost_usd_diff": round(c2 - c1, 4)
            }

        # top diff group (max |accuracy_diff|)
        if expected_groups:
            top_group = max(expected_groups, key=lambda g: abs(expected_groups[g]["accuracy_diff"]))
        else:
            top_group = None

        # Compare with agent output
        with open(output_path) as f:
            data = json.load(f)
        agent_groups = data["groups"]
        agent_top = data.get("top_diff_group")

        # Validate groups
        groups_ok = True
        reasons = []
        for g in expected_groups:
            if g not in agent_groups:
                groups_ok = False
                reasons.append(f"missing group {g}")
                continue
            for k in ["accuracy_diff", "latency_ms_diff", "cost_usd_diff"]:
                expected_val = expected_groups[g][k]
                agent_val = agent_groups[g].get(k)
                if agent_val is None or abs(agent_val - expected_val) > 0.001:
                    groups_ok = False
                    reasons.append(f"group {g} {k} expected {expected_val}, got {agent_val}")
        # Also ensure no extra groups (beyond common_groups) that were never in both
        for g in agent_groups:
            if g not in expected_groups:
                groups_ok = False
                reasons.append(f"unexpected group {g} in output")
        # top_diff_group
        top_ok = (agent_top == top_group)
        if not top_ok:
            reasons.append(f"top_diff_group expected '{top_group}', got '{agent_top}'")

        if groups_ok and top_ok:
            item["score"] = 40
            item["passed"] = True
            item["reason"] = "all diffs and top group correct"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "; ".join(reasons)
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Error computing expected diffs: {str(e)}"
    details.append(item)
    score += item["score"]

    # ------------------------------------------------------------
    # 5. Optional: check no extra unwanted keys (bonus or penalty - we'll just check)
    # ------------------------------------------------------------
    # Already covered above; if extra groups present we penalize.

    # ------------------------------------------------------------
    # Final total (hard cap 100)
    # ------------------------------------------------------------
    total_score = min(score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    main()
