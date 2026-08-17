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
        self.contacts_file = self.data_root / "contacts.json"
        self.companies_file = self.data_root / "companies.json"
        self.tag_definitions_file = self.data_root / "tags" / "tag_definitions.json"
        self.reminders_file = self.data_root / "reminders" / "reminders.json"
        self.scenario_dir = self.data_root / "scenarios"
        self.accounts_file = self.data_root / "accounts.json"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_companies(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.companies_file)
        return {item["company_id"]: item for item in payload["companies"]}

    def load_tag_definitions(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.tag_definitions_file)
        return {item["tag_id"]: item for item in payload["tag_definitions"]}

    def load_reminders(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.reminders_file)
        return {item["reminder_id"]: item for item in payload["reminders"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]
