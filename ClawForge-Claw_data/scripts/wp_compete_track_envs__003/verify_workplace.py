import sys
import os
import json
import math

def verify(workspace):
    details = []
    total_score = 0

    # ── Helper to add score item ────────────────────────────────
    def add_item(name, score, max_score, reason):
        nonlocal total_score
        total_score += score
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": score == max_score,
            "reason": reason
        })

    # ── 1. Directory existence (5 pts) ─────────────────────────
    reports_dir = os.path.join(workspace, "data", "reports")
    dir_exists = os.path.isdir(reports_dir)
    add_item("data/reports/ directory exists",
             5 if dir_exists else 0, 5,
             "found" if dir_exists else "not found")

    # ── 2. Output file existence (10 pts) ────────────────────
    output_path = os.path.join(reports_dir, "avg_market_cap_affected.json")
    file_exists = os.path.isfile(output_path)
    add_item("Output file avg_market_cap_affected.json exists",
             10 if file_exists else 0, 10,
             "found" if file_exists else "not found")

    if not file_exists:
        # Can't proceed further
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f)
        return

    # ── 3. JSON parseable (10 pts) ────────────────────────────
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        parse_ok = True
        add_item("Output file is valid JSON", 10, 10, "parsed successfully")
    except Exception as e:
        parse_ok = False
        add_item("Output file is valid JSON", 0, 10, f"parse error: {e}")
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f)
        return

    # ── 4. Required keys present (15 pts) ─────────────────────
    required_keys = ["policy_id", "affected_competitors", "avg_market_cap", "count"]
    missing = [k for k in required_keys if k not in data]
    if not missing:
        add_item("All required keys present", 15, 15, "keys: " + ", ".join(required_keys))
    else:
        add_item("All required keys present", 0, 15, f"missing keys: {missing}")
        # Continue scoring other fields if possible

    # ── 5. policy_id exactly correct (15 pts) ─────────────────
    expected_policy_id = "US_AI_Transparency_Act_2025"
    policy_ok = data.get("policy_id") == expected_policy_id
    add_item("policy_id is correct",
             15 if policy_ok else 0, 15,
             f"expected '{expected_policy_id}', got '{data.get('policy_id')}'")

    # ── 6. affected_competitors list (20 pts) ─────────────────
    expected_competitors = {"CloudMajor", "DataFlow AI"}
    actual_set = set(data.get("affected_competitors", []))
    if actual_set == expected_competitors:
        add_item("affected_competitors list matches expected set", 20, 20,
                 f"found {actual_set}")
    else:
        extra = actual_set - expected_competitors
        missing = expected_competitors - actual_set
        reason = (f"extra: {extra}, missing: {missing}" if extra or missing
                  else "content mismatch")
        add_item("affected_competitors list matches expected set", 0, 20, reason)

    # ── 7. avg_market_cap exact value (25 pts) ───────────────
    # Expected avg = (800000 + 1200000) / 2 = 1000000
    expected_avg = 1000000.0
    actual_avg = data.get("avg_market_cap")
    if isinstance(actual_avg, (int, float)):
        # Allow small floating rounding differences
        if abs(actual_avg - expected_avg) < 1e-9:
            add_item("avg_market_cap exact value", 25, 25,
                     f"value is {actual_avg}")
        else:
            add_item("avg_market_cap exact value", 0, 25,
                     f"expected {expected_avg}, got {actual_avg}")
    else:
        add_item("avg_market_cap exact value", 0, 25,
                 f"avg_market_cap is not a number: {type(actual_avg)}")

    # ── 8. count correct (10 pts) ────────────────────────────
    expected_count = 2
    actual_count = data.get("count")
    if actual_count == expected_count:
        add_item("count is correct", 10, 10,
                 f"value is {actual_count}")
    else:
        add_item("count is correct", 0, 10,
                 f"expected {expected_count}, got {actual_count}")

    # ── Final score ───────────────────────────────────────────
    final_score = min(total_score, 100)  # cap at 100
    output = {
        "total_score": final_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
