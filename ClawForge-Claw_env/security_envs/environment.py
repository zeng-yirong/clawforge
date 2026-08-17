"""Security monitoring environment for home/office intrusion detection and response."""
import logging
import uuid
import threading
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from .repository import DatasetRepository
from .store import SessionStore
from . import doors, zones, alerts, emergency_calls, evidence, notifications

logger = logging.getLogger(__name__)

DEFAULT_STATE_ROOT = Path(__file__).parent / ".session_state"


class SecurityMonitorEnvironment:
    """Security monitoring environment facade.
    
    Provides a unified interface for security monitoring operations including:
    - Door lock/unlock control
    - Zone arming/disarming
    - Intrusion detection and alerts
    - Emergency calls
    - Evidence capture
    - Notification delivery
    
    Closed-loop workflow: detect intrusion -> lock doors -> call emergency -> 
    save evidence -> notify contacts -> evaluate response
    
    Example:
        >>> env = SecurityMonitorEnvironment(scenario_id="intrusion_response")
        >>> env.reset()
        >>> result = env.execute_action("check_intrusion_detected")
        >>> if result["intrusion_detected"]:
        ...     env.execute_action("lock_all_doors")
        ...     env.execute_action("dial_emergency", call_type="police")
    """
    
    def __init__(
        self,
        scenario_id: str = "intrusion_response",
        repository: DatasetRepository | None = None,
        store: SessionStore | None = None,
        config: dict[str, Any] | None = None
    ):
        """Initialize security monitoring environment.
        
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
            "lock_door": {
                "fn": doors.lock_door,
                "params": ["door_id"],
                "description": "Lock a specific door"
            },
            "unlock_door": {
                "fn": doors.unlock_door,
                "params": ["door_id"],
                "description": "Unlock a specific door"
            },
            "lock_all_doors": {
                "fn": doors.lock_all_doors,
                "params": ["zone_id"],
                "description": "Lock all doors, optionally filtered by zone"
            },
            "get_all_doors_status": {
                "fn": doors.get_all_doors_status,
                "params": [],
                "description": "Get status of all doors"
            },
            "arm_zone": {
                "fn": zones.arm_zone,
                "params": ["zone_id"],
                "description": "Arm a specific security zone"
            },
            "disarm_zone": {
                "fn": zones.disarm_zone,
                "params": ["zone_id"],
                "description": "Disarm a specific security zone"
            },
            "arm_all_zones": {
                "fn": zones.arm_all_zones,
                "params": [],
                "description": "Arm all security zones"
            },
            "check_zone_sensors": {
                "fn": zones.check_zone_sensors,
                "params": ["zone_id"],
                "description": "Check sensors in a zone"
            },
            "check_intrusion_detected": {
                "fn": alerts.check_intrusion_detected,
                "params": [],
                "description": "Check if intrusion is currently detected"
            },
            "create_alert": {
                "fn": alerts.create_alert,
                "params": ["alert_type", "zone_id", "description", "severity", "source"],
                "description": "Create a new security alert"
            },
            "acknowledge_alert": {
                "fn": alerts.acknowledge_alert,
                "params": ["alert_id"],
                "description": "Acknowledge an existing alert"
            },
            "resolve_alert": {
                "fn": alerts.resolve_alert,
                "params": ["alert_id", "resolution"],
                "description": "Resolve an alert with a resolution"
            },
            "dial_emergency": {
                "fn": emergency_calls.dial_emergency,
                "params": ["call_type", "description", "location"],
                "description": "Place an emergency call (police/fire/ambulance)"
            },
            "list_emergency_calls": {
                "fn": emergency_calls.list_emergency_calls,
                "params": ["query", "call_type", "status", "limit"],
                "description": "List emergency calls with optional filters"
            },
            "get_emergency_contacts": {
                "fn": emergency_calls.get_emergency_contacts,
                "params": [],
                "description": "Get list of emergency contacts"
            },
            "save_evidence": {
                "fn": evidence.save_evidence,
                "params": ["evidence_type", "description", "source", "metadata"],
                "description": "Save evidence to secure storage"
            },
            "capture_camera_snapshot": {
                "fn": evidence.capture_camera_snapshot,
                "params": ["camera_id", "zone_id"],
                "description": "Capture snapshot from camera"
            },
            "capture_motion_clip": {
                "fn": evidence.capture_motion_clip,
                "params": ["camera_id", "zone_id", "duration_seconds"],
                "description": "Capture motion clip from camera"
            },
            "create_notification": {
                "fn": notifications.create_notification,
                "params": ["notification_type", "recipient_name", "recipient_contact", 
                          "subject", "body", "priority"],
                "description": "Create a new notification"
            },
            "send_notification": {
                "fn": notifications.send_notification,
                "params": ["notification_id"],
                "description": "Send a pending notification"
            },
            "compose_intrusion_notification": {
                "fn": notifications.compose_intrusion_notification,
                "params": ["recipient_name", "recipient_contact", "alert_id"],
                "description": "Compose notification for intrusion alert"
            },
            "list_notifications": {
                "fn": notifications.list_notifications,
                "params": [],
                "description": "List all notifications"
            },
        }
    
    def reset(self) -> dict[str, Any]:
        """Reset environment to initial state for new session.
        
        Loads scenario data and initializes session state including:
        - All doors unlocked
        - All zones disarmed
        - No alerts
        - No evidence recorded
        - No notifications sent
        
        Returns:
            dict containing session initialization summary
        """
        with self._lock:
            logger.info(f"Resetting security environment for scenario: {self.scenario_id}")
            
            scenario_data = self.repository.load_scenario(self.scenario_id)
            doors_data = self.repository.load_doors()
            zones_data = self.repository.load_zones()
            contacts_data = self.repository.load_contacts()
            
            session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:8]}"
            
            doors_state = {}
            for door_id, door_info in doors_data.items():
                doors_state[door_id] = {
                    "locked": False,
                    "door_name": door_info.get("door_name", door_id),
                    "location": door_info.get("location", "unknown"),
                    "zone_id": door_info.get("zone_id", "unassigned")
                }
            
            zones_state = {}
            for zone_id, zone_info in zones_data.items():
                zones_state[zone_id] = {
                    "armed": False,
                    "zone_name": zone_info.get("zone_name", zone_id),
                    "sensors": zone_info.get("sensors", []),
                    "intrusion_detected": False,
                    "last_sensor_triggered": None
                }
            
            initial_state = {
                "session_id": session_id,
                "scenario_id": self.scenario_id,
                "scenario_name": scenario_data.get("name", self.scenario_id),
                "doors": doors_state,
                "zones": zones_state,
                "contacts": contacts_data,
                "alerts": [],
                "emergency_calls": [],
                "evidence": [],
                "notifications": [],
                "action_history": [],
                "metrics": {
                    "total_actions": 0,
                    "intrusions_detected": 0,
                    "doors_locked": 0,
                    "emergency_calls_made": 0,
                    "evidence_saved": 0,
                    "notifications_sent": 0
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
                "doors_count": len(doors_state),
                "zones_count": len(zones_state),
                "contacts_count": len(contacts_data),
                "message": "Security environment initialized successfully"
            }
    
    def _load_current_session(self) -> dict[str, Any]:
        """Load current session state."""
        if self._current_session_id is None:
            raise RuntimeError("No active session. Call reset() first.")
        return self.store.load_session(self._current_session_id)
    
    def _save_current_session(self, session: dict[str, Any]) -> None:
        """Save current session state."""
        if self._current_session_id is None:
            raise RuntimeError("No active session. Call reset() first.")
        self.store.save_session(self._current_session_id, session)
    
    def get_state(self) -> dict[str, Any]:
        """Get current environment state.
        
        Returns:
            dict containing full current state
        """
        with self._lock:
            session = self._load_current_session()
            return session.copy()
    
    def execute_action(self, action_name: str, **kwargs) -> dict[str, Any]:
        """Execute a security monitoring action.
        
        Args:
            action_name: Name of action to execute
            **kwargs: Action parameters
            
        Returns:
            dict containing action result
            
        Raises:
            ValueError: If action_name is not found in registry
        """
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
                    try:
                        result = fn(session, action_index=action_index, **kwargs)
                    except TypeError as exc:
                        if "action_index" not in str(exc):
                            raise
                        result = fn(session, **kwargs)
                    if isinstance(result, dict) and "action_index" in result:
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
        if not isinstance(result, dict):
            return
        succeeded = result.get("success", "error" not in result)
        if action_name == "check_intrusion_detected" and result.get("intrusion_detected"):
            session["metrics"]["intrusions_detected"] = session["metrics"].get("intrusions_detected", 0) + 1
        elif action_name in ("lock_door", "lock_all_doors") and succeeded:
            session["metrics"]["doors_locked"] = session["metrics"].get("doors_locked", 0) + result.get("doors_locked_count", 1)
        elif action_name == "dial_emergency" and succeeded:
            session["metrics"]["emergency_calls_made"] = session["metrics"].get("emergency_calls_made", 0) + 1
        elif action_name in ("save_evidence", "capture_camera_snapshot", "capture_motion_clip") and succeeded:
            session["metrics"]["evidence_saved"] = session["metrics"].get("evidence_saved", 0) + 1
        elif action_name == "send_notification" and succeeded:
            session["metrics"]["notifications_sent"] = session["metrics"].get("notifications_sent", 0) + 1
    
    def get_available_actions(self) -> list[dict[str, Any]]:
        """Get list of all available actions with their descriptions.
        
        Returns:
            list of dicts containing action info
        """
        return [
            {
                "action": name,
                "description": info["description"],
                "parameters": info["params"]
            }
            for name, info in self._action_registry.items()
        ]
    
    def get_security_status(self) -> dict[str, Any]:
        """Get comprehensive security status.
        
        Returns:
            dict with doors, zones, alerts, and active threats summary
        """
        with self._lock:
            session = self._load_current_session()
            
            doors_state = session.get("doors", {})
            zones_state = session.get("zones", {})
            alerts = session.get("alerts", [])
            
            locked_doors = sum(1 for d in doors_state.values() if d.get("locked", False))
            armed_zones = sum(1 for z in zones_state.values() if z.get("armed", False))
            active_alerts = [a for a in alerts if a.get("status") == "active"]
            
            intrusion_zones = [
                zone_id for zone_id, zone in zones_state.items()
                if zone.get("intrusion_detected", False)
            ]
            
            return {
                "session_id": session.get("session_id"),
                "doors": {
                    "total": len(doors_state),
                    "locked": locked_doors,
                    "unlocked": len(doors_state) - locked_doors
                },
                "zones": {
                    "total": len(zones_state),
                    "armed": armed_zones,
                    "disarmed": len(zones_state) - armed_zones
                },
                "alerts": {
                    "total": len(alerts),
                    "active": len(active_alerts),
                    "resolved": len(alerts) - len(active_alerts)
                },
                "intrusion_detected": len(intrusion_zones) > 0,
                "intrusion_zones": intrusion_zones,
                "metrics": session.get("metrics", {})
            }
    
    def run_closed_loop_response(self) -> dict[str, Any]:
        """Run automated closed-loop security response.
        
        Executes the full security response workflow:
        1. Check for intrusion
        2. Lock all doors
        3. Dial emergency
        4. Save evidence
        5. Notify contacts
        
        Returns:
            dict with results of each step
        """
        results = {}
        
        check_result = self.execute_action("check_intrusion_detected")
        results["check_intrusion"] = check_result
        
        if check_result.get("intrusion_detected"):
            lock_result = self.execute_action("lock_all_doors")
            results["lock_doors"] = lock_result
            
            session = self._load_current_session()
            active_alerts = [a for a in session.get("alerts", []) if a.get("status") == "active"]
            
            if active_alerts:
                alert = active_alerts[0]
                
                dial_result = self.execute_action(
                    "dial_emergency",
                    call_type="police",
                    description=f"Intrusion detected in zone: {alert.get('zone_id')}",
                    location=alert.get("location", "unknown")
                )
                results["emergency_call"] = dial_result
                
                evidence_result = self.execute_action(
                    "save_evidence",
                    evidence_type="intrusion_event",
                    description=f"Evidence of intrusion in zone {alert.get('zone_id')}",
                    source="automated_capture",
                    metadata={"alert_id": alert.get("alert_id"), "severity": alert.get("severity")}
                )
                results["save_evidence"] = evidence_result
                
                contacts = session.get("contacts", {}).get("security_contacts", [])
                notification_results = []
                for contact in contacts:
                    notif_result = self.execute_action(
                        "compose_intrusion_notification",
                        recipient_name=contact.get("name", "Security Contact"),
                        recipient_contact=contact.get("phone", contact.get("email", "")),
                        alert_id=alert.get("alert_id")
                    )
                    if notif_result.get("success"):
                        send_result = self.execute_action("send_notification", notification_id=notif_result.get("notification_id"))
                        notification_results.append(send_result)
                
                results["notifications"] = notification_results
        
        return results
    
    def evaluate_response(self) -> dict[str, Any]:
        """Evaluate the security response quality.
        
        Returns:
            dict with evaluation scores and feedback
        """
        from .evaluator import SecurityEvaluator
        
        with self._lock:
            session = self._load_current_session()
            scenario_data = self.repository.load_scenario(self.scenario_id)
            
            evaluator = SecurityEvaluator(scenario=scenario_data)
            return evaluator.evaluate(session)
