"""Schedule management functions for scheduling environment."""
from datetime import datetime
from typing import Any


def create_schedule(
    session: dict[str, Any],
    schedule_name: str,
    device_id: str,
    action: str,
    time_spec: str,
    repeat_type: str,
    days_of_week: list[int] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    action_index: int | None = None
) -> dict[str, Any]:
    """Create a new schedule.
    
    Args:
        session: Current session state
        schedule_name: Human-readable name for the schedule
        device_id: ID of device to control
        action: Action to perform ('on' or 'off')
        time_spec: Time in HH:MM format (e.g., '08:00')
        repeat_type: 'once', 'daily', 'weekly', 'custom'
        days_of_week: List of days (0=Monday, 6=Sunday) for weekly/custom
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        action_index: Index of this action for tracking
        
    Returns:
        dict with created schedule info
    """
    devices = session.get("devices", {})
    if device_id not in devices:
        return {"success": False, "error": f"Device not found: {device_id}"}
    
    schedules = session.setdefault("schedules", [])
    
    schedule_id = f"sched_{len(schedules) + 1:03d}"
    
    schedule = {
        "schedule_id": schedule_id,
        "schedule_name": schedule_name,
        "device_id": device_id,
        "action": action,
        "time_spec": time_spec,
        "repeat_type": repeat_type,
        "days_of_week": days_of_week or [],
        "start_date": start_date,
        "end_date": end_date,
        "enabled": True,
        "last_run": None,
        "next_run": _calculate_next_run(time_spec, repeat_type, days_of_week, start_date, end_date),
        "run_count": 0,
    }
    
    schedules.append(schedule)
    
    action_record = {
        "action": "create_schedule",
        "schedule_id": schedule_id,
        "schedule_name": schedule_name,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "schedule": schedule,
        "action_index": action_index,
    }


def update_schedule(
    session: dict[str, Any],
    schedule_id: str,
    schedule_name: str | None = None,
    time_spec: str | None = None,
    repeat_type: str | None = None,
    days_of_week: list[int] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    enabled: bool | None = None,
    action_index: int | None = None
) -> dict[str, Any]:
    """Update an existing schedule.
    
    Args:
        session: Current session state
        schedule_id: ID of schedule to update
        schedule_name: New name (optional)
        time_spec: New time in HH:MM format (optional)
        repeat_type: New repeat type (optional)
        days_of_week: New days of week (optional)
        start_date: New start date (optional)
        end_date: New end date (optional)
        enabled: New enabled state (optional)
        action_index: Index of this action for tracking
        
    Returns:
        dict with updated schedule info
    """
    schedules = session.setdefault("schedules", [])
    
    target = None
    for sched in schedules:
        if sched["schedule_id"] == schedule_id:
            target = sched
            break
    
    if target is None:
        return {"success": False, "error": f"Schedule not found: {schedule_id}"}
    
    if schedule_name is not None:
        target["schedule_name"] = schedule_name
    if time_spec is not None:
        target["time_spec"] = time_spec
    if repeat_type is not None:
        target["repeat_type"] = repeat_type
    if days_of_week is not None:
        target["days_of_week"] = days_of_week
    if start_date is not None:
        target["start_date"] = start_date
    if end_date is not None:
        target["end_date"] = end_date
    if enabled is not None:
        target["enabled"] = enabled
    
    target["next_run"] = _calculate_next_run(
        target["time_spec"],
        target["repeat_type"],
        target["days_of_week"],
        target["start_date"],
        target["end_date"]
    )
    
    action_record = {
        "action": "update_schedule",
        "schedule_id": schedule_id,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "schedule": target,
        "action_index": action_index,
    }


