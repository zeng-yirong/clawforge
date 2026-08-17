import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

results = []
total_score = 0
max_total = 100

def check(description, passed, score, max_score, reason=""):
    global total_score
    if passed:
        total_score += score
    results.append({
        "item": description,
        "score": score if passed else 0,
        "max_score": max_score,
        "passed": passed,
        "reason": reason if not passed else "OK"
    })

# 1. Directory structure check (10 points)
dirs_to_check = ["ops", "data/flights", "data/bookings", "data/hotels", "data/transports"]
dir_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in dirs_to_check)
check("Directory structure (ops, data/*)", dir_ok, 10, 10, "Missing required directories" if not dir_ok else "")

# 2. Expected output file exists (10 points)
plan_path = os.path.join(workspace, "ops", "disruption_plan.json")
plan_exists = os.path.isfile(plan_path)
check("Output file ops/disruption_plan.json exists", plan_exists, 10, 10, "File not found" if not plan_exists else "")

if not plan_exists:
    # Early exit if file missing
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)
    print(f"Score: {total_score}/{max_total}")
    sys.exit(0)

# 3. Valid JSON (10 points)
try:
    with open(plan_path, "r") as f:
        plan = json.load(f)
    check("JSON is valid", True, 10, 10)
except (json.JSONDecodeError, Exception) as e:
    check("JSON is valid", False, 10, 10, f"Invalid JSON: {str(e)}")
    # Cannot continue if JSON is broken
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)
    print(f"Score: {total_score}/{max_total}")
    sys.exit(0)

# 4. Required top-level fields (10 points)
required_fields = ["flight_id", "delay_minutes", "affected_hotel_bookings", "affected_transport_bookings"]
missing_fields = [f for f in required_fields if f not in plan]
check("Top-level fields present", len(missing_fields)==0, 10, 10, f"Missing fields: {missing_fields}" if missing_fields else "")

# 5. flight_id correct (10 points)
flight_ok = plan.get("flight_id") == "UA123"
check("flight_id is 'UA123'", flight_ok, 10, 10, f"Got {plan.get('flight_id')}" if not flight_ok else "")

# 6. delay_minutes correct (10 points)
delay_ok = plan.get("delay_minutes") == 120
check("delay_minutes is 120", delay_ok, 10, 10, f"Got {plan.get('delay_minutes')}" if not delay_ok else "")

# 7. affected_hotel_bookings (expected list: HB001, HB002, HB003, HB005) note HB001 dup but should be unique.
# Expected set after dedup: {'HB001', 'HB002', 'HB003', 'HB005'} (4 items)
# But prompt says "list out exactly which hotel bookings". We accept any order and duplicates? 
# For consistency, we expect the agent to produce unique IDs. We'll score based on set equality.
expected_hotel = {"HB001", "HB002", "HB003", "HB005"}
actual_hotel = set(plan.get("affected_hotel_bookings", []))
hotel_ok = (expected_hotel == actual_hotel)
hotel_reason = f"Expected {sorted(expected_hotel)}, got {sorted(actual_hotel)}" if not hotel_ok else ""
check("affected_hotel_bookings contains correct IDs", hotel_ok, 20, 20, hotel_reason)

# 8. affected_transport_bookings (expected: TB001, TB002, TB004)
expected_transport = {"TB001", "TB002", "TB004"}
actual_transport = set(plan.get("affected_transport_bookings", []))
transport_ok = (expected_transport == actual_transport)
transport_reason = f"Expected {sorted(expected_transport)}, got {sorted(actual_transport)}" if not transport_ok else ""
check("affected_transport_bookings contains correct IDs", transport_ok, 20, 20, transport_reason)

# 9. No unexpected top-level fields (bonus as part of other checks, but we deduct if extra)
allowed_fields = set(required_fields)
extra_fields = set(plan.keys()) - allowed_fields
if extra_fields:
    # deduct 10 points but not below 0
    total_score = max(0, total_score - 10)
    results.append({
        "item": "No extra fields",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": f"Unexpected fields: {extra_fields}"
    })
else:
    results.append({
        "item": "No extra fields",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "OK"
    })

# Adjust total because we added an extra 10 max; our max_total should be 110 originally. Let's keep max_total=100 by scaling.
# Actually we defined max_total=100 earlier. We'll just cap total_score at 100.
total_score = min(total_score, 100)

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": results}, f, indent=2)

print(f"Score: {total_score}/{max_total}")
