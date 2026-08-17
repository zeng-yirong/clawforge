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
        self.devices_dir = self.data_root / "devices"
        self.schedules_dir = self.data_root / "schedules"
        self.accounts_file = self.data_root / "accounts.json"
        self.scenario_dir = self.data_root / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_devices(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.devices_dir / "devices.json")
        return {item["device_id"]: item for item in payload["devices"]}

    def load_schedules(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.schedules_dir / "schedules.json")
        return {item["schedule_id"]: item for item in payload["schedules"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]
