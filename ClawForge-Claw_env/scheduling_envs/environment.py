"""Scheduling environment for device automation with custom timed tasks."""
import logging
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from .repository import DatasetRepository
from .store import SessionStore
from . import devices, schedules, tasks

logger = logging.getLogger(__name__)

DEFAULT_STATE_ROOT = Path(__file__).parent / ".session_state"


class SchedulingEnvironment:
    """Scheduling environment facade.
    
    Provides a unified interface for device scheduling operations including:
    - Device control (lights, AC, humidifiers, smart plugs)
    - Schedule creation and management
    - Task execution (single/recurring)
    - Automatic device start/stop
    
    Workflow: create schedule -> enable schedule -> execute tasks -> auto control devices
    
    Example:
        >>> env = SchedulingEnvironment(scenario_id="device_scheduling")
        >>> env.reset()
        >>> result = env.execute_action("create_schedule", schedule_name="Morning Light", device_id="light_001", action="on", time_spec="07:00", repeat_type="daily")
    """
    
    def __init__(
        self,
        scenario_id: str = "device_scheduling",
        repository: DatasetRepository | None = None,
        store: SessionStore | None = None,
        config: dict[str, Any] | None = None
    ):
        """Initialize scheduling environment.
        
        Args:
            scenario_id: ID of scenario to load for session initialization
            repository: Optional DatasetRepository instance (creates default if None)
            store: Optional SessionStore instance (creates default if None)
            config: Optional configuration overrides
        """
        self.scenario_id = scenario_id
        self.repository = repository or DatasetRepository()
        state_root = config.get("state_root", DEFAULT_STATE_ROOT) if config else DEFAULT_STATE_ROOT
        self.store = store or SessionStore(state_root=state_root)
        self.config = config or {}
        self._lock = threading.Lock()
        self._initialized = False
        self._current_session_id: str | None = None
        self._action_registry = self._build_action_registry()
    
    def _build_action_registry(self) -> dict[str, dict[str, Any]]:
        """Build action registry mapping action names to their implementations."""
        return {
            "turn_on_device": {
                "fn": devices.turn_on_device,
                "params": ["device_id"],
                "description": "Turn on a device"
            },
            "turn_off_device": {
                "fn": devices.turn_off_device,
                "params": ["device_id"],
                "description": "Turn off a device"
            },
            "set_device_setting": {
                "fn": devices.set_device_setting,
                "params": ["device_id", "setting", "value"],
                "description": "Set a device setting"
            },
            "get_device_status": {
                "fn": devices.get_device_status,
                "params": ["device_id"],
                "description": "Get device status"
            },
            "get_all_devices": {
                "fn": devices.get_all_devices,
                "params": ["device_type"],
                "description": "Get all devices"
            },
            "get_devices_by_type": {
                "fn": devices.get_devices_by_type,
                "params": ["device_type"],
                "description": "Get devices by type"
            },
            "control_light": {
                "fn": devices.control_light,
                "params": ["device_id", "action"],
                "description": "Control a light device"
            },
            "control_ac": {
                "fn": devices.control_ac,
                "params": ["device_id", "action"],
                "description": "Control an AC device"
            },
            "control_humidifier": {
                "fn": devices.control_humidifier,
                "params": ["device_id", "action"],
                "description": "Control a humidifier device"
            },
            "control_smart_plug": {
                "fn": devices.control_smart_plug,
                "params": ["device_id", "action"],
                "description": "Control a smart plug device"
            },
            "create_schedule": {
                "fn": schedules.create_schedule,
                "params": ["schedule_name", "device_id", "action", "time_spec", "repeat_type"],
                "description": "Create a new schedule"
            },
            "update_schedule": {
                "fn": schedules.update_schedule,
                "params": ["schedule_id"],
                "description": "Update a schedule"
            },
            "delete_schedule": {
                "fn": schedules.delete_schedule,
                "params": ["schedule_id"],
                "description": "Delete a schedule"
            },
            "enable_schedule": {
                "fn": schedules.enable_schedule,
                "params": ["schedule_id"],
                "description": "Enable a schedule"
            },
            "disable_schedule": {
                "fn": schedules.disable_schedule,
                "params": ["schedule_id"],
                "description": "Disable a schedule"
            },
            "get_schedule": {
                "fn": schedules.get_schedule,
                "params": ["schedule_id"],
                "description": "Get schedule details"
            },
            "list_schedules": {
                "fn": schedules.list_schedules,
                "params": ["enabled"],
                "description": "List all schedules"
            },
            "execute_scheduled_tasks": {
                "fn": tasks.execute_scheduled_tasks,
                "params": ["current_time"],
                "description": "Execute due scheduled tasks"
            },
            "get_next_scheduled_tasks": {
                "fn": tasks.get_next_scheduled_tasks,
                "params": ["limit"],
                "description": "Get upcoming scheduled tasks"
            },
            "get_task_execution_history": {
                "fn": tasks.get_task_execution_history,
                "params": ["schedule_id"],
                "description": "Get task execution history"
            },
        }
    
    def _load_current_session(self) -> dict[str, Any]:
        """Load current session from store."""
        if self._current_session_id is None:
            raise RuntimeError("No active session. Call reset() first.")
        session = self.store.load_session(self._current_session_id)
        if session is None:
            raise RuntimeError(f"Session {self._current_session_id} not found.")
        return session
    
    def _save_current_session(self, session: dict[str, Any]) -> None:
        """Save current session state."""
        if self._current_session_id is None:
            raise RuntimeError("No active session. Call reset() first.")
        self.store.save_session(self._current_session_id, session)
    
    def get_state(self) -> dict[str, Any]:
        """Get current environment state."""
        with self._lock:
            session = self._load_current_session()
            return session.copy()
    
    def reset(self) -> dict[str, Any]:
        """Reset environment to initial state for new session."""
        with self._lock:
            logger.info(f"Resetting scheduling environment for scenario: {self.scenario_id}")
            
            scenario_data = self.repository.load_scenario(self.scenario_id)
            devices_data = self.repository.load_devices()
            
            session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:8]}"
            
            devices_state = {}
            for device_id, device_info in devices_data.items():
                devices_state[device_id] = {
                    **device_info,
                    "state": "off",
                    "last_triggered": None,
                    "last_schedule_id": None,
                }
            
            initial_state = {
                "session_id": session_id,
                "scenario_id": self.scenario_id,
                "scenario_name": scenario_data.get("name", self.scenario_id),
                "devices": devices_state,
                "schedules": [],
                "actions": [],
                "metrics": {
                    "total_actions": 0,
                    "schedules_created": 0,
                    "tasks_executed": 0,
                    "devices_controlled": 0,
                }
            }
            
            if "initial_state" in scenario_data:
                initial_state.update(scenario_data["initial_state"])
            
            self.store.create_session(session_id, initial_state)
            self._current_session_id = session_id
            self._initialized = True
            
            logger.info(f"Session {session_id} created successfully")
            
            return {
                "session_id": session_id,
                "scenario": initial_state["scenario_name"],
                "devices_count": len(devices_state),
            }
    
    def execute_action(self, action_name: str, **kwargs) -> dict[str, Any]:
        """Execute a scheduling action."""
        with self._lock:
            if not self._initialized:
                return {"error": "Environment not initialized. Call reset() first."}
            
            if action_name not in self._action_registry:
                available = list(self._action_registry.keys())
                return {
                    "success": False,
                    "error": f"Unknown action: {action_name}",
                    "available_actions": available
                }
            
            action_info = self._action_registry[action_name]
            fn = action_info["fn"]
            required_params = action_info["params"]
            
            missing_params = [p for p in required_params if p not in kwargs]
            if missing_params:
                return {
                    "success": False,
                    "error": f"Missing required parameters: {missing_params}",
                    "required_params": required_params
                }
            
            try:
                if self._current_session_id is None:
                    raise RuntimeError("No active session. Call reset() first.")
                with self.store.session_lock(self._current_session_id):
                    session = self._load_current_session()
                    action_index = session.get("metrics", {}).get("total_actions", 0)
                    result = fn(session, action_index=action_index, **kwargs)
                    if "action_index" in result:
                        session["metrics"]["total_actions"] = action_index + 1
                    self._update_metrics(session, action_name, result)
                    self.store.save_session_unlocked(self._current_session_id, session)
                
                return result
                
            except Exception as e:
                logger.exception(f"Error executing action {action_name}")
                return {
                    "success": False,
                    "error": str(e),
                    "action": action_name
                }
    
    def _update_metrics(self, session: dict[str, Any], action_name: str, result: dict[str, Any]) -> None:
        """Update session metrics based on action results."""
        if result.get("success", False):
            if action_name in ("create_schedule", "update_schedule"):
                session["metrics"]["schedules_created"] = session["metrics"].get("schedules_created", 0) + 1
            elif action_name == "execute_scheduled_tasks":
                session["metrics"]["tasks_executed"] = session["metrics"].get("tasks_executed", 0) + result.get("total_executed", 0)
            elif action_name.startswith(("turn_", "control_", "set_")):
                session["metrics"]["devices_controlled"] = session["metrics"].get("devices_controlled", 0) + 1
    
    def get_available_actions(self) -> list[dict[str, Any]]:
        """Get list of all available actions with their descriptions."""
        return [
            {
                "action": name,
                "description": info["description"],
                "parameters": info["params"]
            }
            for name, info in self._action_registry.items()
        ]
    
    def get_scheduling_status(self) -> dict[str, Any]:
        """Get comprehensive scheduling status."""
        with self._lock:
            session = self._load_current_session()
            
            devices_state = session.get("devices", {})
            schedules_list = session.get("schedules", [])
            
            enabled_schedules = [s for s in schedules_list if s.get("enabled", False)]
            on_devices = sum(1 for d in devices_state.values() if d.get("state") == "on")
            
            device_types = {}
            for device in devices_state.values():
                dev_type = device.get("device_type", "unknown")
                device_types[dev_type] = device_types.get(dev_type, 0) + 1
            
            return {
                "session_id": session.get("session_id"),
                "devices": {
                    "total": len(devices_state),
                    "on": on_devices,
                    "off": len(devices_state) - on_devices,
                    "by_type": device_types,
                },
                "schedules": {
                    "total": len(schedules_list),
                    "enabled": len(enabled_schedules),
                    "disabled": len(schedules_list) - len(enabled_schedules),
                },
                "metrics": session.get("metrics", {})
            }
    
    def evaluate_session(self) -> dict[str, Any]:
        """Evaluate current session performance."""
        with self._lock:
            from .evaluator import ScheduleEvaluator
            session = self._load_current_session()
            scenario = self.repository.load_scenario(self.scenario_id)
            evaluator = ScheduleEvaluator(scenario=scenario)
            return evaluator.evaluate(session)
    
    def session_summary(self) -> dict[str, Any]:
        """Get summary of current session."""
        with self._lock:
            session = self._load_current_session()
            devices_state = session.get("devices", {})
            schedules_list = session.get("schedules", [])
            on_devices = sum(1 for d in devices_state.values() if d.get("state") == "on")
            return {
                "session_id": session.get("session_id"),
                "scenario_id": session.get("scenario_id"),
                "total_devices": len(devices_state),
                "devices_on": on_devices,
                "total_schedules": len(schedules_list),
                "enabled_schedules": sum(1 for s in schedules_list if s.get("enabled", False)),
                "total_actions": session.get("metrics", {}).get("total_actions", 0),
            }
