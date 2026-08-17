"""
IoT Sensor Data Platform Environment API

This module provides a complete environment API for an IoT sensor data platform
that collects, stores, and manages time-series data from distributed sensors.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Default state with initial sample data
DEFAULT_STATE: Dict[str, Any] = {
    # Sensor readings - time-series data from devices
    "sensor_readings": [
        {
            "reading_id": "reading_001",
            "device_id": "device_001",
            "timestamp": "2024-01-15T10:30:00",
            "sensor_type": "temperature",
            "value": 23.5
        },
        {
            "reading_id": "reading_002",
            "device_id": "device_001",
            "timestamp": "2024-01-15T10:35:00",
            "sensor_type": "humidity",
            "value": 65.2
        },
        {
            "reading_id": "reading_003",
            "device_id": "device_002",
            "timestamp": "2024-01-15T10:32:00",
            "sensor_type": "temperature",
            "value": 21.8
        },
        {
            "reading_id": "reading_004",
            "device_id": "device_002",
            "timestamp": "2024-01-15T10:40:00",
            "sensor_type": "pressure",
            "value": 1013.25
        },
        {
            "reading_id": "reading_005",
            "device_id": "device_003",
            "timestamp": "2024-01-15T10:28:00",
            "sensor_type": "humidity",
            "value": 58.7
        }
    ],
    
    # Registered devices
    "devices": [
        {
            "device_id": "device_001",
            "location": "Building A - Floor 1",
            "device_type": "multi_sensor",
            "registration_status": "active"
        },
        {
            "device_id": "device_002",
            "location": "Building A - Floor 2",
            "device_type": "weather_station",
            "registration_status": "active"
        },
        {
            "device_id": "device_003",
            "location": "Building B - Basement",
            "device_type": "humidity_sensor",
            "registration_status": "active"
        },
        {
            "device_id": "device_004",
            "location": "Building C - Roof",
            "device_type": "solar_monitor",
            "registration_status": "inactive"
        }
    ],
    
    # Supported sensor types
    "sensor_types": [
        {
            "sensor_type": "temperature",
            "unit_of_measurement": "°C",
            "description": "Measures ambient temperature in Celsius"
        },
        {
            "sensor_type": "humidity",
            "unit_of_measurement": "%",
            "description": "Measures relative humidity percentage"
        },
        {
            "sensor_type": "pressure",
            "unit_of_measurement": "hPa",
            "description": "Measures atmospheric pressure in hectopascals"
        }
    ],
    
    # Counter for generating unique reading IDs
    "reading_counter": 6,
    
    # Data retention period in days
    "retention_days": 30,
    
    # Current simulated time for the environment
    "current_time": "2024-01-15T12:00:00"
}


class IoTSensorDataPlatform:
    """
    IoT Sensor Data Platform Environment API.
    
    This class provides a complete API for managing an IoT sensor data platform
    that collects, stores, and manages time-series data from distributed sensors.
    It supports device registration, sensor type management, data ingestion,
    and flexible querying capabilities.
    """
    
    def __init__(self) -> None:
        """
        Initialize the IoT Sensor Data Platform environment.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self.sensor_readings: List[Dict[str, Any]] = []
        self.devices: List[Dict[str, Any]] = []
        self.sensor_types: List[Dict[str, Any]] = []
        self.reading_counter: int = 1
        self.retention_days: int = 30
        self.current_time: str = ""
        
        self._api_description: str = (
            "IoT Sensor Data Platform API for collecting, storing, and managing "
            "time-series data from distributed sensors with support for device "
            "registration, sensor type management, and flexible querying."
        )
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values. If a key is missing,
                     falls back to DEFAULT_STATE values.
            long_context: Flag for long context scenarios (reserved for future use).
            
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
        Get the current state of the environment.
        
        Returns a dictionary containing all internal state variables of the
        IoT Sensor Data Platform, including sensor readings, devices,
        sensor types, and configuration settings.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary with the following keys:
                - sensor_readings: List of all sensor reading records
                - devices: List of all registered device records
                - sensor_types: List of all supported sensor type definitions
                - reading_counter: Current counter for generating reading IDs
                - retention_days: Data retention period in days
                - current_time: Current simulated time in ISO format
        """
        return {
            "sensor_readings": deepcopy(self.sensor_readings),
            "devices": deepcopy(self.devices),
            "sensor_types": deepcopy(self.sensor_types),
            "reading_counter": self.reading_counter,
            "retention_days": self.retention_days,
            "current_time": self.current_time
        }
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp for the environment.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string based on current_time.
        """
        return self.current_time
    
    def _is_device_registered(self, device_id: str) -> bool:
        """
        Check if a device is registered and active.
        
        Args:
            device_id: The device identifier to check.
            
        Returns:
            bool: True if device exists and is active, False otherwise.
        """
        for device in self.devices:
            if device["device_id"] == device_id:
                return device["registration_status"] == "active"
        return False
    
    def _is_sensor_type_registered(self, sensor_type: str) -> bool:
        """
        Check if a sensor type is registered in the system.
        
        Args:
            sensor_type: The sensor type identifier to check.
            
        Returns:
            bool: True if sensor type exists, False otherwise.
        """
        return any(st["sensor_type"] == sensor_type for st in self.sensor_types)
    
    def _is_valid_timestamp(self, timestamp: str) -> bool:
        """
        Validate that a timestamp is within acceptable range.
        
        Args:
            timestamp: ISO format timestamp string to validate.
            
        Returns:
            bool: True if timestamp is valid, False otherwise.
        """
        try:
            ts = datetime.fromisoformat(timestamp)
            current = datetime.fromisoformat(self.current_time)
            # Timestamp should not be more than 1 day in the future
            max_future = current + timedelta(days=1)
            return ts <= max_future
        except (ValueError, TypeError):
            return False
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_sensor_readings_by_device(self, device_id: str) -> Dict[str, Any]:
        """
        Retrieve all sensor readings associated with a specific device.
        
        Args:
            device_id: The unique identifier of the device to query readings for.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - readings: List of sensor reading records for the device
                - count: Number of readings found
                - device_id: The queried device ID
                Or {"error": "..."} if the device is not found.
        """
        device_exists = any(d["device_id"] == device_id for d in self.devices)
        if not device_exists:
            return {"error": f"Device '{device_id}' not found in the system"}
        
        readings = [r for r in self.sensor_readings if r["device_id"] == device_id]
        return {
            "readings": deepcopy(readings),
            "count": len(readings),
            "device_id": device_id
        }
        
    def get_device_readings(self, device_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve readings for a specific device, optionally limiting the count.
        
        Args:
            device_id: The unique identifier of the device.
            limit: Maximum number of recent readings to return.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if successful
                - device_id: The device ID
                - readings: List of reading records
                - count: Number of returned readings
                Or {"error": "..."} if device not found.
        """
        result = self.get_sensor_readings_by_device(device_id)
        if "error" in result:
            return result
        
        readings = result["readings"]
        if limit is not None and limit > 0:
            readings = readings[-limit:]
            
        return {
            "success": True,
            "device_id": device_id,
            "readings": readings,
            "count": len(readings)
        }
    
    def get_sensor_readings_by_time_range(
        self, 
        start_time: str, 
        end_time: str
    ) -> Dict[str, Any]:
        """
        Retrieve all sensor readings within a specified time range.
        
        Args:
            start_time: ISO format timestamp for the start of the range (inclusive).
            end_time: ISO format timestamp for the end of the range (inclusive).
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - readings: List of sensor readings within the time range
                - count: Number of readings found
                - start_time: Query start time
                - end_time: Query end time
                Or {"error": "..."} if timestamps are invalid.
        """
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
        except (ValueError, TypeError):
            return {"error": "Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}
        
        if start_dt > end_dt:
            return {"error": "start_time must be before or equal to end_time"}
        
        readings = []
        for r in self.sensor_readings:
            try:
                r_ts = datetime.fromisoformat(r["timestamp"])
                if start_dt <= r_ts <= end_dt:
                    readings.append(r)
            except (ValueError, TypeError):
                continue
        
        return {
            "readings": deepcopy(readings),
            "count": len(readings),
            "start_time": start_time,
            "end_time": end_time
        }
    
    def get_sensor_readings_by_sensor_type(self, sensor_type: str) -> Dict[str, Any]:
        """
        Retrieve all readings for a specific sensor type.
        
        Args:
            sensor_type: The type of sensor to query (e.g., 'temperature', 'humidity').
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - readings: List of sensor readings for the specified type
                - count: Number of readings found
                - sensor_type: The queried sensor type
                Or {"error": "..."} if sensor type is not registered.
        """
        if not self._is_sensor_type_registered(sensor_type):
            return {"error": f"Sensor type '{sensor_type}' is not registered in the system"}
        
        readings = [r for r in self.sensor_readings if r["sensor_type"] == sensor_type]
        return {
            "readings": deepcopy(readings),
            "count": len(readings),
            "sensor_type": sensor_type
        }
    
    def get_sensor_readings_filtered(
        self,
        device_id: Optional[str] = None,
        sensor_types: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve readings filtered by device, sensor type(s), and time range.
        
        Args:
            device_id: Optional device ID to filter by.
            sensor_types: Optional list of sensor types to filter by.
            start_time: Optional ISO format start timestamp for time range.
            end_time: Optional ISO format end timestamp for time range.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - readings: List of filtered sensor readings
                - count: Number of readings found
                - filters_applied: Dictionary of filters that were applied
                Or {"error": "..."} if validation fails.
        """
        readings = deepcopy(self.sensor_readings)
        filters_applied = {}
        
        if device_id is not None:
            device_exists = any(d["device_id"] == device_id for d in self.devices)
            if not device_exists:
                return {"error": f"Device '{device_id}' not found in the system"}
            readings = [r for r in readings if r["device_id"] == device_id]
            filters_applied["device_id"] = device_id
        
        if sensor_types is not None:
            for st in sensor_types:
                if not self._is_sensor_type_registered(st):
                    return {"error": f"Sensor type '{st}' is not registered"}
            readings = [r for r in readings if r["sensor_type"] in sensor_types]
            filters_applied["sensor_types"] = sensor_types
        
        if start_time is not None or end_time is not None:
            try:
                start_dt = datetime.fromisoformat(start_time) if start_time else None
                end_dt = datetime.fromisoformat(end_time) if end_time else None
            except (ValueError, TypeError):
                return {"error": "Invalid timestamp format. Use ISO format"}
            
            if start_dt and end_dt and start_dt > end_dt:
                return {"error": "start_time must be before or equal to end_time"}
            
            filtered = []
            for r in readings:
                try:
                    r_ts = datetime.fromisoformat(r["timestamp"])
                    if start_dt and r_ts < start_dt:
                        continue
                    if end_dt and r_ts > end_dt:
                        continue
                    filtered.append(r)
                except (ValueError, TypeError):
                    continue
            readings = filtered
            
            if start_time:
                filters_applied["start_time"] = start_time
            if end_time:
                filters_applied["end_time"] = end_time
        
        return {
            "readings": readings,
            "count": len(readings),
            "filters_applied": filters_applied
        }
    
    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """
        Retrieve metadata for a given device.
        
        Args:
            device_id: The unique identifier of the device to query.
            
        Returns:
            Dict[str, Any]: A dictionary containing device metadata:
                - device_id: Device identifier
                - location: Physical location of the device
                - device_type: Type of device
                - registration_status: Current registration status
                Or {"error": "..."} if device is not found.
        """
        for device in self.devices:
            if device["device_id"] == device_id:
                return deepcopy(device)
        return {"error": f"Device '{device_id}' not found in the system"}
    
    def list_registered_devices(self) -> Dict[str, Any]:
        """
        Return a list of all registered devices in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - devices: List of all device records
                - count: Total number of devices
                - active_count: Number of active devices
        """
        active_count = sum(1 for d in self.devices if d["registration_status"] == "active")
        return {
            "devices": deepcopy(self.devices),
            "count": len(self.devices),
            "active_count": active_count
        }
    
    def list_supported_sensor_types(self) -> Dict[str, Any]:
        """
        Return a list of all sensor types registered in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - sensor_types: List of all sensor type definitions
                - count: Total number of sensor types
        """
        return {
            "sensor_types": deepcopy(self.sensor_types),
            "count": len(self.sensor_types)
        }
    
    def get_sensor_type_info(self, sensor_type: str) -> Dict[str, Any]:
        """
        Retrieve metadata for a given sensor type.
        
        Args:
            sensor_type: The sensor type identifier to query.
            
        Returns:
            Dict[str, Any]: A dictionary containing sensor type metadata:
                - sensor_type: Sensor type identifier
                - unit_of_measurement: Unit used for measurements
                - description: Description of the sensor type
                Or {"error": "..."} if sensor type is not found.
        """
        for st in self.sensor_types:
            if st["sensor_type"] == sensor_type:
                return deepcopy(st)
        return {"error": f"Sensor type '{sensor_type}' not registered in the system"}
    
    def check_device_registration_status(self, device_id: str) -> Dict[str, Any]:
        """
        Check whether a device is registered in the system.
        
        Args:
            device_id: The device identifier to check.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - device_id: The queried device ID
                - is_registered: Boolean indicating if device exists
                - registration_status: Current status if registered, None otherwise
        """
        for device in self.devices:
            if device["device_id"] == device_id:
                return {
                    "device_id": device_id,
                    "is_registered": True,
                    "registration_status": device["registration_status"]
                }
        return {
            "device_id": device_id,
            "is_registered": False,
            "registration_status": None
        }
    
    def check_sensor_type_registered(self, sensor_type: str) -> Dict[str, Any]:
        """
        Verify whether a sensor type is defined in the system.
        
        Args:
            sensor_type: The sensor type identifier to check.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - sensor_type: The queried sensor type
                - is_registered: Boolean indicating if sensor type exists
        """
        is_registered = self._is_sensor_type_registered(sensor_type)
        return {
            "sensor_type": sensor_type,
            "is_registered": is_registered
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def record_sensor_reading(
        self,
        device_id: str,
        value: float,
        unit: str,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a new sensor reading. Compatibility wrapper for ingest_sensor_reading.
        
        Args:
            device_id: The ID of the device.
            value: The numeric value of the reading.
            unit: The unit or sensor type for the reading.
            timestamp: Optional ISO format timestamp.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if successful
                - reading_id: The ID of the new reading
                - timestamp: The timestamp of the reading
                Or {"error": "..."} if validation fails.
        """
        if timestamp is None:
            timestamp = self._timestamp()
            
        sensor_type = unit
        for st in self.sensor_types:
            if st.get("unit_of_measurement") == unit or st.get("sensor_type") == unit:
                sensor_type = st["sensor_type"]
                break
                
        result = self.ingest_sensor_reading(device_id, sensor_type, value, timestamp)
        if "error" in result:
            return result
            
        return {
            "success": True,
            "reading_id": result["reading_id"],
            "timestamp": result["reading"]["timestamp"]
        }
        
    def ingest_sensor_reading(
        self,
        device_id: str,
        sensor_type: str,
        value: float,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new sensor reading to the system.
        
        Validates device_id, sensor_type, and timestamp before ingestion.
        
        Args:
            device_id: The ID of the device that produced the reading.
            sensor_type: The type of sensor measurement.
            value: The numeric value of the reading.
            timestamp: Optional ISO format timestamp. Uses current time if not provided.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if ingestion was successful
                - reading_id: The ID assigned to the new reading
                - reading: The complete reading record
                Or {"error": "..."} if validation fails.
        """
        if not self._is_device_registered(device_id):
            return {"error": f"Device '{device_id}' is not registered or not active"}
        
        if not self._is_sensor_type_registered(sensor_type):
            return {"error": f"Sensor type '{sensor_type}' is not registered"}
        
        if timestamp is None:
            timestamp = self._timestamp()
        
        if not self._is_valid_timestamp(timestamp):
            return {"error": f"Invalid timestamp '{timestamp}'. Must be valid and not in far future"}
        
        reading_id = f"reading_{self.reading_counter:03d}"
        reading = {
            "reading_id": reading_id,
            "device_id": device_id,
            "timestamp": timestamp,
            "sensor_type": sensor_type,
            "value": value
        }
        
        self.sensor_readings.append(reading)
        self.reading_counter += 1
        
        return {
            "success": True,
            "reading_id": reading_id,
            "reading": deepcopy(reading)
        }
    
    def register_device(
        self,
        device_id: str,
        device_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        registration_status: str = "active"
    ) -> Dict[str, Any]:
        """
        Register a new physical device in the system.
        
        Args:
            device_id: Unique identifier for the new device.
            device_type: Type/model of the device.
            metadata: Optional dictionary of additional metadata (e.g. location).
            registration_status: Initial status (default: 'active').
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if registration was successful
                - device_id: The identifier of the device
                - message: Success message
                - device: The complete device record
                Or {"error": "..."} if device already exists.
        """
        if not device_id or not str(device_id).strip():
            return {"error": "Invalid or missing device ID"}
            
        device_id = device_id.strip()
        
        if any(d["device_id"] == device_id for d in self.devices):
            return {"error": f"Device '{device_id}' already exists in the system"}
        
        valid_statuses = ["active", "inactive", "maintenance"]
        if registration_status not in valid_statuses:
            return {"error": f"Invalid status. Must be one of: {valid_statuses}"}
        
        location = metadata.get("location", "Unknown") if metadata else "Unknown"
        
        device = {
            "device_id": device_id,
            "location": location,
            "device_type": device_type,
            "registration_status": registration_status,
            "metadata": metadata or {}
        }
        
        self.devices.append(device)
        
        return {
            "success": True,
            "device_id": device_id,
            "message": "Device registered successfully",
            "device": deepcopy(device)
        }
    
    def register_sensor_type(
        self,
        sensor_type: str,
        unit_of_measurement: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Add a new sensor type to the system.
        
        Args:
            sensor_type: Unique identifier for the sensor type.
            unit_of_measurement: Unit used for measurements (e.g., '°C', '%').
            description: Human-readable description of what the sensor measures.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if registration was successful
                - sensor_type_record: The complete sensor type record
                Or {"error": "..."} if sensor type already exists.
        """
        if self._is_sensor_type_registered(sensor_type):
            return {"error": f"Sensor type '{sensor_type}' already exists"}
        
        sensor_type_record = {
            "sensor_type": sensor_type,
            "unit_of_measurement": unit_of_measurement,
            "description": description
        }
        
        self.sensor_types.append(sensor_type_record)
        
        return {
            "success": True,
            "sensor_type_record": deepcopy(sensor_type_record)
        }
    
    def update_device_location(
        self,
        device_id: str,
        new_location: str
    ) -> Dict[str, Any]:
        """
        Update the physical location of a registered device.
        
        Args:
            device_id: The ID of the device to update.
            new_location: The new location string.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if update was successful
                - device_id: The updated device ID
                - old_location: Previous location
                - new_location: Updated location
                Or {"error": "..."} if device is not found.
        """
        for device in self.devices:
            if device["device_id"] == device_id:
                old_location = device.get("location", "")
                device["location"] = new_location
                if "metadata" in device:
                    device["metadata"]["location"] = new_location
                else:
                    device["metadata"] = {"location": new_location}
                return {
                    "success": True,
                    "device_id": device_id,
                    "old_location": old_location,
                    "new_location": new_location
                }
        
        return {"error": f"Device '{device_id}' not found in the system"}
    
    def deregister_device(self, device_id: str) -> Dict[str, Any]:
        """
        Mark a device as unregistered or decommissioned.
        
        Args:
            device_id: The ID of the device to deregister.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if deregistration was successful
                - device_id: The deregistered device ID
                - message: Success message
                - previous_status: Status before deregistration
                Or {"error": "..."} if device is not found.
        """
        for device in self.devices:
            if device["device_id"] == device_id:
                previous_status = device["registration_status"]
                if previous_status == "inactive":
                    return {"error": f"Device '{device_id}' is already inactive"}
                device["registration_status"] = "inactive"
                return {
                    "success": True,
                    "device_id": device_id,
                    "message": "Device deregistered successfully",
                    "previous_status": previous_status
                }
        
        return {"error": f"Device '{device_id}' not found in the system"}
    
    def remove_sensor_type(self, sensor_type: str) -> Dict[str, Any]:
        """
        Remove a sensor type from the system.
        
        Only succeeds if no readings depend on this sensor type.
        
        Args:
            sensor_type: The sensor type identifier to remove.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if removal was successful
                - sensor_type: The removed sensor type
                Or {"error": "..."} if sensor type has dependent readings or not found.
        """
        if not self._is_sensor_type_registered(sensor_type):
            return {"error": f"Sensor type '{sensor_type}' not found in the system"}
        
        dependent_readings = [r for r in self.sensor_readings if r["sensor_type"] == sensor_type]
        if dependent_readings:
            return {
                "error": f"Cannot remove sensor type '{sensor_type}': "
                        f"{len(dependent_readings)} readings depend on it"
            }
        
        self.sensor_types = [st for st in self.sensor_types if st["sensor_type"] != sensor_type]
        
        return {
            "success": True,
            "sensor_type": sensor_type
        }
    
    def batch_ingest_readings(
        self,
        readings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Ingest multiple sensor readings at once.
        
        Validates each reading against constraints before ingestion.
        
        Args:
            readings: List of reading dictionaries, each containing:
                - device_id: Device identifier
                - sensor_type: Type of sensor
                - value: Numeric measurement value
                - timestamp: Optional ISO format timestamp
                
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if all readings were ingested
                - ingested_count: Number of successfully ingested readings
                - ingested_readings: List of ingested reading records
                - errors: List of error messages for failed readings
        """
        if not readings:
            return {"error": "No readings provided for batch ingestion"}
        
        ingested = []
        errors = []
        
        for i, reading_data in enumerate(readings):
            device_id = reading_data.get("device_id")
            sensor_type = reading_data.get("sensor_type")
            value = reading_data.get("value")
            timestamp = reading_data.get("timestamp")
            
            if not device_id or not sensor_type or value is None:
                errors.append(f"Reading {i}: Missing required fields")
                continue
            
            if not self._is_device_registered(device_id):
                errors.append(f"Reading {i}: Device '{device_id}' not registered/active")
                continue
            
            if not self._is_sensor_type_registered(sensor_type):
                errors.append(f"Reading {i}: Sensor type '{sensor_type}' not registered")
                continue
            
            if timestamp is None:
                timestamp = self._timestamp()
            elif not self._is_valid_timestamp(timestamp):
                errors.append(f"Reading {i}: Invalid timestamp '{timestamp}'")
                continue
            
            reading_id = f"reading_{self.reading_counter:03d}"
            reading = {
                "reading_id": reading_id,
                "device_id": device_id,
                "timestamp": timestamp,
                "sensor_type": sensor_type,
                "value": value
            }
            
            self.sensor_readings.append(reading)
            self.reading_counter += 1
            ingested.append(deepcopy(reading))
        
        return {
            "success": len(errors) == 0,
            "ingested_count": len(ingested),
            "ingested_readings": ingested,
            "errors": errors
        }
        
    def cleanup_old_readings(self, days_to_keep: int) -> Dict[str, Any]:
        """
        Remove sensor readings older than a specified number of days.
        
        Args:
            days_to_keep: Number of days of data to retain.
            
        Returns:
            Dict[str, Any]: A dictionary containing cleanup statistics
                or {"error": "..."} if invalid.
        """
        return self.clear_expired_readings(retention_days=days_to_keep)
    
    def clear_expired_readings(
        self,
        retention_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Remove sensor readings older than a retention period.
        
        Args:
            retention_days: Number of days to retain data. Uses system default if not provided.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if cleanup completed
                - removed_count: Number of readings removed
                - retained_count: Number of readings retained
                - cutoff_time: Timestamp used as the retention cutoff
        """
        if retention_days is None:
            retention_days = self.retention_days
        
        if retention_days < 0:
            return {"error": "retention_days must be a non-negative integer"}
        
        try:
            current = datetime.fromisoformat(self.current_time)
            cutoff = current - timedelta(days=retention_days)
            cutoff_str = cutoff.isoformat()
        except (ValueError, TypeError):
            return {"error": "Invalid current_time in system state"}
        
        original_count = len(self.sensor_readings)
        retained = []
        
        for reading in self.sensor_readings:
            try:
                r_ts = datetime.fromisoformat(reading["timestamp"])
                if r_ts >= cutoff:
                    retained.append(reading)
            except (ValueError, TypeError):
                retained.append(reading)
        
        self.sensor_readings = retained
        removed_count = original_count - len(retained)
        
        return {
            "success": True,
            "removed_count": removed_count,
            "retained_count": len(retained),
            "cutoff_time": cutoff_str
        }
    
    def reactivate_device(self, device_id: str) -> Dict[str, Any]:
        """
        Reactivate a previously deregistered or inactive device.
        
        Args:
            device_id: The unique identifier of the device to reactivate
            
        Returns:
            Dict[str, Any]: Dictionary containing reactivation status and device info
                or {"error": "..."} on failure.
        """
        if not device_id or not isinstance(device_id, str):
            return {"error": "Invalid device ID"}
        
        device_id = device_id.strip()
        
        for device in self.devices:
            if device["device_id"] == device_id:
                if device["registration_status"] == "active":
                    return {"error": "Device is already active"}
                
                device["registration_status"] = "active"
                device["reactivated_at"] = self._timestamp()
                
                return {
                    "success": True,
                    "device_id": device_id,
                    "message": "Device reactivated successfully",
                    "device_info": deepcopy(device)
                }
        
        return {"error": "Device not found"}
    
    def get_device_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about all registered devices.
        
        Args:
            None
            
        Returns:
            Dict[str, Any]: Dictionary containing device statistics.
        """
        total_active_devices = sum(1 for d in self.devices if d["registration_status"] == "active")
        total_inactive_devices = len(self.devices) - total_active_devices
        
        device_types = {}
        for device in self.devices:
            d_type = device.get("device_type", "unknown")
            device_types[d_type] = device_types.get(d_type, 0) + 1
        
        readings_per_device = {}
        for reading in self.sensor_readings:
            d_id = reading.get("device_id", "unknown")
            readings_per_device[d_id] = readings_per_device.get(d_id, 0) + 1
        
        return {
            "success": True,
            "total_active_devices": total_active_devices,
            "total_inactive_devices": total_inactive_devices,
            "device_types": device_types,
            "total_readings": len(self.sensor_readings),
            "readings_per_device": readings_per_device
        }
    
    def export_device_data(self, device_id: str, format_type: str = "json") -> Dict[str, Any]:
        """
        Export all data for a specific device.
        
        Args:
            device_id: The unique identifier of the device
            format_type: Export format ('json' or 'summary')
            
        Returns:
            Dict[str, Any]: Dictionary containing exported data or error
        """
        if not device_id or not isinstance(device_id, str):
            return {"error": "Invalid device ID"}
        
        device_id = device_id.strip()
        
        device_info = None
        for device in self.devices:
            if device["device_id"] == device_id:
                device_info = device
                break
                
        if not device_info:
            return {"error": "Device not found"}
        
        device_readings = [r for r in self.sensor_readings if r.get("device_id") == device_id]
        
        if format_type == "json":
            return {
                "success": True,
                "device_id": device_id,
                "device_info": deepcopy(device_info),
                "readings": deepcopy(device_readings),
                "reading_count": len(device_readings)
            }
        elif format_type == "summary":
            return {
                "success": True,
                "device_id": device_id,
                "device_type": device_info.get("device_type", "unknown"),
                "status": device_info.get("registration_status", "unknown"),
                "total_readings": len(device_readings),
                "registered_at": device_info.get("reactivated_at", "unknown")
            }
        else:
            return {"error": f"Unsupported format: {format_type}"}


__TEST_CASES__ = [
    {
        "method_name": "register_device",
        "input": {
            "device_id": "sensor_001",
            "device_type": "temperature",
            "metadata": {"location": "room_1"}
        },
        "expected_keys": ["success", "device_id", "message", "device"]
    },
    {
        "method_name": "register_device",
        "input": {
            "device_id": "",
            "device_type": "temperature"
        },
        "expected_keys": ["error"]
    },
    {
        "method_name": "record_sensor_reading",
        "input": {
            "device_id": "device_001",
            "value": 25.5,
            "unit": "temperature"
        },
        "expected_keys": ["success", "reading_id", "timestamp"]
    },
    {
        "method_name": "reactivate_device",
        "input": {
            "device_id": "device_004"
        },
        "expected_keys": ["success", "device_id", "message", "device_info"]
    },
    {
        "method_name": "export_device_data",
        "input": {
            "device_id": "device_001",
            "format_type": "xml"
        },
        "expected_keys": ["error"]
    }
]