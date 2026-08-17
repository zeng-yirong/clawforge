#!/usr/bin/env python3
"""Verify the result of wp_sku_competition_env__010 task."""

import json
import sys
import os
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. Check expected output file exists (10 pts)
    result_path = ws / "ops" / "lumina_pricing_snapshot.json"
    if result_path.is_file():
        details.append({
            "item": "Output file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/lumina_pricing_snapshot.json found"
        })
        total_score += 10
    else:
        details.append({
            "item": "Output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/lumina_pricing_snapshot.json not found"
        })
        # Cannot proceed without file
        _write_score(total_score, details, ws)
        return

    # 2. Parse JSON and check validity (10 pts)
    try:
        with open(result_path, "r") as f:
            content = json.load(f)
        details.append({
            "item": "Valid JSON array",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "Valid JSON array",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        _write_score(total_score, details, ws)
        return

    # 3. Must be a list (5 pts)
    if isinstance(content, list):
        details.append({
            "item": "Result is a list",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Output is a JSON list"
        })
        total_score += 5
    else:
        details.append({
            "item": "Result is a list",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Expected list, got {type(content).__name__}"
        })

    # 4. Each element must have fields: sku_id, sku_name, unit_price (15 pts)
    required_fields = {"sku_id", "sku_name", "unit_price"}
    field_ok = True
    for i, item in enumerate(content):
        if not isinstance(item, dict):
            field_ok = False
            break
        missing = required_fields - set(item.keys())
        if missing:
            field_ok = False
            break
    if field_ok:
        details.append({
            "item": "All entries contain required fields (sku_id, sku_name, unit_price)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"All {len(content)} entries have correct fields"
        })
        total_score += 15
    else:
        details.append({
            "item": "All entries contain required fields",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "Some entries missing required fields"
        })

    # 5. Only LuminaSkin SKUs, no ghosts, correct count (30 pts)
    # We need to determine the expected set from the built environment.
    # Reload SKU master and price book to compute ground truth.
    sku_path = ws / "data" / "skus" / "skus.json"
    pb_path = ws / "ops" / "pricing" / "price_books.json"
    try:
        with open(sku_path) as f:
            sku_data = json.load(f)["data"]
        with open(pb_path) as f:
            pb_data = json.load(f)["data"]
    except Exception as e:
        details.append({
            "item": "Load ground truth (env files)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Could not read environment data: {e}"
        })
        _write_score(total_score, details, ws)
        return

    # Build sku lookup: sku_id -> sku_name & brand_name
    sku_info = {}
    for s in sku_data:
        sku_info[s["sku_id"]] = {"sku_name": s["sku_name"], "brand_name": s["brand_name"]}

    # Find live price book
    live_book = None
    for pb in pb_data:
        if pb.get("is_current") and pb.get("status") == "approved":
            live_book = pb
            break
    if not live_book:
        details.append({
            "item": "Live price book (env data integrity)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "No live price book found in built data"
        })
        _write_score(total_score, details, ws)
        return

    # Build expected set: LuminaSkin skus that exist both in sku master and in live entries
    expected = {}  # sku_id -> {sku_name, unit_price}
    for entry in live_book["entries"]:
        sku_id = entry["sku_id"]
        if sku_id not in sku_info:
            continue  # ghost entry
        if sku_info[sku_id]["brand_name"] != "LuminaSkin":
            continue  # wrong brand
        expected[sku_id] = {
            "sku_name": sku_info[sku_id]["sku_name"],
            "unit_price": entry["unit_price"]
        }

    # Sort expected by unit_price descending
    expected_sorted = sorted(expected.items(), key=lambda x: x[1]["unit_price"], reverse=True)

    # Compare results
    result_map = {item["sku_id"]: item for item in content}
    result_ids = set(result_map.keys())
    expected_ids = set(expected.keys())

    # Check no extra skus
    extra = result_ids - expected_ids
    missing = expected_ids - result_ids

    correct_ids = (len(extra) == 0 and len(missing) == 0)
    if correct_ids:
        id_score = 30
        reason = f"SKU set matches exactly: {len(expected_ids)} LuminaSkin SKUs, no extras, no missing"
    else:
        deductions = 0
        if extra:
            deductions += len(extra) * 5
        if missing:
            deductions += len(missing) * 5
        id_score = max(0, 30 - deductions)
        reason_parts = []
        if extra:
            reason_parts.append(f"extra SKUs: {sorted(extra)}")
        if missing:
            reason_parts.append(f"missing SKUs: {sorted(missing)}")
        reason = "; ".join(reason_parts)

    details.append({
        "item": "Correct set of LuminaSkin SKUs (no ghost, no other brand)",
        "score": id_score,
        "max_score": 30,
        "passed": id_score == 30,
        "reason": reason
    })
    total_score += id_score

    # 6. Prices and ordering (30 pts)
    # Check each entry price matches expected, and order is descending
    order_ok = True
    price_ok = True
    # Compare using the expected sorted list
    if len(content) == len(expected_sorted):
        for i, (expected_id, expected_info) in enumerate(expected_sorted):
            actual = content[i]
            if actual["sku_id"] != expected_id:
                order_ok = False
            if actual.get("unit_price") != expected_info["unit_price"]:
                price_ok = False
    else:
        # If count mismatched, we can't match positions; partial credit
        order_ok = False
        price_ok = False

    # Score: 15 for order, 15 for price accuracy
    order_score = 15 if order_ok else 0
    price_score = 15 if price_ok else 0
    if not order_ok:
        # Provide partial: check if ids are sorted by price descending irrespective of position?
        # For simplicity, strict matching required
        reason_order = "Result order does not match descending unit_price from the live price book"
    else:
        reason_order = "Entries are sorted by unit_price descending correctly"

    if not price_ok:
        reason_price = "One or more unit_price values differ from the live price book"
    else:
        reason_price = "All unit_price values match the live price book"

    details.append({
        "item": "Entries sorted by unit_price descending",
        "score": order_score,
        "max_score": 15,
        "passed": order_ok,
        "reason": reason_order
    })
    total_score += order_score

    details.append({
        "item": "unit_price matches live price book",
        "score": price_score,
        "max_score": 15,
        "passed": price_ok,
        "reason": reason_price
    })
    total_score += price_score

    # Ensure total_score is integer
    total_score = max(0, min(100, total_score))
    _write_score(total_score, details, ws)

def _write_score(total_score, details, ws):
    out = {
        "total_score": total_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
