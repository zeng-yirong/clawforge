import sys
import json
import os
import math

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. Check ops directory and file existence
    ops_dir = os.path.join(workspace, "ops")
    file_path = os.path.join(ops_dir, "price_gaps.json")
    if os.path.isfile(file_path):
        details.append({"item": "Output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/price_gaps.json found"})
        total_score += 10
    else:
        details.append({"item": "Output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/price_gaps.json not found"})
        # early exit? still try to parse other checks but will fail later
        # We'll continue but most checks will fail due to missing data
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. Parse JSON and check structure
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    if not isinstance(data, dict) or "price_gaps" not in data:
        details.append({"item": "Valid JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'price_gaps' key or not an object"})
        details.append({"item": "Contents correctness", "score": 0, "max_score": 20, "passed": False, "reason": "Skipped due to structure failure"})
        details.append({"item": "Price gap calculation accuracy", "score": 0, "max_score": 60, "passed": False, "reason": "Skipped due to structure failure"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    gaps = data["price_gaps"]
    if not isinstance(gaps, list):
        details.append({"item": "Valid JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "'price_gaps' is not a list"})
        details.append({"item": "Contents correctness", "score": 0, "max_score": 20, "passed": False, "reason": "Skipped due to structure failure"})
        details.append({"item": "Price gap calculation accuracy", "score": 0, "max_score": 60, "passed": False, "reason": "Skipped due to structure failure"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    total_score += 10
    details.append({"item": "Valid JSON structure", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON with 'price_gaps' list"})

    # 3. Compute expected result from the env data
    # Load skus
    skus_path = os.path.join(workspace, "data/skus/skus.json")
    with open(skus_path, "r") as f:
        skus_data = json.load(f)
    skus_list = skus_data["skus"]

    # Load price books
    pb_path = os.path.join(workspace, "data/pricing/price_books.json")
    with open(pb_path, "r") as f:
        pb_data = json.load(f)
    pbs = pb_data["price_books"]

    # Find live price book
    live_pb = None
    for pb in pbs:
        if pb["is_current"]:
            live_pb = pb
            break
    if not live_pb:
        details.append({"item": "Contents correctness", "score": 0, "max_score": 20, "passed": False, "reason": "No live price book found in env data"})
        details.append({"item": "Price gap calculation accuracy", "score": 0, "max_score": 60, "passed": False, "reason": "Skipped"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # Build price lookup
    price_map = {}
    for entry in live_pb["entries"]:
        price_map[entry["sku_id"]] = entry["price"]

    # Define target category and competitor brands (non-LuminaSkin)
    target_category = "Hydration Serum"
    target_brand = "LuminaSkin"
    competitor_brands = {"AquaPulse", "DermVeil"}

    # Get competitor active SKU prices
    comp_prices = []
    for sku in skus_list:
        if (sku["category_name"] == target_category and
            sku["brand_name"] in competitor_brands and
            sku["status"] == "active" and
            sku["sku_id"] in price_map):
            comp_prices.append(price_map[sku["sku_id"]])

    if not comp_prices:
        # edge case
        avg_comp_price = 0.0
    else:
        avg_comp_price = sum(comp_prices) / len(comp_prices)

    # Compute expected gaps for LuminaSkin active Hydration Serum
    expected_gaps = []
    for sku in skus_list:
        if (sku["category_name"] == target_category and
            sku["brand_name"] == target_brand and
            sku["status"] == "active" and
            sku["sku_id"] in price_map):
            lum_price = price_map[sku["sku_id"]]
            gap = (lum_price - avg_comp_price) / avg_comp_price if avg_comp_price != 0 else 0.0
            if gap > 0.2:  # >20% higher
                expected_gaps.append({"sku_id": sku["sku_id"], "price_gap_percent": round(gap, 4)})

    # 4. Compare with agent output (order-insensitive, only compare sku_ids and rounded percents)
    # Map agent output by sku_id
    agent_map = {item["sku_id"]: item.get("price_gap_percent") for item in gaps if isinstance(item, dict) and "sku_id" in item}
    expected_map = {item["sku_id"]: item["price_gap_percent"] for item in expected_gaps}

    # Check for extra or missing skus
    agent_sku_set = set(agent_map.keys())
    expected_sku_set = set(expected_map.keys())
    extra = agent_sku_set - expected_sku_set
    missing = expected_sku_set - agent_sku_set

    content_score = 20
    content_passed = True
    content_reason = ""
    if extra:
        content_passed = False
        content_reason += f"Extra SKUs not expected: {extra}. "
        content_score = 0
    if missing:
        content_passed = False
        content_reason += f"Missing SKUs: {missing}. "
        content_score = 0
    # If both sets match, check values
    if content_passed:
        all_match = True
        for sku_id, expected_gap in expected_map.items():
            actual_gap = agent_map.get(sku_id)
            if actual_gap is None or abs(actual_gap - expected_gap) > 0.001:
                all_match = False
                content_reason += f"SKU {sku_id}: expected gap {expected_gap:.4f}, got {actual_gap}. "
                content_score = 0
                break
        if all_match:
            content_reason = "All SKUs match expected IDs and gap values."
    details.append({"item": "Contents correctness", "score": content_score, "max_score": 20, "passed": content_passed, "reason": content_reason})
    total_score += content_score

    # 5. Price gap calculation accuracy (60 points, split equally among expected skus, or 0 if any wrong)
    calc_score = 0
    calc_passed = False
    calc_reason = ""
    if content_passed and len(expected_gaps) > 0:
        # All correct already verified in content_score; but we can give full points if content was entirely correct
        calc_score = 60
        calc_passed = True
        calc_reason = "All calculated gaps are accurate."
    elif content_passed and len(expected_gaps) == 0:
        # No gaps expected but agent might have output empty list
        if len(gaps) == 0:
            calc_score = 60
            calc_passed = True
            calc_reason = "No LuminaSkin SKUs exceed 20% threshold, empty output is correct."
        else:
            calc_score = 0
            calc_passed = False
            calc_reason = "Expected no gaps, but agent output non-empty list."
    else:
        calc_score = 0
        calc_passed = False
        calc_reason = "Content correctness failed, calculation not verified."
    details.append({"item": "Price gap calculation accuracy", "score": calc_score, "max_score": 60, "passed": calc_passed, "reason": calc_reason})
    total_score += calc_score

    total_score = min(total_score, 100)  # cap at 100
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
