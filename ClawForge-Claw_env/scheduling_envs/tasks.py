"""Task execution functions for scheduling environment."""
from datetime import datetime
from typing import Any


def execute_scheduled_tasks(session: dict[str, Any], current_time: str | None = None, action_index: int | None = None) -> dict[str, Any]:
    """Execute all schedules that are due to run.
    
    Args:
        session: Current session state
        current_time: Optional ISO timestamp to check against (defaults to now)
        action_index: Index of this action for tracking
        
    Returns:
        dict with execution results
    """
    if current_time is None:
        current_time = datetime.now().isoformat()
    
    schedules = session.get("schedules", [])
    devices = session.get("devices", {})
    executed = []
    failed = []
    
    for schedule in schedules:
        if not schedule.get("enabled", False):
            continue
        
        if _is_schedule_due(schedule, current_time):
            device_id = schedule.get("device_id")
            action = schedule.get("action")
            
            if device_id not in devices:
                failed.append({
                    "schedule_id": schedule["schedule_id"],
                    "error": f"Device not found: {device_id}"
                })
                continue
            
            device = devices[device_id]
            old_state = device.get("state")
            
            device["state"] = action
            device["last_triggered"] = "schedule"
            device["last_schedule_id"] = schedule["schedule_id"]
            
            schedule["last_run"] = current_time
            schedule["run_count"] = schedule.get("run_count", 0) + 1
            schedule["next_run"] = _calculate_next_run(schedule)
            
            executed.append({
                "schedule_id": schedule["schedule_id"],
                "schedule_name": schedule.get("schedule_name"),
                "device_id": device_id,
                "action": action,
                "old_state": old_state,
                "new_state": action,
            })
    
    action_record = {
        "action": "execute_scheduled_tasks",
        "executed_count": len(executed),
        "failed_count": len(failed),
        "action_index": action_index,
    }
    session.setdefault("actions", []).append(action_record)
    
    return {
        "success": True,
        "executed": executed,
        "failed": failed,
        "total_executed": len(executed),
        "total_failed": len(failed),
        "action_index": action_index,
    }


def get_next_scheduled_tasks(session: dict[str, Any], limit: int = 10, action_index: int | None = None) -> dict[str, Any]:
    """Get the next scheduled tasks to be executed.
    
    Args:
        session: Current session state
        limit: Maximum number of tasks to return
        action_index: Index of this action for tracking
        
    Returns:
        dict with upcoming tasks
    """
    schedules = session.get("schedules", [])
    
    upcoming = []
    for schedule in schedules:
        if schedule.get("enabled", False) and schedule.get("next_run"):
            upcoming.append({
                "schedule_id": schedule["schedule_id"],
                "schedule_name": schedule.get("schedule_name"),
                "device_id": schedule.get("device_id"),
                "action": schedule.get("action"),
                "next_run": schedule.get("next_run"),
                "repeat_type": schedule.get("repeat_type"),
            })
    
    upcoming.sort(key=lambda x: x["next_run"] or "")
    
    return {
        "success": True,
        "upcoming_tasks": upcoming[:limit],
        "count": len(upcoming),
        "action_index": action_index,
    }


def get_task_execution_history(session: dict[str, Any], schedule_id: str | None = None, limit: int = 50, action_index: int | None = None) -> dict[str, Any]:
    """Get history of task executions.
    
    Args:
        session: Current session state
        schedule_id: Optional filter by schedule ID
        limit: Maximum number of records to return
        action_index: Index of this action for tracking
        
    Returns:
        dict with execution history
    """
    devices = session.get("devices", {})
    
    history = []
    for dev_id, device in devices.items():
        if device.get("last_triggered") == "schedule":
            history.append({
                "device_id": dev_id,
                "device_name": device.get("device_name"),
                "device_type": device.get("device_type"),
                "last_schedule_id": device.get("last_schedule_id"),
                "last_triggered": device.get("last_triggered"),
                "state": device.get("state"),
            })
    
    if schedule_id:
        history = [h for h in history if h.get("last_schedule_id") == schedule_id]
    
    history.sort(key=lambda x: x.get("last_triggered", ""), reverse=True)
    
    return {
        "success": True,
        "history": history[:limit],
        "count": len(history),
        "action_index": action_index,
    }


def _is_schedule_due(schedule: dict[str, Any], current_time: str) -> bool:
    """Check if a schedule is due to execute."""
    if not schedule.get("enabled", False):
        return False
    
    next_run = schedule.get("next_run")
    if not next_run:
        return False
    
    try:
        next_run_dt = datetime.fromisoformat(next_run.replace("Z", "+00:00"))
        current_dt = datetime.fromisoformat(current_time.replace("Z", "+00:00"))
        
        if next_run_dt.tzinfo is not None:
            next_run_dt = next_run_dt.replace(tzinfo=None)
        if current_dt.tzinfo is not None:
            current_dt = current_dt.replace(tzinfo=None)
        
        return current_dt >= next_run_dt
    except (ValueError, AttributeError):
        return False


def _calculate_next_run(schedule: dict[str, Any]) -> str | None:
    """Recalculate next run time for a schedule."""
    from .schedules import _calculate_next_run as calc_next
    
    return calc_next(
        schedule.get("time_spec", "00:00"),
        schedule.get("repeat_type", "once"),
        schedule.get("days_of_week"),
        schedule.get("start_date"),
        schedule.get("end_date")
    )
