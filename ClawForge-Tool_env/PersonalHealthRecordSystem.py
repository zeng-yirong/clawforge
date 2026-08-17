"""
Personal Health Record Management System

A digital platform for maintaining and updating individual health information,
such as physiological measurements, medical history, and wellness data.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

# Valid metric types and their corresponding valid units
VALID_METRIC_UNITS: Dict[str, List[str]] = {
    "weight": ["kg", "lb", "lbs"],
    "height": ["cm", "m", "in", "ft"],
    "blood_pressure_systolic": ["mmHg"],
    "blood_pressure_diastolic": ["mmHg"],
    "heart_rate": ["bpm"],
    "body_temperature": ["°C", "°F", "C", "F"],
    "blood_glucose": ["mg/dL", "mmol/L"],
    "oxygen_saturation": ["%"],
    "bmi": ["kg/m²", "kg/m2"],
    "cholesterol": ["mg/dL", "mmol/L"],
}

DEFAULT_STATE: Dict[str, Any] = {
    "users": [
        {
            "_id": "user_001",
            "name": "Alice Johnson",
            "date_of_birth": "1985-03-15",
            "gender": "female",
            "profile_created_date": "2023-01-10T09:00:00"
        },
        {
            "_id": "user_002",
            "name": "Bob Smith",
            "date_of_birth": "1978-07-22",
            "gender": "male",
            "profile_created_date": "2023-02-20T14:30:00"
        },
        {
            "_id": "user_003",
            "name": "Carol White",
            "date_of_birth": "1990-11-08",
            "gender": "female",
            "profile_created_date": "2023-03-05T11:15:00"
        }
    ],
    "health_metrics": [
        {
            "metric_id": "metric_001",
            "user_id": "user_001",
            "metric_type": "weight",
            "value": 65.5,
            "unit": "kg",
            "timestamp": "2024-01-15T08:00:00"
        },
        {
            "metric_id": "metric_002",
            "user_id": "user_001",
            "metric_type": "heart_rate",
            "value": 72,
            "unit": "bpm",
            "timestamp": "2024-01-15T08:05:00"
        },
        {
            "metric_id": "metric_003",
            "user_id": "user_002",
            "metric_type": "weight",
            "value": 82.0,
            "unit": "kg",
            "timestamp": "2024-01-14T07:30:00"
        },
        {
            "metric_id": "metric_004",
            "user_id": "user_002",
            "metric_type": "blood_pressure_systolic",
            "value": 120,
            "unit": "mmHg",
            "timestamp": "2024-01-14T07:35:00"
        },
        {
            "metric_id": "metric_005",
            "user_id": "user_003",
            "metric_type": "body_temperature",
            "value": 36.6,
            "unit": "°C",
            "timestamp": "2024-01-13T09:00:00"
        }
    ],
    "medical_history": [
        {
            "record_id": "mh_001",
            "user_id": "user_001",
            "condition": "Hypertension",
            "diagnosis_date": "2020-06-15",
            "notes": "Mild hypertension, managed with lifestyle changes",
            "status": "active"
        },
        {
            "record_id": "mh_002",
            "user_id": "user_001",
            "condition": "Seasonal Allergies",
            "diagnosis_date": "2018-04-10",
            "notes": "Spring allergies, treated with antihistamines",
            "status": "active"
        },
        {
            "record_id": "mh_003",
            "user_id": "user_002",
            "condition": "Type 2 Diabetes",
            "diagnosis_date": "2019-09-20",
            "notes": "Controlled with medication and diet",
            "status": "active"
        },
        {
            "record_id": "mh_004",
            "user_id": "user_003",
            "condition": "Appendicitis",
            "diagnosis_date": "2015-08-12",
            "notes": "Appendectomy performed successfully",
            "status": "resolved"
        }
    ],
    "current_user": {
        "user_id": None,
        "role": None
    },
    "metric_id_counter": 6,
    "record_id_counter": 5
}


class PersonalHealthRecordSystem:
    """
    Personal Health Record Management System API.
    
    A digital platform for maintaining and updating individual health information,
    including physiological measurements, medical history, and wellness data.
    Supports entry, modification, and retrieval of vital statistics with proper
    access control and data validation.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Personal Health Record Management System.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self.users: List[Dict[str, Any]] = []
        self.health_metrics: List[Dict[str, Any]] = []
        self.medical_history: List[Dict[str, Any]] = []
        self.current_user: Dict[str, Optional[str]] = {"user_id": None, "role": None}
        self.metric_id_counter: int = 1
        self.record_id_counter: int = 1
        
        self._api_description: str = (
            "Personal health record management system for maintaining physiological "
            "measurements, medical history, and wellness data with access control."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _get_date_from_timestamp(self, timestamp: str) -> str:
        """
        Extract date portion from an ISO timestamp.
        
        Args:
            timestamp: ISO format timestamp string.
            
        Returns:
            str: Date portion (YYYY-MM-DD).
        """
        return timestamp.split("T")[0]
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data.
            long_context: Flag for extended context loading (unused).
            
        Returns:
            None
        """
        if not scenario:
            scenario = {}
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Retrieve the current state of all environment variables.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - users: List of user profile dictionaries
                - health_metrics: List of health metric entries
                - medical_history: List of medical history records
                - current_user: Current session user info (user_id and role)
                - metric_id_counter: Counter for generating metric IDs
                - record_id_counter: Counter for generating record IDs
        """
        return {
            "users": deepcopy(self.users),
            "health_metrics": deepcopy(self.health_metrics),
            "medical_history": deepcopy(self.medical_history),
            "current_user": deepcopy(self.current_user),
            "metric_id_counter": self.metric_id_counter,
            "record_id_counter": self.record_id_counter
        }
    
    # ==================== Query Operations ====================
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user profile information using the unique user _id.
        
        Args:
            user_id: The unique identifier of the user to retrieve.
            
        Returns:
            Dict[str, Any]: User profile dictionary if found, or error dictionary.
        """
        for user in self.users:
            if user["_id"] == user_id:
                return {"user": deepcopy(user)}
        return {"error": f"User with id '{user_id}' not found"}
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get full personal details of the currently logged-in user.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Current user's profile dictionary or error if not logged in.
        """
        if not self.current_user["user_id"]:
            return {"error": "No user currently logged in"}
        
        return self.get_user_by_id(self.current_user["user_id"])
    
    def list_health_metrics_by_user(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve all health metric entries associated with a specific user.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of health metrics or error.
        """
        # Check if user exists
        user_result = self.get_user_by_id(user_id)
        if "error" in user_result:
            return user_result
        
        metrics = [
            deepcopy(m) for m in self.health_metrics 
            if m["user_id"] == user_id
        ]
        return {"metrics": metrics, "count": len(metrics)}
    
    def get_latest_metric_by_type(
        self, user_id: str, metric_type: str
    ) -> Dict[str, Any]:
        """
        Fetch the most recent value, unit, and timestamp for a given metric type.
        
        Args:
            user_id: The unique identifier of the user.
            metric_type: The type of metric (e.g., "weight", "heart_rate").
            
        Returns:
            Dict[str, Any]: Latest metric entry or error dictionary.
        """
        # Check if user exists
        user_result = self.get_user_by_id(user_id)
        if "error" in user_result:
            return user_result
        
        # Filter metrics by user and type
        user_metrics = [
            m for m in self.health_metrics
            if m["user_id"] == user_id and m["metric_type"] == metric_type
        ]
        
        if not user_metrics:
            return {
                "error": f"No '{metric_type}' metrics found for user '{user_id}'"
            }
        
        # Sort by timestamp descending and get the latest
        user_metrics.sort(key=lambda x: x["timestamp"], reverse=True)
        latest = user_metrics[0]
        
        return {
            "metric": deepcopy(latest),
            "value": latest["value"],
            "unit": latest["unit"],
            "timestamp": latest["timestamp"]
        }
    
    def get_metric_history_by_type(
        self, user_id: str, metric_type: str
    ) -> Dict[str, Any]:
        """
        Retrieve historical readings of a specific metric type over time.
        
        Args:
            user_id: The unique identifier of the user.
            metric_type: The type of metric to retrieve history for.
            
        Returns:
            Dict[str, Any]: Dictionary with list of historical metrics or error.
        """
        # Check if user exists
        user_result = self.get_user_by_id(user_id)
        if "error" in user_result:
            return user_result
        
        # Filter and sort metrics
        history = [
            deepcopy(m) for m in self.health_metrics
            if m["user_id"] == user_id and m["metric_type"] == metric_type
        ]
        history.sort(key=lambda x: x["timestamp"])
        
        return {"history": history, "count": len(history), "metric_type": metric_type}
    
    def validate_metric_unit(
        self, metric_type: str, unit: str
    ) -> Dict[str, Any]:
        """
        Check whether the provided unit is valid for the specified metric type.
        
        Args:
            metric_type: The type of metric (e.g., "weight").
            unit: The unit to validate (e.g., "kg").
            
        Returns:
            Dict[str, Any]: Validation result with valid flag and valid units list.
        """
        if metric_type not in VALID_METRIC_UNITS:
            return {
                "valid": False,
                "error": f"Unknown metric type '{metric_type}'",
                "known_types": list(VALID_METRIC_UNITS.keys())
            }
        
        valid_units = VALID_METRIC_UNITS[metric_type]
        is_valid = unit in valid_units
        
        return {
            "valid": is_valid,
            "metric_type": metric_type,
            "provided_unit": unit,
            "valid_units": valid_units
        }
    
    def list_medical_history(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve all medical conditions in a user's history.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: Dictionary with list of medical history records or error.
        """
        # Check if user exists
        user_result = self.get_user_by_id(user_id)
        if "error" in user_result:
            return user_result
        
        records = [
            deepcopy(r) for r in self.medical_history
            if r["user_id"] == user_id
        ]
        return {"medical_history": records, "count": len(records)}
    
    def get_active_medical_conditions(self, user_id: str) -> Dict[str, Any]:
        """
        List only the active (unresolved) medical conditions for a user.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: Dictionary with list of active conditions or error.
        """
        # Check if user exists
        user_result = self.get_user_by_id(user_id)
        if "error" in user_result:
            return user_result
        
        active = [
            deepcopy(r) for r in self.medical_history
            if r["user_id"] == user_id and r["status"] == "active"
        ]
        return {"active_conditions": active, "count": len(active)}
    
    def check_current_user_role(self) -> Dict[str, Any]:
        """
        Determine the role of the current session user for access control.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary with current user_id and role, or error.
        """
        if not self.current_user["user_id"]:
            return {"error": "No user currently logged in", "user_id": None, "role": None}
        
        return {
            "user_id": self.current_user["user_id"],
            "role": self.current_user["role"]
        }
    
    # ==================== State Change Operations ====================
    
    def set_current_user(
        self, user_id: str, role: str
    ) -> Dict[str, Any]:
        """
        Set the current session user to enforce access control during operations.
        
        Args:
            user_id: The unique identifier of the user to set as current.
            role: The role of the user ("patient" or "provider").
            
        Returns:
            Dict[str, Any]: Success confirmation or error dictionary.
        """
        # Validate role
        valid_roles = ["patient", "provider"]
        if role not in valid_roles:
            return {
                "error": f"Invalid role '{role}'. Must be one of: {valid_roles}"
            }
        
        # Check if user exists
        user_result = self.get_user_by_id(user_id)
        if "error" in user_result:
            return user_result
        
        self.current_user["user_id"] = user_id
        self.current_user["role"] = role
        
        return {
            "success": True,
            "message": f"Current user set to '{user_id}' with role '{role}'",
            "current_user": deepcopy(self.current_user)
        }
    
    def add_health_metric(
        self,
        user_id: str,
        metric_type: str,
        value: float,
        unit: str
    ) -> Dict[str, Any]:
        """
        Append a new physiological measurement to the user's record.
        
        Validates metric type and unit before adding. Users can only add metrics
        for themselves unless they have provider role.
        
        Args:
            user_id: The unique identifier of the user.
            metric_type: The type of metric (e.g., "weight", "heart_rate").
            value: The numeric value of the measurement.
            unit: The unit of measurement.
            
        Returns:
            Dict[str, Any]: Created metric entry or error dictionary.
        """
        # Check authorization
        if not self.current_user["user_id"]:
            return {"error": "No user currently logged in"}
        
        if (self.current_user["user_id"] != user_id and 
                self.current_user["role"] != "provider"):
            return {
                "error": "Unauthorized: Users can only add metrics for themselves "
                         "unless authorized by a healthcare provider role"
            }
        
        # Check if user exists
        user_result = self.get_user_by_id(user_id)
        if "error" in user_result:
            return user_result
        
        # Validate metric type and unit
        validation = self.validate_metric_unit(metric_type, unit)
        if not validation["valid"]:
            if "error" in validation:
                return {"error": validation["error"]}
            return {
                "error": f"Invalid unit '{unit}' for metric type '{metric_type}'. "
                         f"Valid units are: {validation['valid_units']}"
            }
        
        # Create new metric entry
        metric_id = f"metric_{self.metric_id_counter:03d}"
        self.metric_id_counter += 1
        
        new_metric = {
            "metric_id": metric_id,
            "user_id": user_id,
            "metric_type": metric_type,
            "value": value,
            "unit": unit,
            "timestamp": self._timestamp()
        }
        
        self.health_metrics.append(new_metric)
        
        return {
            "success": True,
            "message": "Health metric added successfully",
            "metric": deepcopy(new_metric)
        }
    
    def update_latest_metric(
        self,
        user_id: str,
        metric_type: str,
        new_value: float,
        new_unit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify the most recent health metric entry of the same type.
        
        Only allowed if recorded on the same day and user is authorized.
        
        Args:
            user_id: The unique identifier of the user.
            metric_type: The type of metric to update.
            new_value: The new value for the measurement.
            new_unit: Optional new unit (must be valid if provided).
            
        Returns:
            Dict[str, Any]: Updated metric entry or error dictionary.
        """
        # Check authorization
        if not self.current_user["user_id"]:
            return {"error": "No user currently logged in"}
        
        if (self.current_user["user_id"] != user_id and 
                self.current_user["role"] != "provider"):
            return {
                "error": "Unauthorized: Users can only update their own metrics "
                         "unless authorized by a healthcare provider role"
            }
        
        # Get latest metric
        latest_result = self.get_latest_metric_by_type(user_id, metric_type)
        if "error" in latest_result:
            return latest_result
        
        latest_metric = latest_result["metric"]
        
        # Check if recorded on the same day
        today = self._get_date_from_timestamp(self._timestamp())
        metric_date = self._get_date_from_timestamp(latest_metric["timestamp"])
        
        if metric_date != today:
            return {
                "error": f"Cannot update metric from '{metric_date}'. "
                         f"Updates are only allowed for entries recorded today ({today})"
            }
        
        # Validate new unit if provided
        unit_to_use = new_unit if new_unit else latest_metric["unit"]
        validation = self.validate_metric_unit(metric_type, unit_to_use)
        if not validation["valid"]:
            return {
                "error": f"Invalid unit '{unit_to_use}' for metric type '{metric_type}'. "
                         f"Valid units are: {validation['valid_units']}"
            }
        
        # Find and update the metric in the list
        for metric in self.health_metrics:
            if metric["metric_id"] == latest_metric["metric_id"]:
                metric["value"] = new_value
                metric["unit"] = unit_to_use
                metric["timestamp"] = self._timestamp()
                return {
                    "success": True,
                    "message": "Health metric updated successfully",
                    "metric": deepcopy(metric)
                }
        
        return {"error": "Failed to update metric - metric not found in storage"}
    
    def record_medical_condition(
        self,
        user_id: str,
        condition: str,
        diagnosis_date: str,
        notes: str = "",
        status: str = "active"
    ) -> Dict[str, Any]:
        """
        Add a new diagnosed condition to the user's medical history.
        
        Args:
            user_id: The unique identifier of the user.
            condition: Name/description of the medical condition.
            diagnosis_date: Date of diagnosis (YYYY-MM-DD format).
            notes: Additional notes about the condition.
            status: Initial status ("active" or "resolved").
            
        Returns:
            Dict[str, Any]: Created medical record or error dictionary.
        """
        # Check authorization
        if not self.current_user["user_id"]:
            return {"error": "No user currently logged in"}
        
        if (self.current_user["user_id"] != user_id and 
                self.current_user["role"] != "provider"):
            return {
                "error": "Unauthorized: Users can only record conditions for themselves "
                         "unless authorized by a healthcare provider role"
            }
        
        # Check if user exists
        user_result = self.get_user_by_id(user_id)
        if "error" in user_result:
            return user_result
        
        # Validate status
        valid_statuses = ["active", "resolved"]
        if status not in valid_statuses:
            return {
                "error": f"Invalid status '{status}'. Must be one of: {valid_statuses}"
            }
        
        # Create new medical history record
        record_id = f"mh_{self.record_id_counter:03d}"
        self.record_id_counter += 1
        
        new_record = {
            "record_id": record_id,
            "user_id": user_id,
            "condition": condition,
            "diagnosis_date": diagnosis_date,
            "notes": notes,
            "status": status
        }
        
        self.medical_history.append(new_record)
        
        return {
            "success": True,
            "message": "Medical condition recorded successfully",
            "record": deepcopy(new_record)
        }
    
    def resolve_medical_condition(self, record_id: str) -> Dict[str, Any]:
        """
        Update the status of a diagnosed condition from "active" to "resolved".
        
        Args:
            record_id: The unique identifier of the medical history record.
            
        Returns:
            Dict[str, Any]: Updated record or error dictionary.
        """
        # Check authorization
        if not self.current_user["user_id"]:
            return {"error": "No user currently logged in"}
        
        # Find the record
        target_record = None
        for record in self.medical_history:
            if record["record_id"] == record_id:
                target_record = record
                break
        
        if not target_record:
            return {"error": f"Medical record with id '{record_id}' not found"}
        
        # Check user authorization
        if (self.current_user["user_id"] != target_record["user_id"] and 
                self.current_user["role"] != "provider"):
            return {
                "error": "Unauthorized: Users can only resolve their own conditions "
                         "unless authorized by a healthcare provider role"
            }
        
        # Check if already resolved
        if target_record["status"] == "resolved":
            return {
                "error": f"Medical condition '{record_id}' is already resolved"
            }
        
        # Update status
        target_record["status"] = "resolved"
        
        return {
            "success": True,
            "message": "Medical condition resolved successfully",
            "record": deepcopy(target_record)
        }
    
    def remove_health_metric(self, metric_id: str) -> Dict[str, Any]:
        """
        Delete a specific health metric entry.
        
        Subject to access and immutability policies - only allowed for providers
        or for error correction purposes.
        
        Args:
            metric_id: The unique identifier of the metric to remove.
            
        Returns:
            Dict[str, Any]: Success confirmation or error dictionary.
        """
        # Check authorization - only providers can remove metrics
        if not self.current_user["user_id"]:
            return {"error": "No user currently logged in"}
        
        # Find the metric
        target_metric = None
        target_index = None
        for i, metric in enumerate(self.health_metrics):
            if metric["metric_id"] == metric_id:
                target_metric = metric
                target_index = i
                break
        
        if target_metric is None:
            return {"error": f"Health metric with id '{metric_id}' not found"}
        
        # Only providers can remove metrics, or users can remove their own
        # same-day entries for error correction
        is_provider = self.current_user["role"] == "provider"
        is_own_metric = self.current_user["user_id"] == target_metric["user_id"]
        
        today = self._get_date_from_timestamp(self._timestamp())
        metric_date = self._get_date_from_timestamp(target_metric["timestamp"])
        is_same_day = metric_date == today
        
        if not is_provider and not (is_own_metric and is_same_day):
            return {
                "error": "Unauthorized: Only providers can remove metrics, or users "
                         "can remove their own same-day entries for error correction"
            }
        
        # Remove the metric
        removed_metric = self.health_metrics.pop(target_index)
        
        return {
            "success": True,
            "message": "Health metric removed successfully",
            "removed_metric": deepcopy(removed_metric)
        }


__TEST_CASES__ = [
    {
        "name": "Complete user login and health metric workflow",
        "steps": [
            {"tool_call": "set_current_user(user_id='user_001', role='patient')", "expect_success": True},
            {"tool_call": "get_user_profile()", "expect_success": True},
            {"tool_call": "add_health_metric(user_id='user_001', metric_type='weight', value=66.0, unit='kg')", "expect_success": True},
            {"tool_call": "get_latest_metric_by_type(user_id='user_001', metric_type='weight')", "expect_success": True},
            {"tool_call": "list_health_metrics_by_user(user_id='user_001')", "expect_success": True}
        ]
    },
    {
        "name": "Provider managing patient records",
        "steps": [
            {"tool_call": "set_current_user(user_id='user_002', role='provider')", "expect_success": True},
            {"tool_call": "add_health_metric(user_id='user_001', metric_type='heart_rate', value=75, unit='bpm')", "expect_success": True},
            {"tool_call": "record_medical_condition(user_id='user_001', condition='Migraine', diagnosis_date='2024-01-20', notes='Recurring headaches', status='active')", "expect_success": True},
            {"tool_call": "get_active_medical_conditions(user_id='user_001')", "expect_success": True}
        ]
    },
    {
        "name": "Medical history and condition resolution",
        "steps": [
            {"tool_call": "set_current_user(user_id='user_001', role='patient')", "expect_success": True},
            {"tool_call": "list_medical_history(user_id='user_001')", "expect_success": True},
            {"tool_call": "resolve_medical_condition(record_id='mh_002')", "expect_success": True},
            {"tool_call": "get_active_medical_conditions(user_id='user_001')", "expect_success": True}
        ]
    },
    {
        "name": "Unauthorized access attempt - error path",
        "steps": [
            {"tool_call": "set_current_user(user_id='user_003', role='patient')", "expect_success": True},
            {"tool_call": "add_health_metric(user_id='user_001', metric_type='weight', value=70.0, unit='kg')", "expect_success": False},
            {"tool_call": "resolve_medical_condition(record_id='mh_001')", "expect_success": False}
        ]
    },
    {
        "name": "Invalid metric unit validation - error path",
        "steps": [
            {"tool_call": "set_current_user(user_id='user_001', role='patient')", "expect_success": True},
            {"tool_call": "validate_metric_unit(metric_type='weight', unit='meters')", "expect_success": True},
            {"tool_call": "add_health_metric(user_id='user_001', metric_type='weight', value=65.0, unit='meters')", "expect_success": False},
            {"tool_call": "get_user_by_id(user_id='user_999')", "expect_success": False}
        ]
    }
]