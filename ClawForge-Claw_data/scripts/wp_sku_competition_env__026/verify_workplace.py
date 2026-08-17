import sys
import os
import json
import re
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # Helper to add detail
    def add_detail(item, score, max_score, passed, reason):
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # ---- 1. Output directory exists (5 pts) ----
    output_dir = Path(workspace) / "outputs"
    if output_dir.is_dir():
        add_detail("Output directory exists", 5, 5, True, "outputs/ found")
        score += 5
    else:
        add_detail("Output directory exists", 0, 5, False, "outputs/ not found")
        # can't proceed further without output dir
        write_final(score, details)
        return

    # ---- 2. competition_report.json exists and is valid JSON (10 pts) ----
    report_path = output_dir / "competition_report.json"
    if not report_path.is_file():
        add_detail("Report file exists", 0, 10, False, "competition_report.json not found")
        write_final(score, details)
        return
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        add_detail("JSON valid", 10, 10, True, "Parsed successfully")
        score += 10
    except (json.JSONDecodeError, ValueError) as e:
        add_detail("JSON valid", 0, 10, False, f"Invalid JSON: {e}")
        write_final(score, details)
        return

    # ---- 3. Required top-level keys exist (10 pts) ----
    required_keys = ["lumina_skin_skus", "derm_veil_skus", "average_prices"]
    missing = [k for k in required_keys if k not in report]
    if not missing:
        add_detail("Top-level keys present", 10, 10, True, "All required keys found")
        score += 10
    else:
        add_detail("Top-level keys present", 0, 10, False, f"Missing keys: {missing}")
        # Still attempt partial checks

    # ---- 4. Correct SKU lists (20 pts: 15 for content, 5 for correct exclusion) ----
    # Expected active Hydration Serum SKUs for LuminaSkin: LS-001, LS-002, LS-003
    # For DermVeil: DV-101, DV-102
    # Also ensure no wrong SKUs (like LS-004, DV-103, AP-001) are included
    ls_skus = report.get("lumina_skin_skus", [])
    dv_skus = report.get("derm_veil_skus", [])
    expected_ls_ids = {"LS-001", "LS-002", "LS-003"}
    expected_dv_ids = {"DV-101", "DV-102"}

    # Check LuminaSkin list
    ls_ids = set(s.get("sku_id") for s in ls_skus if isinstance(s, dict))
    ls_correct = (ls_ids == expected_ls_ids)
    # Check DermVeil list
    dv_ids = set(s.get("sku_id") for s in dv_skus if isinstance(s, dict))
    dv_correct = (dv_ids == expected_dv_ids)

    if ls_correct and dv_correct:
        add_detail("SKU list correctness", 15, 15, True, "Both brand SKU sets match expected active Hydration Serum SKUs")
        score += 15
    else:
        reason = ""
        if not ls_correct:
            reason += f"LuminaSkin SKUs: got {ls_ids}, expected {expected_ls_ids}. "
        if not dv_correct:
            reason += f"DermVeil SKUs: got {dv_ids}, expected {expected_dv_ids}. "
        add_detail("SKU list correctness", 0, 15, False, reason.strip())

    # Check that no extra SKUs from wrong categories/brands are present
    all_ids = ls_ids.union(dv_ids)
    forbidden = {"LS-004", "DV-103", "AP-001"}
    extra_penalized = [fid for fid in all_ids if fid in forbidden]
    if extra_penalized:
        add_detail("No extraneous SKUs", 0, 5, False, f"Found disallowed SKUs: {extra_penalized}")
    else:
        add_detail("No extraneous SKUs", 5, 5, True, "Only allowed SKUs present")
        score += 5

    # ---- 5. Correct prices (20 pts) ----
    # Build lookup for expected prices from the live price book
    expected_prices = {
        "LS-001": 24.99,
        "LS-002": 26.50,
        "LS-003": 27.50,
        "DV-101": 25.49,
        "DV-102": 29.49
    }
    price_ok = True
    price_errors = []
    for sku_list, name in [(ls_skus, "LuminaSkin"), (dv_skus, "DermVeil")]:
        for s in sku_list:
            if not isinstance(s, dict):
                price_ok = False
                price_errors.append(f"Non-dict entry in {name}")
                continue
            sid = s.get("sku_id")
            if sid not in expected_prices:
                continue  # handled above
            actual_price = s.get("price")
            expected = expected_prices[sid]
            # Allow up to 0.005 tolerance (floating point)
            if actual_price is None or abs(actual_price - expected) > 0.005:
                price_ok = False
                price_errors.append(f"{sid}: got {actual_price}, expected {expected}")
    if price_ok:
        add_detail("Price correctness", 20, 20, True, "All SKU prices match expected")
        score += 20
    else:
        add_detail("Price correctness", 0, 20, False, "; ".join(price_errors))

    # ---- 6. Correct average calculations (20 pts) ----
    # Expected averages:
    # LS: (24.99+26.50+27.50)/3 = 78.99/3 = 26.33
    # DV: (25.49+29.49)/2 = 54.98/2 = 27.49
    # diff: 26.33 - 27.49 = -1.16
    avg = report.get("average_prices", {})
    expected_avg = {
        "lumina_skin": 26.33,
        "derm_veil": 27.49,
        "difference": -1.16
    }
    avg_ok = True
    avg_errors = []
    for key, expected_val in expected_avg.items():
        actual = avg.get(key)
        if actual is None or abs(actual - expected_val) > 0.005:
            avg_ok = False
            avg_errors.append(f"{key}: got {actual}, expected {expected_val}")
    if avg_ok:
        add_detail("Average price calculations", 20, 20, True, "All average values correct")
        score += 20
    else:
        add_detail("Average price calculations", 0, 20, False, "; ".join(avg_errors))

    # ---- 7. Structured properly: each SKU entry is a dict with sku_id and price (5 pts) ----
    structure_ok = True
    for sku_list, name in [(ls_skus, "LuminaSkin"), (dv_skus, "DermVeil")]:
        for s in sku_list:
            if not isinstance(s, dict) or "sku_id" not in s or "price" not in s:
                structure_ok = False
                break
    if structure_ok:
        add_detail("SKU entry structure", 5, 5, True, "Each entry contains sku_id and price")
        score += 5
    else:
        add_detail("SKU entry structure", 0, 5, False, "Some entries missing required fields")

    # ---- 8. Report metadata (optional but nice) ----
    # We don't enforce metadata, but give extra 5 if it contains 'based_on_price_book' with correct version
    meta = report.get("average_prices", {})
    # Actually no metadata required – we'll skip

    # ---- Total written to workplace_score.json ----
    write_final(score, details)

def write_final(score, details):
    output = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Total score: {score}/100")
    # Ensure exit code for CI (optional)
    sys.exit(0 if score == 100 else 1)

if __name__ == "__main__":
    main()
