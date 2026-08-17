import json, sys, os, pathlib

def run():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = pathlib.Path(workspace)
    details = []
    total = 0
    max_total = 100

    # --- 1. Directory structure (10 pts) ---
    dirs_ok = True
    needed_dirs = ["ops", "policies", "platforms"]
    for d in needed_dirs:
        if not (workspace / d).is_dir():
            dirs_ok = False
            break
    if dirs_ok:
        details.append({"item": "Directory structure", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories present"})
        total += 10
    else:
        details.append({"item": "Directory structure", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing required directory under {workspace}"})

    # --- 2. Output file exists (10 pts) ---
    output_path = workspace / "ops" / "booking_request.json"
    if output_path.is_file():
        details.append({"item": "Output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/booking_request.json present"})
        total += 10
    else:
        details.append({"item": "Output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/booking_request.json not found"})
        # can't proceed further
        _write_score(workspace, total, details)
        return

    # --- 3. JSON parseable (10 pts) ---
    try:
        data = json.loads(output_path.read_text(encoding="utf-8"))
        details.append({"item": "JSON format", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON format", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        _write_score(workspace, total, details)
        return

    # --- 4. Required fields present (20 pts) ---
    required_fields = ["selected_flight_id", "platform_id", "price", "needs_approval"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({"item": "Required fields in booking_request.json", "score": 20, "max_score": 20, "passed": True, "reason": "All required fields present"})
        total += 20
    else:
        details.append({"item": "Required fields in booking_request.json", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing fields: {missing}"})
        # proceed but will lose points for correctness

    # --- 5. Correctness checks (50 pts) ---
    correct_points = 0
    max_correct = 50

    # 5a. selected_flight_id (20)
    expected_flight = "flight_sky_001"
    if data.get("selected_flight_id") == expected_flight:
        correct_points += 20
    else:
        details.append({"item": "selected_flight_id", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_flight}, got {data.get('selected_flight_id')}"})

    # 5b. platform_id (10)
    expected_platform = "skybook"
    if data.get("platform_id") == expected_platform:
        correct_points += 10
    else:
        details.append({"item": "platform_id", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_platform}, got {data.get('platform_id')}"})

    # 5c. price (10)
    expected_price = 1400.00
    got_price = data.get("price")
    if isinstance(got_price, (int, float)) and abs(got_price - expected_price) < 0.001:
        correct_points += 10
    else:
        details.append({"item": "price", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_price}, got {got_price}"})

    # 5d. needs_approval (10)
    expected_approval = True  # because 1400 > 1300
    if data.get("needs_approval") is expected_approval:
        correct_points += 10
    else:
        details.append({"item": "needs_approval", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_approval}, got {data.get('needs_approval')}"})

    details.append({"item": "Correctness aggregate", "score": correct_points, "max_score": max_correct, "passed": correct_points == max_correct, "reason": f"Scored {correct_points}/{max_correct}"})
    total += correct_points

    _write_score(workspace, total, details)

def _write_score(workspace, total, details):
    score_path = workspace / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    print(f"Verification complete. Score: {total}/100")

if __name__ == "__main__":
    run()
