import sys
import os
import json
import math

def verify(workspace: str) -> dict:
    details = []
    ops_path = os.path.join(workspace, "ops")
    diff_path = os.path.join(ops_path, "diff_record.json")

    # ------------------------------------------------------------------
    # 1. Directory & File existence (10 points)
    # ------------------------------------------------------------------
    dir_exists = os.path.isdir(ops_path)
    details.append({
        "item": "ops directory exists",
        "score": 2 if dir_exists else 0,
        "max_score": 2,
        "passed": dir_exists,
        "reason": "ops/ found" if dir_exists else "ops/ missing"
    })

    file_exists = os.path.isfile(diff_path)
    details.append({
        "item": "diff_record.json exists",
        "score": 4 if file_exists else 0,
        "max_score": 4,
        "passed": file_exists,
        "reason": "file exists" if file_exists else "file not found"
    })

    if not file_exists:
        # nothing more to verify
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}

    # ------------------------------------------------------------------
    # 2. JSON validity & structure (10 points)
    # ------------------------------------------------------------------
    try:
        with open(diff_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON parseable",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "valid JSON"
        })
    except Exception as e:
        details.append({
            "item": "JSON parseable",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"parse error: {e}"
        })
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}

    if not isinstance(data, dict):
        details.append({
            "item": "top-level is dict",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "not a dict"
        })
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}
    details.append({
        "item": "top-level is dict",
        "score": 5,
        "max_score": 5,
        "passed": True,
        "reason": "is dict"
    })

    # ------------------------------------------------------------------
    # 3. Correct groups present (30 points)
    # ------------------------------------------------------------------
    expected_groups = {"A", "B", "C"}
    actual_groups = set(data.keys())
    missing = expected_groups - actual_groups
    extra = actual_groups - expected_groups

    for g in expected_groups:
        present = g in actual_groups
        details.append({
            "item": f"group '{g}' present",
            "score": 10 if present else 0,
            "max_score": 10,
            "passed": present,
            "reason": f"found {g}" if present else f"missing {g}"
        })

    if extra:
        details.append({
            "item": "no extra groups",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"extra groups: {extra}"
        })
    else:
        details.append({
            "item": "no extra groups",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "only expected groups"
        })

    # ------------------------------------------------------------------
    # 4. Numerical accuracy + field naming (50 points)
    #    - 45 points for exact values (5 per metric, 9 metrics)
    #    - 5 points for using preferred field names
    # ------------------------------------------------------------------
    expected_values = {
        "A": {"accuracy_diff": 0.02, "latency_ms_diff": -10, "cost_usd_diff": 0.05},
        "B": {"accuracy_diff": -0.03, "latency_ms_diff": 10, "cost_usd_diff": -0.05},
        "C": {"accuracy_diff": 0.01, "latency_ms_diff": -5, "cost_usd_diff": 0.02}
    }

    # Preferred key for each metric
    key_mappings = {
        "accuracy_diff":   ["accuracy_diff", "acc_diff", "accuracy_delta"],
        "latency_ms_diff": ["latency_ms_diff", "latency_diff", "latency_delta", "latency_ms_delta"],
        "cost_usd_diff":   ["cost_usd_diff", "cost_diff", "cost_delta", "cost_usd_delta"]
    }

    all_preferred = True   # for the 5-point naming bonus
    for g in expected_groups:
        if g not in data:
            continue
        group_data = data[g]
        if not isinstance(group_data, dict):
            details.append({
                "item": f"group '{g}' value is dict",
                "score": 0,
                "max_score": 3,
                "passed": False,
                "reason": "not a dict"
            })
            continue

        for metric, exp_val in expected_values[g].items():
            found_val = None
            found_key = None
            for candidate in key_mappings[metric]:
                if candidate in group_data:
                    found_val = group_data[candidate]
                    found_key = candidate
                    break

            if found_val is None:
                details.append({
                    "item": f"group '{g}' {metric}",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": "field not found"
                })
                all_preferred = False
                continue

            # check if preferred key was used
            if found_key != key_mappings[metric][0]:
                all_preferred = False

            try:
                val = float(found_val)
            except (ValueError, TypeError):
                details.append({
                    "item": f"group '{g}' {metric}",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": f"non-numeric value: {found_val}"
                })
                continue

            if math.isclose(val, exp_val, rel_tol=1e-5, abs_tol=1e-5):
                details.append({
                    "item": f"group '{g}' {metric}",
                    "score": 5,
                    "max_score": 5,
                    "passed": True,
                    "reason": f"correct value {val}"
                })
            else:
                details.append({
                    "item": f"group '{g}' {metric}",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": f"expected {exp_val}, got {val}"
                })

    # bonus for standard field naming (5 points)
    if all_preferred:
        details.append({
            "item": "field naming uses standard keys",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "all metrics use preferred field names"
        })
    else:
        details.append({
            "item": "field naming uses standard keys",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "non‑standard field names used (e.g. latency_diff instead of latency_ms_diff)"
        })

    # ------------------------------------------------------------------
    total_score = sum(d["score"] for d in details)
    return {"total_score": total_score, "details": details}


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {result['total_score']}")
