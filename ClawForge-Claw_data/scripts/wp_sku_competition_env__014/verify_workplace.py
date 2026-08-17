import json, os, sys, math

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def verify(workspace):
    details = []
    total_score = 0

    # 1. Check output file exists
    report_path = os.path.join(workspace, "ops", "lumina_uv_report.json")
    if os.path.isfile(report_path):
        details.append({"item": "Output file exists", "score": 10, "max_score": 10,
                        "passed": True, "reason": "ops/lumina_uv_report.json found"})
        total_score += 10
    else:
        details.append({"item": "Output file exists", "score": 0, "max_score": 10,
                        "passed": False, "reason": "File ops/lumina_uv_report.json not found"})
        # cannot proceed with further checks
        write_score(details, total_score, workspace)
        return

    # 2. Load and validate JSON
    try:
        report = load_json(report_path)
        details.append({"item": "Valid JSON", "score": 10, "max_score": 10,
                        "passed": True, "reason": "File parses as valid JSON"})
        total_score += 10
    except Exception as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10,
                        "passed": False, "reason": f"JSON parse error: {e}"})
        write_score(details, total_score, workspace)
        return

    # 3. Required top-level fields
    required_fields = ["brand_name", "category_name", "price_book_version", "skus"]
    missing = [f for f in required_fields if f not in report]
    if not missing:
        details.append({"item": "Top-level fields present", "score": 10, "max_score": 10,
                        "passed": True, "reason": "All required fields present"})
        total_score += 10
    else:
        details.append({"item": "Top-level fields present", "score": 0, "max_score": 10,
                        "passed": False, "reason": f"Missing fields: {missing}"})
        # still try to check partial

    # 4. brand_name
    if report.get("brand_name") == "LuminaSkin":
        details.append({"item": "brand_name correct", "score": 5, "max_score": 5,
                        "passed": True, "reason": "Matches LuminaSkin"})
        total_score += 5
    else:
        details.append({"item": "brand_name correct", "score": 0, "max_score": 5,
                        "passed": False, "reason": f"Got '{report.get('brand_name')}', expected 'LuminaSkin'"})

    # 5. category_name
    if report.get("category_name") == "UV Moisturizer":
        details.append({"item": "category_name correct", "score": 5, "max_score": 5,
                        "passed": True, "reason": "Matches UV Moisturizer"})
        total_score += 5
    else:
        details.append({"item": "category_name correct", "score": 0, "max_score": 5,
                        "passed": False, "reason": f"Got '{report.get('category_name')}', expected 'UV Moisturizer'"})

    # 6. price_book_version
    if report.get("price_book_version") == "APAC-Q2-2026-LIVE":
        details.append({"item": "price_book_version correct", "score": 5, "max_score": 5,
                        "passed": True, "reason": "Matches APAC-Q2-2026-LIVE"})
        total_score += 5
    else:
        details.append({"item": "price_book_version correct", "score": 0, "max_score": 5,
                        "passed": False, "reason": f"Got '{report.get('price_book_version')}', expected 'APAC-Q2-2026-LIVE'"})

    # 7. Build expected SKU list from raw data
    # load raw data
    brands = load_json(os.path.join(workspace, "data", "brands", "brands.json"))
    skus = load_json(os.path.join(workspace, "data", "skus", "skus.json"))
    price_books = load_json(os.path.join(workspace, "data", "pricing", "price_books.json"))

    # find LuminaSkin brand_id
    lumina = next((b for b in brands if b["brand_name"] == "LuminaSkin"), None)
    if not lumina:
        details.append({"item": "Data integrity", "score": 0, "max_score": 0,
                        "passed": False, "reason": "LuminaSkin brand not found in source data"})
        write_score(details, total_score, workspace)
        return

    # find current live price book
    live_pb = next((pb for pb in price_books if pb["is_current"] == True), None)
    if not live_pb:
        details.append({"item": "Data integrity", "score": 0, "max_score": 0,
                        "passed": False, "reason": "Current price book not found"})
        write_score(details, total_score, workspace)
        return

    # price lookup
    price_map = {e["sku_id"]: e["price"] for e in live_pb["entries"]}

    # filter expected SKUs: brand LuminaSkin, category UV Moisturizer
    expected_skus = [s for s in skus
                     if s["brand_id"] == lumina["brand_id"]
                     and s["category_name"] == "UV Moisturizer"]
    expected_sku_ids = {s["sku_id"] for s in expected_skus}

    # 8. skus list length
    agent_skus = report.get("skus", [])
    if isinstance(agent_skus, list) and len(agent_skus) == len(expected_skus):
        details.append({"item": "SKU list length correct", "score": 10, "max_score": 10,
                        "passed": True, "reason": f"Contains {len(expected_skus)} SKUs"})
        total_score += 10
    else:
        details.append({"item": "SKU list length correct", "score": 0, "max_score": 10,
                        "passed": False, "reason": f"Expected {len(expected_skus)} SKUs, got {len(agent_skus) if isinstance(agent_skus, list) else 'not a list'}"})

    # 9. Check each expected SKU in agent output
    sku_field_score = 0
    sku_price_score = 0
    sku_details_score = 0
    max_sku_field = 10
    max_sku_price = 20
    max_sku_details = 10

    # Build agent SKU lookup by sku_id
    agent_sku_map = {}
    if isinstance(agent_skus, list):
        for s in agent_skus:
            if isinstance(s, dict) and "sku_id" in s:
                agent_sku_map[s["sku_id"]] = s

    # Check for extra SKUs (should not exist)
    extra_sku_ids = [sid for sid in agent_sku_map if sid not in expected_sku_ids]
    if extra_sku_ids:
        # penalise: remove 5 points from total (we'll incorporate in one of the items)
        pass  # handled separately

    # For each expected SKU, check required fields, price, ingredients, selling_points
    sku_field_ok = True
    sku_price_ok = True
    sku_details_ok = True
    for exp in expected_skus:
        sid = exp["sku_id"]
        agent_s = agent_sku_map.get(sid)
        if not agent_s:
            sku_field_ok = False
            continue
        # required sub-fields
        sub_req = ["sku_id", "sku_name", "current_price", "selling_points", "ingredients"]
        if not all(f in agent_s for f in sub_req):
            sku_field_ok = False
        # price check
        expected_price = price_map.get(sid)
        if expected_price is not None and agent_s.get("current_price") != expected_price:
            sku_price_ok = False
        # selling_points and ingredients check (order insensitive)
        exp_sp_set = set(exp["selling_points"])
        agent_sp_set = set(agent_s.get("selling_points", []))
        exp_ing_set = set(exp["ingredients"])
        agent_ing_set = set(agent_s.get("ingredients", []))
        if exp_sp_set != agent_sp_set or exp_ing_set != agent_ing_set:
            sku_details_ok = False

    # field completeness for all expected SKUs
    if sku_field_ok and len(expected_skus) > 0:
        sku_field_score = max_sku_field
        details.append({"item": "SKU fields completeness", "score": max_sku_field, "max_score": max_sku_field,
                        "passed": True, "reason": "All expected SKUs contain required sub-fields"})
    else:
        details.append({"item": "SKU fields completeness", "score": 0, "max_score": max_sku_field,
                        "passed": False, "reason": "Some expected SKUs missing required sub-fields (sku_id, sku_name, current_price, selling_points, ingredients)"})
    total_score += sku_field_score

    # price accuracy
    if sku_price_ok and len(expected_skus) > 0:
        sku_price_score = max_sku_price
        details.append({"item": "Current price accuracy", "score": max_sku_price, "max_score": max_sku_price,
                        "passed": True, "reason": "All SKU current_price match the live price book"})
    else:
        details.append({"item": "Current price accuracy", "score": 0, "max_score": max_sku_price,
                        "passed": False, "reason": "One or more SKU prices differ from expected live price"})
    total_score += sku_price_score

    # selling_points and ingredients accuracy
    if sku_details_ok and len(expected_skus) > 0:
        sku_details_score = max_sku_details
        details.append({"item": "Selling points & ingredients accuracy", "score": max_sku_details, "max_score": max_sku_details,
                        "passed": True, "reason": "All SKU attributes match source data"})
    else:
        details.append({"item": "Selling points & ingredients accuracy", "score": 0, "max_score": max_sku_details,
                        "passed": False, "reason": "Some SKU selling points or ingredients differ from expected"})
    total_score += sku_details_score

    # Penalise extra SKUs (non-target)
    if extra_sku_ids:
        penalty = 5
        details.append({"item": "No extra SKUs", "score": 0, "max_score": 5,
                        "passed": False, "reason": f"Found extra SKUs not belonging to LuminaSkin UV Moisturizer: {extra_sku_ids}"})
        # we already accounted this in total? Actually we haven't added any positive score for this item, so just record 0/5
        # We need to add an item with max_score 5 but 0 points
        # Let's adjust: add another detail entry
        # But the schema expects details items; we can just add this as a scored item
        # However we already have max_score sum = 10+10+10+5+5+5+10+10+20+10 = 95? Let's recalc.
        # We have: file exist10, valid json10, top-fields10, brand5, category5, version5, sku count10, sku fields10, price20, details10 = 95
        # Plus we need an extra item for 'no extra skus' worth 5 to make 100. So total max 100.
        # So add this item with max 5.
        # But we already added some items for sku fields/price/details which include checks for correctness; the extra sku penalty is separate.
        # Let's restructure: include 'no extra skus' as a separate item with max 5.
        # However we already inserted 10 items? Let's manually append.
        details.append({"item": "No extra SKUs", "score": 0, "max_score": 5,
                        "passed": False, "reason": f"Found extra SKUs: {extra_sku_ids}"})
        total_score += 0  # no points
    else:
        details.append({"item": "No extra SKUs", "score": 5, "max_score": 5,
                        "passed": True, "reason": "No irrelevant SKUs included"})
        total_score += 5

    # ensure total does not exceed 100
    total_score = min(100, total_score)

    write_score(details, total_score, workspace)

def write_score(details, total_score, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
