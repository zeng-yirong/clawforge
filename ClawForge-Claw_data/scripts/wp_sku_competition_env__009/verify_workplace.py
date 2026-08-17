import sys
import json
import os
import pathlib
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace)

    details = []
    total_score = 0

    # 1. Check reports directory exists (10 points)
    reports_dir = ws / "reports"
    if reports_dir.is_dir():
        details.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found reports/"})
        total_score += 10
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing reports/ directory"})

    # 2. Check competitor_report.json exists and is valid JSON (10 points)
    report_path = reports_dir / "competitor_report.json"
    if not report_path.is_file():
        details.append({"item": "competitor_report.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        write_result(details, total_score)
        return
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "competitor_report.json is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "File is valid JSON"})
        total_score += 10
    except Exception as e:
        details.append({"item": "competitor_report.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        write_result(details, total_score)
        return

    # 3. Check required fields (10 points)
    required_fields = ["lumina_skus", "aqua_skus", "lumina_avg_price", "aqua_avg_price", "avg_price_diff"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({"item": "required fields present", "score": 10, "max_score": 10, "passed": True, "reason": "All 5 required fields exist"})
        total_score += 10
    else:
        details.append({"item": "required fields present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields: {missing}"})
        write_result(details, total_score)
        return

    # 4. Verify lumina_skus (20 points) – must contain exactly LS-HS-001 and LS-HS-002 with correct prices
    lumina_expected = {
        "LS-HS-001": {"sku_name": "HydraGlow Essence", "price": 28.50},
        "LS-HS-002": {"sku_name": "Radiance Boost Serum", "price": 32.00}
    }
    lumina_skus = data["lumina_skus"]
    lumina_score = 0
    lumina_reasons = []
    if not isinstance(lumina_skus, list):
        lumina_reasons.append("lumina_skus is not a list")
    else:
        # check count
        if len(lumina_skus) != 2:
            lumina_reasons.append(f"Expected 2 SKUs, got {len(lumina_skus)}")
        else:
            # check each expected SKU
            for entry in lumina_skus:
                sid = entry.get("sku_id")
                if sid not in lumina_expected:
                    continue
                exp = lumina_expected[sid]
                if entry.get("sku_name") != exp["sku_name"]:
                    lumina_reasons.append(f"{sid}: sku_name mismatch (got {entry.get('sku_name')})")
                if not math.isclose(entry.get("current_price", 0), exp["price"], abs_tol=0.005):
                    lumina_reasons.append(f"{sid}: price mismatch (got {entry.get('current_price')}, expected {exp['price']})")
            # also ensure no extra SKUs
            extra = [e for e in lumina_skus if e.get("sku_id") not in lumina_expected]
            if extra:
                lumina_reasons.append(f"Extra SKUs in lumina_skus: {[e['sku_id'] for e in extra]}")
    if not lumina_reasons:
        lumina_score = 20
        details.append({"item": "lumina_skus correct", "score": 20, "max_score": 20, "passed": True, "reason": "Both SKUs with correct names and prices"})
    else:
        details.append({"item": "lumina_skus correct", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(lumina_reasons)})
    total_score += lumina_score

    # 5. Verify aqua_skus (20 points) – must contain exactly AP-HS-001 and AP-HS-002 with correct prices
    aqua_expected = {
        "AP-HS-001": {"sku_name": "AquaCharge Serum", "price": 30.00},
        "AP-HS-002": {"sku_name": "Deepsea Hydrator", "price": 34.00}
    }
    aqua_skus = data["aqua_skus"]
    aqua_score = 0
    aqua_reasons = []
    if not isinstance(aqua_skus, list):
        aqua_reasons.append("aqua_skus is not a list")
    else:
        if len(aqua_skus) != 2:
            aqua_reasons.append(f"Expected 2 SKUs, got {len(aqua_skus)}")
        else:
            for entry in aqua_skus:
                sid = entry.get("sku_id")
                if sid not in aqua_expected:
                    continue
                exp = aqua_expected[sid]
                if entry.get("sku_name") != exp["sku_name"]:
                    aqua_reasons.append(f"{sid}: sku_name mismatch")
                if not math.isclose(entry.get("current_price", 0), exp["price"], abs_tol=0.005):
                    aqua_reasons.append(f"{sid}: price mismatch")
            extra = [e for e in aqua_skus if e.get("sku_id") not in aqua_expected]
            if extra:
                aqua_reasons.append(f"Extra SKUs in aqua_skus: {[e['sku_id'] for e in extra]}")
    if not aqua_reasons:
        aqua_score = 20
        details.append({"item": "aqua_skus correct", "score": 20, "max_score": 20, "passed": True, "reason": "Both SKUs with correct names and prices"})
    else:
        details.append({"item": "aqua_skus correct", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(aqua_reasons)})
    total_score += aqua_score

    # 6. Compute expected averages from the data above
    lumina_prices = [28.50, 32.00]
    aqua_prices = [30.00, 34.00]
    exp_lumina_avg = round(sum(lumina_prices) / len(lumina_prices), 2)
    exp_aqua_avg = round(sum(aqua_prices) / len(aqua_prices), 2)
    exp_diff = round(exp_lumina_avg - exp_aqua_avg, 2)

    # 7. Check lumina_avg_price (10 points)
    try:
        lumina_avg = data["lumina_avg_price"]
        if math.isclose(lumina_avg, exp_lumina_avg, abs_tol=0.005):
            details.append({"item": "lumina_avg_price correct", "score": 10, "max_score": 10, "passed": True, "reason": f"Got {lumina_avg}"})
            total_score += 10
        else:
            details.append({"item": "lumina_avg_price correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {exp_lumina_avg}, got {lumina_avg}"})
    except Exception as e:
        details.append({"item": "lumina_avg_price correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Error: {e}"})

    # 8. Check aqua_avg_price (10 points)
    try:
        aqua_avg = data["aqua_avg_price"]
        if math.isclose(aqua_avg, exp_aqua_avg, abs_tol=0.005):
            details.append({"item": "aqua_avg_price correct", "score": 10, "max_score": 10, "passed": True, "reason": f"Got {aqua_avg}"})
            total_score += 10
        else:
            details.append({"item": "aqua_avg_price correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {exp_aqua_avg}, got {aqua_avg}"})
    except Exception as e:
        details.append({"item": "aqua_avg_price correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Error: {e}"})

    # 9. Check avg_price_diff (10 points)
    try:
        diff = data["avg_price_diff"]
        if math.isclose(diff, exp_diff, abs_tol=0.005):
            details.append({"item": "avg_price_diff correct", "score": 10, "max_score": 10, "passed": True, "reason": f"Got {diff}"})
            total_score += 10
        else:
            details.append({"item": "avg_price_diff correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {exp_diff}, got {diff}"})
    except Exception as e:
        details.append({"item": "avg_price_diff correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Error: {e}"})

    write_result(details, total_score)

def write_result(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
