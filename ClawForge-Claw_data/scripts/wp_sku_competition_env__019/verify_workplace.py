import json
import os
import sys
from math import isclose

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_expected_comparisons(workspace):
    price_books = load_json(os.path.join(workspace, "data/pricing/price_books.json"))["price_books"]
    skus_data = load_json(os.path.join(workspace, "data/skus/skus.json"))["skus"]
    brands = load_json(os.path.join(workspace, "data/brands/brands.json"))["brands"]

    current_pb = None
    for pb_id, pb in price_books.items():
        if pb["is_current"] and pb["status"] == "approved":
            current_pb = pb
            break
    if not current_pb:
        return None
    entries = {e["sku_id"]: e["price"] for e in current_pb["entries"]}

    lumina_id = None
    derm_id = None
    for bid, b in brands.items():
        if b["brand_name"] == "LuminaSkin":
            lumina_id = bid
        elif b["brand_name"] == "DermVeil":
            derm_id = bid

    lumina_skus = {}
    derm_skus = {}
    for sku_id, sku in skus_data.items():
        if sku["status"] != "active":
            continue
        if sku["category_name"] != "Hydration Serum":
            continue
        if sku["brand_id"] == lumina_id:
            lumina_skus[sku_id] = sku
        elif sku["brand_id"] == derm_id:
            derm_skus[sku_id] = sku

    lumina_by_size = {}
    for sku_id, sku in lumina_skus.items():
        key = (sku["size_value"], sku["size_unit"])
        lumina_by_size[key] = (sku_id, sku)
    derm_by_size = {}
    for sku_id, sku in derm_skus.items():
        key = (sku["size_value"], sku["size_unit"])
        derm_by_size[key] = (sku_id, sku)

    comparisons = []
    for size_key, (lum_sku_id, lum_sku) in sorted(lumina_by_size.items()):
        if size_key in derm_by_size:
            der_sku_id, der_sku = derm_by_size[size_key]
            lum_price = entries.get(lum_sku_id)
            der_price = entries.get(der_sku_id)
            if lum_price is None or der_price is None:
                continue
            diff = round(lum_price - der_price, 2)
            comparisons.append({
                "lumina_sku": lum_sku_id,
                "lumina_price": lum_price,
                "competitor_sku": der_sku_id,
                "competitor_price": der_price,
                "size_ml": size_key[0],
                "price_difference": diff
            })
    return comparisons

def normalize_key(obj, candidates):
    for key in obj:
        key_lower = key.lower().replace(" ", "_").replace("-", "_")
        for cand in candidates:
            if cand.lower() in key_lower:
                return key
    return None

def get_value(obj, candidates):
    key = normalize_key(obj, candidates)
    return obj.get(key) if key else None

