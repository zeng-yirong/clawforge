import json
import os
import sys
import math

def score_item(details, item, score, max_score, passed, reason):
    details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

def verify(workspace):
    details = []
    total = 0

    # 1. Directory structure: ops/ exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_item(details, "ops directory exists", 10, 10, True, "ops/ directory found")
        total += 10
    else:
        score_item(details, "ops directory exists", 0, 10, False, "ops/ directory not found")

    # 2. File existence: ops/competitor_report.json (10 points)
    report_path = os.path.join(ops_dir, "competitor_report.json")
    if os.path.isfile(report_path):
        score_item(details, "competitor_report.json exists", 10, 10, True, "File found")
        total += 10
    else:
        score_item(details, "competitor_report.json exists", 0, 10, False, "File not found")
        # cannot continue without file
        final_score = total
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        return

    # 3. JSON validity (10 points)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        score_item(details, "JSON is valid", 10, 10, True, "Parsed successfully")
        total += 10
    except Exception as e:
        score_item(details, "JSON is valid", 0, 10, False, f"Invalid JSON: {e}")
        final_score = total
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        return

    # 4. Required fields in report (20 points)
    # Must contain: brand, skus (list), avg_price (number)
    brand_ok = isinstance(data.get("brand"), str) and data["brand"] == "LuminaSkin"
    skus_ok = isinstance(data.get("skus"), list) and len(data["skus"]) > 0
    avg_price_ok = "avg_price" in data and isinstance(data["avg_price"], (int, float))
    if brand_ok and skus_ok and avg_price_ok:
        score_item(details, "Required fields present (brand, skus, avg_price)", 20, 20, True, "All required fields found with correct types")
        total += 20
    else:
        missing = []
        if not brand_ok:
            missing.append("brand (should be 'LuminaSkin')")
        if not skus_ok:
            missing.append("skus (non-empty list)")
        if not avg_price_ok:
            missing.append("avg_price (number)")
        score_item(details, "Required fields present (brand, skus, avg_price)", 0, 20, False,
                   f"Missing or wrong: {', '.join(missing)}")
        # partial credit could be given but for simplicity full 0 here

    # 5. SKU list correctness (50 points)
    # We need to compute expected output from builder data
    # Build reference: only LuminaSkin, active SKUs, from current price book
    # Active LuminaSkin SKU IDs: SKU-LUM-001, SKU-LUM-002, SKU-LUM-003
    # Prices from live price book: 29.99, 39.99, 24.99
    expected_sku_ids = {"SKU-LUM-001", "SKU-LUM-002", "SKU-LUM-003"}
    expected_prices = {
        "SKU-LUM-001": 29.99,
        "SKU-LUM-002": 39.99,
        "SKU-LUM-003": 24.99
    }
    expected_avg = round((29.99 + 39.99 + 24.99) / 3, 2)  # 31.656666... -> 31.66
    # Allow small tolerance (0.01) for floating point rounding
    expected_avg_exact = 94.97 / 3  # ≈31.6566667

    # Check each SKU in report
    reported_skus = data.get("skus", [])
    errors = []
    points_per_sku = 10  # 3 correct SKUs * 10 = 30, plus avg 20 => 50 total
    sku_ok_count = 0
    for sku_entry in reported_skus:
        if not isinstance(sku_entry, dict):
            errors.append("SKU entry is not a dict")
            continue
        sku_id = sku_entry.get("sku_id")
        if sku_id not in expected_sku_ids:
            errors.append(f"Unexpected SKU ID '{sku_id}' included")
            continue
        # Check price
        price = sku_entry.get("retail_price")
        if price is None or not isinstance(price, (int, float)):
            errors.append(f"SKU {sku_id} missing or invalid price")
            continue
        expected_price = expected_prices[sku_id]
        if abs(price - expected_price) > 0.001:
            errors.append(f"SKU {sku_id} price {price} != expected {expected_price}")
            continue
        # Check that brand_name is present (optional but good)
        sku_ok_count += 1

    # Check all expected SKUs are present
    reported_ids = {s.get("sku_id") for s in reported_skus if isinstance(s, dict)}
    missing_ids = expected_sku_ids - reported_ids
    if missing_ids:
        errors.append(f"Missing SKUs: {missing_ids}")

    # Score for SKU correctness: 30 points divided among correctness of each SKU
    # For simplicity, if no errors, give full 30; otherwise deduct
    if not errors and sku_ok_count == 3:
        score_item(details, "SKU list correct (all 3 active LuminaSkin SKUs with correct prices)", 30, 30, True, "All SKUs match expected")
        total += 30
    else:
        # partial: each correctly present+price = 7 points, plus bonus for no extra
        points = 0
        for sku_id in expected_sku_ids:
            if sku_id in reported_ids:
                # check price
                entry = next((s for s in reported_skus if isinstance(s, dict) and s.get("sku_id") == sku_id), None)
                if entry and abs(entry.get("retail_price", 0) - expected_prices[sku_id]) < 0.001:
                    points += 7
        # round down to nearest 5
        points = min(points, 30)
        score_item(details, "SKU list partial correctness", points, 30, points >= 25,
                   f"Errors: {'; '.join(errors)}")
        total += points

    # 6. Average price correctness (20 points)
    avg = data.get("avg_price")
    # Use relative tolerance 0.01 for floating point
    if avg is not None:
        if abs(avg - expected_avg_exact) <= 0.01:
            score_item(details, "Average price correct (within 0.01)", 20, 20, True,
                       f"avg_price={avg}, expected≈{round(expected_avg_exact,2)}")
            total += 20
        else:
            score_item(details, "Average price correct (within 0.01)", 0, 20, False,
                       f"avg_price={avg}, expected={round(expected_avg_exact,2)}")
    else:
        score_item(details, "Average price correct (within 0.01)", 0, 20, False, "avg_price missing")

    # Final score
    final_score = total
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
