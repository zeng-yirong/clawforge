import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # Helper to check file existence
    def check_file(path, score, max_score):
        nonlocal total_score
        full_path = os.path.join(workspace, path)
        exists = os.path.isfile(full_path)
        details.append({
            "item": f"File exists: {path}",
            "score": score if exists else 0,
            "max_score": max_score,
            "passed": exists,
            "reason": f"{'Found' if exists else 'Missing'} {full_path}"
        })
        total_score += score if exists else 0

    # 1. Check that required input files exist (10 points)
    required_inputs = [
        "data/devices/devices.json",
        "data/electricity/rates.json",
        "data/weather/weather.json",
        "data/health/health.json",
        "ops/occupancy.json"
    ]
    for f in required_inputs:
        check_file(f, 2, 2)  # 5 files * 2 = 10

    # 2. Check output file exists (10 points)
    output_path = os.path.join(workspace, "optimized_settings.json")
    output_exists = os.path.isfile(output_path)
    details.append({
        "item": "Output file exists: optimized_settings.json",
        "score": 10 if output_exists else 0,
        "max_score": 10,
        "passed": output_exists,
        "reason": f"{'Found' if output_exists else 'Missing'} {output_path}"
    })
    total_score += 10 if output_exists else 0

    if not output_exists:
        # Cannot proceed with further checks
        _finish(details, total_score)
        return

    # 3. Check JSON is valid (10 points)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        json_valid = True
        reason = "Valid JSON"
    except json.JSONDecodeError as e:
        json_valid = False
        reason = f"Invalid JSON: {e}"
    details.append({
        "item": "Output JSON is valid",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    total_score += 10 if json_valid else 0

    if not json_valid:
        _finish(details, total_score)
        return

    # 4. Check that the output contains exactly the 4 climate devices (10 points)
    expected_device_ids = {"Bedroom AC", "Bedroom Humidifier", "Living Room AC", "Living Room Humidifier"}
    actual_device_ids = set()
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict) and "device_id" in entry:
                actual_device_ids.add(entry["device_id"])
    else:
        details.append({
            "item": "Output is a list of device objects",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Expected a list"
        })
        total_score += 0
        _finish(details, total_score)
        return

    missing = expected_device_ids - actual_device_ids
    extra = actual_device_ids - expected_device_ids
    device_match = (len(missing) == 0 and len(extra) == 0)
    reason_parts = []
    if missing:
        reason_parts.append(f"Missing: {missing}")
    if extra:
        reason_parts.append(f"Extra: {extra}")
    reason = "; ".join(reason_parts) if reason_parts else "Exactly 4 expected devices present"
    details.append({
        "item": "Output contains exactly the 4 climate devices",
        "score": 10 if device_match else 0,
        "max_score": 10,
        "passed": device_match,
        "reason": reason
    })
    total_score += 10 if device_match else 0

    # 5. Check each device's recommended settings (15 points each, total 60)
    # Expected correct values based on env_builder data:
    # Weather: temp=32, humidity=65, time=14:00 (peak)
    # Occupancy: bedroom->Jane, living_room->John
    # Jane: temp pref 22-25 -> recommended 23.5 but we round to 23.0
    #       humidity pref 40-50 -> current 65 > 50 => humidifier OFF
    # John: temp pref 24-26 -> recommended 25.0
    #       humidity pref 50-60 -> current 65 > 60 => humidifier OFF
    # All other devices (smart plugs) not expected.
    expected = {
        "Bedroom AC": {"status": "on", "temperature": 23.0, "humidity": None},
        "Bedroom Humidifier": {"status": "off", "temperature": None, "humidity": None},
        "Living Room AC": {"status": "on", "temperature": 25.0, "humidity": None},
        "Living Room Humidifier": {"status": "off", "temperature": None, "humidity": None}
    }

    for dev_id in expected_device_ids:
        # Find entry in data
        entry = None
        for item in data:
            if item.get("device_id") == dev_id:
                entry = item
                break
        if entry is None:
            details.append({
                "item": f"Device '{dev_id}' found in output",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "Missing entry"
            })
            continue

        exp = expected[dev_id]
        fields_ok = True
        field_reason = []
        # Check status
        status = entry.get("recommended_status")
        if status != exp["status"]:
            fields_ok = False
            field_reason.append(f"status expected '{exp['status']}' got '{status}'")
        # Check temperature
        temp = entry.get("recommended_temperature")
        if temp != exp["temperature"]:
            fields_ok = False
            field_reason.append(f"temperature expected {exp['temperature']} got {temp}")
        # Check humidity
        hum = entry.get("recommended_humidity")
        if hum != exp["humidity"]:
            fields_ok = False
            field_reason.append(f"humidity expected {exp['humidity']} got {hum}")

        score = 15 if fields_ok else 0
        reason = "; ".join(field_reason) if field_reason else "All fields correct"
        details.append({
            "item": f"Correct settings for '{dev_id}'",
            "score": score,
            "max_score": 15,
            "passed": fields_ok,
            "reason": reason
        })
        total_score += score

    _finish(details, total_score)

def _finish(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
