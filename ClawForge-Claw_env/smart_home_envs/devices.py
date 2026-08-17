from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


def get_device_status(session: dict[str, Any], device_id: str) -> dict[str, Any]:
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"error": f"Device {device_id} not found", "online": False}

    device = deepcopy(devices[device_id])
    return {"device_id": device_id, "online": device.get("online", True), **device}


def set_air_conditioner(
    session: dict[str, Any],
    device_id: str,
    temperature: float,
    mode: str = "auto",
    fan_speed: str = "auto",
    action_index: int | None = None,
) -> dict[str, Any]:
    devices = session.setdefault("devices", {})
    device = devices.setdefault(device_id, {
        "type": "air_conditioner",
        "online": True,
        "state": "off",
        "settings": {},
    })

    device["type"] = "air_conditioner"
    device["online"] = True
    device["state"] = "on"
    device["settings"]["temperature"] = temperature
    device["settings"]["mode"] = mode
    device["settings"]["fan_speed"] = fan_speed

    action = {
        "action": "set_ac",
        "device_id": device_id,
        "temperature": temperature,
        "mode": mode,
        "fan_speed": fan_speed,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }

    session.setdefault("actions", []).append(action)
    return {
        "device_id": device_id,
        "state": "on",
        "settings": deepcopy(device["settings"]),
        "action_index": action_index,
    }


def set_humidifier(
    session: dict[str, Any],
    device_id: str,
    humidity_level: int,
    mode: str = "auto",
    action_index: int | None = None,
) -> dict[str, Any]:
    devices = session.setdefault("devices", {})
    device = devices.setdefault(device_id, {
        "type": "humidifier",
        "online": True,
        "state": "off",
        "settings": {},
    })

    device["type"] = "humidifier"
    device["online"] = True
    device["state"] = "on"
    device["settings"]["humidity_level"] = humidity_level
    device["settings"]["mode"] = mode

    action = {
        "action": "set_humidifier",
        "device_id": device_id,
        "humidity_level": humidity_level,
        "mode": mode,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }

    session.setdefault("actions", []).append(action)
    return {
        "device_id": device_id,
        "state": "on",
        "settings": deepcopy(device["settings"]),
        "action_index": action_index,
    }


def set_smart_plug(
    session: dict[str, Any],
    device_id: str,
    power_state: bool,
    action_index: int | None = None,
) -> dict[str, Any]:
    devices = session.setdefault("devices", {})
    device = devices.setdefault(device_id, {
        "type": "smart_plug",
        "online": True,
        "state": "off",
        "settings": {},
    })

    device["type"] = "smart_plug"
    device["online"] = True
    device["state"] = "on" if power_state else "off"

    action = {
        "action": "set_smart_plug",
        "device_id": device_id,
        "power_state": power_state,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }

    session.setdefault("actions", []).append(action)
    return {
        "device_id": device_id,
        "state": device["state"],
        "action_index": action_index,
    }


def turn_off_device(
    session: dict[str, Any],
    device_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"error": f"Device {device_id} not found", "online": False}

    devices[device_id]["state"] = "off"

    action = {
        "action": "turn_off",
        "device_id": device_id,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }

    session.setdefault("actions", []).append(action)
    return {
        "device_id": device_id,
        "state": "off",
        "action_index": action_index,
    }


def get_all_devices(session: dict[str, Any]) -> list[dict[str, Any]]:
    devices = session.get("devices", {})
    return [
        {"device_id": did, "online": d.get("online", True), **d}
        for did, d in devices.items()
    ]


def get_devices_by_type(session: dict[str, Any], device_type: str) -> list[dict[str, Any]]:
    devices = session.get("devices", {})
    return [
        {"device_id": did, "online": d.get("online", True), **d}
        for did, d in devices.items()
        if d.get("type") == device_type
    ]


def calculate_device_power_consumption(
    session: dict[str, Any],
    device_id: str,
    hours: float,
) -> dict[str, Any]:
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"error": f"Device {device_id} not found"}

    device = devices[device_id]
    if device.get("state") != "on":
        return {"device_id": device_id, "state": "off", "energy_kwh": 0, "estimated_cost": 0}

    power_watts_map = {
        "air_conditioner": 1200,
        "humidifier": 300,
        "smart_plug": 50,
    }

    power_watts = power_watts_map.get(device.get("type"), 100)
    energy_kwh = (power_watts / 1000) * hours

    return {
        "device_id": device_id,
        "power_watts": power_watts,
        "hours": hours,
        "energy_kwh": round(energy_kwh, 3),
    }
