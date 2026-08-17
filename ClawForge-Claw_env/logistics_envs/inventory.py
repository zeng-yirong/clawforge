from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_inventory_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "sku": item["sku"],
        "name": item["name"],
        "category": item["category"],
        "stock_level": item["stock_level"],
        "reserved": item["reserved"],
        "available": item["available"],
        "reorder_point": item["reorder_point"],
        "warehouse_id": item["warehouse_id"],
        "needs_reorder": item["available"] <= item["reorder_point"],
    }


def list_inventory(
    session: dict[str, Any],
    *,
    query: str = "",
    category: str | None = None,
    warehouse_id: str | None = None,
    low_stock_only: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    category_lower = category.strip().lower() if category else None
    results = []

    for item in session["inventory"]:
        if category_lower and item["category"].lower() != category_lower:
            continue
        if warehouse_id and item["warehouse_id"] != warehouse_id:
            continue
        if low_stock_only and item["available"] > item["reorder_point"]:
            continue

        searchable_text = " ".join(
            [
                item["sku"],
                item["name"],
                item["category"],
            ]
        ).lower()
        if query_lower and query_lower not in searchable_text:
            continue
        results.append(build_inventory_summary(item))

    results.sort(key=lambda item: item["sku"])
    return results[:limit] if limit is not None else results


def get_inventory_item(session: dict[str, Any], sku: str) -> dict[str, Any]:
    for item in session["inventory"]:
        if item["sku"] == sku:
            return deepcopy(item)
    raise KeyError(f"Inventory item not found: {sku}")


def adjust_inventory(
    session: dict[str, Any],
    sku: str,
    warehouse_id: str,
    quantity_change: int,
    reason_code: str,
    event_at: str,
    action_index: int,
    notes: str | None = None,
) -> dict[str, Any]:
    valid_reason_codes = {
        "DAMAGE", "THEFT", "EXPIRED", "INTERNAL_USE",
        "SYSTEM_CORRECTION", "RECOUNT", "RETURN_DAMAGED"
    }
    reason_code_upper = reason_code.upper().strip()
    if reason_code_upper not in valid_reason_codes:
        raise ValueError(f"Invalid reason code: {reason_code}. Must be one of {valid_reason_codes}")

    for item in session["inventory"]:
        if item["sku"] == sku and item["warehouse_id"] == warehouse_id:
            new_stock_level = item["stock_level"] + quantity_change
            if new_stock_level < 0:
                raise ValueError(
                    f"Adjustment would result in negative stock level. Current: {item['stock_level']}, Change: {quantity_change}"
                )

            item["stock_level"] = new_stock_level
            item["available"] = item["stock_level"] - item["reserved"]
            item["last_action_index"] = action_index
            item["last_adjustment"] = {
                "timestamp": event_at,
                "quantity_change": quantity_change,
                "reason_code": reason_code_upper,
                "notes": notes,
            }

            adjustment_record = {
                "sku": sku,
                "warehouse_id": warehouse_id,
                "quantity_change": quantity_change,
                "reason_code": reason_code_upper,
                "timestamp": event_at,
                "action_index": action_index,
                "notes": notes,
            }
            session.setdefault("inventory_adjustments", []).append(adjustment_record)

            return deepcopy(item)
    raise KeyError(f"Inventory item not found: SKU={sku}, Warehouse={warehouse_id}")


def reserve_inventory(
    session: dict[str, Any],
    sku: str,
    warehouse_id: str,
    quantity: int,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for item in session["inventory"]:
        if item["sku"] == sku and item["warehouse_id"] == warehouse_id:
            if item["available"] < quantity:
                raise ValueError(
                    f"Insufficient available inventory. Available: {item['available']}, Requested: {quantity}"
                )

            item["reserved"] += quantity
            item["available"] = item["stock_level"] - item["reserved"]
            item["last_action_index"] = action_index

            reservation_record = {
                "sku": sku,
                "warehouse_id": warehouse_id,
                "quantity": quantity,
                "timestamp": event_at,
                "action_index": action_index,
            }
            session.setdefault("inventory_reservations", []).append(reservation_record)

            return deepcopy(item)
    raise KeyError(f"Inventory item not found: SKU={sku}, Warehouse={warehouse_id}")


def generate_reconciliation_report(
    session: dict[str, Any],
    warehouse_id: str | None = None,
) -> dict[str, Any]:
    items_to_reconcile = session["inventory"]
    if warehouse_id:
        items_to_reconcile = [item for item in items_to_reconcile if item["warehouse_id"] == warehouse_id]

    low_stock_items = [item for item in items_to_reconcile if item["available"] <= item["reorder_point"]]
    adjustments = session.get("inventory_adjustments", [])

    total_discrepancy_value = 0.0
    for adjustment in adjustments:
        for item in session["inventory"]:
            if item["sku"] == adjustment["sku"]:
                total_discrepancy_value += abs(adjustment["quantity_change"]) * item["unit_cost"]
                break

    report = {
        "report_type": "inventory_reconciliation",
        "generated_at": "2026-06-16T10:00:00+00:00",
        "warehouse_filter": warehouse_id,
        "total_items": len(items_to_reconcile),
        "low_stock_count": len(low_stock_items),
        "low_stock_items": [
            {"sku": item["sku"], "name": item["name"], "available": item["available"], "reorder_point": item["reorder_point"]}
            for item in low_stock_items
        ],
        "total_adjustments": len(adjustments),
        "total_discrepancy_value": round(total_discrepancy_value, 2),
        "adjustments_by_reason": _summarize_adjustments_by_reason(adjustments),
    }
    session.setdefault("reports", []).append(report)
    return report


def _summarize_adjustments_by_reason(adjustments: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for adj in adjustments:
        reason = adj.get("reason_code", "UNKNOWN")
        summary[reason] = summary.get(reason, 0) + 1
    return summary
