"""
Automotive Service and Repair Management System

An automotive service and repair management system is a stateful software platform 
used by service centers to manage vehicle maintenance, repairs, and customer records.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Default initial state with sample data for all entities
DEFAULT_STATE = {
    "vehicles": {
        "1HGBH41JXMN109186": {
            "vin": "1HGBH41JXMN109186",
            "make": "Honda",
            "model": "Accord",
            "year": 2021,
            "current_mileage": 45000,
            "owner_customer_id": "CUST001"
        },
        "2T1BURHE5JC123456": {
            "vin": "2T1BURHE5JC123456",
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "current_mileage": 62000,
            "owner_customer_id": "CUST002"
        },
        "3FAHP0HA7CR987654": {
            "vin": "3FAHP0HA7CR987654",
            "make": "Ford",
            "model": "Fusion",
            "year": 2019,
            "current_mileage": 78000,
            "owner_customer_id": "CUST003"
        }
    },
    "service_records": {
        "SR001": {
            "record_id": "SR001",
            "vin": "1HGBH41JXMN109186",
            "service_date": "2024-01-15",
            "service_type": "oil_change",
            "mileage_at_service": 40000,
            "description": "Regular oil change with synthetic oil"
        },
        "SR002": {
            "record_id": "SR002",
            "vin": "2T1BURHE5JC123456",
            "service_date": "2024-02-20",
            "service_type": "tire_rotation",
            "mileage_at_service": 58000,
            "description": "Tire rotation and balance"
        },
        "SR003": {
            "record_id": "SR003",
            "vin": "3FAHP0HA7CR987654",
            "service_date": "2023-12-10",
            "service_type": "brake_inspection",
            "mileage_at_service": 70000,
            "description": "Brake pad inspection and fluid check"
        }
    },
    "maintenance_schedules": {
        "Honda_Accord_2021_oil_change": {
            "make": "Honda",
            "model": "Accord",
            "year": 2021,
            "service_type": "oil_change",
            "recommended_interval_km": 8000,
            "recommended_interval_days": 180
        },
        "Toyota_Camry_2020_oil_change": {
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "service_type": "oil_change",
            "recommended_interval_km": 10000,
            "recommended_interval_days": 180
        },
        "Ford_Fusion_2019_brake_inspection": {
            "make": "Ford",
            "model": "Fusion",
            "year": 2019,
            "service_type": "brake_inspection",
            "recommended_interval_km": 20000,
            "recommended_interval_days": 365
        },
        "Honda_Accord_2021_tire_rotation": {
            "make": "Honda",
            "model": "Accord",
            "year": 2021,
            "service_type": "tire_rotation",
            "recommended_interval_km": 12000,
            "recommended_interval_days": 180
        }
    },
    "repair_estimates": {
        "EST001": {
            "estimate_id": "EST001",
            "vin": "1HGBH41JXMN109186",
            "creation_date": "2024-03-01",
            "status": "draft",
            "total_estimated_cost": 0.0,
            "labor_cost": 0.0,
            "parts_cost": 0.0,
            "damage_assessment_ids": ["DA001"],
            "linked_part_ids": []
        },
        "EST002": {
            "estimate_id": "EST002",
            "vin": "2T1BURHE5JC123456",
            "creation_date": "2024-03-05",
            "status": "finalized",
            "total_estimated_cost": 850.0,
            "labor_cost": 500.0,
            "parts_cost": 350.0,
            "damage_assessment_ids": ["DA002"],
            "linked_part_ids": []
        },
        "EST003": {
            "estimate_id": "EST003",
            "vin": "3FAHP0HA7CR987654",
            "creation_date": "2024-03-10",
            "status": "approved",
            "total_estimated_cost": 1200.0,
            "labor_cost": 700.0,
            "parts_cost": 500.0,
            "damage_assessment_ids": ["DA003"],
            "linked_part_ids": []
        }
    },
    "damage_assessments": {
        "DA001": {
            "assessment_id": "DA001",
            "estimate_id": "EST001",
            "affected_component": "front_bumper",
            "damage_severity": "minor",
            "repair_action": "repair",
            "estimated_labor_hours": 2.0
        },
        "DA002": {
            "assessment_id": "DA002",
            "estimate_id": "EST002",
            "affected_component": "brake_pads",
            "damage_severity": "moderate",
            "repair_action": "replace",
            "estimated_labor_hours": 3.0
        },
        "DA003": {
            "assessment_id": "DA003",
            "estimate_id": "EST003",
            "affected_component": "transmission",
            "damage_severity": "severe",
            "repair_action": "rebuild",
            "estimated_labor_hours": 8.0
        }
    },
    "repair_catalog": {
        "front_bumper_repair": {
            "component_name": "front_bumper",
            "repair_action": "repair",
            "base_labor_hours": 2.0,
            "required_part_id": "PART001",
            "labor_rate_multiplier": 1.0
        },
        "front_bumper_replace": {
            "component_name": "front_bumper",
            "repair_action": "replace",
            "base_labor_hours": 3.5,
            "required_part_id": "PART001",
            "labor_rate_multiplier": 1.2
        },
        "brake_pads_replace": {
            "component_name": "brake_pads",
            "repair_action": "replace",
            "base_labor_hours": 2.5,
            "required_part_id": "PART002",
            "labor_rate_multiplier": 1.0
        },
        "transmission_rebuild": {
            "component_name": "transmission",
            "repair_action": "rebuild",
            "base_labor_hours": 10.0,
            "required_part_id": "PART003",
            "labor_rate_multiplier": 1.5
        }
    },
    "parts": {
        "PART001": {
            "part_id": "PART001",
            "part_name": "Front Bumper Cover",
            "current_stock": 5,
            "unit_cost": 250.0,
            "compatible_vehicles": ["Honda_Accord", "Toyota_Camry"],
            "available_on_order": True
        },
        "PART002": {
            "part_id": "PART002",
            "part_name": "Brake Pad Set",
            "current_stock": 20,
            "unit_cost": 85.0,
            "compatible_vehicles": ["Honda_Accord", "Toyota_Camry", "Ford_Fusion"],
            "available_on_order": True
        },
        "PART003": {
            "part_id": "PART003",
            "part_name": "Transmission Rebuild Kit",
            "current_stock": 2,
            "unit_cost": 450.0,
            "compatible_vehicles": ["Ford_Fusion"],
            "available_on_order": True
        },
        "PART004": {
            "part_id": "PART004",
            "part_name": "Oil Filter",
            "current_stock": 0,
            "unit_cost": 15.0,
            "compatible_vehicles": ["Honda_Accord", "Toyota_Camry", "Ford_Fusion"],
            "available_on_order": False
        }
    },
    "customers": {
        "CUST001": {
            "customer_id": "CUST001",
            "name": "John Smith",
            "contact_info": {"phone": "555-0101", "email": "john.smith@email.com"},
            "owned_vehicles": ["1HGBH41JXMN109186"]
        },
        "CUST002": {
            "customer_id": "CUST002",
            "name": "Sarah Johnson",
            "contact_info": {"phone": "555-0102", "email": "sarah.j@email.com"},
            "owned_vehicles": ["2T1BURHE5JC123456"]
        },
        "CUST003": {
            "customer_id": "CUST003",
            "name": "Michael Brown",
            "contact_info": {"phone": "555-0103", "email": "m.brown@email.com"},
            "owned_vehicles": ["3FAHP0HA7CR987654"]
        }
    },
    "repair_orders": {},
    "invoices": {},
    "base_labor_rate": 75.0,
    "next_record_id": 4,
    "next_estimate_id": 4,
    "next_assessment_id": 4,
    "next_repair_order_id": 1,
    "next_invoice_id": 1,
    "current_timestamp": "2024-03-15T10:00:00",
    "audit_log": []
}


class AutomotiveServiceRepairSystem:
    """
    Automotive Service and Repair Management System API.
    
    A stateful platform for managing vehicle maintenance, repairs, customer records,
    service scheduling, diagnostic logging, cost estimation, and work order generation.
    """
    
    def __init__(self):
        """
        Initialize the Automotive Service and Repair Management System.
        
        Declares all state attributes with type hints and sets the API description.
        """
        self.vehicles: Dict[str, Dict[str, Any]] = {}
        self.service_records: Dict[str, Dict[str, Any]] = {}
        self.maintenance_schedules: Dict[str, Dict[str, Any]] = {}
        self.repair_estimates: Dict[str, Dict[str, Any]] = {}
        self.damage_assessments: Dict[str, Dict[str, Any]] = {}
        self.repair_catalog: Dict[str, Dict[str, Any]] = {}
        self.parts: Dict[str, Dict[str, Any]] = {}
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.repair_orders: Dict[str, Dict[str, Any]] = {}
        self.invoices: Dict[str, Dict[str, Any]] = {}
        self.base_labor_rate: float = 75.0
        self.next_record_id: int = 4
        self.next_estimate_id: int = 4
        self.next_assessment_id: int = 4
        self.next_repair_order_id: int = 1
        self.next_invoice_id: int = 1
        self.current_timestamp: str = "2024-03-15T10:00:00"
        self.audit_log: List[Dict[str, Any]] = []
        
        self._api_description = "Automotive service and repair management system for vehicle maintenance, repairs, and customer records."
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp string for operations.
        
        Returns:
            str: ISO format timestamp string.
        """
        return self.current_timestamp
    
    def _log_audit(self, action: str, details: Dict[str, Any]) -> None:
        """Add an audit log entry."""
        self.audit_log.append({
            "timestamp": self._timestamp(),
            "action": action,
            "details": deepcopy(details)
        })
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        If scenario is empty or None, load DEFAULT_STATE.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for extended context scenarios (unused).
        """
        if not scenario:
            scenario = {}
        # Merge scenario with DEFAULT_STATE (scenario overrides)
        merged = deepcopy(DEFAULT_STATE)
        for key in merged:
            if key in scenario:
                merged[key] = deepcopy(scenario[key])
        for key in merged:
            setattr(self, key, merged[key])
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Return the current environment state as a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables
                including vehicles, service_records, maintenance_schedules,
                repair_estimates, damage_assessments, repair_catalog, parts,
                customers, repair_orders, invoices, base_labor_rate, ID counters,
                and audit_log.
        """
        return {
            "vehicles": deepcopy(self.vehicles),
            "service_records": deepcopy(self.service_records),
            "maintenance_schedules": deepcopy(self.maintenance_schedules),
            "repair_estimates": deepcopy(self.repair_estimates),
            "damage_assessments": deepcopy(self.damage_assessments),
            "repair_catalog": deepcopy(self.repair_catalog),
            "parts": deepcopy(self.parts),
            "customers": deepcopy(self.customers),
            "repair_orders": deepcopy(self.repair_orders),
            "invoices": deepcopy(self.invoices),
            "base_labor_rate": self.base_labor_rate,
            "next_record_id": self.next_record_id,
            "next_estimate_id": self.next_estimate_id,
            "next_assessment_id": self.next_assessment_id,
            "next_repair_order_id": self.next_repair_order_id,
            "next_invoice_id": self.next_invoice_id,
            "current_timestamp": self.current_timestamp,
            "audit_log": deepcopy(self.audit_log)
        }
    
    # ===================== QUERY OPERATIONS =====================
    
    def get_vehicle_by_vin(self, vin: str) -> Dict[str, Any]:
        """
        Retrieve full vehicle details using VIN.
        
        Args:
            vin: The Vehicle Identification Number to look up.
            
        Returns:
            Dict[str, Any]: Vehicle details including make, model, year, mileage,
                and owner, or an error dictionary if not found.
        """
        if not vin:
            return {"success": False, "error": "VIN is required"}
        
        if vin not in self.vehicles:
            return {"success": False, "error": f"Vehicle with VIN '{vin}' not found"}
        
        return {"success": True, "data": deepcopy(self.vehicles[vin])}
    
    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer information by customer_id.
        
        Args:
            customer_id: The unique identifier for the customer.
            
        Returns:
            Dict[str, Any]: Customer information including name, contact info,
                and owned vehicles, or an error dictionary if not found.
        """
        if not customer_id:
            return {"success": False, "error": "Customer ID is required"}
        
        if customer_id not in self.customers:
            return {"success": False, "error": f"Customer with ID '{customer_id}' not found"}
        
        return {"success": True, "data": deepcopy(self.customers[customer_id])}
    
    def get_last_service_record(self, vin: str) -> Dict[str, Any]:
        """
        Retrieve the most recent service record for a vehicle.
        
        Args:
            vin: The Vehicle Identification Number.
            
        Returns:
            Dict[str, Any]: The most recent service record or an error dictionary.
        """
        if not vin:
            return {"success": False, "error": "VIN is required"}
        
        if vin not in self.vehicles:
            return {"success": False, "error": f"Vehicle with VIN '{vin}' not found"}
        
        vehicle_records = [
            record for record in self.service_records.values()
            if record["vin"] == vin
        ]
        
        if not vehicle_records:
            return {"success": False, "error": f"No service records found for VIN '{vin}'"}
        
        latest_record = max(vehicle_records, key=lambda x: x["service_date"])
        return {"success": True, "data": deepcopy(latest_record)}
    
    def list_service_history(self, vin: str) -> Dict[str, Any]:
        """
        Retrieve all past service records for a given vehicle.
        
        Args:
            vin: The Vehicle Identification Number.
            
        Returns:
            Dict[str, Any]: Dictionary with list of service records sorted by date,
                or an error dictionary if vehicle not found.
        """
        if not vin:
            return {"success": False, "error": "VIN is required"}
        
        if vin not in self.vehicles:
            return {"success": False, "error": f"Vehicle with VIN '{vin}' not found"}
        
        vehicle_records = [
            deepcopy(record) for record in self.service_records.values()
            if record["vin"] == vin
        ]
        
        vehicle_records.sort(key=lambda x: x["service_date"], reverse=True)
        
        return {
            "success": True,
            "vin": vin,
            "service_history": vehicle_records,
            "total_records": len(vehicle_records)
        }
    
    def get_maintenance_schedule(self, make: str, model: str, year: int) -> Dict[str, Any]:
        """
        Retrieve recommended service intervals for a vehicle.
        
        Args:
            make: Vehicle manufacturer.
            model: Vehicle model name.
            year: Vehicle model year.
            
        Returns:
            Dict[str, Any]: Dictionary containing all maintenance schedules
                for the specified vehicle, or an error if none found.
        """
        if not make or not model or not year:
            return {"success": False, "error": "Make, model, and year are all required"}
        
        schedules = []
        for schedule in self.maintenance_schedules.values():
            if (schedule["make"] == make and 
                schedule["model"] == model and 
                schedule["year"] == year):
                schedules.append(deepcopy(schedule))
        
        if not schedules:
            return {"success": False, "error": f"No maintenance schedule found for {year} {make} {model}"}
        
        return {
            "success": True,
            "make": make,
            "model": model,
            "year": year,
            "schedules": schedules
        }
    
    def check_maintenance_due(self, vin: str, service_type: str) -> Dict[str, Any]:
        """
        Determine whether a vehicle is due for maintenance.
        
        Args:
            vin: The Vehicle Identification Number.
            service_type: Type of maintenance service to check.
            
        Returns:
            Dict[str, Any]: Dictionary indicating if maintenance is due,
                with details on mileage and time since last service.
        """
        if not vin or not service_type:
            return {"success": False, "error": "VIN and service_type are required"}
        
        if vin not in self.vehicles:
            return {"success": False, "error": f"Vehicle with VIN '{vin}' not found"}
        
        vehicle = self.vehicles[vin]
        
        # Find maintenance schedule
        schedule = None
        for sched in self.maintenance_schedules.values():
            if (sched["make"] == vehicle["make"] and
                sched["model"] == vehicle["model"] and
                sched["year"] == vehicle["year"] and
                sched["service_type"] == service_type):
                schedule = sched
                break
        
        if not schedule:
            return {"success": False, "error": f"No maintenance schedule found for {service_type} on this vehicle"}
        
        # Find last service of this type
        last_service = None
        for record in self.service_records.values():
            if record["vin"] == vin and record["service_type"] == service_type:
                if last_service is None or record["service_date"] > last_service["service_date"]:
                    last_service = record
        
        current_mileage = vehicle["current_mileage"]
        current_date = self._timestamp().split("T")[0]
        
        if last_service is None:
            return {
                "success": True,
                "vin": vin,
                "service_type": service_type,
                "is_due": True,
                "reason": "No previous service record found",
                "current_mileage": current_mileage,
                "recommended_interval_km": schedule["recommended_interval_km"],
                "recommended_interval_days": schedule["recommended_interval_days"]
            }
        
        mileage_since_service = current_mileage - last_service["mileage_at_service"]
        
        # Calculate days since service
        last_date = datetime.strptime(last_service["service_date"], "%Y-%m-%d")
        current = datetime.strptime(current_date, "%Y-%m-%d")
        days_since_service = (current - last_date).days
        
        mileage_due = mileage_since_service >= schedule["recommended_interval_km"]
        time_due = days_since_service >= schedule["recommended_interval_days"]
        
        return {
            "success": True,
            "vin": vin,
            "service_type": service_type,
            "is_due": mileage_due or time_due,
            "mileage_since_last_service": mileage_since_service,
            "days_since_last_service": days_since_service,
            "recommended_interval_km": schedule["recommended_interval_km"],
            "recommended_interval_days": schedule["recommended_interval_days"],
            "last_service_date": last_service["service_date"],
            "last_service_mileage": last_service["mileage_at_service"]
        }
    
    def get_repair_catalog_entry(self, component_name: str, repair_action: str) -> Dict[str, Any]:
        """
        Retrieve standard repair data for a component and action.
        
        Args:
            component_name: The name of the affected component.
            repair_action: The type of repair action (repair, replace, rebuild).
            
        Returns:
            Dict[str, Any]: Catalog entry with labor hours, part, and multiplier,
                or an error dictionary if not found.
        """
        if not component_name or not repair_action:
            return {"success": False, "error": "Component name and repair action are required"}
        
        catalog_key = f"{component_name}_{repair_action}"
        
        if catalog_key not in self.repair_catalog:
            return {"success": False, "error": f"No catalog entry found for {component_name} - {repair_action}"}
        
        return {"success": True, "data": deepcopy(self.repair_catalog[catalog_key])}
    
    def get_part_by_id(self, part_id: str) -> Dict[str, Any]:
        """
        Retrieve part details including name, stock level, and unit cost.
        
        Args:
            part_id: The unique identifier for the part.
            
        Returns:
            Dict[str, Any]: Part details or an error dictionary if not found.
        """
        if not part_id:
            return {"success": False, "error": "Part ID is required"}
        
        if part_id not in self.parts:
            return {"success": False, "error": f"Part with ID '{part_id}' not found"}
        
        return {"success": True, "data": deepcopy(self.parts[part_id])}
    
    def check_part_availability(self, part_id: str) -> Dict[str, Any]:
        """
        Verify if a part is in stock or available on order.
        
        Args:
            part_id: The unique identifier for the part.
            
        Returns:
            Dict[str, Any]: Availability status including stock level and
                order availability, or an error if part not found.
        """
        if not part_id:
            return {"success": False, "error": "Part ID is required"}
        
        if part_id not in self.parts:
            return {"success": False, "error": f"Part with ID '{part_id}' not found"}
        
        part = self.parts[part_id]
        in_stock = part["current_stock"] > 0
        available_on_order = part.get("available_on_order", False)
        
        return {
            "success": True,
            "part_id": part_id,
            "part_name": part["part_name"],
            "in_stock": in_stock,
            "current_stock": part["current_stock"],
            "available_on_order": available_on_order,
            "can_include_in_estimate": in_stock or available_on_order
        }
    
    def get_existing_estimate(self, estimate_id: str) -> Dict[str, Any]:
        """
        Retrieve an existing repair estimate by estimate_id.
        
        Args:
            estimate_id: The unique identifier for the estimate.
            
        Returns:
            Dict[str, Any]: Estimate details or an error dictionary if not found.
        """
        if not estimate_id:
            return {"success": False, "error": "Estimate ID is required"}
        
        if estimate_id not in self.repair_estimates:
            return {"success": False, "error": f"Estimate with ID '{estimate_id}' not found"}
        
        return {"success": True, "data": deepcopy(self.repair_estimates[estimate_id])}
    
    def get_damage_assessments_from_estimate(self, estimate_id: str) -> Dict[str, Any]:
        """
        List all damage assessments associated with a repair estimate.
        
        Args:
            estimate_id: The unique identifier for the estimate.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of damage assessments,
                or an error dictionary if estimate not found.
        """
        if not estimate_id:
            return {"success": False, "error": "Estimate ID is required"}
        
        if estimate_id not in self.repair_estimates:
            return {"success": False, "error": f"Estimate with ID '{estimate_id}' not found"}
        
        estimate = self.repair_estimates[estimate_id]
        assessments = []
        
        for assessment_id in estimate.get("damage_assessment_ids", []):
            if assessment_id in self.damage_assessments:
                assessments.append(deepcopy(self.damage_assessments[assessment_id]))
        
        return {
            "success": True,
            "estimate_id": estimate_id,
            "damage_assessments": assessments,
            "total_assessments": len(assessments)
        }
    
    # ===================== STATE CHANGE OPERATIONS =====================
    
    def schedule_maintenance_service(
        self, 
        vin: str, 
        service_type: str, 
        description: str,
        service_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new service record for a maintenance task.
        
        Constraint: Cannot schedule unless vehicle's current mileage and 
        last service date are known.
        
        Args:
            vin: The Vehicle Identification Number.
            service_type: Type of maintenance service.
            description: Description of the service performed.
            service_date: Date of service (defaults to current timestamp).
            
        Returns:
            Dict[str, Any]: Created service record or error dictionary.
        """
        if not vin or not service_type or not description:
            return {"success": False, "error": "VIN, service_type, and description are required"}
        
        # Check vehicle exists
        if vin not in self.vehicles:
            return {"success": False, "error": f"Vehicle with VIN '{vin}' not found"}
        
        vehicle = self.vehicles[vin]
        
        # Constraint: Must know current mileage
        if vehicle.get("current_mileage") is None:
            return {"success": False, "error": "Cannot schedule service: vehicle current mileage is unknown"}
        
        # Constraint: Must have valid maintenance schedule
        schedule_found = False
        for schedule in self.maintenance_schedules.values():
            if (schedule["make"] == vehicle["make"] and
                schedule["model"] == vehicle["model"] and
                schedule["year"] == vehicle["year"] and
                schedule["service_type"] == service_type):
                schedule_found = True
                break
        
        if not schedule_found:
            return {"success": False, "error": f"No valid maintenance schedule found for {service_type} on {vehicle['year']} {vehicle['make']} {vehicle['model']}"}
        
        # Create service record
        record_id = f"SR{self.next_record_id:03d}"
        self.next_record_id += 1
        
        if service_date is None:
            service_date = self._timestamp().split("T")[0]
        
        new_record = {
            "record_id": record_id,
            "vin": vin,
            "service_date": service_date,
            "service_type": service_type,
            "mileage_at_service": vehicle["current_mileage"],
            "description": description
        }
        
        self.service_records[record_id] = new_record
        
        self._log_audit("schedule_maintenance_service", {
            "record_id": record_id,
            "vin": vin,
            "service_type": service_type,
            "service_date": service_date
        })
        
        return {
            "success": True,
            "record_id": record_id,
            "service_record": deepcopy(new_record)
        }
    
    def create_repair_estimate(self, vin: str) -> Dict[str, Any]:
        """
        Initialize a new repair estimate for a vehicle.
        
        Args:
            vin: The Vehicle Identification Number.
            
        Returns:
            Dict[str, Any]: Created estimate with draft status or error dictionary.
        """
        if not vin:
            return {"success": False, "error": "VIN is required"}
        
        if vin not in self.vehicles:
            return {"success": False, "error": f"Vehicle with VIN '{vin}' not found"}
        
        estimate_id = f"EST{self.next_estimate_id:03d}"
        self.next_estimate_id += 1
        
        new_estimate = {
            "estimate_id": estimate_id,
            "vin": vin,
            "creation_date": self._timestamp().split("T")[0],
            "status": "draft",
            "total_estimated_cost": 0.0,
            "labor_cost": 0.0,
            "parts_cost": 0.0,
            "damage_assessment_ids": [],
            "linked_part_ids": []
        }
        
        self.repair_estimates[estimate_id] = new_estimate
        
        self._log_audit("create_repair_estimate", {
            "estimate_id": estimate_id,
            "vin": vin
        })
        
        return {
            "success": True,
            "estimate_id": estimate_id,
            "estimate": deepcopy(new_estimate)
        }
    
    def add_damage_assessment(
        self,
        estimate_id: str,
        affected_component: str,
        damage_severity: str,
        repair_action: str,
        estimated_labor_hours: float,
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Add a validated damage assessment to a repair estimate.
        
        Constraint: Must reference valid component and severity in RepairCatalog.
        
        Args:
            estimate_id: The estimate to add assessment to.
            affected_component: The damaged component name.
            damage_severity: Severity level (minor, moderate, severe).
            repair_action: Required action (repair, replace, rebuild).
            estimated_labor_hours: Estimated hours for the repair.
            notes: Optional notes about the damage.
            
        Returns:
            Dict[str, Any]: Created assessment or error dictionary.
        """
        if not all([estimate_id, affected_component, damage_severity, repair_action]):
            return {"success": False, "error": "Estimate ID, component, severity, and action are required"}
        
        if estimate_id not in self.repair_estimates:
            return {"success": False, "error": f"Estimate with ID '{estimate_id}' not found"}
        
        # Validate against repair catalog
        catalog_key = f"{affected_component}_{repair_action}"
        if catalog_key not in self.repair_catalog:
            return {"success": False, "error": f"Invalid component/action: {affected_component} - {repair_action}. Must be in repair catalog."}
        
        estimate = self.repair_estimates[estimate_id]
        
        assessment_id = f"DA{self.next_assessment_id:03d}"
        self.next_assessment_id += 1
        
        assessment = {
            "assessment_id": assessment_id,
            "estimate_id": estimate_id,
            "affected_component": affected_component,
            "damage_severity": damage_severity,
            "repair_action": repair_action,
            "estimated_labor_hours": estimated_labor_hours,
            "notes": notes,
            "created_at": self._timestamp()
        }
        
        # Store in global damage_assessments dict
        self.damage_assessments[assessment_id] = assessment
        
        # Add ID to estimate's damage_assessment_ids list
        estimate["damage_assessment_ids"].append(assessment_id)
        
        self._log_audit("add_damage_assessment", {
            "assessment_id": assessment_id,
            "estimate_id": estimate_id,
            "component": affected_component,
            "action": repair_action
        })
        
        return {
            "success": True,
            "assessment_id": assessment_id,
            "assessment": deepcopy(assessment)
        }
    
    def calculate_repair_cost(
        self,
        estimate_id: str,
        labor_rate: float = 75.0,
        parts_markup: float = 1.25
    ) -> Dict[str, Any]:
        """
        Calculate total repair cost for an estimate using repair catalog and parts inventory.
        
        Args:
            estimate_id: The estimate to calculate costs for.
            labor_rate: Hourly labor rate in dollars.
            parts_markup: Markup multiplier for parts.
            
        Returns:
            Dict[str, Any]: Cost breakdown or error dictionary.
        """
        if estimate_id not in self.repair_estimates:
            return {"success": False, "error": f"Estimate with ID '{estimate_id}' not found"}
        
        estimate = self.repair_estimates[estimate_id]
        assessment_ids = estimate.get("damage_assessment_ids", [])
        
        total_labor_hours = 0.0
        total_parts_cost = 0.0
        labor_cost = 0.0
        linked_part_ids = []
        part_availability_warnings = []
        
        for aid in assessment_ids:
            if aid not in self.damage_assessments:
                continue
            assessment = self.damage_assessments[aid]
            component = assessment["affected_component"]
            action = assessment["repair_action"]
            catalog_key = f"{component}_{action}"
            
            # Use catalog data if available
            if catalog_key in self.repair_catalog:
                entry = self.repair_catalog[catalog_key]
                base_hours = entry["base_labor_hours"]
                multiplier = entry["labor_rate_multiplier"]
                # Use assessment's labor hours if provided, else catalog base
                hours = assessment.get("estimated_labor_hours", base_hours)
                total_labor_hours += hours
                labor_cost += hours * labor_rate * multiplier
                
                # Handle parts
                required_part_id = entry.get("required_part_id")
                if required_part_id and required_part_id in self.parts:
                    part = self.parts[required_part_id]
                    part_cost = part["unit_cost"] * parts_markup
                    total_parts_cost += part_cost
                    if required_part_id not in linked_part_ids:
                        linked_part_ids.append(required_part_id)
                    # Check stock availability
                    if part["current_stock"] <= 0:
                        part_availability_warnings.append(
                            f"Part {required_part_id} ({part['part_name']}) is out of stock"
                        )
            else:
                # Fallback to raw assessment hours
                hours = assessment.get("estimated_labor_hours", 0)
                total_labor_hours += hours
                labor_cost += hours * labor_rate
        
        # Total cost
        total_cost = labor_cost + total_parts_cost
        
        # Update estimate with calculated costs
        estimate["labor_cost"] = round(labor_cost, 2)
        estimate["parts_cost"] = round(total_parts_cost, 2)
        estimate["total_estimated_cost"] = round(total_cost, 2)
        # Also update linked_part_ids (preserve existing and add new)
        existing_linked = set(estimate.get("linked_part_ids", []))
        existing_linked.update(linked_part_ids)
        estimate["linked_part_ids"] = list(existing_linked)
        
        self._log_audit("calculate_repair_cost", {
            "estimate_id": estimate_id,
            "labor_cost": labor_cost,
            "parts_cost": total_parts_cost,
            "total_cost": total_cost
        })
        
        result = {
            "success": True,
            "estimate_id": estimate_id,
            "total_labor_hours": total_labor_hours,
            "labor_rate": labor_rate,
            "labor_cost": round(labor_cost, 2),
            "parts_cost": round(total_parts_cost, 2),
            "parts_markup": parts_markup,
            "total_cost": round(total_cost, 2)
        }
        if part_availability_warnings:
            result["warnings"] = part_availability_warnings
        
        return result
    
    def update_estimate_status(
        self,
        estimate_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a repair estimate.
        
        Valid statuses: draft, pending, approved, finalized, in_progress, completed, cancelled.
        
        Args:
            estimate_id: The estimate to update.
            status: New status.
            notes: Optional status update notes.
            
        Returns:
            Dict[str, Any]: Updated estimate or error dictionary.
        """
        valid_statuses = ["draft", "pending", "approved", "finalized", "in_progress", "completed", "cancelled"]
        
        if status not in valid_statuses:
            return {"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}
        
        if estimate_id not in self.repair_estimates:
            return {"success": False, "error": f"Estimate with ID '{estimate_id}' not found"}
        
        estimate = self.repair_estimates[estimate_id]
        old_status = estimate["status"]
        estimate["status"] = status
        estimate["updated_at"] = self._timestamp()
        
        if notes:
            if "status_history" not in estimate:
                estimate["status_history"] = []
            estimate["status_history"].append({
                "status": status,
                "notes": notes,
                "timestamp": self._timestamp()
            })
        
        self._log_audit("update_estimate_status", {
            "estimate_id": estimate_id,
            "old_status": old_status,
            "new_status": status,
            "notes": notes
        })
        
        return {
            "success": True,
            "estimate_id": estimate_id,
            "status": status,
            "updated_at": estimate["updated_at"]
        }
    
    def get_estimate_summary(self, estimate_id: str) -> Dict[str, Any]:
        """
        Get a summary of a repair estimate.
        
        Args:
            estimate_id: The estimate to summarize.
            
        Returns:
            Dict[str, Any]: Estimate summary or error dictionary.
        """
        if estimate_id not in self.repair_estimates:
            return {"success": False, "error": f"Estimate with ID '{estimate_id}' not found"}
        
        estimate = self.repair_estimates[estimate_id]
        assessment_ids = estimate.get("damage_assessment_ids", [])
        
        # Get vehicle info from vehicles dict
        vin = estimate["vin"]
        if vin in self.vehicles:
            vehicle = self.vehicles[vin]
            vehicle_summary = f"{vehicle['year']} {vehicle['make']} {vehicle['model']}"
        else:
            vehicle_summary = "Unknown Unknown Unknown"
        
        assessments = []
        for aid in assessment_ids:
            if aid in self.damage_assessments:
                assessments.append(self.damage_assessments[aid]["affected_component"])
        
        return {
            "success": True,
            "estimate_id": estimate_id,
            "vehicle": vehicle_summary,
            "status": estimate.get("status", "draft"),
            "total_assessments": len(assessments),
            "components_affected": assessments,
            "created_at": estimate.get("creation_date"),
            "updated_at": estimate.get("updated_at"),
            "total_estimated_cost": estimate.get("total_estimated_cost", 0.0)
        }


__TEST_CASES__ = [
    {
        "name": "create_repair_estimate_success",
        "input": {
            "method": "create_repair_estimate",
            "args": {
                "vin": "1HGBH41JXMN109186"
            }
        },
        "expected_keys": ["success", "estimate_id", "estimate"]
    },
    {
        "name": "create_repair_estimate_missing_fields",
        "input": {
            "method": "create_repair_estimate",
            "args": {
                "vin": ""
            }
        },
        "expected_keys": ["success", "error"]
    },
    {
        "name": "add_damage_assessment_success",
        "input": {
            "method": "add_damage_assessment",
            "args": {
                "estimate_id": "__DYNAMIC_ESTIMATE_ID__",
                "affected_component": "front_bumper",
                "damage_severity": "moderate",
                "repair_action": "replace",
                "estimated_labor_hours": 3.5,
                "notes": "Crack on driver side"
            }
        },
        "expected_keys": ["success", "assessment_id", "assessment"]
    },
    {
        "name": "add_damage_assessment_invalid_estimate",
        "input": {
            "method": "add_damage_assessment",
            "args": {
                "estimate_id": "INVALID-ID",
                "affected_component": "Hood",
                "damage_severity": "minor",
                "repair_action": "repair",
                "estimated_labor_hours": 1.0
            }
        },
        "expected_keys": ["success", "error"]
    },
    {
        "name": "calculate_repair_cost_success",
        "input": {
            "method": "calculate_repair_cost",
            "args": {
                "estimate_id": "__DYNAMIC_ESTIMATE_ID__",
                "labor_rate": 85.0,
                "parts_markup": 1.3
            }
        },
        "expected_keys": ["success", "estimate_id", "total_labor_hours", "labor_rate", "labor_cost", "parts_cost", "total_cost"]
    },
    {
        "name": "update_estimate_status_success",
        "input": {
            "method": "update_estimate_status",
            "args": {
                "estimate_id": "__DYNAMIC_ESTIMATE_ID__",
                "status": "approved",
                "notes": "Customer approved the estimate"
            }
        },
        "expected_keys": ["success", "estimate_id", "status", "updated_at"]
    },
    {
        "name": "update_estimate_status_invalid",
        "input": {
            "method": "update_estimate_status",
            "args": {
                "estimate_id": "__DYNAMIC_ESTIMATE_ID__",
                "status": "invalid_status"
            }
        },
        "expected_keys": ["success", "error"]
    },
    {
        "name": "get_estimate_summary_success",
        "input": {
            "method": "get_estimate_summary",
            "args": {
                "estimate_id": "__DYNAMIC_ESTIMATE_ID__"
            }
        },
        "expected_keys": ["success", "estimate_id", "vehicle", "status", "total_assessments", "components_affected"]
    },
    {
        "name": "get_estimate_summary_not_found",
        "input": {
            "method": "get_estimate_summary",
            "args": {
                "estimate_id": "NONEXISTENT-123"
            }
        },
        "expected_keys": ["success", "error"]
    }
]