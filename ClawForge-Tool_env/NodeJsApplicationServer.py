"""
Node.js Application Server Environment API

A simulated Node.js application server environment for Agentic RL training.
Supports service health monitoring, external data services, request context management,
and product caching operations.
"""

import time
from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Default state containing initial data for all entities
DEFAULT_STATE: Dict[str, Any] = {
    # ServiceHealthIndicator entities
    "service_health_indicators": {
        "utile_space": {
            "service_name": "utile_space",
            "status": "healthy",
            "last_checked": "2024-01-15T10:30:00",
            "response_time": 45
        },
        "auth_service": {
            "service_name": "auth_service",
            "status": "healthy",
            "last_checked": "2024-01-15T10:29:55",
            "response_time": 120
        },
        "cache_service": {
            "service_name": "cache_service",
            "status": "unhealthy",
            "last_checked": "2024-01-15T10:25:00",
            "response_time": 5000
        }
    },
    
    # ExternalDataService entities
    "external_data_services": {
        "product_database": {
            "service_type": "database",
            "connection_status": "connected",
            "endpoint": "postgresql://db.example.com:5432/products",
            "last_response": "2024-01-15T10:30:00"
        },
        "inventory_api": {
            "service_type": "API",
            "connection_status": "connected",
            "endpoint": "https://api.inventory.example.com/v1",
            "last_response": "2024-01-15T10:29:50"
        },
        "payment_gateway": {
            "service_type": "API",
            "connection_status": "disconnected",
            "endpoint": "https://payments.example.com/api",
            "last_response": "2024-01-15T09:00:00"
        }
    },
    
    # RuntimeRequestContext entities
    "request_contexts": {
        "req-001": {
            "request_id": "req-001",
            "input_parameters": {"h": 180, "s": 50, "v": 75},
            "computed_results": {"rgb": [96, 191, 191], "hex": "#60BFBF"},
            "timestamp": "2024-01-15T10:28:00"
        },
        "req-002": {
            "request_id": "req-002",
            "input_parameters": {"h": 0, "s": 100, "v": 100},
            "computed_results": {"rgb": [255, 0, 0], "hex": "#FF0000"},
            "timestamp": "2024-01-15T10:29:00"
        },
        "req-003": {
            "request_id": "req-003",
            "input_parameters": {"h": 120, "s": 80, "v": 60},
            "computed_results": None,
            "timestamp": "2024-01-15T10:30:00"
        }
    },
    
    # ProductCache entities
    "product_cache": {
        "12345": {
            "product_id": "12345",
            "name": "Wireless Bluetooth Headphones",
            "price": 79.99,
            "last_updated": "2024-01-15T10:00:00",
            "cached_at": "2024-01-15T10:00:00"
        },
        "67890": {
            "product_id": "67890",
            "name": "USB-C Charging Cable",
            "price": 12.99,
            "last_updated": "2024-01-15T09:45:00",
            "cached_at": "2024-01-15T09:45:00"
        },
        "11111": {
            "product_id": "11111",
            "name": "Mechanical Keyboard",
            "price": 149.99,
            "last_updated": "2024-01-14T15:00:00",
            "cached_at": "2024-01-14T15:00:00"
        }
    },
    
    # Auxiliary state
    "current_user": {
        "user_id": "admin-001",
        "username": "system_admin",
        "roles": ["admin", "operator"],
        "authenticated": True
    },
    
    "session": {
        "session_id": "sess-abc123",
        "created_at": "2024-01-15T08:00:00",
        "expires_at": "2024-01-15T20:00:00"
    },
    
    # Configuration
    "health_check_threshold_seconds": 30,
    "cache_ttl_seconds": 3600,
    
    # Simulated current time for testing
    "simulated_current_time": "2024-01-15T10:30:15",
    
    # Newly integrated state fields for managers
    "user_sessions": {},
    "rate_limit_buckets": {},
    "configurations": {}
}


