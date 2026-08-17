#!/usr/bin/env python3
import json
import os
import sys

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def compute_expected_recommendations(base_dir):
    """Compute the single correct recommendations based on initial data."""
    # load data
    devices = load_json(os.path.join(base_dir, "data/devices/devices.json"))["devices"]
    weather = load_json(os.path.join(base_dir, "data/weather/weather.json"))["weather_data"][0]
    users = load_json(os.path.join(base_dir, "data/health/health.json"))["users"]
    rates = load_json(os.path.join(base_dir, "data/electricity/rates.json"))["rates"]

    current_hour = 14  # timestamp implies 14:00 (UTC)

    # find peak rate
    peak_rate = None
    for r in rates:
        if r["start_hour"] <= current_hour < r["end_hour"] and r["period"] == "peak":
            peak_rate = r
            break
    is_peak = peak_rate is not None

    # use Jane's preferences (strictest)
    jane = next(u for u in users if u["user_id"] == "jane")
    temp_min, temp_max = jane["temperature_preference"]["min"], jane["temperature_preference"]["max"]
    hum_min, hum_max = jane["humidity_preference"]["min"], jane["humidity_preference"]["max"]
    target_temp = (temp_min + temp_max) / 2  # 23
    target_hum = (hum_min + hum_max) / 2    # 45

    current_temp = weather["temperature"]
    current_hum = weather["humidity"]

    # Build recommendations for every device
    recommendations = []
    for dev in devices:
        rec = {"device_id": dev["device_id"]}
        if dev["type"] == "air_conditioner":
            if current_temp > temp_max:
                rec["action"] = "adjust"
                rec["target"] = target_temp
            else:
                rec["action"] = "keep"  # no change needed
        elif dev["type"] == "humidifier":
            if current_hum < hum_min:
                rec["action"] = "turn_on"
                rec["target"] = target_hum
            else:
                rec["action"] = "turn_off"
        else:  # smart_plug
            # if not in bedroom or living room and it's peak, turn off
            if dev["location"] not in ("bedroom", "living_room") and is_peak:
                rec["action"] = "turn_off"
            else:
                rec["action"] = "keep"
        recommendations.append(rec)

    # normalize: remove "keep" actions? The prompt expects all devices; we'll output all with action kept as is.
    # But agent likely uses "keep" or omits? The prompt specified turn_on/off/adjust, so they might use "keep" which is not allowed.
    # We'll map "keep" to a representation that can be matched flexibly; for scoring we'll allow both "keep" and not listing.
    # Actually the prompt says action must be turn_on/turn_off/adjust. So we cannot use "keep".
    # We need to decide: for devices that should stay as is, what action? The prompt didn't explicitly say, but the template had only three actions.
    # Possible interpretations: "turn_off" for humidifier when already at correct humidity is reasonable (since it's not needed),
    # and for AC when already in range we could keep it on but not adjust. But the system may still want it on. The safest is to leave it on with no adjustment.
    # However the prompt says list all devices. For AC when temp is fine, we can say "keep_on" or "no_change". But the allowed actions are three.
    # To avoid ambiguity, we can require agent to use "adjust" only when changing, and for others use either "turn_on" or "turn_off" depending on whether they should be on.
    # Let's define: for AC: if temp>max -> adjust (cool to target), else -> turn_on (keep on). For humidifier: if humidity<min -> turn_on (set target), else -> turn_off.
    # For smart plugs: in bedroom/living_room -> turn_on (keep on), else if peak -> turn_off.
    # This gives a clear set of three actions for all.
    expected = []
    for dev in devices:
        item = {"device_id": dev["device_id"]}
        if dev["type"] == "air_conditioner":
            if current_temp > temp_max:
                item["action"] = "adjust"
                item["target"] = target_temp
            else:
                item["action"] = "turn_on"
        elif dev["type"] == "humidifier":
            if current_hum < hum_min:
                item["action"] = "turn_on"
                item["target"] = target_hum
            else:
                item["action"] = "turn_off"
        else:  # smart_plug
            if dev["location"] in ("bedroom", "living_room"):
                item["action"] = "turn_on"
            else:
                if is_peak:
                    item["action"] = "turn_off"
                else:
                    item["action"] = "turn_on"
        expected.append(item)
    return expected

