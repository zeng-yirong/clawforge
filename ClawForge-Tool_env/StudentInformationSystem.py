"""
Student Information System (SIS) Environment API

A stateful software environment for managing academic data including student demographics,
course offerings, and enrollment records.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE = {
    "students": {
        "STU001": {
            "student_id": "STU001",
            "name": "Alice Johnson",
            "year_level": 2,
            "program": "Computer Science",
            "enrollment_status": "active"
        },
        "STU002": {
            "student_id": "STU002",
            "name": "Bob Smith",
            "year_level": 3,
            "program": "Mathematics",
            "enrollment_status": "active"
        },
        "STU003": {
            "student_id": "STU003",
            "name": "Carol Williams",
            "year_level": 1,
            "program": "Physics",
            "enrollment_status": "active"
        },
        "STU004": {
            "student_id": "STU004",
            "name": "David Brown",
            "year_level": 4,
            "program": "Computer Science",
            "enrollment_status": "inactive"
        }
    },
    "courses": {
        "CRS101": {
            "course_id": "CRS101",
            "course_name": "Introduction to Programming",
            "department": "Computer Science",
            "credits": 3,
            "max_capacity": 30,
            "registration_start": "2024-01-01",
            "registration_end": "2024-02-15"
        },
        "CRS102": {
            "course_id": "CRS102",
            "course_name": "Calculus I",
            "department": "Mathematics",
            "credits": 4,
            "max_capacity": 25,
            "registration_start": "2024-01-01",
            "registration_end": "2024-02-15"
        },
        "CRS103": {
            "course_id": "CRS103",
            "course_name": "Physics 101",
            "department": "Physics",
            "credits": 4,
            "max_capacity": 20,
            "registration_start": "2024-01-01",
            "registration_end": "2024-02-15"
        },
        "CRS104": {
            "course_id": "CRS104",
            "course_name": "Data Structures",
            "department": "Computer Science",
            "credits": 3,
            "max_capacity": 2,
            "registration_start": "2024-01-01",
            "registration_end": "2024-02-15"
        }
    },
    "enrollments": {
        "ENR001": {
            "enrollment_id": "ENR001",
            "student_id": "STU001",
            "course_id": "CRS101",
            "enrollment_date": "2024-01-15",
            "status": "active"
        },
        "ENR002": {
            "enrollment_id": "ENR002",
            "student_id": "STU002",
            "course_id": "CRS102",
            "enrollment_date": "2024-01-16",
            "status": "active"
        },
        "ENR003": {
            "enrollment_id": "ENR003",
            "student_id": "STU003",
            "course_id": "CRS103",
            "enrollment_date": "2024-01-17",
            "status": "dropped"
        },
        "ENR004": {
            "enrollment_id": "ENR004",
            "student_id": "STU001",
            "course_id": "CRS104",
            "enrollment_date": "2024-01-18",
            "status": "active"
        },
        "ENR005": {
            "enrollment_id": "ENR005",
            "student_id": "STU002",
            "course_id": "CRS104",
            "enrollment_date": "2024-01-19",
            "status": "active"
        }
    },
    "current_user": "admin",
    "enrollment_counter": 6
}


class StudentInformationSystem:
    """
    A Student Information System environment for managing academic data.
    
    This system manages student demographics, course offerings, and enrollment records.
    It maintains persistent relationships between students and courses, tracks enrollment
    timestamps, and supports administrative workflows such as registration and reporting.
    """

    def __init__(self):
        """
        Initialize the Student Information System.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self.students: Dict[str, Dict[str, Any]] = {}
        self.courses: Dict[str, Dict[str, Any]] = {}
        self.enrollments: Dict[str, Dict[str, Any]] = {}
        self.current_user: str = ""
        self.enrollment_counter: int = 0
        
        self._api_description = "A Student Information System for managing student demographics, course offerings, and enrollment records in educational institutions."

    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp string.
        
        Args:
            None
        
        Returns:
            str: ISO format date string (YYYY-MM-DD).
        """
        return datetime.now().strftime("%Y-%m-%d")

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for extended context loading (unused).
            
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
                - students: All registered student records
                - courses: All course offerings
                - enrollments: All enrollment records
                - current_user: The current authenticated user
                - enrollment_counter: Counter for generating enrollment IDs
        """
        return {
            "students": deepcopy(self.students),
            "courses": deepcopy(self.courses),
            "enrollments": deepcopy(self.enrollments),
            "current_user": self.current_user,
            "enrollment_counter": self.enrollment_counter
        }

    # ==================== Query Operations ====================

    def get_student_by_id(self, student_id: str) -> Dict[str, Any]:
        """
        Retrieve student information by student_id.
        
        Args:
            student_id: The unique identifier of the student.
            
        Returns:
            Dict[str, Any]: Student information including name, year level, program,
                and enrollment status, or an error dict if not found.
        """
        if student_id not in self.students:
            return {"error": f"Student with ID '{student_id}' not found"}
        return deepcopy(self.students[student_id])

    def get_course_by_id(self, course_id: str) -> Dict[str, Any]:
        """
        Retrieve course details by course_id.
        
        Args:
            course_id: The unique identifier of the course.
            
        Returns:
            Dict[str, Any]: Course details including name, department, credits,
                and max_capacity, or an error dict if not found.
        """
        if course_id not in self.courses:
            return {"error": f"Course with ID '{course_id}' not found"}
        return deepcopy(self.courses[course_id])

    def get_course_by_name(self, course_name: str) -> Dict[str, Any]:
        """
        Search for a course by course name.
        
        Args:
            course_name: The name of the course to search for.
            
        Returns:
            Dict[str, Any]: Matching course_id and details, or an error dict if not found.
        """
        for course_id, course in self.courses.items():
            if course["course_name"].lower() == course_name.lower():
                return deepcopy(course)
        return {"error": f"Course with name '{course_name}' not found"}

    def check_student_exists(self, student_id: str) -> Dict[str, Any]:
        """
        Check whether a student with the given student_id is registered.
        
        Args:
            student_id: The unique identifier of the student.
            
        Returns:
            Dict[str, Any]: Dictionary with 'exists' boolean indicating registration status.
        """
        return {"exists": student_id in self.students, "student_id": student_id}

    def check_course_exists(self, course_id: str) -> Dict[str, Any]:
        """
        Check whether a course with the given course_id exists.
        
        Args:
            course_id: The unique identifier of the course.
            
        Returns:
            Dict[str, Any]: Dictionary with 'exists' boolean indicating course existence.
        """
        return {"exists": course_id in self.courses, "course_id": course_id}

    def list_student_enrollments(self, student_id: str) -> Dict[str, Any]:
        """
        Retrieve all enrollment records for a specific student.
        
        Args:
            student_id: The unique identifier of the student.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of enrollment records (active or dropped),
                or an error dict if student not found.
        """
        if student_id not in self.students:
            return {"error": f"Student with ID '{student_id}' not found"}
        
        student_enrollments = []
        for enrollment in self.enrollments.values():
            if enrollment["student_id"] == student_id:
                student_enrollments.append(deepcopy(enrollment))
        
        return {"student_id": student_id, "enrollments": student_enrollments}

    def get_active_enrollments_for_course(self, course_id: str) -> Dict[str, Any]:
        """
        Count and list all active enrollments for a course.
        
        Args:
            course_id: The unique identifier of the course.
            
        Returns:
            Dict[str, Any]: Dictionary with count and list of active enrollments,
                or an error dict if course not found.
        """
        if course_id not in self.courses:
            return {"error": f"Course with ID '{course_id}' not found"}
        
        active_enrollments = []
        for enrollment in self.enrollments.values():
            if enrollment["course_id"] == course_id and enrollment["status"] == "active":
                active_enrollments.append(deepcopy(enrollment))
        
        return {
            "course_id": course_id,
            "active_count": len(active_enrollments),
            "enrollments": active_enrollments
        }

    def check_student_enrolled_in_course(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Determine if a student has an active enrollment in a specific course.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier of the course.
            
        Returns:
            Dict[str, Any]: Dictionary with 'enrolled' boolean and enrollment details if found.
        """
        for enrollment in self.enrollments.values():
            if (enrollment["student_id"] == student_id and 
                enrollment["course_id"] == course_id and 
                enrollment["status"] == "active"):
                return {
                    "enrolled": True,
                    "student_id": student_id,
                    "course_id": course_id,
                    "enrollment_id": enrollment["enrollment_id"]
                }
        return {"enrolled": False, "student_id": student_id, "course_id": course_id}

    def get_course_capacity_status(self, course_id: str) -> Dict[str, Any]:
        """
        Return current number of active enrollments and max capacity for a course.
        
        Args:
            course_id: The unique identifier of the course.
            
        Returns:
            Dict[str, Any]: Dictionary with current enrollment count, max capacity,
                and available spots, or an error dict if course not found.
        """
        if course_id not in self.courses:
            return {"error": f"Course with ID '{course_id}' not found"}
        
        active_count = sum(
            1 for e in self.enrollments.values()
            if e["course_id"] == course_id and e["status"] == "active"
        )
        max_capacity = self.courses[course_id]["max_capacity"]
        
        return {
            "course_id": course_id,
            "current_enrollment": active_count,
            "max_capacity": max_capacity,
            "available_spots": max_capacity - active_count
        }

    def validate_enrollment_date_within_period(self, course_id: str, enrollment_date: str) -> Dict[str, Any]:
        """
        Check whether a given enrollment date falls within the valid registration window.
        
        Args:
            course_id: The unique identifier of the course.
            enrollment_date: The date to validate (YYYY-MM-DD format).
            
        Returns:
            Dict[str, Any]: Dictionary with 'valid' boolean and period details,
                or an error dict if course not found or date format invalid.
        """
        if course_id not in self.courses:
            return {"error": f"Course with ID '{course_id}' not found"}
        
        course = self.courses[course_id]
        reg_start = course.get("registration_start", "")
        reg_end = course.get("registration_end", "")
        
        if not reg_start or not reg_end:
            return {"error": "Registration period not defined for this course"}
        
        try:
            date_obj = datetime.strptime(enrollment_date, "%Y-%m-%d")
            start_obj = datetime.strptime(reg_start, "%Y-%m-%d")
            end_obj = datetime.strptime(reg_end, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        is_valid = start_obj <= date_obj <= end_obj
        
        return {
            "valid": is_valid,
            "course_id": course_id,
            "enrollment_date": enrollment_date,
            "registration_start": reg_start,
            "registration_end": reg_end
        }

    # ==================== State Change Operations ====================

    def enroll_student_in_course(
        self, 
        student_id: str, 
        course_id: str, 
        enrollment_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new enrollment record for a student in a course.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier of the course.
            enrollment_date: The enrollment date (YYYY-MM-DD). Defaults to current date.
            
        Returns:
            Dict[str, Any]: Created enrollment record on success, or error dict on failure.
        """
        # Constraint: student must exist
        if student_id not in self.students:
            return {"error": f"Student with ID '{student_id}' does not exist"}
        
        # Constraint: course must exist
        if course_id not in self.courses:
            return {"error": f"Course with ID '{course_id}' does not exist"}
        
        # Constraint: no duplicate active enrollment
        for enrollment in self.enrollments.values():
            if (enrollment["student_id"] == student_id and 
                enrollment["course_id"] == course_id and 
                enrollment["status"] == "active"):
                return {"error": f"Student '{student_id}' already has an active enrollment in course '{course_id}'"}
        
        # Set enrollment date
        if enrollment_date is None:
            enrollment_date = self._timestamp()
        
        # Constraint: enrollment date within registration period
        date_validation = self.validate_enrollment_date_within_period(course_id, enrollment_date)
        if "error" in date_validation:
            return date_validation
        if not date_validation["valid"]:
            return {"error": f"Enrollment date '{enrollment_date}' is outside the registration period"}
        
        # Constraint: capacity check
        capacity_status = self.get_course_capacity_status(course_id)
        if capacity_status["available_spots"] <= 0:
            return {"error": f"Course '{course_id}' has reached maximum capacity"}
        
        # Create enrollment
        enrollment_id = f"ENR{self.enrollment_counter:03d}"
        self.enrollment_counter += 1
        
        new_enrollment = {
            "enrollment_id": enrollment_id,
            "student_id": student_id,
            "course_id": course_id,
            "enrollment_date": enrollment_date,
            "status": "active"
        }
        
        self.enrollments[enrollment_id] = new_enrollment
        
        return {"success": True, "enrollment": deepcopy(new_enrollment)}

    def drop_student_from_course(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Update the enrollment status of a student in a course from active to dropped.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier of the course.
            
        Returns:
            Dict[str, Any]: Updated enrollment record on success, or error dict on failure.
        """
        for enrollment_id, enrollment in self.enrollments.items():
            if (enrollment["student_id"] == student_id and 
                enrollment["course_id"] == course_id and 
                enrollment["status"] == "active"):
                self.enrollments[enrollment_id]["status"] = "dropped"
                return {"success": True, "enrollment": deepcopy(self.enrollments[enrollment_id])}
        
        return {"error": f"No active enrollment found for student '{student_id}' in course '{course_id}'"}

    def bulk_enroll_students(
        self, 
        student_ids: List[str], 
        course_id: str, 
        enrollment_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enroll multiple students into a course at once.
        
        Args:
            student_ids: List of student identifiers to enroll.
            course_id: The unique identifier of the course.
            enrollment_date: The enrollment date (YYYY-MM-DD). Defaults to current date.
            
        Returns:
            Dict[str, Any]: Summary of successful and failed enrollments.
        """
        if not student_ids:
            return {"error": "No student IDs provided"}
        
        if course_id not in self.courses:
            return {"error": f"Course with ID '{course_id}' does not exist"}
        
        if enrollment_date is None:
            enrollment_date = self._timestamp()
        
        successful = []
        failed = []
        
        for student_id in student_ids:
            result = self.enroll_student_in_course(student_id, course_id, enrollment_date)
            if "error" in result:
                failed.append({"student_id": student_id, "error": result["error"]})
            else:
                successful.append(result["enrollment"])
        
        return {
            "success": True,
            "course_id": course_id,
            "successful_enrollments": successful,
            "failed_enrollments": failed,
            "total_successful": len(successful),
            "total_failed": len(failed)
        }

    def modify_enrollment_date(
        self, 
        student_id: str, 
        course_id: str, 
        new_enrollment_date: str
    ) -> Dict[str, Any]:
        """
        Update the enrollment date of a student in a course.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier of the course.
            new_enrollment_date: The new enrollment date (YYYY-MM-DD).
            
        Returns:
            Dict[str, Any]: Updated enrollment record on success, or error dict on failure.
        """
        # Validate new date format
        try:
            datetime.strptime(new_enrollment_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Constraint: new date must be within registration period
        date_validation = self.validate_enrollment_date_within_period(course_id, new_enrollment_date)
        if "error" in date_validation:
            return date_validation
        if not date_validation["valid"]:
            return {"error": f"New enrollment date '{new_enrollment_date}' is outside the registration period"}
        
        # Find active enrollment
        for enrollment_id, enrollment in self.enrollments.items():
            if (enrollment["student_id"] == student_id and 
                enrollment["course_id"] == course_id and 
                enrollment["status"] == "active"):
                self.enrollments[enrollment_id]["enrollment_date"] = new_enrollment_date
                return {"success": True, "enrollment": deepcopy(self.enrollments[enrollment_id])}
        
        return {"error": f"No active enrollment found for student '{student_id}' in course '{course_id}'"}

    def reinstate_dropped_enrollment(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """
        Change a dropped enrollment back to active.
        
        Args:
            student_id: The unique identifier of the student.
            course_id: The unique identifier of the course.
            
        Returns:
            Dict[str, Any]: Updated enrollment record on success, or error dict on failure.
        """
        # Constraint: course must exist
        if course_id not in self.courses:
            return {"error": f"Course with ID '{course_id}' does not exist"}
        
        # Check for existing active enrollment
        for enrollment in self.enrollments.values():
            if (enrollment["student_id"] == student_id and 
                enrollment["course_id"] == course_id and 
                enrollment["status"] == "active"):
                return {"error": f"Student '{student_id}' already has an active enrollment in course '{course_id}'"}
        
        # Constraint: capacity check
        capacity_status = self.get_course_capacity_status(course_id)
        if capacity_status["available_spots"] <= 0:
            return {"error": f"Course '{course_id}' has reached maximum capacity"}
        
        # Find dropped enrollment
        for enrollment_id, enrollment in self.enrollments.items():
            if (enrollment["student_id"] == student_id and 
                enrollment["course_id"] == course_id and 
                enrollment["status"] == "dropped"):
                
                # Check if enrollment date is still valid
                date_validation = self.validate_enrollment_date_within_period(
                    course_id, 
                    enrollment["enrollment_date"]
                )
                if "error" not in date_validation and not date_validation["valid"]:
                    # Update to current date if original is invalid
                    new_date = self._timestamp()
                    current_validation = self.validate_enrollment_date_within_period(course_id, new_date)
                    if "error" in current_validation or not current_validation["valid"]:
                        return {"error": "Cannot reinstate enrollment outside registration period"}
                    self.enrollments[enrollment_id]["enrollment_date"] = new_date
                
                self.enrollments[enrollment_id]["status"] = "active"
                return {"success": True, "enrollment": deepcopy(self.enrollments[enrollment_id])}
        
        return {"error": f"No dropped enrollment found for student '{student_id}' in course '{course_id}'"}

    def add_student(
        self,
        student_id: str,
        name: str,
        year_level: int,
        program: str,
        enrollment_status: str = "active"
    ) -> Dict[str, Any]:
        """
        Register a new student into the system.
        
        Args:
            student_id: Unique identifier for the new student.
            name: Full name of the student.
            year_level: Academic year level (1-10).
            program: Academic program/major.
            enrollment_status: Status of the student (active/inactive).
            
        Returns:
            Dict[str, Any]: Created student record on success, or error dict on failure.
        """
        if student_id in self.students:
            return {"error": f"Student with ID '{student_id}' already exists"}
        
        if not name or not name.strip():
            return {"error": "Student name cannot be empty"}
        
        if not isinstance(year_level, int) or year_level < 1 or year_level > 10:
            return {"error": "Year level must be an integer between 1 and 10"}
        
        if not program or not program.strip():
            return {"error": "Program cannot be empty"}
        
        if enrollment_status not in ["active", "inactive"]:
            return {"error": "Enrollment status must be 'active' or 'inactive'"}
        
        new_student = {
            "student_id": student_id,
            "name": name.strip(),
            "year_level": year_level,
            "program": program.strip(),
            "enrollment_status": enrollment_status
        }
        
        self.students[student_id] = new_student
        
        return {"success": True, "student": deepcopy(new_student)}

    def add_course(
        self,
        course_id: str,
        course_name: str,
        department: str,
        credits: int,
        max_capacity: int,
        registration_start: Optional[str] = None,
        registration_end: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new course offering to the system.
        
        Args:
            course_id: Unique identifier for the new course.
            course_name: Name of the course.
            department: Department offering the course.
            credits: Number of credit hours.
            max_capacity: Maximum number of students allowed.
            registration_start: Start date of registration period (YYYY-MM-DD).
            registration_end: End date of registration period (YYYY-MM-DD).
            
        Returns:
            Dict[str, Any]: Created course record on success, or error dict on failure.
        """
        if course_id in self.courses:
            return {"error": f"Course with ID '{course_id}' already exists"}
        
        if not course_name or not course_name.strip():
            return {"error": "Course name cannot be empty"}
        
        if not department or not department.strip():
            return {"error": "Department cannot be empty"}
        
        if not isinstance(credits, int) or credits < 1 or credits > 12:
            return {"error": "Credits must be an integer between 1 and 12"}
        
        if not isinstance(max_capacity, int) or max_capacity < 1:
            return {"error": "Max capacity must be a positive integer"}
        
        # Validate dates if provided
        if registration_start:
            try:
                datetime.strptime(registration_start, "%Y-%m-%d")
            except ValueError:
                return {"error": "Invalid registration_start date format. Use YYYY-MM-DD"}
        
        if registration_end:
            try:
                datetime.strptime(registration_end, "%Y-%m-%d")
            except ValueError:
                return {"error": "Invalid registration_end date format. Use YYYY-MM-DD"}
        
        if registration_start and registration_end:
            if registration_start > registration_end:
                return {"error": "Registration start date must be before end date"}
        
        new_course = {
            "course_id": course_id,
            "course_name": course_name.strip(),
            "department": department.strip(),
            "credits": credits,
            "max_capacity": max_capacity,
            "registration_start": registration_start or "",
            "registration_end": registration_end or ""
        }
        
        self.courses[course_id] = new_course
        
        return {"success": True, "course": deepcopy(new_course)}


__TEST_CASES__ = [
    {
        "name": "Complete enrollment workflow",
        "steps": [
            {"tool_call": "check_student_exists(student_id='STU001')", "expect_success": True},
            {"tool_call": "check_course_exists(course_id='CRS101')", "expect_success": True},
            {"tool_call": "get_course_capacity_status(course_id='CRS101')", "expect_success": True},
            {"tool_call": "list_student_enrollments(student_id='STU001')", "expect_success": True}
        ]
    },
    {
        "name": "Add new student and enroll in course",
        "steps": [
            {"tool_call": "add_student(student_id='STU005', name='Emily Davis', year_level=2, program='Biology')", "expect_success": True},
            {"tool_call": "get_student_by_id(student_id='STU005')", "expect_success": True},
            {"tool_call": "enroll_student_in_course(student_id='STU005', course_id='CRS101', enrollment_date='2024-01-20')", "expect_success": True},
            {"tool_call": "check_student_enrolled_in_course(student_id='STU005', course_id='CRS101')", "expect_success": True}
        ]
    },
    {
        "name": "Drop and reinstate enrollment",
        "steps": [
            {"tool_call": "check_student_enrolled_in_course(student_id='STU001', course_id='CRS101')", "expect_success": True},
            {"tool_call": "drop_student_from_course(student_id='STU001', course_id='CRS101')", "expect_success": True},
            {"tool_call": "reinstate_dropped_enrollment(student_id='STU001', course_id='CRS101')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - duplicate enrollment attempt",
        "steps": [
            {"tool_call": "check_student_enrolled_in_course(student_id='STU001', course_id='CRS101')", "expect_success": True},
            {"tool_call": "enroll_student_in_course(student_id='STU001', course_id='CRS101', enrollment_date='2024-01-20')", "expect_success": False}
        ]
    },
    {
        "name": "Error handling - non-existent resources",
        "steps": [
            {"tool_call": "get_student_by_id(student_id='INVALID_ID')", "expect_success": False},
            {"tool_call": "get_course_by_id(course_id='INVALID_COURSE')", "expect_success": False},
            {"tool_call": "enroll_student_in_course(student_id='INVALID_ID', course_id='CRS101', enrollment_date='2024-01-20')", "expect_success": False}
        ]
    }
]