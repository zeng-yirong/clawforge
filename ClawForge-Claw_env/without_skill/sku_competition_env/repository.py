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
        self.brands_file = self.data_root / "brands" / "brands.json"
        self.skus_file = self.data_root / "skus" / "skus.json"
        self.price_books_file = self.data_root / "pricing" / "price_books.json"
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

    def load_brands(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.brands_file)
        return {item["brand_id"]: item for item in payload["brands"]}

    def load_brand(self, brand_id: str) -> dict[str, Any]:
        brands = self.load_brands()
        if brand_id not in brands:
            raise KeyError(f"Brand not found: {brand_id}")
        return brands[brand_id]

    def load_skus(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.skus_file)
        return {item["sku_id"]: item for item in payload["skus"]}

    def load_sku(self, sku_id: str) -> dict[str, Any]:
        skus = self.load_skus()
        if sku_id not in skus:
            raise KeyError(f"SKU not found: {sku_id}")
        return skus[sku_id]

    def load_price_books(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.price_books_file)
        return {item["price_book_id"]: item for item in payload["price_books"]}

    def load_price_book(self, price_book_id: str) -> dict[str, Any]:
        books = self.load_price_books()
        if price_book_id not in books:
            raise KeyError(f"Price book not found: {price_book_id}")
        return books[price_book_id]

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachments_dir / relative_path
        if not attachment_path.exists():
            raise FileNotFoundError(f"Attachment not found: {relative_path}")
        return attachment_path.read_text(encoding="utf-8")

