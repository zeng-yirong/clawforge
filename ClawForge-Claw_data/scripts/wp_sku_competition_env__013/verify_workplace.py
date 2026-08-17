import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # Helper to read JSON safely
    def load_json(rel_path):
        full = os.path.join(workspace, rel_path)
        if not os.path.exists(full):
            return None, f"File not found: {rel_path}"
        try:
            with open(full, 'r') as f:
                data = json.load(f)
            return data, None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON in {rel_path}: {e}"

    # ---------- 1. Check output file exists ----------
    out_path = os.path.join(workspace, "ops", "competition_pricing.json")
    item = {"item": "Output file exists", "max_score": 10}
    if os.path.exists(out_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops/competition_pricing.json found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops/competition_pricing.json missing"
    results.append(item)

    # ---------- 2. Validate JSON and required keys ----------
    item = {"item": "Output JSON valid & contains required fields", "max_score": 15}
    try:
        with open(out_path, 'r') as f:
            agent_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Cannot read output: {e}"
        results.append(item)
        # Cannot proceed further
        finalize(results, total_score, workspace)
        return

    required_keys = ["LuminaSkin", "AquaPulse", "price_difference"]
    missing = [k for k in required_keys if k not in agent_data]
    if missing:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"Missing keys: {missing}"
    else:
        # Also check nested keys for each brand
        ls = agent_data.get("LuminaSkin", {})
        ap = agent_data.get("AquaPulse", {})
        brand_required = ["average_price", "skus_count"]
        ls_missing = [k for k in brand_required if k not in ls]
        ap_missing = [k for k in brand_required if k not in ap]
        if ls_missing or ap_missing:
            item["score"] = 5
            item["passed"] = False
            item["reason"] = f"LuminaSkin missing {ls_missing}, AquaPulse missing {ap_missing}"
        else:
            item["score"] = 15
            item["passed"] = True
            item["reason"] = "All required fields present"
    results.append(item)
    total_score += item["score"] if item["passed"] else 0

    # ---------- 3. Load ground truth from workspace ----------
    def compute_expected():
        # Load price books
        pb_data, err = load_json("data/pricing/price_books.json")
        if err:
            return None, err
        if "price_books" not in pb_data:
            return None, "price_books key missing"
        # Find current price book
        current_pb = None
        for pb in pb_data["price_books"]:
            if pb.get("is_current") == True:
                current_pb = pb
                break
        if current_pb is None:
            return None, "No current price book found"
        entries = {e["sku_id"]: e["price"] for e in current_pb["entries"]}

        # Load SKUs
        sku_data, err = load_json("data/skus/skus.json")
        if err:
            return None, err
        if "skus" not in sku_data:
            return None, "skus key missing"

        # Filter LuminaSkin & AquaPulse Hydration Serum
        ls_skus = []
        ap_skus = []
        for sku in sku_data["skus"]:
            if sku["category_name"] != "Hydration Serum":
                continue
            if sku["brand_name"] == "LuminaSkin":
                ls_skus.append(sku["sku_id"])
            elif sku["brand_name"] == "AquaPulse":
                ap_skus.append(sku["sku_id"])

        # Get prices (use only those with entries)
        ls_prices = [entries[s] for s in ls_skus if s in entries]
        ap_prices = [entries[s] for s in ap_skus if s in entries]

        if len(ls_prices) != 2:
            return None, f"Expected 2 LuminaSkin HS prices, got {len(ls_prices)}"
        if len(ap_prices) != 3:
            return None, f"Expected 3 AquaPulse HS prices, got {len(ap_prices)}"

        # Compute average with 2 decimal rounding
        ls_avg = round(sum(ls_prices) / len(ls_prices), 2)
        ap_avg = round(sum(ap_prices) / len(ap_prices), 2)
        diff = round(ls_avg - ap_avg, 2)

        expected = {
            "LuminaSkin": {"average_price": ls_avg, "skus_count": len(ls_prices)},
            "AquaPulse": {"average_price": ap_avg, "skus_count": len(ap_prices)},
            "price_difference": diff
        }
        return expected, None

    exp, err = compute_expected()
    if err:
        for suffix in [" (LuminaSkin avg)", " (AquaPulse avg)", " (difference)"]:
            results.append({"item": f"Computed expected value{suffix}", "score": 0, "max_score": 25, "passed": False,
                            "reason": f"Could not compute ground truth: {err}"})
        finalize(results, total_score, workspace)
        return

    # ---------- 4. Compare each numeric value ----------
    checks = [
        ("LuminaSkin average price", "LuminaSkin", "average_price", exp["LuminaSkin"]["average_price"], 20),
        ("LuminaSkin SKU count", "LuminaSkin", "skus_count", exp["LuminaSkin"]["skus_count"], 5),
        ("AquaPulse average price", "AquaPulse", "average_price", exp["AquaPulse"]["average_price"], 20),
        ("AquaPulse SKU count", "AquaPulse", "skus_count", exp["AquaPulse"]["skus_count"], 5),
        ("Price difference", None, "price_difference", exp["price_difference"], 20),
    ]

    for item_name, brand, key, expected_val, weight in checks:
        item = {"item": item_name, "max_score": weight}
        if brand is None:
            actual = agent_data.get(key)
        else:
            brand_dict = agent_data.get(brand, {})
            actual = brand_dict.get(key) if isinstance(brand_dict, dict) else None

        if actual is None:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"Missing value for {item_name}"
        else:
            try:
                actual_num = float(actual)
            except (TypeError, ValueError):
                item["score"] = 0
                item["passed"] = False
                item["reason"] = f"Value not numeric: {actual}"
                results.append(item)
                continue
            # Allow small floating point tolerance (0.01)
            if abs(actual_num - expected_val) < 0.015:
                item["score"] = weight
                item["passed"] = True
                item["reason"] = f"Expected {expected_val}, got {actual_num}"
            else:
                item["score"] = 0
                item["passed"] = False
                item["reason"] = f"Expected {expected_val}, got {actual_num}"
        results.append(item)

    # ---------- Finalize ----------
    finalize(results, total_score, workspace)


def finalize(results, total_score, workspace):
    # Compute total score from passed scores
    final_total = sum(r["score"] for r in results)
    output = {
        "total_score": final_total,
        "details": results
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Validation complete. Score: {final_total}/100")


if __name__ == "__main__":
    main()
