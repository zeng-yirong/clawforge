from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .evaluator import evaluate_session
from .inventory import (
    adjust_inventory,
    generate_reconciliation_report,
    get_inventory_item,
    list_inventory,
    reserve_inventory,
)
from .orders import get_order, list_orders, update_order_status
from .repository import DatasetRepository
from .returns import (
    approve_return,
    get_return,
    inspect_return,
    list_returns,
    receive_return,
    reject_return,
)
from .shipments import get_shipment, list_shipments, update_shipment_status
from .store import SessionStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class LogisticsEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("LOGISTICS_STATE_ROOT", Path.cwd() / ".logistics_state"))
        self.repository = DatasetRepository(data_root)
        self.store = SessionStore(state_root or default_state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()
        self.warehouses = self.repository.load_warehouses()

    def list_scenarios(self) -> dict[str, Any]:
        return {
            "scenarios": [
                {
                    "scenario_id": item["scenario_id"],
                    "title": item["title"],
                    "task_prompt": item["task_prompt"],
                }
                for item in self.repository.list_scenarios()
            ]
        }

    def create_session(self, session_id: str, scenario_id: str, overwrite: bool = False) -> dict[str, Any]:
        scenario = self.repository.load_scenario(scenario_id)
        session_payload = self._build_session_payload(session_id=session_id, scenario=scenario)
        self.store.create_session(session_id, session_payload, overwrite=overwrite)
        return self.session_summary(session_id)

    def reset_session(self, session_id: str) -> dict[str, Any]:
        existing = self.store.load_session(session_id)
        return self.create_session(session_id, existing["scenario_id"], overwrite=True)

    def get_task(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
            "pending_returns_count": sum(1 for r in session["returns"] if r["status"] in {"pending_review", "pending_inspection"}),
        }

    def list_orders(
        self,
        session_id: str,
        *,
        query: str = "",
        status: str | None = None,
        customer_id: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_orders(
                session,
                query=query,
                status=status,
                customer_id=customer_id,
                limit=limit,
            ),
        }

    def get_order(self, session_id: str, order_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_order(session, order_id)}

    def update_order_status(self, session_id: str, order_id: str, new_status: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = update_order_status(session, order_id, new_status, event_at, action_index)
            self._record_action(session, action_index, event_at, "update_order_status", {"order_id": order_id, "new_status": new_status})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_shipments(
        self,
        session_id: str,
        *,
        query: str = "",
        status: str | None = None,
        carrier: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_shipments(
                session,
                query=query,
                status=status,
                carrier=carrier,
                limit=limit,
            ),
        }

    def get_shipment(self, session_id: str, shipment_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_shipment(session, shipment_id)}

    def update_shipment_status(
        self,
        session_id: str,
        shipment_id: str,
        new_status: str,
        tracking_number: str | None = None,
        current_location: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = update_shipment_status(
                session, shipment_id, new_status, event_at, action_index,
                tracking_number=tracking_number, current_location=current_location
            )
            self._record_action(session, action_index, event_at, "update_shipment_status", {"shipment_id": shipment_id, "new_status": new_status})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_returns(
        self,
        session_id: str,
        *,
        query: str = "",
        status: str | None = None,
        customer_id: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_returns(
                session,
                query=query,
                status=status,
                customer_id=customer_id,
                limit=limit,
            ),
        }

    def get_return(self, session_id: str, return_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_return(session, return_id)}

    def approve_return(self, session_id: str, return_id: str, notes: str | None = None) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = approve_return(session, return_id, event_at, action_index, notes=notes)
            self._record_action(session, action_index, event_at, "approve_return", {"return_id": return_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def reject_return(self, session_id: str, return_id: str, reason: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = reject_return(session, return_id, event_at, action_index, reason=reason)
            self._record_action(session, action_index, event_at, "reject_return", {"return_id": return_id, "reason": reason})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def inspect_return(
        self,
        session_id: str,
        return_id: str,
        inspection_notes: str,
        resolution: str,
        condition: str = "acceptable",
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = inspect_return(
                session, return_id, event_at, action_index,
                inspection_notes=inspection_notes, resolution=resolution, condition=condition
            )
            self._record_action(session, action_index, event_at, "inspect_return", {"return_id": return_id, "resolution": resolution})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def receive_return(self, session_id: str, return_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = receive_return(session, return_id, event_at, action_index)
            self._record_action(session, action_index, event_at, "receive_return", {"return_id": return_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_inventory(
        self,
        session_id: str,
        *,
        query: str = "",
        category: str | None = None,
        warehouse_id: str | None = None,
        low_stock_only: bool = False,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_inventory(
                session,
                query=query,
                category=category,
                warehouse_id=warehouse_id,
                low_stock_only=low_stock_only,
                limit=limit,
            ),
        }

    def get_inventory_item(self, session_id: str, sku: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_inventory_item(session, sku)}

    def adjust_inventory(
        self,
        session_id: str,
        sku: str,
        warehouse_id: str,
        quantity_change: int,
        reason_code: str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = adjust_inventory(
                session, sku, warehouse_id, quantity_change, reason_code, event_at, action_index, notes=notes
            )
            self._record_action(
                session, action_index, event_at, "adjust_inventory",
                {"sku": sku, "warehouse_id": warehouse_id, "quantity_change": quantity_change, "reason_code": reason_code}
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def reserve_inventory(
        self,
        session_id: str,
        sku: str,
        warehouse_id: str,
        quantity: int,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = reserve_inventory(session, sku, warehouse_id, quantity, event_at, action_index)
            self._record_action(session, action_index, event_at, "reserve_inventory", {"sku": sku, "warehouse_id": warehouse_id, "quantity": quantity})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def generate_reconciliation_report(self, session_id: str, warehouse_id: str | None = None) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            payload = generate_reconciliation_report(session, warehouse_id=warehouse_id)
            self._record_action(session, 0, _utc_now_iso(), "generate_reconciliation_report", {"warehouse_id": warehouse_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def read_attachment(self, session_id: str, attachment_id: str) -> dict[str, Any]:
        attachment_meta = self._find_attachment_metadata(session_id, attachment_id)
        content = self.repository.read_attachment(attachment_meta["relative_path"])
        return {
            "session_id": session_id,
            "data": {
                "attachment_id": attachment_id,
                "file_name": attachment_meta["file_name"],
                "content": content,
            }
        }

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "pending_returns_count": sum(1 for r in session["returns"] if r["status"] in {"pending_review", "pending_inspection"}),
            "pending_shipments_count": sum(1 for s in session["shipments"] if s["status"] in {"processing", "in_transit"}),
            "low_stock_items_count": sum(1 for i in session["inventory"] if i["available"] <= i["reorder_point"]),
            "action_count": len(session.get("actions", [])),
            "adjustments_count": len(session.get("inventory_adjustments", [])),
            "reports_count": len(session.get("reports", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_orders = self.repository.load_orders()
        all_shipments = self.repository.load_shipments()
        all_returns = self.repository.load_returns()
        all_inventory = self.repository.load_inventory()

        orders = [self._hydrate_order(all_orders[oid]) for oid in scenario["order_ids"] if oid in all_orders]
        shipments = [self._hydrate_shipment(all_shipments[sid]) for sid in scenario["shipment_ids"] if sid in all_shipments]
        returns = [self._hydrate_return(all_returns[rid]) for rid in scenario["return_ids"] if rid in all_returns]
        inventory = [self._hydrate_inventory(all_inventory[sku]) for sku in all_inventory]

        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": _utc_now_iso(),
            "meta": {
                "base_time": scenario["current_time"],
                "action_index": 0,
            },
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "orders": orders,
            "shipments": shipments,
            "returns": returns,
            "inventory": inventory,
            "actions": [],
            "inventory_adjustments": [],
            "inventory_reservations": [],
            "reports": [],
        }

    def _hydrate_order(self, order: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(order)
        customer = deepcopy(self.contacts.get(hydrated["customer_id"], {}))
        hydrated["customer"] = {
            "contact_id": customer.get("contact_id"),
            "name": customer.get("name"),
            "email": customer.get("email"),
        }
        hydrated["last_action_index"] = None
        return hydrated

    def _hydrate_shipment(self, shipment: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(shipment)
        hydrated["last_action_index"] = None
        return hydrated

    def _hydrate_return(self, return_item: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(return_item)
        hydrated["last_action_index"] = None
        return hydrated

    def _hydrate_inventory(self, item: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(item)
        hydrated["last_action_index"] = None
        hydrated["last_adjustment"] = None
        return hydrated

    def _find_attachment_metadata(self, session_id: str, attachment_id: str) -> dict[str, Any]:
        attachment_map = {
            "att_return_policy": {"relative_path": "att_return_policy.md", "file_name": "Return Policy.md"},
            "att_inventory_adjustment_guide": {"relative_path": "att_inventory_adjustment_guide.md", "file_name": "Inventory Adjustment Guide.md"},
            "att_shipment_tracking_guide": {"relative_path": "att_shipment_tracking_guide.md", "file_name": "Shipment Tracking Guide.md"},
        }
        if attachment_id not in attachment_map:
            raise KeyError(f"Attachment not found: {attachment_id}")
        return attachment_map[attachment_id]

    def _next_event(self, session: dict[str, Any]) -> tuple[str, int]:
        action_index = int(session["meta"]["action_index"]) + 1
        session["meta"]["action_index"] = action_index
        event_at = (_coerce_iso_datetime(session["meta"]["base_time"]) + timedelta(minutes=action_index)).isoformat()
        return event_at, action_index

    def _record_action(
        self,
        session: dict[str, Any],
        action_index: int,
        event_at: str,
        action_type: str,
        details: dict[str, Any],
    ) -> None:
        session["actions"].append(
            {
                "action_index": action_index,
                "timestamp": event_at,
                "action_type": action_type,
                "details": details,
            }
        )
