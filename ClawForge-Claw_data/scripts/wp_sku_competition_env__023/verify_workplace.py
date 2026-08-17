import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check that reports directory exists
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        score_details.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "reports/ found"})
        total_score += 10
    else:
        score_details.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/ not found"})
        # cannot continue without the directory
        _write_score({"total_score": total_score, "details": score_details}, workspace)
        return

    # 2. Check competition_analysis.json exists and is valid JSON
    json_path = os.path.join(reports_dir, "competition_analysis.json")
    if not os.path.isfile(json_path):
        score_details.append({"item": "competition_analysis.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        _write_score({"total_score": total_score, "details": score_details}, workspace)
        return

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "file is valid JSON"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {str(e)}"})
        _write_score({"total_score": total_score, "details": score_details}, workspace)
        return

    # 3. Check that the JSON has a top-level key that is an array of brands (allow flexibility: "brands" or results)
    # We'll accept "brands" or "report" containing "brands". Look for a list of dicts with "brand_name"
    brands_list = None
    if isinstance(data, dict):
        if "brands" in data and isinstance(data["brands"], list):
            brands_list = data["brands"]
        elif "report" in data and isinstance(data["report"], dict) and "brands" in data["report"]:
            brands_list = data["report"]["brands"]
        else:
            # try to find any list that contains items with "brand_name"
            for v in data.values():
                if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict) and "brand_name" in v[0]:
                    brands_list = v
                    break

    if brands_list is None:
        score_details.append({"item": "brands list found", "score": 0, "max_score": 20, "passed": False, "reason": "No array of brand objects with 'brand_name' found"})
        _write_score({"total_score": total_score, "details": score_details}, workspace)
        return
    else:
        score_details.append({"item": "brands list found", "score": 20, "max_score": 20, "passed": True, "reason": f"Found {len(brands_list)} brand entries"})
        total_score += 20

    # 4. Verify each brand’s SKU list
    # Expected brands: AquaPulse, DermVeil, LuminaSkin (ordered alphabetically by brand_name)
    # Expected SKUs per brand (order within brand by sku_id):
    #   AquaPulse: AP-001 (29.99), AP-002 (34.99)
    #   DermVeil: DV-001 (44.99)
    #   LuminaSkin: LS-001 (39.99), LS-002 (54.99)
    # Additionally, ensure no SKU from wrong category (e.g., PL-001) or inactive (DV-002, SO-001) appear.

    expected_brands = {
        "AquaPulse": {
            "skus": [
                {"sku_id": "AP-001", "list_price": 29.99, "sku_name": "Aqua Burst", "selling_points": ["Instant moisture burst", "Lightweight"], "ingredients": ["Water Lily Extract", "Glycerin"]},
                {"sku_id": "AP-002", "list_price": 34.99, "sku_name": "Ocean Dew", "selling_points": ["Deep ocean minerals", "pH balanced"], "ingredients": ["Sea Salt", "Algae Extract"]}
            ]
        },
        "DermVeil": {
            "skus": [
                {"sku_id": "DV-001", "list_price": 44.99, "sku_name": "Veil Hydrator", "selling_points": ["Barrier support", "Soothing"], "ingredients": ["Ceramides", "Panthenol"]}
            ]
        },
        "LuminaSkin": {
            "skus": [
                {"sku_id": "LS-001", "list_price": 39.99, "sku_name": "HydraBoost Serum", "selling_points": ["Intense hydration", "Fast absorption"], "ingredients": ["Hyaluronic Acid", "Vitamin B5"]},
                {"sku_id": "LS-002", "list_price": 54.99, "sku_name": "Glow Elixir", "selling_points": ["Brightening", "Anti-aging"], "ingredients": ["Niacinamide", "Peptides"]}
            ]
        }
    }

    brand_score = 0
    brand_max = 40
    # Flatten all expected SKU IDs for quick lookup
    all_expected_sku_ids = set()
    for b_expected in expected_brands.values():
        for s in b_expected["skus"]:
            all_expected_sku_ids.add(s["sku_id"])

    # Check that no unwanted SKU appears
    unwanted_found = []
    # Extract brand_name->skus mapping from agent output
    output_brands = {}
    for b in brands_list:
        bname = b.get("brand_name")
        skus_list = b.get("skus", [])
        if bname:
            output_brands[bname] = skus_list

    # Check each expected brand
    for bname, b_exp in expected_brands.items():
        if bname not in output_brands:
            brand_score -= 5  # missing brand penalty
            unwanted_found.append(f"Missing brand {bname}")
            continue
        agent_skus = output_brands[bname]
        # Expect same number of SKUs
        if len(agent_skus) != len(b_exp["skus"]):
            brand_score -= 3
            unwanted_found.append(f"{bname}: expected {len(b_exp['skus'])} SKUs, got {len(agent_skus)}")
        # Check each expected SKU in order
        for i, exp_sku in enumerate(b_exp["skus"]):
            if i >= len(agent_skus):
                brand_score -= 2
                unwanted_found.append(f"{bname}: missing SKU {exp_sku['sku_id']}")
                continue
            agent_sku = agent_skus[i]
            # Check sku_id
            if agent_sku.get("sku_id") != exp_sku["sku_id"]:
                brand_score -= 2
                unwanted_found.append(f"{bname}: expected SKU id {exp_sku['sku_id']}, got {agent_sku.get('sku_id')}")
            # Check list_price (allow small floating error)
            agent_price = agent_sku.get("list_price")
            if agent_price is None or not isinstance(agent_price, (int, float)):
                brand_score -= 2
                unwanted_found.append(f"{bname}: {exp_sku['sku_id']} list_price missing or not numeric")
            elif abs(float(agent_price) - exp_sku["list_price"]) > 0.01:
                brand_score -= 2
                unwanted_found.append(f"{bname}: {exp_sku['sku_id']} list_price expected {exp_sku['list_price']}, got {agent_price}")
            # Check sku_name (optional but good)
            if agent_sku.get("sku_name") != exp_sku["sku_name"]:
                brand_score -= 1
                unwanted_found.append(f"{bname}: {exp_sku['sku_id']} sku_name mismatch")
            # Check selling_points (as list, order sensitive)
            if agent_sku.get("selling_points") != exp_sku["selling_points"]:
                brand_score -= 2
                unwanted_found.append(f"{bname}: {exp_sku['sku_id']} selling_points mismatch")
            # Check ingredients (as list)
            if agent_sku.get("ingredients") != exp_sku["ingredients"]:
                brand_score -= 2
                unwanted_found.append(f"{bname}: {exp_sku['sku_id']} ingredients mismatch")

    # Check for extra brands (should be only the three)
    extra_brands = [b for b in output_brands if b not in expected_brands]
    if extra_brands:
        for b in extra_brands:
            brand_score -= 5
            unwanted_found.append(f"Extra brand {b} (should not appear)")

    # Check that no unwanted SKU IDs appear anywhere
    all_agent_sku_ids = set()
    for b_skus in output_brands.values():
        for s in b_skus:
            all_agent_sku_ids.add(s.get("sku_id"))
    unwanted_ids = all_agent_sku_ids - all_expected_sku_ids
    if unwanted_ids:
        for uid in unwanted_ids:
            brand_score -= 2
            unwanted_found.append(f"Unwanted SKU {uid} present")

    # Clamp brand_score between 0 and brand_max
    brand_score = max(0, brand_score)
    score_details.append({"item": "SKU correctness and exclusion of noise", "score": brand_score, "max_score": brand_max, "passed": brand_score == brand_max, "reason": "; ".join(unwanted_found) if unwanted_found else "All SKUs match expectations"})
    total_score += brand_score

    # 5. Optional: Check that total_active_skus or summary field exists, but not required for full points
    # (We'll add a small extra check for bonus, but not deduct)
    summary_fields = ["total_skus", "total_active_skus", "summary"]
    has_summary = any(k in data for k in summary_fields) or (isinstance(data.get("report"), dict) and any(k in data["report"] for k in summary_fields))
    if has_summary:
        score_details.append({"item": "summary field present", "score": 5, "max_score": 5, "passed": True, "reason": "Found summary information"})
        total_score += 5
    else:
        score_details.append({"item": "summary field present", "score": 0, "max_score": 5, "passed": False, "reason": "No summary field found (optional, not penalized)"})
        # Not mandatory, so we don't add penalty

    # Write final score
    final_score = min(100, total_score)
    _write_score({"total_score": final_score, "details": score_details}, workspace)

def _write_score(result, workspace):
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
