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
        self.clusters_file = self.data_root / "resources" / "clusters.json"
        self.ledger_file = self.data_root / "resources" / "resource_ledger.json"
        self.pricing_catalogs_file = self.data_root / "pricing" / "pricing_catalogs.json"
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

    def load_clusters(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.clusters_file)
        return {item["cluster_id"]: item for item in payload["clusters"]}

    def load_cluster(self, cluster_id: str) -> dict[str, Any]:
        clusters = self.load_clusters()
        if cluster_id not in clusters:
            raise KeyError(f"Cluster not found: {cluster_id}")
        return clusters[cluster_id]

    def load_resource_ledger(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.ledger_file)
        return {item["entry_id"]: item for item in payload["resource_ledger"]}

    def load_ledger_entry(self, entry_id: str) -> dict[str, Any]:
        ledger = self.load_resource_ledger()
        if entry_id not in ledger:
            raise KeyError(f"Ledger entry not found: {entry_id}")
        return ledger[entry_id]

    def load_pricing_catalogs(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.pricing_catalogs_file)
        return {item["catalog_id"]: item for item in payload["pricing_catalogs"]}

    def load_pricing_catalog(self, catalog_id: str) -> dict[str, Any]:
        catalogs = self.load_pricing_catalogs()
        if catalog_id not in catalogs:
            raise KeyError(f"Pricing catalog not found: {catalog_id}")
        return catalogs[catalog_id]

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachments_dir / relative_path
        if not attachment_path.exists():
            raise FileNotFoundError(f"Attachment not found: {relative_path}")
        return attachment_path.read_text(encoding="utf-8")
