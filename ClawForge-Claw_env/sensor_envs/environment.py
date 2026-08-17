"""Sensor monitoring environment for real-time data collection and anomaly detection."""
import logging
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from .repository import DatasetRepository
from .store import SessionStore
from . import sensors, monitoring, alerts, reports, trends, notifications

logger = logging.getLogger(__name__)

DEFAULT_STATE_ROOT = Path(__file__).parent / ".session_state"


class SensorMonitorEnvironment:
    """Sensor monitoring environment facade.
    
    Provides a unified interface for sensor monitoring operations including:
    - Real-time sensor data reading
    - Anomaly detection and monitoring
    - Alert management
    - Report generation (hourly/daily/monthly)
    - Trend analysis
    - Notification delivery
    
    Workflow: collect sensor data -> detect anomalies -> generate alerts ->
    create notifications -> produce reports and trend analysis
    
    Example:
        >>> env = SensorMonitorEnvironment(scenario_id="sensor_monitoring")
        >>> env.reset()
        >>> result = env.execute_action("read_sensor_data", sensor_id="temp_001")
        >>> result = env.execute_action("check_anomalies")
    """
    
    def __init__(
        self,
        scenario_id: str = "sensor_monitoring",
        repository: DatasetRepository | None = None,
        store: SessionStore | None = None,
        config: dict[str, Any] | None = None
    ):
        """Initialize sensor monitoring environment.
        
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
            "read_sensor_data": {
                "fn": sensors.read_sensor_data,
                "params": ["sensor_id"],
                "description": "Read current sensor data"
            },
            "read_all_sensors_current": {
                "fn": sensors.read_all_sensors_current,
                "params": ["sensor_type", "location_id"],
                "description": "Read all sensors current values"
            },
            "get_sensor_thresholds": {
                "fn": sensors.get_sensor_thresholds,
                "params": ["sensor_id"],
                "description": "Get sensor thresholds"
            },
            "set_sensor_threshold": {
                "fn": sensors.set_sensor_threshold,
                "params": ["sensor_id", "threshold_low", "threshold_high"],
                "description": "Set sensor thresholds"
            },
            "get_sensors_by_type": {
                "fn": sensors.get_sensors_by_type,
                "params": ["sensor_type"],
                "description": "Get sensors by type"
            },
            "get_sensors_by_location": {
                "fn": sensors.get_sensors_by_location,
                "params": ["location_id"],
                "description": "Get sensors by location"
            },
            "get_sensor_stats": {
                "fn": sensors.get_sensor_stats,
                "params": ["sensor_id", "start_time", "end_time"],
                "description": "Get sensor statistics for time range"
            },
            "check_anomalies": {
                "fn": monitoring.check_anomalies,
                "params": ["sensor_id", "severity"],
                "description": "Check all anomalies"
            },
            "detect_anomaly": {
                "fn": monitoring.detect_anomaly,
                "params": ["sensor_id", "value"],
                "description": "Detect anomaly for sensor value"
            },
            "acknowledge_anomaly": {
                "fn": monitoring.acknowledge_anomaly,
                "params": ["anomaly_id"],
                "description": "Acknowledge an anomaly"
            },
            "resolve_anomaly": {
                "fn": monitoring.resolve_anomaly,
                "params": ["anomaly_id", "resolution"],
                "description": "Resolve an anomaly"
            },
            "get_monitoring_summary": {
                "fn": monitoring.get_monitoring_summary,
                "params": [],
                "description": "Get monitoring summary"
            },
            "create_alert": {
                "fn": alerts.create_alert,
                "params": ["alert_type", "severity", "title", "description", "sensor_id", "location_id"],
                "description": "Create an alert"
            },
            "acknowledge_alert": {
                "fn": alerts.acknowledge_alert,
                "params": ["alert_id"],
                "description": "Acknowledge an alert"
            },
            "resolve_alert": {
                "fn": alerts.resolve_alert,
                "params": ["alert_id", "resolution"],
                "description": "Resolve an alert"
            },
            "get_active_alerts": {
                "fn": alerts.get_active_alerts,
                "params": ["severity", "alert_type"],
                "description": "Get active alerts"
            },
            "list_alerts": {
                "fn": alerts.list_alerts,
                "params": ["status", "severity", "alert_type", "limit"],
                "description": "List alerts with filters"
            },
            "generate_hourly_report": {
                "fn": reports.generate_hourly_report,
                "params": ["location_id", "sensor_type"],
                "description": "Generate hourly report"
            },
            "generate_daily_report": {
                "fn": reports.generate_daily_report,
                "params": ["location_id", "sensor_type"],
                "description": "Generate daily report"
            },
            "generate_monthly_report": {
                "fn": reports.generate_monthly_report,
                "params": ["location_id", "sensor_type"],
                "description": "Generate monthly report"
            },
            "generate_anomaly_report": {
                "fn": reports.generate_anomaly_report,
                "params": ["start_time", "end_time", "severity"],
                "description": "Generate anomaly report"
            },
            "generate_energy_report": {
                "fn": reports.generate_energy_report,
                "params": ["location_id", "start_time", "end_time"],
                "description": "Generate energy report"
            },
            "analyze_trend": {
                "fn": trends.analyze_trend,
                "params": ["sensor_id", "start_time", "end_time"],
                "description": "Analyze sensor trend"
            },
            "calculate_moving_average": {
                "fn": trends.calculate_moving_average,
                "params": ["sensor_id", "window_size", "start_time", "end_time"],
                "description": "Calculate moving average"
            },
            "detect_seasonality": {
                "fn": trends.detect_seasonality,
                "params": ["sensor_id", "expected_period_hours"],
                "description": "Detect seasonality"
            },
            "get_trend_summary": {
                "fn": trends.get_trend_summary,
                "params": ["location_id", "sensor_type"],
                "description": "Get trend summary"
            },
            "create_notification": {
                "fn": notifications.create_notification,
                "params": ["notification_type", "recipient_name", "recipient_contact", "subject", "body", "priority"],
                "description": "Create notification"
            },
            "send_notification": {
                "fn": notifications.send_notification,
                "params": ["notification_id"],
                "description": "Send notification"
            },
            "compose_anomaly_alert_notification": {
                "fn": notifications.compose_anomaly_alert_notification,
                "params": ["recipient_name", "recipient_contact", "anomaly_id"],
                "description": "Compose anomaly notification"
            },
            "list_notifications": {
                "fn": notifications.list_notifications,
                "params": ["status", "notification_type", "priority", "limit"],
                "description": "List notifications"
            },
            "get_notification_stats": {
                "fn": notifications.get_notification_stats,
                "params": [],
                "description": "Get notification statistics"
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
        """Get current environment state.
        
        Returns:
            dict containing full current state
        """
        with self._lock:
            session = self._load_current_session()
            return session.copy()
    
    def reset(self) -> dict[str, Any]:
        """Reset environment to initial state for new session.
        
        Loads scenario data and initializes session state including:
        - All sensors loaded
        - All locations loaded
        - No anomalies
        - No alerts
        - No notifications
        - Empty reports
        
        Returns:
            dict containing session initialization summary
        """
        with self._lock:
            logger.info(f"Resetting sensor monitoring environment for scenario: {self.scenario_id}")
            
            scenario_data = self.repository.load_scenario(self.scenario_id)
            sensors_data = self.repository.load_sensors()
            locations_data = self.repository.load_locations()
            accounts_data = self.repository.load_accounts()
            
            session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uuid.uuid4().hex[:8]}"
            
            sensors_state = {}
            for sensor_id, sensor_info in sensors_data.items():
                sensors_state[sensor_id] = {
                    **sensor_info,
                    "last_value": sensor_info.get("initial_value"),
                }
            
            sensor_readings = {}
            for sensor_id in sensors_data.keys():
                sensor_readings[sensor_id] = {}
            
            account_list = list(accounts_data.values())
            workspace_account = account_list[0] if account_list else {}
            
            initial_state = {
                "session_id": session_id,
                "scenario_id": self.scenario_id,
                "scenario_name": scenario_data.get("name", self.scenario_id),
                "workspace_account": workspace_account.get("account_name", "Default Account"),
                "sensors": sensors_state,
                "sensor_readings": sensor_readings,
                "locations": locations_data,
                "anomalies": [],
                "alerts": [],
                "notifications": [],
                "actions": [],
                "metrics": {
                    "total_actions": 0,
                    "anomalies_detected": 0,
                    "anomalies_resolved": 0,
                    "alerts_triggered": 0,
                    "notifications_sent": 0,
                    "reports_generated": 0,
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
                "sensors_count": len(sensors_state),
                "locations_count": len(locations_data),
            }
    
    def execute_action(self, action_name: str, **kwargs) -> dict[str, Any]:
        """Execute a sensor monitoring action.
        
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
                    before_actions = len(session.get("actions", []))
                    result = fn(session, action_index=action_index, **kwargs)
                    after_actions = len(session.get("actions", []))
                    if isinstance(result, dict) and ("action_index" in result or after_actions > before_actions):
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
        if result.get("success", False) or result.get("anomalies_detected"):
            if action_name == "check_anomalies" and result.get("anomalies_detected", 0) > 0:
                session["metrics"]["anomalies_detected"] = session["metrics"].get("anomalies_detected", 0) + result.get("anomalies_detected", 0)
            elif action_name == "resolve_anomaly" and result.get("success"):
                session["metrics"]["anomalies_resolved"] = session["metrics"].get("anomalies_resolved", 0) + 1
            elif action_name == "create_alert" and result.get("success"):
                session["metrics"]["alerts_triggered"] = session["metrics"].get("alerts_triggered", 0) + 1
            elif action_name == "send_notification" and result.get("success"):
                session["metrics"]["notifications_sent"] = session["metrics"].get("notifications_sent", 0) + 1
            elif action_name.startswith("generate_") and result.get("success"):
                session["metrics"]["reports_generated"] = session["metrics"].get("reports_generated", 0) + 1
    
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
    
    def get_monitoring_status(self) -> dict[str, Any]:
        """Get comprehensive monitoring status.
        
        Returns:
            dict with sensors, anomalies, alerts, and notifications summary
        """
        with self._lock:
            session = self._load_current_session()
            
            sensors_state = session.get("sensors", {})
            anomalies = session.get("anomalies", [])
            alerts_list = session.get("alerts", [])
            notifications_list = session.get("notifications", [])
            
            active_anomalies = [a for a in anomalies if a.get("status") == "active"]
            active_alerts = [a for a in alerts_list if a.get("status") == "active"]
            pending_notifications = [n for n in notifications_list if n.get("status") == "pending"]
            
            sensor_types = {}
            for sensor in sensors_state.values():
                sensor_type = sensor.get("sensor_type", "unknown")
                sensor_types[sensor_type] = sensor_types.get(sensor_type, 0) + 1
            
            return {
                "session_id": session.get("session_id"),
                "sensors": {
                    "total": len(sensors_state),
                    "by_type": sensor_types,
                },
                "anomalies": {
                    "total": len(anomalies),
                    "active": len(active_anomalies),
                    "resolved": len(anomalies) - len(active_anomalies)
                },
                "alerts": {
                    "total": len(alerts_list),
                    "active": len(active_alerts),
                    "resolved": len(alerts_list) - len(active_alerts)
                },
                "notifications": {
                    "total": len(notifications_list),
                    "pending": len(pending_notifications),
                    "sent": len(notifications_list) - len(pending_notifications)
                },
                "metrics": session.get("metrics", {})
            }
    
    def evaluate_session(self) -> dict[str, Any]:
        """Evaluate current session performance.
        
        Returns:
            dict containing evaluation results
        """
        with self._lock:
            from .evaluator import ReportEvaluator
            session = self._load_current_session()
            scenario = self.repository.load_scenario(self.scenario_id)
            evaluator = ReportEvaluator(scenario=scenario)
            return evaluator.evaluate(session)
    
    def session_summary(self) -> dict[str, Any]:
        """Get summary of current session.
        
        Returns:
            dict containing session summary
        """
        with self._lock:
            session = self._load_current_session()
            sensors_state = session.get("sensors", {})
            sensor_readings = session.get("sensor_readings", {})
            anomalies = session.get("anomalies", [])
            alerts_list = session.get("alerts", [])
            active_anomalies = [a for a in anomalies if a.get("status") == "active"]
            active_alerts = [a for a in alerts_list if a.get("status") == "active"]
            return {
                "session_id": session.get("session_id"),
                "scenario_id": session.get("scenario_id"),
                "total_sensors": len(sensors_state),
                "total_readings": sum(len(r) for r in sensor_readings.values()),
                "active_anomalies": len(active_anomalies),
                "active_alerts": len(active_alerts),
                "total_actions": session.get("metrics", {}).get("total_actions", 0),
                "reports_generated": session.get("metrics", {}).get("reports_generated", 0),
            }
