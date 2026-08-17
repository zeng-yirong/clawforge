"""
Vehicle Insurance Claim Management System API

A vehicle insurance claim management system governs the submission, tracking, and resolution 
of claims related to insured vehicles. It maintains records of customer policies, vehicle details, 
and indexed claims, allowing users to report incidents, provide necessary documentation, and 
monitor claim statuses.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE: Dict[str, Any] = {
    "customers": {
        "CUST001": {
            "customer_id": "CUST001",
            "name": "John Smith",
            "contact_info": "john.smith@email.com, +1-555-0101",
            "address": "123 Main Street, Springfield, IL 62701"
        },
        "CUST002": {
            "customer_id": "CUST002",
            "name": "Sarah Johnson",
            "contact_info": "sarah.j@email.com, +1-555-0102",
            "address": "456 Oak Avenue, Chicago, IL 60601"
        },
        "CUST003": {
            "customer_id": "CUST003",
            "name": "Michael Davis",
            "contact_info": "m.davis@email.com, +1-555-0103",
            "address": "789 Pine Road, Naperville, IL 60540"
        }
    },
    "policies": {
        "POL001": {
            "policy_id": "POL001",
            "customer_id": "CUST001",
            "policy_number": "AUTO-2024-00001",
            "coverage_type": "comprehensive",
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "status": "active"
        },
        "POL002": {
            "policy_id": "POL002",
            "customer_id": "CUST002",
            "policy_number": "AUTO-2024-00002",
            "coverage_type": "collision",
            "start_date": "2024-03-15",
            "end_date": "2025-03-15",
            "status": "active"
        },
        "POL003": {
            "policy_id": "POL003",
            "customer_id": "CUST003",
            "policy_number": "AUTO-2023-00099",
            "coverage_type": "liability",
            "start_date": "2023-06-01",
            "end_date": "2024-06-01",
            "status": "expired"
        }
    },
    "vehicles": {
        "VEH001": {
            "vehicle_id": "VEH001",
            "VIN": "1HGBH41JXMN109186",
            "make": "Honda",
            "model": "Accord",
            "year": 2023,
            "customer_id": "CUST001",
            "policy_id": "POL001"
        },
        "VEH002": {
            "vehicle_id": "VEH002",
            "VIN": "5YJSA1E26MF123456",
            "make": "Tesla",
            "model": "Model S",
            "year": 2022,
            "customer_id": "CUST002",
            "policy_id": "POL002"
        },
        "VEH003": {
            "vehicle_id": "VEH003",
            "VIN": "WVWZZZ3CZWE123789",
            "make": "Volkswagen",
            "model": "Passat",
            "year": 2021,
            "customer_id": "CUST003",
            "policy_id": "POL003"
        },
        "VEH004": {
            "vehicle_id": "VEH004",
            "VIN": "2T1BURHE5JC123456",
            "make": "Toyota",
            "model": "Corolla",
            "year": 2024,
            "customer_id": "CUST001",
            "policy_id": "POL001"
        }
    },
    "claims": {
        "CLM001": {
            "claim_id": "CLM001",
            "policy_id": "POL001",
            "incident_description": "Rear-end collision at intersection",
            "status": "under_review",
            "date_filed": "2024-02-15T10:30:00",
            "vehicle_id": "VEH001"
        },
        "CLM002": {
            "claim_id": "CLM002",
            "policy_id": "POL002",
            "incident_description": "Hail damage to windshield and roof",
            "status": "approved",
            "date_filed": "2024-04-20T14:45:00",
            "vehicle_id": "VEH002"
        },
        "CLM003": {
            "claim_id": "CLM003",
            "policy_id": "POL001",
            "incident_description": "Parking lot scrape on driver side door",
            "status": "submitted",
            "date_filed": "2024-05-10T09:00:00",
            "vehicle_id": "VEH004"
        }
    },
    "supporting_documents": {
        "CLM001": ["police_report.pdf", "damage_photos.zip"],
        "CLM002": ["weather_report.pdf", "repair_estimate.pdf"],
        "CLM003": []
    },
    "next_claim_id": 4,
    "next_policy_id": 4,
    "next_vehicle_id": 5,
    "current_user": None,
    "session_id": None
}


class VehicleInsuranceClaimManagementSystem:
    """
    Vehicle Insurance Claim Management System API.
    
    This system manages the submission, tracking, and resolution of vehicle insurance claims.
    It maintains records of customer policies, vehicle details, and claim information, allowing
    users to report incidents, provide documentation, and monitor claim statuses.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Vehicle Insurance Claim Management System.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.vehicles: Dict[str, Dict[str, Any]] = {}
        self.claims: Dict[str, Dict[str, Any]] = {}
        self.supporting_documents: Dict[str, List[str]] = {}
        self.next_claim_id: int = 1
        self.next_policy_id: int = 1
        self.next_vehicle_id: int = 1
        self.current_user: Optional[str] = None
        self.session_id: Optional[str] = None
        
        self._api_description = (
            "A vehicle insurance claim management system for submitting, tracking, "
            "and resolving claims related to insured vehicles."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a unified ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data for the environment.
            long_context: Flag for extended context loading (not used in base implementation).
        
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
        Retrieve the current state of the entire environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables including:
                - customers: All registered customers
                - policies: All insurance policies
                - vehicles: All registered vehicles
                - claims: All submitted claims
                - supporting_documents: Documents attached to claims
                - next_claim_id: Counter for next claim ID
                - next_policy_id: Counter for next policy ID
                - next_vehicle_id: Counter for next vehicle ID
                - current_user: Currently logged in user
                - session_id: Current session identifier
        """
        return {
            "customers": deepcopy(self.customers),
            "policies": deepcopy(self.policies),
            "vehicles": deepcopy(self.vehicles),
            "claims": deepcopy(self.claims),
            "supporting_documents": deepcopy(self.supporting_documents),
            "next_claim_id": self.next_claim_id,
            "next_policy_id": self.next_policy_id,
            "next_vehicle_id": self.next_vehicle_id,
            "current_user": self.current_user,
            "session_id": self.session_id
        }
    
    # ========== QUERY OPERATIONS ==========
    
    def get_policy_by_number(self, policy_number: str) -> Dict[str, Any]:
        """
        Retrieve policy details using the unique policy_number.
        
        Used to validate policy existence and status before performing operations.
        
        Args:
            policy_number: The unique policy number to search for.
        
        Returns:
            Dict[str, Any]: Policy details if found, or error dictionary if not found.
        """
        for policy in self.policies.values():
            if policy.get("policy_number") == policy_number:
                return deepcopy(policy)
        return {"error": f"Policy with number '{policy_number}' not found"}
    
    def get_policy_by_id(self, policy_id: str) -> Dict[str, Any]:
        """
        Retrieve a policy by its internal policy_id.
        
        Args:
            policy_id: The internal policy identifier.
        
        Returns:
            Dict[str, Any]: Policy details if found, or error dictionary if not found.
        """
        if policy_id in self.policies:
            return deepcopy(self.policies[policy_id])
        return {"error": f"Policy with ID '{policy_id}' not found"}
    
    def get_vehicle_by_vin(self, vin: str) -> Dict[str, Any]:
        """
        Find a registered vehicle using its VIN.
        
        Ensures the vehicle exists in the system before processing claims.
        
        Args:
            vin: The Vehicle Identification Number to search for.
        
        Returns:
            Dict[str, Any]: Vehicle details if found, or error dictionary if not found.
        """
        for vehicle in self.vehicles.values():
            if vehicle.get("VIN") == vin:
                return deepcopy(vehicle)
        return {"error": f"Vehicle with VIN '{vin}' not found"}
    
    def get_vehicle_by_id(self, vehicle_id: str) -> Dict[str, Any]:
        """
        Retrieve vehicle details by vehicle_id.
        
        Args:
            vehicle_id: The internal vehicle identifier.
        
        Returns:
            Dict[str, Any]: Vehicle details if found, or error dictionary if not found.
        """
        if vehicle_id in self.vehicles:
            return deepcopy(self.vehicles[vehicle_id])
        return {"error": f"Vehicle with ID '{vehicle_id}' not found"}
    
    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer information by customer_id.
        
        Args:
            customer_id: The internal customer identifier.
        
        Returns:
            Dict[str, Any]: Customer details (name, contact, address) if found,
                or error dictionary if not found.
        """
        if customer_id in self.customers:
            return deepcopy(self.customers[customer_id])
        return {"error": f"Customer with ID '{customer_id}' not found"}
    
    def get_customer_by_name(self, name: str) -> Dict[str, Any]:
        """
        Search for a customer by name.
        
        May return multiple results if name is not unique.
        
        Args:
            name: The customer name to search for (case-insensitive partial match).
        
        Returns:
            Dict[str, Any]: Dictionary containing list of matching customers,
                or error if none found.
        """
        matches = []
        name_lower = name.lower()
        for customer in self.customers.values():
            if name_lower in customer.get("name", "").lower():
                matches.append(deepcopy(customer))
        
        if matches:
            return {"customers": matches, "count": len(matches)}
        return {"error": f"No customers found matching name '{name}'"}
    
    def list_vehicles_by_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve all vehicles associated with a given customer_id.
        
        Args:
            customer_id: The customer identifier to filter vehicles by.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of vehicles owned by the customer.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        vehicles = [
            deepcopy(v) for v in self.vehicles.values()
            if v.get("customer_id") == customer_id
        ]
        return {"vehicles": vehicles, "count": len(vehicles)}
    
    def list_policies_by_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        List all policies (active/inactive) held by a specific customer.
        
        Args:
            customer_id: The customer identifier to filter policies by.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of all policies for the customer.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        policies = [
            deepcopy(p) for p in self.policies.values()
            if p.get("customer_id") == customer_id
        ]
        return {"policies": policies, "count": len(policies)}
    
    def list_claims_by_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Retrieve all claims associated with a given policy_id.
        
        Args:
            policy_id: The policy identifier to filter claims by.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of claims for the policy.
        """
        if policy_id not in self.policies:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        claims = [
            deepcopy(c) for c in self.claims.values()
            if c.get("policy_id") == policy_id
        ]
        return {"claims": claims, "count": len(claims)}
    
    def list_claims_by_vehicle(self, vehicle_id: str) -> Dict[str, Any]:
        """
        Retrieve all claims linked to a specific vehicle_id.
        
        Args:
            vehicle_id: The vehicle identifier to filter claims by.
        
        Returns:
            Dict[str, Any]: Dictionary containing list of claims for the vehicle.
        """
        if vehicle_id not in self.vehicles:
            return {"error": f"Vehicle with ID '{vehicle_id}' not found"}
        
        claims = [
            deepcopy(c) for c in self.claims.values()
            if c.get("vehicle_id") == vehicle_id
        ]
        return {"claims": claims, "count": len(claims)}
    
    def get_claim_by_id(self, claim_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a specific claim.
        
        Args:
            claim_id: The claim identifier to retrieve.
        
        Returns:
            Dict[str, Any]: Claim details if found, or error dictionary if not found.
        """
        if claim_id in self.claims:
            return deepcopy(self.claims[claim_id])
        return {"error": f"Claim with ID '{claim_id}' not found"}
    
    def check_policy_status(self, policy_id: str) -> Dict[str, Any]:
        """
        Determine if a policy is active.
        
        Required before allowing new claim submission.
        
        Args:
            policy_id: The policy identifier to check.
        
        Returns:
            Dict[str, Any]: Dictionary containing policy status and active flag.
        """
        if policy_id not in self.policies:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        policy = self.policies[policy_id]
        status = policy.get("status", "unknown")
        is_active = status == "active"
        
        return {
            "policy_id": policy_id,
            "status": status,
            "is_active": is_active
        }
    
    def validate_vehicle_policy_link(self, vehicle_id: str, policy_id: str) -> Dict[str, Any]:
        """
        Confirm that a given vehicle is covered under a specific policy.
        
        Args:
            vehicle_id: The vehicle identifier to validate.
            policy_id: The policy identifier to validate against.
        
        Returns:
            Dict[str, Any]: Dictionary containing validation result and details.
        """
        if vehicle_id not in self.vehicles:
            return {"error": f"Vehicle with ID '{vehicle_id}' not found"}
        
        if policy_id not in self.policies:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        vehicle = self.vehicles[vehicle_id]
        is_linked = vehicle.get("policy_id") == policy_id
        
        return {
            "vehicle_id": vehicle_id,
            "policy_id": policy_id,
            "is_linked": is_linked,
            "vehicle_policy_id": vehicle.get("policy_id")
        }
    
    def get_claim_status(self, claim_id: str) -> Dict[str, Any]:
        """
        Check the current processing status of a claim.
        
        Args:
            claim_id: The claim identifier to check.
        
        Returns:
            Dict[str, Any]: Dictionary containing claim status information
                (e.g., submitted, under_review, approved, denied).
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        claim = self.claims[claim_id]
        return {
            "claim_id": claim_id,
            "status": claim.get("status"),
            "date_filed": claim.get("date_filed")
        }
    
    # ========== STATE CHANGE OPERATIONS ==========
    
    def create_claim(
        self,
        policy_id: str,
        vehicle_id: str,
        incident_description: str
    ) -> Dict[str, Any]:
        """
        Submit a new claim with incident description.
        
        Links the claim to a valid policy and vehicle, sets status to "submitted" by default,
        and enforces all constraints.
        
        Constraints enforced:
        - A claim can only be submitted for a vehicle covered under an active policy.
        - Each claim must be associated with exactly one policy and one vehicle.
        - The policy must be active.
        - The vehicle must be linked to the specified policy.
        
        Args:
            policy_id: The policy under which to file the claim.
            vehicle_id: The vehicle involved in the incident.
            incident_description: Description of the incident.
        
        Returns:
            Dict[str, Any]: Created claim details on success, or error dictionary on failure.
        """
        # Validate policy exists
        if policy_id not in self.policies:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        # Validate vehicle exists
        if vehicle_id not in self.vehicles:
            return {"error": f"Vehicle with ID '{vehicle_id}' not found"}
        
        # Constraint 1: Policy must be active
        policy = self.policies[policy_id]
        if policy.get("status") != "active":
            return {"error": f"Cannot create claim: Policy '{policy_id}' is not active (status: {policy.get('status')})"}
        
        # Constraint 5: Vehicle must be linked to the policy
        vehicle = self.vehicles[vehicle_id]
        if vehicle.get("policy_id") != policy_id:
            return {
                "error": f"Cannot create claim: Vehicle '{vehicle_id}' is not covered under policy '{policy_id}'"
            }
        
        # Validate incident description is provided
        if not incident_description or not incident_description.strip():
            return {"error": "Incident description cannot be empty"}
        
        # Create the claim with status "submitted" (Constraint 4)
        claim_id = f"CLM{self.next_claim_id:03d}"
        self.next_claim_id += 1
        
        new_claim = {
            "claim_id": claim_id,
            "policy_id": policy_id,
            "incident_description": incident_description.strip(),
            "status": "submitted",
            "date_filed": self._timestamp(),
            "vehicle_id": vehicle_id
        }
        
        self.claims[claim_id] = new_claim
        self.supporting_documents[claim_id] = []
        
        return {
            "success": True,
            "message": "Claim created successfully",
            "claim": deepcopy(new_claim)
        }
    
    def update_claim_status(self, claim_id: str, new_status: str) -> Dict[str, Any]:
        """
        Change the status of an existing claim.
        
        Valid statuses: submitted, under_review, approved, denied, closed.
        
        Args:
            claim_id: The claim identifier to update.
            new_status: The new status to set.
        
        Returns:
            Dict[str, Any]: Updated claim details on success, or error dictionary on failure.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        valid_statuses = ["submitted", "under_review", "approved", "denied", "closed"]
        if new_status not in valid_statuses:
            return {
                "error": f"Invalid status '{new_status}'. Valid statuses: {', '.join(valid_statuses)}"
            }
        
        old_status = self.claims[claim_id]["status"]
        self.claims[claim_id]["status"] = new_status
        
        return {
            "success": True,
            "message": f"Claim status updated from '{old_status}' to '{new_status}'",
            "claim": deepcopy(self.claims[claim_id])
        }
    
    def add_policy(
        self,
        customer_id: str,
        policy_number: str,
        coverage_type: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Register a new insurance policy.
        
        Ensures policy_number uniqueness and validity.
        
        Args:
            customer_id: The customer to associate the policy with.
            policy_number: Unique policy number (must not already exist).
            coverage_type: Type of coverage (e.g., comprehensive, collision, liability).
            start_date: Policy start date (YYYY-MM-DD format).
            end_date: Policy end date (YYYY-MM-DD format).
        
        Returns:
            Dict[str, Any]: Created policy details on success, or error dictionary on failure.
        """
        # Validate customer exists
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        # Constraint 2: policy_number must be unique
        for policy in self.policies.values():
            if policy.get("policy_number") == policy_number:
                return {"error": f"Policy number '{policy_number}' already exists"}
        
        # Validate policy_number format (basic validation)
        if not policy_number or not policy_number.strip():
            return {"error": "Policy number cannot be empty"}
        
        # Validate coverage_type
        valid_coverage_types = ["comprehensive", "collision", "liability", "basic"]
        if coverage_type not in valid_coverage_types:
            return {
                "error": f"Invalid coverage type '{coverage_type}'. Valid types: {', '.join(valid_coverage_types)}"
            }
        
        # Create the policy
        policy_id = f"POL{self.next_policy_id:03d}"
        self.next_policy_id += 1
        
        new_policy = {
            "policy_id": policy_id,
            "customer_id": customer_id,
            "policy_number": policy_number.strip(),
            "coverage_type": coverage_type,
            "start_date": start_date,
            "end_date": end_date,
            "status": "active"
        }
        
        self.policies[policy_id] = new_policy
        
        return {
            "success": True,
            "message": "Policy created successfully",
            "policy": deepcopy(new_policy)
        }
    
    def update_policy_status(self, policy_id: str, new_status: str) -> Dict[str, Any]:
        """
        Modify the status of a policy.
        
        Valid statuses: active, expired, canceled, suspended.
        
        Args:
            policy_id: The policy identifier to update.
            new_status: The new status to set.
        
        Returns:
            Dict[str, Any]: Updated policy details on success, or error dictionary on failure.
        """
        if policy_id not in self.policies:
            return {"error": f"Policy with ID '{policy_id}' not found"}
        
        valid_statuses = ["active", "expired", "canceled", "suspended"]
        if new_status not in valid_statuses:
            return {
                "error": f"Invalid status '{new_status}'. Valid statuses: {', '.join(valid_statuses)}"
            }
        
        old_status = self.policies[policy_id]["status"]
        self.policies[policy_id]["status"] = new_status
        
        return {
            "success": True,
            "message": f"Policy status updated from '{old_status}' to '{new_status}'",
            "policy": deepcopy(self.policies[policy_id])
        }
    
    def register_vehicle(
        self,
        vin: str,
        make: str,
        model: str,
        year: int,
        customer_id: str,
        policy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new vehicle to the system.
        
        Links it to a customer and optionally a policy.
        
        Args:
            vin: Vehicle Identification Number (must be unique).
            make: Vehicle manufacturer.
            model: Vehicle model name.
            year: Vehicle manufacturing year.
            customer_id: Customer who owns the vehicle.
            policy_id: Optional policy to link the vehicle to.
        
        Returns:
            Dict[str, Any]: Created vehicle details on success, or error dictionary on failure.
        """
        # Validate customer exists
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        # Constraint 3: VIN must be unique
        for vehicle in self.vehicles.values():
            if vehicle.get("VIN") == vin:
                return {"error": f"Vehicle with VIN '{vin}' already exists"}
        
        # Validate VIN format (basic check)
        if not vin or len(vin) < 10:
            return {"error": "Invalid VIN format. VIN must be at least 10 characters"}
        
        # Validate policy if provided
        if policy_id is not None:
            if policy_id not in self.policies:
                return {"error": f"Policy with ID '{policy_id}' not found"}
            # Verify policy belongs to the same customer
            policy = self.policies[policy_id]
            if policy.get("customer_id") != customer_id:
                return {
                    "error": f"Policy '{policy_id}' does not belong to customer '{customer_id}'"
                }
        
        # Create the vehicle
        vehicle_id = f"VEH{self.next_vehicle_id:03d}"
        self.next_vehicle_id += 1
        
        new_vehicle = {
            "vehicle_id": vehicle_id,
            "VIN": vin,
            "make": make,
            "model": model,
            "year": year,
            "customer_id": customer_id,
            "policy_id": policy_id
        }
        
        self.vehicles[vehicle_id] = new_vehicle
        
        return {
            "success": True,
            "message": "Vehicle registered successfully",
            "vehicle": deepcopy(new_vehicle)
        }
    
    def update_vehicle_policy_link(self, vehicle_id: str, new_policy_id: str) -> Dict[str, Any]:
        """
        Reassign a vehicle to a different policy.
        
        Used during policy renewal or transfer.
        
        Args:
            vehicle_id: The vehicle identifier to update.
            new_policy_id: The new policy to link the vehicle to.
        
        Returns:
            Dict[str, Any]: Updated vehicle details on success, or error dictionary on failure.
        """
        if vehicle_id not in self.vehicles:
            return {"error": f"Vehicle with ID '{vehicle_id}' not found"}
        
        if new_policy_id not in self.policies:
            return {"error": f"Policy with ID '{new_policy_id}' not found"}
        
        vehicle = self.vehicles[vehicle_id]
        policy = self.policies[new_policy_id]
        
        # Verify policy belongs to the same customer
        if policy.get("customer_id") != vehicle.get("customer_id"):
            return {
                "error": f"Cannot link vehicle to policy '{new_policy_id}': policy belongs to a different customer"
            }
        
        old_policy_id = vehicle.get("policy_id")
        self.vehicles[vehicle_id]["policy_id"] = new_policy_id
        
        return {
            "success": True,
            "message": f"Vehicle policy link updated from '{old_policy_id}' to '{new_policy_id}'",
            "vehicle": deepcopy(self.vehicles[vehicle_id])
        }
    
    def delete_claim(self, claim_id: str) -> Dict[str, Any]:
        """
        Remove a claim from the system.
        
        Subject to audit rules (cannot delete approved or denied claims).
        
        Args:
            claim_id: The claim identifier to delete.
        
        Returns:
            Dict[str, Any]: Success confirmation or error dictionary.
        """
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        claim = self.claims[claim_id]
        
        # Audit rule: Cannot delete claims that have been processed
        if claim.get("status") in ["approved", "denied"]:
            return {
                "error": f"Cannot delete claim '{claim_id}': claim has been processed (status: {claim.get('status')})"
            }
        
        deleted_claim = deepcopy(claim)
        del self.claims[claim_id]
        
        # Remove associated documents
        if claim_id in self.supporting_documents:
            del self.supporting_documents[claim_id]
        
        return {
            "success": True,
            "message": f"Claim '{claim_id}' deleted successfully",
            "deleted_claim": deleted_claim
        }
    
    def add_supporting_document(self, claim_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Add a supporting document to a claim."""
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        if claim_id not in self.supporting_documents:
            self.supporting_documents[claim_id] = []
        
        doc_id = f"DOC-{claim_id}-{len(self.supporting_documents[claim_id]) + 1}"
        document["document_id"] = doc_id
        document["uploaded_at"] = datetime.now().isoformat()
        
        self.supporting_documents[claim_id].append(document)
        
        return {
            "success": True,
            "document_id": doc_id,
            "message": f"Document added to claim '{claim_id}'"
        }
    
    def get_supporting_documents(self, claim_id: str) -> Dict[str, Any]:
        """Get all supporting documents for a claim."""
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        return {
            "claim_id": claim_id,
            "documents": self.supporting_documents.get(claim_id, [])
        }
    
    def calculate_claim_total(self, claim_id: str) -> Dict[str, Any]:
        """Calculate the total amount for a claim including all line items."""
        if claim_id not in self.claims:
            return {"error": f"Claim with ID '{claim_id}' not found"}
        
        claim = self.claims[claim_id]
        line_items = claim.get("line_items", [])
        
        total = sum(item.get("amount", 0) for item in line_items)
        
        return {
            "claim_id": claim_id,
            "line_items_count": len(line_items),
            "total_amount": total
        }
    
    def get_claims_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all claims with a specific status."""
        return [
            deepcopy(claim) for claim in self.claims.values()
            if claim.get("status") == status
        ]
    
    def get_claims_by_claimant(self, claimant_id: str) -> List[Dict[str, Any]]:
        """Get all claims for a specific claimant."""
        return [
            deepcopy(claim) for claim in self.claims.values()
            if claim.get("claimant_id") == claimant_id
        ]


__TEST_CASES__ = [
    {
        "name": "test_create_claim",
        "input": {
            "method": "create_claim",
            "args": {
                "claimant_id": "CLM-001",
                "claim_type": "medical",
                "description": "Hospital visit for annual checkup",
                "amount": 500.00
            }
        },
        "expected_keys": ["success", "claim_id", "message"]
    },
    {
        "name": "test_get_claim",
        "setup": {
            "method": "create_claim",
            "args": {
                "claimant_id": "CLM-002",
                "claim_type": "dental",
                "description": "Dental cleaning",
                "amount": 150.00
            }
        },
        "input": {
            "method": "get_claim",
            "args": {"claim_id": "__SETUP_CLAIM_ID__"}
        },
        "expected_keys": ["claim_id", "claimant_id", "claim_type", "status"]
    },
    {
        "name": "test_get_nonexistent_claim",
        "input": {
            "method": "get_claim",
            "args": {"claim_id": "INVALID-ID"}
        },
        "expected_keys": ["error"]
    },
    {
        "name": "test_update_claim_status",
        "setup": {
            "method": "create_claim",
            "args": {
                "claimant_id": "CLM-003",
                "claim_type": "vision",
                "description": "Eye exam",
                "amount": 200.00
            }
        },
        "input": {
            "method": "update_claim_status",
            "args": {
                "claim_id": "__SETUP_CLAIM_ID__",
                "new_status": "under_review",
                "reviewer_notes": "Reviewing submitted documents"
            }
        },
        "expected_keys": ["success", "claim_id", "old_status", "new_status"]
    },
    {
        "name": "test_delete_pending_claim",
        "setup": {
            "method": "create_claim",
            "args": {
                "claimant_id": "CLM-004",
                "claim_type": "medical",
                "description": "Prescription medication",
                "amount": 75.00
            }
        },
        "input": {
            "method": "delete_claim",
            "args": {"claim_id": "__SETUP_CLAIM_ID__"}
        },
        "expected_keys": ["success", "message", "deleted_claim"]
    },
    {
        "name": "test_delete_processed_claim_fails",
        "setup": [
            {
                "method": "create_claim",
                "args": {
                    "claimant_id": "CLM-005",
                    "claim_type": "medical",
                    "description": "Surgery",
                    "amount": 5000.00
                }
            },
            {
                "method": "update_claim_status",
                "args": {
                    "claim_id": "__SETUP_CLAIM_ID__",
                    "new_status": "approved"
                }
            }
        ],
        "input": {
            "method": "delete_claim",
            "args": {"claim_id": "__SETUP_CLAIM_ID__"}
        },
        "expected_keys": ["error"]
    },
    {
        "name": "test_add_supporting_document",
        "setup": {
            "method": "create_claim",
            "args": {
                "claimant_id": "CLM-006",
                "claim_type": "medical",
                "description": "Lab tests",
                "amount": 300.00
            }
        },
        "input": {
            "method": "add_supporting_document",
            "args": {
                "claim_id": "__SETUP_CLAIM_ID__",
                "document": {
                    "type": "receipt",
                    "filename": "lab_receipt.pdf",
                    "size_bytes": 102400
                }
            }
        },
        "expected_keys": ["success", "document_id", "message"]
    },
    {
        "name": "test_get_supporting_documents",
        "setup": [
            {
                "method": "create_claim",
                "args": {
                    "claimant_id": "CLM-007",
                    "claim_type": "dental",
                    "description": "Root canal",
                    "amount": 1200.00
                }
            },
            {
                "method": "add_supporting_document",
                "args": {
                    "claim_id": "__SETUP_CLAIM_ID__",
                    "document": {
                        "type": "invoice",
                        "filename": "dental_invoice.pdf"
                    }
                }
            }
        ],
        "input": {
            "method": "get_supporting_documents",
            "args": {"claim_id": "__SETUP_CLAIM_ID__"}
        },
        "expected_keys": ["claim_id", "documents"]
    },
    {
        "name": "test_calculate_claim_total",
        "setup": {
            "method": "create_claim",
            "args": {
                "claimant_id": "CLM-008",
                "claim_type": "medical",
                "description": "Multiple services",
                "amount": 0,
                "line_items": [
                    {"description": "Consultation", "amount": 100.00},
                    {"description": "X-ray", "amount": 250.00},
                    {"description": "Medication", "amount": 50.00}
                ]
            }
        },
        "input": {
            "method": "calculate_claim_total",
            "args": {"claim_id": "__SETUP_CLAIM_ID__"}
        },
        "expected": {
            "line_items_count": 3,
            "total_amount": 400.00
        }
    },
    {
        "name": "test_get_claims_by_status",
        "setup": [
            {
                "method": "create_claim",
                "args": {
                    "claimant_id": "CLM-009",
                    "claim_type": "medical",
                    "description": "Checkup",
                    "amount": 100.00
                }
            },
            {
                "method": "create_claim",
                "args": {
                    "claimant_id": "CLM-010",
                    "claim_type": "dental",
                    "description": "Cleaning",
                    "amount": 150.00
                }
            }
        ],
        "input": {
            "method": "get_claims_by_status",
            "args": {"status": "pending"}
        },
        "expected_type": "list",
        "expected_min_length": 2
    },
    {
        "name": "test_get_claims_by_claimant",
        "setup": [
            {
                "method": "create_claim",
                "args": {
                    "claimant_id": "CLM-MULTI",
                    "claim_type": "medical",
                    "description": "Visit 1",
                    "amount": 100.00
                }
            },
            {
                "method": "create_claim",
                "args": {
                    "claimant_id": "CLM-MULTI",
                    "claim_type": "dental",
                    "description": "Visit 2",
                    "amount": 200.00
                }
            }
        ],
        "input": {
            "method": "get_claims_by_claimant",
            "args": {"claimant_id": "CLM-MULTI"}
        },
        "expected_type": "list",
        "expected_length": 2
    },
    {
        "name": "test_list_all_claims",
        "setup": {
            "method": "create_claim",
            "args": {
                "claimant_id": "CLM-011",
                "claim_type": "vision",
                "description": "Glasses",
                "amount": 350.00
            }
        },
        "input": {
            "method": "list_claims",
            "args": {}
        },
        "expected_type": "list"
    }
]