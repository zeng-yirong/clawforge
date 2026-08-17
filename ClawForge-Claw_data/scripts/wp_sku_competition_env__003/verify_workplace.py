import json
import sys
import math
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []
    total_score = 0
    max_total = 100

    # 1. Check ops directory exists (5 points)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        total_score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ missing"})

    # 2. Check price_alert.json exists (5 points)
    alert_file = ops_dir / "price_alert.json"
    if alert_file.is_file():
        details.append({"item": "price_alert.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "file found"})
        total_score += 5
    else:
        details.append({"item": "price_alert.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "file missing"})
        _finish(ws, details, total_score)
        return

    # 3. Parse JSON (5 points)
    try:
        with open(alert_file, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "parse OK"})
        total_score += 5
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": f"parse error: {str(e)}"})
        _finish(ws, details, total_score)
        return

    # 4. Check brand field (10 points)
    if data.get("brand") == "SolarOat":
        details.append({"item": "brand field", "score": 10, "max_score": 10, "passed": True, "reason": "correct brand"})
        total_score += 10
    else:
        details.append({"item": "brand field", "score": 0, "max_score": 10, "passed": False, "reason": f"expected 'SolarOat', got {data.get('brand')}"})

    # 5. Check sku_id field (10 points)
    if data.get("sku_id") == "SO-1001":
        details.append({"item": "sku_id field", "score": 10, "max_score": 10, "passed": True, "reason": "correct sku_id"})
        total_score += 10
    else:
        details.append({"item": "sku_id field", "score": 0, "max_score": 10, "passed": False, "reason": f"expected 'SO-1001', got {data.get('sku_id')}"})

    # 6. Check current_price (20 points)
    expected_price = 24.80
    actual_price = data.get("current_price")
    if isinstance(actual_price, (int, float)) and math.isclose(actual_price, expected_price, rel_tol=1e-9):
        details.append({"item": "current_price value", "score": 20, "max_score": 20, "passed": True, "reason": f"correct price {actual_price}"})
        total_score += 20
    else:
        details.append({"item": "current_price value", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_price}, got {actual_price}"})

    # 7. Check competitors array (10 points for existence & length)
    competitors = data.get("competitors")
    if isinstance(competitors, list) and len(competitors) == 2:
        details.append({"item": "competitors array", "score": 10, "max_score": 10, "passed": True, "reason": "array with 2 entries"})
        total_score += 10
    else:
        details.append({"item": "competitors array", "score": 0, "max_score": 10, "passed": False, "reason": f"expected list of 2, got {competitors}"})
        competitors = []  # avoid downstream errors

    # 8. Check each competitor (20 points total, 10 each)
    expected_competitors = [
        {"brand": "LuminaSkin", "sku_id": "LS-2001", "price": 29.90},
        {"brand": "DermVeil", "sku_id": "DV-3001", "price": 32.00}
    ]
    comp_score = 0
    comp_reasons = []
    for idx, exp in enumerate(expected_competitors):
        if idx >= len(competitors):
            comp_reasons.append(f"competitor[{idx}] missing")
            continue
        act = competitors[idx]
        ok = True
        if act.get("brand") != exp["brand"]:
            ok = False; comp_reasons.append(f"competitor[{idx}] brand expected {exp['brand']} got {act.get('brand')}")
        if act.get("sku_id") != exp["sku_id"]:
            ok = False; comp_reasons.append(f"competitor[{idx}] sku_id expected {exp['sku_id']} got {act.get('sku_id')}")
        if not isinstance(act.get("price"), (int, float)) or not math.isclose(act["price"], exp["price"], rel_tol=1e-9):
            ok = False; comp_reasons.append(f"competitor[{idx}] price expected {exp['price']} got {act.get('price')}")
        if ok:
            comp_score += 10
    details.append({"item": "competitor details", "score": comp_score, "max_score": 20, "passed": comp_score==20, "reason": "; ".join(comp_reasons) if comp_reasons else "all correct"})
    total_score += comp_score

    # 9. Extra: ensure prices are from LIVE book (not archive) – implicit check already done via precise values
    # For robustness, we can check that no competitor price matches archive values.
    archive_prices = {"LS-2001": 27.50, "DV-3001": 30.00}
    if isinstance(competitors, list):
        used_archive = False
        for c in competitors:
            if c.get("sku_id") in archive_prices and math.isclose(c.get("price",0), archive_prices[c["sku_id"]], rel_tol=1e-9):
                used_archive = True
                break
        if not used_archive:
            details.append({"item": "archive price prevention", "score": 5, "max_score": 5, "passed": True, "reason": "no archive prices used"})
            total_score += 5
        else:
            details.append({"item": "archive price prevention", "score": 0, "max_score": 5, "passed": False, "reason": "detected archive prices in competitors"})
    else:
        details.append({"item": "archive price prevention", "score": 0, "max_score": 5, "passed": False, "reason": "cannot check competitors"})

    # 10. Remaining points for overall structure (bonus)
    # check no extra top-level keys? not required, but we can add small bonus for clean structure.
    # We'll give 5 if brand, sku_id, current_price, competitors present and no obvious garbage.
    required_keys = {"brand", "sku_id", "current_price", "competitors"}
    actual_keys = set(data.keys())
    if required_keys.issubset(actual_keys) and len(actual_keys) <= 5:
        details.append({"item": "clean structure", "score": 5, "max_score": 5, "passed": True, "reason": "no extraneous keys"})
        total_score += 5
    else:
        details.append({"item": "clean structure", "score": 0, "max_score": 5, "passed": False, "reason": f"unexpected keys: {actual_keys - required_keys}"})

    total_score = min(total_score, 100)
    _finish(ws, details, total_score)

def _finish(ws, details, total_score):
    result = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