def verify_workplace(workspace):
    score = 0
    details = []

    output_path = os.path.join(workspace, "ops/competitive_analysis.json")
    if os.path.exists(output_path):
        details.append({"item": "Output file exists", "score": 5, "max_score": 5, "passed": True, "reason": "File found at ops/competitive_analysis.json"})
        score += 5
    else:
        details.append({"item": "Output file exists", "score": 0, "max_score": 5, "passed": False, "reason": "File not found"})
        write_result(workspace, score, details)
        return score

    try:
        data = load_json(output_path)
        details.append({"item": "JSON valid", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
        score += 5
    except Exception as e:
        details.append({"item": "JSON valid", "score": 0, "max_score": 5, "passed": False, "reason": f"Invalid JSON: {e}"})
        write_result(workspace, score, details)
        return score

    main_list = None
    list_key = None
    for key, value in data.items():
        if isinstance(value, list):
            main_list = value
            list_key = key
            break
    if main_list is None:
        details.append({"item": "Contains a list", "score": 0, "max_score": 10, "passed": False, "reason": "No list found in output JSON"})
    else:
        details.append({"item": "Contains a list", "score": 10, "max_score": 10, "passed": True, "reason": f"Found list under key '{list_key}' with {len(main_list)} entries"})
        score += 10

    expected = get_expected_comparisons(workspace)
    if expected is None:
        details.append({"item": "Expected data derivation", "score": 0, "max_score": 0, "passed": False, "reason": "Failed to derive expected comparisons from source data"})
        write_result(workspace, score, details)
        return score

    expected_count = len(expected)
    if len(main_list) != expected_count:
        details.append({"item": "Comparison count", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_count} comparisons, got {len(main_list)}"})
    else:
        details.append({"item": "Comparison count", "score": 10, "max_score": 10, "passed": True, "reason": f"Correct number of comparisons ({expected_count})"})
        score += 10

    agent_map = {}
    for entry in main_list:
        lum_sku = get_value(entry, ["lumina_sku", "our_sku", "sku", "lumina_sku_id"])
        if lum_sku:
            agent_map[lum_sku] = entry

    required_fields_total = len(main_list) * 5
    required_fields_present = 0
    for entry in main_list:
        if get_value(entry, ["lumina_sku", "our_sku", "sku", "lumina_sku_id"]):
            required_fields_present += 1
        if get_value(entry, ["competitor_sku", "their_sku", "competitor_sku_id"]):
            required_fields_present += 1
        if get_value(entry, ["lumina_price", "our_price"]):
            required_fields_present += 1
        if get_value(entry, ["competitor_price", "their_price"]):
            required_fields_present += 1
        if get_value(entry, ["price_difference", "diff", "difference"]):
            required_fields_present += 1
    fields_score = int(10 * required_fields_present / required_fields_total) if required_fields_total else 0
    details.append({"item": "Required fields present in each entry", "score": fields_score, "max_score": 10, "passed": required_fields_present == required_fields_total, "reason": f"Fields present: {required_fields_present}/{required_fields_total}"})
    score += fields_score

    correct_prices = 0
    correct_diffs = 0
    for exp in expected:
        lum_sku = exp["lumina_sku"]
        if lum_sku not in agent_map:
            continue
        entry = agent_map[lum_sku]
        lum_price = get_value(entry, ["lumina_price", "our_price"])
        comp_price = get_value(entry, ["competitor_price", "their_price"])
        diff = get_value(entry, ["price_difference", "diff", "difference"])

        if lum_price is not None and isclose(lum_price, exp["lumina_price"], abs_tol=0.01):
            correct_prices += 1
        if comp_price is not None and isclose(comp_price, exp["competitor_price"], abs_tol=0.01):
            correct_prices += 1
        if diff is not None and isclose(diff, exp["price_difference"], abs_tol=0.01):
            correct_diffs += 1

    max_correct_prices = expected_count * 2
    price_score = int(15 * correct_prices / max_correct_prices)
    details.append({"item": "Price values accuracy", "score": price_score, "max_score": 15, "passed": correct_prices == max_correct_prices, "reason": f"Correct prices: {correct_prices}/{max_correct_prices}"})
    score += price_score

    diff_score = int(15 * correct_diffs / expected_count)
    details.append({"item": "Price difference accuracy", "score": diff_score, "max_score": 15, "passed": correct_diffs == expected_count, "reason": f"Correct diffs: {correct_diffs}/{expected_count}"})
    score += diff_score

    extra_entries = []
    expected_lumina_skus = {e["lumina_sku"] for e in expected}
    for entry in main_list:
        lum_sku = get_value(entry, ["lumina_sku", "our_sku", "sku"])
        if lum_sku and lum_sku not in expected_lumina_skus:
            extra_entries.append(lum_sku)
    if extra_entries:
        details.append({"item": "No extra entries", "score": 0, "max_score": 10, "passed": False, "reason": f"Found extra entries: {extra_entries}"})
    else:
        details.append({"item": "No extra entries", "score": 10, "max_score": 10, "passed": True, "reason": "No extraneous comparisons"})
        score += 10

    missing_skus = [e["lumina_sku"] for e in expected if e["lumina_sku"] not in agent_map]
    if missing_skus:
        details.append({"item": "All expected SKUs covered", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing SKUs: {missing_skus}"})
    else:
        details.append({"item": "All expected SKUs covered", "score": 5, "max_score": 5, "passed": True, "reason": "All expected SKUs present"})
        score += 5

    write_result(workspace, score, details)
    return score

def write_result(workspace, score, details):
    result = {
        "total_score": min(score, 100),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
