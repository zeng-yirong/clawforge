import json
import os
import sys

def verify_workspace(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. Check ops directory exists (10 points)
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    if dir_exists:
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ directory found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory missing"})

    # 2. Check adjustments.json exists (10 points)
    adj_path = os.path.join(workspace, "ops", "adjustments.json")
    file_exists = os.path.isfile(adj_path)
    if file_exists:
        details.append({"item": "adjustments.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/adjustments.json found"})
        total_score += 10
    else:
        details.append({"item": "adjustments.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/adjustments.json not found"})
        # save partial score and exit early because remaining checks depend on file
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. Parse JSON and check validity (10 points)
    try:
        with open(adj_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON valid", "score": 10, "max_score": 10, "passed": True, "reason": "File is valid JSON"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. Check required fields exist (20 points total, 10 each)
    has_hotel = isinstance(data.get("hotel_bookings"), list)
    has_transport = isinstance(data.get("transport_bookings"), list)
    if has_hotel:
        details.append({"item": "hotel_bookings field exists and is list", "score": 10, "max_score": 10, "passed": True, "reason": "Field hotel_bookings is a list"})
        total_score += 10
    else:
        details.append({"item": "hotel_bookings field exists and is list", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or invalid hotel_bookings field"})
    
    if has_transport:
        details.append({"item": "transport_bookings field exists and is list", "score": 10, "max_score": 10, "passed": True, "reason": "Field transport_bookings is a list"})
        total_score += 10
    else:
        details.append({"item": "transport_bookings field exists and is list", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or invalid transport_bookings field"})

    # 5. Check hotel bookings list correctness (20 points)
    expected_hotel = {"hb_001", "hb_003"}
    actual_hotel = set(data.get("hotel_bookings", []))
    if actual_hotel == expected_hotel:
        details.append({"item": "hotel_bookings IDs correct", "score": 20, "max_score": 20, "passed": True, "reason": f"Exact match: {sorted(actual_hotel)}"})
        total_score += 20
    else:
        # partial credit? For simplicity, 0 if not exact; but we can give partial for overlap
        intersection = actual_hotel & expected_hotel
        extra = actual_hotel - expected_hotel
        missing = expected_hotel - actual_hotel
        reason = f"Intersection={len(intersection)}, extra={extra}, missing={missing}"
        score = 0
        if len(intersection) == 2 and not extra and not missing:
            score = 20  # should not happen but safe
        elif len(intersection) > 0:
            score = 10  # partial (e.g., only one correct)
        details.append({"item": "hotel_bookings IDs correct", "score": score, "max_score": 20, "passed": score == 20, "reason": reason})
        total_score += score

    # 6. Check transport bookings list correctness (20 points)
    expected_transport = {"tb_001", "tb_002"}
    actual_transport = set(data.get("transport_bookings", []))
    if actual_transport == expected_transport:
        details.append({"item": "transport_bookings IDs correct", "score": 20, "max_score": 20, "passed": True, "reason": f"Exact match: {sorted(actual_transport)}"})
        total_score += 20
    else:
        intersection = actual_transport & expected_transport
        extra = actual_transport - expected_transport
        missing = expected_transport - actual_transport
        reason = f"Intersection={len(intersection)}, extra={extra}, missing={missing}"
        score = 10 if len(intersection) > 0 else 0
        details.append({"item": "transport_bookings IDs correct", "score": score, "max_score": 20, "passed": score == 20, "reason": reason})
        total_score += score

    # 7. No extra fields (10 points) - but we only penalize if extra root-level fields beyond the two expected
    expected_fields = {"hotel_bookings", "transport_bookings"}
    extra_fields = set(data.keys()) - expected_fields
    if not extra_fields:
        details.append({"item": "No extra root-level fields", "score": 10, "max_score": 10, "passed": True, "reason": "Only hotel_bookings and transport_bookings present"})
        total_score += 10
    else:
        details.append({"item": "No extra root-level fields", "score": 0, "max_score": 10, "passed": False, "reason": f"Extra fields: {extra_fields}"})

    # Ensure total does not exceed 100
    total_score = min(total_score, 100)

    # Write score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workspace(workspace)
