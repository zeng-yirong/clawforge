from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class DatasetRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent / "data"
        self.data_root = base_root.resolve()
        self.orders_dir = self.data_root / "orders"
        self.shipments_dir = self.data_root / "shipments"
        self.returns_dir = self.data_root / "returns"
        self.inventory_dir = self.data_root / "inventory"
        self.warehouses_file = self.data_root / "warehouses.json"
        self.accounts_file = self.data_root / "accounts.json"
        self.contacts_file = self.data_root / "contacts.json"
        self.attachment_dir = self.data_root / "attachments"
        self.scenario_dir = self.data_root / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_warehouses(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.warehouses_file)
        return {item["warehouse_id"]: item for item in payload["warehouses"]}

    def load_orders(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.orders_dir / "orders.json")
        return {item["order_id"]: item for item in payload["orders"]}

    def load_order(self, order_id: str) -> dict[str, Any]:
        all_orders = self.load_orders()
        if order_id not in all_orders:
            raise KeyError(f"Order not found: {order_id}")
        return all_orders[order_id]

    def load_shipments(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.shipments_dir / "shipments.json")
        return {item["shipment_id"]: item for item in payload["shipments"]}

    def load_shipment(self, shipment_id: str) -> dict[str, Any]:
        all_shipments = self.load_shipments()
        if shipment_id not in all_shipments:
            raise KeyError(f"Shipment not found: {shipment_id}")
        return all_shipments[shipment_id]

    def load_returns(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.returns_dir / "returns.json")
        return {item["return_id"]: item for item in payload["returns"]}

    def load_return(self, return_id: str) -> dict[str, Any]:
        all_returns = self.load_returns()
        if return_id not in all_returns:
            raise KeyError(f"Return not found: {return_id}")
        return all_returns[return_id]

    def load_inventory(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.inventory_dir / "inventory.json")
        return {item["sku"]: item for item in payload["inventory"]}

    def load_inventory_item(self, sku: str) -> dict[str, Any]:
        all_inventory = self.load_inventory()
        if sku not in all_inventory:
            raise KeyError(f"Inventory item not found: {sku}")
        return all_inventory[sku]

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachment_dir / relative_path
        return attachment_path.read_text(encoding="utf-8")
