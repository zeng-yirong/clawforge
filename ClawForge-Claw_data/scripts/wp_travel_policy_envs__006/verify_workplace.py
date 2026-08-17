import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace).resolve()
    score = 0
    max_score = 100
    details = []

    # 1. ops directory exists (10分)
    ops_dir = base / "ops"
    if ops_dir.is_dir():
        score += 10
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found ops directory"
        })
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops directory not found"
        })

    # 2. ops/approval_request.json exists and is valid JSON (10分)
    req_file = ops_dir / "approval_request.json"
    if req_file.is_file():
        score += 10
        detail = {
            "item": "approval_request.json exists and is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found"
        }
        try:
            data = json.loads(req_file.read_text())
        except json.JSONDecodeError as e:
            data = None
            detail["score"] = 0
            detail["passed"] = False
            detail["reason"] = f"Invalid JSON: {e}"
        details.append(detail)
    else:
        details.append({
            "item": "approval_request.json exists and is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        data = None

    # If file is valid, check fields
    if isinstance(data, dict):
        # 3. Contains required fields (20分)
        required_fields = ["booking_id", "amount", "account_id", "approver"]
        missing = [f for f in required_fields if f not in data]
        if not missing:
            score += 20
            details.append({
                "item": "Contains all required fields (booking_id, amount, account_id, approver)",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "All fields present"
            })
        else:
            details.append({
                "item": "Contains all required fields",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Missing fields: {missing}"
            })

        # 4. booking_id correct (15分)
        if data.get("booking_id") == "BK-20250315-B":
            score += 15
            details.append({
                "item": "booking_id is correct (BK-20250315-B)",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "Match"
            })
        else:
            details.append({
                "item": "booking_id is correct",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Got {data.get('booking_id')}, expected BK-20250315-B"
            })

        # 5. amount correct (15分)
        expected_amount = 12500.0
        received = data.get("amount")
        if isinstance(received, (int, float)) and abs(received - expected_amount) < 0.01:
            score += 15
            details.append({
                "item": "amount is correct (12500.0)",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": f"Amount matches {expected_amount}"
            })
        else:
            details.append({
                "item": "amount is correct",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Got {received}, expected {expected_amount}"
            })

        # 6. account_id correct (10分)
        if data.get("account_id") == "acme_corp":
            score += 10
            details.append({
                "item": "account_id is correct (acme_corp)",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Match"
            })
        else:
            details.append({
                "item": "account_id is correct",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Got {data.get('account_id')}, expected acme_corp"
            })

        # 7. approver correct (10分)
        expected_approver = "jeff@acme.com"
        if data.get("approver") == expected_approver:
            score += 10
            details.append({
                "item": "approver is correct (jeff@acme.com)",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Match"
            })
        else:
            details.append({
                "item": "approver is correct",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Got {data.get('approver')}, expected {expected_approver}"
            })

        # 8. No extra fields (5分, 扣分制? 这里作为奖励)
        expected_keys = set(required_fields)
        actual_keys = set(data.keys())
        extra = actual_keys - expected_keys
        if not extra:
            score += 5
            details.append({
                "item": "No extra fields",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "All keys are expected"
            })
        else:
            details.append({
                "item": "No extra fields",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Extra keys: {extra}"
            })
    else:
        # Not a dict, fill zeros for remaining items
        for item_name, item_max in [
            ("Contains all required fields", 20),
            ("booking_id is correct", 15),
            ("amount is correct", 15),
            ("account_id is correct", 10),
            ("approver is correct", 10),
            ("No extra fields", 5)
        ]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": item_max,
                "passed": False,
                "reason": "File not valid or not present"
            })

    # Ensure total score does not exceed max
    total = min(score, max_score)
    output = {
        "total_score": total,
        "details": details
    }
    with open(base / "workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
