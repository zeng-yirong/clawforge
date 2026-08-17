"""
University Course Registration System API

A university course registration system manages student enrollments in academic courses,
tracks available seats, and maintains waitlists for oversubscribed classes.
"""

import re
from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE: Dict[str, Any] = {
    "students": [
        {
            "student_id": "STU001",
            "name": "Alice Johnson",
            "email": "alice.johnson@university.edu",
            "academic_program": "Computer Science",
            "enrollment_status": "active"
        },
        {
            "student_id": "STU002",
            "name": "Bob Smith",
            "email": "bob.smith@university.edu",
            "academic_program": "Mathematics",
            "enrollment_status": "active"
        },
        {
            "student_id": "STU003",
            "name": "Carol Davis",
            "email": "carol.davis@university.edu",
            "academic_program": "Physics",
            "enrollment_status": "active"
        },
        {
            "student_id": "STU004",
            "name": "David Lee",
            "email": "david.lee@university.edu",
            "academic_program": "Computer Science",
            "enrollment_status": "active"
        }
    ],
    "courses": [
        {
            "course_id": "CRS001",
            "course_code": "CS101",
            "title": "Introduction to Programming",
            "instructor": "Dr. Emily Chen",
            "capacity": 3,
            "current_enrollment": 3,
            "schedule": "MWF 9:00-10:00",
            "credits": 3
        },
        {
            "course_id": "CRS002",
            "course_code": "MATH201",
            "title": "Linear Algebra",
            "instructor": "Dr. Michael Brown",
            "capacity": 30,
            "current_enrollment": 15,
            "schedule": "TTH 10:00-11:30",
            "credits": 4
        },
        {
            "course_id": "CRS003",
            "course_code": "PHYS101",
            "title": "Physics I",
            "instructor": "Dr. Sarah Wilson",
            "capacity": 25,
            "current_enrollment": 25,
            "schedule": "MWF 11:00-12:00",
            "credits": 4
        }
    ],
    "enrollments": [
        {
            "enrollment_id": "ENR001",
            "student_id": "STU001",
            "course_id": "CRS001",
            "status": "enrolled",
            "enrollment_date": "2024-01-10T08:00:00"
        },
        {
            "enrollment_id": "ENR002",
            "student_id": "STU002",
            "course_id": "CRS001",
            "status": "enrolled",
            "enrollment_date": "2024-01-10T09:00:00"
        },
        {
            "enrollment_id": "ENR003",
            "student_id": "STU003",
            "course_id": "CRS001",
            "status": "enrolled",
            "enrollment_date": "2024-01-10T10:00:00"
        },
        {
            "enrollment_id": "ENR004",
            "student_id": "STU001",
            "course_id": "CRS002",
            "status": "enrolled",
            "enrollment_date": "2024-01-11T08:00:00"
        },
        {
            "enrollment_id": "ENR005",
            "student_id": "STU003",
            "course_id": "CRS003",
            "status": "enrolled",
            "enrollment_date": "2024-01-12T08:00:00"
        }
    ],
    "waitlists": [
        {
            "waitlist_id": "WL001",
            "course_id": "CRS001",
            "student_id": "STU004",
            "position": 1,
            "timestamp": "2024-01-15T10:30:00"
        },
        {
            "waitlist_id": "WL002",
            "course_id": "CRS003",
            "student_id": "STU002",
            "position": 1,
            "timestamp": "2024-01-16T09:00:00"
        },
        {
            "waitlist_id": "WL003",
            "course_id": "CRS003",
            "student_id": "STU004",
            "position": 2,
            "timestamp": "2024-01-16T09:15:00"
        }
    ],
    "max_waitlist_size": 50,
    "next_enrollment_id": 6,
    "next_waitlist_id": 4,
    "next_course_id": 4,
    "next_student_id": 5,
    "current_timestamp": "2024-01-20T12:00:00"
}


