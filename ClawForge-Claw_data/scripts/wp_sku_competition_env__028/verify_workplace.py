import json
import os
import sys
from collections.abc import Mapping

def verify(workspace):
    details = []
    score_total = 0
    MAX_TOTAL = 100

    # Helper to add detail
    def add_detail(item, score, max_score, reason):
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": score >= max_score,
            "reason": reason
        })
        return score

    # 1. File exists (5 pts)
    report_path = os.path.join(workspace, "ops", "lumina_sku_report.json")
    file_exists = os.path.isfile(report_path)
    score_total += add_detail("File ops/lumina_sku_report.json exists", 5 if file_exists else 0, 5,
                              "File found" if file_exists else "File missing")

    if not file_exists:
        # Cannot proceed further
        final_score = score_total
        write_score(final_score, details)
        return

    # 2. JSON valid (5 pts)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        score_total += add_detail("Valid JSON", 5, 5, "Parsed successfully")
    except (json.JSONDecodeError, Exception) as e:
        score_total += add_detail("Valid JSON", 0, 5, f"Invalid JSON: {e}")
        final_score = score_total
        write_score(final_score, details)
        return

    # Expected active LuminaSkin SKUs and their prices
    expected_active = {
        "LS-HY-100": 49.99,
        "LS-UV-50":  39.99,
        "LS-HY-30":  29.99
    }
    expected_categories = {"Hydration Serum", "UV Moisturizer"}

    # 3. Structure: top-level should be an object with categories as keys (15 pts)
    structure_ok = isinstance(report, Mapping) and len(report) > 0
    if structure_ok:
        cat_keys = set(report.keys())
        if cat_keys == expected_categories:
            score_total += add_detail("Top-level grouped by category", 15, 15,
                                      "Exactly two correct category keys")
        elif cat_keys:
            # partial match – still useful, but lower score
            overlap = cat_keys & expected_categories
            partial = len(overlap) / len(expected_categories)
            pts = round(15 * partial)
            score_total += add_detail("Top-level grouped by category (partial)", pts, 15,
                                      f"Found categories {cat_keys}, expected {expected_categories}")
        else:
            score_total += add_detail("Top-level grouped by category", 0, 15,
                                      "Empty object")
    else:
        # could be a list or other; we'll treat as ungrouped
        score_total += add_detail("Top-level grouped by category", 0, 15,
                                  "Top-level is not an object (expected category grouping)")

    # Helper to iterate over all SKU records in report
    def iter_records(report_obj):
        if isinstance(report_obj, Mapping):
            for cat, sku_list in report_obj.items():
                if isinstance(sku_list, list):
                    for rec in sku_list:
                        yield rec
        elif isinstance(report_obj, list):
            for rec in report_obj:
                yield rec

    records = list(iter_records(report))

    # 4. Includes all active LuminaSkin SKUs (20 pts)
    found_skus = set()
    for rec in records:
        sku_id = rec.get("sku_id")
        if sku_id in expected_active:
            found_skus.add(sku_id)
    all_found = len(found_skus) == len(expected_active)
    missing = set(expected_active.keys()) - found_skus
    if all_found:
        score_total += add_detail("All active LuminaSkin SKUs present", 20, 20,
                                  "LS-HY-100, LS-UV-50, LS-HY-30 all found")
    else:
        pts = max(0, 20 - len(missing) * 7)
        score_total += add_detail("All active LuminaSkin SKUs present", pts, 20,
                                  f"Missing: {missing}")

    # 5. No extra/discontinued/other brand SKUs (5 pts)
    all_valid_ids = set(expected_active.keys())
    extra_skus = [rec.get("sku_id") for rec in records if rec.get("sku_id") not in all_valid_ids]
    if not extra_skus:
        score_total += add_detail("No invalid SKUs present", 5, 5, "All SKUs are valid active LuminaSkin")
    else:
        score_total += add_detail("No invalid SKUs present", max(0, 5 - len(extra_skus)*5), 5,
                                  f"Extra SKUs found: {extra_skus}")

    # 6. Field completeness (15 pts)
    required_fields = {"sku_id", "sku_name", "category_name", "selling_points", "ingredients", "price"}
    total_field_issues = 0
    field_check_items = []
    for rec in records:
        missing_fields = required_fields - set(rec.keys())
        if missing_fields:
            total_field_issues += len(missing_fields)
            field_check_items.append(f"{rec.get('sku_id','?')} missing {missing_fields}")
    max_field_pts = 15
    if total_field_issues == 0:
        score_total += add_detail("All records have required fields", max_field_pts, max_field_pts,
                                  "All 6 fields present on every record")
    else:
        penalty = min(max_field_pts, total_field_issues * 2)
        score_total += add_detail("All records have required fields", max_field_pts - penalty, max_field_pts,
                                  f"Issues: {field_check_items}")

    # 7. Correct prices (20 pts)
    price_errors = []
    for rec in records:
        sku_id = rec.get("sku_id")
        if sku_id in expected_active:
            expected_price = expected_active[sku_id]
            actual_price = rec.get("price")
            if actual_price is None or abs(actual_price - expected_price) > 0.005:
                price_errors.append(f"{sku_id}: expected {expected_price}, got {actual_price}")
    if not price_errors:
        score_total += add_detail("Prices match APAC-Q2-2026-LIVE", 20, 20,
                                  "All prices correct")
    else:
        pts = max(0, 20 - len(price_errors) * 7)
        score_total += add_detail("Prices match APAC-Q2-2026-LIVE", pts, 20,
                                  f"Errors: {price_errors}")

    # 8. Category grouping accuracy (15 pts)
    grouping_issues = []
    if isinstance(report, Mapping):
        for cat, sku_list in report.items():
            if not isinstance(sku_list, list):
                continue
            for rec in sku_list:
                rec_cat = rec.get("category_name")
                if rec_cat != cat:
                    grouping_issues.append(f"SKU {rec.get('sku_id')} has category '{rec_cat}' but placed under '{cat}'")
    if not grouping_issues:
        score_total += add_detail("Category grouping accurate", 15, 15, "All SKUs placed under correct category key")
    else:
        pts = max(0, 15 - len(grouping_issues) * 5)
        score_total += add_detail("Category grouping accurate", pts, 15,
                                  f"Issues: {grouping_issues}")

    # Cap at 100
    final_score = min(score_total, MAX_TOTAL)
    write_score(final_score, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
