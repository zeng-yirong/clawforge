from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_shipment_summary(shipment: dict[str, Any]) -> dict[str, Any]:
    return {
        "shipment_id": shipment["shipment_id"],
        "order_id": shipment["order_id"],
        "carrier": shipment["carrier"],
        "tracking_number": shipment["tracking_number"],
        "status": shipment["status"],
        "current_location": shipment.get("current_location"),
        "shipped_at": shipment.get("shipped_at"),
        "delivered_at": shipment.get("delivered_at"),
    }


def list_shipments(
    session: dict[str, Any],
    *,
    query: str = "",
    status: str | None = None,
    carrier: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    status_lower = status.strip().lower() if status else None
    carrier_lower = carrier.strip().lower() if carrier else None
    results = []

    for shipment in session["shipments"]:
        if status_lower and shipment["status"].lower() != status_lower:
            continue
        if carrier_lower and shipment["carrier"].lower() != carrier_lower:
            continue

        searchable_text = " ".join(
            [
                shipment["shipment_id"],
                shipment["order_id"],
                shipment["carrier"],
                shipment["tracking_number"],
                shipment["status"],
            ]
        ).lower()
        if query_lower and query_lower not in searchable_text:
            continue
        results.append(build_shipment_summary(shipment))

    results.sort(key=lambda item: item.get("shipped_at") or "", reverse=True)
    return results[:limit] if limit is not None else results


def get_shipment(session: dict[str, Any], shipment_id: str) -> dict[str, Any]:
    for shipment in session["shipments"]:
        if shipment["shipment_id"] == shipment_id:
            return deepcopy(shipment)
    raise KeyError(f"Shipment not found: {shipment_id}")


def update_shipment_status(
    session: dict[str, Any],
    shipment_id: str,
    new_status: str,
    event_at: str,
    action_index: int,
    tracking_number: str | None = None,
    current_location: str | None = None,
) -> dict[str, Any]:
    valid_statuses = {
        "processing", "shipped", "in_transit", "out_for_delivery",
        "delivered", "exception", "returned"
    }
    new_status_lower = new_status.lower().strip()
    if new_status_lower not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}. Must be one of {valid_statuses}")

    for shipment in session["shipments"]:
        if shipment["shipment_id"] == shipment_id:
            shipment["status"] = new_status_lower
            if tracking_number:
                shipment["tracking_number"] = tracking_number
            if current_location:
                shipment["current_location"] = current_location
            if new_status_lower == "shipped" and not shipment.get("shipped_at"):
                shipment["shipped_at"] = event_at
            if new_status_lower == "delivered" and not shipment.get("delivered_at"):
                shipment["delivered_at"] = event_at
            shipment["last_action_index"] = action_index

            new_event = {
                "timestamp": event_at,
                "status": new_status_lower.replace("_", " ").title(),
                "location": current_location or shipment.get("current_location", "Unknown"),
            }
            shipment.setdefault("events", []).append(new_event)

            return deepcopy(shipment)
    raise KeyError(f"Shipment not found: {shipment_id}")
