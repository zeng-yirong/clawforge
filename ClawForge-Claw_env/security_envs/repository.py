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
        self.doors_dir = self.data_root / "doors"
        self.zones_dir = self.data_root / "zones"
        self.contacts_dir = self.data_root / "contacts"
        self.accounts_file = self.data_root / "accounts.json"
        self.scenario_dir = self.data_root / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_doors(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.doors_dir / "doors.json")
        return {item["door_id"]: item for item in payload["doors"]}

    def load_zones(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.zones_dir / "zones.json")
        return {item["zone_id"]: item for item in payload["zones"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.contacts_dir / "contacts.json")
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]
