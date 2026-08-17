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
        self.stocks_dir = self.data_root / "stocks"
        self.news_dir = self.data_root / "news"
        self.earnings_dir = self.data_root / "earnings"
        self.analysts_dir = self.data_root / "analysts"
        self.briefs_dir = self.data_root / "briefs"
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

    def load_stocks(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.stocks_dir / "stocks.json")
        return {item["ticker"]: item for item in payload["stocks"]}

    def load_stock(self, ticker: str) -> dict[str, Any]:
        all_stocks = self.load_stocks()
        if ticker not in all_stocks:
            raise KeyError(f"Stock not found: {ticker}")
        return all_stocks[ticker]

    def load_news(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.news_dir / "news.json")
        return {item["news_id"]: item for item in payload["news"]}

    def load_news_item(self, news_id: str) -> dict[str, Any]:
        all_news = self.load_news()
        if news_id not in all_news:
            raise KeyError(f"News not found: {news_id}")
        return all_news[news_id]

    def load_earnings(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.earnings_dir / "earnings.json")
        return {item["earnings_id"]: item for item in payload["earnings"]}

    def load_earnings_record(self, earnings_id: str) -> dict[str, Any]:
        all_earnings = self.load_earnings()
        if earnings_id not in all_earnings:
            raise KeyError(f"Earnings record not found: {earnings_id}")
        return all_earnings[earnings_id]

    def load_analysts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.analysts_dir / "analysts.json")
        return {item["analyst_id"]: item for item in payload["analysts"]}

    def load_analyst(self, analyst_id: str) -> dict[str, Any]:
        all_analysts = self.load_analysts()
        if analyst_id not in all_analysts:
            raise KeyError(f"Analyst not found: {analyst_id}")
        return all_analysts[analyst_id]

    def load_briefs(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.briefs_dir / "briefs.json")
        return {item["brief_id"]: item for item in payload["briefs"]}

    def load_brief(self, brief_id: str) -> dict[str, Any]:
        all_briefs = self.load_briefs()
        if brief_id not in all_briefs:
            raise KeyError(f"Brief not found: {brief_id}")
        return all_briefs[brief_id]

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachment_dir / relative_path
        return attachment_path.read_text(encoding="utf-8")
