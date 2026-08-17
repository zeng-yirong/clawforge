import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check output directory and file existence (10 points)
    target_path = os.path.join(workspace, "output", "peak_cost.json")
    if os.path.isfile(target_path):
        score_details.append({
            "item": "output/peak_cost.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "output/peak_cost.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"File not found at {target_path}"
        })
        # 如果文件不存在，后续无法检查，直接写入结果
        write_result(workspace, total_score, score_details)
        return

    # 2. JSON parse (10 points)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {str(e)}"
        })
        write_result(workspace, total_score, score_details)
        return

    # 3. Required fields (10 points)
    if "device_id" in data and "cost" in data:
        score_details.append({
            "item": "Required fields (device_id, cost)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Both fields present"
        })
        total_score += 10
    else:
        missing = []
        if "device_id" not in data: missing.append("device_id")
        if "cost" not in data: missing.append("cost")
        score_details.append({
            "item": "Required fields (device_id, cost)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing fields: {', '.join(missing)}"
        })
        write_result(workspace, total_score, score_details)
        return

    # 4. device_id correctness (20 points)
    expected_device_id = "ac-002"  # Living Room AC with 3500W
    actual_device_id = data["device_id"]
    # Also verify that this device exists and is an air_conditioner in the original data
    devices_path = os.path.join(workspace, "data", "devices", "devices.json")
    device_valid = False
    if os.path.isfile(devices_path):
        with open(devices_path, "r") as f:
            devices_data = json.load(f)
        for dev in devices_data["devices"]:
            if dev["device_id"] == actual_device_id:
                if dev["type"] == "air_conditioner":
                    device_valid = True
                break
    if actual_device_id == expected_device_id and device_valid:
        score_details.append({
            "item": "device_id correctness",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Correct device {expected_device_id} and type is air_conditioner"
        })
        total_score += 20
    elif actual_device_id == expected_device_id and not device_valid:
        score_details.append({
            "item": "device_id correctness",
            "score": 10,
            "max_score": 20,
            "passed": False,
            "reason": f"device_id matches expected but device type not air_conditioner"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "device_id correctness",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected {expected_device_id}, got {actual_device_id}"
        })

    # 5. cost value (50 points total, split: 20 for correct order of magnitude, 30 for precision)
    # Expected cost = 3500 * 0.45 / 1000 = 1.575 (we accept 1.57-1.58)
    expected_cost = 1.575
    actual_cost = data["cost"]
    # Check if cost is within tolerance of 0.02
    if isinstance(actual_cost, (int, float)):
        if abs(actual_cost - expected_cost) < 0.02:
            # Precision sub-score: 30 if within 0.005, else 15 if within 0.02
            if abs(actual_cost - expected_cost) < 0.005:
                cost_score = 50
                reason = f"Cost {actual_cost:.3f} matches expected {expected_cost:.3f} with high precision"
            else:
                cost_score = 35
                reason = f"Cost {actual_cost:.3f} close to expected {expected_cost:.3f} (tolerance 0.02)"
            score_details.append({
                "item": "cost value accuracy",
                "score": cost_score,
                "max_score": 50,
                "passed": True,
                "reason": reason
            })
            total_score += cost_score
        else:
            score_details.append({
                "item": "cost value accuracy",
                "score": 0,
                "max_score": 50,
                "passed": False,
                "reason": f"Cost {actual_cost} deviates from {expected_cost} by more than 0.02"
            })
    else:
        score_details.append({
            "item": "cost value accuracy",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"cost is not a number, got {type(actual_cost)}"
        })

    # Write final result
    write_result(workspace, total_score, score_details)

def write_result(workspace, total_score, details):
    result_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {result_path}")

if __name__ == "__main__":
    main()
