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
        self.flights_dir = self.data_root / "flights"
        self.hotels_dir = self.data_root / "hotels"
        self.transports_dir = self.data_root / "transports"
        self.conferences_dir = self.data_root / "conferences"
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

    def load_flights(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.flights_dir / "flights.json")
        return {item["flight_id"]: item for item in payload["flights"]}

    def load_flight(self, flight_id: str) -> dict[str, Any]:
        all_flights = self.load_flights()
        if flight_id not in all_flights:
            raise KeyError(f"Flight not found: {flight_id}")
        return all_flights[flight_id]

    def load_hotels(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.hotels_dir / "hotels.json")
        return {item["hotel_id"]: item for item in payload["hotels"]}

    def load_hotel(self, hotel_id: str) -> dict[str, Any]:
        all_hotels = self.load_hotels()
        if hotel_id not in all_hotels:
            raise KeyError(f"Hotel not found: {hotel_id}")
        return all_hotels[hotel_id]

    def load_transports(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.transports_dir / "transports.json")
        return {item["transport_id"]: item for item in payload["transports"]}

    def load_transport(self, transport_id: str) -> dict[str, Any]:
        all_transports = self.load_transports()
        if transport_id not in all_transports:
            raise KeyError(f"Transport not found: {transport_id}")
        return all_transports[transport_id]

    def load_conferences(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.conferences_dir / "conferences.json")
        return {item["conference_id"]: item for item in payload["conferences"]}

    def load_conference(self, conference_id: str) -> dict[str, Any]:
        all_conferences = self.load_conferences()
        if conference_id not in all_conferences:
            raise KeyError(f"Conference not found: {conference_id}")
        return all_conferences[conference_id]

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachment_dir / relative_path
        return attachment_path.read_text(encoding="utf-8")
