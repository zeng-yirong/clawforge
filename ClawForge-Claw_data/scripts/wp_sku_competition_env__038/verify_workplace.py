#!/usr/bin/env python3
"""Verify the agent's output for wp_sku_competition_env__038.

Expected output: workspace/ops/price_comparison.json
Content must be a JSON object with exactly three fields:
  - lumina_avg: float (one decimal)
  - pure_avg: float (one decimal)
  - diff: float (one decimal, lumina_avg - pure_avg)

Expected values (computed from builder data):
  LuminaSkin active Hydration Serum SKUs: LUM-HS-001 (25.0), LUM-HS-002 (36.0)  -> avg = 30.5
  PureLattice active Hydration Serum SKUs: PL-HS-001 (22.0), PL-HS-002 (32.0) -> avg = 27.0
  diff = 30.5 - 27.0 = 3.5

Score breakdown:
  - output file exists: 10 pts
  - JSON is valid and has correct structure: 20 pts
  - lumina_avg = 30.5: 25 pts
  - pure_avg   = 27.0: 25 pts
  - diff       = 3.5 : 20 pts
Total: 100 pts
"""
import json
import sys
import os
import math

def check(condition, item_name, score, max_score, details):
    if condition:
        details.append({"item": item_name, "score": score, "max_score": max_score, "passed": True, "reason": "OK"})
        return score
    else:
        details.append({"item": item_name, "score": 0, "max_score": max_score, "passed": False, "reason": "Failed"})
        return 0

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = os.path.join(workspace, "ops", "price_comparison.json")
    details = []
    total = 0

    # 1. file existence (10 pts)
    file_exists = os.path.isfile(output_path)
    total += check(file_exists, "output file exists", 10, 10, details)
    if not file_exists:
        # Short-circuit: no file, rest impossible
        result = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print("FAIL: output file not found, score 0")
        return

    # 2. JSON structure (20 pts)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError):
        total += check(False, "JSON valid", 20, 20, details)
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"FAIL: invalid JSON, score {total}")
        return

    # Check keys and types
    keys_ok = isinstance(data, dict) and all(k in data for k in ("lumina_avg", "pure_avg", "diff"))
    total += check(keys_ok, "JSON structure (object with lumina_avg, pure_avg, diff)", 20, 20, details)

    # 3. numeric correctness (70 pts)
    expected_lumina = 30.5
    expected_pure = 27.0
    expected_diff = 3.5

    # Use tolerance for floating point
    eps = 0.01

    lumina_ok = keys_ok and isinstance(data.get("lumina_avg"), (int, float)) and abs(data["lumina_avg"] - expected_lumina) < eps
    total += check(lumina_ok, "lumina_avg = 30.5", 25, 25, details)

    pure_ok = keys_ok and isinstance(data.get("pure_avg"), (int, float)) and abs(data["pure_avg"] - expected_pure) < eps
    total += check(pure_ok, "pure_avg = 27.0", 25, 25, details)

    diff_ok = keys_ok and isinstance(data.get("diff"), (int, float)) and abs(data["diff"] - expected_diff) < eps
    total += check(diff_ok, "diff = 3.5", 20, 20, details)

    # Write final score
    result = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total}/100")

if __name__ == "__main__":
    main()
