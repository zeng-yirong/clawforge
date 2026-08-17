from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

DEFAULT_STATE = {
    "zones": {},
    "sensors": {},
    "rules": [],
    "event_log": [],
    "action_log": [],
    "security_status": "normal",
    "zone_counter": 1,
    "sensor_counter": 1,
    "rule_counter": 1,
    "event_counter": 1,
}

VALID_ZONE_TYPES = ("entrance", "office", "corridor", "storage", "outdoor", "parking")
VALID_SENSOR_TYPES = ("motion", "door", "window", "camera", "glass_break", "smoke")
VALID_TRIGGER_TYPES = ("intrusion_detected", "unauthorized_entry", "motion_alert", 
                       "door_forced", "window_break", "after_hours_activity")
VALID_CONDITION_OPS = ("eq", "neq", "gt", "lt", "gte", "lte", "contains", "matches")
VALID_ACTION_TYPES = ("lock_door", "call_police", "capture_video", "send_sms", 
                      "sound_alarm", "notify_security", "activate_lights")


class SecurityPatrolEventDrivenEnv:
    """
    A class representing a home/office security patrol automation environment.
    
    This class allows an agent to configure security zones, deploy sensors,
    and create automation rules that respond to intrusion events. When anomalies
    are detected, the system can automatically lock doors, call emergency services,
    capture video evidence, and notify responsible personnel.
    
    Attributes:
        zones (Dict): Configured security zones with their properties.
        sensors (Dict): Deployed sensors monitoring different areas.
        rules (List[Dict]): Configured security automation rules.
        event_log (List[Dict]): History of all security events.
        action_log (List[Dict]): History of all executed security actions.
        security_status (str): Overall security status (normal/alert/lockdown).
        zone_counter (int): Auto-incrementing zone ID counter.
        sensor_counter (int): Auto-incrementing sensor ID counter.
        rule_counter (int): Auto-incrementing rule ID counter.
        event_counter (int): Auto-incrementing event ID counter.
    """
    
    def __init__(self):
        self.zones: Dict[str, Dict[str, Any]]
        self.sensors: Dict[str, Dict[str, Any]]
        self.rules: List[Dict[str, Any]]
        self.event_log: List[Dict[str, Any]]
        self.action_log: List[Dict[str, Any]]
        self.security_status: str
        self.zone_counter: int
        self.sensor_counter: int
        self.rule_counter: int
        self.event_counter: int
        self._api_description = (
            "This tool manages security patrol automation for homes and offices. "
            "It monitors intrusion events through sensors, evaluates security rules, "
            "and executes protective actions like locking doors, calling police, "
            "capturing video evidence, and notifying personnel."
        )
    
    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.zones = scenario.get("zones", DEFAULT_STATE_COPY["zones"])
        self.sensors = scenario.get("sensors", DEFAULT_STATE_COPY["sensors"])
        self.rules = scenario.get("rules", DEFAULT_STATE_COPY["rules"])
        self.event_log = scenario.get("event_log", DEFAULT_STATE_COPY["event_log"])
        self.action_log = scenario.get("action_log", DEFAULT_STATE_COPY["action_log"])
        self.security_status = scenario.get("security_status", DEFAULT_STATE_COPY["security_status"])
        self.zone_counter = scenario.get("zone_counter", DEFAULT_STATE_COPY["zone_counter"])
        self.sensor_counter = scenario.get("sensor_counter", DEFAULT_STATE_COPY["sensor_counter"])
        self.rule_counter = scenario.get("rule_counter", DEFAULT_STATE_COPY["rule_counter"])
        self.event_counter = scenario.get("event_counter", DEFAULT_STATE_COPY["event_counter"])
    
    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.
        
        Returns:
            dict: All environment state variables including zones, sensors, rules,
                event_log, action_log, security_status, and counters.
        """
        return {
            "zones": self.zones,
            "sensors": self.sensors,
            "rules": self.rules,
            "event_log": self.event_log,
            "action_log": self.action_log,
            "security_status": self.security_status,
            "zone_counter": self.zone_counter,
            "sensor_counter": self.sensor_counter,
            "rule_counter": self.rule_counter,
            "event_counter": self.event_counter,
        }
    
    # ── Zone management ────────────────────────────────────────────────
    
    def create_zone(
        self,
        name: str,
        zone_type: str,
        access_level: str = "public",
        has_door_lock: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new security zone to monitor.
        
        Args:
            name (str): Unique name for the zone (e.g., 'main_entrance', 'office_floor2').
            zone_type (str): Type of zone — must be one of: entrance, office, corridor, 
                storage, outdoor, parking.
            access_level (str): Access restriction level — public, restricted, private. 
                Defaults to 'public'.
            has_door_lock (bool): Whether this zone has an electronic door lock that can 
                be controlled remotely. Defaults to False.
        
        Returns:
            dict: Contains zone_id (str) and zone (Dict) with all zone properties,
                or error (str) if creation failed.
        """
        if zone_type not in VALID_ZONE_TYPES:
            return {"error": f"Invalid zone_type '{zone_type}'. Must be one of: {', '.join(VALID_ZONE_TYPES)}"}
        if name in self.zones:
            return {"error": f"Zone '{name}' already exists."}
        if access_level not in ("public", "restricted", "private"):
            return {"error": f"Invalid access_level '{access_level}'. Must be: public, restricted, or private."}
        
        zone_id = f"zone_{self.zone_counter}"
        self.zone_counter += 1
        
        self.zones[name] = {
            "zone_id": zone_id,
            "zone_type": zone_type,
            "access_level": access_level,
            "has_door_lock": has_door_lock,
            "lock_status": "unlocked" if has_door_lock else None,
            "sensor_count": 0,
            "alert_count": 0,
        }
        return {"zone_id": zone_id, "zone": {"name": name, **self.zones[name]}}
    
    def list_zones(self, zone_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all configured security zones.
        
        Args:
            zone_type (str): [Optional] Filter by zone type.
        
        Returns:
            dict: Contains zones (List[Dict]) with all matching zones.
        """
        zones = [{"name": k, **v} for k, v in self.zones.items()]
        if zone_type:
            zones = [z for z in zones if z["zone_type"] == zone_type]
        return {"zones": zones}
    
    def update_zone(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update properties of an existing zone.
        
        Args:
            name (str): Name of the zone to update.
            updates (Dict): Fields to change. Allowed keys: access_level, has_door_lock.
        
        Returns:
            dict: Contains zone (Dict) with updated properties, or error (str) if failed.
        """
        if name not in self.zones:
            return {"error": f"Zone '{name}' not found."}
        
        allowed_fields = {"access_level", "has_door_lock"}
        invalid = set(updates.keys()) - allowed_fields
        if invalid:
            return {"error": f"Invalid update fields: {', '.join(invalid)}"}
        
        zone = self.zones[name]
        for key, value in updates.items():
            if key == "access_level" and value not in ("public", "restricted", "private"):
                return {"error": f"Invalid access_level '{value}'."}
            if key == "has_door_lock":
                if value and zone["lock_status"] is None:
                    zone["lock_status"] = "unlocked"
                elif not value:
                    zone["lock_status"] = None
            zone[key] = value
        
        return {"success": True, "zone": {"name": name, **zone}}
    
    # ── Sensor management ──────────────────────────────────────────────
    
    def deploy_sensor(
        self,
        zone_name: str,
        sensor_type: str,
        location: str,
    ) -> Dict[str, Any]:
        """
        Deploy a security sensor in a specific zone.
        
        Args:
            zone_name (str): Name of the zone where sensor will be deployed.
            sensor_type (str): Type of sensor — motion, door, window, camera, 
                glass_break, smoke.
            location (str): Specific location description within the zone.
        
        Returns:
            dict: Contains sensor_id (str) and sensor (Dict) with all sensor properties,
                or error (str) if deployment failed.
        """
        if zone_name not in self.zones:
            return {"error": f"Zone '{zone_name}' not found."}
        if sensor_type not in VALID_SENSOR_TYPES:
            return {"error": f"Invalid sensor_type '{sensor_type}'. Must be one of: {', '.join(VALID_SENSOR_TYPES)}"}
        
        sensor_id = f"sensor_{self.sensor_counter}"
        self.sensor_counter += 1
        
        self.sensors[sensor_id] = {
            "sensor_id": sensor_id,
            "zone_name": zone_name,
            "sensor_type": sensor_type,
            "location": location,
            "status": "active",
            "trigger_count": 0,
        }
        self.zones[zone_name]["sensor_count"] += 1
        
        return {"sensor_id": sensor_id, "sensor": self.sensors[sensor_id]}
    
    def list_sensors(
        self,
        zone_name: Optional[str] = None,
        sensor_type: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List deployed sensors with optional filtering.
        
        Args:
            zone_name (str): [Optional] Filter by zone name.
            sensor_type (str): [Optional] Filter by sensor type.
        
        Returns:
            dict: Contains sensors (List[Dict]) with all matching sensors.
        """
        sensors = list(self.sensors.values())
        if zone_name:
            sensors = [s for s in sensors if s["zone_name"] == zone_name]
        if sensor_type:
            sensors = [s for s in sensors if s["sensor_type"] == sensor_type]
        return {"sensors": sensors}
    
    def update_sensor_status(self, sensor_id: str, status: str) -> Dict[str, Any]:
        """
        Update the operational status of a sensor.
        
        Args:
            sensor_id (str): ID of the sensor to update.
            status (str): New status — active, inactive, maintenance.
        
        Returns:
            dict: Contains sensor (Dict) with updated status, or error (str) if failed.
        """
        if sensor_id not in self.sensors:
            return {"error": f"Sensor '{sensor_id}' not found."}
        if status not in ("active", "inactive", "maintenance"):
            return {"error": f"Invalid status '{status}'. Must be: active, inactive, or maintenance."}
        
        self.sensors[sensor_id]["status"] = status
        return {"success": True, "sensor": self.sensors[sensor_id]}
    
    # ── Rule management ────────────────────────────────────────────────
    
    def create_rule(
        self,
        name: str,
        trigger_type: str,
        condition_field: str,
        condition_op: str,
        condition_value: str,
        actions: List[Dict[str, Any]],
        zone_filter: Optional[str] = None,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """
        Create a security automation rule.
        
        Args:
            name (str): Human-readable rule name.
            trigger_type (str): Event type that triggers evaluation — intrusion_detected,
                unauthorized_entry, motion_alert, door_forced, window_break, after_hours_activity.
            condition_field (str): Field in the event payload to evaluate.
            condition_op (str): Comparison operator — eq, neq, gt, lt, gte, lte, 
                contains, matches.
            condition_value (str): Value to compare against.
            actions (List[Dict]): Ordered list of actions to execute when condition is met.
                Each action has 'type' (lock_door, call_police, capture_video, send_sms,
                sound_alarm, notify_security, activate_lights) and 'params'.
            zone_filter (str): [Optional] Only trigger for events in this specific zone.
            priority (str): Rule priority level — low, normal, high, critical. 
                Defaults to 'normal'.
        
        Returns:
            dict: Contains rule_id (int) and rule (Dict) with all rule properties,
                or error (str) if creation failed.
        """
        if trigger_type not in VALID_TRIGGER_TYPES:
            return {"error": f"Invalid trigger_type '{trigger_type}'. Must be one of: {', '.join(VALID_TRIGGER_TYPES)}"}
        if condition_op not in VALID_CONDITION_OPS:
            return {"error": f"Invalid condition_op '{condition_op}'. Must be one of: {', '.join(VALID_CONDITION_OPS)}"}
        if not actions:
            return {"error": "At least one action is required."}
        if zone_filter and zone_filter not in self.zones:
            return {"error": f"Zone filter '{zone_filter}' is not a registered zone."}
        if priority not in ("low", "normal", "high", "critical"):
            return {"error": f"Invalid priority '{priority}'. Must be: low, normal, high, or critical."}
        
        for action in actions:
            if action.get("type") not in VALID_ACTION_TYPES:
                return {"error": f"Invalid action type '{action.get('type')}'. Must be one of: {', '.join(VALID_ACTION_TYPES)}"}
        
        rule_id = self.rule_counter
        self.rule_counter += 1
        
        rule = {
            "rule_id": rule_id,
            "name": name,
            "enabled": True,
            "trigger_type": trigger_type,
            "condition": {
                "field": condition_field,
                "op": condition_op,
                "value": condition_value,
            },
            "actions": actions,
            "zone_filter": zone_filter,
            "priority": priority,
            "match_count": 0,
        }
        self.rules.append(rule)
        return {"rule_id": rule_id, "rule": rule}
    
    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update fields of an existing security rule.
        
        Args:
            rule_id (int): ID of the rule to update.
            updates (Dict): Fields to change. Allowed keys: name, enabled, trigger_type,
                condition, actions, zone_filter, priority.
        
        Returns:
            dict: Contains rule (Dict) with updated properties, or error (str) if failed.
        """
        rule = self._find_rule(rule_id)
        if not rule:
            return {"error": f"Rule ID {rule_id} not found."}
        
        allowed_fields = {"name", "enabled", "trigger_type", "condition", "actions", 
                         "zone_filter", "priority"}
        invalid = set(updates.keys()) - allowed_fields
        if invalid:
            return {"error": f"Invalid update fields: {', '.join(invalid)}"}
        
        for key, value in updates.items():
            if key == "trigger_type" and value not in VALID_TRIGGER_TYPES:
                return {"error": f"Invalid trigger_type '{value}'."}
            if key == "priority" and value not in ("low", "normal", "high", "critical"):
                return {"error": f"Invalid priority '{value}'."}
            if key == "zone_filter" and value and value not in self.zones:
                return {"error": f"Zone filter '{value}' is not a registered zone."}
            rule[key] = value
        
        return {"success": True, "rule": rule}
    
    def delete_rule(self, rule_id: int) -> Dict[str, str]:
        """
        Delete a security automation rule.
        
        Args:
            rule_id (int): ID of the rule to delete.
        
        Returns:
            dict: Contains status (str) with deletion confirmation, or error (str) if failed.
        """
        rule = self._find_rule(rule_id)
        if not rule:
            return {"error": f"Rule ID {rule_id} not found."}
        self.rules.remove(rule)
        return {"status": f"Rule {rule_id} deleted successfully."}
    
    def list_rules(
        self,
        enabled_only: bool = False,
        priority: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all configured security rules with optional filtering.
        
        Args:
            enabled_only (bool): If True, return only enabled rules. Defaults to False.
            priority (str): [Optional] Filter by priority level.
        
        Returns:
            dict: Contains rules (List[Dict]) with all matching rules.
        """
        rules = self.rules
        if enabled_only:
            rules = [r for r in rules if r["enabled"]]
        if priority:
            rules = [r for r in rules if r["priority"] == priority]
        return {"rules": rules}
    
    # ── Event simulation & processing ──────────────────────────────────
    
    def inject_event(
        self,
        zone_name: str = None,
        event_type: str = None,
        payload: Dict[str, Any] = None,
        sensor_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Inject a simulated security event. The environment evaluates all matching rules
        and executes actions for those whose conditions are met.
        
        Args:
            zone_name (str): Name of the zone where the event occurred.
            event_type (str): Type of the security event (must match a valid trigger_type).
            payload (Dict): Arbitrary key-value data describing the event (e.g., severity,
                threat_level, person_count, time_of_day).
            sensor_id (str): [Optional] ID of the sensor that detected the event.
        
        Returns:
            dict: Contains event_id (int), matched_rules (int) count, and 
                executed_actions (List[Dict]) with results of each action,
                or error (str) if injection failed.
        """
        if not isinstance(zone_name, str):
            return {"error": "zone_name must be a string."}
        if not isinstance(event_type, str):
            return {"error": "event_type must be a string."}
        if not isinstance(payload, dict):
            return {"error": "payload must be a dictionary."}
        if sensor_id is not None and not isinstance(sensor_id, str):
            return {"error": "sensor_id must be a string if provided."}
        if zone_name not in self.zones:
            return {"error": f"Zone '{zone_name}' not found."}
        if event_type not in VALID_TRIGGER_TYPES:
            return {"error": f"Invalid event_type '{event_type}'."}
        if sensor_id and sensor_id not in self.sensors:
            return {"error": f"Sensor '{sensor_id}' not found."}
        
        event_id = self.event_counter
        self.event_counter += 1
        
        event = {
            "event_id": event_id,
            "zone_name": zone_name,
            "event_type": event_type,
            "payload": payload,
            "sensor_id": sensor_id,
            "timestamp": f"event_t+{event_id}",
        }
        self.event_log.append(event)
        self.zones[zone_name]["alert_count"] += 1
        
        if sensor_id:
            self.sensors[sensor_id]["trigger_count"] += 1
        
        # Update security status based on event severity
        severity = payload.get("severity", "low")
        if severity in ("high", "critical") and self.security_status == "normal":
            self.security_status = "alert"
        
        executed = []
        matched_count = 0
        
        for rule in self.rules:
            if not rule["enabled"]:
                continue
            if rule["trigger_type"] != event_type:
                continue
            if rule["zone_filter"] and rule["zone_filter"] != zone_name:
                continue
            if not self._evaluate_condition(rule["condition"], payload):
                continue
            
            matched_count += 1
            rule["match_count"] += 1
            
            for action in rule["actions"]:
                result = self._execute_action(action, event)
                executed.append(result)
        
        return {
            "event_id": event_id,
            "matched_rules": matched_count,
            "executed_actions": executed,
        }
    
    def get_event_log(
        self,
        zone_name: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Retrieve filtered security event history.
        
        Args:
            zone_name (str): [Optional] Filter by zone name.
            event_type (str): [Optional] Filter by event type.
            limit (int): Maximum events to return. Defaults to 20.
        
        Returns:
            dict: Contains events (List[Dict]) with matching events (newest first)
                and total (int) matching count.
        """
        events = self.event_log
        if zone_name:
            events = [e for e in events if e["zone_name"] == zone_name]
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        events = list(reversed(events))[:limit]
        return {"events": events, "total": len(events)}
    
    def get_action_log(
        self,
        action_type: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Retrieve history of executed security actions.
        
        Args:
            action_type (str): [Optional] Filter by action type.
            limit (int): Maximum actions to return. Defaults to 50.
        
        Returns:
            dict: Contains actions (List[Dict]) with executed actions (newest first)
                and total (int) action count.
        """
        log = self.action_log
        if action_type:
            log = [a for a in log if a["action_type"] == action_type]
        log = list(reversed(log))[:limit]
        return {"actions": log, "total": len(log)}
    
    # ── Security operations ────────────────────────────────────────────
    
    def set_security_status(self, status: str) -> Dict[str, Any]:
        """
        Manually set the overall security status.
        
        Args:
            status (str): New security status — normal, alert, lockdown.
        
        Returns:
            dict: Contains status (str) confirmation and previous_status (str),
                or error (str) if failed.
        """
        if status not in ("normal", "alert", "lockdown"):
            return {"error": f"Invalid status '{status}'. Must be: normal, alert, or lockdown."}
        
        previous = self.security_status
        self.security_status = status
        
        # If entering lockdown, lock all doors
        if status == "lockdown":
            for zone_name, zone in self.zones.items():
                if zone["has_door_lock"] and zone["lock_status"] == "unlocked":
                    zone["lock_status"] = "locked"
        
        return {
            "status": f"Security status changed to '{status}'.",
            "previous_status": previous,
        }
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get the current overall security status and zone summary.
        
        Returns:
            dict: Contains security_status (str), total_zones (int), total_sensors (int),
                active_rules (int), and recent_alerts (int) from last 10 events.
        """
        recent_alerts = len([e for e in self.event_log[-10:]
                           if (e.get("payload") or {}).get("severity") in ("high", "critical")])
        
        return {
            "security_status": self.security_status,
            "total_zones": len(self.zones),
            "total_sensors": len(self.sensors),
            "active_rules": len([r for r in self.rules if r["enabled"]]),
            "recent_alerts": recent_alerts,
        }
    
    def lock_zone_door(self, zone_name: str) -> Dict[str, Any]:
        """
        Manually lock the door of a specific zone.
        
        Args:
            zone_name (str): Name of the zone to lock.
        
        Returns:
            dict: Contains status (str) confirmation, or error (str) if failed.
        """
        if zone_name not in self.zones:
            return {"error": f"Zone '{zone_name}' not found."}
        
        zone = self.zones[zone_name]
        if not zone["has_door_lock"]:
            return {"error": f"Zone '{zone_name}' does not have a controllable door lock."}
        if zone["lock_status"] == "locked":
            return {"error": f"Zone '{zone_name}' door is already locked."}
        
        zone["lock_status"] = "locked"
        return {"status": f"Zone '{zone_name}' door locked successfully."}
    
    def unlock_zone_door(self, zone_name: str) -> Dict[str, Any]:
        """
        Manually unlock the door of a specific zone.
        
        Args:
            zone_name (str): Name of the zone to unlock.
        
        Returns:
            dict: Contains status (str) confirmation, or error (str) if failed.
        """
        if zone_name not in self.zones:
            return {"error": f"Zone '{zone_name}' not found."}
        
        zone = self.zones[zone_name]
        if not zone["has_door_lock"]:
            return {"error": f"Zone '{zone_name}' does not have a controllable door lock."}
        if zone["lock_status"] == "unlocked":
            return {"error": f"Zone '{zone_name}' door is already unlocked."}
        
        zone["lock_status"] = "unlocked"
        return {"status": f"Zone '{zone_name}' door unlocked successfully."}
    
    # ── Internal helpers ───────────────────────────────────────────────
    
    def _find_rule(self, rule_id: int) -> Optional[Dict[str, Any]]:
        for rule in self.rules:
            if rule["rule_id"] == rule_id:
                return rule
        return None
    
    def _evaluate_condition(
        self, condition: Dict[str, str], payload: Dict[str, Any]
    ) -> bool:
        field = condition["field"]
        op = condition["op"]
        expected = condition["value"]
        
        actual = payload.get(field)
        if actual is None:
            return False
        
        actual_str = str(actual)
        expected_str = str(expected)
        
        if op == "eq":
            return actual_str == expected_str
        if op == "neq":
            return actual_str != expected_str
        if op == "contains":
            return expected_str.lower() in actual_str.lower()
        if op == "matches":
            return bool(re.search(expected_str, actual_str))
        
        try:
            actual_num = float(actual)
            expected_num = float(expected)
        except (ValueError, TypeError):
            return False
        
        if op == "gt":
            return actual_num > expected_num
        if op == "lt":
            return actual_num < expected_num
        if op == "gte":
            return actual_num >= expected_num
        if op == "lte":
            return actual_num <= expected_num
        return False
    
    def _execute_action(
        self, action: Dict[str, Any], event: Dict[str, Any]
    ) -> Dict[str, Any]:
        action_type = action.get("type", "unknown")
        params = action.get("params", {})
        zone_name = event["zone_name"]
        
        output = f"Simulated execution of '{action_type}'"
        
        # Simulate specific action behaviors
        if action_type == "lock_door":
            zone = self.zones.get(zone_name)
            if zone and zone["has_door_lock"]:
                zone["lock_status"] = "locked"
                output = f"Locked door in zone '{zone_name}'"
            else:
                output = f"Cannot lock door in zone '{zone_name}' (no lock available)"
        
        elif action_type == "call_police":
            phone = params.get("phone", "911")
            output = f"Emergency call placed to {phone} for zone '{zone_name}'"
        
        elif action_type == "capture_video":
            duration = params.get("duration", 30)
            backup_location = params.get("backup_location", "cloud_storage")
            output = f"Captured {duration}s video from zone '{zone_name}', backed up to {backup_location}"
        
        elif action_type == "send_sms":
            recipient = params.get("recipient", "security_manager")
            message = params.get("message", f"Security alert in {zone_name}")
            output = f"SMS sent to {recipient}: {message}"
        
        elif action_type == "sound_alarm":
            alarm_type = params.get("alarm_type", "intrusion")
            output = f"Sounded {alarm_type} alarm in zone '{zone_name}'"
        
        elif action_type == "notify_security":
            channel = params.get("channel", "security_app")
            output = f"Notified security team via {channel} about event in '{zone_name}'"
        
        elif action_type == "activate_lights":
            output = f"Activated emergency lights in zone '{zone_name}'"
        
        else:
            output = f"Simulated execution of '{action_type}' with params {params}"
        
        result = {
            "action_type": action_type,
            "params": params,
            "event_id": event["event_id"],
            "zone_name": zone_name,
            "status": "executed",
            "output": output,
        }
        self.action_log.append(result)
        return result

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })