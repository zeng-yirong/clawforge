from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class VaultRepository:
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
        elif isinstance(accounts, dict):
            return [accounts]
        return []

    def get_vault_schema(self) -> dict[str, Any]:
        return self._load_json("vault_schema.json")

    def get_category(self, category_id: str) -> dict[str, Any] | None:
        schema = self.get_vault_schema()
        categories = schema.get("credential_categories", [])
        for cat in categories:
            if cat.get("category_id") == category_id:
                return cat
        return None

    def list_categories(self) -> list[dict[str, Any]]:
        schema = self.get_vault_schema()
        return schema.get("credential_categories", [])

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
