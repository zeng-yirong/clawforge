import os
import sys
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def verify():
    score = 0
    details = []

    # 1. Check that ops/comfort_adjustment.json exists
    target_path = os.path.join(workspace, "ops", "comfort_adjustment.json")
    if not os.path.exists(target_path):
        details.append({
            "item": "File existence: ops/comfort_adjustment.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # No file -> remaining checks impossible
        total_score = 0
        write_score(total_score, details)
        return

    details.append({
        "item": "File existence: ops/comfort_adjustment.json",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File present."
    })
    score += 10

    # 2. Parse JSON and check structure
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        write_score(score, details)
        return

    if not isinstance(data, dict):
        details.append({
            "item": "JSON validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Root is not a JSON object."
        })
        write_score(score, details)
        return

    details.append({
        "item": "JSON validity",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON object."
    })
    score += 10

    # 3. Check required fields
    required_fields = ["device_id", "start_hour", "duration_hours"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Missing fields: {', '.join(missing)}"
        })
        write_score(score, details)
        return

    # Check no extra unexpected top-level fields (allow 'device_id','start_hour','duration_hours')
    allowed = set(required_fields)
    extra = [k for k in data if k not in allowed]
    if extra:
        details.append({
            "item": "No extra top-level fields",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Unexpected fields: {', '.join(extra)}"
        })
        # continue, but deduct
        score_with_extra = score  # keep current score without extra penalty? We'll add later.
    else:
        details.append({
            "item": "No extra top-level fields",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "No unexpected fields."
        })
        score += 5

    # 4. Check field types
    field_type_ok = True
    type_issues = []
    if not isinstance(data.get("device_id"), str):
        type_issues.append("device_id must be string")
        field_type_ok = False
    if not isinstance(data.get("start_hour"), int):
        type_issues.append("start_hour must be integer")
        field_type_ok = False
    if not isinstance(data.get("duration_hours"), int):
        type_issues.append("duration_hours must be integer")
        field_type_ok = False

    if not field_type_ok:
        details.append({
            "item": "Field types",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "; ".join(type_issues)
        })
        write_score(score, details)
        return
    else:
        details.append({
            "item": "Field types",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All fields have correct types."
        })
        score += 10

    # 5. Validate start_hour range (0-23)
    if not (0 <= data["start_hour"] <= 23):
        details.append({
            "item": "start_hour range 0-23",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"start_hour {data['start_hour']} out of range."
        })
    else:
        details.append({
            "item": "start_hour range 0-23",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "start_hour in valid range."
        })
        score += 5

    # 6. Validate duration_hours positive
    if data["duration_hours"] <= 0:
        details.append({
            "item": "duration_hours positive",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"duration_hours must be >0, got {data['duration_hours']}."
        })
    else:
        details.append({
            "item": "duration_hours positive",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "duration_hours positive."
        })
        score += 5

    # 7. Verify device_id is the bedroom humidifier (device_id must be "humidifier_bedroom_01")
    expected_device_id = "humidifier_bedroom_01"
    if data["device_id"] == expected_device_id:
        details.append({
            "item": "device_id correctness",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Correct device_id: {expected_device_id}."
        })
        score += 20
    else:
        details.append({
            "item": "device_id correctness",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected '{expected_device_id}', got '{data['device_id']}'."
        })

    # 8. Verify start_hour is the off-peak start hour (22)
    expected_start = 22
    if data["start_hour"] == expected_start:
        details.append({
            "item": "start_hour correctness",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"Correct start_hour: {expected_start} (off-peak)."
        })
        score += 15
    else:
        details.append({
            "item": "start_hour correctness",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Expected {expected_start}, got {data['start_hour']}."
        })

    # 9. Verify duration_hours = 2 (needs to raise humidity from 30% to 40% at 5%/h)
    expected_duration = 2
    if data["duration_hours"] == expected_duration:
        details.append({
            "item": "duration_hours correctness",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"Correct duration_hours: {expected_duration}."
        })
        score += 15
    else:
        details.append({
            "item": "duration_hours correctness",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Expected {expected_duration}, got {data['duration_hours']}."
        })

    # Final score (clamp to 100)
    total_score = min(score, 100)
    write_score(total_score, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    verify()
