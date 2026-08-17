from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class DataRepository:
    def __init__(self, data_root: str | None = None):
        if data_root is None:
            self.data_root = Path(__file__).parent / "data"
        else:
            self.data_root = Path(data_root)
        self._cache: dict[str, Any] = {}

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        full_path = self.data_root / relative_path
        with open(full_path, encoding="utf-8") as f:
            return json.load(f)

    def get_accounts(self) -> list[dict[str, Any]]:
        return self._load_json("accounts.json")

    def get_contacts(self) -> list[dict[str, Any]]:
        return self._load_json("contacts.json")

    def get_platform(self, platform_id: str) -> dict[str, Any]:
        cache_key = f"platform:{platform_id}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load_json(f"platforms/{platform_id}.json")
        return self._cache[cache_key]

    def list_platform_ids(self) -> list[str]:
        platforms_dir = self.data_root / "platforms"
        return [p.stem for p in platforms_dir.glob("*.json")]

    def get_policy(self, policy_id: str) -> dict[str, Any]:
        cache_key = f"policy:{policy_id}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load_json(f"policies/{policy_id}.json")
        return self._cache[cache_key]

    def list_policy_ids(self) -> list[str]:
        policies_dir = self.data_root / "policies"
        return [p.stem for p in policies_dir.glob("*.json")]

    def get_scenario(self, scenario_id: str) -> dict[str, Any]:
        return self._load_json(f"scenarios/{scenario_id}.json")

    def list_scenario_ids(self) -> list[str]:
        scenarios_dir = self.data_root / "scenarios"
        return [s.stem for s in scenarios_dir.glob("*.json")]
