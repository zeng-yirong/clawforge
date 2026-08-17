#!/usr/bin/env python3
"""Verify the agent's output for task wp_cloud_cost_ledger_env__016.

Checks:
- Expected directory structure (ops/ exists)
- Output file ops/final_cost.json exists and is valid JSON
- Contains required fields: cluster_name, billing_month, currency, total_cost
- total_cost matches the expected value calculated from env_builder data
- No extra unexpected fields (strict)
- Edge cases: non-positive quantities are ignored (shared-ops zero vcpu should not affect)
- Scoring: weighted per item.
"""
import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_card = []

    # 1. Check that ops directory exists (5 pts)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_card.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found ops/"})
    else:
        score_card.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ directory missing"})
        # if missing, skip further file checks
        finalize(score_card)
        return

    # 2. Check that ops/final_cost.json exists (10 pts)
    report_path = os.path.join(ops_dir, "final_cost.json")
    if not os.path.isfile(report_path):
        score_card.append({"item": "final_cost.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File ops/final_cost.json not found"})
        finalize(score_card)
        return
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        score_card.append({"item": "final_cost.json is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
    except (json.JSONDecodeError, Exception) as e:
        score_card.append({"item": "final_cost.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        finalize(score_card)
        return

    # 3. Check required fields (15 pts)
    required_fields = ["cluster_name", "billing_month", "currency", "total_cost"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        score_card.append({"item": "Required fields present", "score": 15, "max_score": 15, "passed": True, "reason": f"All {required_fields} present"})
    else:
        score_card.append({"item": "Required fields present", "score": 0, "max_score": 15, "passed": False, "reason": f"Missing fields: {missing}"})
        finalize(score_card)
        return

    # 4. Check no extra fields (5 pts)
    allowed = set(required_fields)
    extra = [k for k in data if k not in allowed]
    if not extra:
        score_card.append({"item": "No extra fields", "score": 5, "max_score": 5, "passed": True, "reason": "No unexpected fields"})
    else:
        score_card.append({"item": "No extra fields", "score": 0, "max_score": 5, "passed": False, "reason": f"Extra fields: {extra}"})
        finalize(score_card)
        return

    # 5. Check cluster_name value (5 pts)
    if data["cluster_name"] == "ads-ranking":
        score_card.append({"item": "cluster_name correct", "score": 5, "max_score": 5, "passed": True, "reason": "cluster_name = 'ads-ranking'"})
    else:
        score_card.append({"item": "cluster_name correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected 'ads-ranking', got '{data['cluster_name']}'"})
        finalize(score_card)
        return

    # 6. Check billing_month (5 pts)
    if data["billing_month"] == "2026-06":
        score_card.append({"item": "billing_month correct", "score": 5, "max_score": 5, "passed": True, "reason": "billing_month = '2026-06'"})
    else:
        score_card.append({"item": "billing_month correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected '2026-06', got '{data['billing_month']}'"})
        finalize(score_card)
        return

    # 7. Check currency (5 pts)
    if data["currency"] == "USD":
        score_card.append({"item": "currency correct", "score": 5, "max_score": 5, "passed": True, "reason": "currency = 'USD'"})
    else:
        score_card.append({"item": "currency correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected 'USD', got '{data['currency']}'"})
        finalize(score_card)
        return

    # 8. Check total_cost value (the most important: 50 pts)
    # Expected calculation from env_builder data:
    # Ads-ranking entries: rle_001 (vcpu 120 * 0.05 = 6.0), rle_002 (mem 512 * 0.01 = 5.12),
    # rle_003 (gpu 8 * 0.5 = 4.0), rle_004 (block 2000 * 0.08 = 160.0), rle_005 (object 5000 * 0.02 = 100.0)
    # Total = 275.12
    expected_total = 275.12
    actual_total = data["total_cost"]
    # Allow floating point tolerance (1e-6 relative)
    if isinstance(actual_total, (int, float)) and math.isclose(actual_total, expected_total, rel_tol=1e-6):
        score_card.append({"item": "total_cost correct", "score": 50, "max_score": 50, "passed": True,
                           "reason": f"Expected {expected_total}, got {actual_total}"})
    else:
        score_card.append({"item": "total_cost correct", "score": 0, "max_score": 50, "passed": False,
                           "reason": f"Expected {expected_total}, got {actual_total}"})
        finalize(score_card)
        return

    finalize(score_card)

def finalize(score_card):
    total = sum(item["score"] for item in score_card)
    result = {
        "total_score": total,
        "details": score_card
    }
    # Write to workplace_score.json in the workspace root
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    # Print summary for human readability
    print(f"Total score: {total}/100")
    for d in score_card:
        status = "PASS" if d["passed"] else "FAIL"
        print(f"  [{status}] {d['item']}: {d['score']}/{d['max_score']} - {d['reason']}")
    sys.exit(0 if total == 100 else 1)

if __name__ == "__main__":
    main()
