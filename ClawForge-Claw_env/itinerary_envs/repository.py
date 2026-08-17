from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ItineraryRepository:
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

    def get_city(self, city_id: str) -> dict[str, Any] | None:
        data = self._load_json("transportation.json")
        cities = data.get("cities", [])
        for city in cities:
            if city.get("city_id") == city_id:
                return city
        return None

    def list_cities(self) -> list[dict[str, Any]]:
        data = self._load_json("transportation.json")
        return data.get("cities", [])

    def get_route(self, origin: str, destination: str) -> dict[str, Any] | None:
        data = self._load_json("transportation.json")
        routes = data.get("routes", [])
        for route in routes:
            if route.get("origin") == origin and route.get("destination") == destination:
                return route
        return None

    def list_routes_from(self, origin: str) -> list[dict[str, Any]]:
        data = self._load_json("transportation.json")
        routes = data.get("routes", [])
        return [r for r in routes if r.get("origin") == origin]

    def get_transfer_hubs(self) -> list[dict[str, Any]]:
        data = self._load_json("transportation.json")
        return data.get("transfer_hubs", [])

    def get_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        scenarios_dir = self.data_root / "scenarios"
        if not scenarios_dir.exists():
            return None
        for f in scenarios_dir.glob("*.json"):
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
                if data.get("scenario_id") == scenario_id:
                    return data
        return None

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
