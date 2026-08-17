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
        self.accounts_file = self.data_root / "accounts.json"
        self.contacts_file = self.data_root / "contacts.json"
        self.attachments_file = self.data_root / "attachments.json"
        self.reports_file = self.data_root / "reports" / "reports.json"
        self.presentations_file = self.data_root / "presentations" / "presentations.json"
        self.media_samples_file = self.data_root / "media_samples" / "media_samples.json"
        self.attachments_dir = self.data_root / "attachments"
        self.scenario_dir = self.data_root / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_attachment_manifest(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.attachments_file)
        return {item["path"]: item for item in payload["attachments"]}

    def load_reports(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.reports_file)
        return {item["report_id"]: item for item in payload["reports"]}

    def load_presentations(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.presentations_file)
        return {item["presentation_id"]: item for item in payload["presentations"]}

    def load_media_samples(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.media_samples_file)
        return {item["sample_id"]: item for item in payload["media_samples"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachments_dir / relative_path
        if not attachment_path.exists():
            raise FileNotFoundError(f"Attachment not found: {relative_path}")
        return attachment_path.read_text(encoding="utf-8")