class UniversityCourseRegistrationSystem:
    """
    A university course registration system API that manages student enrollments,
    tracks available seats, and maintains waitlists for oversubscribed classes.
    
    This system supports operations like registration, cancellation, waitlist management,
    and retrieving enrollment/waitlist positions while enforcing academic policies.
    """
    
    def __init__(self) -> None:
        """
        Initialize the University Course Registration System.
        
        Declares all state attributes with type hints and sets up the API description.
        """
        self.students: List[Dict[str, Any]] = []
        self.courses: List[Dict[str, Any]] = []
        self.enrollments: List[Dict[str, Any]] = []
        self.waitlists: List[Dict[str, Any]] = []
        self.max_waitlist_size: int = 50
        self.next_enrollment_id: int = 1
        self.next_waitlist_id: int = 1
        self.next_course_id: int = 1
        self.next_student_id: int = 1
        self.current_timestamp: str = ""
        
        self._api_description = (
            "University Course Registration System API for managing student enrollments, "
            "course capacities, and waitlists in academic course registration."
        )
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data. If keys are missing,
                     falls back to DEFAULT_STATE values.
            long_context: Flag for extended context loading (unused in base implementation).
        
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
            Dict[str, Any]: A dictionary containing all internal state variables including:
                - students: List of student records
                - courses: List of course records
                - enrollments: List of enrollment records
                - waitlists: List of waitlist entries
                - max_waitlist_size: Maximum allowed waitlist size
                - next_enrollment_id: Counter for next enrollment ID
                - next_waitlist_id: Counter for next waitlist ID
                - next_course_id: Counter for next course ID
                - next_student_id: Counter for next student ID
                - current_timestamp: Current system timestamp
        """
        return {
            "students": deepcopy(self.students),
            "courses": deepcopy(self.courses),
            "enrollments": deepcopy(self.enrollments),
            "waitlists": deepcopy(self.waitlists),
            "max_waitlist_size": self.max_waitlist_size,
            "next_enrollment_id": self.next_enrollment_id,
            "next_waitlist_id": self.next_waitlist_id,
            "next_course_id": self.next_course_id,
            "next_student_id": self.next_student_id,
            "current_timestamp": self.current_timestamp
        }
    
    def _timestamp(self) -> str:
        """
        Generate a unified timestamp string for the system.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        if self.current_timestamp:
            return self.current_timestamp
        return datetime.now().isoformat()
    
    def _find_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to find a student by ID.
        
        Args:
            student_id: The unique identifier of the student.
        
        Returns:
            Optional[Dict[str, Any]]: Student record or None if not found.
        """
        for student in self.students:
            if student["student_id"] == student_id:
                return student
        return None
    
    def _find_course_by_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to find a course by ID.
        
        Args:
            course_id: The unique identifier of the course.
        
        Returns:
            Optional[Dict[str, Any]]: Course record or None if not found.
        """
        for course in self.courses:
            if course["course_id"] == course_id:
                return course
        return None
    
    def _find_course_by_code(self, course_code: str) -> Optional[Dict[str, Any]]:
        """
        Helper to find a course by course code.
        
        Args:
            course_code: The course code (e.g., CS101).
        
        Returns:
            Optional[Dict[str, Any]]: Course record or None if not found.
        """
        for course in self.courses:
            if course.get("course_code") == course_code:
                return course
        return None
        
    def _resolve_course(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Helper to find a course by either its ID or course code.
        
        Args:
            identifier: Course ID or Course Code.
            
        Returns:
            Optional[Dict[str, Any]]: Course record or None if not found.
        """
        course = self._find_course_by_id(identifier)
        if not course:
            course = self._find_course_by_code(identifier)
        return course
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_student_by_name(self, name: str) -> Dict[str, Any]:
        """
        Retrieve student information using their name.
        
        Args:
            name: The full name of the student to search for.
        
        Returns:
            Dict[str, Any]: Student information including id, email, program,
                           or an error dictionary if student not found.
        """
        for student in self.students:
            if student["name"].lower() == name.lower():
                return {
                    "student_id": student["student_id"],
                    "name": student["name"],
                    "email": student["email"],
                    "academic_program": student.get("academic_program", ""),
                    "enrollment_status": student.get("enrollment_status", "active")
                }
        return {"error": f"Student with name '{name}' not found"}
    
    def get_student_by_id(self, student_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a student using their unique student_id.
        
        Args:
            student_id: The unique identifier of the student.
        
        Returns:
            Dict[str, Any]: Full student details or error if not found.
        """
        student = self._find_student_by_id(student_id)
        if student:
            return deepcopy(student)
        return {"error": f"Student with ID '{student_id}' not found"}
    
    def get_waitlist_entries_for_student(self, student_id: str) -> Dict[str, Any]:
        """
        List all courses for which a student is on the waitlist.
        
        Args:
            student_id: The unique identifier of the student.
        
        Returns:
            Dict[str, Any]: List of waitlist entries with course details,
                           position, and timestamp, or error if student not found.
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        entries = []
        for wl in self.waitlists:
            if wl["student_id"] == student_id:
                course = self._find_course_by_id(wl["course_id"])
                course_info = course["title"] if course else "Unknown"
                entries.append({
                    "waitlist_id": wl["waitlist_id"],
                    "course_id": wl["course_id"],
                    "course_title": course_info,
                    "position": wl["position"],
                    "timestamp": wl["timestamp"]
                })
        
        return {
            "student_id": student_id,
            "student_name": student["name"],
            "waitlist_entries": entries,
            "total_count": len(entries)
        }
    
    def get_waitlist_position(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Get a student's position in the waitlist for a specific course.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Waitlist position information or error if not found.
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
            
        resolved_course_id = course["course_id"]
        
        for wl in self.waitlists:
            if wl["student_id"] == student_id and wl["course_id"] == resolved_course_id:
                total_on_waitlist = sum(1 for w in self.waitlists if w["course_id"] == resolved_course_id)
                return {
                    "student_id": student_id,
                    "course_id": resolved_course_id,
                    "position": wl["position"],
                    "total_on_waitlist": total_on_waitlist,
                    "timestamp": wl["timestamp"]
                }
        
        return {"error": f"Student '{student_id}' is not on the waitlist for course '{course_id}'"}
    
    def get_course_waitlist(self, course_id: str) -> Dict[str, Any]:
        """
        Retrieve the full ordered waitlist for a given course.
        
        Args:
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Ordered list of waitlist entries or error if course not found.
        """
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
            
        resolved_course_id = course["course_id"]
        
        waitlist_entries = []
        for wl in self.waitlists:
            if wl["course_id"] == resolved_course_id:
                student = self._find_student_by_id(wl["student_id"])
                student_name = student["name"] if student else "Unknown"
                waitlist_entries.append({
                    "waitlist_id": wl["waitlist_id"],
                    "student_id": wl["student_id"],
                    "student_name": student_name,
                    "position": wl["position"],
                    "timestamp": wl["timestamp"]
                })
        
        waitlist_entries.sort(key=lambda x: x["position"])
        
        return {
            "course_id": resolved_course_id,
            "course_title": course["title"],
            "waitlist": waitlist_entries,
            "total_count": len(waitlist_entries)
        }
    
    def get_course_details(self, course_id: str) -> Dict[str, Any]:
        """
        Retrieve course information including title, instructor, capacity, and enrollment.
        
        Args:
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Course details or error if not found.
        """
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
        
        return deepcopy(course)
    
    def get_course_info(self, course_id: str) -> Dict[str, Any]:
        """
        Retrieve course information including enrolled count.
        
        Args:
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Course info with enrolled_count or error if not found.
        """
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
        
        return {
            "course_id": course["course_id"],
            "course_code": course.get("course_code", ""),
            "title": course["title"],
            "instructor": course["instructor"],
            "capacity": course["capacity"],
            "enrolled_count": course["current_enrollment"],
            "schedule": course.get("schedule", ""),
            "credits": course.get("credits", 0)
        }
    
    def check_course_capacity_status(self, course_id: str) -> Dict[str, Any]:
        """
        Determine if a course is full, has available seats, or is closed.
        
        Args:
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Capacity status information or error if course not found.
        """
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
        
        available_seats = course["capacity"] - course["current_enrollment"]
        
        if available_seats > 0:
            status = "available"
        elif available_seats == 0:
            status = "full"
        else:
            status = "overenrolled"
        
        return {
            "course_id": course["course_id"],
            "course_title": course["title"],
            "capacity": course["capacity"],
            "current_enrollment": course["current_enrollment"],
            "available_seats": max(0, available_seats),
            "status": status
        }
    
    def is_student_enrolled_in_course(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Check whether a student is already enrolled in a specific course.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Enrollment status information or error if entities not found.
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
            
        resolved_course_id = course["course_id"]
        
        for enrollment in self.enrollments:
            if (enrollment["student_id"] == student_id and 
                enrollment["course_id"] == resolved_course_id and
                enrollment["status"] == "enrolled"):
                return {
                    "student_id": student_id,
                    "course_id": resolved_course_id,
                    "is_enrolled": True,
                    "enrollment_id": enrollment["enrollment_id"]
                }
        
        return {
            "student_id": student_id,
            "course_id": resolved_course_id,
            "is_enrolled": False
        }
    
    def is_student_on_waitlist_for_course(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Check if a student is already on the waitlist for a given course.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Waitlist status information or error if entities not found.
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
            
        resolved_course_id = course["course_id"]
        
        for wl in self.waitlists:
            if wl["student_id"] == student_id and wl["course_id"] == resolved_course_id:
                return {
                    "student_id": student_id,
                    "course_id": resolved_course_id,
                    "is_on_waitlist": True,
                    "position": wl["position"],
                    "waitlist_id": wl["waitlist_id"]
                }
        
        return {
            "student_id": student_id,
            "course_id": resolved_course_id,
            "is_on_waitlist": False
        }
    
    def get_enrollment_status(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Retrieve a student's enrollment status for a specific course.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Enrollment status (enrolled, waitlisted, dropped, or not_registered).
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
            
        resolved_course_id = course["course_id"]
        
        for enrollment in self.enrollments:
            if enrollment["student_id"] == student_id and enrollment["course_id"] == resolved_course_id:
                return {
                    "student_id": student_id,
                    "course_id": resolved_course_id,
                    "status": enrollment["status"],
                    "enrollment_id": enrollment["enrollment_id"]
                }
        
        for wl in self.waitlists:
            if wl["student_id"] == student_id and wl["course_id"] == resolved_course_id:
                return {
                    "student_id": student_id,
                    "course_id": resolved_course_id,
                    "status": "waitlisted",
                    "waitlist_position": wl["position"]
                }
        
        return {
            "student_id": student_id,
            "course_id": resolved_course_id,
            "status": "not_registered"
        }
    
    def get_student_schedule(self, student_id: str) -> Dict[str, Any]:
        """
        Get a student's complete course schedule.
        
        Args:
            student_id: The unique identifier of the student.
        
        Returns:
            Dict[str, Any]: Student's enrolled courses and waitlisted courses.
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        # Get enrolled courses
        enrolled_courses = []
        for enrollment in self.enrollments:
            if enrollment["student_id"] == student_id and enrollment["status"] == "enrolled":
                course = self._find_course_by_id(enrollment["course_id"])
                if course:
                    enrolled_courses.append({
                        "course_id": course["course_id"],
                        "title": course["title"],
                        "instructor": course["instructor"],
                        "schedule": course.get("schedule", ""),
                        "credits": course.get("credits", 0),
                        "enrollment_date": enrollment.get("enrollment_date", "")
                    })
        
        # Get waitlisted courses
        waitlisted_courses = []
        for waitlist in self.waitlists:
            if waitlist["student_id"] == student_id:
                course = self._find_course_by_id(waitlist["course_id"])
                if course:
                    waitlisted_courses.append({
                        "course_id": course["course_id"],
                        "title": course["title"],
                        "instructor": course["instructor"],
                        "schedule": course.get("schedule", ""),
                        "credits": course.get("credits", 0),
                        "position": waitlist["position"],
                        "added_date": waitlist["timestamp"]
                    })
        
        total_credits = sum(c["credits"] for c in enrolled_courses)
        
        return {
            "student_id": student_id,
            "student_name": student["name"],
            "enrolled_courses": enrolled_courses,
            "waitlisted_courses": waitlisted_courses,
            "total_enrolled": len(enrolled_courses),
            "total_waitlisted": len(waitlisted_courses),
            "total_credits": total_credits
        }
    
    def check_schedule_conflict(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Check if a course would conflict with student's current schedule.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier or code of the course to check.
        
        Returns:
            Dict[str, Any]: Conflict information.
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
        
        new_schedule = course.get("schedule", "")
        conflicts = []
        
        for enrollment in self.enrollments:
            if enrollment["student_id"] == student_id and enrollment["status"] == "enrolled":
                enrolled_course = self._find_course_by_id(enrollment["course_id"])
                if enrolled_course:
                    enrolled_schedule = enrolled_course.get("schedule", "")
                    if enrolled_schedule and enrolled_schedule == new_schedule:
                        conflicts.append({
                            "course_id": enrolled_course["course_id"],
                            "title": enrolled_course["title"],
                            "schedule": enrolled_schedule
                        })
        
        return {
            "has_conflict": len(conflicts) > 0,
            "conflicts": conflicts,
            "course_to_add": {
                "course_id": course["course_id"],
                "title": course["title"],
                "schedule": course.get("schedule", "")
            }
        }
    
    def list_all_courses(self) -> Dict[str, Any]:
        """
        List all available courses in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: List of all courses with total count.
        """
        courses_list = []
        for course in self.courses:
            courses_list.append({
                "course_id": course["course_id"],
                "course_code": course.get("course_code", ""),
                "title": course["title"],
                "instructor": course["instructor"],
                "capacity": course["capacity"],
                "current_enrollment": course["current_enrollment"],
                "available_seats": max(0, course["capacity"] - course["current_enrollment"]),
                "schedule": course.get("schedule", ""),
                "credits": course.get("credits", 0)
            })
        
        return {
            "courses": courses_list,
            "total_count": len(courses_list)
        }
    
    def get_waitlist(self, course_id: str) -> Dict[str, Any]:
        """
        Get the waitlist for a specific course.
        
        Args:
            course_id: The unique identifier or code of the course.
        
        Returns:
            Dict[str, Any]: Waitlist information for the course.
        """
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
            
        resolved_course_id = course["course_id"]
        
        waitlist_entries = []
        for wl in self.waitlists:
            if wl["course_id"] == resolved_course_id:
                student = self._find_student_by_id(wl["student_id"])
                student_name = student["name"] if student else "Unknown"
                waitlist_entries.append({
                    "waitlist_id": wl["waitlist_id"],
                    "student_id": wl["student_id"],
                    "student_name": student_name,
                    "position": wl["position"],
                    "timestamp": wl["timestamp"]
                })
        
        waitlist_entries.sort(key=lambda x: x["position"])
        
        return {
            "course_id": resolved_course_id,
            "course_title": course["title"],
            "waitlist": waitlist_entries,
            "total_count": len(waitlist_entries)
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def add_course(self, course_code: str, title: str, instructor: str, capacity: int,
                   schedule: str = "", credits: int = 3) -> Dict[str, Any]:
        """
        Add a new course to the system.
        
        Args:
            course_code: The course code/identifier (e.g., CS101).
            title: The title of the course.
            instructor: The instructor's name.
            capacity: Maximum number of students allowed.
            schedule: Course schedule (e.g., "MWF 9:00-10:00").
            credits: Number of credits for the course.
        
        Returns:
            Dict[str, Any]: Success status with course details or error.
        """
        existing = self._find_course_by_code(course_code)
        if existing:
            return {"error": f"Course with code '{course_code}' already exists"}
        
        new_course_id = f"CRS{self.next_course_id:03d}"
        
        new_course = {
            "course_id": new_course_id,
            "course_code": course_code,
            "title": title,
            "instructor": instructor,
            "capacity": capacity,
            "current_enrollment": 0,
            "schedule": schedule,
            "credits": credits
        }
        
        self.courses.append(new_course)
        self.next_course_id += 1
        
        return deepcopy(new_course)
    
    def register_student(self, student_id: str, name: str, email: str, academic_program: str) -> Dict[str, Any]:
        """
        Register a new student in the system.
        
        Args:
            student_id: The unique identifier for the student.
            name: The student's full name.
            email: The student's email address.
            academic_program: The student's academic major/program.
        
        Returns:
            Dict[str, Any]: Success status with student details or error.
        """
        existing = self._find_student_by_id(student_id)
        if existing:
            return {"error": f"Student with ID '{student_id}' already exists"}
        
        if not self._validate_email(email):
            return {"error": "Invalid email format"}
        
        new_student = {
            "student_id": student_id,
            "name": name,
            "email": email,
            "academic_program": academic_program,
            "enrollment_status": "active",
            "registration_date": self._timestamp()
        }
        
        self.students.append(new_student)
        self.next_student_id += 1
        
        return deepcopy(new_student)
    
    def enroll_student_in_course(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Enroll a student in a specific course.
        
        Args:
            student_id: The student's unique identifier.
            course_id: The course unique identifier or code to enroll in.
        
        Returns:
            Dict[str, Any]: Enrollment details or error.
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
            
        resolved_course_id = course["course_id"]
        
        # Check if already enrolled
        status_check = self.is_student_enrolled_in_course(student_id, resolved_course_id)
        if status_check.get("is_enrolled"):
            return {"error": f"Student is already enrolled in '{course.get('course_code', resolved_course_id)}'"}
        
        # Check course capacity
        if course["current_enrollment"] >= course["capacity"]:
            return {"error": f"Course '{course.get('course_code', resolved_course_id)}' is at full capacity"}
        
        enrollment_id = f"ENR{self.next_enrollment_id:03d}"
        
        new_enrollment = {
            "enrollment_id": enrollment_id,
            "student_id": student_id,
            "course_id": resolved_course_id,
            "status": "enrolled",
            "enrollment_date": self._timestamp()
        }
        
        self.enrollments.append(new_enrollment)
        course["current_enrollment"] += 1
        self.next_enrollment_id += 1
        
        return {
            "enrollment_id": enrollment_id,
            "student_id": student_id,
            "course_id": resolved_course_id,
            "course_code": course.get("course_code", ""),
            "status": "enrolled"
        }
    
    def drop_course(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Drop a student from a course.
        
        Args:
            student_id: The student's unique identifier.
            course_id: The course unique identifier or code to drop.
        
        Returns:
            Dict[str, Any]: Success status with details or error.
        """
        student = self._find_student_by_id(student_id)
        if not student:
            return {"error": f"Student with ID '{student_id}' not found"}
            
        course = self._resolve_course(course_id)
        if not course:
            return {"error": f"Course '{course_id}' not found"}
            
        resolved_course_id = course["course_id"]
        
        enrollment_to_drop = None
        for enr in self.enrollments:
            if enr["student_id"] == student_id and enr["course_id"] == resolved_course_id and enr["status"] == "enrolled":
                enrollment_to_drop = enr
                break
                
        if not enrollment_to_drop:
            return {"error": f"Student is not enrolled in '{course.get('course_code', resolved_course_id)}'"}
        
        enrollment_to_drop["status"] = "dropped"
        course["current_enrollment"] -= 1
        
        return {
            "student_id": student_id,
            "course_id": resolved_course_id,
            "course_code": course.get("course_code", ""),
            "status": "dropped"
        }


__TEST_CASES__ = [
    {
        "name": "test_enroll_student_success",
        "setup": lambda: UniversityCourseRegistrationSystem(),
        "action": lambda sys: sys.enroll_student_in_course("STU001", "MATH201"),
        "expected": {
            "enrollment_id": "ENR006",
            "student_id": "STU001",
            "course_id": "CRS002",
            "course_code": "MATH201",
            "status": "enrolled"
        }
    },
    {
        "name": "test_enroll_nonexistent_student",
        "setup": lambda: UniversityCourseRegistrationSystem(),
        "action": lambda sys: sys.enroll_student_in_course("FAKE001", "CS101"),
        "expected": {"error": "Student with ID 'FAKE001' not found"}
    },
    {
        "name": "test_course_capacity_limit",
        "setup": lambda: UniversityCourseRegistrationSystem(),
        "action": lambda sys: sys.enroll_student_in_course("STU004", "CS101"),
        "expected": {"error": "Course 'CS101' is at full capacity"}
    },
    {
        "name": "test_register_duplicate_student",
        "setup": lambda: UniversityCourseRegistrationSystem(),
        "action": lambda sys: sys.register_student("STU001", "Alice Clone", "alice@university.edu", "Computer Science"),
        "expected": {"error": "Student with ID 'STU001' already exists"}
    }
]