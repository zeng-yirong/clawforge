from copy import deepcopy
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

# Global default state
DEFAULT_STATE = {
    "environments": [],
    "devices": [],
    "subscriptions": [],
    "weather_history": [],
    "price_history": [],
    "health_history": [],
    "adjustment_history": {},
    "environment_counter": 1,
    "device_counter": 1,
    "subscription_counter": 1,
    "adjustment_counter": 1,
    "weather_counter": 1,
    "price_counter": 1,
    "health_counter": 1,
}

# Constant definitions
VALID_ENVIRONMENT_TYPES = ("indoor", "outdoor", "hybrid")
VALID_DEVICE_TYPES = ("air_conditioner", "humidifier", "smart_plug")
VALID_DEVICE_STATUSES = ("off", "standby", "active", "error")
VALID_ADJUSTMENT_MODES = ("auto", "manual", "scheduled")
VALID_SEVERITY_LEVELS = ("low", "medium", "high", "critical")


class AdaptiveEnvControl:
    """
    A multidimensional adaptive environment control system with real-time streaming.
    
    This system combines weather API data, tiered electricity pricing curves, and user
    health data to dynamically adjust air conditioner temperature, humidifier, and smart
    plugs. It uses a publish-subscribe pattern to notify subscribed components about
    environmental changes that require adaptive responses.
    
    Core concept: Define environments (indoor/outdoor) → Register adaptive devices →
    Subscribe to specific environmental factors → Receive async notifications when
    thresholds are breached → Send adjustment commands based on multi-factor optimization.
    
    Attributes:
        environments (List[Dict]): Defined environmental zones with properties.
        devices (List[Dict]): Registered adaptive devices with configurations.
        subscriptions (List[Dict]): Active subscriptions for environmental factor monitoring.
        weather_history (List[Dict]): Historical weather data records.
        price_history (List[Dict]): Historical electricity pricing records.
        health_history (List[Dict]): Historical user health metrics.
        adjustment_history (Dict[str, List[Dict]]): Adjustment logs keyed by environment_id.
        environment_counter (int): Auto-incrementing environment ID counter.
        device_counter (int): Auto-incrementing device ID counter.
        subscription_counter (int): Auto-incrementing subscription ID counter.
        adjustment_counter (int): Auto-incrementing adjustment ID counter.
    """

    def __init__(self):
        self.environments: List[Dict[str, Any]]
        self.devices: List[Dict[str, Any]]
        self.subscriptions: List[Dict[str, Any]]
        self.weather_history: List[Dict[str, Any]]
        self.price_history: List[Dict[str, Any]]
        self.health_history: List[Dict[str, Any]]
        self.adjustment_history: Dict[str, List[Dict[str, Any]]]
        self.environment_counter: int
        self.device_counter: int
        self.subscription_counter: int
        self.adjustment_counter: int
        self.weather_counter: int
        self.price_counter: int
        self.health_counter: int
        
        self._api_description = (
            "This tool manages multidimensional adaptive environmental control by "
            "combining real-time weather data, electricity pricing, and user health "
            "metrics to optimize air conditioner, humidifier, and smart plug settings."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """Load initial state from scenario dictionary, fallback to DEFAULT_STATE."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.environments = scenario.get("environments", DEFAULT_STATE_COPY["environments"])
        self.devices = scenario.get("devices", DEFAULT_STATE_COPY["devices"])
        self.subscriptions = scenario.get("subscriptions", DEFAULT_STATE_COPY["subscriptions"])
        self.weather_history = scenario.get("weather_history", DEFAULT_STATE_COPY["weather_history"])
        self.price_history = scenario.get("price_history", DEFAULT_STATE_COPY["price_history"])
        self.health_history = scenario.get("health_history", DEFAULT_STATE_COPY["health_history"])
        self.adjustment_history = scenario.get("adjustment_history", DEFAULT_STATE_COPY["adjustment_history"])
        self.environment_counter = scenario.get("environment_counter", DEFAULT_STATE_COPY["environment_counter"])
        self.device_counter = scenario.get("device_counter", DEFAULT_STATE_COPY["device_counter"])
        self.subscription_counter = scenario.get("subscription_counter", DEFAULT_STATE_COPY["subscription_counter"])
        self.adjustment_counter = scenario.get("adjustment_counter", DEFAULT_STATE_COPY["adjustment_counter"])
        self.weather_counter = scenario.get("weather_counter", DEFAULT_STATE_COPY["weather_counter"])
        self.price_counter = scenario.get("price_counter", DEFAULT_STATE_COPY["price_counter"])
        self.health_counter = scenario.get("health_counter", DEFAULT_STATE_COPY["health_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.
        
        Returns:
            dict: All environment state variables including environments, devices,
                  subscriptions, historical data, and counters.
        """
        return {
            "environments": self.environments,
            "devices": self.devices,
            "subscriptions": self.subscriptions,
            "weather_history": self.weather_history[-50:] if self.weather_history else [],
            "price_history": self.price_history[-50:] if self.price_history else [],
            "health_history": self.health_history[-50:] if self.health_history else [],
            "adjustment_history": self.adjustment_history,
            "environment_counter": self.environment_counter,
            "device_counter": self.device_counter,
            "subscription_counter": self.subscription_counter,
            "adjustment_counter": self.adjustment_counter,
            "weather_counter": self.weather_counter,
            "price_counter": self.price_counter,
            "health_counter": self.health_counter,
        }

    # ── Environment Management ─────────────────────────────────────────────

    def create_environment(
        self,
        name: str,
        env_type: str = "indoor",
        area_m2: float = 20.0,
        target_temperature: float = 24.0,
        target_humidity: float = 45.0,
        occupants: int = 1,
    ) -> Dict[str, Any]:
        """
        Define a new environmental zone for adaptive control.
        
        Args:
            name (str): Environment name (e.g., 'living_room', 'bedroom').
            env_type (str): Environment type - 'indoor', 'outdoor', or 'hybrid'.
            area_m2 (float): Area in square meters.
            target_temperature (float): Comfort target temperature in Celsius.
            target_humidity (float): Comfort target humidity percentage.
            occupants (int): Number of occupants in the environment.
            
        Returns:
            environment_id (int): Unique environment identifier.
            environment (Dict): The created environment record.
        """
        if env_type not in VALID_ENVIRONMENT_TYPES:
            return {"error": f"Invalid env_type '{env_type}'. Must be one of: {', '.join(VALID_ENVIRONMENT_TYPES)}"}
        if area_m2 <= 0:
            return {"error": "Area must be positive."}
        if occupants < 0:
            return {"error": "Occupants cannot be negative."}

        env_id = self.environment_counter
        self.environment_counter += 1

        environment = {
            "environment_id": env_id,
            "name": name,
            "env_type": env_type,
            "area_m2": area_m2,
            "current_temperature": target_temperature,  # Initial state
            "current_humidity": target_humidity,         # Initial state
            "target_temperature": target_temperature,
            "target_humidity": target_humidity,
            "occupants": occupants,
            "devices": [],
            "status": "active",
            "created_at": f"t+{env_id}",
        }
        self.environments.append(environment)
        self.adjustment_history[str(env_id)] = []
        return {"environment_id": env_id, "environment": environment}

    def list_environments(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all defined environments.
        
        Returns:
            environments (List[Dict]): Environment summaries with id, name, type, and current status.
        """
        summaries = [{
            "environment_id": e["environment_id"],
            "name": e["name"],
            "env_type": e["env_type"],
            "current_temperature": e["current_temperature"],
            "current_humidity": e["current_humidity"],
            "devices_count": len(e["devices"]),
            "status": e["status"],
        } for e in self.environments]
        return {"environments": summaries}

    def get_environment_state(self, environment_id: int) -> Dict[str, Any]:
        """
        Get the full state of an environment including recent adjustments.
        
        Args:
            environment_id (int): Environment ID.
            
        Returns:
            environment (Dict): Full environment record with recent adjustments.
        """
        env = self._find_environment(environment_id)
        if not env:
            return {"error": f"Environment ID {environment_id} not found."}
        adjustments = self.adjustment_history.get(str(environment_id), [])
        return {
            "environment": env,
            "recent_adjustments": adjustments[-10:],
            "total_adjustments": len(adjustments),
        }

    # ── Device Management ─────────────────────────────────────────────────

    def register_device(
        self,
        environment_id: int,
        device_type: str,
        name: str,
        min_value: float = 0.0,
        max_value: float = 100.0,
        default_value: float = 50.0,
        power_rating_w: float = 1000.0,
    ) -> Dict[str, Any]:
        """
        Register an adaptive device to an environment.
        
        Args:
            environment_id (int): Target environment ID.
            device_type (str): Device type - 'air_conditioner', 'humidifier', or 'smart_plug'.
            name (str): Device name/identifier.
            min_value (float): Minimum operational value (e.g., temperature in °C or humidity %).
            max_value (float): Maximum operational value.
            default_value (float): Default operational value.
            power_rating_w (float): Power rating in watts.
            
        Returns:
            device_id (int): Unique device identifier.
            device (Dict): The created device record.
        """
        env = self._find_environment(environment_id)
        if not env:
            return {"error": f"Environment ID {environment_id} not found."}
        if device_type not in VALID_DEVICE_TYPES:
            return {"error": f"Invalid device_type '{device_type}'. Must be one of: {', '.join(VALID_DEVICE_TYPES)}"}
        if min_value >= max_value:
            return {"error": "min_value must be less than max_value."}
        if not (min_value <= default_value <= max_value):
            return {"error": f"default_value {default_value} must be between min_value {min_value} and max_value {max_value}."}

        device_id = self.device_counter
        self.device_counter += 1

        device = {
            "device_id": device_id,
            "environment_id": environment_id,
            "device_type": device_type,
            "name": name,
            "current_value": default_value,
            "min_value": min_value,
            "max_value": max_value,
            "target_value": default_value,
            "power_rating_w": power_rating_w,
            "status": "standby",
            "power_consumption_kwh": 0.0,
            "created_at": f"t+{device_id}",
        }
        self.devices.append(device)
        env["devices"].append(device_id)
        return {"device_id": device_id, "device": device}

    def list_devices(self, environment_id: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered devices, optionally filtered by environment.
        
        Args:
            environment_id (int): [Optional] Filter by environment ID.
            
        Returns:
            devices (List[Dict]): Matching device records.
        """
        devices = self.devices
        if environment_id is not None:
            devices = [d for d in devices if d["environment_id"] == environment_id]
        return {"devices": devices}

    def update_device_status(
        self,
        device_id: int,
        status: str,
        current_value: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Update device operational status and current value.
        
        Args:
            device_id (int): Device ID.
            status (str): New status - 'off', 'standby', 'active', or 'error'.
            current_value (float): [Optional] New current value if changing.
            
        Returns:
            device_id (int): The device ID.
            status (str): Updated status.
            current_value (float): Current operational value.
        """
        device = self._find_device(device_id)
        if not device:
            return {"error": f"Device ID {device_id} not found."}
        if status not in VALID_DEVICE_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_DEVICE_STATUSES)}"}
        
        device["status"] = status
        if current_value is not None:
            if not (device["min_value"] <= current_value <= device["max_value"]):
                return {"error": f"current_value {current_value} must be between {device['min_value']} and {device['max_value']}."}
            device["current_value"] = current_value
            
        return {
            "device_id": device_id,
            "status": status,
            "current_value": device["current_value"],
        }

    # ── Subscription Management ──────────────────────────────────────────

    def subscribe_environment_factor(
        self,
        environment_id: int,
        factor_type: str,
        threshold_min: Optional[float] = None,
        threshold_max: Optional[float] = None,
        adjustment_mode: str = "auto",
        severity_level: str = "medium",
    ) -> Dict[str, Any]:
        """
        Subscribe to an environmental factor for adaptive control notifications.
        
        When the factor exceeds threshold bounds, subscribers receive notifications
        to trigger adaptive adjustments. Uses push delivery for async notifications.
        
        Args:
            environment_id (int): Target environment ID.
            factor_type (str): Factor to monitor - 'temperature', 'humidity', 'price', or 'health'.
            threshold_min (float): [Optional] Lower bound threshold.
            threshold_max (float): [Optional] Upper bound threshold.
            adjustment_mode (str): Adjustment mode - 'auto', 'manual', or 'scheduled'.
            severity_level (str): Severity for threshold breaches - 'low', 'medium', 'high', 'critical'.
            
        Returns:
            subscription_id (int): Unique subscription identifier.
            subscription (Dict): The created subscription record.
        """
        env = self._find_environment(environment_id)
        if not env:
            return {"error": f"Environment ID {environment_id} not found."}
        if factor_type not in ["temperature", "humidity", "price", "health"]:
            return {"error": f"Invalid factor_type '{factor_type}'. Must be: temperature, humidity, price, or health."}
        if adjustment_mode not in VALID_ADJUSTMENT_MODES:
            return {"error": f"Invalid adjustment_mode '{adjustment_mode}'. Must be one of: {', '.join(VALID_ADJUSTMENT_MODES)}"}
        if severity_level not in VALID_SEVERITY_LEVELS:
            return {"error": f"Invalid severity_level '{severity_level}'. Must be one of: {', '.join(VALID_SEVERITY_LEVELS)}"}
        if threshold_min is not None and threshold_max is not None and threshold_min >= threshold_max:
            return {"error": "threshold_min must be less than threshold_max."}

        sub_id = self.subscription_counter
        self.subscription_counter += 1

        subscription = {
            "subscription_id": sub_id,
            "environment_id": environment_id,
            "factor_type": factor_type,
            "threshold_min": threshold_min,
            "threshold_max": threshold_max,
            "adjustment_mode": adjustment_mode,
            "severity_level": severity_level,
            "status": "active",
            "breach_count": 0,
            "notifications": [],
            "created_at": f"t+{sub_id}",
        }
        self.subscriptions.append(subscription)
        return {"subscription_id": sub_id, "subscription": subscription}

    def unsubscribe(self, subscription_id: int) -> Dict[str, str]:
        """
        Cancel an active subscription.
        
        Args:
            subscription_id (int): Subscription ID to cancel.
            
        Returns:
            status (str): Cancellation confirmation.
        """
        sub = self._find_subscription(subscription_id)
        if not sub:
            return {"error": f"Subscription ID {subscription_id} not found."}
        if sub["status"] != "active":
            return {"error": f"Subscription {subscription_id} is already {sub['status']}."}

        sub["status"] = "cancelled"
        return {"status": f"Subscription {subscription_id} cancelled."}

    def list_subscriptions(
        self, environment_id: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List subscriptions, optionally filtered by environment.
        
        Args:
            environment_id (int): [Optional] Filter by environment ID.
            
        Returns:
            subscriptions (List[Dict]): Matching subscription records.
        """
        subs = self.subscriptions
        if environment_id is not None:
            subs = [s for s in subs if s["environment_id"] == environment_id]
        return {"subscriptions": subs}

    def get_notifications(self, subscription_id: int) -> Dict[str, Any]:
        """
        Get pending notifications for a subscription.
        
        Args:
            subscription_id (int): Subscription ID.
            
        Returns:
            subscription_id (int): The subscription ID.
            notifications (List[Dict]): Pending notification records.
            count (int): Number of pending notifications.
        """
        sub = self._find_subscription(subscription_id)
        if not sub:
            return {"error": f"Subscription ID {subscription_id} not found."}
        return {
            "subscription_id": subscription_id,
            "notifications": sub["notifications"],
            "count": len(sub["notifications"]),
        }

    def acknowledge_notification(self, subscription_id: int, notification_id: int) -> Dict[str, Any]:
        """
        Acknowledge receipt of a notification.
        
        Args:
            subscription_id (int): Subscription ID.
            notification_id (int): Notification ID to acknowledge.
            
        Returns:
            subscription_id (int): The subscription ID.
            acknowledged (int): The acknowledged notification ID.
            remaining (int): Remaining unacknowledged notifications.
        """
        sub = self._find_subscription(subscription_id)
        if not sub:
            return {"error": f"Subscription ID {subscription_id} not found."}
        
        # Find and remove the notification
        for i, notif in enumerate(sub["notifications"]):
            if notif.get("notification_id") == notification_id:
                sub["notifications"].pop(i)
                return {
                    "subscription_id": subscription_id,
                    "acknowledged": notification_id,
                    "remaining": len(sub["notifications"]),
                }
        return {"error": f"Notification ID {notification_id} not found for subscription {subscription_id}."}

    # ── Data Streaming & Event Push ──────────────────────────────────────

    def push_weather_data(
        self,
        environment_id: int,
        temperature: float,
        humidity: float,
        pressure: float = 1013.25,
    ) -> Dict[str, Any]:
        """
        Push weather data to an environment. Triggers subscription checks.
        
        Args:
            environment_id (int): Target environment ID.
            temperature (float): Temperature in Celsius.
            humidity (float): Humidity percentage.
            pressure (float): Atmospheric pressure in hPa.
            
        Returns:
            weather_id (int): Unique weather record identifier.
            weather (Dict): The weather data record.
            triggered_subscriptions (List[int]): Subscription IDs that were triggered.
        """
        env = self._find_environment(environment_id)
        if not env:
            return {"error": f"Environment ID {environment_id} not found."}

        weather_record = {
            "weather_id": self.weather_counter,
            "environment_id": environment_id,
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "timestamp": f"t+{self.weather_counter}",
        }
        self.weather_history.append(weather_record)
        self.weather_counter += 1

        # Update environment state
        env["current_temperature"] = temperature
        env["current_humidity"] = humidity

        # Check subscriptions
        triggered = []
        for sub in self.subscriptions:
            if (sub["environment_id"] == environment_id and 
                sub["status"] == "active" and 
                sub["factor_type"] in ["temperature", "humidity"]):
                
                if self._check_threshold_breach(weather_record, sub):
                    notification_id = len(sub["notifications"]) + 1
                    notification = {
                        "notification_id": notification_id,
                        "subscription_id": sub["subscription_id"],
                        "factor_type": sub["factor_type"],
                        "severity_level": sub["severity_level"],
                        "current_value": temperature if sub["factor_type"] == "temperature" else humidity,
                        "threshold_min": sub["threshold_min"],
                        "threshold_max": sub["threshold_max"],
                        "timestamp": f"t+{notification_id}",
                    }
                    sub["notifications"].append(notification)
                    sub["breach_count"] += 1
                    triggered.append(sub["subscription_id"])

        return {
            "weather_id": weather_record["weather_id"],
            "weather": weather_record,
            "triggered_subscriptions": triggered,
        }

    def push_price_data(
        self,
        price_tier: str,
        price_per_kwh: float,
        time_block: str = "peak",
    ) -> Dict[str, Any]:
        """
        Push electricity pricing data. Triggers subscription checks.
        
        Args:
            price_tier (str): Pricing tier identifier.
            price_per_kwh (float): Price per kWh in local currency.
            time_block (str): Time period - 'off_peak', 'mid', or 'peak'.
            
        Returns:
            price_id (int): Unique price record identifier.
            price (Dict): The price data record.
            triggered_subscriptions (List[int]): Subscription IDs that were triggered.
        """
        if price_per_kwh is None or price_per_kwh < 0:
            return {"error": "Price per kWh cannot be negative."}

        price_record = {
            "price_id": self.price_counter,
            "price_tier": price_tier,
            "price_per_kwh": price_per_kwh,
            "time_block": time_block,
            "timestamp": f"t+{self.price_counter}",
        }
        self.price_history.append(price_record)
        self.price_counter += 1

        # Check subscriptions for price factor
        triggered = []
        for sub in self.subscriptions:
            if sub["status"] == "active" and sub["factor_type"] == "price":
                if sub["threshold_max"] is not None and price_per_kwh > sub["threshold_max"]:
                    notification_id = len(sub["notifications"]) + 1
                    notification = {
                        "notification_id": notification_id,
                        "subscription_id": sub["subscription_id"],
                        "factor_type": sub["factor_type"],
                        "severity_level": sub["severity_level"],
                        "current_value": price_per_kwh,
                        "threshold_max": sub["threshold_max"],
                        "timestamp": f"t+{notification_id}",
                    }
                    sub["notifications"].append(notification)
                    sub["breach_count"] += 1
                    triggered.append(sub["subscription_id"])

        return {
            "price_id": price_record["price_id"],
            "price": price_record,
            "triggered_subscriptions": triggered,
        }

    def push_health_data(
        self,
        environment_id: int,
        heart_rate: int,
        respiratory_rate: int,
        thermal_comfort: float,
    ) -> Dict[str, Any]:
        """
        Push user health data for adaptive comfort optimization.
        
        Args:
            environment_id (int): Target environment ID.
            heart_rate (int): Heart rate in BPM.
            respiratory_rate (int): Respiratory rate in breaths per minute.
            thermal_comfort (float): Thermal comfort score (0-10).
            
        Returns:
            health_id (int): Unique health record identifier.
            health (Dict): The health data record.
            triggered_subscriptions (List[int]): Subscription IDs that were triggered.
        """
        if thermal_comfort is None or not (0 <= thermal_comfort <= 10):
            return {"error": "Thermal comfort score must be between 0 and 10."}

        health_record = {
            "health_id": self.health_counter,
            "environment_id": environment_id,
            "heart_rate": heart_rate,
            "respiratory_rate": respiratory_rate,
            "thermal_comfort": thermal_comfort,
            "timestamp": f"t+{self.health_counter}",
        }
        self.health_history.append(health_record)
        self.health_counter += 1

        # Check subscriptions for health factor
        triggered = []
        for sub in self.subscriptions:
            if (sub["environment_id"] == environment_id and 
                sub["status"] == "active" and 
                sub["factor_type"] == "health"):
                
                # Check thermal comfort threshold
                if (sub["threshold_min"] is not None and thermal_comfort < sub["threshold_min"]):
                    notification_id = len(sub["notifications"]) + 1
                    notification = {
                        "notification_id": notification_id,
                        "subscription_id": sub["subscription_id"],
                        "factor_type": sub["factor_type"],
                        "severity_level": sub["severity_level"],
                        "current_value": thermal_comfort,
                        "threshold_min": sub["threshold_min"],
                        "timestamp": f"t+{notification_id}",
                    }
                    sub["notifications"].append(notification)
                    sub["breach_count"] += 1
                    triggered.append(sub["subscription_id"])

        return {
            "health_id": health_record["health_id"],
            "health": health_record,
            "triggered_subscriptions": triggered,
        }

    # ── Adaptive Adjustment ──────────────────────────────────────────────

    def adjust_device(
        self,
        device_id: int,
        target_value: float,
        adjustment_reason: str = "optimization",
    ) -> Dict[str, Any]:
        """
        Adjust a device's target value based on multi-factor optimization.
        
        Args:
            device_id (int): Device ID to adjust.
            target_value (float): New target value.
            adjustment_reason (str): Reason for adjustment.
            
        Returns:
            adjustment_id (int): Unique adjustment identifier.
            adjustment (Dict): The adjustment record.
            estimated_power_change (float): Estimated power change in kWh.
        """
        device = self._find_device(device_id)
        if not device:
            return {"error": f"Device ID {device_id} not found."}
        if not (device["min_value"] <= target_value <= device["max_value"]):
            return {"error": f"target_value {target_value} must be between {device['min_value']} and {device['max_value']}."}

        adjustment_id = self.adjustment_counter
        self.adjustment_counter += 1

        old_value = device["target_value"]
        device["target_value"] = target_value
        
        # Calculate estimated power change (simplified model)
        power_change = abs(target_value - old_value) * device["power_rating_w"] / 1000 / 3600  # kWh per hour
        
        adjustment_record = {
            "adjustment_id": adjustment_id,
            "device_id": device_id,
            "environment_id": device["environment_id"],
            "device_type": device["device_type"],
            "old_value": old_value,
            "new_value": target_value,
            "adjustment_reason": adjustment_reason,
            "power_change_kwh": power_change,
            "timestamp": f"t+{adjustment_id}",
        }
        
        # Store in history
        env_history = self.adjustment_history.get(str(device["environment_id"]), [])
        env_history.append(adjustment_record)
        self.adjustment_history[str(device["environment_id"])] = env_history

        return {
            "adjustment_id": adjustment_id,
            "adjustment": adjustment_record,
            "estimated_power_change": power_change,
        }

    def compute_optimal_adjustment(
        self,
        environment_id: int,
        include_price: bool = True,
        include_health: bool = True,
    ) -> Dict[str, Any]:
        """
        Compute optimal device adjustments based on current multi-factor state.
        
        Args:
            environment_id (int): Environment ID.
            include_price (bool): Whether to consider electricity pricing.
            include_health (bool): Whether to consider health data.
            
        Returns:
            environment_id (int): The environment ID.
            optimal_adjustments (List[Dict]): Recommended device adjustments.
            total_power_change (float): Total estimated power change in kWh.
        """
        env = self._find_environment(environment_id)
        if not env:
            return {"error": f"Environment ID {environment_id} not found."}
        
        devices = [d for d in self.devices if d["environment_id"] == environment_id]
        if not devices:
            return {"error": f"No devices found for environment {environment_id}."}
        
        optimal_adjustments = []
        total_power_change = 0.0
        
        # Simplified optimization logic
        current_temp = env["current_temperature"]
        target_temp = env["target_temperature"]
        current_humidity = env["current_humidity"]
        target_humidity = env["target_humidity"]
        
        # Get current price (most recent)
        current_price = 0.1  # Default
        if self.price_history and include_price:
            current_price = self.price_history[-1]["price_per_kwh"]
        
        # Get health score (most recent for this environment)
        health_score = 5.0  # Default neutral
        if self.health_history and include_health:
            env_health = [h for h in self.health_history if h["environment_id"] == environment_id]
            if env_health:
                health_score = env_health[-1]["thermal_comfort"]
        
        for device in devices:
            if device["device_type"] == "air_conditioner":
                # Adjust based on temperature delta, price, and health
                temp_delta = current_temp - target_temp
                price_factor = 1.0 if current_price < 0.15 else 0.8  # Reduce adjustment if price high
                health_factor = max(0.5, min(1.5, health_score / 5))  # Scale by comfort
                
                adjustment = temp_delta * -0.5 * price_factor * health_factor
                new_target = max(device["min_value"], min(device["max_value"], 
                                        device["target_value"] + adjustment))
                
            elif device["device_type"] == "humidifier":
                # Adjust based on humidity delta
                humidity_delta = target_humidity - current_humidity
                adjustment = humidity_delta * 0.3
                new_target = max(device["min_value"], min(device["max_value"], 
                                        device["target_value"] + adjustment))
                
            elif device["device_type"] == "smart_plug":
                # Smart plugs adjust based on price and occupancy
                occupancy_factor = 1.0 if env["occupants"] > 0 else 0.3
                price_factor = 0.3 if current_price > 0.2 else 1.0
                new_target = device["max_value"] * occupancy_factor * price_factor
                new_target = max(device["min_value"], min(device["max_value"], new_target))
                
            else:
                new_target = device["target_value"]
            
            if new_target != device["target_value"]:
                power_change = abs(new_target - device["target_value"]) * device["power_rating_w"] / 1000 / 3600
                total_power_change += power_change
                
                optimal_adjustments.append({
                    "device_id": device["device_id"],
                    "device_type": device["device_type"],
                    "current_target": device["target_value"],
                    "recommended_target": new_target,
                    "estimated_power_change": power_change,
                })
        
        return {
            "environment_id": environment_id,
            "optimal_adjustments": optimal_adjustments,
            "total_power_change": total_power_change,
        }

    # ── Data Retrieval ───────────────────────────────────────────────────

    def get_weather_history(
        self,
        environment_id: Optional[int] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Retrieve weather history, optionally filtered by environment.
        
        Args:
            environment_id (int): [Optional] Filter by environment ID.
            limit (int): Maximum number of records to return.
            
        Returns:
            weather_history (List[Dict]): Matching weather records, newest first.
            total (int): Total weather records.
        """
        history = self.weather_history
        if environment_id is not None:
            history = [w for w in history if w["environment_id"] == environment_id]
        
        recent = list(reversed(history[-limit:]))
        return {
            "weather_history": recent,
            "total": len(history),
            "filtered_by_environment": environment_id is not None,
        }

    def get_price_history(
        self,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Retrieve electricity pricing history.
        
        Args:
            limit (int): Maximum number of records to return.
            
        Returns:
            price_history (List[Dict]): Price records, newest first.
            total (int): Total price records.
        """
        recent = list(reversed(self.price_history[-limit:]))
        return {
            "price_history": recent,
            "total": len(self.price_history),
        }

    def get_health_history(
        self,
        environment_id: Optional[int] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Retrieve health data history, optionally filtered by environment.
        
        Args:
            environment_id (int): [Optional] Filter by environment ID.
            limit (int): Maximum number of records to return.
            
        Returns:
            health_history (List[Dict]): Matching health records, newest first.
            total (int): Total health records.
        """
        history = self.health_history
        if environment_id is not None:
            history = [h for h in history if h["environment_id"] == environment_id]
        
        recent = list(reversed(history[-limit:]))
        return {
            "health_history": recent,
            "total": len(history),
            "filtered_by_environment": environment_id is not None,
        }

    def get_adjustment_history(
        self,
        environment_id: int,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Retrieve adjustment history for an environment.
        
        Args:
            environment_id (int): Environment ID.
            limit (int): Maximum number of records to return.
            
        Returns:
            environment_id (int): The environment ID.
            adjustments (List[Dict]): Adjustment records, newest first.
            total (int): Total adjustments for this environment.
        """
        adjustments = self.adjustment_history.get(str(environment_id), [])
        recent = list(reversed(adjustments[-limit:]))
        return {
            "environment_id": environment_id,
            "adjustments": recent,
            "total": len(adjustments),
        }

    # ── Helper Methods ───────────────────────────────────────────────────

    def _find_environment(self, environment_id: int) -> Optional[Dict[str, Any]]:
        """Find an environment by ID. Returns None if not found."""
        for e in self.environments:
            if e["environment_id"] == environment_id:
                return e
        return None

    def _find_device(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Find a device by ID. Returns None if not found."""
        for d in self.devices:
            if d["device_id"] == device_id:
                return d
        return None

    def _find_subscription(self, subscription_id: int) -> Optional[Dict[str, Any]]:
        """Find a subscription by ID. Returns None if not found."""
        for s in self.subscriptions:
            if s["subscription_id"] == subscription_id:
                return s
        return None

    @staticmethod
    def _check_threshold_breach(data_record: Dict, subscription: Dict) -> bool:
        """Check if data record breaches subscription thresholds."""
        factor_type = subscription["factor_type"]
        
        if factor_type == "temperature":
            value = data_record.get("temperature")
        elif factor_type == "humidity":
            value = data_record.get("humidity")
        elif factor_type == "price":
            value = data_record.get("price_per_kwh")
        elif factor_type == "health":
            value = data_record.get("thermal_comfort")
        else:
            return False
        
        if value is None:
            return False
            
        min_thresh = subscription.get("threshold_min")
        max_thresh = subscription.get("threshold_max")
        
        # Check if value is outside threshold bounds
        if min_thresh is not None and value < min_thresh:
            return True
        if max_thresh is not None and value > max_thresh:
            return True

        return False

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })