"""Device control functions for scheduling environment."""
from typing import Any


def turn_on_device(session: dict[str, Any], device_id: str, action_index: int | None = None) -> dict[str, Any]:
    """Turn on a device.
    
    Args:
        session: Current session state
        device_id: ID of device to turn on
        action_index: Index of this action for tracking
        
    Returns:
        dict with success status and device state
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    devices[device_id]["state"] = "on"
    devices[device_id]["last_triggered"] = "auto"
    
    action_record = {
        "action": "turn_on_device",
        "device_id": device_id,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "device_id": device_id,
        "device_name": devices[device_id].get("device_name", device_id),
        "state": "on",
        "action_index": action_index,
    }


def turn_off_device(session: dict[str, Any], device_id: str, action_index: int | None = None) -> dict[str, Any]:
    """Turn off a device.
    
    Args:
        session: Current session state
        device_id: ID of device to turn off
        action_index: Index of this action for tracking
        
    Returns:
        dict with success status and device state
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    devices[device_id]["state"] = "off"
    devices[device_id]["last_triggered"] = "auto"
    
    action_record = {
        "action": "turn_off_device",
        "device_id": device_id,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "device_id": device_id,
        "device_name": devices[device_id].get("device_name", device_id),
        "state": "off",
        "action_index": action_index,
    }


def set_device_setting(session: dict[str, Any], device_id: str, setting: str, value: Any, action_index: int | None = None) -> dict[str, Any]:
    """Set a specific setting on a device.
    
    Args:
        session: Current session state
        device_id: ID of device
        setting: Setting name (e.g., 'temperature', 'brightness')
        value: New value for setting
        action_index: Index of this action for tracking
        
    Returns:
        dict with success status and updated setting
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    device = devices[device_id]
    device_type = device.get("device_type", "")
    
    if setting not in device.get("supported_settings", []):
        return {"success": False, "error": f"Setting '{setting}' not supported by device type '{device_type}'"}
    
    device["settings"][setting] = value
    
    action_record = {
        "action": "set_device_setting",
        "device_id": device_id,
        "setting": setting,
        "value": value,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "device_id": device_id,
        "setting": setting,
        "value": value,
        "action_index": action_index,
    }


def get_device_status(session: dict[str, Any], device_id: str, action_index: int | None = None) -> dict[str, Any]:
    """Get current status of a device.
    
    Args:
        session: Current session state
        device_id: ID of device
        action_index: Index of this action for tracking
        
    Returns:
        dict with device status information
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    device = devices[device_id]
    
    return {
        "success": True,
        "device_id": device_id,
        "device_name": device.get("device_name"),
        "device_type": device.get("device_type"),
        "state": device.get("state"),
        "settings": device.get("settings", {}),
        "last_triggered": device.get("last_triggered"),
        "action_index": action_index,
    }


def get_all_devices(session: dict[str, Any], device_type: str | None = None, action_index: int | None = None) -> dict[str, Any]:
    """Get all devices, optionally filtered by type.
    
    Args:
        session: Current session state
        device_type: Optional filter by device type
        action_index: Index of this action for tracking
        
    Returns:
        dict with list of devices
    """
    devices = session.get("devices", {})
    
    filtered = {}
    for dev_id, dev_info in devices.items():
        if device_type is None or dev_info.get("device_type") == device_type:
            filtered[dev_id] = dev_info
    
    return {
        "success": True,
        "devices": filtered,
        "count": len(filtered),
        "action_index": action_index,
    }


def get_devices_by_type(session: dict[str, Any], device_type: str, action_index: int | None = None) -> dict[str, Any]:
    """Get all devices of a specific type.
    
    Args:
        session: Current session state
        device_type: Type of devices to get
        action_index: Index of this action for tracking
        
    Returns:
        dict with list of devices of specified type
    """
    return get_all_devices(session, device_type=device_type, action_index=action_index)


def control_light(session: dict[str, Any], device_id: str, action: str, brightness: int | None = None, action_index: int | None = None) -> dict[str, Any]:
    """Control a light device.
    
    Args:
        session: Current session state
        device_id: ID of light device
        action: 'on' or 'off'
        brightness: Optional brightness level (0-100)
        action_index: Index of this action for tracking
        
    Returns:
        dict with control result
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    device = devices[device_id]
    if device.get("device_type") != "light":
        return {"success": False, "error": f"Device {device_id} is not a light"}
    
    if action == "on":
        device["state"] = "on"
        if brightness is not None:
            device["settings"]["brightness"] = brightness
    else:
        device["state"] = "off"
    
    device["last_triggered"] = "auto"
    
    action_record = {
        "action": "control_light",
        "device_id": device_id,
        "action": action,
        "brightness": brightness,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "device_id": device_id,
        "state": device["state"],
        "brightness": device["settings"].get("brightness"),
        "action_index": action_index,
    }


def control_ac(session: dict[str, Any], device_id: str, action: str, temperature: float | None = None, mode: str | None = None, action_index: int | None = None) -> dict[str, Any]:
    """Control an air conditioner device.
    
    Args:
        session: Current session state
        device_id: ID of AC device
        action: 'on' or 'off'
        temperature: Optional target temperature
        mode: Optional mode ('cool', 'heat', 'fan', 'auto')
        action_index: Index of this action for tracking
        
    Returns:
        dict with control result
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    device = devices[device_id]
    if device.get("device_type") != "ac":
        return {"success": False, "error": f"Device {device_id} is not an AC"}
    
    if action == "on":
        device["state"] = "on"
        if temperature is not None:
            device["settings"]["temperature"] = temperature
        if mode is not None:
            device["settings"]["mode"] = mode
    else:
        device["state"] = "off"
    
    device["last_triggered"] = "auto"
    
    action_record = {
        "action": "control_ac",
        "device_id": device_id,
        "action": action,
        "temperature": temperature,
        "mode": mode,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "device_id": device_id,
        "state": device["state"],
        "temperature": device["settings"].get("temperature"),
        "mode": device["settings"].get("mode"),
        "action_index": action_index,
    }


def control_humidifier(session: dict[str, Any], device_id: str, action: str, humidity_level: int | None = None, action_index: int | None = None) -> dict[str, Any]:
    """Control a humidifier device.
    
    Args:
        session: Current session state
        device_id: ID of humidifier device
        action: 'on' or 'off'
        humidity_level: Optional target humidity level (0-100)
        action_index: Index of this action for tracking
        
    Returns:
        dict with control result
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    device = devices[device_id]
    if device.get("device_type") != "humidifier":
        return {"success": False, "error": f"Device {device_id} is not a humidifier"}
    
    if action == "on":
        device["state"] = "on"
        if humidity_level is not None:
            device["settings"]["humidity_level"] = humidity_level
    else:
        device["state"] = "off"
    
    device["last_triggered"] = "auto"
    
    action_record = {
        "action": "control_humidifier",
        "device_id": device_id,
        "action": action,
        "humidity_level": humidity_level,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "device_id": device_id,
        "state": device["state"],
        "humidity_level": device["settings"].get("humidity_level"),
        "action_index": action_index,
    }


def control_smart_plug(session: dict[str, Any], device_id: str, action: str, action_index: int | None = None) -> dict[str, Any]:
    """Control a smart plug device.
    
    Args:
        session: Current session state
        device_id: ID of smart plug device
        action: 'on' or 'off'
        action_index: Index of this action for tracking
        
    Returns:
        dict with control result
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    device = devices[device_id]
    if device.get("device_type") != "smart_plug":
        return {"success": False, "error": f"Device {device_id} is not a smart plug"}
    
    device["state"] = "on" if action == "on" else "off"
    device["last_triggered"] = "auto"
    
    action_record = {
        "action": "control_smart_plug",
        "device_id": device_id,
        "action": action,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "device_id": device_id,
        "state": device["state"],
        "action_index": action_index,
    }
