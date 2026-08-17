"""
Network Monitoring System Environment API

A network monitoring system that continuously collects and analyzes data from network devices
to ensure service availability and performance. Supports anomaly detection, incident correlation,
and root cause analysis.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    "current_user": "admin",
    "session_id": "session_001",
    
    "network_devices": [
        {
            "device_id": "dev_001",
            "device_type": "router",
            "hostname": "core-router-01",
            "ip_address": "192.168.1.1",
            "status": "up",
            "last_seen": "2024-01-15T10:30:00"
        },
        {
            "device_id": "dev_002",
            "device_type": "switch",
            "hostname": "access-switch-01",
            "ip_address": "192.168.1.10",
            "status": "up",
            "last_seen": "2024-01-15T10:29:00"
        },
        {
            "device_id": "dev_003",
            "device_type": "server",
            "hostname": "web-server-01",
            "ip_address": "192.168.1.100",
            "status": "up",
            "last_seen": "2024-01-15T10:28:00"
        },
        {
            "device_id": "dev_004",
            "device_type": "firewall",
            "hostname": "edge-firewall-01",
            "ip_address": "192.168.1.254",
            "status": "maintenance",
            "last_seen": "2024-01-15T09:00:00"
        },
        {
            "device_id": "dev_005",
            "device_type": "router",
            "hostname": "branch-router-01",
            "ip_address": "192.168.2.1",
            "status": "down",
            "last_seen": "2024-01-15T08:45:00"
        }
    ],
    
    "performance_metrics": [
        {
            "metric_id": "met_001",
            "device_id": "dev_001",
            "timestamp": "2024-01-15T10:00:00",
            "cpu_usage": 45.5,
            "memory_usage": 62.3,
            "bandwidth_utilization": 78.0,
            "packet_loss": 0.1
        },
        {
            "metric_id": "met_002",
            "device_id": "dev_002",
            "timestamp": "2024-01-15T10:00:00",
            "cpu_usage": 30.2,
            "memory_usage": 45.0,
            "bandwidth_utilization": 55.0,
            "packet_loss": 0.0
        },
        {
            "metric_id": "met_003",
            "device_id": "dev_003",
            "timestamp": "2024-01-15T10:00:00",
            "cpu_usage": 92.5,
            "memory_usage": 88.0,
            "bandwidth_utilization": 40.0,
            "packet_loss": 0.5
        },
        {
            "metric_id": "met_004",
            "device_id": "dev_001",
            "timestamp": "2024-01-15T10:05:00",
            "cpu_usage": 48.0,
            "memory_usage": 63.5,
            "bandwidth_utilization": 80.0,
            "packet_loss": 0.2
        },
        {
            "metric_id": "met_005",
            "device_id": "dev_005",
            "timestamp": "2024-01-15T08:40:00",
            "cpu_usage": 95.0,
            "memory_usage": 90.0,
            "bandwidth_utilization": 95.0,
            "packet_loss": 15.0
        }
    ],
    
    "system_logs": [
        {
            "log_id": "log_001",
            "device_id": "dev_001",
            "timestamp": "2024-01-15T10:00:00",
            "log_level": "info",
            "message": "Routing table updated successfully",
            "source_component": "routing_engine"
        },
        {
            "log_id": "log_002",
            "device_id": "dev_003",
            "timestamp": "2024-01-15T10:01:00",
            "log_level": "warning",
            "message": "High CPU usage detected, threshold exceeded",
            "source_component": "performance_monitor"
        },
        {
            "log_id": "log_003",
            "device_id": "dev_005",
            "timestamp": "2024-01-15T08:44:00",
            "log_level": "error",
            "message": "Connection timeout to upstream provider",
            "source_component": "wan_interface"
        },
        {
            "log_id": "log_004",
            "device_id": "dev_004",
            "timestamp": "2024-01-15T09:00:00",
            "log_level": "info",
            "message": "Entering maintenance mode for firmware update",
            "source_component": "system_manager"
        },
        {
            "log_id": "log_005",
            "device_id": "dev_002",
            "timestamp": "2024-01-15T10:15:00",
            "log_level": "error",
            "message": "Port failure detected on interface eth0/24",
            "source_component": "interface_monitor"
        }
    ],
    
    "alerts": [
        {
            "alert_id": "alt_001",
            "device_id": "dev_003",
            "timestamp": "2024-01-15T10:01:00",
            "alert_type": "high_cpu",
            "severity": "warning",
            "resolved": False
        },
        {
            "alert_id": "alt_002",
            "device_id": "dev_005",
            "timestamp": "2024-01-15T08:45:00",
            "alert_type": "outage",
            "severity": "critical",
            "resolved": False
        },
        {
            "alert_id": "alt_003",
            "device_id": "dev_001",
            "timestamp": "2024-01-14T15:30:00",
            "alert_type": "high_bandwidth",
            "severity": "warning",
            "resolved": True
        },
        {
            "alert_id": "alt_004",
            "device_id": "dev_004",
            "timestamp": "2024-01-13T22:00:00",
            "alert_type": "intrusion_detected",
            "severity": "critical",
            "resolved": True
        }
    ],
    
    "configurations": [
        {
            "config_id": "cfg_001",
            "device_id": "dev_001",
            "version": "1.2.3",
            "timestamp": "2024-01-14T08:00:00",
            "configuration_data": {"ospf_enabled": True, "bgp_as": 65001},
            "applied_by": "admin"
        },
        {
            "config_id": "cfg_002",
            "device_id": "dev_004",
            "version": "2.0.1",
            "timestamp": "2024-01-15T09:00:00",
            "configuration_data": {"firewall_rules": ["allow_https", "block_telnet"]},
            "applied_by": "security_admin"
        },
        {
            "config_id": "cfg_003",
            "device_id": "dev_003",
            "version": "3.1.0",
            "timestamp": "2024-01-10T12:00:00",
            "configuration_data": {"web_server_port": 443, "ssl_enabled": True},
            "applied_by": "devops"
        },
        {
            "config_id": "cfg_004",
            "device_id": "dev_002",
            "version": "1.0.5",
            "timestamp": "2024-01-12T14:30:00",
            "configuration_data": {"vlan_config": [10, 20, 30], "stp_enabled": True},
            "applied_by": "network_admin"
        }
    ],
    
    "incidents": [
        {
            "incident_id": "inc_001",
            "start_time": "2024-01-15T08:45:00",
            "end_time": None,
            "affected_devices": ["dev_005"],
            "status": "open",
            "root_cause": None,
            "resolution_notes": None
        },
        {
            "incident_id": "inc_002",
            "start_time": "2024-01-13T22:00:00",
            "end_time": "2024-01-13T23:30:00",
            "affected_devices": ["dev_004"],
            "status": "resolved",
            "root_cause": "Unauthorized access attempt blocked",
            "resolution_notes": "Blocked malicious IP ranges"
        },
        {
            "incident_id": "inc_003",
            "start_time": "2024-01-14T15:00:00",
            "end_time": "2024-01-14T16:00:00",
            "affected_devices": ["dev_001", "dev_002"],
            "status": "resolved",
            "root_cause": "Network congestion due to DDoS attack",
            "resolution_notes": "Enabled DDoS mitigation"
        }
    ],
    
    "thresholds": {
        "cpu_usage": 90.0,
        "memory_usage": 85.0,
        "bandwidth_utilization": 90.0,
        "packet_loss": 5.0
    },
    
    "outage_detection_window_minutes": 5,
    "min_devices_for_outage": 2,
    
    "next_ids": {
        "metric": 6,
        "log": 6,
        "alert": 5,
        "config": 5,
        "incident": 4
    }
}


class NetworkMonitoringSystem:
    """
    Network Monitoring System Environment API.
    
    Provides comprehensive network monitoring capabilities including device management,
    performance metrics tracking, log analysis, alert management, configuration tracking,
    and incident management for root cause analysis.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Network Monitoring System environment.
        
        Declares all state attributes with type hints and sets the API description.
        """
        self._api_description: str = (
            "A network monitoring system that collects and analyzes data from network devices "
            "to ensure service availability, detect anomalies, and perform root cause analysis."
        )
        
        self.current_user: str = ""
        self.session_id: str = ""
        self.network_devices: List[Dict[str, Any]] = []
        self.performance_metrics: List[Dict[str, Any]] = []
        self.system_logs: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.configurations: List[Dict[str, Any]] = []
        self.incidents: List[Dict[str, Any]] = []
        self.thresholds: Dict[str, float] = {}
        self.outage_detection_window_minutes: int = 5
        self.min_devices_for_outage: int = 2
        self.next_ids: Dict[str, int] = {}
        
        self._injected_timestamp: Optional[str] = None
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (unused but required for interface).
            
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
        Return the current environment state.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables including:
                - current_user: The current authenticated user
                - session_id: Current session identifier
                - network_devices: List of all network devices
                - performance_metrics: List of performance metric records
                - system_logs: List of system log entries
                - alerts: List of alert records
                - configurations: List of configuration records
                - incidents: List of incident records
                - thresholds: Performance threshold values
                - outage_detection_window_minutes: Time window for outage detection
                - min_devices_for_outage: Minimum devices for outage inference
                - next_ids: Counter for generating unique IDs
        """
        return {
            "current_user": self.current_user,
            "session_id": self.session_id,
            "network_devices": deepcopy(self.network_devices),
            "performance_metrics": deepcopy(self.performance_metrics),
            "system_logs": deepcopy(self.system_logs),
            "alerts": deepcopy(self.alerts),
            "configurations": deepcopy(self.configurations),
            "incidents": deepcopy(self.incidents),
            "thresholds": deepcopy(self.thresholds),
            "outage_detection_window_minutes": self.outage_detection_window_minutes,
            "min_devices_for_outage": self.min_devices_for_outage,
            "next_ids": deepcopy(self.next_ids)
        }
    
    def _timestamp(self) -> str:
        """
        Generate a consistent ISO format timestamp.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        if self._injected_timestamp:
            return self._injected_timestamp
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _parse_timestamp(self, ts: str) -> Optional[datetime]:
        """
        Parse an ISO format timestamp string to datetime object.
        
        Args:
            ts: ISO format timestamp string.
            
        Returns:
            Optional[datetime]: Parsed datetime object or None if parsing fails.
        """
        try:
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            return None
    
    def _generate_id(self, id_type: str) -> str:
        """
        Generate a unique ID for a given entity type.
        
        Args:
            id_type: Type of entity (metric, log, alert, config, incident).
            
        Returns:
            str: Generated unique ID.
        """
        prefix_map = {
            "metric": "met",
            "log": "log",
            "alert": "alt",
            "config": "cfg",
            "incident": "inc"
        }
        prefix = prefix_map.get(id_type, id_type[:3])
        current_id = self.next_ids.get(id_type, 1)
        self.next_ids[id_type] = current_id + 1
        return f"{prefix}_{current_id:03d}"
    
    # ==================== Query Operations ====================
    
    def get_device_by_id(self, device_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a network device by its device_id.
        
        Args:
            device_id: The unique identifier of the network device.
            
        Returns:
            Dict[str, Any]: Device information dictionary or error if not found.
        """
        if not device_id:
            return {"error": "device_id is required"}
        
        for device in self.network_devices:
            if device["device_id"] == device_id:
                return {"device": deepcopy(device)}
        
        return {"error": f"Device with id '{device_id}' not found"}
    
    def list_devices_by_type(self, device_type: str) -> Dict[str, Any]:
        """
        List all devices filtered by type for targeted analysis.
        
        Args:
            device_type: Type of device (router, switch, server, firewall).
            
        Returns:
            Dict[str, Any]: List of matching devices or error if invalid type.
        """
        valid_types = ["router", "switch", "server", "firewall"]
        if device_type not in valid_types:
            return {"error": f"Invalid device_type. Must be one of: {valid_types}"}
        
        devices = [
            deepcopy(d) for d in self.network_devices 
            if d["device_type"] == device_type
        ]
        return {"devices": devices, "count": len(devices)}
    
    def list_devices_by_status(self, status: str) -> Dict[str, Any]:
        """
        Retrieve devices currently in a specific status.
        
        Args:
            status: Device status (up, down, maintenance).
            
        Returns:
            Dict[str, Any]: List of matching devices or error if invalid status.
        """
        valid_statuses = ["up", "down", "maintenance"]
        if status not in valid_statuses:
            return {"error": f"Invalid status. Must be one of: {valid_statuses}"}
        
        devices = [
            deepcopy(d) for d in self.network_devices 
            if d["status"] == status
        ]
        return {"devices": devices, "count": len(devices)}
    
    def get_recent_outage_events(
        self, 
        start_time: str, 
        end_time: str
    ) -> Dict[str, Any]:
        """
        Identify time windows where multiple devices reported down status or high packet loss.
        
        Args:
            start_time: Start of the time range (ISO format).
            end_time: End of the time range (ISO format).
            
        Returns:
            Dict[str, Any]: Outage events detected within the time range.
        """
        start_dt = self._parse_timestamp(start_time)
        end_dt = self._parse_timestamp(end_time)
        
        if not start_dt or not end_dt:
            return {"error": "Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}
        
        if start_dt > end_dt:
            return {"error": "start_time must be before end_time"}
        
        outage_events = []
        
        down_devices = []
        for device in self.network_devices:
            last_seen_dt = self._parse_timestamp(device["last_seen"])
            if last_seen_dt and start_dt <= last_seen_dt <= end_dt:
                if device["status"] == "down":
                    down_devices.append({
                        "device_id": device["device_id"],
                        "hostname": device["hostname"],
                        "last_seen": device["last_seen"]
                    })
        
        high_packet_loss_devices = []
        packet_loss_threshold = self.thresholds.get("packet_loss", 5.0)
        for metric in self.performance_metrics:
            metric_dt = self._parse_timestamp(metric["timestamp"])
            if metric_dt and start_dt <= metric_dt <= end_dt:
                if metric.get("packet_loss", 0) > packet_loss_threshold:
                    high_packet_loss_devices.append({
                        "device_id": metric["device_id"],
                        "timestamp": metric["timestamp"],
                        "packet_loss": metric["packet_loss"]
                    })
        
        if len(down_devices) >= self.min_devices_for_outage:
            outage_events.append({
                "type": "multiple_devices_down",
                "devices": down_devices,
                "detected_at": self._timestamp()
            })
        
        if len(high_packet_loss_devices) >= self.min_devices_for_outage:
            outage_events.append({
                "type": "high_packet_loss",
                "devices": high_packet_loss_devices,
                "detected_at": self._timestamp()
            })
        
        return {
            "outage_events": outage_events,
            "down_devices_count": len(down_devices),
            "high_packet_loss_count": len(high_packet_loss_devices),
            "time_range": {"start": start_time, "end": end_time}
        }
    
    def get_metrics_by_device_and_time(
        self, 
        device_id: str, 
        start_time: str, 
        end_time: str
    ) -> Dict[str, Any]:
        """
        Retrieve performance metrics for a specific device within a given time range.
        
        Args:
            device_id: The device identifier.
            start_time: Start of the time range (ISO format).
            end_time: End of the time range (ISO format).
            
        Returns:
            Dict[str, Any]: List of metrics or error if parameters are invalid.
        """
        if not device_id:
            return {"error": "device_id is required"}
        
        start_dt = self._parse_timestamp(start_time)
        end_dt = self._parse_timestamp(end_time)
        
        if not start_dt or not end_dt:
            return {"error": "Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}
        
        if start_dt > end_dt:
            return {"error": "start_time must be before end_time"}
        
        device_exists = any(d["device_id"] == device_id for d in self.network_devices)
        if not device_exists:
            return {"error": f"Device with id '{device_id}' not found"}
        
        metrics = []
        for metric in self.performance_metrics:
            if metric["device_id"] == device_id:
                metric_dt = self._parse_timestamp(metric["timestamp"])
                if metric_dt and start_dt <= metric_dt <= end_dt:
                    metrics.append(deepcopy(metric))
        
        return {"metrics": metrics, "count": len(metrics)}
    
    def get_high_utilization_metrics(
        self, 
        cpu_threshold: Optional[float] = None,
        memory_threshold: Optional[float] = None,
        packet_loss_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Find metrics indicating resource bottlenecks.
        
        Args:
            cpu_threshold: CPU usage threshold (default from system thresholds).
            memory_threshold: Memory usage threshold (default from system thresholds).
            packet_loss_threshold: Packet loss threshold (default from system thresholds).
            
        Returns:
            Dict[str, Any]: List of metrics exceeding thresholds.
        """
        cpu_thresh = cpu_threshold if cpu_threshold is not None else self.thresholds.get("cpu_usage", 90.0)
        mem_thresh = memory_threshold if memory_threshold is not None else self.thresholds.get("memory_usage", 85.0)
        pkt_thresh = packet_loss_threshold if packet_loss_threshold is not None else self.thresholds.get("packet_loss", 5.0)
        
        high_util_metrics = []
        for metric in self.performance_metrics:
            reasons = []
            if metric.get("cpu_usage", 0) >= cpu_thresh:
                reasons.append(f"high_cpu ({metric['cpu_usage']}%)")
            if metric.get("memory_usage", 0) >= mem_thresh:
                reasons.append(f"high_memory ({metric['memory_usage']}%)")
            if metric.get("packet_loss", 0) >= pkt_thresh:
                reasons.append(f"high_packet_loss ({metric['packet_loss']}%)")
            
            if reasons:
                metric_copy = deepcopy(metric)
                metric_copy["threshold_violations"] = reasons
                high_util_metrics.append(metric_copy)
        
        return {
            "metrics": high_util_metrics,
            "count": len(high_util_metrics),
            "thresholds_used": {
                "cpu": cpu_thresh,
                "memory": mem_thresh,
                "packet_loss": pkt_thresh
            }
        }
    
    def get_logs_by_time_range(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Retrieve system logs within a specified time window for forensic analysis.
        
        Args:
            start_time: Start of the time range (ISO format).
            end_time: End of the time range (ISO format).
            
        Returns:
            Dict[str, Any]: List of logs within the time range.
        """
        start_dt = self._parse_timestamp(start_time)
        end_dt = self._parse_timestamp(end_time)
        
        if not start_dt or not end_dt:
            return {"error": "Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}
        
        if start_dt > end_dt:
            return {"error": "start_time must be before end_time"}
        
        logs = []
        for log in self.system_logs:
            log_dt = self._parse_timestamp(log["timestamp"])
            if log_dt and start_dt <= log_dt <= end_dt:
                logs.append(deepcopy(log))
        
        return {"logs": logs, "count": len(logs)}
    
    def get_logs_by_level(self, log_level: str) -> Dict[str, Any]:
        """
        Filter logs by severity level to identify critical events.
        
        Args:
            log_level: Log severity level (info, warning, error).
            
        Returns:
            Dict[str, Any]: List of logs matching the specified level.
        """
        valid_levels = ["info", "warning", "error"]
        if log_level not in valid_levels:
            return {"error": f"Invalid log_level. Must be one of: {valid_levels}"}
        
        logs = [deepcopy(log) for log in self.system_logs if log["log_level"] == log_level]
        return {"logs": logs, "count": len(logs)}
    
    def get_alerts_by_time_range(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Retrieve all alerts generated within a specific time period.
        
        Args:
            start_time: Start of the time range (ISO format).
            end_time: End of the time range (ISO format).
            
        Returns:
            Dict[str, Any]: List of alerts within the time range.
        """
        start_dt = self._parse_timestamp(start_time)
        end_dt = self._parse_timestamp(end_time)
        
        if not start_dt or not end_dt:
            return {"error": "Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}
        
        if start_dt > end_dt:
            return {"error": "start_time must be before end_time"}
        
        alerts = []
        for alert in self.alerts:
            alert_dt = self._parse_timestamp(alert["timestamp"])
            if alert_dt and start_dt <= alert_dt <= end_dt:
                alerts.append(deepcopy(alert))
        
        return {"alerts": alerts, "count": len(alerts)}
    
    def get_unresolved_alerts(self) -> Dict[str, Any]:
        """
        List active alerts that have not been resolved.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: List of unresolved alerts.
        """
        unresolved = [deepcopy(a) for a in self.alerts if not a["resolved"]]
        return {"alerts": unresolved, "count": len(unresolved)}
    
    def get_alerts_by_type(self, alert_type: str) -> Dict[str, Any]:
        """
        Filter alerts by type to investigate specific threats.
        
        Args:
            alert_type: Type of alert (e.g., high_cpu, outage, intrusion_detected).
            
        Returns:
            Dict[str, Any]: List of alerts matching the specified type.
        """
        if not alert_type:
            return {"error": "alert_type is required"}
        
        alerts = [deepcopy(a) for a in self.alerts if a["alert_type"] == alert_type]
        return {"alerts": alerts, "count": len(alerts)}
    
    def get_configuration_changes_by_time(
        self, 
        start_time: str, 
        end_time: str
    ) -> Dict[str, Any]:
        """
        Retrieve configuration changes applied within a time window.
        
        Args:
            start_time: Start of the time range (ISO format).
            end_time: End of the time range (ISO format).
            
        Returns:
            Dict[str, Any]: List of configuration changes within the time range.
        """
        start_dt = self._parse_timestamp(start_time)
        end_dt = self._parse_timestamp(end_time)
        
        if not start_dt or not end_dt:
            return {"error": "Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}
        
        if start_dt > end_dt:
            return {"error": "start_time must be before end_time"}
        
        configs = []
        for config in self.configurations:
            config_dt = self._parse_timestamp(config["timestamp"])
            if config_dt and start_dt <= config_dt <= end_dt:
                configs.append(deepcopy(config))
        
        return {"configurations": configs, "count": len(configs)}
    
    def get_configuration_by_device(
        self, 
        device_id: str, 
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the latest or historical configuration of a specific device.
        
        Args:
            device_id: The device identifier.
            version: Optional specific version to retrieve. If None, returns latest.
            
        Returns:
            Dict[str, Any]: Configuration data or error if not found.
        """
        if not device_id:
            return {"error": "device_id is required"}
        
        device_exists = any(d["device_id"] == device_id for d in self.network_devices)
        if not device_exists:
            return {"error": f"Device with id '{device_id}' not found"}
        
        device_configs = [c for c in self.configurations if c["device_id"] == device_id]
        
        if not device_configs:
            return {"error": f"No configurations found for device '{device_id}'"}
        
        if version:
            for config in device_configs:
                if config["version"] == version:
                    return {"configuration": deepcopy(config)}
            return {"error": f"Version '{version}' not found for device '{device_id}'"}
        
        latest_config = max(
            device_configs, 
            key=lambda c: self._parse_timestamp(c["timestamp"]) or datetime.min
        )
        return {"configuration": deepcopy(latest_config)}
    
    def get_incidents_by_time_range(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Retrieve incidents that started within a given time period.
        
        Args:
            start_time: Start of the time range (ISO format).
            end_time: End of the time range (ISO format).
            
        Returns:
            Dict[str, Any]: List of incidents within the time range.
        """
        start_dt = self._parse_timestamp(start_time)
        end_dt = self._parse_timestamp(end_time)
        
        if not start_dt or not end_dt:
            return {"error": "Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."}
        
        if start_dt > end_dt:
            return {"error": "Start time must be before end time."}
        
        matching_incidents = []
        for incident in self.incidents:
            incident_time = self._parse_timestamp(incident.get("start_time", ""))
            if incident_time and start_dt <= incident_time <= end_dt:
                matching_incidents.append(deepcopy(incident))
        
        return {"incidents": matching_incidents, "count": len(matching_incidents)}
    
    def get_device_health_summary(self, device_id: str) -> Dict[str, Any]:
        """
        Get a health summary for a specific device.
        
        Args:
            device_id: The unique identifier of the device.
            
        Returns:
            Dict[str, Any]: Health summary including status, recent incidents, and metrics.
        """
        device = None
        for d in self.network_devices:
            if d.get("device_id") == device_id:
                device = d
                break
                
        if not device:
            return {"error": f"Device '{device_id}' not found."}
        
        # Get recent incidents for this device
        device_incidents = [
            inc for inc in self.incidents 
            if device_id in inc.get("affected_devices", [])
        ]
        recent_incidents = sorted(
            device_incidents,
            key=lambda x: self._parse_timestamp(x.get("start_time", "")) or datetime.min,
            reverse=True
        )[:5]
        
        # Get latest metrics
        device_metrics = [m for m in self.performance_metrics if m.get("device_id") == device_id]
        latest_metrics = {}
        if device_metrics:
            latest = max(
                device_metrics,
                key=lambda m: self._parse_timestamp(m.get("timestamp", "")) or datetime.min
            )
            latest_metrics = deepcopy(latest)
        
        return {
            "device_id": device_id,
            "status": device.get("status", "unknown"),
            "device_type": device.get("device_type", "unknown"),
            "hostname": device.get("hostname", "unknown"),
            "recent_incidents": recent_incidents,
            "latest_metrics": latest_metrics,
            "total_incidents": len(device_incidents)
        }


__TEST_CASES__ = [
    {
        "name": "test_get_device_health_summary_success",
        "setup": lambda env: env._load_scenario({}),
        "action": lambda env: env.get_device_health_summary("dev_005"),
        "check": lambda result: result.get("device_id") == "dev_005" and result.get("status") == "down" and "recent_incidents" in result,
    },
    {
        "name": "test_get_device_health_summary_not_found",
        "setup": lambda env: env._load_scenario({}),
        "action": lambda env: env.get_device_health_summary("invalid_device"),
        "expected": {"error": "Device 'invalid_device' not found."},
    },
    {
        "name": "test_get_incidents_by_time_range_success",
        "setup": lambda env: env._load_scenario({}),
        "action": lambda env: env.get_incidents_by_time_range("2024-01-13T00:00:00", "2024-01-16T00:00:00"),
        "check": lambda result: "incidents" in result and result.get("count", 0) > 0,
    },
    {
        "name": "test_get_incidents_by_time_range_invalid_format",
        "setup": lambda env: env._load_scenario({}),
        "action": lambda env: env.get_incidents_by_time_range("2024/01/14", "2024-01-16T00:00:00"),
        "expected": {"error": "Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."},
    },
    {
        "name": "test_get_recent_outage_events",
        "setup": lambda env: env._load_scenario({}),
        "action": lambda env: env.get_recent_outage_events("2024-01-15T00:00:00", "2024-01-15T12:00:00"),
        "check": lambda result: "outage_events" in result,
    }
]