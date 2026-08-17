import sys
import os
import json
import math

def score(workspace):
    details = []
    total = 0
    max_total = 100

    # 1. directory structure check (file exists)
    expected_path = os.path.join(workspace, "ops", "competition_summary.json")
    item = {"item": "ops/competition_summary.json exists", "max_score": 10}
    if os.path.isfile(expected_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "File found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "File not found at ops/competition_summary.json"
        details.append(item)
        # cannot proceed without file
        total += 0
        details.append({"item": "Total", "score": 0, "max_score": max_total, "passed": False, "reason": "File missing"})
        return {"total_score": 0, "details": details}

    total += item["score"]
    details.append(item)

    # 2. parse JSON
    item = {"item": "Valid JSON", "max_score": 10}
    try:
        with open(expected_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Root must be a dict")
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Valid JSON object"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Invalid JSON: {str(e)}"
        pending = [item]
        # no further checks possible
        total2 = total + 0
        details.append(item)
        details.append({"item": "brand field", "score": 0, "max_score": 10, "passed": False, "reason": "Skipped due to JSON error"})
        details.append({"item": "category field", "score": 0, "max_score": 10, "passed": False, "reason": "Skipped due to JSON error"})
        details.append({"item": "sku_count", "score": 0, "max_score": 15, "passed": False, "reason": "Skipped"})
        details.append({"item": "avg_price", "score": 0, "max_score": 20, "passed": False, "reason": "Skipped"})
        details.append({"item": "skus list", "score": 0, "max_score": 25, "passed": False, "reason": "Skipped"})
        return {"total_score": total2, "details": details}

    total += item["score"]
    details.append(item)

    # 3. brand field
    item = {"item": "brand field", "max_score": 10}
    if data.get("brand") == "DermVeil":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "brand = DermVeil"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Expected 'DermVeil', got {data.get('brand')!r}"
    total += item["score"]
    details.append(item)

    # 4. category field
    item = {"item": "category field", "max_score": 10}
    if data.get("category") == "UV Moisturizer":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "category = UV Moisturizer"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Expected 'UV Moisturizer', got {data.get('category')!r}"
    total += item["score"]
    details.append(item)

    # 5. sku_count
    skus_list = data.get("skus", [])
    item = {"item": "sku_count", "max_score": 15}
    if data.get("sku_count") != len(skus_list):
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"sku_count={data.get('sku_count')} does not match len(skus)={len(skus_list)}"
    elif data.get("sku_count") != 2:
        item["score"] = 5  # correct match but wrong count
        item["passed"] = False
        item["reason"] = f"Expected 2 SKUs, got {data.get('sku_count')}"
    else:
        item["score"] = 15
        item["passed"] = True
        item["reason"] = "sku_count = 2, matches number of skus"
    total += item["score"]
    details.append(item)

    # 6. avg_price
    item = {"item": "avg_price", "max_score": 20}
    expected_avg = (32.50 + 28.80) / 2.0  # 30.65
    actual_avg = data.get("avg_price")
    if actual_avg is None:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "avg_price missing"
    elif math.isclose(actual_avg, expected_avg, rel_tol=1e-9, abs_tol=0.005):
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"avg_price = {actual_avg}, expected ~{expected_avg}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"avg_price = {actual_avg}, expected ~{expected_avg}"
    total += item["score"]
    details.append(item)

    # 7. skus list content
    item = {"item": "skus list", "max_score": 25}
    expected_skus = [
        {"sku_id": "DVM-101", "sku_name": "DermVeil UV Shield SPF50", "price": 32.50},
        {"sku_id": "DVM-102", "sku_name": "DermVeil Daily UV Lotion", "price": 28.80}
    ]
    # sort both for comparison
    try:
        actual_sorted = sorted(skus_list, key=lambda x: x["sku_id"])
        expected_sorted = sorted(expected_skus, key=lambda x: x["sku_id"])
    except (KeyError, TypeError):
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "skus list items missing required fields (sku_id, sku_name, price)"
        total += item["score"]
        details.append(item)
        # finish
        details.append({"item": "Total", "score": total, "max_score": max_total, "passed": total >= 80, "reason": "Score computed"})
        return {"total_score": total, "details": details}

    score_per_sku = 8  # 2 skus * 8 = 16, remaining 9 for exact match order? use 12.5 each but simpler
    # We'll grade each SKU individually
    sub_score = 0
    sub_max = 25
    # check length
    if len(actual_sorted) != len(expected_sorted):
        sub_score = 0
        item["reason"] = f"Expected {len(expected_sorted)} SKUs, got {len(actual_sorted)}"
    else:
        all_ok = True
        for i, (act, exp) in enumerate(zip(actual_sorted, expected_sorted)):
            if act.get("sku_id") != exp["sku_id"]:
                all_ok = False
                item["reason"] = f"SKU {i+1}: sku_id mismatch"
                break
            if act.get("sku_name") != exp["sku_name"]:
                all_ok = False
                item["reason"] = f"SKU {i+1}: sku_name mismatch"
                break
            if not math.isclose(act.get("price", 0), exp["price"], rel_tol=1e-9, abs_tol=0.005):
                all_ok = False
                item["reason"] = f"SKU {i+1}: price mismatch, got {act.get('price')}, expected {exp['price']}"
                break
        if all_ok:
            sub_score = 25
            item["reason"] = "All 2 SKUs match expected"
        else:
            sub_score = 0
    item["score"] = sub_score
    item["passed"] = sub_score == 25
    total += sub_score
    details.append(item)

    # final total
    details.append({"item": "Total", "score": total, "max_score": max_total, "passed": total >= 80, "reason": "Score computed"})
    return {"total_score": total, "details": details}


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = score(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