def verify(workspace):
    score = 0
    details = []

    # 1. Check ops/control_recommendations.json exists
    path = os.path.join(workspace, "ops/control_recommendations.json")
    if not os.path.isfile(path):
        details.append({"item": "output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "File ops/control_recommendations.json not found"})
        # cannot continue
        total = 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    details.append({"item": "output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
    score += 10

    # 2. JSON parseable and has top-level key "recommendations"
    try:
        data = load_json(path)
    except Exception as e:
        details.append({"item": "JSON validity", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        finalize(workspace, score, details)
        return

    if not isinstance(data, dict) or "recommendations" not in data:
        details.append({"item": "JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "Missing top-level key 'recommendations'"})
        finalize(workspace, score, details)
        return

    recommendations = data["recommendations"]
    if not isinstance(recommendations, list):
        details.append({"item": "JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "'recommendations' is not a list"})
        finalize(workspace, score, details)
        return

    details.append({"item": "JSON validity & structure", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON with recommendations array"})
    score += 10

    # 3. Compute expected
    expected = compute_expected_recommendations(workspace)
    expected_dict = {e["device_id"]: e for e in expected}
    agent_dict = {}
    for rec in recommendations:
        if not isinstance(rec, dict) or "device_id" not in rec or "action" not in rec:
            continue
        agent_dict[rec["device_id"]] = rec

    # 4. Device completeness: all expected devices should be present, no extra
    # Note: the builder includes 7 devices (6 + floor_lamp). We expect all 7.
    expected_ids = sorted(e["device_id"] for e in expected)
    agent_ids = sorted(agent_dict.keys())
    if expected_ids == agent_ids:
        details.append({"item": "device completeness", "score": 10, "max_score": 10, "passed": True, "reason": "All 7 devices present, no extras"})
        score += 10
    else:
        missing = set(expected_ids) - set(agent_ids)
        extra = set(agent_ids) - set(expected_ids)
        d_reason = f"Missing: {missing}, Extra: {extra}" if missing or extra else ""
        details.append({"item": "device completeness", "score": 0, "max_score": 10, "passed": False, "reason": d_reason})
        # continue scoring partial

    # 5. Per-device action and target accuracy (12 points each, total 84? but we have 7 devices, so 12 each =84)
    # We'll make it 12 points per device, but we only have 70 points left after 10+10+10=30? Actually we have 100 total.
    # Let's reallocate: file existence 10, JSON 10, completeness 10, each device 10 -> 7*10=70, total 100.
    # So each device 10 points.
    device_score = 0
    for dev_id in expected_ids:
        exp = expected_dict[dev_id]
        ag = agent_dict.get(dev_id)
        if ag is None:
            device_score += 0
            details.append({"item": f"device {dev_id}", "score": 0, "max_score": 10, "passed": False, "reason": "Device missing"})
            continue
        # check action
        exp_action = exp["action"]
        ag_action = ag.get("action")
        if ag_action is None:
            device_score += 0
            details.append({"item": f"device {dev_id}", "score": 0, "max_score": 10, "passed": False, "reason": "Action field missing"})
            continue
        if ag_action != exp_action:
            device_score += 0
            details.append({"item": f"device {dev_id}", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected action '{exp_action}', got '{ag_action}'"})
            continue
        # if action is "adjust" or "turn_on" with target, check target
        if exp_action in ("adjust", "turn_on"):
            exp_target = exp.get("target")
            ag_target = ag.get("target")
            if ag_target is None:
                device_score += 0
                details.append({"item": f"device {dev_id}", "score": 0, "max_score": 10, "passed": False, "reason": "Target missing for action requiring it"})
                continue
            # compare with tolerance
            try:
                if abs(float(ag_target) - exp_target) > 0.01:
                    device_score += 0
                    details.append({"item": f"device {dev_id}", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected target {exp_target}, got {ag_target}"})
                    continue
            except (ValueError, TypeError):
                device_score += 0
                details.append({"item": f"device {dev_id}", "score": 0, "max_score": 10, "passed": False, "reason": f"Target not numeric: {ag_target}"})
                continue
        device_score += 10
        details.append({"item": f"device {dev_id}", "score": 10, "max_score": 10, "passed": True, "reason": f"Action '{exp_action}' and target match"})
    score += device_score

    # finalize
    finalize(workspace, score, details)

def finalize(workspace, total, details):
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
