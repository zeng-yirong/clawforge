import json
import os
import sys
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # Expected results
    expected_avgs = {"P001": 150.0, "P002": 200.0, "P003": 450.0}
    expected_keys = set(expected_avgs.keys())

    # File must exist
    json_path = os.path.join(workspace, "output", "average_order_values.json")
    if not os.path.isfile(json_path):
        details.append({
            "item": "output/average_order_values.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        total_score += 0
    else:
        details.append({
            "item": "output/average_order_values.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists."
        })
        total_score += 10

        # Must be valid JSON
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            details.append({
                "item": "Valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "JSON parsed successfully."
            })
            total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "Valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON parse error: {e}"
            })
            total_score += 0
            # Cannot proceed with further checks
            _write_score(details, total_score)
            return

        # Must be a dict
        if not isinstance(data, dict):
            details.append({
                "item": "Content is a dict",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Root value is not a dict."
            })
            total_score += 0
            _write_score(details, total_score)
            return
        else:
            details.append({
                "item": "Content is a dict",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Root is a dict."
            })
            total_score += 10

        # Keys must match exactly (no extra, no missing)
        actual_keys = set(data.keys())
        if actual_keys == expected_keys:
            details.append({
                "item": "Keys match expected products",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": f"Keys are exactly {sorted(expected_keys)}."
            })
            total_score += 20
        else:
            missing = expected_keys - actual_keys
            extra = actual_keys - expected_keys
            msg = f"Keys mismatch. Missing: {missing}, Extra: {extra}"
            details.append({
                "item": "Keys match expected products",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": msg
            })
            total_score += 0

        # Numerical values must be correct (within 1e-6)
        all_correct = True
        for key in expected_keys:
            exp_val = expected_avgs[key]
            actual_val = data.get(key)
            if actual_val is None:
                all_correct = False
                continue
            # Allow float or int, compare with tolerance
            try:
                val = float(actual_val)
            except (TypeError, ValueError):
                all_correct = False
                continue
            if not math.isclose(val, exp_val, rel_tol=1e-6, abs_tol=1e-6):
                all_correct = False

        if all_correct:
            details.append({
                "item": "Average order values correct",
                "score": 50,
                "max_score": 50,
                "passed": True,
                "reason": f"All averages match expected: {expected_avgs}."
            })
            total_score += 50
        else:
            # Provide partial credit: each correct product gets 16.66 (rounded)
            correct_count = 0
            for key in expected_keys:
                exp_val = expected_avgs[key]
                actual_val = data.get(key)
                try:
                    val = float(actual_val) if actual_val is not None else None
                except:
                    val = None
                if val is not None and math.isclose(val, exp_val, rel_tol=1e-6, abs_tol=1e-6):
                    correct_count += 1
            partial = int(50 * correct_count / len(expected_keys))
            msg = f"Only {correct_count}/{len(expected_keys)} products correct."
            details.append({
                "item": "Average order values correct",
                "score": partial,
                "max_score": 50,
                "passed": partial == 50,
                "reason": msg
            })
            total_score += partial

    # Final output
    _write_score(details, total_score)

def _write_score(details, total_score):
    # total_score should be integer between 0 and 100
    score_dict = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(score_dict, f, indent=2)

if __name__ == "__main__":
    main()