def delete_schedule(session: dict[str, Any], schedule_id: str, action_index: int | None = None) -> dict[str, Any]:
    """Delete a schedule.
    
    Args:
        session: Current session state
        schedule_id: ID of schedule to delete
        action_index: Index of this action for tracking
        
    Returns:
        dict with deletion result
    """
    schedules = session.setdefault("schedules", [])
    
    original_len = len(schedules)
    schedules = [s for s in schedules if s["schedule_id"] != schedule_id]
    
    if len(schedules) == original_len:
        return {"success": False, "error": f"Schedule not found: {schedule_id}"}
    
    session["schedules"] = schedules
    
    action_record = {
        "action": "delete_schedule",
        "schedule_id": schedule_id,
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "schedule_id": schedule_id,
        "action_index": action_index,
    }


def enable_schedule(session: dict[str, Any], schedule_id: str, action_index: int | None = None) -> dict[str, Any]:
    """Enable a schedule.
    
    Args:
        session: Current session state
        schedule_id: ID of schedule to enable
        action_index: Index of this action for tracking
        
    Returns:
        dict with updated schedule info
    """
    return update_schedule(session, schedule_id, enabled=True, action_index=action_index)


def disable_schedule(session: dict[str, Any], schedule_id: str, action_index: int | None = None) -> dict[str, Any]:
    """Disable a schedule.
    
    Args:
        session: Current session state
        schedule_id: ID of schedule to disable
        action_index: Index of this action for tracking
        
    Returns:
        dict with updated schedule info
    """
    return update_schedule(session, schedule_id, enabled=False, action_index=action_index)


def get_schedule(session: dict[str, Any], schedule_id: str, action_index: int | None = None) -> dict[str, Any]:
    """Get details of a specific schedule.
    
    Args:
        session: Current session state
        schedule_id: ID of schedule to get
        action_index: Index of this action for tracking
        
    Returns:
        dict with schedule details
    """
    schedules = session.setdefault("schedules", [])
    
    for sched in schedules:
        if sched["schedule_id"] == schedule_id:
            return {
                "success": True,
                "schedule": sched,
                "action_index": action_index,
            }
    
    return {"success": False, "error": f"Schedule not found: {schedule_id}"}


def list_schedules(session: dict[str, Any], enabled: bool | None = None, device_id: str | None = None, action_index: int | None = None) -> dict[str, Any]:
    """List all schedules with optional filters.
    
    Args:
        session: Current session state
        enabled: Optional filter by enabled state
        device_id: Optional filter by device
        action_index: Index of this action for tracking
        
    Returns:
        dict with list of schedules
    """
    schedules = session.setdefault("schedules", [])
    
    filtered = schedules
    if enabled is not None:
        filtered = [s for s in filtered if s.get("enabled") == enabled]
    if device_id is not None:
        filtered = [s for s in filtered if s.get("device_id") == device_id]
    
    return {
        "success": True,
        "schedules": filtered,
        "count": len(filtered),
        "action_index": action_index,
    }


def _calculate_next_run(time_spec: str, repeat_type: str, days_of_week: list[int] | None, start_date: str | None, end_date: str | None) -> str | None:
    """Calculate the next run time for a schedule."""
    now = datetime.now()
    try:
        hour, minute = map(int, time_spec.split(":"))
    except ValueError:
        return None
    
    if repeat_type == "once":
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                next_run = start_dt.replace(hour=hour, minute=minute)
                if next_run > now:
                    return next_run.isoformat()
            except ValueError:
                pass
        return None
    
    elif repeat_type == "daily":
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            from datetime import timedelta
            next_run += timedelta(days=1)
        return next_run.isoformat()
    
    elif repeat_type == "weekly" and days_of_week:
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        from datetime import timedelta
        for _ in range(8):
            if next_run.weekday() in days_of_week and next_run > now:
                return next_run.isoformat()
            next_run += timedelta(days=1)
        return None
    
    elif repeat_type == "custom" and days_of_week:
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        from datetime import timedelta
        for _ in range(8):
            if next_run.weekday() in days_of_week and next_run > now:
                return next_run.isoformat()
            next_run += timedelta(days=1)
        return None
    
    return None
