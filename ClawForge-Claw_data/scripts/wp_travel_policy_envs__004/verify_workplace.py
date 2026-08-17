import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total = 0
    max_total = 0

    # 1. 检查 result/ 目录是否存在 (10分)
    max_total += 10
    result_dir = "result"
    if os.path.isdir(result_dir):
        details.append({
            "item": "result directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "result/ directory is present"
        })
        total += 10
    else:
        details.append({
            "item": "result directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "result/ directory not found"
        })

    # 2. 检查 result/booking_request.json 是否存在且合法 JSON (10分)
    max_total += 10
    request_path = os.path.join(result_dir, "booking_request.json") if os.path.isdir(result_dir) else None
    if request_path and os.path.isfile(request_path):
        try:
            with open(request_path, "r") as f:
                data = json.load(f)
            details.append({
                "item": "booking_request.json is valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "File exists and is valid JSON"
            })
            total += 10
        except (json.JSONDecodeError, Exception):
            details.append({
                "item": "booking_request.json is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "File is not valid JSON"
            })
            data = None
    else:
        details.append({
            "item": "booking_request.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "booking_request.json not found in result/"
        })
        data = None

    # 3. 检查 flight_id 字段 (30分)
    max_total += 30
    if data and isinstance(data, dict) and "flight_id" in data:
        if data["flight_id"] == "FL006":
            details.append({
                "item": "flight_id is FL006 (cheapest compliant flight)",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "Correct cheapest flight selected"
            })
            total += 30
        else:
            details.append({
                "item": "flight_id is FL006 (cheapest compliant flight)",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": f"flight_id is {data['flight_id']}, expected FL006"
            })
    else:
        details.append({
            "item": "flight_id is FL006 (cheapest compliant flight)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "Missing 'flight_id' field in JSON"
        })

    # 4. 检查 policy_id 字段 (10分)
    max_total += 10
    if data and isinstance(data, dict) and "policy_id" in data:
        if data["policy_id"] == "travel_policy_001":
            details.append({
                "item": "policy_id is travel_policy_001 (Business Travel Policy)",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Correct policy selected"
            })
            total += 10
        else:
            details.append({
                "item": "policy_id is travel_policy_001",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"policy_id is {data['policy_id']}, expected travel_policy_001"
            })
    else:
        details.append({
            "item": "policy_id is travel_policy_001",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing 'policy_id' field"
        })

    # 5. 检查 total_cost 是否为 2300 (20分)
    max_total += 20
    if data and isinstance(data, dict) and "total_cost" in data:
        try:
            cost = float(data["total_cost"])
            if cost == 2300:
                details.append({
                    "item": "total_cost is 2300 (correct cheapest price)",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": "Price matches the cheapest compliant flight"
                })
                total += 20
            else:
                details.append({
                    "item": "total_cost is 2300",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"total_cost is {cost}, expected 2300"
                })
        except (ValueError, TypeError):
            details.append({
                "item": "total_cost is 2300",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "total_cost is not numeric"
            })
    else:
        details.append({
            "item": "total_cost is 2300",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Missing 'total_cost' field"
        })

    # 6. 检查 requires_approval 是否为 true (10分)
    max_total += 10
    if data and isinstance(data, dict) and "requires_approval" in data:
        if data["requires_approval"] is True:
            details.append({
                "item": "requires_approval is true (cost > 2000)",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Approval required as 2300 > 2000"
            })
            total += 10
        else:
            details.append({
                "item": "requires_approval is true",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"requires_approval is {data['requires_approval']}, expected true"
            })
    else:
        details.append({
            "item": "requires_approval is true",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing 'requires_approval' field"
        })

    # 7. 检查 approver 是否正确 (10分)
    max_total += 10
    if data and isinstance(data, dict) and "approver" in data:
        approver = data["approver"]
        # 允许 name 或 email 形式
        expected_names = ["Alice", "alice@acme.com"]
        if approver in expected_names or (isinstance(approver, dict) and (approver.get("name") == "Alice" or approver.get("email") == "alice@acme.com")):
            details.append({
                "item": "approver is Alice (first approver from accounts)",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Correct approver identified"
            })
            total += 10
        else:
            details.append({
                "item": "approver is Alice",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"approver is {approver}, expected Alice or alice@acme.com"
            })
    else:
        details.append({
            "item": "approver is Alice",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing 'approver' field"
        })

    # 写入结果
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total}/{max_total}")

if __name__ == "__main__":
    main()
