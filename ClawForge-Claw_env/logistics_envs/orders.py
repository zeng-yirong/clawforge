from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_order_summary(order: dict[str, Any]) -> dict[str, Any]:
    return {
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "status": order["status"],
        "created_at": order["created_at"],
        "total_amount": order["total_amount"],
        "item_count": len(order.get("items", [])),
        "warehouse_id": order.get("warehouse_id"),
    }


def list_orders(
    session: dict[str, Any],
    *,
    query: str = "",
    status: str | None = None,
    customer_id: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    status_lower = status.strip().lower() if status else None
    results = []

    for order in session["orders"]:
        if status_lower and order["status"].lower() != status_lower:
            continue
        if customer_id and order["customer_id"] != customer_id:
            continue

        searchable_text = " ".join(
            [
                order["order_id"],
                order["status"],
                str(order["total_amount"]),
                " ".join(item["name"] for item in order.get("items", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable_text:
            continue
        results.append(build_order_summary(order))

    results.sort(key=lambda item: item["created_at"], reverse=True)
    return results[:limit] if limit is not None else results


def get_order(session: dict[str, Any], order_id: str) -> dict[str, Any]:
    for order in session["orders"]:
        if order["order_id"] == order_id:
            return deepcopy(order)
    raise KeyError(f"Order not found: {order_id}")


def update_order_status(
    session: dict[str, Any],
    order_id: str,
    new_status: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    valid_statuses = {
        "pending", "processing", "shipped", "in_transit",
        "out_for_delivery", "delivered", "cancelled", "returned"
    }
    new_status_lower = new_status.lower().strip()
    if new_status_lower not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}. Must be one of {valid_statuses}")

    for order in session["orders"]:
        if order["order_id"] == order_id:
            order["status"] = new_status_lower
            order["updated_at"] = event_at
            order["last_action_index"] = action_index
            return deepcopy(order)
    raise KeyError(f"Order not found: {order_id}")
