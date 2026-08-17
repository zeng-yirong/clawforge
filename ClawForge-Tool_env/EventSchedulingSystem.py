"""
Event Scheduling System Environment API

An event scheduling system for managing the planning and coordination of events,
including creation, retrieval, conflict detection, and updates.
"""

import re
from copy import deepcopy
from typing import Dict, List, Optional, Any

DEFAULT_STATE: Dict[str, Any] = {
    "events": {
        "evt_001": {
            "event_id": "evt_001",
            "title": "Annual Tech Conference",
            "description": "A conference for technology enthusiasts",
            "date": "2024-03-15",
            "time_slot": "morning",
            "location": "loc_001",
            "status": "confirmed",
            "event_type": "conference",
            "participants": ["user1", "user2"]
        },
        "evt_002": {
            "event_id": "evt_002",
            "title": "Team Building Workshop",
            "description": "Interactive workshop for team collaboration",
            "date": "2024-03-15",
            "time_slot": "afternoon",
            "location": "loc_002",
            "status": "confirmed",
            "event_type": "workshop",
            "participants": ["user1", "user3"]
        },
        "evt_003": {
            "event_id": "evt_003",
            "title": "Product Launch Webinar",
            "description": "Online webinar for new product introduction",
            "date": "2024-03-16",
            "time_slot": "morning",
            "location": "loc_003",
            "status": "pending",
            "event_type": "webinar",
            "participants": ["user2"]
        },
        "evt_004": {
            "event_id": "evt_004",
            "title": "Community Meetup",
            "description": "Monthly community gathering",
            "date": "2024-03-20",
            "time_slot": "evening",
            "location": "loc_001",
            "status": "pending",
            "event_type": "meetup",
            "participants": []
        }
    },
    "locations": {
        "loc_001": {
            "location_id": "loc_001",
            "name": "Main Conference Hall",
            "address": "123 Business Park, Building A",
            "capacity": 500,
            "location_type": "physical",
            "booking_status": "available",
            "amenities": ["projector", "microphone", "whiteboard"]
        },
        "loc_002": {
            "location_id": "loc_002",
            "name": "Training Room B",
            "address": "123 Business Park, Building B",
            "capacity": 50,
            "location_type": "physical",
            "booking_status": "available",
            "amenities": ["projector", "whiteboard"]
        },
        "loc_003": {
            "location_id": "loc_003",
            "name": "Zoom Meeting Room",
            "address": "https://zoom.us/j/123456789",
            "capacity": 100,
            "location_type": "virtual",
            "booking_status": "available",
            "amenities": ["screen_sharing", "recording"]
        },
        "loc_004": {
            "location_id": "loc_004",
            "name": "Outdoor Amphitheater",
            "address": "456 Park Avenue",
            "capacity": 1000,
            "location_type": "physical",
            "booking_status": "available",
            "amenities": ["stage", "sound_system"]
        }
    },
    "time_slots": {
        "morning": {
            "slot_id": "ts_001",
            "label": "morning",
            "start_time": "08:00",
            "end_time": "12:00",
            "available": True
        },
        "afternoon": {
            "slot_id": "ts_002",
            "label": "afternoon",
            "start_time": "13:00",
            "end_time": "17:00",
            "available": True
        },
        "evening": {
            "slot_id": "ts_003",
            "label": "evening",
            "start_time": "18:00",
            "end_time": "22:00",
            "available": True
        }
    },
    "event_series": {
        "series_001": {
            "series_id": "series_001",
            "title": "Tech Talk Series",
            "event_type": "talk",
            "member_events": ["evt_001"],
            "organizer": "Tech Community Group"
        },
        "series_002": {
            "series_id": "series_002",
            "title": "Monthly Workshops",
            "event_type": "workshop",
            "member_events": ["evt_002"],
            "organizer": "HR Department"
        },
        "series_003": {
            "series_id": "series_003",
            "title": "Product Launch Events",
            "event_type": "webinar",
            "member_events": ["evt_003"],
            "organizer": "Marketing Team"
        }
    },
    "location_bookings": {
        "loc_001": {
            "2024-03-15": ["morning"],
            "2024-03-20": ["evening"]
        },
        "loc_002": {
            "2024-03-15": ["afternoon"]
        },
        "loc_003": {
            "2024-03-16": ["morning"]
        }
    },
    "next_event_id": 5,
    "next_series_id": 4,
    "next_location_id": 5,
    "current_user": "admin",
    "system_timestamp": "2024-03-01T10:00:00"
}


