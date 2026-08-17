"""
Fitness Class Scheduling System Environment API

A fitness class scheduling system that manages timetables, enrollments,
instructors, and locations for a fitness center.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

DEFAULT_STATE: Dict[str, Any] = {
    "class_types": {
        "CT001": {
            "class_id": "CT001",
            "name": "Yoga",
            "description": "A relaxing yoga session focusing on flexibility and mindfulness",
            "duration": 60,
            "category": "Mind & Body"
        },
        "CT002": {
            "class_id": "CT002",
            "name": "Spin",
            "description": "High-intensity indoor cycling workout",
            "duration": 45,
            "category": "Cardio"
        },
        "CT003": {
            "class_id": "CT003",
            "name": "HIIT",
            "description": "High-Intensity Interval Training for maximum calorie burn",
            "duration": 30,
            "category": "Cardio"
        },
        "CT004": {
            "class_id": "CT004",
            "name": "Pilates",
            "description": "Core strengthening and flexibility exercises",
            "duration": 50,
            "category": "Mind & Body"
        }
    },
    "scheduled_classes": {
        "SC001": {
            "scheduled_id": "SC001",
            "class_id": "CT001",
            "date": "2024-03-14",
            "start_time": "09:00",
            "end_time": "10:00",
            "instructor_id": "INS001",
            "location": "LOC001",
            "current_enrollment": 8,
            "max_capacity": 20
        },
        "SC002": {
            "scheduled_id": "SC002",
            "class_id": "CT002",
            "date": "2024-03-14",
            "start_time": "10:30",
            "end_time": "11:15",
            "instructor_id": "INS002",
            "location": "LOC002",
            "current_enrollment": 15,
            "max_capacity": 15
        },
        "SC003": {
            "scheduled_id": "SC003",
            "class_id": "CT003",
            "date": "2024-03-14",
            "start_time": "12:00",
            "end_time": "12:30",
            "instructor_id": "INS003",
            "location": "LOC003",
            "current_enrollment": 5,
            "max_capacity": 25
        },
        "SC004": {
            "scheduled_id": "SC004",
            "class_id": "CT001",
            "date": "2024-03-15",
            "start_time": "09:00",
            "end_time": "10:00",
            "instructor_id": "INS001",
            "location": "LOC001",
            "current_enrollment": 10,
            "max_capacity": 20
        }
    },
    "instructors": {
        "INS001": {
            "instructor_id": "INS001",
            "name": "Sarah Johnson",
            "specialty": "Yoga, Pilates",
            "contact_info": "sarah.johnson@fitnesscenter.com"
        },
        "INS002": {
            "instructor_id": "INS002",
            "name": "Mike Chen",
            "specialty": "Spin, HIIT",
            "contact_info": "mike.chen@fitnesscenter.com"
        },
        "INS003": {
            "instructor_id": "INS003",
            "name": "Emily Davis",
            "specialty": "HIIT, CrossFit",
            "contact_info": "emily.davis@fitnesscenter.com"
        }
    },
    "locations": {
        "LOC001": {
            "location_id": "LOC001",
            "room_name": "Zen Studio",
            "facility": "Main Building",
            "max_capacity": 25
        },
        "LOC002": {
            "location_id": "LOC002",
            "room_name": "Spin Room",
            "facility": "Main Building",
            "max_capacity": 15
        },
        "LOC003": {
            "location_id": "LOC003",
            "room_name": "Fitness Hall A",
            "facility": "Main Building",
            "max_capacity": 30
        }
    },
    "enrollments": {
        "ENR001": {
            "enrollment_id": "ENR001",
            "scheduled_id": "SC001",
            "member_id": "MEM001",
            "enrollment_time": "2024-03-10T14:30:00"
        },
        "ENR002": {
            "enrollment_id": "ENR002",
            "scheduled_id": "SC001",
            "member_id": "MEM002",
            "enrollment_time": "2024-03-10T15:00:00"
        },
        "ENR003": {
            "enrollment_id": "ENR003",
            "scheduled_id": "SC002",
            "member_id": "MEM001",
            "enrollment_time": "2024-03-11T09:00:00"
        },
        "ENR004": {
            "enrollment_id": "ENR004",
            "scheduled_id": "SC003",
            "member_id": "MEM003",
            "enrollment_time": "2024-03-12T10:00:00"
        }
    },
    "members": {
        "MEM001": {
            "member_id": "MEM001",
            "name": "John Smith",
            "membership_status": "active",
            "contact_info": "john.smith@email.com"
        },
        "MEM002": {
            "member_id": "MEM002",
            "name": "Jane Doe",
            "membership_status": "active",
            "contact_info": "jane.doe@email.com"
        },
        "MEM003": {
            "member_id": "MEM003",
            "name": "Bob Wilson",
            "membership_status": "active",
            "contact_info": "bob.wilson@email.com"
        },
        "MEM004": {
            "member_id": "MEM004",
            "name": "Alice Brown",
            "membership_status": "inactive",
            "contact_info": "alice.brown@email.com"
        }
    },
    "next_scheduled_id": 5,
    "next_enrollment_id": 5,
    "current_timestamp": "2024-03-13T10:00:00"
}


class FitnessClassSchedulingSystem:
    """
    A fitness class scheduling system that manages the timetable of various
    exercise classes offered by a fitness center, gym, or health club.
    
    The system provides tools to search for available classes, enroll participants,
    manage instructor and location schedules, and update class information.
    """
    
    def __init__(self) -> None:
        """
        Initialize the FitnessClassSchedulingSystem with default state attributes.
        
        Sets up all state variables for class types, scheduled classes, instructors,
        locations, enrollments, and members.
        
        Args:
            None
        
        Returns:
            None
        """
        self.class_types: Dict[str, Dict[str, Any]] = {}
        self.scheduled_classes: Dict[str, Dict[str, Any]] = {}
        self.instructors: Dict[str, Dict[str, Any]] = {}
        self.locations: Dict[str, Dict[str, Any]] = {}
        self.enrollments: Dict[str, Dict[str, Any]] = {}
        self.members: Dict[str, Dict[str, Any]] = {}
        self.next_scheduled_id: int = 1
        self.next_enrollment_id: int = 1
        self.current_timestamp: str = "2024-03-13T10:00:00"
        
        self._api_description = "Fitness class scheduling system for managing gym class timetables, enrollments, and instructor/location assignments."
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from the provided scenario dictionary.
        
        Args:
            scenario: Dictionary containing the initial state data.
            long_context: Flag for extended context scenarios (unused in this implementation).
        
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
        Return the current state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - class_types: Dictionary of available class types
                - scheduled_classes: Dictionary of scheduled class instances
                - instructors: Dictionary of instructor records
                - locations: Dictionary of location records
                - enrollments: Dictionary of enrollment records
                - members: Dictionary of member records
                - next_scheduled_id: Counter for generating scheduled class IDs
                - next_enrollment_id: Counter for generating enrollment IDs
                - current_timestamp: Current system timestamp
        """
        return {
            "class_types": deepcopy(self.class_types),
            "scheduled_classes": deepcopy(self.scheduled_classes),
            "instructors": deepcopy(self.instructors),
            "locations": deepcopy(self.locations),
            "enrollments": deepcopy(self.enrollments),
            "members": deepcopy(self.members),
            "next_scheduled_id": self.next_scheduled_id,
            "next_enrollment_id": self.next_enrollment_id,
            "current_timestamp": self.current_timestamp
        }
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp string for the system.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        return self.current_timestamp
    
    def _calculate_end_time(self, start_time: str, duration: int) -> str:
        """
        Calculate end time based on start time and duration in minutes.
        
        Args:
            start_time: Start time in HH:MM format.
            duration: Duration in minutes.
        
        Returns:
            str: End time in HH:MM format.
        """
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(minutes=duration)
        return end.strftime("%H:%M")
    
    def _check_time_overlap(self, start1: str, end1: str, start2: str, end2: str) -> bool:
        """
        Check if two time ranges overlap.
        
        Args:
            start1: Start time of first range (HH:MM).
            end1: End time of first range (HH:MM).
            start2: Start time of second range (HH:MM).
            end2: End time of second range (HH:MM).
        
        Returns:
            bool: True if times overlap, False otherwise.
        """
        s1 = datetime.strptime(start1, "%H:%M")
        e1 = datetime.strptime(end1, "%H:%M")
        s2 = datetime.strptime(start2, "%H:%M")
        e2 = datetime.strptime(end2, "%H:%M")
        return s1 < e2 and s2 < e1
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_classes_by_date(self, date: str) -> Dict[str, Any]:
        """
        Retrieve all scheduled classes on a specific date.
        
        Args:
            date: The date to query in YYYY-MM-DD format (e.g., '2024-03-14').
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - date: The queried date
                - classes: List of scheduled class details for that date
                - count: Number of classes found
        """
        classes = []
        for sc_id, sc in self.scheduled_classes.items():
            if sc["date"] == date:
                class_info = deepcopy(sc)
                if sc["class_id"] in self.class_types:
                    class_info["class_name"] = self.class_types[sc["class_id"]]["name"]
                classes.append(class_info)
        
        return {
            "success": True,
            "date": date,
            "classes": classes,
            "count": len(classes)
        }
    
    def get_class_availability(self, scheduled_id: str) -> Dict[str, Any]:
        """
        Check how many spots are left in a scheduled class.
        
        Args:
            scheduled_id: The unique identifier of the scheduled class.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - scheduled_id: The queried class ID
                - available_spots: Number of remaining spots
                - current_enrollment: Current number of enrolled members
                - max_capacity: Maximum class capacity
            Or an error dictionary if class not found.
        """
        if scheduled_id not in self.scheduled_classes:
            return {"error": f"Scheduled class '{scheduled_id}' not found"}
        
        sc = self.scheduled_classes[scheduled_id]
        available = sc["max_capacity"] - sc["current_enrollment"]
        
        return {
            "success": True,
            "scheduled_id": scheduled_id,
            "available_spots": available,
            "current_enrollment": sc["current_enrollment"],
            "max_capacity": sc["max_capacity"]
        }
    
    def get_class_details(self, class_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a class type.
        
        Args:
            class_id: The unique identifier of the class type.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - class_type: Dictionary with class details (name, category, duration, etc.)
            Or an error dictionary if class type not found.
        """
        if class_id not in self.class_types:
            return {"error": f"Class type '{class_id}' not found"}
        
        return {
            "success": True,
            "class_type": deepcopy(self.class_types[class_id])
        }
    
    def get_scheduled_class_info(self, scheduled_id: str) -> Dict[str, Any]:
        """
        Get full details of a specific scheduled class.
        
        Args:
            scheduled_id: The unique identifier of the scheduled class.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - scheduled_class: Dictionary with full scheduled class details
                - class_type: Dictionary with class type information
                - instructor: Dictionary with instructor details
                - location: Dictionary with location details
            Or an error dictionary if not found.
        """
        if scheduled_id not in self.scheduled_classes:
            return {"error": f"Scheduled class '{scheduled_id}' not found"}
        
        sc = deepcopy(self.scheduled_classes[scheduled_id])
        result = {
            "success": True,
            "scheduled_class": sc
        }
        
        if sc["class_id"] in self.class_types:
            result["class_type"] = deepcopy(self.class_types[sc["class_id"]])
        
        if sc["instructor_id"] in self.instructors:
            result["instructor"] = deepcopy(self.instructors[sc["instructor_id"]])
        
        if sc["location"] in self.locations:
            result["location"] = deepcopy(self.locations[sc["location"]])
        
        return result
    
    def list_instructor_schedule(self, instructor_id: str, date: str) -> Dict[str, Any]:
        """
        Retrieve all scheduled classes for a given instructor on a specific date.
        
        Args:
            instructor_id: The unique identifier of the instructor.
            date: The date to query in YYYY-MM-DD format.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - instructor_id: The queried instructor ID
                - date: The queried date
                - classes: List of scheduled classes for this instructor
                - count: Number of classes found
            Or an error dictionary if instructor not found.
        """
        if instructor_id not in self.instructors:
            return {"error": f"Instructor '{instructor_id}' not found"}
        
        classes = []
        for sc_id, sc in self.scheduled_classes.items():
            if sc["instructor_id"] == instructor_id and sc["date"] == date:
                class_info = deepcopy(sc)
                if sc["class_id"] in self.class_types:
                    class_info["class_name"] = self.class_types[sc["class_id"]]["name"]
                classes.append(class_info)
        
        return {
            "success": True,
            "instructor_id": instructor_id,
            "instructor_name": self.instructors[instructor_id]["name"],
            "date": date,
            "classes": classes,
            "count": len(classes)
        }
    
    def list_location_schedule(self, location_id: str, date: str) -> Dict[str, Any]:
        """
        Retrieve all scheduled classes for a given location on a specific date.
        
        Args:
            location_id: The unique identifier of the location.
            date: The date to query in YYYY-MM-DD format.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - location_id: The queried location ID
                - date: The queried date
                - classes: List of scheduled classes at this location
                - count: Number of classes found
            Or an error dictionary if location not found.
        """
        if location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        
        classes = []
        for sc_id, sc in self.scheduled_classes.items():
            if sc["location"] == location_id and sc["date"] == date:
                class_info = deepcopy(sc)
                if sc["class_id"] in self.class_types:
                    class_info["class_name"] = self.class_types[sc["class_id"]]["name"]
                classes.append(class_info)
        
        return {
            "success": True,
            "location_id": location_id,
            "location_name": self.locations[location_id]["room_name"],
            "date": date,
            "classes": classes,
            "count": len(classes)
        }
    
    def get_instructor_by_id(self, instructor_id: str) -> Dict[str, Any]:
        """
        Retrieve instructor details by instructor_id.
        
        Args:
            instructor_id: The unique identifier of the instructor.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - instructor: Dictionary with instructor details
            Or an error dictionary if not found.
        """
        if instructor_id not in self.instructors:
            return {"error": f"Instructor '{instructor_id}' not found"}
        
        return {
            "success": True,
            "instructor": deepcopy(self.instructors[instructor_id])
        }
    
    def get_location_by_id(self, location_id: str) -> Dict[str, Any]:
        """
        Retrieve location details by location_id.
        
        Args:
            location_id: The unique identifier of the location.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - location: Dictionary with location details
            Or an error dictionary if not found.
        """
        if location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        
        return {
            "success": True,
            "location": deepcopy(self.locations[location_id])
        }
    
    def check_member_status(self, member_id: str) -> Dict[str, Any]:
        """
        Verify if a member has active status and is eligible to enroll.
        
        Args:
            member_id: The unique identifier of the member.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - member_id: The queried member ID
                - name: Member's name
                - membership_status: Current membership status
                - is_eligible: Boolean indicating if member can enroll
            Or an error dictionary if member not found.
        """
        if member_id not in self.members:
            return {"error": f"Member '{member_id}' not found"}
        
        member = self.members[member_id]
        is_eligible = member["membership_status"] == "active"
        
        return {
            "success": True,
            "member_id": member_id,
            "name": member["name"],
            "membership_status": member["membership_status"],
            "is_eligible": is_eligible
        }
    
    def list_available_classes(self, date: str) -> Dict[str, Any]:
        """
        Retrieve all scheduled classes on a given date that still have available capacity.
        
        Args:
            date: The date to query in YYYY-MM-DD format.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - date: The queried date
                - classes: List of available classes with capacity info
                - count: Number of available classes
        """
        available_classes = []
        for sc_id, sc in self.scheduled_classes.items():
            if sc["date"] == date and sc["current_enrollment"] < sc["max_capacity"]:
                class_info = deepcopy(sc)
                class_info["available_spots"] = sc["max_capacity"] - sc["current_enrollment"]
                if sc["class_id"] in self.class_types:
                    class_info["class_name"] = self.class_types[sc["class_id"]]["name"]
                available_classes.append(class_info)
        
        return {
            "success": True,
            "date": date,
            "classes": available_classes,
            "count": len(available_classes)
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def enroll_member_in_class(self, member_id: str, scheduled_id: str) -> Dict[str, Any]:
        """
        Register an active member in a scheduled class.
        
        Validates that the member is active and the class has available capacity
        before creating the enrollment.
        
        Args:
            member_id: The unique identifier of the member to enroll.
            scheduled_id: The unique identifier of the scheduled class.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - enrollment_id: The newly created enrollment ID
                - member_id: The enrolled member's ID
                - scheduled_id: The class ID
                - enrollment_time: Timestamp of enrollment
            Or an error dictionary if validation fails.
        """
        if member_id not in self.members:
            return {"error": f"Member '{member_id}' not found"}
        
        if scheduled_id not in self.scheduled_classes:
            return {"error": f"Scheduled class '{scheduled_id}' not found"}
        
        member = self.members[member_id]
        if member["membership_status"] != "active":
            return {"error": f"Member '{member_id}' is not active. Only active members can enroll in classes"}
        
        sc = self.scheduled_classes[scheduled_id]
        if sc["current_enrollment"] >= sc["max_capacity"]:
            return {"error": f"Scheduled class '{scheduled_id}' is at full capacity ({sc['max_capacity']}/{sc['max_capacity']})"}
        
        for enr in self.enrollments.values():
            if enr["member_id"] == member_id and enr["scheduled_id"] == scheduled_id:
                return {"error": f"Member '{member_id}' is already enrolled in class '{scheduled_id}'"}
        
        enrollment_id = f"ENR{self.next_enrollment_id:03d}"
        self.next_enrollment_id += 1
        
        self.enrollments[enrollment_id] = {
            "enrollment_id": enrollment_id,
            "scheduled_id": scheduled_id,
            "member_id": member_id,
            "enrollment_time": self._timestamp()
        }
        
        self.scheduled_classes[scheduled_id]["current_enrollment"] += 1
        
        return {
            "success": True,
            "enrollment_id": enrollment_id,
            "member_id": member_id,
            "scheduled_id": scheduled_id,
            "enrollment_time": self._timestamp()
        }
    
    def cancel_enrollment(self, enrollment_id: str) -> Dict[str, Any]:
        """
        Remove a member's enrollment from a scheduled class.
        
        Args:
            enrollment_id: The unique identifier of the enrollment to cancel.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - enrollment_id: The cancelled enrollment ID
                - member_id: The member's ID
                - scheduled_id: The class ID
                - message: Confirmation message
            Or an error dictionary if enrollment not found.
        """
        if enrollment_id not in self.enrollments:
            return {"error": f"Enrollment '{enrollment_id}' not found"}
        
        enrollment = self.enrollments[enrollment_id]
        scheduled_id = enrollment["scheduled_id"]
        member_id = enrollment["member_id"]
        
        if scheduled_id in self.scheduled_classes:
            self.scheduled_classes[scheduled_id]["current_enrollment"] -= 1
        
        del self.enrollments[enrollment_id]
        
        return {
            "success": True,
            "enrollment_id": enrollment_id,
            "member_id": member_id,
            "scheduled_id": scheduled_id,
            "message": "Enrollment successfully cancelled"
        }
    
    def schedule_class(
        self,
        class_id: str,
        date: str,
        start_time: str,
        instructor_id: str,
        location_id: str,
        max_capacity: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new scheduled class instance.
        
        Validates instructor and location availability, time alignment with class
        duration, and ensures no double-booking conflicts.
        
        Args:
            class_id: The class type ID to schedule.
            date: The date for the class in YYYY-MM-DD format.
            start_time: The start time in HH:MM format.
            instructor_id: The instructor to assign.
            location_id: The location for the class.
            max_capacity: Optional maximum capacity (defaults to location's capacity).
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - scheduled_id: The newly created scheduled class ID
                - scheduled_class: Full details of the new scheduled class
            Or an error dictionary if validation fails.
        """
        if class_id not in self.class_types:
            return {"error": f"Class type '{class_id}' not found"}
        
        if instructor_id not in self.instructors:
            return {"error": f"Instructor '{instructor_id}' not found"}
        
        if location_id not in self.locations:
            return {"error": f"Location '{location_id}' not found"}
        
        class_type = self.class_types[class_id]
        duration = class_type["duration"]
        end_time = self._calculate_end_time(start_time, duration)
        
        for sc_id, sc in self.scheduled_classes.items():
            if sc["instructor_id"] == instructor_id and sc["date"] == date:
                if self._check_time_overlap(start_time, end_time, sc["start_time"], sc["end_time"]):
                    return {"error": f"Instructor '{instructor_id}' is already scheduled at this time on {date}"}
        
        for sc_id, sc in self.scheduled_classes.items():
            if sc["location"] == location_id and sc["date"] == date:
                if self._check_time_overlap(start_time, end_time, sc["start_time"], sc["end_time"]):
                    return {"error": f"Location '{location_id}' is already booked at this time on {date}"}
        
        location = self.locations[location_id]
        if max_capacity is None:
            max_capacity = location["max_capacity"]
        elif max_capacity > location["max_capacity"]:
            return {"error": f"Requested capacity ({max_capacity}) exceeds location capacity ({location['max_capacity']})"}
        
        scheduled_id = f"SC{self.next_scheduled_id:03d}"
        self.next_scheduled_id += 1
        
        new_class = {
            "scheduled_id": scheduled_id,
            "class_id": class_id,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "instructor_id": instructor_id,
            "location": location_id,
            "current_enrollment": 0,
            "max_capacity": max_capacity
        }
        
        self.scheduled_classes[scheduled_id] = new_class
        
        return {
            "success": True,
            "scheduled_id": scheduled_id,
            "scheduled_class": deepcopy(new_class)
        }
    
    def reschedule_class(
        self,
        scheduled_id: str,
        new_date: Optional[str] = None,
        new_start_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the date or time of an existing scheduled class.
        
        Revalidates for conflicts and duration alignment.
        
        Args:
            scheduled_id: The unique identifier of the scheduled class.
            new_date: Optional new date in YYYY-MM-DD format.
            new_start_time: Optional new start time in HH:MM format.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: Boolean indicating operation success
                - scheduled_id: The rescheduled class ID
                - scheduled_class: Updated class details
            Or an error dictionary if validation fails.
        """
        if scheduled_id not in self.scheduled_classes:
            return {"error": f"Scheduled class '{scheduled_id}' not found"}
        
        if new_date is None and new_start_time is None:
            return {"error": "At least one of new_date or new_start_time must be provided"}
        
        sc = self.scheduled_classes[scheduled_id]
        class_type = self.class_types.get(sc["class_id"])
        
        if not class_type:
            return {"error": f"Class type '{sc['class_id']}' not found"}
        
        date = new_date if new_date else sc["date"]
        start_time = new_start_time if new_start_time else sc["start_time"]
        end_time = self._calculate_end_time(start_time, class_type["duration"])
        
        # Check instructor conflict
        for other_id, other_sc in self.scheduled_classes.items():
            if other_id == scheduled_id:
                continue
            if other_sc["instructor_id"] == sc["instructor_id"] and other_sc["date"] == date:
                if self._check_time_overlap(start_time, end_time, other_sc["start_time"], other_sc["end_time"]):
                    return {"error": f"Instructor '{sc['instructor_id']}' has a conflict at this time"}
        
        # Check room conflict
        for other_id, other_sc in self.scheduled_classes.items():
            if other_id == scheduled_id:
                continue
            if other_sc.get("room_id") == sc.get("room_id") and other_sc["date"] == date:
                if self._check_time_overlap(start_time, end_time, other_sc["start_time"], other_sc["end_time"]):
                    return {"error": f"Room '{sc.get('room_id')}' is already booked at this time"}
        
        sc["date"] = date
        sc["start_time"] = start_time
        sc["end_time"] = end_time
        
        return {"success": True, "scheduled_class": sc}
    
    def cancel_scheduled_class(self, scheduled_id: str) -> dict:
        if scheduled_id not in self.scheduled_classes:
            return {"error": f"Scheduled class '{scheduled_id}' not found"}
        
        cancelled = self.scheduled_classes.pop(scheduled_id)
        return {"success": True, "cancelled_class": cancelled}
    
    def get_schedule_by_date(self, date: str) -> list:
        result = []
        for sc_id, sc in self.scheduled_classes.items():
            if sc["date"] == date:
                result.append({"id": sc_id, **sc})
        return sorted(result, key=lambda x: x["start_time"])
    
    def get_instructor_schedule(self, instructor_id: str, date: str = None) -> list:
        result = []
        for sc_id, sc in self.scheduled_classes.items():
            if sc["instructor_id"] == instructor_id:
                if date is None or sc["date"] == date:
                    result.append({"id": sc_id, **sc})
        return sorted(result, key=lambda x: (x["date"], x["start_time"]))
    
    def get_room_availability(self, room_id: str, date: str) -> list:
        if not hasattr(self, 'rooms') or room_id not in self.rooms:
            return []
        
        room = self.rooms[room_id]
        booked_slots = []
        
        for sc in self.scheduled_classes.values():
            if sc.get("room_id") == room_id and sc["date"] == date:
                booked_slots.append((sc["start_time"], sc["end_time"]))
        
        available_slots = []
        current_time = room["available_from"]
        
        booked_slots.sort()
        
        for start, end in booked_slots:
            if current_time < start:
                available_slots.append({"from": current_time, "to": start})
            current_time = max(current_time, end)
        
        if current_time < room["available_until"]:
            available_slots.append({"from": current_time, "to": room["available_until"]})
        
        return available_slots


__TEST_CASES__ = [
    {
        "name": "test_add_class_type",
        "input": {"class_id": "yoga101", "name": "Beginner Yoga", "duration": 60, "max_capacity": 20},
        "expected_keys": ["success", "class_type"]
    },
    {
        "name": "test_add_instructor",
        "input": {"instructor_id": "inst001", "name": "Sarah Johnson", "specializations": ["yoga", "pilates"]},
        "expected_keys": ["success", "instructor"]
    },
    {
        "name": "test_add_room",
        "input": {"room_id": "room_a", "name": "Studio A", "capacity": 25, "available_from": "06:00", "available_until": "22:00"},
        "expected_keys": ["success", "room"]
    },
    {
        "name": "test_schedule_class_success",
        "setup": ["add_class_type", "add_instructor", "add_room"],
        "input": {"class_id": "yoga101", "instructor_id": "inst001", "room_id": "room_a", "date": "2024-01-15", "start_time": "09:00"},
        "expected_keys": ["success", "scheduled_class"]
    },
    {
        "name": "test_schedule_class_instructor_conflict",
        "setup": ["add_class_type", "add_instructor", "add_room", "schedule_first_class"],
        "input": {"class_id": "yoga101", "instructor_id": "inst001", "room_id": "room_a", "date": "2024-01-15", "start_time": "09:30"},
        "expected_keys": ["error"]
    },
    {
        "name": "test_reschedule_class",
        "setup": ["add_class_type", "add_instructor", "add_room", "schedule_first_class"],
        "input": {"scheduled_id": "sc001", "new_date": "2024-01-16", "new_start_time": "10:00"},
        "expected_keys": ["success", "scheduled_class"]
    },
    {
        "name": "test_cancel_scheduled_class",
        "setup": ["add_class_type", "add_instructor", "add_room", "schedule_first_class"],
        "input": {"scheduled_id": "sc001"},
        "expected_keys": ["success", "cancelled_class"]
    },
    {
        "name": "test_get_schedule_by_date",
        "setup": ["add_class_type", "add_instructor", "add_room", "schedule_first_class"],
        "input": {"date": "2024-01-15"},
        "expected_type": "list"
    },
    {
        "name": "test_get_instructor_schedule",
        "setup": ["add_class_type", "add_instructor", "add_room", "schedule_first_class"],
        "input": {"instructor_id": "inst001"},
        "expected_type": "list"
    },
    {
        "name": "test_get_room_availability",
        "setup": ["add_class_type", "add_instructor", "add_room", "schedule_first_class"],
        "input": {"room_id": "room_a", "date": "2024-01-15"},
        "expected_type": "list"
    }
]