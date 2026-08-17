import sys
import os
import json
import math

def compute_distance(lat1, lon1, lat2, lon2):
    # simple Euclidean approximation for ranking, not for absolute accuracy
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    max_total = 100

    # 1. Check directory structure (10 pts)
    dirs_ok = True
    for d in ["data", "ops"]:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
            break
    if dirs_ok:
        total_score += 10
        score_details.append({
            "item": "Directory structure (data/ and ops/)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Both required directories exist."
        })
    else:
        score_details.append({
            "item": "Directory structure (data/ and ops/)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing data/ or ops/ directory."
        })

    # 2. Check output file exists (10 pts)
    result_path = os.path.join(workspace, "ops", "charge_route.json")
    if os.path.isfile(result_path):
        total_score += 10
        score_details.append({
            "item": "Output file ops/charge_route.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
    else:
        score_details.append({
            "item": "Output file ops/charge_route.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # early exit because we cannot validate content
        final_score = total_score
        result = {
            "total_score": final_score,
            "details": score_details
        }
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. Validate JSON format (10 pts)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        total_score += 10
        score_details.append({
            "item": "JSON format validity",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON."
        })
    except Exception as e:
        total_score += 0
        score_details.append({
            "item": "JSON format validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        final_score = total_score
        result = {
            "total_score": final_score,
            "details": score_details
        }
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. Check top-level structure (5 pts)
    if not isinstance(data, dict) or "route_stops" not in data:
        total_score += 0
        score_details.append({
            "item": "Top-level structure contains 'route_stops'",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Missing 'route_stops' key or not a dict."
        })
    else:
        total_score += 5
        score_details.append({
            "item": "Top-level structure contains 'route_stops'",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Key found."
        })

    # 5. Check route_stops is a list with correct length (15 pts)
    stops = data.get("route_stops", [])
    expected_ids = ["ch01", "ch03", "ch05"]  # ordered by distance from Beijing center
    if isinstance(stops, list) and len(stops) == len(expected_ids):
        total_score += 15
        score_details.append({
            "item": "route_stops length (should be 3)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"Length is {len(stops)}."
        })
    else:
        total_score += 0
        score_details.append({
            "item": "route_stops length (should be 3)",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Length is {len(stops)}, expected {len(expected_ids)}."
        })

    # 6. Validate each stop has required fields (10 pts)
    required_fields = ["poi_id", "name", "lat", "lon"]
    all_fields_ok = True
    for idx, stop in enumerate(stops):
        if not isinstance(stop, dict):
            all_fields_ok = False
            break
        for field in required_fields:
            if field not in stop:
                all_fields_ok = False
                break
        if not all_fields_ok:
            break
    if all_fields_ok:
        total_score += 10
        score_details.append({
            "item": "Each stop has poi_id, name, lat, lon",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required fields present."
        })
    else:
        total_score += 0
        score_details.append({
            "item": "Each stop has poi_id, name, lat, lon",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing fields in one or more stops."
        })

    # 7. Validate actual content: correct IDs in correct order (40 pts)
    actual_ids = [stop.get("poi_id") for stop in stops]
    if actual_ids == expected_ids:
        total_score += 40
        score_details.append({
            "item": "Correct POI IDs in correct order (ch01, ch03, ch05)",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": f"IDs match expected order: {expected_ids}."
        })
    else:
        # partial credit if all IDs correct but order wrong (20 pts)
        if set(actual_ids) == set(expected_ids) and len(actual_ids) == len(expected_ids):
            total_score += 20
            score_details.append({
                "item": "Correct POI IDs in correct order (ch01, ch03, ch05)",
                "score": 20,
                "max_score": 40,
                "passed": False,
                "reason": f"IDs correct but order wrong: {actual_ids}, expected {expected_ids}."
            })
        else:
            total_score += 0
            score_details.append({
                "item": "Correct POI IDs in correct order (ch01, ch03, ch05)",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"IDs mismatch: actual {actual_ids}, expected {expected_ids}."
            })

    # Ensure total_score does not exceed max_total
    total_score = min(total_score, max_total)

    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    # Print for human debugging (optional)
    print(f"Total score: {total_score}/{max_total}")
    for d in score_details:
        print(f"  {d['item']}: {d['score']}/{d['max_score']} ({'PASS' if d['passed'] else 'FAIL'}) - {d['reason']}")

if __name__ == "__main__":
    main()
