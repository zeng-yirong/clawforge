from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ExpenseRepository:
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

    def get_travel_policy(self, tier: str) -> dict[str, Any] | None:
        policies = self._load_json("travel_policies.json")
        if isinstance(policies, dict) and "tiers" in policies:
            tiers = policies.get("tiers", {})
            if tier in tiers:
                return {"tier": tier, **tiers[tier], "categories": policies.get("categories", []), "reimbursement_rules": policies.get("reimbursement_rules", {})}
        return None

    def get_all_tiers(self) -> list[str]:
        policies = self._load_json("travel_policies.json")
        if isinstance(policies, dict) and "tiers" in policies:
            return list(policies.get("tiers", {}).keys())
        return []

    def get_consumption_records(self, trip_id: str) -> dict[str, Any] | None:
        records_path = self.data_root / "consumption_records.json"
        if not records_path.exists():
            return None
        with open(records_path, encoding="utf-8") as f:
            data = json.load(f)
            if data.get("trip_id") == trip_id:
                return data
        return None

    def list_trip_ids(self) -> list[str]:
        records_path = self.data_root / "consumption_records.json"
        if not records_path.exists():
            return []
        with open(records_path, encoding="utf-8") as f:
            data = json.load(f)
            return [data.get("trip_id", "")]

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
