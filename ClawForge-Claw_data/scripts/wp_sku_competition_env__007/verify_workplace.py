import json
import os
import sys
from pathlib import Path
from statistics import mean

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def verify(workspace: str) -> dict:
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. ops/ directory exists (10 points)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # 2. ops/price_outliers.json exists (10 points)
    out_file = ops_dir / "price_outliers.json"
    if out_file.is_file():
        details.append({"item": "price_outliers.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File present"})
        total_score += 10
    else:
        details.append({"item": "price_outliers.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})
        # Cannot continue without file
        return {"total_score": total_score, "details": details}

    # 3. JSON is valid and is a list (10 points)
    try:
        outliers = load_json(out_file)
        if isinstance(outliers, list):
            details.append({"item": "JSON is a valid list", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully as list"})
            total_score += 10
        else:
            details.append({"item": "JSON is a valid list", "score": 0, "max_score": 10, "passed": False, "reason": "Root is not a list"})
            return {"total_score": total_score, "details": details}
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON is a valid list", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        return {"total_score": total_score, "details": details}

    # 4. Each outlier has required fields (sku_id, price, category, average_price, flag) (10 points)
    required_fields = {"sku_id", "price", "category", "average_price", "flag"}
    all_have_fields = True
    for idx, entry in enumerate(outliers):
        if not isinstance(entry, dict):
            all_have_fields = False
            break
        if not required_fields.issubset(entry.keys()):
            all_have_fields = False
            break
    if all_have_fields and len(outliers) > 0:
        details.append({"item": "All outliers have required fields", "score": 10, "max_score": 10, "passed": True, "reason": f"{len(outliers)} entries with correct keys"})
        total_score += 10
    else:
        details.append({"item": "All outliers have required fields", "score": 0, "max_score": 10, "passed": False, "reason": "Missing fields or empty list"})
        # Try to continue with partial points later; but stop here for fairness
        return {"total_score": total_score, "details": details}

    # 5. Read source data and recompute correct outliers (50 points)
    #    We give 25 per correct outlier (two expected), or 50 total if both correct, partial if one.
    try:
        skus_data = load_json(ws / "data" / "skus" / "skus.json")
        pb_data = load_json(ws / "data" / "pricing" / "price_books.json")
    except Exception as e:
        details.append({"item": "Computational correctness", "score": 0, "max_score": 50, "passed": False, "reason": f"Could not read source data: {e}"})
        return {"total_score": total_score, "details": details}

    # Find the live price book
    live_pb = None
    for pb in pb_data.get("price_books", []):
        if pb.get("is_current") and pb.get("status") == "approved":
            live_pb = pb
            break
    if live_pb is None:
        details.append({"item": "Computational correctness", "score": 0, "max_score": 50, "passed": False, "reason": "No live price book found"})
        return {"total_score": total_score, "details": details}

    # Build lookup: sku_id -> category_name
    sku_to_cat = {}
    for s in skus_data.get("skus", []):
        sku_to_cat[s["sku_id"]] = s["category_name"]

    # Build per‑category list of prices (from live entries only)
    cat_prices = {}
    for entry in live_pb.get("entries", []):
        sid = entry["sku_id"]
        cat = sku_to_cat.get(sid)
        if cat is not None:
            cat_prices.setdefault(cat, []).append(entry["price"])

    # Compute category averages
    cat_avg = {cat: mean(prices) for cat, prices in cat_prices.items()}

    # Determine expected outliers (price > 1.5 * avg or price < 0.5 * avg)
    expected_outliers = []
    # We'll also build a dict of expected values for comparison
    for entry in live_pb.get("entries", []):
        sid = entry["sku_id"]
        price = entry["price"]
        cat = sku_to_cat.get(sid)
        if cat is None:
            continue
        avg = cat_avg[cat]
        if price > 1.5 * avg or price < 0.5 * avg:
            flag = "above" if price > 1.5 * avg else "below"
            expected_outliers.append({
                "sku_id": sid,
                "price": price,
                "category": cat,
                "average_price": round(avg, 4),  # to avoid floating point noise
                "flag": flag
            })

    # Sort both lists by sku_id for comparison
    expected_outliers.sort(key=lambda x: x["sku_id"])
    agent_outliers = sorted(outliers, key=lambda x: x["sku_id"])

    # Check total count
    if len(agent_outliers) != len(expected_outliers):
        details.append({"item": "Outlier count matches", "score": 0, "max_score": 50, "passed": False,
                        "reason": f"Expected {len(expected_outliers)} outliers, found {len(agent_outliers)}"})
        return {"total_score": total_score, "details": details}

    # Compare each expected outlier with agent's
    correct_count = 0
    for exp, act in zip(expected_outliers, agent_outliers):
        # compare with tolerance for float
        ok = True
        reason_parts = []
        # sku_id (exact)
        if exp["sku_id"] != act.get("sku_id"):
            ok = False
            reason_parts.append(f"sku_id mismatch: expected {exp['sku_id']}")
        # price (float within 1e-6)
        if abs(exp["price"] - act.get("price", 0.0)) > 1e-6:
            ok = False
            reason_parts.append(f"price mismatch: expected {exp['price']}")
        # category (exact)
        if exp["category"] != act.get("category"):
            ok = False
            reason_parts.append(f"category mismatch: expected {exp['category']}")
        # average_price (float within 1e-6)
        if abs(exp["average_price"] - act.get("average_price", 0.0)) > 1e-4:  # slightly larger due to rounding
            ok = False
            reason_parts.append(f"average_price mismatch: expected {exp['average_price']}")
        # flag (exact)
        if exp["flag"] != act.get("flag"):
            ok = False
            reason_parts.append(f"flag mismatch: expected {exp['flag']}")
        if ok:
            correct_count += 1
        else:
            details.append({"item": f"Outlier {exp['sku_id']} correctness", "score": 0, "max_score": 25, "passed": False,
                            "reason": "; ".join(reason_parts)})

    # Award points per correct entry (25 each, total 50)
    if correct_count == 2:
        details.append({"item": "All (2) outliers correct", "score": 50, "max_score": 50, "passed": True,
                        "reason": "Both expected outliers found with correct values"})
        total_score += 50
    elif correct_count == 1:
        details.append({"item": "Only one outlier correct", "score": 25, "max_score": 50, "passed": False,
                        "reason": "One outlier matched, one did not"})
        total_score += 25
    else:
        details.append({"item": "No correct outliers", "score": 0, "max_score": 50, "passed": False,
                        "reason": "None of the outliers matched expected values"})

    # Note: no extra credit for extra items (already checked count)
    return {"total_score": min(total_score, 100), "details": details}


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