class EventSchedulingSystem:
    """
    Event Scheduling System Environment API.
    
    Manages the planning and coordination of events over time, maintaining
    structured records of event details and supporting operations like
    creation, retrieval, conflict detection, and updates.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Event Scheduling System.
        
        Declares all state attributes with type hints and sets up the API description.
        """
        self.events: Dict[str, Dict[str, Any]] = {}
        self.locations: Dict[str, Dict[str, Any]] = {}
        self.time_slots: Dict[str, Dict[str, Any]] = {}
        self.event_series: Dict[str, Dict[str, Any]] = {}
        self.location_bookings: Dict[str, Dict[str, List[str]]] = {}
        self.next_event_id: int = 1
        self.next_series_id: int = 1
        self.next_location_id: int = 1
        self.current_user: str = ""
        self.system_timestamp: str = ""
        
        self._api_description = "Event scheduling system for managing events, locations, and time coordination."
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data.
            long_context: Flag for long context scenarios (unused but required for interface).
        
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
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp string.
        
        Returns:
            ISO formatted timestamp string.
        """
        return self.system_timestamp if self.system_timestamp else "2024-03-01T10:00:00"

    def _validate_date_format(self, date: str) -> bool:
        """
        Validate date is in YYYY-MM-DD format.
        
        Args:
            date: The date string to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date))
        
    def _validate_time_format(self, time: str) -> bool:
        """
        Validate time is in HH:MM format.
        
        Args:
            time: The time string to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        return bool(re.match(r"^\d{2}:\d{2}$", time))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Return the current environment state.
        
        Returns:
            A dictionary containing all internal state variables.
        """
        return {
            "events": deepcopy(self.events),
            "locations": deepcopy(self.locations),
            "time_slots": deepcopy(self.time_slots),
            "event_series": deepcopy(self.event_series),
            "location_bookings": deepcopy(self.location_bookings),
            "next_event_id": self.next_event_id,
            "next_series_id": self.next_series_id,
            "next_location_id": self.next_location_id,
            "current_user": self.current_user,
            "system_timestamp": self.system_timestamp
        }
    
    # ==================== Query Operations ====================
    
    def get_time_slot_by_label(self, label: str) -> Dict[str, Any]:
        """
        Retrieve the start and end time of a time slot by its label.
        
        Args:
            label: The time slot label (e.g., "morning", "afternoon", "evening").
        
        Returns:
            Dictionary containing time slot details or error message.
        """
        if not label:
            return {"error": "Time slot label is required"}
        
        if label not in self.time_slots:
            return {"error": f"Time slot '{label}' not found"}
        
        slot = self.time_slots[label]
        return {
            "slot_id": slot["slot_id"],
            "label": slot["label"],
            "start_time": slot["start_time"],
            "end_time": slot["end_time"],
            "available": slot["available"]
        }
    
    def list_available_locations(self, date: str, time_slot: str) -> Dict[str, Any]:
        """
        Get all locations that are not fully booked on a given date and time slot.
        
        Args:
            date: The date to check availability (YYYY-MM-DD format).
            time_slot: The time slot label to check.
        
        Returns:
            Dictionary containing list of available locations or error message.
        """
        if not date:
            return {"error": "Date is required"}
        if not self._validate_date_format(date):
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        if not time_slot:
            return {"error": "Time slot is required"}
        if time_slot not in self.time_slots:
            return {"error": f"Invalid time slot '{time_slot}'"}
        
        available_locations = []
        
        for loc_id, location in self.locations.items():
            is_booked = False
            
            if location["location_type"] == "physical":
                if loc_id in self.location_bookings:
                    if date in self.location_bookings[loc_id]:
                        if time_slot in self.location_bookings[loc_id][date]:
                            is_booked = True
            
            if not is_booked:
                available_locations.append(deepcopy(location))
        
        return {
            "date": date,
            "time_slot": time_slot,
            "available_locations": available_locations,
            "count": len(available_locations)
        }
    
    def check_location_availability(
        self, 
        location_id: str, 
        date: str, 
        time_slot: str
    ) -> Dict[str, Any]:
        """
        Determine if a specific location is available for an event at a given date and time slot.
        
        Args:
            location_id: The ID of the location to check.
            date: The date to check (YYYY-MM-DD format).
            time_slot: The time slot label to check.
        
        Returns:
            Dictionary containing availability status or error message.
        """
        if not location_id:
            return {"error": "Location ID is required"}
        if not date:
            return {"error": "Date is required"}
        if not time_slot:
            return {"error": "Time slot is required"}
            
        if not self._validate_date_format(date):
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        if location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        if time_slot not in self.time_slots:
            return {"error": f"Invalid time slot '{time_slot}'"}
        
        location = self.locations[location_id]
        is_available = True
        reason = "Location is available"
        
        if location["location_type"] == "physical":
            if location_id in self.location_bookings:
                if date in self.location_bookings[location_id]:
                    if time_slot in self.location_bookings[location_id][date]:
                        is_available = False
                        reason = "Location is already booked for this time slot"
        
        return {
            "success": True,
            "location_id": location_id,
            "location_name": location["name"],
            "date": date,
            "time_slot": time_slot,
            "is_available": is_available,
            "available": is_available,
            "reason": reason
        }
    
    def find_conflicting_events(
        self, 
        date: str, 
        time_slot: str, 
        location_id: str,
        exclude_event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Identify any existing events that overlap in time and location with a proposed event.
        
        Args:
            date: The date to check for conflicts.
            time_slot: The time slot to check.
            location_id: The location to check.
            exclude_event_id: Optional event ID to exclude from conflict check.
        
        Returns:
            Dictionary containing list of conflicting events or error message.
        """
        if not date:
            return {"error": "Date is required"}
        if not time_slot:
            return {"error": "Time slot is required"}
        if not location_id:
            return {"error": "Location ID is required"}
        
        if location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        if time_slot not in self.time_slots:
            return {"error": f"Invalid time slot '{time_slot}'"}
        
        location = self.locations[location_id]
        conflicts = []
        
        if location["location_type"] == "physical":
            for event_id, event in self.events.items():
                if exclude_event_id and event_id == exclude_event_id:
                    continue
                if event["status"] == "canceled":
                    continue
                if (event["date"] == date and 
                    event["time_slot"] == time_slot and 
                    event["location"] == location_id):
                    conflicts.append(deepcopy(event))
        
        return {
            "date": date,
            "time_slot": time_slot,
            "location_id": location_id,
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "conflict_count": len(conflicts)
        }
    
    def get_event_by_id(self, event_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific event using its event_id.
        
        Args:
            event_id: The unique identifier of the event.
        
        Returns:
            Dictionary containing event details or error message.
        """
        if not event_id:
            return {"error": "Event ID is required"}
        
        if event_id not in self.events:
            return {"error": f"Event '{event_id}' not found"}
        
        event = deepcopy(self.events[event_id])
        
        if event["location"] in self.locations:
            event["location_details"] = deepcopy(self.locations[event["location"]])
        
        if event["time_slot"] in self.time_slots:
            event["time_slot_details"] = deepcopy(self.time_slots[event["time_slot"]])
        
        return event

    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific event using its event_id.
        Alias for get_event_by_id.
        
        Args:
            event_id: The unique identifier of the event.
        
        Returns:
            Dictionary containing event details or error message.
        """
        return self.get_event_by_id(event_id)
    
    def list_events_by_date(self, date: str) -> Dict[str, Any]:
        """
        Retrieve all events scheduled on a specific date.
        
        Args:
            date: The date to filter events (YYYY-MM-DD format).
        
        Returns:
            Dictionary containing list of events on the specified date.
        """
        if not date:
            return {"error": "Date is required"}
            
        if not self._validate_date_format(date):
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        events_on_date = []
        for event in self.events.values():
            if event["date"] == date and event["status"] != "canceled":
                events_on_date.append(deepcopy(event))
        
        return {
            "date": date,
            "events": events_on_date,
            "count": len(events_on_date)
        }
    
    def list_events_by_location(self, location_id: str) -> Dict[str, Any]:
        """
        Get all events scheduled at a particular location.
        
        Args:
            location_id: The ID of the location to filter by.
        
        Returns:
            Dictionary containing list of events at the specified location.
        """
        if not location_id:
            return {"error": "Location ID is required"}
        
        if location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        
        events_at_location = []
        for event in self.events.values():
            if event["location"] == location_id and event["status"] != "canceled":
                events_at_location.append(deepcopy(event))
        
        return {
            "location_id": location_id,
            "location_name": self.locations[location_id]["name"],
            "events": events_at_location,
            "count": len(events_at_location)
        }
    
    def get_location_by_id(self, location_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a location.
        
        Args:
            location_id: The unique identifier of the location.
        
        Returns:
            Dictionary containing location details or error message.
        """
        if not location_id:
            return {"error": "Location ID is required"}
        
        if location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        
        return deepcopy(self.locations[location_id])
    
    def get_event_series_by_id(self, series_id: str) -> Dict[str, Any]:
        """
        Retrieve information about an event series, including its member events.
        
        Args:
            series_id: The unique identifier of the event series.
        
        Returns:
            Dictionary containing series details and member events or error message.
        """
        if not series_id:
            return {"error": "Series ID is required"}
        
        if series_id not in self.event_series:
            return {"error": f"Event series '{series_id}' not found"}
        
        series = deepcopy(self.event_series[series_id])
        
        member_event_details = []
        for event_id in series.get("member_events", []):
            if event_id in self.events:
                member_event_details.append(deepcopy(self.events[event_id]))
        
        series["member_event_details"] = member_event_details
        return series
    
    def validate_event_prerequisites(self, event_id: str) -> Dict[str, Any]:
        """
        Check whether an event has all required fields to be confirmed.
        
        Args:
            event_id: The unique identifier of the event to validate.
        
        Returns:
            Dictionary containing validation results.
        """
        if not event_id:
            return {"error": "Event ID is required"}
        
        if event_id not in self.events:
            return {"error": f"Event '{event_id}' not found"}
        
        event = self.events[event_id]
        missing_fields = []
        
        if not event.get("date"):
            missing_fields.append("date")
        if not event.get("time_slot"):
            missing_fields.append("time_slot")
        if not event.get("location"):
            missing_fields.append("location")
        
        is_valid = len(missing_fields) == 0
        
        conflicts_result = None
        if is_valid:
            conflicts_result = self.find_conflicting_events(
                event["date"], 
                event["time_slot"], 
                event["location"],
                exclude_event_id=event_id
            )
            if conflicts_result.get("has_conflicts"):
                is_valid = False
        
        return {
            "event_id": event_id,
            "is_valid": is_valid,
            "missing_fields": missing_fields,
            "has_conflicts": conflicts_result.get("has_conflicts", False) if conflicts_result else False,
            "can_be_confirmed": is_valid
        }
    
    def get_events_by_participant(self, participant_id: str) -> Dict[str, Any]:
        """
        Get all events where the specified participant is involved.
        
        Args:
            participant_id: The ID of the participant to filter by.
        
        Returns:
            Dictionary containing list of events for the participant.
        """
        if not participant_id:
            return {"error": "Participant ID is required"}
        
        events = []
        for event_id, event in self.events.items():
            if participant_id in event.get("participants", []) and event["status"] != "canceled":
                events.append(deepcopy(event))
        
        return {
            "participant_id": participant_id,
            "events": events,
            "count": len(events)
        }
    
    def get_location_schedule(self, location_id: str, date: str) -> Dict[str, Any]:
        """
        Get the schedule for a specific location on a given date.
        
        Args:
            location_id: The ID of the location.
            date: The date to get the schedule for (YYYY-MM-DD format).
        
        Returns:
            Dictionary containing the location's schedule for the specified date.
        """
        if not location_id:
            return {"error": "Location ID is required"}
        if not date:
            return {"error": "Date is required"}
            
        if not self._validate_date_format(date):
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        if location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        
        location = self.locations[location_id]
        booked_slots = self.location_bookings.get(location_id, {}).get(date, [])
        
        scheduled_events = []
        for event_id, event in self.events.items():
            if (event.get("location") == location_id and 
                event["date"] == date and 
                event["status"] != "canceled"):
                scheduled_events.append({
                    "event_id": event_id,
                    "title": event["title"],
                    "time_slot": event["time_slot"],
                    "status": event["status"]
                })
        
        return {
            "location_id": location_id,
            "location_name": location["name"],
            "date": date,
            "booked_slots": booked_slots,
            "scheduled_events": scheduled_events,
            "total_events": len(scheduled_events)
        }
    
    # ==================== State Change Operations ====================
    
    def create_location(
        self,
        name: str,
        location_type: str,
        capacity: int,
        address: Optional[str] = None,
        amenities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new location in the system.
        
        Args:
            name: The name of the location.
            location_type: The type of location ("physical" or "virtual").
            capacity: The maximum capacity of the location.
            address: Optional address or URL for the location.
            amenities: Optional list of amenities available at the location.
        
        Returns:
            Dictionary containing the created location or error message.
        """
        if not name:
            return {"error": "Location name is required"}
        if not location_type:
            return {"error": "Location type is required"}
        if location_type not in ["physical", "virtual"]:
            return {"error": "Location type must be 'physical' or 'virtual'"}
        if capacity is None or capacity <= 0:
            return {"error": "Capacity must be a positive integer"}
        
        location_id = f"loc_{self.next_location_id:03d}"
        self.next_location_id += 1
        
        new_location = {
            "location_id": location_id,
            "name": name,
            "address": address or "",
            "capacity": capacity,
            "location_type": location_type,
            "booking_status": "available",
            "amenities": amenities or [],
            "created_at": self._timestamp()
        }
        
        self.locations[location_id] = new_location
        
        return {
            "success": True,
            "message": "Location created successfully",
            "location_id": location_id,
            "name": name,
            "location_type": location_type,
            "capacity": capacity,
            "location": deepcopy(new_location)
        }
    
    def create_event(
        self,
        title: str,
        date: str,
        time_slot: str,
        location_id: Optional[str] = None,
        description: Optional[str] = None,
        event_type: Optional[str] = None,
        participants: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a new event to the system.
        
        Args:
            title: The title of the event.
            date: The date of the event (YYYY-MM-DD format).
            time_slot: The time slot label (morning, afternoon, evening).
            location_id: Optional location ID where the event will be held.
            description: Optional description of the event.
            event_type: Optional type/category of the event.
            participants: Optional list of participant IDs.
        
        Returns:
            Dictionary containing the created event or error message.
        """
        if not title:
            return {"error": "Event title is required"}
        if not date:
            return {"error": "Event date is required"}
        if not self._validate_date_format(date):
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        if not time_slot:
            return {"error": "Time slot is required"}
        
        if time_slot not in self.time_slots:
            return {"error": f"Invalid time slot '{time_slot}'"}
        
        if location_id and location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        
        if location_id:
            loc_data = self.locations[location_id]
            if loc_data["location_type"] == "physical":
                conflicts = self.find_conflicting_events(date, time_slot, location_id)
                if conflicts.get("has_conflicts"):
                    return {
                        "error": f"Location '{loc_data['name']}' is already booked for {date} {time_slot}"
                    }
        
        event_id = f"evt_{self.next_event_id:03d}"
        self.next_event_id += 1
        
        new_event = {
            "event_id": event_id,
            "title": title,
            "description": description or "",
            "date": date,
            "time_slot": time_slot,
            "location": location_id or "",
            "status": "pending",
            "event_type": event_type or "general",
            "participants": participants or [],
            "created_at": self._timestamp()
        }
        
        self.events[event_id] = new_event
        
        if location_id:
            loc_data = self.locations[location_id]
            if loc_data["location_type"] == "physical":
                self._add_location_booking(location_id, date, time_slot)
        
        return {
            "success": True,
            "message": "Event created successfully",
            "event_id": event_id,
            "title": title,
            "date": date,
            "time_slot": time_slot,
            "status": "pending",
            "event": deepcopy(new_event)
        }

    def update_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        date: Optional[str] = None,
        time_slot: Optional[str] = None,
        location_id: Optional[str] = None,
        event_type: Optional[str] = None,
        participants: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing event.
        
        Args:
            event_id: The ID of the event to update.
            title: Optional new title.
            description: Optional new description.
            date: Optional new date (YYYY-MM-DD format).
            time_slot: Optional new time slot label.
            location_id: Optional new location ID.
            event_type: Optional new event type.
            participants: Optional new list of participant IDs.
        
        Returns:
            Dictionary containing the updated event or error message.
        """
        if not event_id:
            return {"error": "Event ID is required"}
        if event_id not in self.events:
            return {"error": f"Event '{event_id}' not found"}
            
        event = self.events[event_id]
        
        old_date = event["date"]
        old_time_slot = event["time_slot"]
        old_location = event.get("location")
        
        new_date = date if date is not None else old_date
        new_time_slot = time_slot if time_slot is not None else old_time_slot
        new_location = location_id if location_id is not None else old_location
        
        if date is not None and not self._validate_date_format(date):
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
            
        if time_slot is not None and time_slot not in self.time_slots:
            return {"error": f"Invalid time slot '{time_slot}'"}
            
        if location_id is not None and location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
            
        # Check conflicts if any of date, time_slot, or location changes
        if (new_date != old_date or new_time_slot != old_time_slot or new_location != old_location):
            if new_location:
                loc_data = self.locations[new_location]
                if loc_data["location_type"] == "physical":
                    conflicts = self.find_conflicting_events(new_date, new_time_slot, new_location, exclude_event_id=event_id)
                    if conflicts.get("has_conflicts"):
                        return {"error": f"Location '{loc_data['name']}' is already booked for {new_date} {new_time_slot}"}
        
        # Update location bookings
        if (new_date != old_date or new_time_slot != old_time_slot or new_location != old_location):
            if old_location:
                self._remove_location_booking(old_location, old_date, old_time_slot)
            if new_location:
                loc_data = self.locations[new_location]
                if loc_data["location_type"] == "physical":
                    self._add_location_booking(new_location, new_date, new_time_slot)
                    
        if title is not None:
            if not title:
                return {"error": "Title cannot be empty"}
            event["title"] = title
        if description is not None:
            event["description"] = description
        if date is not None:
            event["date"] = date
        if time_slot is not None:
            event["time_slot"] = time_slot
        if location_id is not None:
            event["location"] = location_id
        if event_type is not None:
            event["event_type"] = event_type
        if participants is not None:
            event["participants"] = participants
            
        return {
            "success": True,
            "message": "Event updated successfully",
            "event": deepcopy(event)
        }
        
    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """
        Delete an event from the system and release its location booking.
        
        Args:
            event_id: The ID of the event to delete.
        
        Returns:
            Dictionary containing success message or error.
        """
        if not event_id:
            return {"error": "Event ID is required"}
        if event_id not in self.events:
            return {"error": f"Event '{event_id}' not found"}
            
        event = self.events[event_id]
        
        # Release location booking
        if event.get("location"):
            self._remove_location_booking(event["location"], event["date"], event["time_slot"])
            
        del self.events[event_id]
        
        # Remove from event_series if applicable
        for series in self.event_series.values():
            if event_id in series.get("member_events", []):
                series["member_events"].remove(event_id)
                
        return {
            "success": True,
            "message": "Event deleted successfully"
        }
    
    def _add_location_booking(self, location_id: str, date: str, time_slot: str) -> None:
        """
        Internal helper to add a location booking.
        
        Args:
            location_id: The location to book.
            date: The date of the booking.
            time_slot: The time slot to book.
        
        Returns:
            None
        """
        if location_id not in self.location_bookings:
            self.location_bookings[location_id] = {}
        if date not in self.location_bookings[location_id]:
            self.location_bookings[location_id][date] = []
        if time_slot not in self.location_bookings[location_id][date]:
            self.location_bookings[location_id][date].append(time_slot)
    
    def _remove_location_booking(self, location_id: str, date: str, time_slot: str) -> None:
        """
        Internal helper to remove a location booking.
        
        Args:
            location_id: The location to unbook.
            date: The date of the booking.
            time_slot: The time slot to remove.
        
        Returns:
            None
        """
        if location_id in self.location_bookings:
            if date in self.location_bookings[location_id]:
                if time_slot in self.location_bookings[location_id][date]:
                    self.location_bookings[location_id][date].remove(time_slot)
                if not self.location_bookings[location_id][date]:
                    del self.location_bookings[location_id][date]
            if not self.location_bookings[location_id]:
                del self.location_bookings[location_id]
    
    def confirm_event(self, event_id: str) -> Dict[str, Any]:
        """
        Update an event's status to confirmed if all prerequisites are met.
        
        Args:
            event_id: The unique identifier of the event to confirm.
        
        Returns:
            Dictionary containing confirmation result or error message.
        """
        if not event_id:
            return {"error": "Event ID is required"}
        
        if event_id not in self.events:
            return {"error": f"Event '{event_id}' not found"}
        
        event = self.events[event_id]
        
        if event["status"] == "confirmed":
            return {"error": "Event is already confirmed"}
        if event["status"] == "canceled":
            return {"error": "Cannot confirm a canceled event"}
        
        validation = self.validate_event_prerequisites(event_id)
        if not validation.get("can_be_confirmed"):
            if validation.get("missing_fields"):
                return {
                    "error": f"Cannot confirm event. Missing fields: {', '.join(validation['missing_fields'])}"
                }
            if validation.get("has_conflicts"):
                return {"error": "Cannot confirm event. There are scheduling conflicts"}
        
        self.events[event_id]["status"] = "confirmed"
        self.events[event_id]["confirmed_at"] = self._timestamp()
        
        return {
            "success": True,
            "message": "Event confirmed successfully",
            "event": deepcopy(self.events[event_id])
        }
    
    def cancel_event(self, event_id: str) -> Dict[str, Any]:
        """
        Change an event's status to canceled and release location booking.
        
        Args:
            event_id: The unique identifier of the event to cancel.
        
        Returns:
            Dictionary containing cancellation result or error message.
        """
        if not event_id:
            return {"error": "Event ID is required"}
        
        if event_id not in self.events:
            return {"error": f"Event '{event_id}' not found"}
        
        event = self.events[event_id]
        
        if event["status"] == "canceled":
            return {"error": "Event is already canceled"}
            
        # Release location booking if exists
        if event.get("location"):
            self._remove_location_booking(event["location"], event["date"], event["time_slot"])
        
        event["status"] = "canceled"
        
        return {
            "success": True,
            "message": "Event canceled successfully",
            "event": deepcopy(self.events[event_id])
        }
    
    def get_events_by_date(self, date: str) -> Dict[str, Any]:
        """
        Retrieve all events scheduled for a specific date.
        
        Args:
            date: The date to filter events (YYYY-MM-DD format).
        
        Returns:
            Dictionary containing list of events or error message.
        """
        if not date:
            return {"error": "Date is required"}
        
        if not self._validate_date_format(date):
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        matching_events = [
            deepcopy(event) for event in self.events.values()
            if event["date"] == date
        ]
        
        return {
            "success": True,
            "date": date,
            "count": len(matching_events),
            "events": matching_events
        }
    
    def get_events_by_status(self, status: str) -> Dict[str, Any]:
        """
        Retrieve all events with a specific status.
        
        Args:
            status: The status to filter by (draft, pending, confirmed, canceled).
        
        Returns:
            Dictionary containing list of events or error message.
        """
        if not status:
            return {"error": "Status is required"}
        
        valid_statuses = ["draft", "pending", "confirmed", "canceled"]
        if status not in valid_statuses:
            return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
        
        matching_events = [
            deepcopy(event) for event in self.events.values()
            if event["status"] == status
        ]
        
        return {
            "success": True,
            "status": status,
            "count": len(matching_events),
            "events": matching_events
        }
    
    def list_all_events(self) -> Dict[str, Any]:
        """
        Retrieve all events in the system.
        
        Returns:
            Dictionary containing list of all events.
        """
        all_events = [deepcopy(event) for event in self.events.values()]
        
        return {
            "success": True,
            "count": len(all_events),
            "events": all_events
        }


__TEST_CASES__ = [
    {
        "name": "create_event_success",
        "input": {
            "method": "create_event",
            "params": {
                "title": "Team Meeting",
                "date": "2024-06-15",
                "time_slot": "morning",
                "description": "Weekly team sync",
                "location_id": "loc_001",
                "participants": ["user1", "user2"]
            }
        },
        "expected_keys": ["success", "message", "event"],
        "expected_values": {"success": True}
    },
    {
        "name": "create_event_invalid_date",
        "input": {
            "method": "create_event",
            "params": {
                "title": "Test Event",
                "date": "06-15-2024",
                "time_slot": "morning"
            }
        },
        "expected_keys": ["error"],
        "expected_values": {"error": "Invalid date format. Use YYYY-MM-DD"}
    },
    {
        "name": "get_event_success",
        "input": {
            "method": "get_event",
            "params": {
                "event_id": "evt_001"
            }
        },
        "expected_keys": ["event_id", "title", "date", "time_slot"],
        "expected_values": {"event_id": "evt_001"}
    },
    {
        "name": "update_event_not_found",
        "input": {
            "method": "update_event",
            "params": {
                "event_id": "nonexistent_id",
                "title": "New Title"
            }
        },
        "expected_keys": ["error"],
        "expected_values": {"error": "Event 'nonexistent_id' not found"}
    },
    {
        "name": "delete_event_success",
        "input": {
            "method": "delete_event",
            "params": {
                "event_id": "evt_002"
            }
        },
        "expected_keys": ["success", "message"],
        "expected_values": {"success": True}
    }
]