from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .devices import (
    get_device_status,
    set_air_conditioner,
    set_humidifier,
    set_smart_plug,
    turn_off_device,
    get_all_devices,
    get_devices_by_type,
    calculate_device_power_consumption,
)
from .electricity import (
    get_electricity_rate,
    calculate_device_energy_cost,
    get_optimal_operation_window,
    get_daily_rate_schedule,
    check_cost_saving_opportunity,
    calculate_total_energy_cost,
)
from .evaluator import evaluate_session
from .health import (
    get_user_health_profile,
    analyze_health_comfort_conflicts,
    get_health_based_recommendations,
    check_health_alerts,
)
from .repository import DatasetRepository
from .store import SessionStore
from .weather import (
    get_weather_at_time,
    analyze_weather_comfort,
    calculate_recommended_temperature,
    get_weather_forecast,
    check_extreme_weather,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class SmartHomeEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("SMART_HOME_STATE_ROOT", Path.cwd() / ".smart_home_state"))
        self.repository = DatasetRepository(data_root)
        self.store = SessionStore(state_root or default_state_root)
        self.accounts = self.repository.load_accounts()

    def list_scenarios(self) -> dict[str, Any]:
        return {
            "scenarios": [
                {
                    "scenario_id": item["scenario_id"],
                    "title": item["title"],
                    "task_prompt": item["task_prompt"],
                }
                for item in self.repository.list_scenarios()
            ]
        }

    def create_session(self, session_id: str, scenario_id: str, overwrite: bool = False) -> dict[str, Any]:
        scenario = self.repository.load_scenario(scenario_id)
        session_payload = self._build_session_payload(session_id=session_id, scenario=scenario)
        self.store.create_session(session_id, session_payload, overwrite=overwrite)
        return self.session_summary(session_id)

    def reset_session(self, session_id: str) -> dict[str, Any]:
        existing = self.store.load_session(session_id)
        return self.create_session(session_id, existing["scenario_id"], overwrite=True)

    def get_task(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
            "active_devices_count": len([d for d in session.get("devices", {}).values() if d.get("state") == "on"]),
            "pending_adjustments": len([a for a in session.get("actions", []) if a.get("action", "").startswith("set_")]),
        }

    def get_weather(self, session_id: str, timestamp: str | None = None) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if timestamp is None:
            timestamp = session.get("meta", {}).get("current_time")
        return {"session_id": session_id, "data": get_weather_at_time(session, timestamp)}

    def analyze_weather_comfort(self, session_id: str, temperature: float, humidity: float) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": analyze_weather_comfort(temperature, humidity)}

    def get_weather_forecast(self, session_id: str, hours_ahead: int = 24) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_weather_forecast(session, hours_ahead)}

    def check_extreme_weather(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": check_extreme_weather(session)}

    def get_electricity_rate(self, session_id: str, timestamp: str | None = None) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if timestamp is None:
            timestamp = session.get("meta", {}).get("current_time")
        return {"session_id": session_id, "data": get_electricity_rate(session, timestamp)}

    def get_daily_rate_schedule(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_daily_rate_schedule(session)}

    def get_optimal_operation_window(
        self,
        session_id: str,
        duration_hours: float,
        preferred_start: str | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_optimal_operation_window(session, duration_hours, preferred_start),
        }

    def check_cost_saving_opportunity(
        self,
        session_id: str,
        device_type: str,
        current_setting: dict[str, Any],
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": check_cost_saving_opportunity(session, device_type, current_setting),
        }

    def calculate_total_energy_cost(
        self,
        session_id: str,
        device_operations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": calculate_total_energy_cost(session, device_operations),
        }

    def get_user_health_profile(self, session_id: str, user_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_user_health_profile(session, user_id)}

    def analyze_health_comfort_conflicts(
        self,
        session_id: str,
        user_id: str,
        current_temp: float,
        current_humidity: float,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": analyze_health_comfort_conflicts(session, user_id, current_temp, current_humidity),
        }

    def get_health_based_recommendations(
        self,
        session_id: str,
        user_id: str,
        weather_conditions: dict[str, Any],
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_health_based_recommendations(session, user_id, weather_conditions),
        }

    def check_health_alerts(
        self,
        session_id: str,
        user_id: str,
        current_temp: float,
        current_humidity: float,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": check_health_alerts(session, user_id, current_temp, current_humidity),
        }

    def get_device_status(self, session_id: str, device_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_device_status(session, device_id)}

    def get_all_devices(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_all_devices(session)}

    def get_devices_by_type(self, session_id: str, device_type: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_devices_by_type(session, device_type)}

    def set_air_conditioner(
        self,
        session_id: str,
        device_id: str,
        temperature: float,
        mode: str = "auto",
        fan_speed: str = "auto",
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = set_air_conditioner(
                session,
                device_id=device_id,
                temperature=temperature,
                mode=mode,
                fan_speed=fan_speed,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "set_air_conditioner", {
                "device_id": device_id,
                "temperature": temperature,
                "mode": mode,
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def set_humidifier(
        self,
        session_id: str,
        device_id: str,
        humidity_level: int,
        mode: str = "auto",
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = set_humidifier(
                session,
                device_id=device_id,
                humidity_level=humidity_level,
                mode=mode,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "set_humidifier", {
                "device_id": device_id,
                "humidity_level": humidity_level,
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def set_smart_plug(
        self,
        session_id: str,
        device_id: str,
        power_state: bool,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = set_smart_plug(
                session,
                device_id=device_id,
                power_state=power_state,
                action_index=action_index,
            )
            self._record_action(session, action_index, event_at, "set_smart_plug", {
                "device_id": device_id,
                "power_state": power_state,
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def turn_off_device(self, session_id: str, device_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = turn_off_device(session, device_id=device_id, action_index=action_index)
            self._record_action(session, action_index, event_at, "turn_off_device", {"device_id": device_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def calculate_device_power_consumption(
        self,
        session_id: str,
        device_id: str,
        hours: float,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": calculate_device_power_consumption(session, device_id, hours),
        }

    def calculate_recommended_temperature(
        self,
        session_id: str,
        current_temp: float | None = None,
        current_humidity: float | None = None,
        user_health_priority: bool = False,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if current_temp is None or current_humidity is None:
            weather = get_weather_at_time(session, session.get("meta", {}).get("current_time"))
            current_temp = current_temp or weather.get("temperature", 25)
            current_humidity = current_humidity or weather.get("humidity", 50)
        return {
            "session_id": session_id,
            "data": calculate_recommended_temperature(current_temp, current_humidity, user_health_priority),
        }

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        devices = session.get("devices", {})
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "devices_count": len(devices),
            "active_devices_count": len([d for d in devices.values() if d.get("state") == "on"]),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_weather = self.repository.load_weather()
        all_health = self.repository.load_health_data()
        all_devices = self.repository.load_devices()

        weather_data = all_weather.get(scenario.get("weather_id", "default_weather"), {})
        health_data = {uid: all_health[uid] for uid in scenario.get("user_ids", []) if uid in all_health}
        device_configs = {did: all_devices[did] for did in scenario.get("device_ids", []) if did in all_devices}

        devices = {}
        for did, dconfig in device_configs.items():
            devices[did] = {
                "type": dconfig.get("type", "smart_plug"),
                "online": True,
                "state": "off",
                "settings": deepcopy(dconfig.get("default_settings", {})),
            }

        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": _utc_now_iso(),
            "meta": {
                "base_time": scenario["current_time"],
                "action_index": 0,
            },
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "weather": weather_data,
            "electricity_rates": {},
            "health_data": health_data,
            "devices": devices,
            "actions": [],
            "alerts": {},
        }

    def _next_event(self, session: dict[str, Any]) -> tuple[str, int]:
        action_index = int(session["meta"]["action_index"]) + 1
        session["meta"]["action_index"] = action_index
        event_at = (_coerce_iso_datetime(session["meta"]["base_time"]) + timedelta(minutes=action_index)).isoformat()
        return event_at, action_index

    def _record_action(
        self,
        session: dict[str, Any],
        action_index: int,
        event_at: str,
        action_type: str,
        details: dict[str, Any],
    ) -> None:
        session["actions"].append(
            {
                "action_index": action_index,
                "timestamp": event_at,
                "action_type": action_type,
                "details": details,
            }
        )
