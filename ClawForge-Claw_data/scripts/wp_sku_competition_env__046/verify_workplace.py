#!/usr/bin/env python3
"""
Verifier for wp_sku_competition_env__046 (LuminaSkin competitor report).
Checks that the agent produced ops/competitor_report.json with correct fields,
only active LuminaSkin SKUs, correct prices from the current price book,
selling_points truncated to 2, ingredients truncated to 3.
No extra SKUs from other brands or non-active state.
Scoring: directory 10, schema 10, filtering 30, pricing 30, truncation 20.
Total 100.
"""
import json
import os
import sys
import re

def verify(workspace):
    details = []
    score = 0

    # ---------- 1. Directory existence ----------
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({"item": "ops/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/ directory."})
        score += 10
    else:
        details.append({"item": "ops/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory not found."})
        # 如果目录都不存在，后面无法检查文件，直接返回
        return details, score

    # ---------- 2. Report file existence and schema ----------
    report_path = os.path.join(ops_path, "competitor_report.json")
    if not os.path.isfile(report_path):
        details.append({"item": "competitor_report.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})
        # 文件不存在则停止
        return details, score
    details.append({"item": "competitor_report.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
    score += 10

    try:
        with open(report_path, "r") as f:
            content = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        return details, score

    # Check it's a list (or dict with expected wrapper? We accept either.)
    if isinstance(content, dict):
        # If it has a wrapper key like "report" or "skus", use that; else treat as single object
        # We'll accept both: a list or a dict with a list under a known key.
        if "skus" in content:
            report_list = content["skus"]
        elif "report" in content:
            report_list = content["report"]
        else:
            report_list = [content]  # maybe single item
    elif isinstance(content, list):
        report_list = content
    else:
        details.append({"item": "Root structure", "score": 0, "max_score": 10, "passed": False, "reason": "Root must be list or dict with list."})
        return details, score

    # Validate each entry has required fields
    required_fields = ["sku_id", "sku_name", "price", "selling_points", "ingredients"]
    for i, entry in enumerate(report_list):
        missing = [f for f in required_fields if f not in entry]
        if missing:
            details.append({"item": f"Entry {i} has all required fields", "score": 0, "max_score": 10, "passed": False,
                            "reason": f"Missing fields: {missing}"})
            # 虽然失败，但仍继续，但不再加分
        else:
            # 我们继续累积，但只在最后给schema分
            pass

    # 如果所有条目都有所需字段，给分
    all_have_fields = all(
        all(f in entry for f in required_fields) for entry in report_list
    )
    if all_have_fields and len(report_list) > 0:
        details.append({"item": "All entries have required fields", "score": 10, "max_score": 10, "passed": True, "reason": "Schema valid."})
        score += 10
    elif len(report_list) == 0:
        details.append({"item": "All entries have required fields", "score": 0, "max_score": 10, "passed": False, "reason": "No entries found."})
    else:
        details.append({"item": "All entries have required fields", "score": 0, "max_score": 10, "passed": False, "reason": "Some entries missing fields."})

    # ---------- 3. Filtering correctness ----------
    # Expected: only LS-1001 and LS-1002 (active LuminaSkin)
    expected_sku_ids = {"LS-1001", "LS-1002"}
    actual_sku_ids = {entry.get("sku_id", "") for entry in report_list}
    # Check no extra (other brands, discontinued)
    extra = actual_sku_ids - expected_sku_ids
    missing = expected_sku_ids - actual_sku_ids
    if extra:
        details.append({"item": "No extra SKUs", "score": 0, "max_score": 30, "passed": False,
                        "reason": f"Found unexpected SKU IDs: {extra}"})
    elif missing:
        details.append({"item": "No extra SKUs", "score": 0, "max_score": 30, "passed": False,
                        "reason": f"Missing expected SKU IDs: {missing}"})
    else:
        details.append({"item": "Correct filtering (only active LuminaSkin)", "score": 30, "max_score": 30, "passed": True,
                        "reason": "Exactly LS-1001 and LS-1002 present."})
        score += 30

    # ---------- 4. Pricing correctness ----------
    # Current price book: pb_apac_q2_live, entries: LS-1001=49.90, LS-1002=42.50
    expected_prices = {"LS-1001": 49.90, "LS-1002": 42.50}
    price_ok = True
    for entry in report_list:
        sku = entry.get("sku_id")
        price = entry.get("price")
        if sku in expected_prices:
            # Allow small floating tolerance (0.001)
            if abs(price - expected_prices[sku]) > 0.001:
                price_ok = False
                details.append({"item": f"Price for {sku}", "score": 0, "max_score": 30, "passed": False,
                                "reason": f"Expected {expected_prices[sku]}, got {price}"})
                break
    if price_ok and actual_sku_ids == expected_sku_ids:
        details.append({"item": "Prices correct from current price book", "score": 30, "max_score": 30, "passed": True,
                        "reason": "All prices match approved Q2 price book."})
        score += 30
    else:
        # 如果没有给过price detail，给0分
        already_scored = any("Price for" in d["item"] for d in details)
        if not already_scored:
            details.append({"item": "Prices correct from current price book", "score": 0, "max_score": 30, "passed": False,
                            "reason": "Price mismatch or missing SKUs."})

    # ---------- 5. Truncation correctness ----------
    # selling_points: first 2, ingredients: first 3
    trunc_ok = True
    # We know the original selling_points lists:
    # LS-1001: ["Boost hydration by 200%", "Lightweight gel texture", "Non-comedogenic"]
    # LS-1002: ["Broad spectrum UVA/UVB", "Water resistant 80min", "Matte finish"]
    # After truncation: first 2
    expected_sp = {
        "LS-1001": ["Boost hydration by 200%", "Lightweight gel texture"],
        "LS-1002": ["Broad spectrum UVA/UVB", "Water resistant 80min"]
    }
    expected_ing = {
        "LS-1001": ["Hyaluronic Acid", "Niacinamide", "Glycerin"],  # first 3
        "LS-1002": ["Zinc Oxide", "Titanium Dioxide", "Vitamin E"]
    }
    for entry in report_list:
        sku = entry.get("sku_id")
        if sku in expected_sp:
            sp = entry.get("selling_points", [])
            if len(sp) != 2 or sp != expected_sp[sku]:
                trunc_ok = False
                details.append({"item": f"Selling points truncation for {sku}", "score": 0, "max_score": 10, "passed": False,
                                "reason": f"Expected {expected_sp[sku]}, got {sp}"})
                break
        ing = entry.get("ingredients", [])
        if sku in expected_ing:
            if len(ing) != 3 or ing != expected_ing[sku]:
                trunc_ok = False
                details.append({"item": f"Ingredients truncation for {sku}", "score": 0, "max_score": 10, "passed": False,
                                "reason": f"Expected {expected_ing[sku]}, got {ing}"})
                break
    if trunc_ok and actual_sku_ids == expected_sku_ids:
        details.append({"item": "Selling points truncated to first 2", "score": 10, "max_score": 10, "passed": True,
                        "reason": "Correct truncation."})
        details.append({"item": "Ingredients truncated to first 3", "score": 10, "max_score": 10, "passed": True,
                        "reason": "Correct truncation."})
        score += 20  # 10+10
    else:
        # 如果没有给过detail，补0分
        if not any("truncation" in d["item"].lower() for d in details):
            details.append({"item": "Selling points truncation", "score": 0, "max_score": 10, "passed": False,
                            "reason": "Truncation not verified or mismatch."})
            details.append({"item": "Ingredients truncation", "score": 0, "max_score": 10, "passed": False,
                            "reason": "Truncation not verified or mismatch."})

    # 修剪details避免重复
    # 如果总分超过100，截断到100
    final_score = min(score, 100)
    return details, final_score


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details, total = verify(workspace)
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/100")

if __name__ == "__main__":
    main()
