import sys
import os
import json
from pathlib import Path

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."
SCORE_FILE = os.path.join(WORKSPACE, "workplace_score.json")
details = []

def check_dir(path, points, description):
    full = os.path.join(WORKSPACE, path)
    passed = os.path.isdir(full)
    details.append({
        "item": f"Directory exists: {path}",
        "score": points if passed else 0,
        "max_score": points,
        "passed": passed,
        "reason": "Found" if passed else f"Missing directory: {full}"
    })
    return passed

def check_file(path, points, description):
    full = os.path.join(WORKSPACE, path)
    passed = os.path.isfile(full)
    details.append({
        "item": f"File exists: {path}",
        "score": points if passed else 0,
        "max_score": points,
        "passed": passed,
        "reason": "Found" if passed else f"Missing file: {full}"
    })
    return passed

def check_json(path, points, description):
    full = os.path.join(WORKSPACE, path)
    try:
        with open(full, "r") as f:
            data = json.load(f)
        details.append({
            "item": f"Valid JSON: {path}",
            "score": points,
            "max_score": points,
            "passed": True,
            "reason": "Parsed successfully"
        })
        return data
    except Exception as e:
        details.append({
            "item": f"Valid JSON: {path}",
            "score": 0,
            "max_score": points,
            "passed": False,
            "reason": str(e)
        })
        return None

def check_field(data, field, expected_type, points, description):
    if data is None:
        details.append({
            "item": description,
            "score": 0,
            "max_score": points,
            "passed": False,
            "reason": "No data to check"
        })
        return None
    if field not in data:
        details.append({
            "item": description,
            "score": 0,
            "max_score": points,
            "passed": False,
            "reason": f"Field '{field}' missing"
        })
        return None
    val = data[field]
    if not isinstance(val, expected_type):
        details.append({
            "item": description,
            "score": 0,
            "max_score": points,
            "passed": False,
            "reason": f"Field '{field}' type mismatch: expected {expected_type.__name__}, got {type(val).__name__}"
        })
        return None
    details.append({
        "item": description,
        "score": points,
        "max_score": points,
        "passed": True,
        "reason": f"Field '{field}' present with type {expected_type.__name__}"
    })
    return val

def check_value(data, field, expected_value, points, description):
    actual = data.get(field) if data else None
    passed = (actual == expected_value)
    details.append({
        "item": description,
        "score": points if passed else 0,
        "max_score": points,
        "passed": passed,
        "reason": f"Expected {expected_value!r}, got {actual!r}" if not passed else "Correct"
    })
    return passed

def main():
    # 1. Check directory structure (10 points)
    check_dir("ops", 5, "ops/ directory")
    check_dir("data", 5, "data/ directory (should remain)")

    # 2. Check target file exists (10 points)
    check_file("ops/booking_decision.json", 10, "ops/booking_decision.json")

    # 3. Parse JSON (15 points)
    data = check_json("ops/booking_decision.json", 15, "Valid JSON in booking_decision.json")

    # 4. Check required field types (20 points)
    cheapest_platform = check_field(data, "cheapest_platform", str, 5, "Field 'cheapest_platform' present and string")
    cheapest_price = check_field(data, "cheapest_price", (int, float), 5, "Field 'cheapest_price' present and numeric")
    requires_approval = check_field(data, "requires_approval", bool, 5, "Field 'requires_approval' present and bool")
    approval_threshold = check_field(data, "approval_threshold", (int, float), 5, "Field 'approval_threshold' present and numeric")

    # 5. Check field values (45 points)
    # Expected values based on env_builder data:
    # - Only active platforms: AeroCheap (2800), FlightPro (3100), AirElite (4200)
    # - Active policy: ACME_2026, version 2.1, min_advance_booking_days=14, requires_approval_above=3000
    # - Today (2026-06-01) to departure (2026-06-15) = 14 days → min_advance_booking_days=14 satisfied
    # - AeroCheap 2800 < 3000 → no approval; FlightPro 3100 >= 3000 → needs approval
    # - Cheapest platform is AeroCheap with price 2800, so requires_approval should be False
    check_value(data, "cheapest_platform", "AeroCheap", 15, "cheapest_platform = 'AeroCheap'")
    check_value(data, "cheapest_price", 2800.0, 15, "cheapest_price = 2800.0")
    check_value(data, "requires_approval", False, 10, "requires_approval = False (price below threshold)")
    check_value(data, "approval_threshold", 3000, 5, "approval_threshold = 3000")

    # 6. Also check that at least one additional context field exists (bonus consideration)
    # We require either policy_applied or today present
    has_context = False
    if data and ("policy_applied" in data or "today" in data):
        has_context = True
        details.append({
            "item": "Context field (policy_applied or today) present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found"
        })
    else:
        details.append({
            "item": "Context field (policy_applied or today) present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Neither 'policy_applied' nor 'today' field found"
        })

    # Calculate total score
    total_score = sum(d["score"] for d in details)
    # Cap at 100
    total_score = min(total_score, 100)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open(SCORE_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {SCORE_FILE}: {total_score}/100")

if __name__ == "__main__":
    main()
