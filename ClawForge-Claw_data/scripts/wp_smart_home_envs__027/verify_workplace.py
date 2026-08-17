import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    # Expected reference (ground truth)
    expected_devices_to_off = {"ac_living", "humidifier_living", "tv_plug", "floor_lamp", "desk_plug"}
    expected_total_power = 2000 + 350 + 100 + 60 + 200  # 2710

    details = []
    total_score = 0

    # Item 1: check file existence
    if os.path.exists("ops/optimization_plan.json"):
        details.append({
            "item": "File ops/optimization_plan.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found"
        })
        total_score += 10
    else:
        details.append({
            "item": "File ops/optimization_plan.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # If file missing, no further checks possible
        _write_score(total_score, details)
        return

    # Item 2: JSON syntax
    try:
        with open("ops/optimization_plan.json", "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON syntax valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "No parse error"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON syntax valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        _write_score(total_score, details)
        return

    # Item 3: required fields present
    has_devices = "devices_to_off" in data
    has_power = "total_savings_watts" in data
    if has_devices and has_power:
        details.append({
            "item": "Contains 'devices_to_off' and 'total_savings_watts'",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Both fields present"
        })
        total_score += 10
    else:
        missing = []
        if not has_devices: missing.append("devices_to_off")
        if not has_power: missing.append("total_savings_watts")
        details.append({
            "item": "Contains 'devices_to_off' and 'total_savings_watts'",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing fields: {', '.join(missing)}"
        })
        # Still try to grade partially
        total_score += 0

    # Item 4: devices_to_off content correctness (30 points)
    devices_to_off = data.get("devices_to_off", [])
    if isinstance(devices_to_off, list):
        actual_set = set(devices_to_off)
    else:
        actual_set = set()

    if actual_set == expected_devices_to_off:
        details.append({
            "item": "devices_to_off set matches expected",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "Exactly the correct devices"
        })
        total_score += 30
    else:
        # Partial credit: count correct matches
        correct = len(actual_set & expected_devices_to_off)
        extra = len(actual_set - expected_devices_to_off)
        missing = len(expected_devices_to_off - actual_set)
        score = max(0, 30 - 5*(missing + extra))  # penalize 5 per mistake
        details.append({
            "item": "devices_to_off set matches expected",
            "score": score,
            "max_score": 30,
            "passed": False,
            "reason": f"Correct items: {correct}, extra: {extra}, missing: {missing}"
        })
        total_score += score

    # Item 5: total_savings_watts correctness (40 points)
    actual_power = data.get("total_savings_watts", None)
    if actual_power == expected_total_power:
        details.append({
            "item": "total_savings_watts correct",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": f"Value {actual_power} matches expected 2710"
        })
        total_score += 40
    else:
        # Check if it equals sum of devices_to_off power values from device registry
        # Fallback: if value is wrong but could be derived from actual devices list
        # Load device registry to compute sum
        base_score = 0
        try:
            with open("data/devices/devices.json", "r") as f:
                dev_data = json.load(f)
            power_map = {d["device_id"]: d["power_watts"] for d in dev_data.get("devices", [])}
            sum_from_list = sum(power_map.get(d, 0) for d in devices_to_off if isinstance(d, str))
            if actual_power == sum_from_list:
                base_score = 20  # Partial: at least internally consistent
                reason = f"Value {actual_power} does not match expected 2710, but matches sum of listed devices ({sum_from_list})"
            else:
                reason = f"Value {actual_power} is neither expected nor sum of listed devices"
        except Exception:
            reason = f"Value {actual_power} incorrect, expected 2710"

        details.append({
            "item": "total_savings_watts correct",
            "score": base_score,
            "max_score": 40,
            "passed": False,
            "reason": reason
        })
        total_score += base_score

    # Write score
    _write_score(total_score, details)

def _write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
