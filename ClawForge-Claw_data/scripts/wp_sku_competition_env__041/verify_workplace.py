import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "category_comparison_lumina_serum.json")
    score_details = []

    # 1. File exists (10 points)
    exists = os.path.isfile(report_path)
    score_details.append({
        "item": "Report file exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File exists" if exists else f"File not found at {report_path}"
    })
    if not exists:
        _write_score(score_details)
        return

    # 2. Valid JSON (10 points)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully"
        })
    except Exception as e:
        score_details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        _write_score(score_details)
        return

    # 3. Required top-level fields (each 4 points -> 16 total)
    required_fields = ["brand_name", "category_name", "skus", "summary"]
    for field in required_fields:
        passed = field in data
        score_details.append({
            "item": f"Field '{field}' exists",
            "score": 4 if passed else 0,
            "max_score": 4,
            "passed": passed,
            "reason": f"Field '{field}' found" if passed else f"Missing field '{field}'"
        })

    # 4. Correct brand_name (4 points)
    brand_ok = data.get("brand_name") == "LuminaSkin"
    score_details.append({
        "item": "brand_name is 'LuminaSkin'",
        "score": 4 if brand_ok else 0,
        "max_score": 4,
        "passed": brand_ok,
        "reason": f"brand_name={data.get('brand_name')}" if not brand_ok else "OK"
    })

    # 5. Correct category_name (4 points)
    cat_ok = data.get("category_name") == "Hydration Serum"
    score_details.append({
        "item": "category_name is 'Hydration Serum'",
        "score": 4 if cat_ok else 0,
        "max_score": 4,
        "passed": cat_ok,
        "reason": f"category_name={data.get('category_name')}" if not cat_ok else "OK"
    })

    # 6. skus is a list (5 points)
    skus = data.get("skus")
    list_ok = isinstance(skus, list)
    score_details.append({
        "item": "skus is a list",
        "score": 5 if list_ok else 0,
        "max_score": 5,
        "passed": list_ok,
        "reason": f"Found {len(skus)} items" if list_ok else "skus is not a list"
    })
    if not list_ok:
        _write_score(score_details)
        return

    # 7. Correct SKU count (10 points)
    expected_count = 3
    count_ok = len(skus) == expected_count
    score_details.append({
        "item": f"Correct SKU count ({expected_count})",
        "score": 10 if count_ok else 0,
        "max_score": 10,
        "passed": count_ok,
        "reason": f"Count = {len(skus)}" if not count_ok else "OK"
    })

    # 8. Per-SKU required fields (10 points)
    per_sku_fields = ["sku_name", "size", "price", "selling_points", "ingredients"]
    all_field_ok = True
    missing = []
    for i, sku in enumerate(skus):
        for f in per_sku_fields:
            if f not in sku:
                all_field_ok = False
                missing.append(f"SKU {i} missing {f}")
    score_details.append({
        "item": "All SKUs have sku_name, size, price, selling_points, ingredients",
        "score": 10 if all_field_ok else 0,
        "max_score": 10,
        "passed": all_field_ok,
        "reason": "OK" if all_field_ok else "; ".join(missing)
    })

    # 9. Price accuracy (15 points, 5 per SKU)
    expected_prices = {
        "LuminaHydra Boost Serum 50ml": 29.99,
        "LuminaHydra Intense Serum 100ml": 49.99,
        "LuminaHydra Travel Duo 30ml": 39.99
    }
    price_score = 0
    price_parts = []
    for sku in skus:
        name = sku.get("sku_name")
        if name not in expected_prices:
            price_parts.append(f"Unexpected SKU: {name}")
            continue
        expected = expected_prices[name]
        actual = sku.get("price")
        if actual is None or not isinstance(actual, (int, float)):
            price_parts.append(f"{name}: price missing or non-numeric")
            continue
        if abs(actual - expected) < 0.005:
            price_score += 5
            price_parts.append(f"{name}: price correct")
        else:
            price_parts.append(f"{name}: price={actual}, expected={expected}")
    score_details.append({
        "item": "Price accuracy (5 pts per SKU)",
        "score": price_score,
        "max_score": 15,
        "passed": price_score == 15,
        "reason": "; ".join(price_parts)
    })

    # 10. Selling points & ingredients match (5 points)
    expected_details = {
        "LuminaHydra Boost Serum 50ml": {
            "selling_points": ["Brightening", "Lightweight"],
            "ingredients": ["Niacinamide", "Hyaluronic Acid", "Vitamin C"]
        },
        "LuminaHydra Intense Serum 100ml": {
            "selling_points": ["Intense Hydration", "Anti-aging"],
            "ingredients": ["Retinol", "Peptides", "Squalane"]
        },
        "LuminaHydra Travel Duo 30ml": {
            "selling_points": ["Travel-friendly", "Quick absorption"],
            "ingredients": ["Green Tea Extract", "Glycerin"]
        }
    }
    details_ok = True
    for sku in skus:
        name = sku.get("sku_name")
        if name not in expected_details:
            details_ok = False
            continue
        exp = expected_details[name]
        actual_sp = set(sku.get("selling_points", []))
        actual_ing = set(sku.get("ingredients", []))
        if set(exp["selling_points"]) != actual_sp or set(exp["ingredients"]) != actual_ing:
            details_ok = False
    score_details.append({
        "item": "Correct selling_points and ingredients",
        "score": 5 if details_ok else 0,
        "max_score": 5,
        "passed": details_ok,
        "reason": "All match" if details_ok else "Mismatch found"
    })

    # 11. Summary count (5 points)
    summary = data.get("summary", {})
    count_val = summary.get("count")
    count_correct = count_val == 3
    score_details.append({
        "item": "summary.count is 3",
        "score": 5 if count_correct else 0,
        "max_score": 5,
        "passed": count_correct,
        "reason": f"count={count_val}" if not count_correct else "OK"
    })

    # 12. Summary average_price (6 points)
    avg_val = summary.get("average_price")
    expected_avg = 39.99
    avg_correct = False
    if isinstance(avg_val, (int, float)):
        if abs(avg_val - expected_avg) < 0.005:
            avg_correct = True
    score_details.append({
        "item": "summary.average_price is 39.99",
        "score": 6 if avg_correct else 0,
        "max_score": 6,
        "passed": avg_correct,
        "reason": f"average_price={avg_val}" if not avg_correct else "OK"
    })

    total = sum(d["score"] for d in score_details)
    _write_score(score_details, total)

def _write_score(details, total=None):
    if total is None:
        total = sum(d["score"] for d in details)
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
