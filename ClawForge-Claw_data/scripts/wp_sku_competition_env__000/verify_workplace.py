#!/usr/bin/env python3
"""
Verify the agent's output for wp_sku_competition_env__000.

Checks:
- Directory structure (10p)
- Output file exists (10p)
- JSON is valid (10p)
- Fields present (10p)
- SKU count correct (10p)
- Each SKU has required fields (10p)
- Prices match the current approved price book (30p)
- No extra brands/categories (10p)
"""
import json
import sys
import os
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # Helper
    def add_item(name, score, max_score, passed, reason):
        details.append({"item": name, "score": score, "max_score": max_score, "passed": passed, "reason": reason})
        return score

    # 1. Directory structure (check data/, data/brands/, data/skus/, data/pricing/, data/attachments/ exist)
    required_dirs = [
        Path(workspace) / "data",
        Path(workspace) / "data/brands",
        Path(workspace) / "data/skus",
        Path(workspace) / "data/pricing",
        Path(workspace) / "data/attachments",
    ]
    dirs_exist = all(d.is_dir() for d in required_dirs)
    total_score += add_item("Directory structure", 10 if dirs_exist else 0, 10, dirs_exist,
                            "All required data subdirectories exist" if dirs_exist else "Missing data/ subdirectories")

    # 2. Output file exists
    output_path = Path(workspace) / "output/competitor_price_report.json"
    file_exists = output_path.is_file()
    total_score += add_item("Output file exists", 10 if file_exists else 0, 10, file_exists,
                            "output/competitor_price_report.json found" if file_exists else "output/competitor_price_report.json not found")
    if not file_exists:
        # Cannot proceed further, return partial score
        return {"total_score": total_score, "details": details}

    # 3. JSON is valid
    try:
        with open(output_path, "r") as f:
            report = json.load(f)
        json_valid = True
        total_score += add_item("JSON valid", 10, 10, True, "Valid JSON")
    except (json.JSONDecodeError, Exception):
        total_score += add_item("JSON valid", 0, 10, False, "File is not valid JSON")
        return {"total_score": total_score, "details": details}

    # 4. Fields present (report_title, skus)
    has_report_title = "report_title" in report
    has_skus = "skus" in report and isinstance(report["skus"], list)
    fields_present = has_report_title and has_skus
    total_score += add_item("Required top-level fields", 10 if fields_present else 0, 10, fields_present,
                            "report_title and skus present" if fields_present else "Missing report_title or skus")

    if not fields_present:
        return {"total_score": total_score, "details": details}

    # 5. SKU count correct (should be 3 LuminaSkin Hydration Serum SKUs)
    expected_sku_ids = {"LS-HS-001", "LS-HS-002", "LS-HS-003"}
    actual_sku_ids = {sku.get("sku_id") for sku in report["skus"]}
    count_correct = len(report["skus"]) == 3 and actual_sku_ids == expected_sku_ids
    total_score += add_item("SKU count and IDs", 10 if count_correct else 0, 10, count_correct,
                            f"Found 3 correct LuminaSkin SKUs" if count_correct else f"SKU set mismatch: got {actual_sku_ids}")

    # 6. Each SKU has required fields (sku_id, sku_name, current_price, selling_points)
    sku_field_ok = True
    for sku in report["skus"]:
        if not all(k in sku for k in ("sku_id", "sku_name", "current_price", "selling_points")):
            sku_field_ok = False
            break
        if not isinstance(sku["selling_points"], list):
            sku_field_ok = False
            break
    total_score += add_item("Each SKU has required fields", 10 if sku_field_ok else 0, 10, sku_field_ok,
                            "All SKUs contain sku_id, sku_name, current_price, selling_points (list)" if sku_field_ok else "Missing fields in one or more SKUs")

    # 7. Prices correct (from current approved price book: PB-APAC-Q2-2026)
    expected_prices = {"LS-HS-001": 28.50, "LS-HS-002": 35.00, "LS-HS-003": 42.00}
    price_mismatch = False
    for sku in report["skus"]:
        sid = sku.get("sku_id")
        actual_price = sku.get("current_price")
        expected = expected_prices.get(sid)
        if expected is None:
            price_mismatch = True  # Should not happen if IDs correct
            break
        # Allow floating point tolerance (we expect exact float match)
        if actual_price != expected:
            price_mismatch = True
            break
    total_score += add_item("Prices match current price book", 30 if not price_mismatch else 0, 30, not price_mismatch,
                            "All prices correct" if not price_mismatch else "Price mismatch found")

    # 8. No extra brands/categories (only LuminaSkin Hydration Serum)
    # We already checked IDs; also verify SKU names relate to LuminaSkin (optional extra check)
    # Also ensure no DermVeil or AquaPulse SKUs
    extra_skus = [sku for sku in report["skus"] if sku.get("sku_id", "").startswith("DV-") or sku.get("sku_id", "").startswith("AP-")]
    no_extra = len(extra_skus) == 0
    total_score += add_item("No extra brands/categories", 10 if no_extra else 0, 10, no_extra,
                            "No foreign SKUs included" if no_extra else f"Found {len(extra_skus)} unwanted SKUs")

    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # Write results
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
