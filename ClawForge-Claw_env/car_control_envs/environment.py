from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .ac import VehicleController, set_ac_power, set_ac_temperature, set_ac_fan_speed, set_ac_mode, set_ac_direction, set_ac_circulation, set_ac_defog, set_ac_defrost, get_ac_status
from .seats import adjust_seat_position, adjust_seat_recline, adjust_seat_lumbar, set_seat_heating, set_seat_ventilation, get_seat_status
from .windows import set_window_open, close_window, open_all_windows, close_all_windows, get_window_status
from .lights import set_ambient_light, set_reading_light, set_fog_lights, get_light_status
from .driving import set_driving_mode, get_driving_mode
from .multimedia import play_media, pause_media, set_volume, adjust_volume, get_multimedia_status
from .status import get_vehicle_status
from .repository import CarRepository
from .store import SessionStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _action_timestamp(base_time: str, action_index: int) -> str:
    base = _coerce_iso_datetime(base_time)
    return (base + timedelta(seconds=action_index * 30)).isoformat()


class CarControlEnvironment:
    def __init__(
        self,
        data_root: Path | str,
        state_root: Path | str,
    ):
        self.data_root = Path(data_root)
        self.state_root = Path(state_root)
        self.repo = CarRepository(data_root)
        self.store = SessionStore(state_root)

    def _get_binding(self, key: str) -> str | None:
        env_key = f"CAR_{key}"
        return os.environ.get(env_key)

    def prepare_rollout(self, scenario_id: str, show_bindings: bool = False) -> dict[str, Any]:
        scenario = self.repo.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        base_time = scenario.get("base_time", _utc_now_iso())
        workspace_account_id = scenario.get("workspace_account_id", "acc_001")
        account = self.repo.get_account(workspace_account_id)
        if not account:
            raise ValueError(f"Account {workspace_account_id} not found")

        import uuid
        session_id = f"car-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:4]}"

        state_root = str(self.state_root)
        self.store.create_session(
            session_id=session_id,
            scenario_id=scenario_id,
            base_time=base_time,
            workspace_account=account,
        )

        bindings = {
            "CAR_SESSION_ID": session_id,
            "CAR_STATE_ROOT": state_root,
            "CAR_SCENARIO_ID": scenario_id,
        }

        result = {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "state_root": state_root,
            "bindings": bindings,
        }
        return result

    def reset_rollout(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        scenario = self.repo.get_scenario(session["scenario_id"])
        if not scenario:
            raise ValueError(f"Scenario {session['scenario_id']} not found")

        base_time = scenario.get("base_time", _utc_now_iso())
        workspace_account_id = scenario.get("workspace_account_id", "acc_001")
        account = self.repo.get_account(workspace_account_id)

        self.store.delete_session(session_id)
        self.store.create_session(
            session_id=session_id,
            scenario_id=session["scenario_id"],
            base_time=base_time,
            workspace_account=account,
        )

        return {"session_id": session_id, "status": "reset"}

    def execute_action(
        self,
        session_id: str,
        action_type: str,
        action_index: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        base_time = session["meta"]["base_time"]
        timestamp = _action_timestamp(base_time, action_index)

        ctrl = VehicleController(session, self.store, session_id)
        result: dict[str, Any] = {"status": "ok"}

        if action_type == "ac_power":
            on = kwargs.get("on", True)
            result = set_ac_power(ctrl, on)
        elif action_type == "ac_temperature":
            temperature = kwargs.get("temperature", 24)
            result = set_ac_temperature(ctrl, temperature)
        elif action_type == "ac_fan_speed":
            speed = kwargs.get("speed", 2)
            result = set_ac_fan_speed(ctrl, speed)
        elif action_type == "ac_mode":
            mode = kwargs.get("mode", "auto")
            result = set_ac_mode(ctrl, mode)
        elif action_type == "ac_direction":
            direction = kwargs.get("direction", "face")
            result = set_ac_direction(ctrl, direction)
        elif action_type == "ac_circulation":
            circulation = kwargs.get("circulation", "internal")
            result = set_ac_circulation(ctrl, circulation)
        elif action_type == "ac_defog":
            on = kwargs.get("on", True)
            result = set_ac_defog(ctrl, on)
        elif action_type == "ac_defrost":
            on = kwargs.get("on", True)
            result = set_ac_defrost(ctrl, on)
        elif action_type == "ac_status":
            result = get_ac_status(ctrl)
        elif action_type == "seat_position":
            zone = kwargs.get("zone", "fl")
            position = kwargs.get("position", 50)
            result = adjust_seat_position(ctrl, zone, position)
        elif action_type == "seat_recline":
            zone = kwargs.get("zone", "fl")
            recline = kwargs.get("recline", 30)
            result = adjust_seat_recline(ctrl, zone, recline)
        elif action_type == "seat_lumbar":
            zone = kwargs.get("zone", "fl")
            lumbar = kwargs.get("lumbar", 30)
            result = adjust_seat_lumbar(ctrl, zone, lumbar)
        elif action_type == "seat_heating":
            zone = kwargs.get("zone", "fl")
            level = kwargs.get("level", 0)
            result = set_seat_heating(ctrl, zone, level)
        elif action_type == "seat_ventilation":
            zone = kwargs.get("zone", "fl")
            level = kwargs.get("level", 0)
            result = set_seat_ventilation(ctrl, zone, level)
        elif action_type == "seat_status":
            zone = kwargs.get("zone")
            result = get_seat_status(ctrl, zone)
        elif action_type == "window_open":
            window = kwargs.get("window", "fl")
            percentage = kwargs.get("percentage", 100)
            result = set_window_open(ctrl, window, percentage)
        elif action_type == "window_close":
            window = kwargs.get("window", "fl")
            result = close_window(ctrl, window)
        elif action_type == "windows_open_all":
            result = open_all_windows(ctrl)
        elif action_type == "windows_close_all":
            result = close_all_windows(ctrl)
        elif action_type == "window_status":
            result = get_window_status(ctrl)
        elif action_type == "ambient_light":
            on = kwargs.get("on", True)
            color = kwargs.get("color")
            brightness = kwargs.get("brightness")
            result = set_ambient_light(ctrl, on, color, brightness)
        elif action_type == "reading_light":
            zone = kwargs.get("zone", "fl")
            on = kwargs.get("on", True)
            result = set_reading_light(ctrl, zone, on)
        elif action_type == "fog_light":
            fog_type = kwargs.get("fog_type", "front")
            on = kwargs.get("on", True)
            result = set_fog_lights(ctrl, fog_type, on)
        elif action_type == "light_status":
            result = get_light_status(ctrl)
        elif action_type == "driving_mode":
            mode = kwargs.get("mode", "comfort")
            result = set_driving_mode(ctrl, mode)
        elif action_type == "driving_mode_status":
            result = get_driving_mode(ctrl)
        elif action_type == "media_play":
            source = kwargs.get("source")
            result = play_media(ctrl, source)
        elif action_type == "media_pause":
            result = pause_media(ctrl)
        elif action_type == "volume_set":
            volume = kwargs.get("volume", 15)
            result = set_volume(ctrl, volume)
        elif action_type == "volume_adjust":
            delta = kwargs.get("delta", 5)
            result = adjust_volume(ctrl, delta)
        elif action_type == "multimedia_status":
            result = get_multimedia_status(ctrl)
        elif action_type == "status_query":
            query_type = kwargs.get("query_type")
            result = get_vehicle_status(ctrl, query_type)
        else:
            result = {"status": "error", "message": f"Unknown action: {action_type}"}

        session["meta"]["action_index"] = action_index + 1
        session["actions"].append({
            "action_index": action_index,
            "timestamp": timestamp,
            "action_type": action_type,
            "details": kwargs,
            "result": result,
        })
        self.store.save_session(session_id, session)

        return result

    def get_session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "vehicle_state": session["vehicle_state"],
            "action_count": len(session.get("actions", [])),
        }

    def get_reward(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        scenario = self.repo.get_scenario(session["scenario_id"])
        if not scenario:
            raise ValueError(f"Scenario {session['scenario_id']} not found")
        return evaluate_session(session, scenario)
