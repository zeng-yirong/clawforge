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
        self.weather_dir = self.data_root / "weather"
        self.electricity_dir = self.data_root / "electricity"
        self.health_dir = self.data_root / "health"
        self.devices_dir = self.data_root / "devices"
        self.accounts_file = self.data_root / "accounts.json"
        self.scenario_dir = self.data_root / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_weather(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.weather_dir / "weather.json")
        return {item["timestamp"]: item for item in payload["weather_data"]}

    def load_electricity_rates(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.electricity_dir / "rates.json")
        return {item["period"]: item for item in payload["rates"]}

    def load_health_data(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.health_dir / "health.json")
        return {item["user_id"]: item for item in payload["users"]}

    def load_devices(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(self.devices_dir / "devices.json")
        return {item["device_id"]: item for item in payload["devices"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return _load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [_load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def get_weather_at_time(self, timestamp: str) -> dict[str, Any]:
        weather_data = self.load_weather()
        if timestamp in weather_data:
            return weather_data[timestamp]
        timestamps = sorted(weather_data.keys())
        for ts in timestamps:
            if ts >= timestamp:
                return weather_data[ts]
        return weather_data[timestamps[-1]] if timestamps else {}

    def get_electricity_rate(self, period: str) -> dict[str, Any]:
        rates = self.load_electricity_rates()
        if period in rates:
            return rates[period]
        return rates.get("off_peak", {"period": period, "rate_per_kwh": 0.12, "label": "standard"})
