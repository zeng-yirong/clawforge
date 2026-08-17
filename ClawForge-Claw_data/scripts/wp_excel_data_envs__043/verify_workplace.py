import sys
import os
import json
import csv
import math

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    score = 0
    max_score = 100
    details = []

    # 1. Check that ops/channel_avg.json exists (10 points)
    path_result = os.path.join(WORKSPACE, "ops", "channel_avg.json")
    if os.path.isfile(path_result):
        details.append({"item": "Result file exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/channel_avg.json found"})
        score += 10
    else:
        details.append({"item": "Result file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/channel_avg.json not found"})
        # Can't proceed if missing
        final_score = 0
        write_score(final_score, details)
        return

    # 2. Validate JSON format and structure (10 points)
    try:
        data = load_json(path_result)
        if "channel_avg" in data and isinstance(data["channel_avg"], dict):
            details.append({"item": "Valid JSON structure", "score": 10, "max_score": 10, "passed": True, "reason": "channel_avg key exists and is a dict"})
            score += 10
        else:
            details.append({"item": "Valid JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "Missing channel_avg key or not a dict"})
            # Still continue to collect partial score
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "Valid JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": f"Cannot parse JSON: {e}"})
        write_score(score, details)
        return

    # 3. Compute expected averages from the clean data
    # We need to load the raw data to recompute what the agent should have produced.
    # But we can also just hardcode expected values because env_builder creates deterministic data.
    # However, to be robust, let's read the v2 file and apply cleaning rules.
    # This also verifies the agent used the correct source.
    raw_path = os.path.join(WORKSPACE, "data", "raw_sales", "sales_v2.csv")
    if not os.path.isfile(raw_path):
        details.append({"item": "Source data exists", "score": 0, "max_score": 5, "passed": False, "reason": "sales_v2.csv not found"})
        # Continue, use hardcoded as fallback
        expected = {"Online": 1025.0, "In-Store": 1862.5, "Wholesale": 377.5}
    else:
        # Parse and clean
        rows = []
        with open(raw_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validate transaction_id format: TXN- followed by 6 digits
                txn = row.get("transaction_id", "")
                if not (txn.startswith("TXN-") and len(txn) == 10 and txn[4:].isdigit()):
                    continue
                # Check sales_amount and quantity are numeric and non-empty
                amt_str = row.get("sales_amount", "").strip()
                qty_str = row.get("quantity", "").strip()
                try:
                    amt = float(amt_str)
                except (ValueError, TypeError):
                    continue
                try:
                    qty = int(qty_str)
                except (ValueError, TypeError):
                    continue
                if amt_str == "" or qty_str == "":
                    continue
                rows.append(row)
        # Deduplicate based on transaction_id (keep first occurrence)
        seen = set()
        unique_rows = []
        for row in rows:
            tid = row["transaction_id"]
            if tid not in seen:
                seen.add(tid)
                unique_rows.append(row)
        # Compute average per channel
        channel_amounts = {}
        for row in unique_rows:
            ch = row["channel"]
            amt = float(row["sales_amount"])
            channel_amounts.setdefault(ch, []).append(amt)
        expected = {}
        for ch, amts in channel_amounts.items():
            avg = sum(amts) / len(amts)
            expected[ch] = round(avg, 2)
    
    # Compare with agent output
    agent_avgs = data["channel_avg"]
    # Check that agent has exactly the same channels
    expected_channels = set(expected.keys())
    agent_channels = set(agent_avgs.keys())
    if expected_channels != agent_channels:
        details.append({"item": "Channel set correctness", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected channels {expected_channels}, got {agent_channels}"})
        # Still check individual channels for partial credit
    else:
        details.append({"item": "Channel set correctness", "score": 20, "max_score": 20, "passed": True, "reason": "All channels present"})
        score += 20

    # For each channel, compare values (10 points each, total 30 if 3 channels, scale accordingly)
    # We have 3 channels: Online, In-Store, Wholesale
    channel_score = 0
    channel_max = 30  # 10 each
    for ch in expected:
        exp_val = expected[ch]
        if ch in agent_avgs:
            agent_val = agent_avgs[ch]
            # Allow small floating point tolerance (0.01)
            if abs(agent_val - exp_val) <= 0.01:
                channel_score += 10
                details.append({"item": f"Average for {ch}", "score": 10, "max_score": 10, "passed": True, "reason": f"Expected {exp_val}, got {agent_val}"})
            else:
                details.append({"item": f"Average for {ch}", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {exp_val}, got {agent_val}"})
        else:
            details.append({"item": f"Average for {ch}", "score": 0, "max_score": 10, "passed": False, "reason": f"Channel {ch} missing"})
    score += channel_score

    # 4. Check that agent did not include any extra channels (penalty? but we already checked set match)
    # If set didn't match, we already gave 0 for channel set; still allow partial for values that are correct.
    # We'll add a note.

    # 5. Check that agent rounded correctly (2 decimal places) - optional extra point
    all_rounded = True
    for ch, val in agent_avgs.items():
        if round(val, 2) != val:
            all_rounded = False
            break
    if all_rounded:
        details.append({"item": "Values rounded to 2 decimals", "score": 5, "max_score": 5, "passed": True, "reason": "All values have at most 2 decimal places"})
        score += 5
    else:
        details.append({"item": "Values rounded to 2 decimals", "score": 0, "max_score": 5, "passed": False, "reason": "Some values have more than 2 decimal places"})

    # 6. Verify that the agent removed duplicates and cleaned bad rows (we can indirectly check via expected values)
    # Already covered by expected values comparison.

    # Calculate final score
    final_score = min(100, score)
    write_score(final_score, details)

def write_score(total, details):
    os.makedirs(os.path.dirname(os.path.join(WORKSPACE, "workplace_score.json")), exist_ok=True)
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
