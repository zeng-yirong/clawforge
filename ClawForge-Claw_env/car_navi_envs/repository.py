from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class NavigationRepository:
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

    def get_vehicle(self) -> dict[str, Any]:
        return self._load_json("vehicle.json")

    def get_regions(self) -> list[dict[str, Any]]:
        data = self._load_json("regions.json")
        return data.get("regions", []) if isinstance(data, dict) else data

    def get_pois(self, category: str | None = None, keyword: str | None = None) -> list[dict[str, Any]]:
        data = self._load_json("pois.json")
        pois = data.get("pois", []) if isinstance(data, dict) else data
        
        if category:
            pois = [p for p in pois if p.get("category") == category]
        if keyword:
            keyword_lower = keyword.lower()
            pois = [p for p in pois if keyword_lower in p.get("name", "").lower() or 
                    keyword_lower in p.get("keyword", "").lower()]
        
        return pois

    def get_poi(self, poi_id: str) -> dict[str, Any] | None:
        pois = self.get_pois()
        for poi in pois:
            if poi.get("poi_id") == poi_id:
                return poi
        return None

    def get_route_preferences(self) -> list[dict[str, Any]]:
        data = self._load_json("route_preferences.json")
        return data.get("preferences", []) if isinstance(data, dict) else data

    def get_traffic_data(self) -> dict[str, Any]:
        return self._load_json("traffic.json")

    def get_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        scenario_path = self.data_root / "scenarios" / f"{scenario_id}.json"
        if not scenario_path.exists():
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
