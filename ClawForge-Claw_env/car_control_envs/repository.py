from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CarRepository:
    def __init__(self, data_root: Path | str):
        self.data_root = Path(data_root)

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        full_path = self.data_root / relative_path
        with open(full_path, encoding="utf-8") as f:
            return json.load(f)

    def get_account(self, account_id: str) -> dict[str, Any] | None:
        accounts = self._load_json("accounts.json")
        if isinstance(accounts, list):
            for acc in accounts:
                if acc.get("account_id") == account_id:
                    return acc
        elif isinstance(accounts, dict) and accounts.get("account_id") == account_id:
            return accounts
        return None

    def list_accounts(self) -> list[dict[str, Any]]:
        accounts = self._load_json("accounts.json")
        if isinstance(accounts, list):
            return accounts
        return [accounts]

    def get_vehicle(self) -> dict[str, Any]:
        return self._load_json("vehicle.json")

    def get_zones(self) -> list[dict[str, Any]]:
        data = self._load_json("zones.json")
        return data.get("zones", []) if isinstance(data, dict) else data

    def get_ac_presets(self) -> dict[str, Any]:
        return self._load_json("ac_presets.json")

    def get_driving_modes(self) -> dict[str, Any]:
        return self._load_json("driving_modes.json")

    def get_ambient_lights(self) -> dict[str, Any]:
        return self._load_json("ambient_lights.json")

    def get_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        scenario_path = self.data_root / "scenarios" / f"{scenario_id}.json"
        if not scenario_path.exists():
            for candidate in (self.data_root / "scenarios").glob("*.json"):
                with open(candidate, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("scenario_id") == scenario_id:
                    return data
            return None
        with open(scenario_path, encoding="utf-8") as f:
            return json.load(f)

    def list_scenarios(self) -> list[dict[str, Any]]:
        scenarios_dir = self.data_root / "scenarios"
        if not scenarios_dir.exists():
            return []
        scenarios = []
        for f in scenarios_dir.glob("*.json"):
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
                scenarios.append({
                    "scenario_id": data.get("scenario_id", f.stem),
                    "title": data.get("title", ""),
                    "task_prompt": data.get("task_prompt", ""),
                })
        return scenarios
