import sys
import json
import os
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check output directory exists
    output_dir = os.path.join(workspace, "output")
    dir_exists = os.path.isdir(output_dir)
    score_details.append({
        "item": "output directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Output directory exists" if dir_exists else "output/ directory not found"
    })
    if dir_exists:
        total_score += 10

    # 2. Check booking_request.json exists
    req_path = os.path.join(output_dir, "booking_request.json")
    file_exists = os.path.isfile(req_path)
    score_details.append({
        "item": "booking_request.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "output/booking_request.json not found"
    })
    if file_exists:
        total_score += 10

    # 3. JSON parseable
    data = None
    parse_ok = False
    if file_exists:
        try:
            with open(req_path, "r") as f:
                data = json.load(f)
            parse_ok = True
            score_details.append({
                "item": "JSON structure is valid",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Valid JSON"
            })
            total_score += 10
        except (json.JSONDecodeError, ValueError):
            score_details.append({
                "item": "JSON structure is valid",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "File is not valid JSON"
            })
    else:
        score_details.append({
            "item": "JSON structure is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File missing, cannot parse"
        })

    # 4. Required fields present
    required_fields = ["flight_id", "price", "currency", "policy_id", "platform"]
    missing = []
    if data and isinstance(data, dict):
        for field in required_fields:
            if field not in data:
                missing.append(field)
        fields_ok = len(missing) == 0
        score_details.append({
            "item": "Required fields present",
            "score": 20 if fields_ok else 0,
            "max_score": 20,
            "passed": fields_ok,
            "reason": f"Missing: {', '.join(missing)}" if missing else "All required fields present"
        })
        if fields_ok:
            total_score += 20
    else:
        score_details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Data is not a dict or missing"
        })

    # 5. flight_id correctness
    flight_id_ok = False
    if data and isinstance(data, dict) and "flight_id" in data:
        flight_id_ok = data["flight_id"] == "SKY001"
        score_details.append({
            "item": "flight_id value",
            "score": 15 if flight_id_ok else 0,
            "max_score": 15,
            "passed": flight_id_ok,
            "reason": f"flight_id = {data.get('flight_id')}" if flight_id_ok else f"Expected SKY001, got {data.get('flight_id')}"
        })
        if flight_id_ok:
            total_score += 15
    else:
        score_details.append({
            "item": "flight_id value",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "flight_id field missing"
        })

    # 6. price correctness
    price_ok = False
    if data and isinstance(data, dict) and "price" in data:
        price_ok = data["price"] == 4200
        score_details.append({
            "item": "price value",
            "score": 15 if price_ok else 0,
            "max_score": 15,
            "passed": price_ok,
            "reason": f"price = {data.get('price')}" if price_ok else f"Expected 4200, got {data.get('price')}"
        })
        if price_ok:
            total_score += 15
    else:
        score_details.append({
            "item": "price value",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "price field missing"
        })

    # 7. policy_id correctness
    policy_ok = False
    if data and isinstance(data, dict) and "policy_id" in data:
        policy_ok = data["policy_id"] == "bp_001"
        score_details.append({
            "item": "policy_id value",
            "score": 15 if policy_ok else 0,
            "max_score": 15,
            "passed": policy_ok,
            "reason": f"policy_id = {data.get('policy_id')}" if policy_ok else f"Expected bp_001, got {data.get('policy_id')}"
        })
        if policy_ok:
            total_score += 15
    else:
        score_details.append({
            "item": "policy_id value",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "policy_id field missing"
        })

    # 8. platform consistency (bonus not needed but include)
    # optional: platform should be SkyBook
    platform_ok = False
    if data and isinstance(data, dict) and "platform" in data:
        platform_ok = data["platform"] == "SkyBook"
        score_details.append({
            "item": "platform value (bonus check)",
            "score": 5 if platform_ok else 0,
            "max_score": 5,
            "passed": platform_ok,
            "reason": f"platform = {data.get('platform')}" if platform_ok else f"Expected SkyBook, got {data.get('platform')}"
        })
        if platform_ok:
            total_score += 5
    else:
        score_details.append({
            "item": "platform value (bonus check)",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "platform field missing"
        })

    # Final score capped at 100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
