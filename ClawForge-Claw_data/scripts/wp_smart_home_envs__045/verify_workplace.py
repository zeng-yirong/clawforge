import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_file = os.path.join(workspace, "ops", "recommendations.json")
    details = []
    total_score = 0
    max_total = 100

    # 1. Check file exists (10 points)
    if os.path.isfile(result_file):
        details.append({
            "item": "recommendations.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found at ops/recommendations.json"
        })
        total_score += 10
    else:
        details.append({
            "item": "recommendations.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found at ops/recommendations.json"
        })
        # If file missing, cannot continue checking content
        _write_score(total_score, max_total, details, workspace)
        return

    # 2. Parse JSON validity (10 points)
    try:
        with open(result_file, "r") as f:
            recs = json.load(f)
        if isinstance(recs, list):
            details.append({
                "item": "JSON format and type",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Valid JSON, root is list"
            })
            total_score += 10
        else:
            details.append({
                "item": "JSON format and type",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Root element is not a list"
            })
            _write_score(total_score, max_total, details, workspace)
            return
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON format and type",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        _write_score(total_score, max_total, details, workspace)
        return

    # 3. Check items structure and required fields (10 points)
    field_ok = True
    for i, r in enumerate(recs):
        if not isinstance(r, dict):
            field_ok = False
            break
        if not all(k in r for k in ("device_id", "setting_type", "recommended_value")):
            field_ok = False
            break
    if field_ok:
        details.append({
            "item": "Required fields present in each entry",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All entries have device_id, setting_type, recommended_value"
        })
        total_score += 10
    else:
        details.append({
            "item": "Required fields present in each entry",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing required fields in one or more entries"
        })
        _write_score(total_score, max_total, details, workspace)
        return

    # 4. Extract recommendations and verify correctness (70 points)
    # Expected correct outputs (order irrelevant)
    expected = [
        {"device_id": "ac_bedroom_01", "setting_type": "target_temperature", "recommended_value": 23},
        {"device_id": "humidifier_bedroom_01", "setting_type": "target_humidity", "recommended_value": 50}
    ]
    # Convert recs to comparable tuples (sorted by device_id)
    recs_normalized = set()
    for r in recs:
        recs_normalized.add((r["device_id"], r["setting_type"], r["recommended_value"]))
    expected_set = set((e["device_id"], e["setting_type"], e["recommended_value"]) for e in expected)

    # Score AC part (35 points)
    ac_entry = ("ac_bedroom_01", "target_temperature", 23)
    if ac_entry in recs_normalized:
        details.append({
            "item": "Bedroom AC temperature recommendation",
            "score": 35,
            "max_score": 35,
            "passed": True,
            "reason": "Correct device_id, setting_type, and recommended_value (23)"
        })
        total_score += 35
    else:
        # Check if present but wrong value
        ac_present = [r for r in recs if r["device_id"] == "ac_bedroom_01" and r["setting_type"] == "target_temperature"]
        if ac_present:
            details.append({
                "item": "Bedroom AC temperature recommendation",
                "score": 0,
                "max_score": 35,
                "passed": False,
                "reason": f"Found entry for ac_bedroom_01 but recommended_value is {ac_present[0]['recommended_value']}, expected 23"
            })
        else:
            details.append({
                "item": "Bedroom AC temperature recommendation",
                "score": 0,
                "max_score": 35,
                "passed": False,
                "reason": "Missing entry for ac_bedroom_01 with setting_type target_temperature"
            })

    # Score humidifier part (35 points)
    hum_entry = ("humidifier_bedroom_01", "target_humidity", 50)
    if hum_entry in recs_normalized:
        details.append({
            "item": "Bedroom Humidifier humidity recommendation",
            "score": 35,
            "max_score": 35,
            "passed": True,
            "reason": "Correct device_id, setting_type, and recommended_value (50)"
        })
        total_score += 35
    else:
        hum_present = [r for r in recs if r["device_id"] == "humidifier_bedroom_01" and r["setting_type"] == "target_humidity"]
        if hum_present:
            details.append({
                "item": "Bedroom Humidifier humidity recommendation",
                "score": 0,
                "max_score": 35,
                "passed": False,
                "reason": f"Found entry for humidifier_bedroom_01 but recommended_value is {hum_present[0]['recommended_value']}, expected 50"
            })
        else:
            details.append({
                "item": "Bedroom Humidifier humidity recommendation",
                "score": 0,
                "max_score": 35,
                "passed": False,
                "reason": "Missing entry for humidifier_bedroom_01 with setting_type target_humidity"
            })

    # Write final score
    _write_score(total_score, max_total, details, workspace)


def _write_score(total, max_total, details, workspace):
    # Clamp total to 100
    total = min(max(total, 0), 100)
    output = {
        "total_score": total,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written to {out_path}: {total}/100")


if __name__ == "__main__":
    main()
