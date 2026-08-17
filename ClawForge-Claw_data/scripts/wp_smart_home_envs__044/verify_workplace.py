import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = os.path.join(workspace, "ops", "adjustments.json")
    details = []
    total_max = 100

    # 1. Check existence of output file
    if not os.path.isfile(output_file):
        details.append({
            "item": "ops/adjustments.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # Provide overall score without further checks
        score = sum(d["score"] for d in details)
        write_result(workspace, score, details)
        return
    else:
        details.append({
            "item": "ops/adjustments.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File present"
        })

    # 2. Parse JSON
    try:
        with open(output_file, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "JSON validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        score = sum(d["score"] for d in details)
        write_result(workspace, score, details)
        return
    details.append({
        "item": "JSON validity",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON"
    })

    # 3. Check top-level structure (expect dict with "adjustments" key)
    if not isinstance(data, dict) or "adjustments" not in data:
        details.append({
            "item": "Top-level structure contains 'adjustments' list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Expected dict with key 'adjustments'"
        })
        score = sum(d["score"] for d in details)
        write_result(workspace, score, details)
        return
    adjustments = data["adjustments"]
    if not isinstance(adjustments, list):
        details.append({
            "item": "Top-level structure contains 'adjustments' list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "'adjustments' is not a list"
        })
        score = sum(d["score"] for d in details)
        write_result(workspace, score, details)
        return
    details.append({
        "item": "Top-level structure contains 'adjustments' list",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Structure correct"
    })

    # 4. Check number of adjustments (exactly 2)
    if len(adjustments) != 2:
        details.append({
            "item": "Number of adjustments is 2",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found {len(adjustments)} adjustments, expected 2"
        })
        # Continue checking but will lose points
    else:
        details.append({
            "item": "Number of adjustments is 2",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Two adjustments present"
        })

    # Helper to find adjustment by device_id
    def find_adj(device_id):
        for adj in adjustments:
            if adj.get("device_id") == device_id:
                return adj
        return None

    # 5. Check bedroom AC adjustment
    ac_adj = find_adj("bd_ac_001")
    ac_score = 0
    ac_passed = False
    ac_reason = ""
    if ac_adj is None:
        ac_reason = "Adjustment for bd_ac_001 not found"
    else:
        target = ac_adj.get("target_temperature")
        if target is not None and (isinstance(target, int) or isinstance(target, float)):
            if target == 24:
                ac_score = 25
                ac_passed = True
                ac_reason = f"target_temperature = {target}"
            else:
                ac_reason = f"target_temperature = {target}, expected 24"
        else:
            ac_reason = "Missing or invalid target_temperature field"
    details.append({
        "item": "Bedroom AC adjustment (device_id=bd_ac_001, target_temperature=24)",
        "score": ac_score,
        "max_score": 25,
        "passed": ac_passed,
        "reason": ac_reason
    })

    # 6. Check bedroom humidifier adjustment
    hum_adj = find_adj("bd_hum_001")
    hum_score = 0
    hum_passed = False
    hum_reason = ""
    if hum_adj is None:
        hum_reason = "Adjustment for bd_hum_001 not found"
    else:
        target = hum_adj.get("target_humidity")
        if target is not None and (isinstance(target, int) or isinstance(target, float)):
            if target == 40:
                hum_score = 25
                hum_passed = True
                hum_reason = f"target_humidity = {target}"
            else:
                hum_reason = f"target_humidity = {target}, expected 40"
        else:
            hum_reason = "Missing or invalid target_humidity field"
    details.append({
        "item": "Bedroom Humidifier adjustment (device_id=bd_hum_001, target_humidity=40)",
        "score": hum_score,
        "max_score": 25,
        "passed": hum_passed,
        "reason": hum_reason
    })

    # 7. No extra adjustments (only the two bedroom devices)
    extra_devices = [adj for adj in adjustments if adj.get("device_id") not in ("bd_ac_001", "bd_hum_001")]
    if extra_devices:
        details.append({
            "item": "No adjustments for non-bedroom devices",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found extra adjustments: {[d.get('device_id') for d in extra_devices]}"
        })
    else:
        details.append({
            "item": "No adjustments for non-bedroom devices",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only bedroom devices adjusted"
        })

    # Compute total
    total_score = sum(d["score"] for d in details)
    write_result(workspace, total_score, details)

def write_result(workspace, score, details):
    result_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": score,
        "details": details
    }
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
