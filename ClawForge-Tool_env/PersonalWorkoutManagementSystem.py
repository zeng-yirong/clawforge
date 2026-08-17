"""
Personal Workout Management System Environment API

A personal workout management system that helps users organize, track, and modify
their exercise routines with stateful records of workouts, schedules, and metrics.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE: Dict[str, Any] = {
    "workouts": {
        "w001": {
            "workout_id": "w001",
            "name": "Morning Cardio",
            "type": "cardio",
            "duration_minutes": 30,
            "intensity_level": "moderate",
            "calories_burned": 250
        },
        "w002": {
            "workout_id": "w002",
            "name": "Upper Body Strength",
            "type": "strength",
            "duration_minutes": 45,
            "intensity_level": "high",
            "calories_burned": 300
        },
        "w003": {
            "workout_id": "w003",
            "name": "Yoga Flow",
            "type": "flexibility",
            "duration_minutes": 60,
            "intensity_level": "low",
            "calories_burned": 150
        },
        "w004": {
            "workout_id": "w004",
            "name": "HIIT Session",
            "type": "cardio",
            "duration_minutes": 25,
            "intensity_level": "high",
            "calories_burned": 350
        }
    },
    "routines": {
        "r001": {
            "routine_id": "r001",
            "user_id": "u001",
            "name": "Weekly Fitness Plan",
            "workout_list": ["w001", "w002", "w003"],
            "creation_date": "2024-01-15T08:00:00",
            "is_active": True
        },
        "r002": {
            "routine_id": "r002",
            "user_id": "u001",
            "name": "Cardio Focus",
            "workout_list": ["w001", "w004"],
            "creation_date": "2024-01-10T09:00:00",
            "is_active": False
        },
        "r003": {
            "routine_id": "r003",
            "user_id": "u002",
            "name": "Beginner Routine",
            "workout_list": ["w003"],
            "creation_date": "2024-01-20T10:00:00",
            "is_active": True
        }
    },
    "scheduled_workouts": {
        "s001": {
            "schedule_id": "s001",
            "routine_id": "r001",
            "workout_id": "w001",
            "date": "2024-02-01",
            "time": "07:00",
            "status": "completed"
        },
        "s002": {
            "schedule_id": "s002",
            "routine_id": "r001",
            "workout_id": "w002",
            "date": "2024-02-02",
            "time": "18:00",
            "status": "pending"
        },
        "s003": {
            "schedule_id": "s003",
            "routine_id": "r001",
            "workout_id": "w003",
            "date": "2024-02-03",
            "time": "09:00",
            "status": "skipped"
        }
    },
    "users": {
        "u001": {
            "user_id": "u001",
            "fitness_level": "intermediate",
            "goals": ["weight loss", "endurance"],
            "preferred_workout_types": ["cardio", "strength"],
            "daily_step_goal": 10000
        },
        "u002": {
            "user_id": "u002",
            "fitness_level": "beginner",
            "goals": ["flexibility", "stress relief"],
            "preferred_workout_types": ["flexibility", "cardio"],
            "daily_step_goal": 7000
        },
        "u003": {
            "user_id": "u003",
            "fitness_level": "advanced",
            "goals": ["muscle gain", "strength"],
            "preferred_workout_types": ["strength"],
            "daily_step_goal": 12000
        }
    },
    "current_user": "u001",
    "current_date": "2024-02-01",
    "next_workout_id": 5,
    "next_routine_id": 4,
    "next_schedule_id": 4
}

VALID_INTENSITY_LEVELS = ["low", "moderate", "high"]
VALID_STATUSES = ["completed", "skipped", "pending"]


class PersonalWorkoutManagementSystem:
    """
    A personal workout management system environment API.
    
    This system helps users organize, track, and modify their exercise routines
    with stateful records of workouts, schedules, performance metrics, and user
    preferences.
    """

    def __init__(self) -> None:
        """
        Initialize the Personal Workout Management System.
        
        Declares all state attributes with type hints and sets the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self._api_description: str = "A personal workout management system for organizing, tracking, and modifying exercise routines."
        
        self.workouts: Dict[str, Dict[str, Any]] = {}
        self.routines: Dict[str, Dict[str, Any]] = {}
        self.scheduled_workouts: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.current_user: Optional[str] = None
        self.current_date: str = ""
        self.next_workout_id: int = 1
        self.next_routine_id: int = 1
        self.next_schedule_id: int = 1

    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format.
        """
        return datetime.now().isoformat()

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (unused currently).
            
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
        Get the current state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all current environment state
                variables including workouts, routines, scheduled_workouts, users,
                current_user, current_date, and ID counters.
        """
        return {
            "workouts": deepcopy(self.workouts),
            "routines": deepcopy(self.routines),
            "scheduled_workouts": deepcopy(self.scheduled_workouts),
            "users": deepcopy(self.users),
            "current_user": self.current_user,
            "current_date": self.current_date,
            "next_workout_id": self.next_workout_id,
            "next_routine_id": self.next_routine_id,
            "next_schedule_id": self.next_schedule_id
        }

    # ==================== QUERY OPERATIONS ====================

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user profile including fitness level, goals, and preferences.
        
        Args:
            user_id: The unique identifier of the user to retrieve.
            
        Returns:
            Dict[str, Any]: User profile data or error dictionary if not found.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found."}
        return {"user": deepcopy(self.users[user_id])}

    def list_user_routines(self, user_id: str) -> Dict[str, Any]:
        """
        List all routines associated with a user, regardless of active status.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: List of routines or error if user not found.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found."}
        
        user_routines = [
            deepcopy(routine) for routine in self.routines.values()
            if routine["user_id"] == user_id
        ]
        return {"routines": user_routines}

    def get_active_routine(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve the currently active routine for a user.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: Active routine data or None if none exists.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found."}
        
        for routine in self.routines.values():
            if routine["user_id"] == user_id and routine["is_active"]:
                return {"routine": deepcopy(routine)}
        
        return {"routine": None}

    def get_workout_by_id(self, workout_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific workout.
        
        Args:
            workout_id: The unique identifier of the workout.
            
        Returns:
            Dict[str, Any]: Workout data or error if not found.
        """
        if workout_id not in self.workouts:
            return {"error": f"Workout with id '{workout_id}' not found."}
        return {"workout": deepcopy(self.workouts[workout_id])}

    def workout_exists(self, workout_id: str) -> Dict[str, Any]:
        """
        Check whether a workout with the given workout_id exists in the system.
        
        Args:
            workout_id: The unique identifier of the workout to check.
            
        Returns:
            Dict[str, Any]: Dictionary with 'exists' boolean.
        """
        return {"exists": workout_id in self.workouts}

    def is_workout_in_routine(self, workout_id: str, routine_id: str) -> Dict[str, Any]:
        """
        Determine if a specific workout is already part of a given routine.
        
        Args:
            workout_id: The unique identifier of the workout.
            routine_id: The unique identifier of the routine.
            
        Returns:
            Dict[str, Any]: Dictionary with 'in_routine' boolean or error.
        """
        if routine_id not in self.routines:
            return {"error": f"Routine with id '{routine_id}' not found."}
        
        routine = self.routines[routine_id]
        return {"in_routine": workout_id in routine["workout_list"]}

    def get_routine_workouts(self, routine_id: str) -> Dict[str, Any]:
        """
        Retrieve the full list of workouts (as objects) in a given routine.
        
        Args:
            routine_id: The unique identifier of the routine.
            
        Returns:
            Dict[str, Any]: List of workout objects or error if routine not found.
        """
        if routine_id not in self.routines:
            return {"error": f"Routine with id '{routine_id}' not found."}
        
        routine = self.routines[routine_id]
        workouts = []
        for wid in routine["workout_list"]:
            if wid in self.workouts:
                workouts.append(deepcopy(self.workouts[wid]))
        
        return {"workouts": workouts}

    def get_scheduled_workouts_by_date(self, date: str) -> Dict[str, Any]:
        """
        Retrieve all scheduled workouts for a specific date.
        
        Args:
            date: The date string (YYYY-MM-DD format) to query.
            
        Returns:
            Dict[str, Any]: List of scheduled workouts for the date.
        """
        scheduled = [
            deepcopy(sw) for sw in self.scheduled_workouts.values()
            if sw["date"] == date
        ]
        return {"scheduled_workouts": scheduled}

    def get_workout_history(
        self, user_id: str, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """
        Retrieve all completed or logged workouts for a user within a date range.
        
        Args:
            user_id: The unique identifier of the user.
            start_date: Start of date range (YYYY-MM-DD).
            end_date: End of date range (YYYY-MM-DD).
            
        Returns:
            Dict[str, Any]: List of completed workouts in the date range.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found."}
        
        user_routines = {
            rid for rid, r in self.routines.items() if r["user_id"] == user_id
        }
        
        history = []
        for sw in self.scheduled_workouts.values():
            if sw["routine_id"] not in user_routines:
                continue
            if sw["status"] != "completed":
                continue
            if start_date <= sw["date"] <= end_date:
                history.append(deepcopy(sw))
        
        return {"workout_history": history}

    def validate_intensity_level(self, intensity_level: str) -> Dict[str, Any]:
        """
        Check if the provided intensity level is valid.
        
        Args:
            intensity_level: The intensity level string to validate.
            
        Returns:
            Dict[str, Any]: Dictionary with 'valid' boolean.
        """
        return {"valid": intensity_level in VALID_INTENSITY_LEVELS}

    # ==================== STATE CHANGE OPERATIONS ====================

    def create_new_workout(
        self,
        name: str,
        workout_type: str,
        duration_minutes: int,
        intensity_level: str,
        calories_burned: int
    ) -> Dict[str, Any]:
        """
        Add a new workout to the system with specified attributes.
        
        Args:
            name: Name of the workout.
            workout_type: Type of workout (e.g., cardio, strength).
            duration_minutes: Duration in minutes.
            intensity_level: Must be 'low', 'moderate', or 'high'.
            calories_burned: Estimated calories burned.
            
        Returns:
            Dict[str, Any]: Created workout data or error.
        """
        if intensity_level not in VALID_INTENSITY_LEVELS:
            return {
                "error": f"Invalid intensity level '{intensity_level}'. Must be one of: {VALID_INTENSITY_LEVELS}"
            }
        
        if duration_minutes <= 0:
            return {"error": "Duration must be a positive number."}
        
        if calories_burned < 0:
            return {"error": "Calories burned cannot be negative."}
        
        workout_id = f"w{self.next_workout_id:03d}"
        self.next_workout_id += 1
        
        new_workout = {
            "workout_id": workout_id,
            "name": name,
            "type": workout_type,
            "duration_minutes": duration_minutes,
            "intensity_level": intensity_level,
            "calories_burned": calories_burned
        }
        
        self.workouts[workout_id] = new_workout
        return {"success": True, "workout": deepcopy(new_workout)}

    def add_workout_to_routine(
        self, workout_id: str, routine_id: str, confirm_duplicate: bool = False
    ) -> Dict[str, Any]:
        """
        Add an existing workout to a routine's workout_list.
        
        Args:
            workout_id: The workout to add.
            routine_id: The routine to add the workout to.
            confirm_duplicate: If True, allows adding duplicate workouts.
            
        Returns:
            Dict[str, Any]: Success status or error.
        """
        if workout_id not in self.workouts:
            return {"error": f"Workout with id '{workout_id}' not found. Workout must be defined before adding to routine."}
        
        if routine_id not in self.routines:
            return {"error": f"Routine with id '{routine_id}' not found."}
        
        routine = self.routines[routine_id]
        
        if workout_id in routine["workout_list"] and not confirm_duplicate:
            return {
                "error": f"Workout '{workout_id}' already exists in routine '{routine_id}'. Set confirm_duplicate=True to add anyway."
            }
        
        routine["workout_list"].append(workout_id)
        return {"success": True, "routine": deepcopy(routine)}

    def remove_workout_from_routine(
        self, workout_id: str, routine_id: str
    ) -> Dict[str, Any]:
        """
        Remove a specific workout from a routine's workout_list.
        
        Args:
            workout_id: The workout to remove.
            routine_id: The routine to remove the workout from.
            
        Returns:
            Dict[str, Any]: Success status or error.
        """
        if routine_id not in self.routines:
            return {"error": f"Routine with id '{routine_id}' not found."}
        
        routine = self.routines[routine_id]
        
        if workout_id not in routine["workout_list"]:
            return {"error": f"Workout '{workout_id}' is not in routine '{routine_id}'."}
        
        routine["workout_list"].remove(workout_id)
        return {"success": True, "routine": deepcopy(routine)}

    def create_new_routine(
        self, user_id: str, name: str, workout_list: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new routine for a user and set it as active.
        
        Args:
            user_id: The user to create the routine for.
            name: Name of the routine.
            workout_list: Optional list of workout IDs to include.
            
        Returns:
            Dict[str, Any]: Created routine data or error.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found."}
        
        if workout_list is None:
            workout_list = []
        
        for wid in workout_list:
            if wid not in self.workouts:
                return {"error": f"Workout '{wid}' does not exist. All workouts must be defined before adding to routine."}
        
        for routine in self.routines.values():
            if routine["user_id"] == user_id and routine["is_active"]:
                routine["is_active"] = False
        
        routine_id = f"r{self.next_routine_id:03d}"
        self.next_routine_id += 1
        
        new_routine = {
            "routine_id": routine_id,
            "user_id": user_id,
            "name": name,
            "workout_list": workout_list.copy(),
            "creation_date": self._timestamp(),
            "is_active": True
        }
        
        self.routines[routine_id] = new_routine
        return {"success": True, "routine": deepcopy(new_routine)}

    def activate_routine(self, routine_id: str) -> Dict[str, Any]:
        """
        Set a specific routine as active for its user.
        
        Args:
            routine_id: The routine to activate.
            
        Returns:
            Dict[str, Any]: Success status or error.
        """
        if routine_id not in self.routines:
            return {"error": f"Routine with id '{routine_id}' not found."}
        
        target_routine = self.routines[routine_id]
        user_id = target_routine["user_id"]
        
        for routine in self.routines.values():
            if routine["user_id"] == user_id and routine["is_active"]:
                routine["is_active"] = False
        
        target_routine["is_active"] = True
        return {"success": True, "routine": deepcopy(target_routine)}

    def deactivate_routine(self, routine_id: str) -> Dict[str, Any]:
        """
        Mark a routine as inactive.
        
        Args:
            routine_id: The routine to deactivate.
            
        Returns:
            Dict[str, Any]: Success status or error.
        """
        if routine_id not in self.routines:
            return {"error": f"Routine with id '{routine_id}' not found."}
        
        self.routines[routine_id]["is_active"] = False
        return {"success": True, "routine": deepcopy(self.routines[routine_id])}

    def schedule_workout(
        self,
        routine_id: str,
        workout_id: str,
        date: str,
        time: str,
        manual_log: bool = False
    ) -> Dict[str, Any]:
        """
        Schedule a workout on a specific date and time.
        
        Args:
            routine_id: The routine this schedule belongs to.
            workout_id: The workout to schedule.
            date: Date string (YYYY-MM-DD format).
            time: Time string (HH:MM format).
            manual_log: If True, allows scheduling in the past.
            
        Returns:
            Dict[str, Any]: Created schedule data or error.
        """
        if routine_id not in self.routines:
            return {"error": f"Routine with id '{routine_id}' not found."}
        
        if workout_id not in self.workouts:
            return {"error": f"Workout with id '{workout_id}' not found."}
        
        if date < self.current_date and not manual_log:
            return {
                "error": f"Cannot schedule workout in the past (date: {date}, current: {self.current_date}). Use manual_log=True for logging past workouts."
            }
        
        schedule_id = f"s{self.next_schedule_id:03d}"
        self.next_schedule_id += 1
        
        status = "completed" if manual_log and date < self.current_date else "pending"
        
        new_schedule = {
            "schedule_id": schedule_id,
            "routine_id": routine_id,
            "workout_id": workout_id,
            "date": date,
            "time": time,
            "status": status
        }
        
        self.scheduled_workouts[schedule_id] = new_schedule
        return {"success": True, "scheduled_workout": deepcopy(new_schedule)}

    def update_scheduled_workout_status(
        self, schedule_id: str, status: str
    ) -> Dict[str, Any]:
        """
        Update the status of a scheduled workout.
        
        Args:
            schedule_id: The scheduled workout to update.
            status: New status ('completed', 'skipped', or 'pending').
            
        Returns:
            Dict[str, Any]: Updated schedule data or error.
        """
        if schedule_id not in self.scheduled_workouts:
            return {"error": f"Scheduled workout with id '{schedule_id}' not found."}
        
        if status not in VALID_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}"}
        
        self.scheduled_workouts[schedule_id]["status"] = status
        return {"success": True, "scheduled_workout": deepcopy(self.scheduled_workouts[schedule_id])}

    def update_workout_intensity(
        self, workout_id: str, intensity_level: str
    ) -> Dict[str, Any]:
        """
        Modify the intensity level of an existing workout.
        
        Args:
            workout_id: The workout to update.
            intensity_level: New intensity ('low', 'moderate', or 'high').
            
        Returns:
            Dict[str, Any]: Updated workout data or error.
        """
        if workout_id not in self.workouts:
            return {"error": f"Workout with id '{workout_id}' not found."}
        
        if intensity_level not in VALID_INTENSITY_LEVELS:
            return {
                "error": f"Invalid intensity level '{intensity_level}'. Must be one of: {VALID_INTENSITY_LEVELS}"
            }
        
        self.workouts[workout_id]["intensity_level"] = intensity_level
        return {"success": True, "workout": deepcopy(self.workouts[workout_id])}

    def modify_routine_workout_order(
        self, routine_id: str, new_order: List[str]
    ) -> Dict[str, Any]:
        """
        Reorder the sequence of workouts within a routine's workout_list.
        
        Args:
            routine_id: The routine to modify.
            new_order: List of workout IDs in the desired order.
            
        Returns:
            Dict[str, Any]: Updated routine data or error.
        """
        if routine_id not in self.routines:
            return {"error": f"Routine with id '{routine_id}' not found."}
        
        routine = self.routines[routine_id]
        current_set = set(routine["workout_list"])
        new_set = set(new_order)
        
        if current_set != new_set:
            return {
                "error": "New order must contain exactly the same workouts as the current routine."
            }
        
        routine["workout_list"] = new_order.copy()
        return {"success": True, "routine": deepcopy(routine)}


__TEST_CASES__ = [
    {
        "name": "Create and add workout to routine",
        "steps": [
            {"tool_call": "create_new_workout(name='Evening Run', workout_type='cardio', duration_minutes=40, intensity_level='moderate', calories_burned=280)", "expect_success": True},
            {"tool_call": "get_active_routine(user_id='u001')", "expect_success": True},
            {"tool_call": "add_workout_to_routine(workout_id='w005', routine_id='r001')", "expect_success": True},
            {"tool_call": "get_routine_workouts(routine_id='r001')", "expect_success": True}
        ]
    },
    {
        "name": "Schedule workout and update status",
        "steps": [
            {"tool_call": "schedule_workout(routine_id='r001', workout_id='w001', date='2024-02-05', time='06:30')", "expect_success": True},
            {"tool_call": "get_scheduled_workouts_by_date(date='2024-02-05')", "expect_success": True},
            {"tool_call": "update_scheduled_workout_status(schedule_id='s004', status='completed')", "expect_success": True}
        ]
    },
    {
        "name": "Create routine and activate it",
        "steps": [
            {"tool_call": "get_active_routine(user_id='u001')", "expect_success": True},
            {"tool_call": "create_new_routine(user_id='u001', name='Strength Focus', workout_list=['w002', 'w004'])", "expect_success": True},
            {"tool_call": "get_active_routine(user_id='u001')", "expect_success": True},
            {"tool_call": "activate_routine(routine_id='r001')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - invalid operations",
        "steps": [
            {"tool_call": "get_user_by_id(user_id='invalid_user')", "expect_success": False},
            {"tool_call": "create_new_workout(name='Bad Workout', workout_type='cardio', duration_minutes=30, intensity_level='extreme', calories_burned=200)", "expect_success": False},
            {"tool_call": "add_workout_to_routine(workout_id='nonexistent', routine_id='r001')", "expect_success": False},
            {"tool_call": "schedule_workout(routine_id='r001', workout_id='w001', date='2023-01-01', time='08:00')", "expect_success": False}
        ]
    },
    {
        "name": "Workout history and routine management",
        "steps": [
            {"tool_call": "get_workout_history(user_id='u001', start_date='2024-01-01', end_date='2024-02-28')", "expect_success": True},
            {"tool_call": "remove_workout_from_routine(workout_id='w003', routine_id='r001')", "expect_success": True},
            {"tool_call": "modify_routine_workout_order(routine_id='r001', new_order=['w002', 'w001'])", "expect_success": True},
            {"tool_call": "update_workout_intensity(workout_id='w001', intensity_level='high')", "expect_success": True}
        ]
    }
]