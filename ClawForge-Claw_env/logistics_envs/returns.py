from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_return_summary(return_item: dict[str, Any]) -> dict[str, Any]:
    return {
        "return_id": return_item["return_id"],
        "order_id": return_item["order_id"],
        "customer_id": return_item["customer_id"],
        "reason": return_item["reason"],
        "status": return_item["status"],
        "requested_at": return_item["requested_at"],
        "refund_amount": return_item["refund_amount"],
        "item_count": len(return_item.get("items", [])),
    }


def list_returns(
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

    for return_item in session["returns"]:
        if status_lower and return_item["status"].lower() != status_lower:
            continue
        if customer_id and return_item["customer_id"] != customer_id:
            continue

        searchable_text = " ".join(
            [
                return_item["return_id"],
                return_item["order_id"],
                return_item["reason"],
                return_item["status"],
            ]
        ).lower()
        if query_lower and query_lower not in searchable_text:
            continue
        results.append(build_return_summary(return_item))

    results.sort(key=lambda item: item["requested_at"], reverse=True)
    return results[:limit] if limit is not None else results


def get_return(session: dict[str, Any], return_id: str) -> dict[str, Any]:
    for return_item in session["returns"]:
        if return_item["return_id"] == return_id:
            return deepcopy(return_item)
    raise KeyError(f"Return not found: {return_id}")


def approve_return(
    session: dict[str, Any],
    return_id: str,
    event_at: str,
    action_index: int,
    notes: str | None = None,
) -> dict[str, Any]:
    for return_item in session["returns"]:
        if return_item["return_id"] == return_id:
            if return_item["status"] not in {"pending_review", "pending_inspection"}:
                raise ValueError(f"Return {return_id} cannot be approved in status: {return_item['status']}")

            return_item["status"] = "approved"
            return_item["approved_at"] = event_at
            return_item["last_action_index"] = action_index
            if notes:
                return_item["approval_notes"] = notes
            return deepcopy(return_item)
    raise KeyError(f"Return not found: {return_id}")


def reject_return(
    session: dict[str, Any],
    return_id: str,
    event_at: str,
    action_index: int,
    reason: str,
) -> dict[str, Any]:
    for return_item in session["returns"]:
        if return_item["return_id"] == return_id:
            if return_item["status"] not in {"pending_review", "pending_inspection"}:
                raise ValueError(f"Return {return_id} cannot be rejected in status: {return_item['status']}")

            return_item["status"] = "rejected"
            return_item["rejected_at"] = event_at
            return_item["rejection_reason"] = reason
            return_item["last_action_index"] = action_index
            return deepcopy(return_item)
    raise KeyError(f"Return not found: {return_id}")


def inspect_return(
    session: dict[str, Any],
    return_id: str,
    event_at: str,
    action_index: int,
    inspection_notes: str,
    resolution: str,
    condition: str = "acceptable",
) -> dict[str, Any]:
    valid_resolutions = {"refund", "partial_refund", "exchange", "store_credit", "rejected"}
    valid_conditions = {"new", "like_new", "used", "damaged"}

    resolution_lower = resolution.lower().strip()
    condition_lower = condition.lower().strip()

    if resolution_lower not in valid_resolutions:
        raise ValueError(f"Invalid resolution: {resolution}. Must be one of {valid_resolutions}")
    if condition_lower not in valid_conditions:
        raise ValueError(f"Invalid condition: {condition}. Must be one of {valid_conditions}")

    for return_item in session["returns"]:
        if return_item["return_id"] == return_id:
            if return_item["status"] not in {"pending_inspection", "approved"}:
                raise ValueError(f"Return {return_id} cannot be inspected in status: {return_item['status']}")

            return_item["status"] = "inspected"
            return_item["inspected_at"] = event_at
            return_item["inspection_notes"] = inspection_notes
            return_item["resolution"] = resolution_lower
            return_item["item_condition"] = condition_lower
            return_item["last_action_index"] = action_index
            return deepcopy(return_item)
    raise KeyError(f"Return not found: {return_id}")


def receive_return(
    session: dict[str, Any],
    return_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for return_item in session["returns"]:
        if return_item["return_id"] == return_id:
            if return_item["status"] != "approved":
                raise ValueError(f"Return {return_id} cannot be received in status: {return_item['status']}")

            return_item["status"] = "received"
            return_item["received_at"] = event_at
            return_item["last_action_index"] = action_index
            return deepcopy(return_item)
    raise KeyError(f"Return not found: {return_id}")
