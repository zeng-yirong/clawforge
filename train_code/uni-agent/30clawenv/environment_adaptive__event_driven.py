from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import re

DEFAULT_STATE = {
    "rules": [],
    "event_log": [],
    "action_log": [],
    "monitored_sources": {},
    "rule_counter": 1,
    "event_counter": 1,
    "current_state": {
        "room_temperature": 25.0,
        "humidity": 50.0,
        "air_conditioner": {
            "power": True,
            "mode": "cool",
            "target_temp": 24.0
        },
        "humidifier": {
            "power": False,
            "target_humidity": 55.0
        },
        "smart_outlets": {
            "outlet_1": True,
            "outlet_2": False,
            "outlet_3": True
        },
        "energy_consumption": {
            "current_rate": "off_peak",
            "total_today": 5.2,
            "current_cost": 0.0
        },
        "user_health": {
            "heart_rate": 72,
            "activity_level": "sedentary",
            "comfort_preference": "normal"
        }
    }
}

VALID_TRIGGER_TYPES = (
    "weather_change", 
    "electricity_rate_change", 
    "health_status_change",
    "scheduled_adjustment",
    "user_override"
)

VALID_CONDITION_OPS = ("eq", "neq", "gt", "lt", "gte", "lte", "contains", "matches")


class MultiDimensionalEnvAdaptiveControl:
    """
    A class representing a multi-dimensional adaptive control environment.
    
    This environment combines weather API data, time-of-use electricity pricing, 
    and user health metrics to dynamically adjust HVAC systems, humidifiers, 
    and smart outlets for optimal comfort, health, and energy efficiency.
    
    Attributes:
        rules (List[Dict]): Configured automation rules.
        event_log (List[Dict]): History of all triggered events.
        action_log (List[Dict]): History of all executed actions.
        monitored_sources (Dict): Registered event sources with their status.
        rule_counter (int): Auto-incrementing rule ID counter.
        event_counter (int): Auto-incrementing event ID counter.
        current_state (Dict): Current state of the controlled environment.
    """
    
    def __init__(self):
        self.rules: List[Dict[str, Any]]
        self.event_log: List[Dict[str, Any]]
        self.action_log: List[Dict[str, Any]]
        self.monitored_sources: Dict[str, Dict[str, Any]]
        self.rule_counter: int
        self.event_counter: int
        self.current_state: Dict[str, Any]
        self._api_description = (
            "This tool enables multi-dimensional adaptive environmental control "
            "by integrating weather data, electricity pricing, and health metrics "
            "to optimize HVAC, humidifier, and smart outlet settings automatically."
        )
        self._load_scenario({})

    # ── Core lifecycle methods ─────────────────────────────────────────

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load initial state from scenario configuration.
        
        Args:
            scenario (dict): Scenario configuration data.
            long_context (bool): Whether to use long context loading. Unused in this class.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.rules = scenario.get("rules", DEFAULT_STATE_COPY["rules"])
        self.event_log = scenario.get("event_log", DEFAULT_STATE_COPY["event_log"])
        self.action_log = scenario.get("action_log", DEFAULT_STATE_COPY["action_log"])
        self.monitored_sources = scenario.get("monitored_sources", DEFAULT_STATE_COPY["monitored_sources"])
        self.rule_counter = scenario.get("rule_counter", DEFAULT_STATE_COPY["rule_counter"])
        self.event_counter = scenario.get("event_counter", DEFAULT_STATE_COPY["event_counter"])
        self.current_state = scenario.get("current_state", DEFAULT_STATE_COPY["current_state"])
    
    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.
        
        Returns:
            dict: All environment state variables including rules, event_log,
                action_log, monitored_sources, counters, and current_state.
        """
        return {
            "rules": self.rules,
            "event_log": self.event_log,
            "action_log": self.action_log,
            "monitored_sources": self.monitored_sources,
            "rule_counter": self.rule_counter,
            "event_counter": self.event_counter,
            "current_state": self.current_state
        }
    
    # ── Source management ──────────────────────────────────────────────
    
    def register_source(
        self, 
        name: str, 
        source_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new event source to monitor.
        
        Args:
            name (str): Unique name for the source (e.g., 'weather_api_nyc').
            source_type (str): Type of source — must be one of VALID_TRIGGER_TYPES.
            config (Dict): Optional configuration for the source.
            
        Returns:
            success (bool): Whether registration succeeded.
            source (Dict): The registered source metadata.
        """
        if source_type not in VALID_TRIGGER_TYPES:
            return {"error": f"Invalid source_type '{source_type}'. Must be one of: {', '.join(VALID_TRIGGER_TYPES)}"}
        
        if name in self.monitored_sources:
            return {"error": f"Source '{name}' is already registered."}
        
        self.monitored_sources[name] = {
            "type": source_type,
            "active": True,
            "event_count": 0,
            "config": config or {},
            "last_update": None
        }
        
        return {
            "success": True, 
            "source": {"name": name, **self.monitored_sources[name]}
        }
    
    def list_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all registered event sources and their status.
        
        Returns:
            sources (List[Dict]): Registered sources with type, active status, and event count.
        """
        return {
            "sources": [
                {"name": k, **v} for k, v in self.monitored_sources.items()
            ]
        }
    
    # ── Rule management ────────────────────────────────────────────────
    
    def create_rule(
        self,
        name: str,
        trigger_type: str,
        condition_field: str,
        condition_op: str,
        condition_value: str,
        actions: List[Dict[str, Any]],
        source_filter: Optional[str] = None,
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Create an automation rule for adaptive environmental control.
        
        Args:
            name (str): Human-readable rule name.
            trigger_type (str): Event type that triggers evaluation.
            condition_field (str): Field in the event payload to evaluate.
            condition_op (str): Comparison operator — eq, neq, gt, lt, gte, lte, contains, matches.
            condition_value (str): Value to compare against.
            actions (List[Dict]): Ordered list of adjustment actions to execute.
                Each action has 'type' and 'params'.
            source_filter (str): [Optional] Only trigger from this specific source name.
            priority (int): Rule priority (1=highest, 5=lowest). Defaults to 1.
            
        Returns:
            rule_id (int): Unique rule identifier.
            rule (Dict): The created rule with all fields.
        """
        if trigger_type not in VALID_TRIGGER_TYPES:
            return {"error": f"Invalid trigger_type '{trigger_type}'. Must be one of: {', '.join(VALID_TRIGGER_TYPES)}"}
        
        if condition_op not in VALID_CONDITION_OPS:
            return {"error": f"Invalid condition_op '{condition_op}'. Must be one of: {', '.join(VALID_CONDITION_OPS)}"}
        
        if not actions:
            return {"error": "At least one action is required."}
        
        if source_filter and source_filter not in self.monitored_sources:
            return {"error": f"Source filter '{source_filter}' is not a registered source."}
        
        if priority < 1 or priority > 5:
            return {"error": "Priority must be between 1 and 5."}
        
        # Validate action types
        valid_action_types = {
            "adjust_ac_temperature", "set_ac_mode", "toggle_ac_power",
            "set_humidifier", "toggle_humidifier_power",
            "toggle_outlet", "set_all_outlets",
            "update_user_preference", "calculate_energy_optimization"
        }
        
        for action in actions:
            action_type = action.get("type")
            if action_type not in valid_action_types:
                return {"error": f"Invalid action type '{action_type}'. Must be one of: {', '.join(valid_action_types)}"}
        
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
            "source_filter": source_filter,
            "priority": priority,
            "match_count": 0,
            "last_matched": None
        }
        self.rules.append(rule)
        
        return {"rule_id": rule_id, "rule": rule}
    
    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update fields of an existing rule.
        
        Args:
            rule_id (int): ID of the rule to update.
            updates (Dict): Fields to change. Allowed keys:
                name, enabled, trigger_type, condition, actions, source_filter, priority.
                
        Returns:
            rule (Dict): The updated rule.
        """
        rule = self._find_rule(rule_id)
        if not rule:
            return {"error": f"Rule ID {rule_id} not found."}
        
        allowed_fields = {"name", "enabled", "trigger_type", "condition", "actions", "source_filter", "priority"}
        invalid = set(updates.keys()) - allowed_fields
        if invalid:
            return {"error": f"Invalid update fields: {', '.join(invalid)}"}
        
        for key, value in updates.items():
            if key == "trigger_type" and value not in VALID_TRIGGER_TYPES:
                return {"error": f"Invalid trigger_type '{value}'."}
            if key == "priority" and (value < 1 or value > 5):
                return {"error": "Priority must be between 1 and 5."}
            rule[key] = value
        
        return {"success": True, "rule": rule}
    
    def delete_rule(self, rule_id: int) -> Dict[str, str]:
        """
        Delete an automation rule.
        
        Args:
            rule_id (int): ID of the rule to delete.
            
        Returns:
            status (str): Deletion confirmation.
        """
        rule = self._find_rule(rule_id)
        if not rule:
            return {"error": f"Rule ID {rule_id} not found."}
        
        self.rules.remove(rule)
        return {"status": f"Rule {rule_id} deleted successfully."}
    
    def list_rules(self, enabled_only: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all configured rules.
        
        Args:
            enabled_only (bool): If True, return only enabled rules. Defaults to False.
            
        Returns:
            rules (List[Dict]): Matching rules, sorted by priority then match count.
        """
        rules = self.rules
        if enabled_only:
            rules = [r for r in rules if r["enabled"]]
        
        rules.sort(key=lambda x: (x["priority"], -x["match_count"]))
        return {"rules": rules}
    
    # ── Event simulation & processing ──────────────────────────────────
    
    def inject_event(
        self,
        source: str,
        event_type: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Inject a simulated event from a monitored source. The environment evaluates
        all matching rules and executes adaptive control actions.
        
        Args:
            source (str): Name of the registered source emitting the event.
            event_type (str): Type of the event (must match a valid trigger_type).
            payload (Dict): Arbitrary key-value data describing the event.
            
        Returns:
            event_id (int): Unique event identifier.
            matched_rules (int): Number of rules whose conditions matched.
            executed_actions (List[Dict]): Results of each executed action.
            new_state (Dict): Current environment state after action execution.
        """
        if source not in self.monitored_sources:
            return {"error": f"Source '{source}' is not registered."}
        
        if event_type not in VALID_TRIGGER_TYPES:
            return {"error": f"Invalid event_type '{event_type}'."}
        
        event_id = self.event_counter
        self.event_counter += 1
        
        event = {
            "event_id": event_id,
            "source": source,
            "event_type": event_type,
            "payload": payload,
            "timestamp": f"adapt_control_t+{event_id}",
        }
        self.event_log.append(event)
        self.monitored_sources[source]["event_count"] += 1
        self.monitored_sources[source]["last_update"] = event["timestamp"]
        
        # Update current state based on event data
        self._update_current_state_from_event(event)
        
        # Find matching rules, sorted by priority
        matched_rules = []
        for rule in self.rules:
            if not rule["enabled"]:
                continue
            if rule["trigger_type"] != event_type:
                continue
            if rule["source_filter"] and rule["source_filter"] != source:
                continue
            if not self._evaluate_condition(rule["condition"], payload):
                continue
            
            matched_rules.append(rule)
        
        matched_rules.sort(key=lambda x: x["priority"])
        
        executed = []
        for rule in matched_rules:
            rule["match_count"] += 1
            rule["last_matched"] = event["timestamp"]
            
            for action in rule["actions"]:
                result = self._execute_adaptive_action(action, event)
                executed.append(result)
        
        return {
            "event_id": event_id,
            "matched_rules": len(matched_rules),
            "executed_actions": executed,
            "new_state": self.current_state
        }
    
    def get_event_log(
        self,
        source: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Retrieve filtered event history.
        
        Args:
            source (str): [Optional] Filter by source name.
            event_type (str): [Optional] Filter by event type.
            limit (int): Maximum events to return. Defaults to 20.
            
        Returns:
            events (List[Dict]): Matching events, newest first.
            total (int): Total matching count.
        """
        events = self.event_log
        if source:
            events = [e for e in events if e["source"] == source]
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        events = list(reversed(events))[:limit]
        return {"events": events, "total": len(events)}
    
    def get_action_log(self, limit: int = 50) -> Dict[str, Any]:
        """
        Retrieve history of executed adaptive control actions.
        
        Args:
            limit (int): Maximum actions to return. Defaults to 50.
            
        Returns:
            actions (List[Dict]): Executed actions, newest first.
            total (int): Total action count.
        """
        log = list(reversed(self.action_log))[:limit]
        return {"actions": log, "total": len(log)}
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current environmental metrics and energy statistics.
        
        Returns:
            metrics (Dict): Current environmental state, comfort metrics, and energy data.
        """
        # Calculate comfort score
        temp = self.current_state["room_temperature"]
        humidity = self.current_state["humidity"]
        target_temp = self.current_state["air_conditioner"]["target_temp"]
        
        temp_diff = abs(temp - target_temp)
        humidity_score = 100 - abs(humidity - 50) * 2  # Optimal humidity around 50%
        comfort_score = max(0, 100 - temp_diff * 10 - (100 - humidity_score) * 0.3)
        
        # Energy efficiency score based on current rate
        rate = self.current_state["energy_consumption"]["current_rate"]
        efficiency_factors = {
            "off_peak": 95,
            "mid_peak": 80,
            "peak": 60,
            "critical_peak": 40
        }
        energy_score = efficiency_factors.get(rate, 50)
        
        return {
            "environmental_metrics": {
                "temperature": temp,
                "humidity": humidity,
                "ac_target_temp": target_temp,
                "ac_powered": self.current_state["air_conditioner"]["power"],
                "humidifier_powered": self.current_state["humidifier"]["power"]
            },
            "comfort_score": round(comfort_score, 1),
            "energy_efficiency_score": energy_score,
            "health_status": self.current_state["user_health"],
            "energy_data": self.current_state["energy_consumption"]
        }
    
    # ── Internal helpers ───────────────────────────────────────────────
    
    def _find_rule(self, rule_id: int) -> Optional[Dict[str, Any]]:
        for rule in self.rules:
            if rule["rule_id"] == rule_id:
                return rule
        return None
    
    def _evaluate_condition(
        self, 
        condition: Dict[str, str], 
        payload: Dict[str, Any]
    ) -> bool:
        field = condition["field"]
        op = condition["op"]
        expected = condition["value"]
        
        actual = payload.get(field)
        if actual is None:
            # Also check current state if not in payload
            actual = self._get_nested_value(self.current_state, field)
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
    
    def _get_nested_value(self, data: Dict, key_path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        keys = key_path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _update_current_state_from_event(self, event: Dict[str, Any]) -> None:
        """Update current state based on incoming event data."""
        payload = event["payload"]
        event_type = event["event_type"]
        
        if event_type == "weather_change":
            if "temperature" in payload:
                self.current_state["room_temperature"] = payload["temperature"]
            if "humidity" in payload:
                self.current_state["humidity"] = payload["humidity"]
            if "weather" in payload:
                # Adjust AC mode based on weather
                if payload["weather"] in ["sunny", "hot"]:
                    self.current_state["air_conditioner"]["mode"] = "cool"
                elif payload["weather"] in ["rainy", "cloudy"]:
                    self.current_state["air_conditioner"]["mode"] = "dry"
        
        elif event_type == "electricity_rate_change":
            if "rate" in payload:
                self.current_state["energy_consumption"]["current_rate"] = payload["rate"]
            if "current_cost" in payload:
                self.current_state["energy_consumption"]["current_cost"] = payload["current_cost"]
        
        elif event_type == "health_status_change":
            if "heart_rate" in payload:
                self.current_state["user_health"]["heart_rate"] = payload["heart_rate"]
            if "activity_level" in payload:
                self.current_state["user_health"]["activity_level"] = payload["activity_level"]
            if "comfort_preference" in payload:
                self.current_state["user_health"]["comfort_preference"] = payload["comfort_preference"]
        
        elif event_type == "user_override":
            # User manual override takes precedence
            if "ac_target_temp" in payload:
                self.current_state["air_conditioner"]["target_temp"] = payload["ac_target_temp"]
            if "ac_power" in payload:
                self.current_state["air_conditioner"]["power"] = payload["ac_power"]
    
    def _execute_adaptive_action(
        self, 
        action: Dict[str, Any], 
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an adaptive control action and update environment state."""
        action_type = action.get("type", "unknown")
        params = action.get("params", {})
        
        # Energy cost calculation
        energy_before = self.current_state["energy_consumption"]["total_today"]
        
        # Perform the action
        if action_type == "adjust_ac_temperature":
            delta = params.get("delta", 0)
            min_temp = params.get("min_temp", 18)
            max_temp = params.get("max_temp", 30)
            current_temp = self.current_state["air_conditioner"]["target_temp"]
            new_temp = max(min_temp, min(max_temp, current_temp + delta))
            self.current_state["air_conditioner"]["target_temp"] = round(new_temp, 1)
            
            # Energy consumption update
            if self.current_state["air_conditioner"]["power"]:
                rate = self.current_state["energy_consumption"]["current_rate"]
                rate_multiplier = {
                    "off_peak": 0.7,
                    "mid_peak": 1.0,
                    "peak": 1.5,
                    "critical_peak": 2.0
                }.get(rate, 1.0)
                
                # More aggressive temperature changes consume more energy
                energy_used = abs(delta) * 0.1 * rate_multiplier
                self.current_state["energy_consumption"]["total_today"] += energy_used
            
            output = f"AC temperature adjusted to {self.current_state['air_conditioner']['target_temp']}°C"
        
        elif action_type == "set_ac_mode":
            mode = params.get("mode", "auto")
            valid_modes = ["cool", "heat", "dry", "fan", "auto"]
            if mode in valid_modes:
                self.current_state["air_conditioner"]["mode"] = mode
                output = f"AC mode set to {mode}"
            else:
                output = f"Invalid AC mode: {mode}"
        
        elif action_type == "toggle_ac_power":
            power = params.get("power")
            if power is not None:
                new_power = bool(power)
            else:
                new_power = not self.current_state["air_conditioner"]["power"]
            
            self.current_state["air_conditioner"]["power"] = new_power
            output = f"AC power {'ON' if new_power else 'OFF'}"
            
            # Update energy if turning off
            if not new_power:
                self.current_state["energy_consumption"]["total_today"] -= 0.5  # Estimated saving
        
        elif action_type == "set_humidifier":
            target_humidity = params.get("target_humidity", 50)
            target_humidity = max(30, min(70, target_humidity))  # Safe range
            self.current_state["humidifier"]["target_humidity"] = round(target_humidity, 1)
            output = f"Humidifier target set to {target_humidity}%"
        
        elif action_type == "toggle_humidifier_power":
            power = params.get("power")
            if power is not None:
                new_power = bool(power)
            else:
                new_power = not self.current_state["humidifier"]["power"]
            
            self.current_state["humidifier"]["power"] = new_power
            output = f"Humidifier power {'ON' if new_power else 'OFF'}"
            
            # Adjust current humidity if turning on/off
            if new_power:
                self.current_state["humidity"] += 0.5
            else:
                self.current_state["humidity"] -= 0.5
            self.current_state["humidity"] = max(0, min(100, self.current_state["humidity"]))
        
        elif action_type == "toggle_outlet":
            outlet = params.get("outlet", "outlet_1")
            power = params.get("power")
            
            if outlet in self.current_state["smart_outlets"]:
                if power is not None:
                    new_power = bool(power)
                else:
                    new_power = not self.current_state["smart_outlets"][outlet]
                
                self.current_state["smart_outlets"][outlet] = new_power
                output = f"Outlet {outlet} {'ON' if new_power else 'OFF'}"
            else:
                output = f"Invalid outlet: {outlet}"
        
        elif action_type == "set_all_outlets":
            power = params.get("power", False)
            for outlet in self.current_state["smart_outlets"]:
                self.current_state["smart_outlets"][outlet] = power
            output = f"All outlets set to {'ON' if power else 'OFF'}"
        
        elif action_type == "update_user_preference":
            preference = params.get("preference", "normal")
            valid_prefs = ["energy_saving", "normal", "max_comfort", "health_focused"]
            
            if preference in valid_prefs:
                self.current_state["user_health"]["comfort_preference"] = preference
                output = f"User preference updated to {preference}"
                
                # Adjust settings based on preference
                if preference == "energy_saving":
                    # Increase AC temperature to save energy
                    current = self.current_state["air_conditioner"]["target_temp"]
                    self.current_state["air_conditioner"]["target_temp"] = min(28, current + 1)
                elif preference == "max_comfort":
                    current = self.current_state["air_conditioner"]["target_temp"]
                    self.current_state["air_conditioner"]["target_temp"] = max(22, current - 1)
            else:
                output = f"Invalid preference: {preference}"
        
        elif action_type == "calculate_energy_optimization":
            rate = self.current_state["energy_consumption"]["current_rate"]
            current_temp = self.current_state["room_temperature"]
            target_temp = self.current_state["air_conditioner"]["target_temp"]
            
            # Simple optimization logic
            if rate in ["peak", "critical_peak"]:
                if target_temp < 25 and current_temp < 28:
                    # Increase target temp during peak hours
                    optimized_temp = min(27, target_temp + 2)
                    self.current_state["air_conditioner"]["target_temp"] = optimized_temp
                    output = f"Energy optimization: increased AC target to {optimized_temp}°C during {rate} rate"
                else:
                    output = "Energy optimization: no adjustment needed"
            else:
                output = "Energy optimization: non-peak rate, maintaining settings"
        
        else:
            output = f"Unknown action type: {action_type}"
        
        energy_after = self.current_state["energy_consumption"]["total_today"]
        energy_change = round(energy_after - energy_before, 2)
        
        result = {
            "action_type": action_type,
            "params": params,
            "event_id": event["event_id"],
            "status": "executed",
            "output": output,
            "energy_change": energy_change,
            "timestamp": event["timestamp"]
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