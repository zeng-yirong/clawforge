"""
Restaurant Reservation System Environment API

A restaurant reservation system that maintains records of table availability,
guest bookings, and schedules for dining establishments.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, time

# Default initial state with sample data for all entities
DEFAULT_STATE: Dict[str, Any] = {
    "restaurants": [
        {
            "restaurant_id": "rest_001",
            "name": "The Golden Fork",
            "location": "123 Main Street, Downtown",
            "operating_hours": {"open": "11:00", "close": "22:00"},
            "max_party_size": 20,
            "cuisine": "American"
        },
        {
            "restaurant_id": "rest_002",
            "name": "Ocean Breeze",
            "location": "456 Beach Boulevard, Seaside",
            "operating_hours": {"open": "12:00", "close": "23:00"},
            "max_party_size": 15,
            "cuisine": "Seafood"
        },
        {
            "restaurant_id": "rest_003",
            "name": "Mountain View Bistro",
            "location": "789 Highland Avenue, Uptown",
            "operating_hours": {"open": "10:00", "close": "21:00"},
            "max_party_size": 12,
            "cuisine": "French"
        }
    ],
    "tables": [
        {
            "table_id": "tbl_001",
            "restaurant_id": "rest_001",
            "capacity": 2,
            "status": "available",
            "location": "Window"
        },
        {
            "table_id": "tbl_002",
            "restaurant_id": "rest_001",
            "capacity": 4,
            "status": "available",
            "location": "Center"
        },
        {
            "table_id": "tbl_003",
            "restaurant_id": "rest_001",
            "capacity": 6,
            "status": "reserved",
            "location": "Private Room"
        },
        {
            "table_id": "tbl_004",
            "restaurant_id": "rest_002",
            "capacity": 2,
            "status": "available",
            "location": "Patio"
        },
        {
            "table_id": "tbl_005",
            "restaurant_id": "rest_002",
            "capacity": 4,
            "status": "available",
            "location": "Main Hall"
        },
        {
            "table_id": "tbl_006",
            "restaurant_id": "rest_003",
            "capacity": 8,
            "status": "available",
            "location": "VIP Section"
        }
    ],
    "reservations": [
        {
            "reservation_id": "res_001",
            "restaurant_id": "rest_001",
            "table_id": "tbl_003",
            "guest_name": "John Smith",
            "guest_contact": "john.smith@email.com",
            "customer_id": "C001",
            "party_size": 5,
            "date": "2024-12-20",
            "start_time": "18:00",
            "end_time": "20:00",
            "status": "confirmed"
        },
        {
            "reservation_id": "res_002",
            "restaurant_id": "rest_002",
            "table_id": "tbl_005",
            "guest_name": "Jane Doe",
            "guest_contact": "jane.doe@email.com",
            "customer_id": "C002",
            "party_size": 3,
            "date": "2024-12-21",
            "start_time": "19:00",
            "end_time": "21:00",
            "status": "confirmed"
        },
        {
            "reservation_id": "res_003",
            "restaurant_id": "rest_001",
            "table_id": "tbl_002",
            "guest_name": "Bob Wilson",
            "guest_contact": "555-1234",
            "customer_id": "C003",
            "party_size": 4,
            "date": "2024-12-19",
            "start_time": "12:00",
            "end_time": "14:00",
            "status": "completed"
        }
    ],
    "availability_slots": [
        {
            "restaurant_id": "rest_001",
            "date": "2024-12-20",
            "time_slot": "18:00",
            "available_tables_count": 2
        },
        {
            "restaurant_id": "rest_001",
            "date": "2024-12-20",
            "time_slot": "20:00",
            "available_tables_count": 3
        },
        {
            "restaurant_id": "rest_002",
            "date": "2024-12-21",
            "time_slot": "19:00",
            "available_tables_count": 1
        }
    ],
    "current_user": None,
    "session": {
        "active": False,
        "last_activity": None
    },
    "next_reservation_id": 4,
    "current_timestamp": "2024-12-18T10:00:00"
}


class RestaurantReservationSystem:
    """
    A restaurant reservation system API that manages table availability,
    guest bookings, and schedules for dining establishments.
    
    This system tracks reservations by date, time, party size, and table assignment,
    ensuring no conflicts and enabling efficient service management.
    """
    
    def __init__(self) -> None:
        """
        Initialize the RestaurantReservationSystem with default state attributes.
        
        Declares all state attributes with type hints and sets up the API description.
        """
        self.restaurants: List[Dict[str, Any]] = []
        self.tables: List[Dict[str, Any]] = []
        self.reservations: List[Dict[str, Any]] = []
        self.availability_slots: List[Dict[str, Any]] = []
        self.current_user: Optional[str] = None
        self.session: Dict[str, Any] = {}
        self.next_reservation_id: int = 1
        self.current_timestamp: str = ""
        self.audit_log: List[Dict[str, Any]] = []  # added audit log
        
        self._api_description = "Restaurant reservation system for managing table bookings, availability, and guest reservations."
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp for operations.
        
        Returns:
            str: ISO format timestamp string.
        """
        return self.current_timestamp if self.current_timestamp else "2024-12-18T10:00:00"
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (unused but required for interface).
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
        Return the current state of the environment.
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables including:
                - restaurants: List of restaurant records
                - tables: List of table records
                - reservations: List of reservation records
                - availability_slots: List of availability slot records
                - current_user: Currently active user (if any)
                - session: Session information
                - next_reservation_id: Counter for generating reservation IDs
                - current_timestamp: Current system timestamp
                - audit_log: Audit log entries
        """
        return {
            "restaurants": deepcopy(self.restaurants),
            "tables": deepcopy(self.tables),
            "reservations": deepcopy(self.reservations),
            "availability_slots": deepcopy(self.availability_slots),
            "current_user": self.current_user,
            "session": deepcopy(self.session),
            "next_reservation_id": self.next_reservation_id,
            "current_timestamp": self.current_timestamp,
            "audit_log": deepcopy(self.audit_log)
        }
    
    def _parse_time(self, time_str: str) -> Optional[time]:
        """
        Parse a time string into a time object.
        
        Args:
            time_str: Time string in HH:MM format.
            
        Returns:
            Optional[time]: Parsed time object or None if parsing fails.
        """
        try:
            parts = time_str.split(":")
            return time(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError, AttributeError):
            return None
    
    def _times_overlap(self, start1: str, end1: str, start2: str, end2: str) -> bool:
        """
        Check if two time ranges overlap.
        
        Args:
            start1: Start time of first range.
            end1: End time of first range.
            start2: Start time of second range.
            end2: End time of second range.
            
        Returns:
            bool: True if ranges overlap, False otherwise.
        """
        t1_start = self._parse_time(start1)
        t1_end = self._parse_time(end1)
        t2_start = self._parse_time(start2)
        t2_end = self._parse_time(end2)
        
        if not all([t1_start, t1_end, t2_start, t2_end]):
            return False
        
        return t1_start < t2_end and t2_start < t1_end
    
    def _check_time_conflict(
        self,
        table_id: str,
        date: str,
        start_time: str,
        end_time: str,
        exclude_reservation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Internal method to check for time conflicts on a table.
        
        Args:
            table_id: The unique identifier of the table.
            date: The date to check (format: YYYY-MM-DD).
            start_time: Start time of the proposed reservation (format: HH:MM).
            end_time: End time of the proposed reservation (format: HH:MM).
            exclude_reservation_id: Optional reservation ID to exclude from conflict check.
            
        Returns:
            Dict[str, Any]: Dictionary with conflict status and details.
        """
        conflicts = []
        
        for reservation in self.reservations:
            if reservation["table_id"] != table_id:
                continue
            if reservation["date"] != date:
                continue
            # Include both confirmed and modified reservations as valid bookings
            if reservation["status"] not in ["confirmed", "modified"]:
                continue
            if exclude_reservation_id and reservation["reservation_id"] == exclude_reservation_id:
                continue
            
            if self._times_overlap(
                start_time, end_time,
                reservation["start_time"], reservation["end_time"]
            ):
                conflicts.append({
                    "reservation_id": reservation["reservation_id"],
                    "start_time": reservation["start_time"],
                    "end_time": reservation["end_time"]
                })
        
        return {
            "has_conflict": len(conflicts) > 0,
            "conflicts": conflicts,
            "table_id": table_id,
            "date": date,
            "checked_time_range": {
                "start_time": start_time,
                "end_time": end_time
            }
        }
    
    # ==================== Query Operations ====================
    
    def get_restaurant_by_name(self, name: str) -> Dict[str, Any]:
        """
        Retrieve restaurant information by name.
        
        Args:
            name: The name of the restaurant to search for.
            
        Returns:
            Dict[str, Any]: Restaurant details including id, location, and operating hours,
                or an error dictionary if not found.
        """
        if not name:
            return {"error": "Restaurant name is required"}
        
        for restaurant in self.restaurants:
            if restaurant["name"].lower() == name.lower():
                return {
                    "restaurant_id": restaurant["restaurant_id"],
                    "name": restaurant["name"],
                    "location": restaurant.get("location", ""),
                    "operating_hours": restaurant["operating_hours"]
                }
        return {"error": f"Restaurant with name '{name}' not found"}
    
    def get_restaurant_by_id(self, restaurant_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a restaurant using its unique identifier.
        
        Args:
            restaurant_id: The unique identifier of the restaurant.
            
        Returns:
            Dict[str, Any]: Complete restaurant details or an error dictionary if not found.
        """
        if not restaurant_id:
            return {"error": "Restaurant ID is required"}
        
        for restaurant in self.restaurants:
            if restaurant["restaurant_id"] == restaurant_id:
                return deepcopy(restaurant)
        return {"error": f"Restaurant with id '{restaurant_id}' not found"}
    
    def check_operating_hours(
        self, 
        restaurant_id: str, 
        date: str, 
        time_to_check: str
    ) -> Dict[str, Any]:
        """
        Verify if a given date and time fall within the restaurant's operating hours.
        
        Args:
            restaurant_id: The unique identifier of the restaurant.
            date: The date to check (format: YYYY-MM-DD).
            time_to_check: The time to check (format: HH:MM).
            
        Returns:
            Dict[str, Any]: Dictionary with 'within_hours' boolean and operating hours info,
                or an error dictionary if restaurant not found.
        """
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if "error" in restaurant:
            return restaurant
        
        check_time = self._parse_time(time_to_check)
        if not check_time:
            return {"error": f"Invalid time format: '{time_to_check}'"}
        
        open_time = self._parse_time(restaurant["operating_hours"]["open"])
        close_time = self._parse_time(restaurant["operating_hours"]["close"])
        
        within_hours = open_time <= check_time <= close_time
        
        return {
            "within_hours": within_hours,
            "operating_hours": restaurant["operating_hours"],
            "checked_time": time_to_check,
            "date": date
        }
    
    def search_available_tables(
        self, 
        restaurant_id: str, 
        required_capacity: int, 
        date: str, 
        start_time: str, 
        end_time: str
    ) -> Dict[str, Any]:
        """
        Find all tables at a restaurant that match capacity and are available during a time slot.
        
        Args:
            restaurant_id: The unique identifier of the restaurant.
            required_capacity: Minimum seating capacity needed.
            date: The date for the reservation (format: YYYY-MM-DD).
            start_time: Start time of the desired slot (format: HH:MM).
            end_time: End time of the desired slot (format: HH:MM).
            
        Returns:
            Dict[str, Any]: Dictionary with list of available tables or error message.
        """
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if "error" in restaurant:
            return restaurant
        
        available_tables = []
        
        for table in self.tables:
            if table["restaurant_id"] != restaurant_id:
                continue
            if table["capacity"] < required_capacity:
                continue
            if table["status"] not in ["available", "reserved"]:
                continue
            
            availability = self.check_table_availability(
                table["table_id"], date, start_time, end_time
            )
            if availability.get("is_available", False):
                available_tables.append(deepcopy(table))
        
        return {
            "available_tables": available_tables,
            "count": len(available_tables),
            "search_criteria": {
                "restaurant_id": restaurant_id,
                "required_capacity": required_capacity,
                "date": date,
                "start_time": start_time,
                "end_time": end_time
            }
        }
    
    def check_availability(
        self,
        restaurant_id: str,
        date: str,
        start_time: str,
        end_time: str,
        party_size: int
    ) -> Dict[str, Any]:
        """
        Check if any tables are available for the given criteria.
        
        Args:
            restaurant_id: The unique identifier of the restaurant.
            date: The date to check (YYYY-MM-DD).
            start_time: Start time (HH:MM).
            end_time: End time (HH:MM).
            party_size: Number of guests.
            
        Returns:
            Dict[str, Any]: Dictionary with 'available' boolean.
        """
        result = self.search_available_tables(restaurant_id, party_size, date, start_time, end_time)
        if "error" in result:
            return {"success": False, "error": result["error"], "available": False}
            
        count = result.get("count", 0)
        return {"success": True, "available": count > 0}
    
    def check_table_availability(
        self, 
        table_id: str, 
        date: str, 
        start_time: str, 
        end_time: str
    ) -> Dict[str, Any]:
        """
        Determine if a specific table is available for booking during a given time range.
        
        Args:
            table_id: The unique identifier of the table.
            date: The date to check (format: YYYY-MM-DD).
            start_time: Start time of the desired slot (format: HH:MM).
            end_time: End time of the desired slot (format: HH:MM).
            
        Returns:
            Dict[str, Any]: Dictionary with availability status and any conflicting reservations.
        """
        table = None
        for t in self.tables:
            if t["table_id"] == table_id:
                table = t
                break
        
        if not table:
            return {"error": f"Table with id '{table_id}' not found"}
        
        if table["status"] == "occupied":
            return {
                "is_available": False,
                "reason": "Table is currently occupied",
                "table_id": table_id
            }
        
        for reservation in self.reservations:
            if (reservation["table_id"] == table_id and 
                reservation["date"] == date and 
                reservation["status"] in ["confirmed", "modified"]):  # Include modified bookings
                if self._times_overlap(
                    start_time, end_time,
                    reservation["start_time"], reservation["end_time"]
                ):
                    return {
                        "is_available": False,
                        "reason": "Time conflict with existing reservation",
                        "conflicting_reservation_id": reservation["reservation_id"],
                        "table_id": table_id
                    }
        
        return {
            "is_available": True,
            "table_id": table_id,
            "date": date,
            "start_time": start_time,
            "end_time": end_time
        }
    
    def get_availability_slot(
        self, 
        restaurant_id: str, 
        date: str, 
        time_slot: str
    ) -> Dict[str, Any]:
        """
        Retrieve the number of available tables for a restaurant at a specific date and time slot.
        This method now computes availability in real-time based on current reservations.
        
        Args:
            restaurant_id: The unique identifier of the restaurant.
            date: The date to check (format: YYYY-MM-DD).
            time_slot: The time slot to check (format: HH:MM).
            
        Returns:
            Dict[str, Any]: Dictionary with available tables count or error message.
        """
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if "error" in restaurant:
            return restaurant
        
        # Real-time computation: count tables that have no conflicting reservation at that time point
        available_count = 0
        check_time = self._parse_time(time_slot)
        if not check_time:
            return {"error": f"Invalid time slot format: '{time_slot}'"}
        
        for table in self.tables:
            if table["restaurant_id"] != restaurant_id:
                continue
            # Consider table available if its status is not 'occupied' (which is a global flag)
            # and no reservation occupies it at this exact time point
            is_occupied = False
            for res in self.reservations:
                if (res["table_id"] == table["table_id"] and
                    res["date"] == date and
                    res["status"] in ["confirmed", "modified"]):
                    res_start = self._parse_time(res["start_time"])
                    res_end = self._parse_time(res["end_time"])
                    if res_start and res_end and res_start <= check_time < res_end:
                        is_occupied = True
                        break
            if not is_occupied:
                available_count += 1
        
        return {
            "restaurant_id": restaurant_id,
            "date": date,
            "time_slot": time_slot,
            "available_tables_count": available_count,
            "note": "Real-time computed from reservations"
        }
    
    def list_reservations_by_restaurant(
        self, 
        restaurant_id: str, 
        date: str
    ) -> Dict[str, Any]:
        """
        Retrieve all reservations for a given restaurant on a specific date.
        
        Args:
            restaurant_id: The unique identifier of the restaurant.
            date: The date to filter by (format: YYYY-MM-DD).
            
        Returns:
            Dict[str, Any]: Dictionary with list of reservations or error message.
        """
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if "error" in restaurant:
            return restaurant
        
        matching_reservations = [
            deepcopy(r) for r in self.reservations
            if r["restaurant_id"] == restaurant_id and r["date"] == date
        ]
        
        return {
            "reservations": matching_reservations,
            "count": len(matching_reservations),
            "restaurant_id": restaurant_id,
            "date": date
        }
    
    def list_reservations_by_guest(
        self, 
        guest_name: Optional[str] = None, 
        guest_contact: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve all reservations made by a guest using their name or contact.
        When both name and contact are provided, both must match.
        
        Args:
            guest_name: The name of the guest (optional).
            guest_contact: The contact information of the guest (optional).
            
        Returns:
            Dict[str, Any]: Dictionary with list of reservations or error message.
        """
        if not guest_name and not guest_contact:
            return {"error": "At least one of guest_name or guest_contact must be provided"}
        
        matching_reservations = []
        for r in self.reservations:
            match = False
            if guest_name and guest_contact:
                # Both provided: require both match
                if (r["guest_name"].lower() == guest_name.lower() and
                    r["guest_contact"].lower() == guest_contact.lower()):
                    match = True
            elif guest_name:
                if r["guest_name"].lower() == guest_name.lower():
                    match = True
            elif guest_contact:
                if r["guest_contact"].lower() == guest_contact.lower():
                    match = True
            if match:
                matching_reservations.append(deepcopy(r))
        
        return {
            "reservations": matching_reservations,
            "count": len(matching_reservations),
            "search_criteria": {
                "guest_name": guest_name,
                "guest_contact": guest_contact
            }
        }
    
    def check_time_conflict(
        self, 
        table_id: str, 
        date: str, 
        start_time: str, 
        end_time: str, 
        exclude_reservation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determine whether a new reservation overlaps with any existing reservation for a table.
        
        Args:
            table_id: The unique identifier of the table.
            date: The date to check (format: YYYY-MM-DD).
            start_time: Start time of the proposed reservation (format: HH:MM).
            end_time: End time of the proposed reservation (format: HH:MM).
            exclude_reservation_id: Optional reservation ID to exclude from conflict check.
            
        Returns:
            Dict[str, Any]: Dictionary with conflict status and details.
        """
        return self._check_time_conflict(table_id, date, start_time, end_time, exclude_reservation_id)
    
    def update_availability_slot(
        self,
        restaurant_id: str,
        date: str,
        time_slot: str,
        delta: int
    ) -> Dict[str, Any]:
        """
        Update the available tables count for a specific time slot.
        NOTE: This method is kept for compatibility but availability is now computed dynamically.
              The actual availability_slots list is no longer used by get_availability_slot.
        Args:
            restaurant_id: The unique identifier of the restaurant.
            date: The date of the slot (format: YYYY-MM-DD).
            time_slot: The time slot to update (format: HH:MM).
            delta: The change in available tables count (positive or negative).
            
        Returns:
            Dict[str, Any]: Updated slot information or error message.
        """
        for slot in self.availability_slots:
            if (slot["restaurant_id"] == restaurant_id and
                slot["date"] == date and
                slot["time_slot"] == time_slot):
                slot["available_tables_count"] = max(0, slot["available_tables_count"] + delta)
                return {
                    "success": True,
                    "slot": deepcopy(slot)
                }
        
        # Create new slot if not exists
        new_slot = {
            "restaurant_id": restaurant_id,
            "date": date,
            "time_slot": time_slot,
            "available_tables_count": max(0, delta)
        }
        self.availability_slots.append(new_slot)
        return {
            "success": True,
            "slot": deepcopy(new_slot),
            "created": True
        }
    
    # ==================== State Change Operations ====================
    
    def add_restaurant(
        self,
        restaurant_id: str,
        name: str,
        cuisine: str,
        max_party_size: int,
        opening_time: str,
        closing_time: str
    ) -> Dict[str, Any]:
        """
        Add a new restaurant to the system.
        
        Args:
            restaurant_id: Unique identifier for the new restaurant.
            name: Name of the restaurant.
            cuisine: Cuisine type.
            max_party_size: Maximum party size allowed.
            opening_time: Opening time (HH:MM).
            closing_time: Closing time (HH:MM).
            
        Returns:
            Dict[str, Any]: Success status and message.
        """
        for r in self.restaurants:
            if r["restaurant_id"] == restaurant_id:
                return {"success": False, "error": f"Restaurant {restaurant_id} already exists"}
                
        self.restaurants.append({
            "restaurant_id": restaurant_id,
            "name": name,
            "cuisine": cuisine,
            "max_party_size": max_party_size,
            "location": "",
            "operating_hours": {"open": opening_time, "close": closing_time}
        })
        
        # Audit log
        self.audit_log.append({
            "timestamp": self._timestamp(),
            "action": "add_restaurant",
            "details": {"restaurant_id": restaurant_id, "name": name}
        })
        
        return {"success": True, "message": "Restaurant added successfully"}
    
    def create_reservation(
        self,
        customer_name: str,
        date: str,
        start_time: str,
        end_time: str,
        party_size: int,
        customer_id: Optional[str] = None,
        restaurant_id: Optional[str] = None,
        table_id: Optional[str] = None,
        preferred_table_id: Optional[str] = None,
        guest_contact: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Book a table by creating a new reservation.
        
        Args:
            customer_name: Name of the customer making the reservation.
            date: Date of the reservation (format: YYYY-MM-DD).
            start_time: Start time of the reservation (format: HH:MM).
            end_time: End time of the reservation (format: HH:MM).
            party_size: Number of guests in the party.
            customer_id: The unique identifier of the customer (optional).
            restaurant_id: The unique identifier of the restaurant (optional, defaults to first restaurant).
            table_id: The unique identifier of the table to reserve (optional, auto-assigned if not provided).
            preferred_table_id: Preferred table ID if specific table is requested (optional).
            guest_contact: Contact information for the guest (optional).
            
        Returns:
            Dict[str, Any]: Created reservation details or error message.
        """
        if not customer_name:
            return {"success": False, "error": "Customer name is required"}
            
        customer_id = customer_id or f"C_{self.next_reservation_id:03d}"
        
        if party_size <= 0:
            return {"success": False, "error": "Party size must be a positive number"}
        
        # Use preferred_table_id if provided, otherwise use table_id
        target_table_id = preferred_table_id or table_id
        
        # Default to first restaurant if not specified
        if not restaurant_id:
            if self.restaurants:
                restaurant_id = self.restaurants[0]["restaurant_id"]
            else:
                return {"success": False, "error": "No restaurants available"}
        
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if "error" in restaurant:
            return {"success": False, "error": restaurant["error"]}
        
        # Check restaurant max_party_size
        if "max_party_size" in restaurant and party_size > restaurant["max_party_size"]:
            return {
                "success": False,
                "error": f"Party size exceeds restaurant maximum of {restaurant['max_party_size']}"
            }
        
        # Check operating hours
        hours_check = self.check_operating_hours(restaurant_id, date, start_time)
        if "error" in hours_check:
            return {"success": False, "error": hours_check["error"]}
        if not hours_check.get("within_hours", False):
            return {"success": False, "error": "Reservation start time is outside operating hours"}
        
        end_hours_check = self.check_operating_hours(restaurant_id, date, end_time)
        if "error" in end_hours_check:
            return {"success": False, "error": end_hours_check["error"]}
        if not end_hours_check.get("within_hours", False):
            return {"success": False, "error": "Reservation end time is outside operating hours"}
        
        # Find suitable table
        selected_table = None
        
        if target_table_id:
            # Check specific table
            for t in self.tables:
                if t["table_id"] == target_table_id:
                    selected_table = t
                    break
            
            if not selected_table:
                return {"success": False, "error": f"Table with id '{target_table_id}' not found"}
            
            if selected_table["restaurant_id"] != restaurant_id:
                return {"success": False, "error": "Table does not belong to the specified restaurant"}
            
            if party_size > selected_table["capacity"]:
                return {
                    "success": False,
                    "error": f"Party size ({party_size}) exceeds table capacity ({selected_table['capacity']})"
                }
            
            conflict_check = self._check_time_conflict(target_table_id, date, start_time, end_time)
            if conflict_check.get("has_conflict", False):
                return {
                    "success": False,
                    "error": "Time conflict with existing reservation",
                    "conflicts": conflict_check["conflicts"]
                }
        else:
            # Auto-assign table
            available_result = self.search_available_tables(
                restaurant_id, party_size, date, start_time, end_time
            )
            if "error" in available_result:
                return {"success": False, "error": available_result["error"]}
            
            available_tables = available_result.get("available_tables", [])
            if not available_tables:
                return {"success": False, "error": "No available tables for the requested party size and time"}
            
            # Select smallest suitable table
            available_tables.sort(key=lambda x: x["capacity"])
            selected_table = available_tables[0]
        
        # Create reservation
        reservation_id = f"res_{self.next_reservation_id:03d}"
        self.next_reservation_id += 1
        
        new_reservation = {
            "reservation_id": reservation_id,
            "restaurant_id": restaurant_id,
            "table_id": selected_table["table_id"],
            "guest_name": customer_name,
            "guest_contact": guest_contact or "",
            "customer_id": customer_id,
            "party_size": party_size,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "status": "confirmed",
            "created_at": self._timestamp()
        }
        
        self.reservations.append(new_reservation)
        
        # Update table status
        for t in self.tables:
            if t["table_id"] == selected_table["table_id"]:
                t["status"] = "reserved"
                break
        
        # Audit log
        self.audit_log.append({
            "timestamp": self._timestamp(),
            "action": "create_reservation",
            "details": {"reservation_id": reservation_id, "table_id": selected_table["table_id"]}
        })
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "table_id": selected_table["table_id"],
            "status": "confirmed",
            "reservation": deepcopy(new_reservation),
            "message": "Reservation created successfully"
        }
    
    def cancel_reservation(self, reservation_id: str) -> Dict[str, Any]:
        """
        Cancel an existing reservation.
        
        Args:
            reservation_id: The unique identifier of the reservation to cancel.
            
        Returns:
            Dict[str, Any]: Cancellation confirmation or error message.
        """
        if not reservation_id:
            return {"success": False, "error": "Reservation ID is required"}
        
        reservation = None
        for r in self.reservations:
            if r["reservation_id"] == reservation_id:
                reservation = r
                break
        
        if not reservation:
            return {"success": False, "error": f"Reservation with id '{reservation_id}' not found"}
        
        if reservation["status"] == "cancelled":
            return {"success": False, "error": "Reservation is already cancelled"}
        
        if reservation["status"] == "completed":
            return {"success": False, "error": "Cannot cancel a completed reservation"}
        
        old_table_id = reservation["table_id"]
        old_restaurant_id = reservation["restaurant_id"]
        old_date = reservation["date"]
        old_start_time = reservation["start_time"]
        
        reservation["status"] = "cancelled"
        reservation["cancelled_at"] = self._timestamp()
        
        # Update table status if no other active reservations on that table
        has_other_reservations = any(
            r["table_id"] == old_table_id and 
            r["status"] in ["confirmed", "modified"] and 
            r["reservation_id"] != reservation_id
            for r in self.reservations
        )
        
        if not has_other_reservations:
            for t in self.tables:
                if t["table_id"] == old_table_id:
                    t["status"] = "available"
                    break
        
        # Audit log
        self.audit_log.append({
            "timestamp": self._timestamp(),
            "action": "cancel_reservation",
            "details": {"reservation_id": reservation_id}
        })
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "message": "Reservation cancelled successfully"
        }
    
    def _update_table_status(self, table_id: str) -> None:
        """
        Update the global status of a table based on active reservations.
        """
        has_active = any(
            r["table_id"] == table_id and r["status"] in ["confirmed", "modified"]
            for r in self.reservations
        )
        for t in self.tables:
            if t["table_id"] == table_id:
                t["status"] = "reserved" if has_active else "available"
                break
    
    def modify_reservation(
        self,
        reservation_id: str,
        new_party_size: Optional[int] = None,
        new_date: Optional[str] = None,
        new_start_time: Optional[str] = None,
        new_end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing reservation. Handles table reassignment if necessary.
        
        Args:
            reservation_id: The unique identifier of the reservation to update.
            new_party_size: Optional new number of guests.
            new_date: Optional new date in YYYY-MM-DD format.
            new_start_time: Optional new start time in HH:MM format.
            new_end_time: Optional new end time in HH:MM format.
            
        Returns:
            A dictionary containing success status and updated reservation details.
        """
        reservation = None
        for r in self.reservations:
            if r["reservation_id"] == reservation_id:
                reservation = r
                break
                
        if not reservation:
            return {
                "success": False,
                "error": f"Reservation {reservation_id} not found"
            }
        
        if reservation["status"] == "cancelled":
            return {
                "success": False,
                "error": "Cannot modify a cancelled reservation"
            }
        
        # Store original values
        original_date = reservation["date"]
        original_start_time = reservation["start_time"]
        original_end_time = reservation["end_time"]
        original_party_size = reservation["party_size"]
        original_table_id = reservation["table_id"]
        original_restaurant_id = reservation["restaurant_id"]
        
        # Determine new values
        target_date = new_date if new_date else original_date
        target_start_time = new_start_time if new_start_time else original_start_time
        target_end_time = new_end_time if new_end_time else original_end_time
        target_party_size = new_party_size if new_party_size else original_party_size
        
        # Validate new party size against restaurant max_party_size
        if new_party_size is not None:
            restaurant = None
            for rest in self.restaurants:
                if rest["restaurant_id"] == reservation["restaurant_id"]:
                    restaurant = rest
                    break
                    
            if restaurant and "max_party_size" in restaurant and new_party_size > restaurant["max_party_size"]:
                return {
                    "success": False,
                    "error": f"Party size exceeds maximum of {restaurant['max_party_size']}"
                }
        
        # Determine if table reassignment is needed
        needs_new_table = (new_date or new_start_time or new_end_time or 
                          (new_party_size is not None and new_party_size != original_party_size))
        
        new_table_id = None
        if needs_new_table:
            # First, try the current table if constraints allow
            current_table_capacity = None
            for t in self.tables:
                if t["table_id"] == original_table_id:
                    current_table_capacity = t["capacity"]
                    break
            
            current_table_works = True
            if current_table_capacity is not None and target_party_size > current_table_capacity:
                current_table_works = False
            else:
                # Check time conflict on current table (exclude self)
                conflict = self._check_time_conflict(
                    original_table_id, target_date, target_start_time, target_end_time,
                    exclude_reservation_id=reservation_id
                )
                if conflict.get("has_conflict", False):
                    current_table_works = False
            
            if current_table_works:
                new_table_id = original_table_id
            else:
                # Search for a new suitable table
                available_result = self.search_available_tables(
                    original_restaurant_id, target_party_size, target_date, target_start_time, target_end_time
                )
                if "error" in available_result:
                    return {"success": False, "error": available_result["error"]}
                
                available_tables = available_result.get("available_tables", [])
                if not available_tables:
                    return {"success": False, "error": "No available tables for the new time or party size"}
                
                available_tables.sort(key=lambda x: x["capacity"])
                new_table_id = available_tables[0]["table_id"]
        else:
            new_table_id = original_table_id
        
        # Apply modifications
        reservation["party_size"] = target_party_size
        reservation["date"] = target_date
        reservation["start_time"] = target_start_time
        reservation["end_time"] = target_end_time
        reservation["table_id"] = new_table_id
        reservation["status"] = "modified"  # Mark as modified (still considered valid occupation)
        
        # Update table statuses if table changed
        if new_table_id != original_table_id:
            self._update_table_status(original_table_id)
            self._update_table_status(new_table_id)
        # Also update original table status if it might have been the only active reservation
        else:
            self._update_table_status(original_table_id)
        
        # Audit log
        self.audit_log.append({
            "timestamp": self._timestamp(),
            "action": "modify_reservation",
            "details": {
                "reservation_id": reservation_id,
                "old_table_id": original_table_id,
                "new_table_id": new_table_id,
                "old_date": original_date,
                "new_date": target_date,
                "old_start_time": original_start_time,
                "new_start_time": target_start_time
            }
        })
        
        return {
            "success": True,
            "reservation": deepcopy(reservation),
            "message": "Reservation modified successfully"
        }
    
    def get_reservation(self, reservation_id: str) -> Dict[str, Any]:
        """
        Retrieve details of a specific reservation.
        
        Args:
            reservation_id: The unique identifier of the reservation.
            
        Returns:
            A dictionary containing the reservation details or an error.
        """
        reservation = None
        for r in self.reservations:
            if r["reservation_id"] == reservation_id:
                reservation = r
                break
                
        if not reservation:
            return {
                "success": False,
                "error": f"Reservation {reservation_id} not found"
            }
        
        return {
            "success": True,
            "reservation": deepcopy(reservation)
        }
    
    def list_reservations(
        self,
        customer_name: Optional[str] = None,
        restaurant_id: Optional[str] = None,
        date: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List reservations with optional filtering.
        
        Args:
            customer_name: Filter by customer name.
            restaurant_id: Filter by restaurant ID.
            date: Filter by date in YYYY-MM-DD format.
            status: Filter by reservation status.
            
        Returns:
            A dictionary containing the list of matching reservations.
        """
        results = []
        
        for reservation in self.reservations:
            if customer_name and reservation.get("guest_name") != customer_name:
                continue
            if restaurant_id and reservation.get("restaurant_id") != restaurant_id:
                continue
            if date and reservation.get("date") != date:
                continue
            if status and reservation.get("status") != status:
                continue
            results.append(deepcopy(reservation))
        
        return {
            "success": True,
            "reservations": results,
            "count": len(results)
        }


__TEST_CASES__ = [
    {
        "name": "test_add_restaurant",
        "input": {
            "method": "add_restaurant",
            "params": {
                "restaurant_id": "rest_004",
                "name": "The Golden Fork 2",
                "cuisine": "Italian",
                "max_party_size": 8,
                "opening_time": "11:00",
                "closing_time": "22:00"
            }
        },
        "expected": {
            "success": True
        }
    },
    {
        "name": "test_check_availability",
        "input": {
            "method": "check_availability",
            "params": {
                "restaurant_id": "rest_001",
                "date": "2024-12-16",
                "start_time": "12:00",
                "end_time": "14:00",
                "party_size": 2
            }
        },
        "expected": {
            "available": True
        }
    },
    {
        "name": "test_create_reservation_party_too_large",
        "input": {
            "method": "create_reservation",
            "params": {
                "restaurant_id": "rest_001",
                "customer_name": "Jane Smith",
                "party_size": 25,
                "date": "2024-12-15",
                "start_time": "19:00",
                "end_time": "21:00"
            }
        },
        "expected": {
            "success": False
        }
    },
    {
        "name": "test_cancel_nonexistent_reservation",
        "input": {
            "method": "cancel_reservation",
            "params": {
                "reservation_id": "res_999"
            }
        },
        "expected": {
            "success": False
        }
    },
    {
        "name": "test_modify_reservation_party_size",
        "input": {
            "method": "modify_reservation",
            "params": {
                "reservation_id": "res_001",
                "new_party_size": 6
            }
        },
        "expected": {
            "success": True
        }
    }
]