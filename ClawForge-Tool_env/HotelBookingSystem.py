"""
Hotel Booking System Environment API

A stateful digital platform that manages room inventory, pricing, availability,
and reservations over time. It tracks check-in and check-out dates, customer
bookings, and room types across various properties.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


# Default initial state with sample data for all entities
DEFAULT_STATE: Dict[str, Any] = {
    "hotels": {
        "hotel_001": {
            "hotel_id": "hotel_001",
            "name": "Grand Plaza Hotel",
            "location": "New York",
            "address": "123 5th Avenue, New York, NY 10001",
            "star_rating": 5,
            "amenities": ["pool", "spa", "gym", "restaurant", "wifi", "parking"]
        },
        "hotel_002": {
            "hotel_id": "hotel_002",
            "name": "Seaside Resort",
            "location": "Miami",
            "address": "456 Ocean Drive, Miami, FL 33139",
            "star_rating": 4,
            "amenities": ["beach_access", "pool", "restaurant", "wifi", "bar"]
        },
        "hotel_003": {
            "hotel_id": "hotel_003",
            "name": "Mountain Lodge",
            "location": "Denver",
            "address": "789 Peak Street, Denver, CO 80202",
            "star_rating": 3,
            "amenities": ["ski_storage", "fireplace", "restaurant", "wifi"]
        },
        "hotel_004": {
            "hotel_id": "hotel_004",
            "name": "City Center Inn",
            "location": "New York",
            "address": "321 Broadway, New York, NY 10012",
            "star_rating": 3,
            "amenities": ["wifi", "breakfast", "business_center"]
        }
    },
    "rooms": {
        "room_001": {
            "room_id": "room_001",
            "hotel_id": "hotel_001",
            "room_type": "deluxe",
            "price_per_night": 350.00,
            "capacity": 2,
            "amenities": ["king_bed", "city_view", "minibar", "jacuzzi"]
        },
        "room_002": {
            "room_id": "room_002",
            "hotel_id": "hotel_001",
            "room_type": "standard",
            "price_per_night": 200.00,
            "capacity": 2,
            "amenities": ["queen_bed", "wifi", "tv"]
        },
        "room_003": {
            "room_id": "room_003",
            "hotel_id": "hotel_001",
            "room_type": "suite",
            "price_per_night": 550.00,
            "capacity": 4,
            "amenities": ["two_bedrooms", "living_room", "kitchen", "balcony"]
        },
        "room_004": {
            "room_id": "room_004",
            "hotel_id": "hotel_002",
            "room_type": "ocean_view",
            "price_per_night": 280.00,
            "capacity": 2,
            "amenities": ["king_bed", "ocean_view", "balcony"]
        },
        "room_005": {
            "room_id": "room_005",
            "hotel_id": "hotel_002",
            "room_type": "standard",
            "price_per_night": 180.00,
            "capacity": 2,
            "amenities": ["queen_bed", "wifi", "tv"]
        },
        "room_006": {
            "room_id": "room_006",
            "hotel_id": "hotel_003",
            "room_type": "cabin",
            "price_per_night": 220.00,
            "capacity": 4,
            "amenities": ["two_beds", "fireplace", "mountain_view"]
        },
        "room_007": {
            "room_id": "room_007",
            "hotel_id": "hotel_004",
            "room_type": "standard",
            "price_per_night": 150.00,
            "capacity": 2,
            "amenities": ["queen_bed", "wifi", "desk"]
        }
    },
    "reservations": {
        "res_001": {
            "reservation_id": "res_001",
            "room_id": "room_001",
            "customer_id": "cust_001",
            "check_in_date": "2025-02-01",
            "check_out_date": "2025-02-05",
            "status": "confirmed"
        },
        "res_002": {
            "reservation_id": "res_002",
            "room_id": "room_004",
            "customer_id": "cust_002",
            "check_in_date": "2025-02-10",
            "check_out_date": "2025-02-15",
            "status": "confirmed"
        },
        "res_003": {
            "reservation_id": "res_003",
            "room_id": "room_002",
            "customer_id": "cust_003",
            "check_in_date": "2025-01-20",
            "check_out_date": "2025-01-25",
            "status": "completed"
        }
    },
    "customers": {
        "cust_001": {
            "customer_id": "cust_001",
            "name": "John Smith",
            "contact_info": {
                "email": "john.smith@email.com",
                "phone": "+1-555-0101"
            },
            "booking_history": ["res_001"]
        },
        "cust_002": {
            "customer_id": "cust_002",
            "name": "Emily Johnson",
            "contact_info": {
                "email": "emily.j@email.com",
                "phone": "+1-555-0102"
            },
            "booking_history": ["res_002"]
        },
        "cust_003": {
            "customer_id": "cust_003",
            "name": "Michael Brown",
            "contact_info": {
                "email": "m.brown@email.com",
                "phone": "+1-555-0103"
            },
            "booking_history": ["res_003"]
        }
    },
    "current_user": None,
    "session": {
        "active": False,
        "user_id": None,
        "login_time": None
    },
    "next_reservation_id": 4,
    "next_room_id": 8,
    "next_customer_id": 4
}


class HotelBookingSystem:
    """
    A hotel booking system environment API that manages room inventory,
    pricing, availability, and reservations over time.
    
    This system tracks check-in and check-out dates, customer bookings,
    and room types across various properties, enabling users to search,
    book, and modify stays while maintaining consistency by preventing
    double bookings and updating availability in real time.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Hotel Booking System environment.
        
        Declares all state attributes with type hints and sets up
        the API description for the environment.
        
        Args:
            None
            
        Returns:
            None
        """
        self._api_description: str = (
            "A hotel booking system that manages room inventory, pricing, "
            "availability, and reservations across multiple properties."
        )
        
        # State attributes with type hints
        self.hotels: Dict[str, Dict[str, Any]] = {}
        self.rooms: Dict[str, Dict[str, Any]] = {}
        self.reservations: Dict[str, Dict[str, Any]] = {}
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.current_user: Optional[str] = None
        self.session: Dict[str, Any] = {}
        self.next_reservation_id: int = 1
        self.next_room_id: int = 1
        self.next_customer_id: int = 1
    
    def _timestamp(self) -> str:
        """
        Generate a unified ISO format timestamp string.
        
        This method provides a single point for timestamp generation,
        allowing for easy injection of fixed times during testing.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from the provided scenario dictionary.
        
        If a key is not present in the scenario, falls back to the
        corresponding value from DEFAULT_STATE using deepcopy.
        
        Args:
            scenario: Dictionary containing initial state values to load.
            long_context: Flag for extended context scenarios (reserved).
            
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
        Return a dictionary containing all current environment state variables.
        
        This method provides a snapshot of the complete internal state
        of the hotel booking system for inspection or persistence.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary with keys:
                - hotels: All hotel records keyed by hotel_id
                - rooms: All room records keyed by room_id
                - reservations: All reservation records keyed by reservation_id
                - customers: All customer records keyed by customer_id
                - current_user: Currently logged in user ID or None
                - session: Current session information
                - next_reservation_id: Counter for generating reservation IDs
                - next_room_id: Counter for generating room IDs
                - next_customer_id: Counter for generating customer IDs
        """
        return {
            "hotels": deepcopy(self.hotels),
            "rooms": deepcopy(self.rooms),
            "reservations": deepcopy(self.reservations),
            "customers": deepcopy(self.customers),
            "current_user": self.current_user,
            "session": deepcopy(self.session),
            "next_reservation_id": self.next_reservation_id,
            "next_room_id": self.next_room_id,
            "next_customer_id": self.next_customer_id
        }
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse a date string into a datetime object.
        
        Args:
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            Optional[datetime]: Parsed datetime object or None if invalid.
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None
    
    def _dates_overlap(
        self,
        start1: str,
        end1: str,
        start2: str,
        end2: str
    ) -> bool:
        """
        Check if two date ranges overlap.
        
        Args:
            start1: Start date of first range (YYYY-MM-DD).
            end1: End date of first range (YYYY-MM-DD).
            start2: Start date of second range (YYYY-MM-DD).
            end2: End date of second range (YYYY-MM-DD).
            
        Returns:
            bool: True if the ranges overlap, False otherwise.
        """
        d_start1 = self._parse_date(start1)
        d_end1 = self._parse_date(end1)
        d_start2 = self._parse_date(start2)
        d_end2 = self._parse_date(end2)
        
        if not all([d_start1, d_end1, d_start2, d_end2]):
            return False
        
        # Ranges overlap if one starts before the other ends
        return d_start1 < d_end2 and d_start2 < d_end1

    # ==================== QUERY OPERATIONS ====================
    
    def get_hotels_by_location(self, location: str) -> Dict[str, Any]:
        """
        Retrieve all hotels located in a specified city or region.
        
        Args:
            location: The city or region name to search for (e.g., "New York").
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - hotels: List of hotel records matching the location
                - count: Number of hotels found
                On error:
                - error: Description of what went wrong
        """
        if not location or not isinstance(location, str):
            return {"error": "Invalid location parameter. Must be a non-empty string."}
        
        location_lower = location.lower().strip()
        matching_hotels = [
            deepcopy(hotel) for hotel in self.hotels.values()
            if hotel.get("location", "").lower() == location_lower
        ]
        
        return {
            "success": True,
            "hotels": matching_hotels,
            "count": len(matching_hotels)
        }
    
    def get_rooms_by_hotel(self, hotel_id: str) -> Dict[str, Any]:
        """
        List all rooms associated with a given hotel.
        
        Args:
            hotel_id: The unique identifier of the hotel.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - hotel_id: The queried hotel ID
                - rooms: List of room records for the hotel
                - count: Number of rooms found
                On error:
                - error: Description of what went wrong
        """
        if not hotel_id or not isinstance(hotel_id, str):
            return {"error": "Invalid hotel_id parameter. Must be a non-empty string."}
        
        if hotel_id not in self.hotels:
            return {"error": f"Hotel with ID '{hotel_id}' not found."}
        
        hotel_rooms = [
            deepcopy(room) for room in self.rooms.values()
            if room.get("hotel_id") == hotel_id
        ]
        
        return {
            "success": True,
            "hotel_id": hotel_id,
            "rooms": hotel_rooms,
            "count": len(hotel_rooms)
        }
    
    def get_room_details(self, room_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a specific room by room_id.
        
        Args:
            room_id: The unique identifier of the room.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - room: Complete room record with all details
                On error:
                - error: Description of what went wrong
        """
        if not room_id or not isinstance(room_id, str):
            return {"error": "Invalid room_id parameter. Must be a non-empty string."}
        
        if room_id not in self.rooms:
            return {"error": f"Room with ID '{room_id}' not found."}
        
        return {
            "success": True,
            "room": deepcopy(self.rooms[room_id])
        }
    
    def get_reservations_by_room(self, room_id: str) -> Dict[str, Any]:
        """
        Retrieve all reservations (past and current) for a specific room.
        
        Args:
            room_id: The unique identifier of the room.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - room_id: The queried room ID
                - reservations: List of all reservations for this room
                - count: Number of reservations found
                On error:
                - error: Description of what went wrong
        """
        if not room_id or not isinstance(room_id, str):
            return {"error": "Invalid room_id parameter. Must be a non-empty string."}
        
        if room_id not in self.rooms:
            return {"error": f"Room with ID '{room_id}' not found."}
        
        room_reservations = [
            deepcopy(res) for res in self.reservations.values()
            if res.get("room_id") == room_id
        ]
        
        return {
            "success": True,
            "room_id": room_id,
            "reservations": room_reservations,
            "count": len(room_reservations)
        }
    
    def check_room_availability(
        self,
        room_id: str,
        check_in_date: str,
        check_out_date: str
    ) -> Dict[str, Any]:
        """
        Determine if a room is available for a given date range.
        
        Args:
            room_id: The unique identifier of the room.
            check_in_date: Desired check-in date (YYYY-MM-DD).
            check_out_date: Desired check-out date (YYYY-MM-DD).
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - room_id: The queried room ID
                - available: True if room is available for the entire period
                - check_in_date: The requested check-in date
                - check_out_date: The requested check-out date
                - conflicting_reservations: List of reservation IDs that conflict
                On error:
                - error: Description of what went wrong
        """
        if not room_id or not isinstance(room_id, str):
            return {"error": "Invalid room_id parameter. Must be a non-empty string."}
        
        if room_id not in self.rooms:
            return {"error": f"Room with ID '{room_id}' not found."}
        
        # Validate dates
        d_check_in = self._parse_date(check_in_date)
        d_check_out = self._parse_date(check_out_date)
        
        if not d_check_in:
            return {"error": f"Invalid check_in_date format: '{check_in_date}'. Use YYYY-MM-DD."}
        if not d_check_out:
            return {"error": f"Invalid check_out_date format: '{check_out_date}'. Use YYYY-MM-DD."}
        
        # Constraint: check-out must be after check-in
        if d_check_out <= d_check_in:
            return {"error": "Check-out date must be after check-in date."}
        
        # Find conflicting reservations
        conflicts = []
        for res in self.reservations.values():
            if res.get("room_id") != room_id:
                continue
            if res.get("status") == "cancelled":
                continue
            if self._dates_overlap(
                check_in_date, check_out_date,
                res.get("check_in_date", ""),
                res.get("check_out_date", "")
            ):
                conflicts.append(res.get("reservation_id"))
        
        return {
            "success": True,
            "room_id": room_id,
            "available": len(conflicts) == 0,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "conflicting_reservations": conflicts
        }
    
    def search_available_rooms(
        self,
        location: str,
        check_in_date: str,
        check_out_date: str,
        room_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find all rooms across hotels in a location available for the requested stay.
        
        Args:
            location: The city or region to search in.
            check_in_date: Desired check-in date (YYYY-MM-DD).
            check_out_date: Desired check-out date (YYYY-MM-DD).
            room_type: Optional filter for room type.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - location: The searched location
                - check_in_date: The requested check-in date
                - check_out_date: The requested check-out date
                - available_rooms: List of available room records with hotel info
                - count: Number of available rooms found
                On error:
                - error: Description of what went wrong
        """
        if not location or not isinstance(location, str):
            return {"error": "Invalid location parameter. Must be a non-empty string."}
        
        # Validate dates
        d_check_in = self._parse_date(check_in_date)
        d_check_out = self._parse_date(check_out_date)
        
        if not d_check_in:
            return {"error": f"Invalid check_in_date format: '{check_in_date}'. Use YYYY-MM-DD."}
        if not d_check_out:
            return {"error": f"Invalid check_out_date format: '{check_out_date}'. Use YYYY-MM-DD."}
        
        if d_check_out <= d_check_in:
            return {"error": "Check-out date must be after check-in date."}
        
        # Find hotels in location
        location_lower = location.lower().strip()
        hotels_in_location = {
            h_id for h_id, hotel in self.hotels.items()
            if hotel.get("location", "").lower() == location_lower
        }
        
        available_rooms = []
        for room_id, room in self.rooms.items():
            if room.get("hotel_id") not in hotels_in_location:
                continue
            
            # Filter by room type if specified
            if room_type and room.get("room_type") != room_type:
                continue
            
            # Check availability
            availability = self.check_room_availability(
                room_id, check_in_date, check_out_date
            )
            if availability.get("available", False):
                room_info = deepcopy(room)
                hotel = self.hotels.get(room.get("hotel_id"), {})
                room_info["hotel_name"] = hotel.get("name", "Unknown")
                room_info["hotel_star_rating"] = hotel.get("star_rating", 0)
                available_rooms.append(room_info)
        
        return {
            "success": True,
            "location": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "available_rooms": available_rooms,
            "count": len(available_rooms)
        }
    
    def get_reservation_by_id(self, reservation_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific reservation.
        
        Args:
            reservation_id: The unique identifier of the reservation.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - reservation: Complete reservation record
                On error:
                - error: Description of what went wrong
        """
        if not reservation_id or not isinstance(reservation_id, str):
            return {"error": "Invalid reservation_id parameter. Must be a non-empty string."}
        
        if reservation_id not in self.reservations:
            return {"error": f"Reservation with ID '{reservation_id}' not found."}
        
        return {
            "success": True,
            "reservation": deepcopy(self.reservations[reservation_id])
        }
    
    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer profile and contact information by customer_id.
        
        Args:
            customer_id: The unique identifier of the customer.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - customer: Complete customer record
                On error:
                - error: Description of what went wrong
        """
        if not customer_id or not isinstance(customer_id, str):
            return {"error": "Invalid customer_id parameter. Must be a non-empty string."}
        
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found."}
        
        return {
            "success": True,
            "customer": deepcopy(self.customers[customer_id])
        }
    
    def get_customer_booking_history(self, customer_id: str) -> Dict[str, Any]:
        """
        List all reservation_ids associated with a customer's booking history.
        
        Args:
            customer_id: The unique identifier of the customer.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - customer_id: The queried customer ID
                - booking_history: List of reservation IDs
                - count: Number of bookings in history
                On error:
                - error: Description of what went wrong
        """
        if not customer_id or not isinstance(customer_id, str):
            return {"error": "Invalid customer_id parameter. Must be a non-empty string."}
        
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found."}
        
        history = self.customers[customer_id].get("booking_history", [])
        
        return {
            "success": True,
            "customer_id": customer_id,
            "booking_history": deepcopy(history),
            "count": len(history)
        }
    
    def get_overlapping_reservations(
        self,
        room_id: str,
        check_in_date: str,
        check_out_date: str
    ) -> Dict[str, Any]:
        """
        Identify any reservations that overlap with a given date range for a room.
        
        Args:
            room_id: The unique identifier of the room.
            check_in_date: Start date of the range to check (YYYY-MM-DD).
            check_out_date: End date of the range to check (YYYY-MM-DD).
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - room_id: The queried room ID
                - overlapping_reservations: List of reservation records that overlap
                - count: Number of overlapping reservations
                On error:
                - error: Description of what went wrong
        """
        if not room_id or not isinstance(room_id, str):
            return {"error": "Invalid room_id parameter. Must be a non-empty string."}
        
        if room_id not in self.rooms:
            return {"error": f"Room with ID '{room_id}' not found."}
        
        d_check_in = self._parse_date(check_in_date)
        d_check_out = self._parse_date(check_out_date)
        
        if not d_check_in:
            return {"error": f"Invalid check_in_date format: '{check_in_date}'. Use YYYY-MM-DD."}
        if not d_check_out:
            return {"error": f"Invalid check_out_date format: '{check_out_date}'. Use YYYY-MM-DD."}
        
        if d_check_out <= d_check_in:
            return {"error": "Check-out date must be after check-in date."}
        
        overlapping = []
        for res in self.reservations.values():
            if res.get("room_id") != room_id:
                continue
            if res.get("status") == "cancelled":
                continue
            if self._dates_overlap(
                check_in_date, check_out_date,
                res.get("check_in_date", ""),
                res.get("check_out_date", "")
            ):
                overlapping.append(deepcopy(res))
        
        return {
            "success": True,
            "room_id": room_id,
            "overlapping_reservations": overlapping,
            "count": len(overlapping)
        }

    # ==================== STATE CHANGE OPERATIONS ====================
    
    def create_reservation(
        self,
        room_id: str,
        customer_id: str,
        check_in_date: str,
        check_out_date: str
    ) -> Dict[str, Any]:
        """
        Book a room by creating a new reservation.
        
        Validates date order and ensures no overlap with existing bookings
        before creating the reservation.
        
        Args:
            room_id: The unique identifier of the room to book.
            customer_id: The unique identifier of the customer making the booking.
            check_in_date: Desired check-in date (YYYY-MM-DD).
            check_out_date: Desired check-out date (YYYY-MM-DD).
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if reservation was created
                - reservation_id: The ID of the newly created reservation
                - reservation: Complete reservation record
                On error:
                - error: Description of what went wrong
        """
        # Validate parameters
        if not room_id or not isinstance(room_id, str):
            return {"error": "Invalid room_id parameter. Must be a non-empty string."}
        if not customer_id or not isinstance(customer_id, str):
            return {"error": "Invalid customer_id parameter. Must be a non-empty string."}
        
        if room_id not in self.rooms:
            return {"error": f"Room with ID '{room_id}' not found."}
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found."}
        
        # Validate dates
        d_check_in = self._parse_date(check_in_date)
        d_check_out = self._parse_date(check_out_date)
        
        if not d_check_in:
            return {"error": f"Invalid check_in_date format: '{check_in_date}'. Use YYYY-MM-DD."}
        if not d_check_out:
            return {"error": f"Invalid check_out_date format: '{check_out_date}'. Use YYYY-MM-DD."}
        
        # Constraint: check-out must be after check-in
        if d_check_out <= d_check_in:
            return {"error": "Check-out date must be after check-in date."}
        
        # Constraint: no double booking
        availability = self.check_room_availability(room_id, check_in_date, check_out_date)
        if not availability.get("available", False):
            conflicts = availability.get("conflicting_reservations", [])
            return {
                "error": f"Room is not available for the requested dates. "
                         f"Conflicting reservations: {conflicts}"
            }
        
        # Create the reservation
        reservation_id = f"res_{self.next_reservation_id:03d}"
        self.next_reservation_id += 1
        
        reservation = {
            "reservation_id": reservation_id,
            "room_id": room_id,
            "customer_id": customer_id,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "status": "confirmed",
            "created_at": self._timestamp()
        }
        
        self.reservations[reservation_id] = reservation
        
        # Update customer booking history
        if "booking_history" not in self.customers[customer_id]:
            self.customers[customer_id]["booking_history"] = []
        self.customers[customer_id]["booking_history"].append(reservation_id)
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "reservation": deepcopy(reservation)
        }
    
    def cancel_reservation(self, reservation_id: str) -> Dict[str, Any]:
        """
        Cancel an existing reservation.
        
        Args:
            reservation_id: The ID of the reservation to cancel
            
        Returns:
            Dict[str, Any]: A dictionary containing cancellation status
                - success: True if cancelled
                - message: Success message
                On error:
                - error: Description of what went wrong
        """
        if not reservation_id or not isinstance(reservation_id, str):
            return {"error": "Invalid reservation_id parameter."}
            
        if reservation_id not in self.reservations:
            return {"error": "Reservation not found"}
        
        reservation = self.reservations[reservation_id]
        
        if reservation.get("status") == "cancelled":
            return {"error": "Reservation is already cancelled"}
        
        if reservation.get("status") == "checked_out":
            return {"error": "Cannot cancel a completed reservation"}
        
        reservation["status"] = "cancelled"
        reservation["cancelled_at"] = self._timestamp()
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "message": "Reservation cancelled successfully"
        }
    
    def check_in(self, reservation_id: str) -> Dict[str, Any]:
        """
        Check in a guest for their reservation.
        
        Args:
            reservation_id: The ID of the reservation
            
        Returns:
            Dict[str, Any]: A dictionary containing check-in status
                - success: True if checked in
                - message: Success message
                On error:
                - error: Description of what went wrong
        """
        if not reservation_id or not isinstance(reservation_id, str):
            return {"error": "Invalid reservation_id parameter."}
            
        if reservation_id not in self.reservations:
            return {"error": "Reservation not found"}
        
        reservation = self.reservations[reservation_id]
        
        if reservation.get("status") != "confirmed":
            return {"error": f"Cannot check in - reservation status is {reservation.get('status')}"}
        
        reservation["status"] = "checked_in"
        reservation["checked_in_at"] = self._timestamp()
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "room_id": reservation.get("room_id"),
            "message": "Check-in successful"
        }
    
    def check_out(self, reservation_id: str) -> Dict[str, Any]:
        """
        Check out a guest from their reservation.
        
        Args:
            reservation_id: The ID of the reservation
            
        Returns:
            Dict[str, Any]: A dictionary containing check-out status and billing info
                - success: True if checked out
                - nights: Number of nights stayed
                - total_amount: Total billing amount
                - message: Success message
                On error:
                - error: Description of what went wrong
        """
        if not reservation_id or not isinstance(reservation_id, str):
            return {"error": "Invalid reservation_id parameter."}
            
        if reservation_id not in self.reservations:
            return {"error": "Reservation not found"}
        
        reservation = self.reservations[reservation_id]
        
        if reservation.get("status") != "checked_in":
            return {"error": f"Cannot check out - reservation status is {reservation.get('status')}"}
        
        room_id = reservation.get("room_id")
        if room_id not in self.rooms:
            return {"error": "Room not found for this reservation."}
            
        room = self.rooms[room_id]
        
        d_check_in = self._parse_date(reservation.get("check_in_date", ""))
        d_check_out = self._parse_date(reservation.get("check_out_date", ""))
        
        if not d_check_in or not d_check_out:
            return {"error": "Invalid dates in reservation record."}
            
        nights = (d_check_out - d_check_in).days
        if nights < 1:
            nights = 1
            
        total_amount = nights * room.get("price_per_night", 0.0)
        
        reservation["status"] = "checked_out"
        reservation["checked_out_at"] = self._timestamp()
        reservation["total_amount"] = total_amount
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "nights": nights,
            "total_amount": total_amount,
            "message": "Check-out successful"
        }
    
    def get_available_rooms(self, check_in_date: str, check_out_date: str, 
                           room_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all available rooms globally for the specified date range.
        
        Args:
            check_in_date: Start date (YYYY-MM-DD)
            check_out_date: End date (YYYY-MM-DD)
            room_type: Optional filter by room type
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - available_rooms: List of available rooms
                - count: Number of available rooms found
                On error:
                - error: Description of what went wrong
        """
        d_check_in = self._parse_date(check_in_date)
        d_check_out = self._parse_date(check_out_date)
        
        if not d_check_in:
            return {"error": f"Invalid check_in_date format: '{check_in_date}'. Use YYYY-MM-DD."}
        if not d_check_out:
            return {"error": f"Invalid check_out_date format: '{check_out_date}'. Use YYYY-MM-DD."}
        if d_check_out <= d_check_in:
            return {"error": "Check-out date must be after check-in date."}

        available = []
        
        for room_id, room in self.rooms.items():
            if room_type and room.get("room_type") != room_type:
                continue
            
            is_available = True
            for res in self.reservations.values():
                if res.get("room_id") != room_id:
                    continue
                if res.get("status") in ["cancelled", "checked_out"]:
                    continue
                
                # Check for date overlap
                res_start = res.get("check_in_date", "")
                res_end = res.get("check_out_date", "")
                
                if self._dates_overlap(check_in_date, check_out_date, res_start, res_end):
                    is_available = False
                    break
            
            if is_available:
                available.append(deepcopy(room))
        
        return {
            "success": True,
            "available_rooms": available,
            "count": len(available)
        }
    
    def get_customer_reservations(self, customer_id: str) -> Dict[str, Any]:
        """
        Get all reservation details for a specific customer.
        
        Args:
            customer_id: The customer's ID
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if operation completed
                - reservations: List of reservation records
                - count: Number of reservations found
                On error:
                - error: Description of what went wrong
        """
        if not customer_id or not isinstance(customer_id, str):
            return {"error": "Invalid customer_id parameter."}
            
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found."}
        
        customer_reservations = []
        for res_id, res in self.reservations.items():
            if res.get("customer_id") == customer_id:
                customer_reservations.append(deepcopy(res))
        
        return {
            "success": True,
            "reservations": customer_reservations,
            "count": len(customer_reservations)
        }
    
    def update_room_price(self, room_id: str, new_price: float) -> Dict[str, Any]:
        """
        Update the price per night for a room.
        
        Args:
            room_id: The room's ID
            new_price: New price per night
            
        Returns:
            Dict[str, Any]: A dictionary containing update status
                - success: True if updated
                - old_price: Previous price
                - new_price: Updated price
                On error:
                - error: Description of what went wrong
        """
        if not room_id or not isinstance(room_id, str):
            return {"error": "Invalid room_id parameter."}
            
        if room_id not in self.rooms:
            return {"error": "Room not found"}
        
        if not isinstance(new_price, (int, float)) or new_price <= 0:
            return {"error": "Price must be positive"}
        
        old_price = self.rooms[room_id].get("price_per_night", 0.0)
        self.rooms[room_id]["price_per_night"] = float(new_price)
        
        return {
            "success": True,
            "room_id": room_id,
            "old_price": old_price,
            "new_price": float(new_price)
        }


__TEST_CASES__ = [
    {
        "name": "test_create_reservation_success",
        "setup": lambda: (lambda env=HotelBookingSystem(): (env._load_scenario({}), env)[1])(),
        "action": lambda env: env.create_reservation("room_005", "cust_001", "2025-03-01", "2025-03-05"),
        "validate": lambda result: result.get("success") is True and "reservation_id" in result
    },
    {
        "name": "test_create_reservation_conflict_error",
        "setup": lambda: (lambda env=HotelBookingSystem(): (env._load_scenario({}), env)[1])(),
        "action": lambda env: env.create_reservation("room_001", "cust_002", "2025-02-03", "2025-02-08"),
        "validate": lambda result: "error" in result and "Room is not available" in result["error"]
    },
    {
        "name": "test_check_in_and_check_out",
        "setup": lambda: (lambda env=HotelBookingSystem(): (env._load_scenario({}), env)[1])(),
        "action": lambda env: (
            env.check_in("res_001"),
            env.check_out("res_001")
        )[1],
        "validate": lambda result: result.get("success") is True and result.get("nights") == 4
    },
    {
        "name": "test_get_available_rooms_type_filter",
        "setup": lambda: (lambda env=HotelBookingSystem(): (env._load_scenario({}), env)[1])(),
        "action": lambda env: env.get_available_rooms("2025-03-01", "2025-03-10", "suite"),
        "validate": lambda result: result.get("success") is True and len(result.get("available_rooms", [])) > 0 and all(r["room_type"] == "suite" for r in result["available_rooms"])
    },
    {
        "name": "test_update_room_price_invalid",
        "setup": lambda: (lambda env=HotelBookingSystem(): (env._load_scenario({}), env)[1])(),
        "action": lambda env: env.update_room_price("room_001", -50.0),
        "validate": lambda result: "error" in result and "positive" in result["error"]
    }
]