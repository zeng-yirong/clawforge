#!/usr/bin/env python3
import json
import os
import sys
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    total_score = 0

    # ---------- 1. File existence (10) ----------
    rec_path = os.path.join(workspace, "ops", "booking_recommendation.json")
    if os.path.isfile(rec_path):
        scores.append({
            "item": "ops/booking_recommendation.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found"
        })
        total_score += 10
    else:
        scores.append({
            "item": "ops/booking_recommendation.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        _write_score(scores)
        return

    # ---------- 2. Valid JSON (10) ----------
    try:
        with open(rec_path, "r") as f:
            data = json.load(f)
        scores.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parse succeeded"
        })
        total_score += 10
    except Exception as e:
        scores.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        _write_score(scores)
        return

    # ---------- 3. Required fields existence (10) ----------
    required_fields = [
        "flight_id", "platform_id", "base_price",
        "transaction_fee", "service_fee", "total_cost",
        "is_compliant", "needs_approval", "policy_id"
    ]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        scores.append({
            "item": "All required fields present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Fields: {', '.join(required_fields)}"
        })
        total_score += 10
    else:
        scores.append({
            "item": "All required fields present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing: {missing}"
        })
        _write_score(scores)
        return

    # ---------- 4. flight_id (10) ----------
    if data["flight_id"] == "SB101":
        scores.append({"item": "flight_id", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
        total_score += 10
    else:
        scores.append({"item": "flight_id", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected SB101, got {data['flight_id']}"})

    # ---------- 5. platform_id (10) ----------
    if data["platform_id"] == "skybook":
        scores.append({"item": "platform_id", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
        total_score += 10
    else:
        scores.append({"item": "platform_id", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected skybook, got {data['platform_id']}"})

    # ---------- 6. base_price (10) ----------
    if data["base_price"] == 1100:
        scores.append({"item": "base_price", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
        total_score += 10
    else:
        scores.append({"item": "base_price", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 1100, got {data['base_price']}"})

    # ---------- 7. transaction_fee (5) + service_fee (5) ----------
    fee_ok = True
    if data.get("transaction_fee") == 20:
        scores.append({"item": "transaction_fee", "score": 5, "max_score": 5, "passed": True, "reason": "Correct"})
        total_score += 5
    else:
        scores.append({"item": "transaction_fee", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected 20, got {data.get('transaction_fee')}"})
        fee_ok = False

    if data.get("service_fee") == 30:
        scores.append({"item": "service_fee", "score": 5, "max_score": 5, "passed": True, "reason": "Correct"})
        total_score += 5
    else:
        scores.append({"item": "service_fee", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected 30, got {data.get('service_fee')}"})
        fee_ok = False

    # ---------- 8. total_cost (10) ----------
    expected_total = 1150
    actual = data.get("total_cost")
    if actual == expected_total:
        scores.append({"item": "total_cost", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
        total_score += 10
    else:
        scores.append({"item": "total_cost", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_total}, got {actual}"})

    # ---------- 9. is_compliant (10) ----------
    if data.get("is_compliant") is True:
        scores.append({"item": "is_compliant", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
        total_score += 10
    else:
        scores.append({"item": "is_compliant", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected true, got {data.get('is_compliant')}"})

    # ---------- 10. needs_approval (10) ----------
    if data.get("needs_approval") is True:
        scores.append({"item": "needs_approval", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
        total_score += 10
    else:
        scores.append({"item": "needs_approval", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected true, got {data.get('needs_approval')}"})

    # ---------- 11. policy_id (10) ----------
    if data.get("policy_id") == "acme_corp_business_travel_policy_v2":
        scores.append({"item": "policy_id", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
        total_score += 10
    else:
        scores.append({"item": "policy_id", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected acme_corp_business_travel_policy_v2, got {data.get('policy_id')}"})

    # ---- finalize ----
    _write_score(scores, total_score)

def _write_score(scores, total_score=None):
    if total_score is None:
        total_score = sum(s["score"] for s in scores)
    result = {
        "total_score": total_score,
        "details": scores
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
