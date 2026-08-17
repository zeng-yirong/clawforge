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
        self.competitors_dir = self.data_root / "competitors"
        self.policies_dir = self.data_root / "policies"
        self.users_dir = self.data_root / "users"
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

    def load_competitors(self) -> dict[str, dict[str, Any]]:
        competitors = {}
        for path in self.competitors_dir.glob("*.json"):
            data = _load_json(path)
            competitors[data["competitor_id"]] = data
        return competitors

    def load_competitor(self, competitor_id: str) -> dict[str, Any]:
        all_competitors = self.load_competitors()
        if competitor_id not in all_competitors:
            raise KeyError(f"Competitor not found: {competitor_id}")
        return all_competitors[competitor_id]

    def load_policies(self) -> dict[str, dict[str, Any]]:
        policies = {}
        for path in self.policies_dir.glob("*.json"):
            data = _load_json(path)
            policies[data["policy_id"]] = data
        return policies

    def load_policy(self, policy_id: str) -> dict[str, Any]:
        all_policies = self.load_policies()
        if policy_id not in all_policies:
            raise KeyError(f"Policy not found: {policy_id}")
        return all_policies[policy_id]

    def load_users(self) -> dict[str, dict[str, Any]]:
        users = {}
        for path in self.users_dir.glob("*.json"):
            data = _load_json(path)
            users[data["user_id"]] = data
        return users

    def load_user(self, user_id: str) -> dict[str, Any]:
        all_users = self.load_users()
        if user_id not in all_users:
            raise KeyError(f"User not found: {user_id}")
        return all_users[user_id]

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachment_dir / relative_path
        return attachment_path.read_text(encoding="utf-8")