class NodeJsApplicationServerEnv:
    """
    A Node.js application server environment for Agentic RL training.
    
    This environment simulates a runtime that executes JavaScript on the server side,
    supporting operations like service health monitoring, data retrieval, computation,
    and system monitoring.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Node.js Application Server environment.
        
        Declares all state attributes with type hints and sets the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self._api_description: str = (
            "A Node.js application server environment that manages service health, "
            "external data services, request contexts, and product caching."
        )
        
        # State attributes with type hints
        self.service_health_indicators: Dict[str, Dict[str, Any]] = {}
        self.external_data_services: Dict[str, Dict[str, Any]] = {}
        self.request_contexts: Dict[str, Dict[str, Any]] = {}
        self.product_cache: Dict[str, Dict[str, Any]] = {}
        self.current_user: Dict[str, Any] = {}
        self.session: Dict[str, Any] = {}
        self.health_check_threshold_seconds: int = 30
        self.cache_ttl_seconds: int = 3600
        self.simulated_current_time: str = ""
        self.user_sessions: Dict[str, Any] = {}
        self.rate_limit_buckets: Dict[str, Any] = {}
        self.configurations: Dict[str, Any] = {}
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: A dictionary containing initial state values.
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
        Return the current environment state as a dictionary.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables.
        """
        return {
            "service_health_indicators": deepcopy(self.service_health_indicators),
            "external_data_services": deepcopy(self.external_data_services),
            "request_contexts": deepcopy(self.request_contexts),
            "product_cache": deepcopy(self.product_cache),
            "current_user": deepcopy(self.current_user),
            "session": deepcopy(self.session),
            "health_check_threshold_seconds": self.health_check_threshold_seconds,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "simulated_current_time": self.simulated_current_time,
            "user_sessions": deepcopy(self.user_sessions),
            "rate_limit_buckets": deepcopy(self.rate_limit_buckets),
            "configurations": deepcopy(self.configurations)
        }
    
    def _timestamp(self) -> str:
        """
        Generate a unified timestamp string.
        
        Uses the simulated current time for testing consistency.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        if self.simulated_current_time:
            return self.simulated_current_time
        # fallback if not set
        now = datetime.now()
        return now.isoformat()[:19]
    
    def _parse_timestamp(self, ts: str) -> datetime:
        """
        Parse an ISO timestamp string to datetime object.
        
        Args:
            ts: ISO format timestamp string.
        
        Returns:
            datetime: Parsed datetime object.
        """
        return datetime.fromisoformat(ts)
    
    def _is_user_authorized(self) -> bool:
        """
        Check if current user is authenticated and authorized.
        
        Args:
            None
        
        Returns:
            bool: True if user is authenticated with admin or operator role.
        """
        if not self.current_user.get("authenticated", False):
            return False
        roles = self.current_user.get("roles", [])
        return "admin" in roles or "operator" in roles
    
    # ==================== Query Operations ====================
    
    def get_service_health_status(self, service_name: str) -> Dict[str, Any]:
        """
        Retrieve the current health status for a given service.
        
        Args:
            service_name: The name of the service to check.
        
        Returns:
            Dict[str, Any]: A dictionary with service health status.
        """
        if service_name not in self.service_health_indicators:
            return {"error": f"Service '{service_name}' not found in health indicators"}
        
        indicator = self.service_health_indicators[service_name]
        return {
            "service_name": indicator["service_name"],
            "status": indicator["status"],
            "response_time": indicator["response_time"],
            "last_checked": indicator["last_checked"]
        }
    
    def is_service_health_check_fresh(self, service_name: str) -> Dict[str, Any]:
        """
        Determine whether the health check for a service is recent (within threshold).
        
        Args:
            service_name: The name of the service to check.
        
        Returns:
            Dict[str, Any]: A dictionary indicating freshness.
        """
        if service_name not in self.service_health_indicators:
            return {"error": f"Service '{service_name}' not found in health indicators"}
        
        indicator = self.service_health_indicators[service_name]
        last_checked = self._parse_timestamp(indicator["last_checked"])
        current_time = self._parse_timestamp(self._timestamp())
        age_seconds = (current_time - last_checked).total_seconds()
        
        return {
            "service_name": service_name,
            "is_fresh": age_seconds <= self.health_check_threshold_seconds,
            "age_seconds": age_seconds,
            "threshold_seconds": self.health_check_threshold_seconds
        }
    
    def get_external_service_connection_status(self, service_id: str) -> Dict[str, Any]:
        """
        Check if an external service is currently connected and responsive.
        
        Args:
            service_id: The identifier of the external service.
        
        Returns:
            Dict[str, Any]: Connection status info.
        """
        if service_id not in self.external_data_services:
            return {"error": f"External service '{service_id}' not found"}
        
        service = self.external_data_services[service_id]
        return {
            "service_id": service_id,
            "service_type": service["service_type"],
            "connection_status": service["connection_status"],
            "endpoint": service["endpoint"],
            "last_response": service["last_response"]
        }
    
    def get_cached_product_info(self, product_id: str) -> Dict[str, Any]:
        """
        Retrieve product data from the in-memory cache by product ID.
        
        Args:
            product_id: The unique identifier of the product.
        
        Returns:
            Dict[str, Any]: Cached product data.
        """
        if product_id not in self.product_cache:
            return {"error": f"Product '{product_id}' not found in cache"}
        
        product = self.product_cache[product_id]
        return {
            "product_id": product["product_id"],
            "name": product["name"],
            "price": product["price"],
            "last_updated": product["last_updated"],
            "cached_at": product["cached_at"]
        }
    
    def get_request_computed_results(self, request_id: str) -> Dict[str, Any]:
        """
        Fetch the computed results from a specific request context.
        
        Args:
            request_id: The unique identifier of the request context.
        
        Returns:
            Dict[str, Any]: Computed results from the context.
        """
        if request_id not in self.request_contexts:
            return {"error": f"Request context '{request_id}' not found"}
        
        context = self.request_contexts[request_id]
        return {
            "request_id": context["request_id"],
            "input_parameters": context["input_parameters"],
            "computed_results": context["computed_results"],
            "timestamp": context["timestamp"]
        }
    
    def list_all_external_services(self) -> Dict[str, Any]:
        """
        Return a list of all registered external data services.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: List of all external services.
        """
        services = []
        for service_id, service in self.external_data_services.items():
            services.append({
                "service_id": service_id,
                "service_type": service["service_type"],
                "endpoint": service["endpoint"],
                "connection_status": service["connection_status"]
            })
        
        return {
            "services": services,
            "total_count": len(services)
        }
    
    def check_request_context_exists(self, request_id: str) -> Dict[str, Any]:
        """
        Verify whether a request context with given ID is active or expired.
        
        Args:
            request_id: The unique identifier of the request context.
        
        Returns:
            Dict[str, Any]: Existence info.
        """
        if request_id not in self.request_contexts:
            return {
                "request_id": request_id,
                "exists": False,
                "timestamp": None,
                "has_results": False
            }
        
        context = self.request_contexts[request_id]
        return {
            "request_id": request_id,
            "exists": True,
            "timestamp": context["timestamp"],
            "has_results": context["computed_results"] is not None
        }
    
    # ==================== State Change Operations ====================
    
    def trigger_service_health_check(self, service_name: str) -> Dict[str, Any]:
        """
        Initiate a health probe for a specified service and update its status.
        
        Args:
            service_name: The name of the service to check.
        
        Returns:
            Dict[str, Any]: Result of the health check trigger.
        """
        if not self._is_user_authorized():
            return {"error": "Unauthorized: User must be authenticated with admin or operator role"}
        
        if service_name not in self.service_health_indicators:
            return {"error": f"Service '{service_name}' not found in health indicators"}
        
        current_time = self._timestamp()
        indicator = self.service_health_indicators[service_name]
        
        simulated_response_time = 50  # milliseconds
        
        indicator["last_checked"] = current_time
        indicator["response_time"] = simulated_response_time
        indicator["status"] = "healthy" if simulated_response_time < 1000 else "unhealthy"
        
        return {
            "success": True,
            "service_name": service_name,
            "new_status": indicator["status"],
            "response_time": indicator["response_time"],
            "checked_at": current_time
        }
    
    def create_request_context(self, request_id: str, input_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize a new runtime request context with input parameters.
        
        Args:
            request_id: Unique identifier for the new request context.
            input_parameters: Dictionary of input parameters.
        
        Returns:
            Dict[str, Any]: Result of creation.
        """
        if request_id in self.request_contexts:
            return {"error": f"Request context '{request_id}' already exists"}
        
        if not input_parameters:
            return {"error": "Input parameters cannot be empty"}
        
        current_time = self._timestamp()
        
        self.request_contexts[request_id] = {
            "request_id": request_id,
            "input_parameters": deepcopy(input_parameters),
            "computed_results": None,
            "timestamp": current_time
        }
        
        return {
            "success": True,
            "request_id": request_id,
            "input_parameters": input_parameters,
            "timestamp": current_time
        }
    
    def perform_color_conversion(self, request_id: str) -> Dict[str, Any]:
        """
        Compute color space conversion (HSV to RGB/HEX) within a request context.
        
        Args:
            request_id: The request context ID containing HSV input parameters.
        
        Returns:
            Dict[str, Any]: Conversion result.
        """
        if request_id not in self.request_contexts:
            return {"error": f"Request context '{request_id}' not found"}
        
        context = self.request_contexts[request_id]
        params = context["input_parameters"]
        
        if not all(key in params for key in ["h", "s", "v"]):
            return {"error": "Input parameters must contain 'h', 's', 'v' values"}
        
        h = params["h"]
        s = params["s"]
        v = params["v"]
        
        if not (0 <= h <= 360):
            return {"error": f"Hue must be between 0 and 360, got {h}"}
        if not (0 <= s <= 100):
            return {"error": f"Saturation must be between 0 and 100, got {s}"}
        if not (0 <= v <= 100):
            return {"error": f"Value must be between 0 and 100, got {v}"}
        
        s_norm = s / 100
        v_norm = v / 100
        
        c = v_norm * s_norm
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v_norm - c
        
        if 0 <= h < 60:
            r_prime, g_prime, b_prime = c, x, 0
        elif 60 <= h < 120:
            r_prime, g_prime, b_prime = x, c, 0
        elif 120 <= h < 180:
            r_prime, g_prime, b_prime = 0, c, x
        elif 180 <= h < 240:
            r_prime, g_prime, b_prime = 0, x, c
        elif 240 <= h < 300:
            r_prime, g_prime, b_prime = x, 0, c
        else:
            r_prime, g_prime, b_prime = c, 0, x
        
        r = int((r_prime + m) * 255)
        g = int((g_prime + m) * 255)
        b = int((b_prime + m) * 255)
        
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        
        context["computed_results"] = {
            "rgb": [r, g, b],
            "hex": hex_color
        }
        
        return {
            "success": True,
            "request_id": request_id,
            "input_hsv": {"h": h, "s": s, "v": v},
            "rgb": [r, g, b],
            "hex": hex_color
        }
    
    def cache_product_data(self, product_id: str, name: str, price: float) -> Dict[str, Any]:
        """
        Add or update a product entry in the in-memory product cache.
        
        Args:
            product_id: Unique identifier for the product.
            name: Product name.
            price: Product price.
        
        Returns:
            Dict[str, Any]: The cache operation result.
        """
        has_connected_service = any(
            svc["connection_status"] == "connected" 
            for svc in self.external_data_services.values()
        )
        
        if not has_connected_service:
            return {"error": "Cannot cache product data: No external service is connected"}
        
        if not product_id or not name:
            return {"error": "Product ID and name are required"}
        
        if price < 0:
            return {"error": "Product price cannot be negative"}
        
        current_time = self._timestamp()
        is_update = product_id in self.product_cache
        
        self.product_cache[product_id] = {
            "product_id": product_id,
            "name": name,
            "price": price,
            "last_updated": current_time,
            "cached_at": current_time
        }
        
        return {
            "success": True,
            "product_id": product_id,
            "name": name,
            "price": price,
            "cached_at": current_time,
            "is_update": is_update
        }
    
    def update_external_service_status(self, service_id: str, connection_status: str) -> Dict[str, Any]:
        """
        Update the connection status of an external service.
        
        Args:
            service_id: The identifier of the external service.
            connection_status: New status ('connected' or 'disconnected').
        
        Returns:
            Dict[str, Any]: The update result.
        """
        if not self._is_user_authorized():
            return {"error": "Unauthorized: User must be authenticated with admin or operator role"}
        
        if service_id not in self.external_data_services:
            return {"error": f"External service '{service_id}' not found"}
        
        valid_statuses = ["connected", "disconnected"]
        if connection_status not in valid_statuses:
            return {"error": f"Invalid status '{connection_status}'. Must be one of: {valid_statuses}"}
        
        service = self.external_data_services[service_id]
        old_status = service["connection_status"]
        current_time = self._timestamp()
        
        service["connection_status"] = connection_status
        service["last_response"] = current_time
        
        return {
            "success": True,
            "service_id": service_id,
            "old_status": old_status,
            "new_status": connection_status,
            "updated_at": current_time
        }
    
    def clear_request_context(self, request_id: str) -> Dict[str, Any]:
        """
        Remove an expired or completed request context to free up memory.
        
        Args:
            request_id: The unique identifier of the request context to clear.
        
        Returns:
            Dict[str, Any]: The operation result.
        """
        if request_id not in self.request_contexts:
            return {"error": f"Request context '{request_id}' not found"}
        
        context = self.request_contexts[request_id]
        had_results = context["computed_results"] is not None
        
        del self.request_contexts[request_id]
        
        return {
            "success": True,
            "request_id": request_id,
            "had_results": had_results
        }
    
    def invalidate_stale_product_cache(self, product_id: str, max_age_seconds: float = 3600) -> Dict[str, Any]:
        """
        Remove outdated product cache entries based on timestamps.
        
        Args:
            product_id: The product ID to check and potentially invalidate.
            max_age_seconds: Maximum allowed age in seconds before considered stale.
        
        Returns:
            Dict[str, Any]: The invalidation result.
        """
        if product_id not in self.product_cache:
            return {"error": f"Product '{product_id}' not found in cache"}
        
        product = self.product_cache[product_id]
        cached_at = self._parse_timestamp(product["cached_at"])
        current_time = self._parse_timestamp(self._timestamp())
        age_seconds = (current_time - cached_at).total_seconds()
        
        was_stale = age_seconds > max_age_seconds
        
        if was_stale:
            del self.product_cache[product_id]
        
        return {
            "success": True,
            "product_id": product_id,
            "was_stale": was_stale,
            "removed": was_stale,
            "age_seconds": age_seconds
        }

    # ==================== Session Management Methods ====================

    def create_user_session(self, user_id: str, session_data: dict = None) -> dict:
        """
        Create a new user session.
        
        Args:
            user_id: The user ID.
            session_data: Additional session data dictionary.
            
        Returns:
            dict: Session creation status or error.
        """
        if not user_id or not isinstance(user_id, str):
            return {"error": "Invalid user_id: must be a non-empty string"}
        
        if user_id in self.user_sessions:
            return {"error": f"Session already exists for user_id: {user_id}"}
        
        session = {
            "user_id": user_id,
            "data": session_data or {},
            "created_at": time.time(),
            "last_accessed": time.time(),
            "valid": True
        }
        
        self.user_sessions[user_id] = session
        
        return {
            "success": True,
            "user_id": user_id,
            "session_created": True,
            "created_at": session["created_at"]
        }
    
    def get_user_session(self, user_id: str) -> dict:
        """
        Retrieve a user session.
        
        Args:
            user_id: The user ID.
            
        Returns:
            dict: Session details or error.
        """
        if not user_id or not isinstance(user_id, str):
            return {"error": "Invalid user_id: must be a non-empty string"}
        
        if user_id not in self.user_sessions:
            return {"error": f"No session found for user_id: {user_id}"}
        
        session = self.user_sessions[user_id]
        session["last_accessed"] = time.time()
        
        return {
            "success": True,
            "user_id": user_id,
            "session_data": session["data"],
            "created_at": session["created_at"],
            "last_accessed": session["last_accessed"],
            "valid": session["valid"]
        }
    
    def update_user_session(self, user_id: str, updates: dict) -> dict:
        """
        Update user session data.
        
        Args:
            user_id: The user ID.
            updates: Dictionary containing the key-value pairs to update.
            
        Returns:
            dict: Update status or error.
        """
        if not user_id or not isinstance(user_id, str):
            return {"error": "Invalid user_id: must be a non-empty string"}
        
        if user_id not in self.user_sessions:
            return {"error": f"No session found for user_id: {user_id}"}
        
        if not isinstance(updates, dict):
            return {"error": "Updates must be a dictionary"}
        
        session = self.user_sessions[user_id]
        session["data"].update(updates)
        session["last_accessed"] = time.time()
        
        return {
            "success": True,
            "user_id": user_id,
            "updated_keys": list(updates.keys()),
            "last_accessed": session["last_accessed"]
        }
    
    def is_user_session_valid(self, user_id: str, max_age_seconds: float = 3600) -> dict:
        """
        Check if a user session is still valid based on its age.
        
        Args:
            user_id: The user ID.
            max_age_seconds: Maximum allowed session age.
            
        Returns:
            dict: Session validity status or error.
        """
        if not user_id or not isinstance(user_id, str):
            return {"error": "Invalid user_id: must be a non-empty string"}
        
        if user_id not in self.user_sessions:
            return {"error": f"No session found for user_id: {user_id}"}
        
        session = self.user_sessions[user_id]
        age = time.time() - session["created_at"]
        is_valid = session["valid"] and age <= max_age_seconds
        
        return {
            "success": True,
            "user_id": user_id,
            "is_valid": is_valid,
            "age_seconds": age,
            "max_age_seconds": max_age_seconds,
            "session_valid_flag": session["valid"]
        }
    
    def invalidate_user_session(self, user_id: str) -> dict:
        """
        Invalidate a user session and remove it from active sessions.
        
        Args:
            user_id: The user ID.
            
        Returns:
            dict: Invalidation status or error.
        """
        if not user_id or not isinstance(user_id, str):
            return {"error": "Invalid user_id: must be a non-empty string"}
        
        if user_id not in self.user_sessions:
            return {"error": f"No session found for user_id: {user_id}"}
        
        session = self.user_sessions.pop(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "session_invalidated": True,
            "session_duration_seconds": time.time() - session["created_at"]
        }

    # ==================== Rate Limiting Methods ====================

    def initialize_rate_limit_bucket(self, client_id: str, max_requests: int = 100, window_seconds: int = 60) -> dict:
        """
        Initialize a rate limit bucket for a client.
        
        Args:
            client_id: The client identifier.
            max_requests: Maximum requests allowed in the window.
            window_seconds: Time window in seconds.
            
        Returns:
            dict: Initialization status or error.
        """
        if not client_id or not isinstance(client_id, str):
            return {"error": "Invalid client_id: must be a non-empty string"}
        
        if max_requests <= 0:
            return {"error": "max_requests must be a positive integer"}
        
        if window_seconds <= 0:
            return {"error": "window_seconds must be a positive integer"}
        
        bucket = {
            "client_id": client_id,
            "max_requests": max_requests,
            "window_seconds": window_seconds,
            "requests": [],
            "created_at": time.time()
        }
        
        self.rate_limit_buckets[client_id] = bucket
        
        return {
            "success": True,
            "client_id": client_id,
            "max_requests": max_requests,
            "window_seconds": window_seconds,
            "bucket_initialized": True
        }
    
    def record_client_request(self, client_id: str) -> dict:
        """
        Record a request from a client.
        
        Args:
            client_id: The client identifier.
            
        Returns:
            dict: Recording status or error.
        """
        if not client_id or not isinstance(client_id, str):
            return {"error": "Invalid client_id: must be a non-empty string"}
        
        if client_id not in self.rate_limit_buckets:
            return {"error": f"No rate limit bucket found for client_id: {client_id}"}
        
        bucket = self.rate_limit_buckets[client_id]
        current_time = time.time()
        
        # Clean up old requests outside the window
        window_start = current_time - bucket["window_seconds"]
        bucket["requests"] = [t for t in bucket["requests"] if t > window_start]
        
        # Check if rate limited
        if len(bucket["requests"]) >= bucket["max_requests"]:
            return {
                "success": False,
                "client_id": client_id,
                "rate_limited": True,
                "current_requests": len(bucket["requests"]),
                "max_requests": bucket["max_requests"],
                "retry_after_seconds": bucket["requests"][0] + bucket["window_seconds"] - current_time
            }
        
        # Record the request
        bucket["requests"].append(current_time)
        
        return {
            "success": True,
            "client_id": client_id,
            "request_recorded": True,
            "current_requests": len(bucket["requests"]),
            "remaining_requests": bucket["max_requests"] - len(bucket["requests"])
        }
    
    def get_rate_limit_status(self, client_id: str) -> dict:
        """
        Get the current rate limit status for a client.
        
        Args:
            client_id: The client identifier.
            
        Returns:
            dict: Status details or error.
        """
        if not client_id or not isinstance(client_id, str):
            return {"error": "Invalid client_id: must be a non-empty string"}
        
        if client_id not in self.rate_limit_buckets:
            return {"error": f"No rate limit bucket found for client_id: {client_id}"}
        
        bucket = self.rate_limit_buckets[client_id]
        current_time = time.time()
        
        # Clean up old requests
        window_start = current_time - bucket["window_seconds"]
        bucket["requests"] = [t for t in bucket["requests"] if t > window_start]
        
        return {
            "success": True,
            "client_id": client_id,
            "current_requests": len(bucket["requests"]),
            "max_requests": bucket["max_requests"],
            "remaining_requests": bucket["max_requests"] - len(bucket["requests"]),
            "window_seconds": bucket["window_seconds"],
            "window_resets_in": bucket["window_seconds"] - (current_time - window_start) if bucket["requests"] else bucket["window_seconds"]
        }
    
    def is_client_rate_limited(self, client_id: str) -> dict:
        """
        Check if a client is currently rate limited.
        
        Args:
            client_id: The client identifier.
            
        Returns:
            dict: Limit boolean status or error.
        """
        if not client_id or not isinstance(client_id, str):
            return {"error": "Invalid client_id: must be a non-empty string"}
        
        if client_id not in self.rate_limit_buckets:
            return {"error": f"No rate limit bucket found for client_id: {client_id}"}
        
        bucket = self.rate_limit_buckets[client_id]
        current_time = time.time()
        
        # Clean up old requests
        window_start = current_time - bucket["window_seconds"]
        bucket["requests"] = [t for t in bucket["requests"] if t > window_start]
        
        is_limited = len(bucket["requests"]) >= bucket["max_requests"]
        
        return {
            "success": True,
            "client_id": client_id,
            "is_rate_limited": is_limited,
            "current_requests": len(bucket["requests"]),
            "max_requests": bucket["max_requests"]
        }
    
    def reset_rate_limit_bucket(self, client_id: str) -> dict:
        """
        Reset a client's rate limit bucket.
        
        Args:
            client_id: The client identifier.
            
        Returns:
            dict: Reset status or error.
        """
        if not client_id or not isinstance(client_id, str):
            return {"error": "Invalid client_id: must be a non-empty string"}
        
        if client_id not in self.rate_limit_buckets:
            return {"error": f"No rate limit bucket found for client_id: {client_id}"}
        
        bucket = self.rate_limit_buckets[client_id]
        previous_count = len(bucket["requests"])
        bucket["requests"] = []
        
        return {
            "success": True,
            "client_id": client_id,
            "bucket_reset": True,
            "cleared_requests": previous_count
        }

    # ==================== Configuration Methods ====================

    def load_configuration(self, config_name: str) -> dict:
        """
        Load a configuration by name into memory.
        
        Args:
            config_name: The name of the configuration to load.
            
        Returns:
            dict: Loaded configuration details or error.
        """
        if not config_name or not isinstance(config_name, str):
            return {"error": "Invalid config_name: must be a non-empty string"}
        
        # Simulate loading default configurations
        default_configs = {
            "app_settings": {
                "debug_mode": False,
                "log_level": "INFO",
                "max_connections": 100,
                "timeout_seconds": 30,
                "enable_caching": True
            },
            "database_settings": {
                "host": "localhost",
                "port": 5432,
                "pool_size": 10,
                "ssl_enabled": True
            },
            "api_settings": {
                "rate_limit": 1000,
                "version": "v1",
                "cors_enabled": True
            }
        }
        
        if config_name in self.configurations:
            config = self.configurations[config_name]
        elif config_name in default_configs:
            config = {
                "name": config_name,
                "values": default_configs[config_name].copy(),
                "loaded_at": time.time(),
                "modified": False
            }
            self.configurations[config_name] = config
        else:
            return {"error": f"Configuration not found: {config_name}"}
        
        return {
            "success": True,
            "config_name": config_name,
            "values": config["values"],
            "loaded_at": config["loaded_at"],
            "modified": config["modified"]
        }
    
    def get_configuration_value(self, config_name: str, key: str) -> dict:
        """
        Get a specific key from a configuration.
        
        Args:
            config_name: Configuration name.
            key: The property key.
            
        Returns:
            dict: The key value or error.
        """
        if not config_name or not isinstance(config_name, str):
            return {"error": "Invalid config_name: must be a non-empty string"}
        
        if not key or not isinstance(key, str):
            return {"error": "Invalid key: must be a non-empty string"}
        
        if config_name not in self.configurations:
            # Try to load it first
            load_result = self.load_configuration(config_name)
            if "error" in load_result:
                return load_result
        
        config = self.configurations[config_name]
        
        if key not in config["values"]:
            return {"error": f"Key '{key}' not found in configuration '{config_name}'"}
        
        return {
            "success": True,
            "config_name": config_name,
            "key": key,
            "value": config["values"][key]
        }
    
    def update_configuration_value(self, config_name: str, key: str, value: Any) -> dict:
        """
        Update a specific key in a configuration.
        
        Args:
            config_name: Configuration name.
            key: The property key.
            value: The updated value.
            
        Returns:
            dict: Update confirmation or error.
        """
        if not config_name or not isinstance(config_name, str):
            return {"error": "Invalid config_name: must be a non-empty string"}
        
        if not key or not isinstance(key, str):
            return {"error": "Invalid key: must be a non-empty string"}
        
        if config_name not in self.configurations:
            return {"error": f"Configuration not loaded: {config_name}"}
        
        config = self.configurations[config_name]
        old_value = config["values"].get(key)
        config["values"][key] = value
        config["modified"] = True
        config["modified_at"] = time.time()
        
        return {
            "success": True,
            "config_name": config_name,
            "key": key,
            "old_value": old_value,
            "new_value": value,
            "modified_at": config["modified_at"]
        }
    
    def validate_configuration(self, config_name: str) -> dict:
        """
        Validate a configuration structure.
        
        Args:
            config_name: Configuration name.
            
        Returns:
            dict: Validation results or error.
        """
        if not config_name or not isinstance(config_name, str):
            return {"error": "Invalid config_name: must be a non-empty string"}
        
        if config_name not in self.configurations:
            return {"error": f"Configuration not loaded: {config_name}"}
        
        config = self.configurations[config_name]
        validation_errors = []
        
        # Perform basic validation based on config type
        if config_name == "app_settings":
            if "max_connections" in config["values"] and config["values"]["max_connections"] <= 0:
                validation_errors.append("max_connections must be positive")
            if "timeout_seconds" in config["values"] and config["values"]["timeout_seconds"] <= 0:
                validation_errors.append("timeout_seconds must be positive")
        elif config_name == "database_settings":
            if "port" in config["values"] and not (0 < config["values"]["port"] < 65536):
                validation_errors.append("port must be between 1 and 65535")
            if "pool_size" in config["values"] and config["values"]["pool_size"] <= 0:
                validation_errors.append("pool_size must be positive")
        
        is_valid = len(validation_errors) == 0
        
        return {
            "success": True,
            "config_name": config_name,
            "is_valid": is_valid,
            "validation_errors": validation_errors,
            "validated_at": time.time()
        }
    
    def reload_configuration(self, config_name: str) -> dict:
        """
        Reload a configuration from defaults, discarding local modifications.
        
        Args:
            config_name: Configuration name.
            
        Returns:
            dict: Reload confirmation or error.
        """
        if not config_name or not isinstance(config_name, str):
            return {"error": "Invalid config_name: must be a non-empty string"}
        
        if config_name in self.configurations:
            del self.configurations[config_name]
        
        load_result = self.load_configuration(config_name)
        if "error" in load_result:
            return load_result
        
        return {
            "success": True,
            "config_name": config_name,
            "reloaded": True,
            "reloaded_at": time.time(),
            "values": load_result["values"]
        }


