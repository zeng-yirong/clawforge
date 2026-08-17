import json
import sys
import os
from pathlib import Path

def verify(workspace):
    results = []
    total_score = 0
    max_total = 100

    adjustments_path = Path(workspace) / "ops" / "adjustments.json"
    # --- Check file existence (10 pts) ---
    if adjustments_path.exists():
        results.append({"item": "adjustments.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found at ops/adjustments.json"})
        total_score += 10
    else:
        results.append({"item": "adjustments.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # Can't continue without file
        return finalize(results, total_score, max_total)

    # --- JSON validity (10 pts) ---
    try:
        with open(adjustments_path, "r") as f:
            data = json.load(f)
        results.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "File parses correctly"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        results.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        return finalize(results, total_score, max_total)

    # --- Expected keys (10 pts) ---
    expected_keys = {"transport_adjustments", "hotel_adjustments"}
    actual_keys = set(data.keys()) if isinstance(data, dict) else set()
    if actual_keys == expected_keys:
        results.append({"item": "Contains both required keys", "score": 10, "max_score": 10, "passed": True, "reason": "Keys transport_adjustments and hotel_adjustments present"})
        total_score += 10
    else:
        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys
        reason = f"Missing keys: {missing}" if missing else f"Extra keys: {extra}"
        results.append({"item": "Contains both required keys", "score": 0, "max_score": 10, "passed": False, "reason": reason})
        return finalize(results, total_score, max_total)

    # --- transport_adjustments array length (10 pts) ---
    transport = data["transport_adjustments"]
    if isinstance(transport, list) and len(transport) == 1:
        results.append({"item": "transport_adjustments array length", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly 1 adjustment"})
        total_score += 10
    else:
        results.append({"item": "transport_adjustments array length", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 1, got {len(transport) if isinstance(transport, list) else 'not a list'}"})

    # --- hotel_adjustments array length (10 pts) ---
    hotel = data["hotel_adjustments"]
    if isinstance(hotel, list) and len(hotel) == 1:
        results.append({"item": "hotel_adjustments array length", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly 1 adjustment"})
        total_score += 10
    else:
        results.append({"item": "hotel_adjustments array length", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 1, got {len(hotel) if isinstance(hotel, list) else 'not a list'}"})

    # --- transport_adjustments[0] id (10 pts) ---
    if transport and isinstance(transport[0], dict) and transport[0].get("id") == "TB001":
        results.append({"item": "transport_adjustments[0] ID", "score": 10, "max_score": 10, "passed": True, "reason": "ID is TB001"})
        total_score += 10
    else:
        results.append({"item": "transport_adjustments[0] ID", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 'TB001', got {transport[0].get('id') if transport else 'none'}"})

    # --- transport_adjustments[0] new_time (20 pts) ---
    expected_transport_time = "2025-04-15T20:30:00"
    actual_time = transport[0].get("new_time") if transport else None
    if actual_time == expected_transport_time:
        results.append({"item": "transport_adjustments[0] new_time", "score": 20, "max_score": 20, "passed": True, "reason": f"Time is {expected_transport_time}"})
        total_score += 20
    else:
        results.append({"item": "transport_adjustments[0] new_time", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected '{expected_transport_time}', got '{actual_time}'"})

    # --- hotel_adjustments[0] id (10 pts) ---
    if hotel and isinstance(hotel[0], dict) and hotel[0].get("id") == "HB001":
        results.append({"item": "hotel_adjustments[0] ID", "score": 10, "max_score": 10, "passed": True, "reason": "ID is HB001"})
        total_score += 10
    else:
        results.append({"item": "hotel_adjustments[0] ID", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 'HB001', got {hotel[0].get('id') if hotel else 'none'}"})

    # --- hotel_adjustments[0] new_time (10 pts) ---
    expected_hotel_time = "2025-04-15T20:00:00"
    actual_time = hotel[0].get("new_time") if hotel else None
    if actual_time == expected_hotel_time:
        results.append({"item": "hotel_adjustments[0] new_time", "score": 10, "max_score": 10, "passed": True, "reason": f"Time is {expected_hotel_time}"})
        total_score += 10
    else:
        results.append({"item": "hotel_adjustments[0] new_time", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected '{expected_hotel_time}', got '{actual_time}'"})

    # Finalization
    finalize(results, total_score, max_total)

def finalize(results, total, max_total):
    # Clamp total to 0-100
    total = max(0, min(total, max_total))
    output = {
        "total_score": total,
        "details": results
    }
    score_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".") / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    # Return for main (not needed when script runs)
    return output

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
