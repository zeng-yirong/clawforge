"""
Motor Vehicle Registration Database Environment API

A stateful system used by government transportation authorities to manage
information about registered vehicles including license plates, VINs, owner
details, registration expiry, and insurance status.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

DEFAULT_STATE: Dict[str, Any] = {
    "vehicle_registrations": {
        "ABC-1234": {
            "registration_number": "ABC-1234",
            "VIN": "1HGBH41JXMN109186",
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "color": "Silver",
            "vehicle_type": "Sedan",
            "registration_expiry_date": "2025-12-31",
            "insurance_status": "active",
            "current_owner_id": "OWN001"
        },
        "XYZ-5678": {
            "registration_number": "XYZ-5678",
            "VIN": "2T1BURHE5JC123456",
            "make": "Toyota",
            "model": "Camry",
            "year": 2021,
            "color": "Blue",
            "vehicle_type": "Sedan",
            "registration_expiry_date": "2025-06-30",
            "insurance_status": "active",
            "current_owner_id": "OWN002"
        },
        "DEF-9012": {
            "registration_number": "DEF-9012",
            "VIN": "3FAHP0HA7CR123789",
            "make": "Ford",
            "model": "F-150",
            "year": 2019,
            "color": "Red",
            "vehicle_type": "Truck",
            "registration_expiry_date": "2024-03-15",
            "insurance_status": "inactive",
            "current_owner_id": "OWN003"
        }
    },
    "owners": {
        "OWN001": {
            "owner_id": "OWN001",
            "name": "John Smith",
            "address": "123 Main Street, Springfield, IL 62701",
            "driver_license_number": "S123-4567-8901",
            "phone_number": "555-123-4567",
            "email": "john.smith@email.com"
        },
        "OWN002": {
            "owner_id": "OWN002",
            "name": "Sarah Johnson",
            "address": "456 Oak Avenue, Chicago, IL 60601",
            "driver_license_number": "J987-6543-2109",
            "phone_number": "555-987-6543",
            "email": "sarah.johnson@email.com"
        },
        "OWN003": {
            "owner_id": "OWN003",
            "name": "Michael Davis",
            "address": "789 Pine Road, Naperville, IL 60540",
            "driver_license_number": "D456-7890-1234",
            "phone_number": "555-456-7890",
            "email": "michael.davis@email.com"
        }
    },
    "vehicle_history": {
        "1HGBH41JXMN109186": [
            {
                "VIN": "1HGBH41JXMN109186",
                "registration_number": "ABC-1234",
                "previous_owners": [],
                "transfer_date": "2020-01-15",
                "reason_for_transfer": "Initial registration"
            }
        ],
        "2T1BURHE5JC123456": [
            {
                "VIN": "2T1BURHE5JC123456",
                "registration_number": "XYZ-5678",
                "previous_owners": [],
                "transfer_date": "2021-03-20",
                "reason_for_transfer": "Initial registration"
            }
        ],
        "3FAHP0HA7CR123789": [
            {
                "VIN": "3FAHP0HA7CR123789",
                "registration_number": "DEF-9012",
                "previous_owners": ["OWN001"],
                "transfer_date": "2022-08-10",
                "reason_for_transfer": "Private sale"
            }
        ]
    },
    "registration_offices": {
        "OFF001": {
            "office_id": "OFF001",
            "location": "100 Government Center, Springfield, IL 62701",
            "operating_hours": "Mon-Fri 8:00 AM - 5:00 PM",
            "authorized_agents": ["Agent Smith", "Agent Brown"]
        },
        "OFF002": {
            "office_id": "OFF002",
            "location": "200 State Street, Chicago, IL 60601",
            "operating_hours": "Mon-Sat 9:00 AM - 6:00 PM",
            "authorized_agents": ["Agent Wilson", "Agent Taylor"]
        },
        "OFF003": {
            "office_id": "OFF003",
            "location": "300 County Road, Naperville, IL 60540",
            "operating_hours": "Mon-Fri 8:30 AM - 4:30 PM",
            "authorized_agents": ["Agent Miller"]
        }
    },
    "vin_to_registration": {
        "1HGBH41JXMN109186": "ABC-1234",
        "2T1BURHE5JC123456": "XYZ-5678",
        "3FAHP0HA7CR123789": "DEF-9012"
    },
    "current_timestamp": "2024-06-15T10:00:00"
}


class MotorVehicleRegistrationDatabase:
    """
    Motor Vehicle Registration Database Environment API.
    
    A stateful system for managing vehicle registrations, owner information,
    and registration history for government transportation authorities.
    """
    
    def __init__(self):
        """
        Initialize the Motor Vehicle Registration Database environment.
        
        Declares all state attributes and sets the API description.
        """
        self.vehicle_registrations: Dict[str, Dict[str, Any]] = {}
        self.owners: Dict[str, Dict[str, Any]] = {}
        self.vehicle_history: Dict[str, List[Dict[str, Any]]] = {}
        self.registration_offices: Dict[str, Dict[str, Any]] = {}
        self.vin_to_registration: Dict[str, str] = {}
        self.current_timestamp: str = ""
        
        self._api_description = (
            "A Motor Vehicle Registration Database for managing vehicle registrations, "
            "owner information, and registration history for government transportation authorities."
        )
    
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
            return
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
            Dict[str, Any]: A dictionary containing all internal state variables:
                - vehicle_registrations: All registered vehicles
                - owners: All registered owners
                - vehicle_history: Transfer and ownership history
                - registration_offices: Administrative offices
                - vin_to_registration: VIN to registration number mapping
                - current_timestamp: Current system timestamp
        """
        return {
            "vehicle_registrations": deepcopy(self.vehicle_registrations),
            "owners": deepcopy(self.owners),
            "vehicle_history": deepcopy(self.vehicle_history),
            "registration_offices": deepcopy(self.registration_offices),
            "vin_to_registration": deepcopy(self.vin_to_registration),
            "current_timestamp": self.current_timestamp
        }
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp for operations.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        return self.current_timestamp
    
    def _is_valid_vin(self, vin: str) -> bool:
        """
        Validate VIN format (17 characters, alphanumeric).
        
        Args:
            vin: Vehicle Identification Number to validate.
            
        Returns:
            bool: True if VIN is valid, False otherwise.
        """
        if not vin or len(vin) != 17:
            return False
        return vin.isalnum()
    
    def _is_future_date(self, date_str: str) -> bool:
        """
        Check if a date string represents a future date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            bool: True if date is in the future, False otherwise.
        """
        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d")
            current = datetime.strptime(self._timestamp()[:10], "%Y-%m-%d")
            return check_date > current
        except ValueError:
            return False
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_vehicle_by_registration_number(self, registration_number: str) -> Dict[str, Any]:
        """
        Retrieve full registration details of a vehicle using its registration number.
        
        Args:
            registration_number: The unique registration plate number.
            
        Returns:
            Dict[str, Any]: Vehicle registration details or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        return {"vehicle": deepcopy(self.vehicle_registrations[registration_number])}
    
    def get_owner_by_id(self, owner_id: str) -> Dict[str, Any]:
        """
        Retrieve owner information by owner_id.
        
        Args:
            owner_id: The unique identifier of the owner.
            
        Returns:
            Dict[str, Any]: Owner details or error message.
        """
        if not owner_id:
            return {"error": "Owner ID is required"}
        
        if owner_id not in self.owners:
            return {"error": f"No owner found with ID: {owner_id}"}
        
        return {"owner": deepcopy(self.owners[owner_id])}
    
    def get_vehicle_by_VIN(self, VIN: str) -> Dict[str, Any]:
        """
        Retrieve current vehicle registration data using its VIN.
        
        Args:
            VIN: The Vehicle Identification Number.
            
        Returns:
            Dict[str, Any]: Vehicle registration details or error message.
        """
        if not VIN:
            return {"error": "VIN is required"}
        
        if VIN not in self.vin_to_registration:
            return {"error": f"No vehicle found with VIN: {VIN}"}
        
        registration_number = self.vin_to_registration[VIN]
        return {"vehicle": deepcopy(self.vehicle_registrations[registration_number])}
    
    def get_vehicle_info(self, VIN: str) -> Dict[str, Any]:
        """
        Get basic vehicle information by VIN.
        
        Args:
            VIN: Vehicle Identification Number.
            
        Returns:
            Dict[str, Any]: Vehicle info with success status.
        """
        if VIN not in self.vin_to_registration:
            return {"success": False, "message": "Vehicle not found"}
            
        reg_num = self.vin_to_registration[VIN]
        vehicle = self.vehicle_registrations[reg_num]
        
        return {
            "success": True,
            "VIN": vehicle["VIN"],
            "make": vehicle["make"],
            "model": vehicle["model"]
        }
    
    def get_vehicle_history_by_VIN(self, VIN: str) -> Dict[str, Any]:
        """
        Retrieve ownership and transfer history for a vehicle using its VIN.
        
        Args:
            VIN: The Vehicle Identification Number.
            
        Returns:
            Dict[str, Any]: Vehicle history records or error message.
        """
        if not VIN:
            return {"error": "VIN is required"}
        
        if VIN not in self.vehicle_history:
            return {"error": f"No history found for VIN: {VIN}"}
        
        return {"history": deepcopy(self.vehicle_history[VIN])}
    
    def check_registration_validity(self, registration_number: str) -> Dict[str, Any]:
        """
        Check whether a registration is valid (expiry in future and insurance active).
        
        Args:
            registration_number: The unique registration plate number.
            
        Returns:
            Dict[str, Any]: Validity status with details or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        vehicle = self.vehicle_registrations[registration_number]
        expiry_valid = self._is_future_date(vehicle["registration_expiry_date"])
        insurance_active = vehicle["insurance_status"] == "active"
        
        is_valid = expiry_valid and insurance_active
        
        return {
            "registration_number": registration_number,
            "is_valid": is_valid,
            "expiry_date": vehicle["registration_expiry_date"],
            "expiry_valid": expiry_valid,
            "insurance_status": vehicle["insurance_status"],
            "insurance_active": insurance_active
        }
    
    def get_registration_expiry_date(self, registration_number: str) -> Dict[str, Any]:
        """
        Retrieve the current registration expiry date for a given vehicle.
        
        Args:
            registration_number: The unique registration plate number.
            
        Returns:
            Dict[str, Any]: Expiry date information or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        vehicle = self.vehicle_registrations[registration_number]
        return {
            "registration_number": registration_number,
            "registration_expiry_date": vehicle["registration_expiry_date"]
        }
    
    def get_insurance_status(self, registration_number: str) -> Dict[str, Any]:
        """
        Retrieve the insurance status of a registered vehicle.
        
        Args:
            registration_number: The unique registration plate number.
            
        Returns:
            Dict[str, Any]: Insurance status information or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        vehicle = self.vehicle_registrations[registration_number]
        return {
            "registration_number": registration_number,
            "insurance_status": vehicle["insurance_status"]
        }
    
    def list_all_registrations(self) -> Dict[str, Any]:
        """
        Retrieve a list of all currently registered vehicles (summary view).
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: List of all registered vehicles with summary info.
        """
        registrations = []
        for reg_num, vehicle in self.vehicle_registrations.items():
            registrations.append({
                "registration_number": reg_num,
                "VIN": vehicle["VIN"],
                "make": vehicle["make"],
                "model": vehicle["model"],
                "year": vehicle["year"],
                "current_owner_id": vehicle["current_owner_id"],
                "registration_expiry_date": vehicle["registration_expiry_date"],
                "insurance_status": vehicle["insurance_status"]
            })
        
        return {
            "total_count": len(registrations),
            "registrations": registrations
        }
    
    def list_vehicles_by_owner_id(self, owner_id: str) -> Dict[str, Any]:
        """
        Retrieve all vehicles currently registered to a specific owner.
        
        Args:
            owner_id: The unique identifier of the owner.
            
        Returns:
            Dict[str, Any]: List of vehicles owned or error message.
        """
        if not owner_id:
            return {"error": "Owner ID is required"}
        
        if owner_id not in self.owners:
            return {"error": f"No owner found with ID: {owner_id}"}
        
        vehicles = []
        for reg_num, vehicle in self.vehicle_registrations.items():
            if vehicle["current_owner_id"] == owner_id:
                vehicles.append(deepcopy(vehicle))
        
        return {
            "owner_id": owner_id,
            "vehicle_count": len(vehicles),
            "vehicles": vehicles
        }
    
    def get_registration_office_by_id(self, office_id: str) -> Dict[str, Any]:
        """
        Retrieve registration office information by office ID.
        
        Args:
            office_id: The unique identifier of the registration office.
            
        Returns:
            Dict[str, Any]: Office details or error message.
        """
        if not office_id:
            return {"error": "Office ID is required"}
        
        if office_id not in self.registration_offices:
            return {"error": f"No registration office found with ID: {office_id}"}
        
        return {"office": deepcopy(self.registration_offices[office_id])}
    
    def list_all_registration_offices(self) -> Dict[str, Any]:
        """
        Retrieve a list of all registration offices.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: List of all registration offices.
        """
        offices = []
        for office_id, office in self.registration_offices.items():
            offices.append(deepcopy(office))
        
        return {
            "total_count": len(offices),
            "offices": offices
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def register_owner(
        self,
        owner_id: str,
        name: str,
        address: str,
        contact_number: str,
        email: str,
        license_number: str
    ) -> Dict[str, Any]:
        """
        Register a new vehicle owner.
        
        Args:
            owner_id: Unique identifier for the owner.
            name: Full name of the owner.
            address: Owner's address.
            contact_number: Contact phone number.
            email: Email address.
            license_number: Driver's license number.
            
        Returns:
            Dict[str, Any]: Success status and message.
        """
        if owner_id in self.owners:
            return {
                "success": False,
                "message": f"Owner with ID {owner_id} already exists"
            }
            
        self.owners[owner_id] = {
            "owner_id": owner_id,
            "name": name,
            "address": address,
            "driver_license_number": license_number,
            "phone_number": contact_number,
            "email": email
        }
        
        return {
            "success": True,
            "message": "Owner registered successfully"
        }
    
    def register_vehicle(
        self,
        VIN: str,
        make: str,
        model: str,
        year: int,
        color: str,
        owner_id: str,
        vehicle_type: str
    ) -> Dict[str, Any]:
        """
        Register a new vehicle with automatically generated details.
        
        Args:
            VIN: Vehicle Identification Number.
            make: Vehicle make.
            model: Vehicle model.
            year: Vehicle year.
            color: Vehicle color.
            owner_id: ID of the owner.
            vehicle_type: Type of the vehicle.
            
        Returns:
            Dict[str, Any]: Success status and message.
        """
        if owner_id not in self.owners:
            return {
                "success": False,
                "message": f"Owner with ID {owner_id} not found"
            }
            
        if VIN in self.vin_to_registration:
            return {
                "success": False,
                "message": f"VIN {VIN} is already registered"
            }

        registration_number = f"REG-{VIN[-6:]}" if len(VIN) >= 6 else f"REG-{VIN}"
        
        try:
            current_date = datetime.strptime(self._timestamp()[:10], "%Y-%m-%d")
        except ValueError:
            current_date = datetime.now()
            
        expiry_date = (current_date + timedelta(days=365)).strftime("%Y-%m-%d")
        
        self.vehicle_registrations[registration_number] = {
            "registration_number": registration_number,
            "VIN": VIN,
            "make": make,
            "model": model,
            "year": year,
            "color": color,
            "vehicle_type": vehicle_type,
            "registration_expiry_date": expiry_date,
            "insurance_status": "active",
            "current_owner_id": owner_id
        }
        
        self.vin_to_registration[VIN] = registration_number
        
        self.vehicle_history[VIN] = [{
            "VIN": VIN,
            "registration_number": registration_number,
            "previous_owners": [],
            "transfer_date": self._timestamp()[:10],
            "reason_for_transfer": "Initial registration"
        }]
        
        return {
            "success": True,
            "message": "Vehicle registered successfully",
            "registration_number": registration_number,
            "VIN": VIN
        }

    def register_new_vehicle(
        self,
        registration_number: str,
        VIN: str,
        make: str,
        model: str,
        year: int,
        color: str,
        vehicle_type: str,
        registration_expiry_date: str,
        insurance_status: str,
        owner_id: str
    ) -> Dict[str, Any]:
        """
        Add a new vehicle registration with valid VIN, registration number, owner, and future expiry.
        
        Args:
            registration_number: Unique registration plate number.
            VIN: 17-character Vehicle Identification Number.
            make: Vehicle manufacturer.
            model: Vehicle model name.
            year: Manufacturing year.
            color: Vehicle color.
            vehicle_type: Type of vehicle (Sedan, Truck, etc.).
            registration_expiry_date: Future expiry date (YYYY-MM-DD).
            insurance_status: Insurance status ("active" or "inactive").
            owner_id: ID of the vehicle owner.
            
        Returns:
            Dict[str, Any]: Success confirmation or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        if not VIN:
            return {"error": "VIN is required"}
        if not owner_id:
            return {"error": "Owner ID is required"}
        
        if registration_number in self.vehicle_registrations:
            return {"error": f"Registration number {registration_number} already exists"}
        
        if not self._is_valid_vin(VIN):
            return {"error": "VIN must be exactly 17 alphanumeric characters"}
        
        if VIN in self.vin_to_registration:
            return {"error": f"VIN {VIN} is already registered"}
        
        if not self._is_future_date(registration_expiry_date):
            return {"error": "Registration expiry date must be a future date"}
        
        if owner_id not in self.owners:
            return {"error": f"Owner with ID {owner_id} does not exist"}
        
        if insurance_status not in ["active", "inactive"]:
            return {"error": "Insurance status must be 'active' or 'inactive'"}
        
        self.vehicle_registrations[registration_number] = {
            "registration_number": registration_number,
            "VIN": VIN,
            "make": make,
            "model": model,
            "year": year,
            "color": color,
            "vehicle_type": vehicle_type,
            "registration_expiry_date": registration_expiry_date,
            "insurance_status": insurance_status,
            "current_owner_id": owner_id
        }
        
        self.vin_to_registration[VIN] = registration_number
        
        self.vehicle_history[VIN] = [{
            "VIN": VIN,
            "registration_number": registration_number,
            "previous_owners": [],
            "transfer_date": self._timestamp()[:10],
            "reason_for_transfer": "Initial registration"
        }]
        
        return {
            "success": True,
            "message": f"Vehicle registered successfully with registration number {registration_number}",
            "registration_number": registration_number,
            "VIN": VIN
        }
    
    def renew_registration(
        self,
        VIN: str,
        renewal_years: int
    ) -> Dict[str, Any]:
        """
        Renew vehicle registration by VIN.
        
        Args:
            VIN: Vehicle Identification Number.
            renewal_years: Number of years to renew.
            
        Returns:
            Dict[str, Any]: Success status and message.
        """
        if VIN not in self.vin_to_registration:
            return {"success": False, "message": "Vehicle not found"}
            
        reg_num = self.vin_to_registration[VIN]
        vehicle = self.vehicle_registrations[reg_num]
        
        try:
            current_expiry = datetime.strptime(vehicle["registration_expiry_date"], "%Y-%m-%d")
        except ValueError:
            current_expiry = datetime.strptime(self._timestamp()[:10], "%Y-%m-%d")
            
        new_expiry = (current_expiry + timedelta(days=365 * renewal_years)).strftime("%Y-%m-%d")
        
        result = self.renew_vehicle_registration(reg_num, new_expiry)
        if "error" in result:
            return {"success": False, "message": result["error"]}
            
        return {
            "success": True,
            "message": "Registration renewed successfully"
        }

    def renew_vehicle_registration(
        self,
        registration_number: str,
        new_expiry_date: str
    ) -> Dict[str, Any]:
        """
        Update the registration expiry date to a future date, contingent on active insurance.
        
        Args:
            registration_number: The unique registration plate number.
            new_expiry_date: New expiry date in YYYY-MM-DD format.
            
        Returns:
            Dict[str, Any]: Success confirmation or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        if not new_expiry_date:
            return {"error": "New expiry date is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        vehicle = self.vehicle_registrations[registration_number]
        
        if vehicle["insurance_status"] != "active":
            return {"error": "Cannot renew registration: insurance status must be active"}
        
        if not self._is_future_date(new_expiry_date):
            return {"error": "New expiry date must be a future date"}
        
        old_expiry = vehicle["registration_expiry_date"]
        vehicle["registration_expiry_date"] = new_expiry_date
        
        return {
            "success": True,
            "message": "Registration renewed successfully",
            "registration_number": registration_number,
            "old_expiry_date": old_expiry,
            "new_expiry_date": new_expiry_date
        }

    def transfer_ownership(
        self,
        VIN: str,
        new_owner_id: str,
        transfer_reason: str
    ) -> Dict[str, Any]:
        """
        Transfer vehicle ownership by VIN.
        
        Args:
            VIN: Vehicle Identification Number.
            new_owner_id: ID of the new owner.
            transfer_reason: Reason for transfer.
            
        Returns:
            Dict[str, Any]: Success status and message.
        """
        if VIN not in self.vin_to_registration:
            return {"success": False, "message": "Vehicle not found"}
            
        reg_num = self.vin_to_registration[VIN]
        result = self.transfer_vehicle_ownership(reg_num, new_owner_id, transfer_reason)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
            
        return {
            "success": True,
            "message": "Ownership transferred successfully"
        }

    def transfer_vehicle_ownership(
        self,
        registration_number: str,
        new_owner_id: str,
        reason_for_transfer: str
    ) -> Dict[str, Any]:
        """
        Change the current owner of a vehicle and record the transfer in VehicleHistory.
        
        Args:
            registration_number: The unique registration plate number.
            new_owner_id: ID of the new owner.
            reason_for_transfer: Reason for the ownership transfer.
            
        Returns:
            Dict[str, Any]: Success confirmation or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        if not new_owner_id:
            return {"error": "New owner ID is required"}
        if not reason_for_transfer:
            return {"error": "Reason for transfer is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        if new_owner_id not in self.owners:
            return {"error": f"New owner with ID {new_owner_id} does not exist"}
        
        vehicle = self.vehicle_registrations[registration_number]
        previous_owner_id = vehicle["current_owner_id"]
        
        if previous_owner_id == new_owner_id:
            return {"error": "New owner cannot be the same as current owner"}
        
        VIN = vehicle["VIN"]
        
        history = self.vehicle_history.get(VIN, [])
        all_previous_owners = []
        for record in history:
            all_previous_owners.extend(record.get("previous_owners", []))
        if previous_owner_id not in all_previous_owners:
            all_previous_owners.append(previous_owner_id)
        
        vehicle["current_owner_id"] = new_owner_id
        
        history_record = {
            "VIN": VIN,
            "registration_number": registration_number,
            "previous_owners": all_previous_owners,
            "transfer_date": self._timestamp()[:10],
            "reason_for_transfer": reason_for_transfer
        }
        
        if VIN in self.vehicle_history:
            self.vehicle_history[VIN].append(history_record)
        else:
            self.vehicle_history[VIN] = [history_record]
        
        return {
            "success": True,
            "message": "Vehicle ownership transferred successfully",
            "registration_number": registration_number,
            "previous_owner_id": previous_owner_id,
            "new_owner_id": new_owner_id,
            "transfer_date": self._timestamp()[:10]
        }
    
    def update_vehicle_insurance_status(
        self,
        registration_number: str,
        new_insurance_status: str
    ) -> Dict[str, Any]:
        """
        Update the insurance status of a vehicle.
        
        Args:
            registration_number: The unique registration plate number.
            new_insurance_status: New insurance status ("active" or "inactive").
            
        Returns:
            Dict[str, Any]: Success confirmation or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        if not new_insurance_status:
            return {"error": "New insurance status is required"}
        
        if new_insurance_status not in ["active", "inactive"]:
            return {"error": "Insurance status must be 'active' or 'inactive'"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        vehicle = self.vehicle_registrations[registration_number]
        old_status = vehicle["insurance_status"]
        vehicle["insurance_status"] = new_insurance_status
        
        return {
            "success": True,
            "message": "Insurance status updated successfully",
            "registration_number": registration_number,
            "old_insurance_status": old_status,
            "new_insurance_status": new_insurance_status
        }
    
    def suspend_registration_due_to_lapsed_insurance(
        self,
        registration_number: str
    ) -> Dict[str, Any]:
        """
        Suspend a registration if insurance is no longer active.
        
        Args:
            registration_number: The unique registration plate number.
            
        Returns:
            Dict[str, Any]: Success confirmation or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        vehicle = self.vehicle_registrations[registration_number]
        
        if vehicle["insurance_status"] == "active":
            return {"error": "Cannot suspend registration: insurance is still active"}
        
        vehicle["registration_expiry_date"] = "1970-01-01"
        
        return {
            "success": True,
            "message": "Registration suspended due to lapsed insurance",
            "registration_number": registration_number,
            "suspension_date": self._timestamp()[:10]
        }
    
    def update_vehicle_registration_details(
        self,
        registration_number: str,
        color: Optional[str] = None,
        vehicle_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify non-critical vehicle details while preserving registration integrity.
        
        Args:
            registration_number: The unique registration plate number.
            color: New vehicle color (optional).
            vehicle_type: New vehicle type (optional).
            
        Returns:
            Dict[str, Any]: Success confirmation or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        if color is None and vehicle_type is None:
            return {"error": "At least one field (color or vehicle_type) must be provided for update"}
        
        vehicle = self.vehicle_registrations[registration_number]
        updates = {}
        
        if color is not None:
            updates["color"] = {"old": vehicle["color"], "new": color}
            vehicle["color"] = color
        
        if vehicle_type is not None:
            updates["vehicle_type"] = {"old": vehicle["vehicle_type"], "new": vehicle_type}
            vehicle["vehicle_type"] = vehicle_type
        
        return {
            "success": True,
            "message": "Vehicle registration details updated successfully",
            "registration_number": registration_number,
            "updates": updates
        }

    def revoke_registration(self, VIN: str, reason: str) -> Dict[str, Any]:
        """
        Revoke a vehicle registration by VIN.
        
        Args:
            VIN: Vehicle Identification Number.
            reason: Reason for revocation.
            
        Returns:
            Dict[str, Any]: Success status and message.
        """
        if VIN not in self.vin_to_registration:
            return {"success": False, "message": "Vehicle not found"}
            
        reg_num = self.vin_to_registration[VIN]
        result = self.revoke_vehicle_registration(reg_num, reason)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
            
        return {
            "success": True,
            "message": "Vehicle registration revoked successfully"
        }

    def revoke_vehicle_registration(
        self,
        registration_number: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Remove or deactivate a vehicle's registration.
        
        Args:
            registration_number: The unique registration plate number.
            reason: Reason for revocation (e.g., salvage, decommissioning).
            
        Returns:
            Dict[str, Any]: Success confirmation or error message.
        """
        if not registration_number:
            return {"error": "Registration number is required"}
        if not reason:
            return {"error": "Reason for revocation is required"}
        
        if registration_number not in self.vehicle_registrations:
            return {"error": f"No vehicle found with registration number: {registration_number}"}
        
        vehicle = self.vehicle_registrations[registration_number]
        VIN = vehicle["VIN"]
        
        revoked_vehicle = self.vehicle_registrations.pop(registration_number)
        
        if VIN in self.vin_to_registration:
            del self.vin_to_registration[VIN]
        
        if VIN in self.vehicle_history:
            self.vehicle_history[VIN].append({
                "VIN": VIN,
                "registration_number": registration_number,
                "previous_owners": [revoked_vehicle["current_owner_id"]],
                "transfer_date": self._timestamp()[:10],
                "reason_for_transfer": f"Registration revoked: {reason}"
            })
        
        return {
            "success": True,
            "message": "Vehicle registration revoked successfully",
            "registration_number": registration_number,
            "VIN": VIN,
            "reason": reason,
            "revocation_date": self._timestamp()[:10]
        }
    
    def add_registration_office(
        self,
        office_id: str,
        location: str,
        operating_hours: str,
        authorized_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Add a new registration office to the system.
        
        Args:
            office_id: Unique identifier for the office
            location: Physical location of the office
            operating_hours: Office operating hours
            authorized_agents: List of authorized agent IDs
            
        Returns:
            Dict[str, Any]: Dictionary containing office creation status
        """
        if office_id in self.registration_offices:
            return {
                "success": False,
                "message": f"Office with ID {office_id} already exists"
            }
        
        self.registration_offices[office_id] = {
            "office_id": office_id,
            "location": location,
            "operating_hours": operating_hours,
            "authorized_agents": authorized_agents,
            "created_date": self._timestamp()[:10],
            "is_active": True,
            "processed_registrations": 0
        }
        
        return {
            "success": True,
            "message": "Registration office added successfully",
            "office_id": office_id,
            "location": location
        }
    
    def get_registration_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about vehicle registrations.
        
        Returns:
            Dict[str, Any]: Dictionary containing registration statistics
        """
        total_vehicles = len(self.vehicle_registrations)
        active_registrations = 0
        pending_registrations = 0
        expired_registrations = 0
        
        for v in self.vehicle_registrations.values():
            if self._is_future_date(v.get("registration_expiry_date", "")):
                if v.get("insurance_status") == "active":
                    active_registrations += 1
                else:
                    pending_registrations += 1
            else:
                expired_registrations += 1
        
        vehicle_types = {}
        for vehicle in self.vehicle_registrations.values():
            v_type = vehicle.get("vehicle_type", "unknown")
            vehicle_types[v_type] = vehicle_types.get(v_type, 0) + 1
        
        return {
            "total_vehicles": total_vehicles,
            "active_registrations": active_registrations,
            "pending_registrations": pending_registrations,
            "expired_registrations": expired_registrations,
            "total_owners": len(self.owners),
            "total_offices": len(self.registration_offices),
            "vehicle_types_distribution": vehicle_types,
            "report_generated": self._timestamp()
        }
    
    def search_vehicles(
        self,
        search_term: str,
        search_field: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Search for vehicles based on various criteria.
        
        Args:
            search_term: Term to search for
            search_field: Field to search in (all, VIN, make, model, owner)
            
        Returns:
            List[Dict[str, Any]]: List of matching vehicles
        """
        results = []
        search_term_lower = search_term.lower()
        
        for vehicle in self.vehicle_registrations.values():
            match = False
            
            if search_field == "all":
                searchable = f"{vehicle.get('VIN', '')} {vehicle.get('make', '')} {vehicle.get('model', '')} {vehicle.get('current_owner_id', '')}"
                match = search_term_lower in searchable.lower()
            elif search_field == "VIN":
                match = search_term_lower in vehicle.get("VIN", "").lower()
            elif search_field == "make":
                match = search_term_lower in vehicle.get("make", "").lower()
            elif search_field == "model":
                match = search_term_lower in vehicle.get("model", "").lower()
            elif search_field == "owner":
                match = search_term_lower in vehicle.get("current_owner_id", "").lower()
            
            if match:
                results.append(vehicle.copy())
        
        return results
    
    def bulk_register_vehicles(
        self,
        vehicles_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Register multiple vehicles in bulk.
        
        Args:
            vehicles_data: List of vehicle data dictionaries
            
        Returns:
            Dict[str, Any]: Dictionary containing bulk registration results
        """
        successful = []
        failed = []
        
        for vehicle_data in vehicles_data:
            try:
                result = self.register_vehicle(
                    VIN=vehicle_data.get("VIN"),
                    make=vehicle_data.get("make"),
                    model=vehicle_data.get("model"),
                    year=vehicle_data.get("year"),
                    color=vehicle_data.get("color"),
                    owner_id=vehicle_data.get("owner_id"),
                    vehicle_type=vehicle_data.get("vehicle_type", "sedan")
                )
                if result.get("success"):
                    successful.append(result)
                else:
                    failed.append({
                        "VIN": vehicle_data.get("VIN"),
                        "error": result.get("message")
                    })
            except Exception as e:
                failed.append({
                    "VIN": vehicle_data.get("VIN"),
                    "error": str(e)
                })
        
        return {
            "success": len(failed) == 0,
            "total_processed": len(vehicles_data),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "successful_registrations": successful,
            "failed_registrations": failed
        }


__TEST_CASES__ = [
    {
        "name": "test_register_owner",
        "input": {
            "method": "register_owner",
            "params": {
                "owner_id": "OWN001",
                "name": "John Smith",
                "address": "123 Main St, City, State 12345",
                "contact_number": "555-123-4567",
                "email": "john.smith@email.com",
                "license_number": "DL123456789"
            }
        },
        "expected": {
            "success": True,
            "message": "Owner registered successfully"
        }
    },
    {
        "name": "test_register_duplicate_owner",
        "setup": [
            {
                "method": "register_owner",
                "params": {
                    "owner_id": "OWN002",
                    "name": "Jane Doe",
                    "address": "456 Oak Ave",
                    "contact_number": "555-987-6543",
                    "email": "jane.doe@email.com",
                    "license_number": "DL987654321"
                }
            }
        ],
        "input": {
            "method": "register_owner",
            "params": {
                "owner_id": "OWN002",
                "name": "Jane Doe",
                "address": "456 Oak Ave",
                "contact_number": "555-987-6543",
                "email": "jane.doe@email.com",
                "license_number": "DL987654321"
            }
        },
        "expected": {
            "success": False,
            "message": "Owner with ID OWN002 already exists"
        }
    },
    {
        "name": "test_register_vehicle",
        "setup": [
            {
                "method": "register_owner",
                "params": {
                    "owner_id": "OWN003",
                    "name": "Bob Johnson",
                    "address": "789 Pine Rd",
                    "contact_number": "555-456-7890",
                    "email": "bob.j@email.com",
                    "license_number": "DL456789012"
                }
            }
        ],
        "input": {
            "method": "register_vehicle",
            "params": {
                "VIN": "1HGBH41JXMN109186",
                "make": "Honda",
                "model": "Accord",
                "year": 2023,
                "color": "Silver",
                "owner_id": "OWN003",
                "vehicle_type": "sedan"
            }
        },
        "expected": {
            "success": True,
            "message": "Vehicle registered successfully"
        }
    },
    {
        "name": "test_transfer_ownership",
        "setup": [
            {
                "method": "register_owner",
                "params": {
                    "owner_id": "OWN004",
                    "name": "Alice Brown",
                    "address": "100 Elm St",
                    "contact_number": "555-111-2222",
                    "email": "alice.b@email.com",
                    "license_number": "DL111222333"
                }
            },
            {
                "method": "register_owner",
                "params": {
                    "owner_id": "OWN005",
                    "name": "Charlie Wilson",
                    "address": "200 Maple Ave",
                    "contact_number": "555-333-4444",
                    "email": "charlie.w@email.com",
                    "license_number": "DL333444555"
                }
            },
            {
                "method": "register_vehicle",
                "params": {
                    "VIN": "3HGBH41JXMN109188",
                    "make": "Ford",
                    "model": "Mustang",
                    "year": 2022,
                    "color": "Red",
                    "owner_id": "OWN004",
                    "vehicle_type": "coupe"
                }
            }
        ],
        "input": {
            "method": "transfer_ownership",
            "params": {
                "VIN": "3HGBH41JXMN109188",
                "new_owner_id": "OWN005",
                "transfer_reason": "Sale"
            }
        },
        "expected": {
            "success": True,
            "message": "Ownership transferred successfully"
        }
    },
    {
        "name": "test_search_vehicles",
        "setup": [
            {
                "method": "register_owner",
                "params": {
                    "owner_id": "OWN009",
                    "name": "Grace Kim",
                    "address": "600 Spruce Way",
                    "contact_number": "555-222-3333",
                    "email": "grace.k@email.com",
                    "license_number": "DL222333444"
                }
            },
            {
                "method": "register_vehicle",
                "params": {
                    "VIN": "7HGBH41JXMN109192",
                    "make": "Mercedes",
                    "model": "C-Class",
                    "year": 2023,
                    "color": "Silver",
                    "owner_id": "OWN009",
                    "vehicle_type": "sedan"
                }
            }
        ],
        "input": {
            "method": "search_vehicles",
            "params": {
                "search_term": "Mercedes",
                "search_field": "make"
            }
        },
        "expected_type": "list",
        "expected_length_min": 1
    }
]