# Test cases for the environment
__TEST_CASES__ = [
    {
        "name": "Health Check Workflow - Check and Refresh Service Health",
        "steps": [
            {"tool_call": "get_service_health_status(service_name='utile_space')", "expect_success": True},
            {"tool_call": "is_service_health_check_fresh(service_name='utile_space')", "expect_success": True},
            {"tool_call": "trigger_service_health_check(service_name='utile_space')", "expect_success": True},
            {"tool_call": "get_service_health_status(service_name='invalid_service')", "expect_success": False}
        ]
    },
    {
        "name": "Product Cache Workflow - Cache and Retrieve Product",
        "steps": [
            {"tool_call": "get_external_service_connection_status(service_id='product_database')", "expect_success": True},
            {"tool_call": "cache_product_data(product_id='99999', name='Test Product', price=29.99)", "expect_success": True},
            {"tool_call": "get_cached_product_info(product_id='99999')", "expect_success": True},
            {"tool_call": "invalidate_stale_product_cache(product_id='99999', max_age_seconds=3600)", "expect_success": True}
        ]
    },
    {
        "name": "Session Management Workflow - Create and Manage User Session",
        "steps": [
            {"tool_call": "create_user_session(user_id='user-test-001', session_data={'role': 'admin', 'permissions': ['read', 'write']})", "expect_success": True},
            {"tool_call": "get_user_session(user_id='user-test-001')", "expect_success": True},
            {"tool_call": "update_user_session(user_id='user-test-001', updates={'last_action': 'login'})", "expect_success": True},
            {"tool_call": "is_user_session_valid(user_id='user-test-001')", "expect_success": True},
            {"tool_call": "invalidate_user_session(user_id='user-test-001')", "expect_success": True}
        ]
    },
    {
        "name": "Rate Limiting Workflow - Track and Check Request Limits",
        "steps": [
            {"tool_call": "initialize_rate_limit_bucket(client_id='client-001', max_requests=100, window_seconds=60)", "expect_success": True},
            {"tool_call": "record_client_request(client_id='client-001')", "expect_success": True},
            {"tool_call": "get_rate_limit_status(client_id='client-001')", "expect_success": True},
            {"tool_call": "is_client_rate_limited(client_id='client-001')", "expect_success": True},
            {"tool_call": "reset_rate_limit_bucket(client_id='client-001')", "expect_success": True}
        ]
    },
    {
        "name": "Configuration Management Workflow - Load and Update Config",
        "steps": [
            {"tool_call": "load_configuration(config_name='app_settings')", "expect_success": True},
            {"tool_call": "get_configuration_value(config_name='app_settings', key='debug_mode')", "expect_success": True},
            {"tool_call": "update_configuration_value(config_name='app_settings', key='debug_mode', value=True)", "expect_success": True},
            {"tool_call": "validate_configuration(config_name='app_settings')", "expect_success": True},
            {"tool_call": "reload_configuration(config_name='app_settings')", "expect_success": True}
        ]
    }
]