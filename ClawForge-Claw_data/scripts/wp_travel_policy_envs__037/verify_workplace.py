import sys
import json
import os
import math
from pathlib import Path

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = Path(WORKSPACE) / rel_path
    if not full.exists():
        return None, f"File not found: {rel_path}"
    try:
        with open(full) as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"

def verify():
    details = []
    total_score = 0

    # 1. Directory existence (10 pts)
    dirs = ["ops", "data/platforms", "data/policies"]
    dir_score = 0
    for d in dirs:
        if (Path(WORKSPACE) / d).is_dir():
            dir_score += 3
            details.append({"item": f"Directory {d} exists", "score": 3, "max_score": 3, "passed": True, "reason": ""})
        else:
            details.append({"item": f"Directory {d} exists", "score": 0, "max_score": 3, "passed": False, "reason": f"Missing {d}"})
    # extra 1 point for ops having exactly one file (will be checked later)
    details.append({"item": "Base directory structure", "score": dir_score, "max_score": 10, "passed": dir_score==10, "reason": ""})
    total_score += dir_score

    # 2. Result file existence and JSON validity (10 pts)
    result_data, err = load_json("ops/booking_recommendation.json")
    if err:
        details.append({"item": "ops/booking_recommendation.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": err})
        # cannot proceed further
        final_score = total_score
        write_score(final_score, details)
        return
    else:
        details.append({"item": "ops/booking_recommendation.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10

    # 3. Required fields present (20 pts)
    required_fields = ["recommended_platform", "flight_id", "total_cost", "requires_approval", "approval_request_id", "approver_email"]
    field_score = 0
    missing = []
    for f in required_fields:
        if f in result_data:
            field_score += 3
        else:
            missing.append(f)
    if len(required_fields) == len(missing):
        field_score = 0
    details.append({"item": "Required fields present", "score": field_score, "max_score": 20, "passed": field_score==20, "reason": f"Missing: {missing}" if missing else ""})
    total_score += field_score

    # 4. Total cost calculation (50 pts) - verify against source data
    # First load all platform data
    platforms_dir = Path(WORKSPACE) / "data/platforms"
    platform_files = list(platforms_dir.glob("*.json"))
    platform_map = {}
    for pf in platform_files:
        with open(pf) as f:
            pdata = json.load(f)
            platform_map[pdata["platform_id"]] = pdata

    # Find the recommended flight in the data
    rec_platform_id = result_data.get("recommended_platform")
    rec_flight_id = result_data.get("flight_id")
    if not rec_platform_id or not rec_flight_id:
        calc_score = 0
        details.append({"item": "Total cost calculation", "score": 0, "max_score": 50, "passed": False, "reason": "Missing recommended_platform or flight_id"})
        total_score += calc_score
    else:
        # Find the platform
        platform = None
        for pid, pdata in platform_map.items():
            if pdata["name"] == rec_platform_id:
                platform = pdata
                break
        if platform is None:
            calc_score = 0
            details.append({"item": "Total cost calculation", "score": 0, "max_score": 50, "passed": False, "reason": f"Platform {rec_platform_id} not found"})
            total_score += calc_score
        else:
            # Find the flight
            target_flight = None
            for flight in platform["flights"]:
                if flight["flight_id"] == rec_flight_id:
                    target_flight = flight
                    break
            if target_flight is None:
                calc_score = 0
                details.append({"item": "Total cost calculation", "score": 0, "max_score": 50, "passed": False, "reason": f"Flight {rec_flight_id} not found in {rec_platform_id}"})
                total_score += calc_score
            else:
                # Compute expected total cost = price + transaction_fee + service_fee
                expected_cost = target_flight["price"] + platform["transaction_fee"] + platform["service_fee"]
                reported_cost = result_data.get("total_cost")
                if reported_cost is None:
                    calc_score = 0
                    details.append({"item": "Total cost calculation", "score": 0, "max_score": 50, "passed": False, "reason": "total_cost missing in result"})
                    total_score += calc_score
                else:
                    # Allow floating point tolerance
                    if math.isclose(reported_cost, expected_cost, rel_tol=1e-9):
                        calc_score = 50
                        details.append({"item": "Total cost calculation", "score": 50, "max_score": 50, "passed": True, "reason": f"Expected {expected_cost}, got {reported_cost}"})
                    else:
                        calc_score = 0
                        details.append({"item": "Total cost calculation", "score": 0, "max_score": 50, "passed": False, "reason": f"Expected {expected_cost}, got {reported_cost}"})
                    total_score += calc_score

    # 5. Approval logic (10 pts)
    approval_score = 0
    reported_approval = result_data.get("requires_approval")
    reported_cost = result_data.get("total_cost")
    if reported_cost is not None and reported_approval is not None:
        expected_approval = reported_cost > 2000  # based on policy requires_approval_above=2000
        if reported_approval == expected_approval:
            approval_score = 5
            details.append({"item": "requires_approval correct", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        else:
            details.append({"item": "requires_approval correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected {expected_approval}, got {reported_approval}"})
        # Check that if approval needed, approval_request_id and approver_email are present and non-empty
        if expected_approval:
            if result_data.get("approval_request_id") and result_data.get("approver_email"):
                approval_score += 5
                details.append({"item": "Approval request fields populated", "score": 5, "max_score": 5, "passed": True, "reason": ""})
            else:
                details.append({"item": "Approval request fields populated", "score": 0, "max_score": 5, "passed": False, "reason": "Missing approval_request_id or approver_email"})
        else:
            # No approval needed, but fields can be present or absent – we allow either, just give points if consistent
            approval_score += 5
            details.append({"item": "Approval request fields (not required)", "score": 5, "max_score": 5, "passed": True, "reason": "No approval needed, fields optional"})
    else:
        details.append({"item": "Approval logic", "score": 0, "max_score": 10, "passed": False, "reason": "Missing total_cost or requires_approval"})
    total_score += approval_score

    # Ensure total is within 0-100
    final_score = min(max(total_score, 0), 100)
    write_score(final_score, details)

def write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open(Path(WORKSPACE) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/100")

if __name__ == "__main__":
    verify()
