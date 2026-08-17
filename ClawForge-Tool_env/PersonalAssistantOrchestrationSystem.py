from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import random

DEFAULT_STATE = {
    "personalities": {},
    "assistants": {},
    "schedules": {},
    "time_slots": [],
    "personality_counter": 1,
    "assistant_counter": 1,
    "schedule_counter": 1,
    "execution_log": [],
}

VALID_PERSONALITY_TRAITS = ("gentle", "strict", "humorous", "grumpy", "energetic", "calm", "sarcastic")
VALID_SCHEDULE_STATUSES = ("draft", "active", "completed", "cancelled", "conflict")
VALID_TIME_SLOTS = ["morning", "afternoon", "evening", "night"]
VALID_CONFLICT_RESOLUTIONS = ("reschedule", "override", "skip", "notify")


class PersonalAssistantOrchestrationEnv:
    """
    A unified orchestration environment for personal assistant configuration.
    
    This environment enables users to define assistant personalities with specific traits,
    configure multiple assistants, and orchestrate their schedules across time slots.
    The system supports personality-based schedule assignment, conflict resolution,
    and dynamic personality trait adjustments.

    Attributes:
        personalities (Dict[str, Dict]): Defined personality templates with traits and behaviors.
        assistants (Dict[str, Dict]): Configured assistants with assigned personalities.
        schedules (Dict[str, Dict]): Scheduled tasks and appointments.
        time_slots (List[str]): Available time slots for scheduling.
        personality_counter (int): Auto-incrementing personality ID counter.
        assistant_counter (int): Auto-incrementing assistant ID counter.
        schedule_counter (int): Auto-incrementing schedule ID counter.
        execution_log (List[Dict]): History of orchestration operations.
    """

    def __init__(self):
        self.personalities: Dict[str, Dict[str, Any]]
        self.assistants: Dict[str, Dict[str, Any]]
        self.schedules: Dict[str, Dict[str, Any]]
        self.time_slots: List[str]
        self.personality_counter: int
        self.assistant_counter: int
        self.schedule_counter: int
        self.execution_log: List[Dict[str, Any]]
        self._api_description = (
            "This tool orchestrates personal assistant configuration: define personality "
            "templates, register assistants with specific traits, schedule tasks across "
            "time slots with conflict resolution, and adjust behaviors dynamically."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.personalities = scenario.get("personalities", DEFAULT_STATE_COPY["personalities"])
        self.assistants = scenario.get("assistants", DEFAULT_STATE_COPY["assistants"])
        self.schedules = scenario.get("schedules", DEFAULT_STATE_COPY["schedules"])
        self.time_slots = scenario.get("time_slots", DEFAULT_STATE_COPY["time_slots"])
        self.personality_counter = scenario.get("personality_counter", DEFAULT_STATE_COPY["personality_counter"])
        self.assistant_counter = scenario.get("assistant_counter", DEFAULT_STATE_COPY["assistant_counter"])
        self.schedule_counter = scenario.get("schedule_counter", DEFAULT_STATE_COPY["schedule_counter"])
        self.execution_log = scenario.get("execution_log", DEFAULT_STATE_COPY["execution_log"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including personalities,
                  assistants, schedules, time slots, counters, and execution log.
        """
        return {
            "personalities": self.personalities,
            "assistants": self.assistants,
            "schedules": self.schedules,
            "time_slots": self.time_slots,
            "personality_counter": self.personality_counter,
            "assistant_counter": self.assistant_counter,
            "schedule_counter": self.schedule_counter,
            "execution_log": self.execution_log,
        }

    # ── Personality Management ───────────────────────────────────────────

    def define_personality(
        self,
        name: str,
        primary_trait: str,
        secondary_traits: Optional[List[str]] = None,
        communication_style: str = "neutral",
        responsiveness: int = 5,
        flexibility: int = 5,
    ) -> Dict[str, Any]:
        """
        Define a new personality template for assistants.

        Args:
            name (str): Personality name (e.g., "gentle_secretary", "gruff_bro").
            primary_trait (str): Primary personality trait.
            secondary_traits (List[str]): [Optional] Additional traits.
            communication_style (str): Style of communication.
            responsiveness (int): 1-10 scale, higher = more responsive.
            flexibility (int): 1-10 scale, higher = more flexible.

        Returns:
            personality_id (str): Unique personality identifier.
            personality (Dict): The defined personality template.
        """
        if not name.strip():
            return {"error": "Personality name cannot be empty."}
        if primary_trait not in VALID_PERSONALITY_TRAITS:
            return {"error": f"Invalid primary trait '{primary_trait}'. Must be one of: {', '.join(VALID_PERSONALITY_TRAITS)}"}
        if not (1 <= responsiveness <= 10):
            return {"error": "Responsiveness must be between 1 and 10."}
        if not (1 <= flexibility <= 10):
            return {"error": "Flexibility must be between 1 and 10."}

        personality_id = f"P{self.personality_counter}"
        self.personality_counter += 1

        personality = {
            "personality_id": personality_id,
            "name": name,
            "primary_trait": primary_trait,
            "secondary_traits": secondary_traits or [],
            "communication_style": communication_style,
            "responsiveness": responsiveness,
            "flexibility": flexibility,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
        }
        self.personalities[personality_id] = personality
        self._log("personality_defined", {"personality_id": personality_id, "name": name, "primary_trait": primary_trait})
        return {"personality_id": personality_id, "personality": personality}

    def get_personality(self, personality_id: str) -> Dict[str, Any]:
        """
        Retrieve a personality template by ID.

        Args:
            personality_id (str): Personality ID.

        Returns:
            personality (Dict): Full personality object.
        """
        if personality_id not in self.personalities:
            return {"error": f"Personality '{personality_id}' not found."}
        return {"personality": self.personalities[personality_id]}

    def update_personality_trait(
        self,
        personality_id: str,
        trait_type: str,
        new_value: Union[str, int],
    ) -> Dict[str, Any]:
        """
        Update a specific trait or attribute of a personality.

        Args:
            personality_id (str): Personality ID.
            trait_type (str): Field to update ('primary_trait', 'responsiveness', etc.).
            new_value: New value for the trait.

        Returns:
            personality_id (str): Updated personality ID.
            updated_field (str): The field that was changed.
            new_value: The new value.
        """
        if personality_id not in self.personalities:
            return {"error": f"Personality '{personality_id}' not found."}
        
        personality = self.personalities[personality_id]
        
        if trait_type == "primary_trait":
            if new_value not in VALID_PERSONALITY_TRAITS:
                return {"error": f"Invalid primary trait '{new_value}'. Must be one of: {', '.join(VALID_PERSONALITY_TRAITS)}"}
        elif trait_type in ("responsiveness", "flexibility"):
            if not (1 <= new_value <= 10):
                return {"error": f"{trait_type.capitalize()} must be between 1 and 10."}
        elif trait_type == "communication_style":
            if not isinstance(new_value, str) or not new_value.strip():
                return {"error": "Communication style must be a non-empty string."}
        
        personality[trait_type] = new_value
        self._log("personality_updated", {
            "personality_id": personality_id,
            "trait_type": trait_type,
            "new_value": new_value
        })
        return {
            "personality_id": personality_id,
            "updated_field": trait_type,
            "new_value": new_value,
        }

    # ── Assistant Configuration ──────────────────────────────────────────

    def register_assistant(
        self,
        name: str,
        personality_id: str,
        capabilities: List[str],
        availability: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new assistant with a specific personality.

        Args:
            name (str): Assistant display name.
            personality_id (str): Personality template ID.
            capabilities (List[str]): List of tasks assistant can perform.
            availability (List[str]): [Optional] Available time slots.

        Returns:
            assistant_id (str): Unique assistant identifier.
            assistant (Dict): The registered assistant record.
        """
        if not name.strip():
            return {"error": "Assistant name cannot be empty."}
        if personality_id not in self.personalities:
            return {"error": f"Personality '{personality_id}' not found."}
        if not capabilities:
            return {"error": "Assistant must have at least one capability."}

        assistant_id = f"A{self.assistant_counter}"
        self.assistant_counter += 1

        personality = self.personalities[personality_id]
        personality["usage_count"] += 1

        assistant = {
            "assistant_id": assistant_id,
            "name": name,
            "personality_id": personality_id,
            "personality_traits": {
                "primary": personality["primary_trait"],
                "secondary": personality["secondary_traits"],
                "communication_style": personality["communication_style"],
            },
            "capabilities": capabilities,
            "availability": availability or self.time_slots.copy(),
            "status": "available",
            "current_schedule": [],
            "task_count": 0,
            "completed_count": 0,
        }
        self.assistants[assistant_id] = assistant
        self._log("assistant_registered", {
            "assistant_id": assistant_id,
            "name": name,
            "personality": personality["primary_trait"]
        })
        return {"assistant_id": assistant_id, "assistant": assistant}

    def update_assistant_availability(
        self,
        assistant_id: str,
        time_slots: List[str],
    ) -> Dict[str, Any]:
        """
        Update the available time slots for an assistant.

        Args:
            assistant_id (str): Assistant ID.
            time_slots (List[str]): New available time slots.

        Returns:
            assistant_id (str): Assistant ID.
            available_slots (List[str]): Updated availability.
        """
        if assistant_id not in self.assistants:
            return {"error": f"Assistant '{assistant_id}' not found."}
        if not all(slot in VALID_TIME_SLOTS for slot in time_slots):
            return {"error": f"Invalid time slot. Must be one of: {', '.join(VALID_TIME_SLOTS)}"}

        self.assistants[assistant_id]["availability"] = time_slots
        self._log("availability_updated", {
            "assistant_id": assistant_id,
            "time_slots": time_slots
        })
        return {
            "assistant_id": assistant_id,
            "available_slots": time_slots,
        }

    def list_assistants_by_trait(
        self,
        trait: str,
        status: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List assistants filtered by personality trait and optionally status.

        Args:
            trait (str): Personality trait to filter by.
            status (str): [Optional] Assistant status ('available', 'busy').

        Returns:
            assistants (List[Dict]): Matching assistant records.
        """
        if trait not in VALID_PERSONALITY_TRAITS:
            return {"error": f"Invalid trait '{trait}'. Must be one of: {', '.join(VALID_PERSONALITY_TRAITS)}"}

        assistants = []
        for assistant in self.assistants.values():
            if assistant["personality_traits"]["primary"] == trait:
                if status is None or assistant["status"] == status:
                    assistants.append(assistant)

        return {"assistants": assistants}

    # ── Schedule Orchestration ───────────────────────────────────────────

    def create_schedule(
        self,
        name: str,
        tasks: List[Dict[str, Any]] = None,
        priority: str = "medium",
        conflict_resolution: str = "notify",
    ) -> Dict[str, Any]:
        """
        Create a new schedule with multiple tasks.

        Args:
            name (str): Schedule name.
            tasks (List[Dict]): List of task definitions. Each task requires:
                - task_id (str): Unique task identifier.
                - description (str): Task description.
                - required_capability (str): Required assistant capability.
                - preferred_trait (str): Preferred assistant personality.
                - time_slot (str): Desired time slot.
                - duration (int): Duration in hours.
            priority (str): Schedule priority ('low', 'medium', 'high').
            conflict_resolution (str): How to handle conflicts.

        Returns:
            schedule_id (str): Unique schedule identifier.
            schedule (Dict): The created schedule with task assignments.
        """
        if not isinstance(name, str) or not name.strip():
            return {"error": "name must be a non-empty string."}
        if tasks is None:
            tasks = []
        if not isinstance(tasks, list):
            return {"error": "tasks must be a list."}
        if not tasks:
            return {"error": "Schedule must contain at least one task."}
        if conflict_resolution not in VALID_CONFLICT_RESOLUTIONS:
            return {"error": f"Invalid conflict resolution '{conflict_resolution}'. Must be one of: {', '.join(VALID_CONFLICT_RESOLUTIONS)}"}

        task_ids = [t["task_id"] for t in tasks]
        if len(task_ids) != len(set(task_ids)):
            return {"error": "Duplicate task_id values are not allowed within a schedule."}

        for task in tasks:
            required = ("task_id", "description", "required_capability", "time_slot")
            for field in required:
                if field not in task:
                    return {"error": f"Task '{task.get('task_id', '?')}' missing required field '{field}'."}
            if task["time_slot"] not in VALID_TIME_SLOTS:
                return {"error": f"Invalid time slot '{task['time_slot']}' for task '{task['task_id']}'."}

        schedule_id = f"S{self.schedule_counter}"
        self.schedule_counter += 1

        initialized_tasks = []
        for task in tasks:
            t = {
                "task_id": task["task_id"],
                "description": task["description"],
                "required_capability": task["required_capability"],
                "preferred_trait": task.get("preferred_trait"),
                "time_slot": task["time_slot"],
                "duration": task.get("duration", 1),
                "status": "pending",
                "assigned_assistant": None,
                "conflicts": [],
            }
            initialized_tasks.append(t)

        schedule = {
            "schedule_id": schedule_id,
            "name": name,
            "priority": priority,
            "conflict_resolution": conflict_resolution,
            "status": "draft",
            "tasks": initialized_tasks,
            "conflict_count": 0,
            "created_at": datetime.now().isoformat(),
        }
        self.schedules[schedule_id] = schedule
        self._log("schedule_created", {
            "schedule_id": schedule_id,
            "name": name,
            "task_count": len(tasks),
            "priority": priority
        })
        return {"schedule_id": schedule_id, "schedule": schedule}

    def assign_task(
        self,
        schedule_id: str,
        task_id: str,
        assistant_id: str,
    ) -> Dict[str, Any]:
        """
        Assign an assistant to a specific task within a schedule.

        Args:
            schedule_id (str): Schedule ID.
            task_id (str): Task ID within the schedule.
            assistant_id (str): Assistant ID to assign.

        Returns:
            task_id (str): The assigned task ID.
            assistant_id (str): The assigned assistant.
            assignment_result (str): Status of assignment.
        """
        if schedule_id not in self.schedules:
            return {"error": f"Schedule '{schedule_id}' not found."}
        if assistant_id not in self.assistants:
            return {"error": f"Assistant '{assistant_id}' not found."}

        schedule = self.schedules[schedule_id]
        task = self._find_task(schedule, task_id)
        if not task:
            return {"error": f"Task '{task_id}' not found in schedule {schedule_id}."}

        assistant = self.assistants[assistant_id]
        
        # Check capability match
        if task["required_capability"] not in assistant["capabilities"]:
            return {"error": f"Assistant '{assistant_id}' lacks required capability '{task['required_capability']}'."}
        
        # Check availability
        if task["time_slot"] not in assistant["availability"]:
            return {"error": f"Assistant '{assistant_id}' not available in time slot '{task['time_slot']}'."}
        
        # Check personality preference
        if task.get("preferred_trait"):
            if task["preferred_trait"] != assistant["personality_traits"]["primary"]:
                self._log("personality_mismatch", {
                    "task_id": task_id,
                    "preferred": task["preferred_trait"],
                    "actual": assistant["personality_traits"]["primary"]
                })

        # Check for conflicts
        conflict = self._check_schedule_conflict(assistant_id, task_id, task["time_slot"])
        if conflict:
            if schedule["conflict_resolution"] == "notify":
                task["conflicts"].append(conflict)
                schedule["conflict_count"] += 1
                assignment_status = "assigned_with_conflict"
                self._log("assignment_conflict", {
                    "task_id": task_id,
                    "assistant_id": assistant_id,
                    "conflict_with": conflict["conflicting_task"]
                })
            elif schedule["conflict_resolution"] == "skip":
                return {"error": f"Cannot assign due to conflict with task '{conflict['conflicting_task']}'. Conflict policy is 'skip'."}
            else:
                assignment_status = "assigned_override"
        else:
            assignment_status = "assigned_successfully"

        task["assigned_assistant"] = assistant_id
        task["status"] = "assigned"
        
        # Update assistant's current schedule
        self.assistants[assistant_id]["current_schedule"].append({
            "task_id": task_id,
            "schedule_id": schedule_id,
            "time_slot": task["time_slot"],
        })
        
        if assignment_status == "assigned_successfully":
            self.assistants[assistant_id]["status"] = "busy"

        self._log("task_assigned", {
            "schedule_id": schedule_id,
            "task_id": task_id,
            "assistant_id": assistant_id,
            "status": assignment_status
        })
        return {
            "task_id": task_id,
            "assistant_id": assistant_id,
            "assignment_result": assignment_status,
        }

    def execute_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """
        Execute all tasks in a schedule, respecting time slots and assignments.

        Args:
            schedule_id (str): Schedule ID.

        Returns:
            schedule_id (str): The executed schedule ID.
            status (str): Overall schedule status.
            task_results (Dict[str, str]): Status per task.
        """
        if schedule_id not in self.schedules:
            return {"error": f"Schedule '{schedule_id}' not found."}

        schedule = self.schedules[schedule_id]
        if schedule["status"] not in ("draft", "active"):
            return {"error": f"Schedule {schedule_id} is already {schedule['status']}."}

        schedule["status"] = "active"
        task_results = {}

        # Group tasks by time slot
        tasks_by_slot = {}
        for task in schedule["tasks"]:
            slot = task["time_slot"]
            if slot not in tasks_by_slot:
                tasks_by_slot[slot] = []
            tasks_by_slot[slot].append(task)

        # Execute tasks slot by slot
        for slot, tasks in tasks_by_slot.items():
            for task in tasks:
                if task["status"] == "assigned":
                    result = self._execute_task(schedule_id, task["task_id"])
                    task_results[task["task_id"]] = result.get("status", "unknown")

        # Update overall schedule status
        all_done = all(t["status"] in ("completed", "failed", "skipped") for t in schedule["tasks"])
        if all_done:
            had_failure = any(t["status"] == "failed" for t in schedule["tasks"])
            schedule["status"] = "failed" if had_failure else "completed"

        return {
            "schedule_id": schedule_id,
            "status": schedule["status"],
            "task_results": task_results,
        }

    def _execute_task(self, schedule_id: str, task_id: str) -> Dict[str, Any]:
        """Execute a single task within a schedule."""
        schedule = self.schedules[schedule_id]
        task = self._find_task(schedule, task_id)
        if not task or not task["assigned_assistant"]:
            return {"error": f"Task '{task_id}' not properly assigned."}

        assistant_id = task["assigned_assistant"]
        assistant = self.assistants[assistant_id]
        
        # Simulate task execution based on personality
        success, result = self._simulate_task_execution(task, assistant)
        
        if success:
            task["status"] = "completed"
            assistant["completed_count"] += 1
            self._log("task_completed", {
                "schedule_id": schedule_id,
                "task_id": task_id,
                "assistant_id": assistant_id
            })
        else:
            task["status"] = "failed"
            self._log("task_failed", {
                "schedule_id": schedule_id,
                "task_id": task_id,
                "result": result
            })

        assistant["task_count"] += 1
        
        # Update assistant status if no more tasks
        remaining_tasks = []
        for t in assistant["current_schedule"]:
            schedule = self.schedules.get(t["schedule_id"])
            if schedule is None:
                continue
            found = self._find_task(schedule, t["task_id"])
            if found is None:
                continue
            if found["status"] not in ("completed", "failed"):
                remaining_tasks.append(t)
        if not remaining_tasks:
            assistant["status"] = "available"

        return {"task_id": task_id, "status": task["status"], "result": result}

    def resolve_conflict(
        self,
        schedule_id: str = None,
        task_id: str = None,
        resolution: str = None,
        new_time_slot: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Resolve a scheduling conflict for a specific task.

        Args:
            schedule_id (str): Schedule ID.
            task_id (str): Task ID with conflict.
            resolution (str): Resolution method ('reschedule', 'override', 'skip').
            new_time_slot (str): [Optional] New time slot for rescheduling.

        Returns:
            task_id (str): The task ID.
            resolution (str): Applied resolution method.
            result (str): Resolution outcome.
        """
        if not isinstance(schedule_id, str):
            return {"error": "schedule_id must be a string."}
        if not isinstance(task_id, str):
            return {"error": "task_id must be a string."}
        if not isinstance(resolution, str):
            return {"error": "resolution must be a string."}

        if schedule_id not in self.schedules:
            return {"error": f"Schedule '{schedule_id}' not found."}
        if resolution not in VALID_CONFLICT_RESOLUTIONS:
            return {"error": f"Invalid resolution '{resolution}'. Must be one of: {', '.join(VALID_CONFLICT_RESOLUTIONS)}"}
        if resolution == "reschedule" and not new_time_slot:
            return {"error": "New time slot required for rescheduling."}
        if resolution == "reschedule" and new_time_slot not in VALID_TIME_SLOTS:
            return {"error": f"Invalid time slot '{new_time_slot}'."}

        schedule = self.schedules[schedule_id]
        task = self._find_task(schedule, task_id)
        if not task:
            return {"error": f"Task '{task_id}' not found in schedule {schedule_id}."}
        if not task["conflicts"]:
            return {"error": f"No conflicts found for task '{task_id}'."}

        if resolution == "reschedule":
            task["time_slot"] = new_time_slot
            task["conflicts"] = []
            schedule["conflict_count"] -= 1
            result = f"Rescheduled to {new_time_slot}"
        elif resolution == "override":
            task["conflicts"] = []
            schedule["conflict_count"] -= 1
            result = "Conflict overridden, will execute anyway"
        elif resolution == "skip":
            task["status"] = "skipped"
            task["conflicts"] = []
            schedule["conflict_count"] -= 1
            result = "Task skipped due to conflict"

        self._log("conflict_resolved", {
            "schedule_id": schedule_id,
            "task_id": task_id,
            "resolution": resolution,
            "result": result
        })
        return {
            "task_id": task_id,
            "resolution": resolution,
            "result": result,
        }

    # ── Result Collection ────────────────────────────────────────────────

    def get_schedule_summary(self, schedule_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of a schedule's status and assignments.

        Args:
            schedule_id (str): Schedule ID.

        Returns:
            schedule_id (str): The schedule ID.
            summary (Dict): Comprehensive schedule summary.
            assignments (Dict): Task assignment details.
        """
        if schedule_id not in self.schedules:
            return {"error": f"Schedule '{schedule_id}' not found."}

        schedule = self.schedules[schedule_id]
        
        task_summary = []
        for task in schedule["tasks"]:
            assistant = self.assistants.get(task.get("assigned_assistant", ""), {})
            task_summary.append({
                "task_id": task["task_id"],
                "description": task["description"],
                "status": task["status"],
                "assigned_to": assistant.get("name", "Unassigned"),
                "personality": assistant.get("personality_traits", {}).get("primary", "Unknown"),
                "time_slot": task["time_slot"],
                "conflicts": len(task["conflicts"]),
            })

        summary = {
            "schedule_name": schedule["name"],
            "status": schedule["status"],
            "total_tasks": len(schedule["tasks"]),
            "assigned_tasks": sum(1 for t in schedule["tasks"] if t["status"] == "assigned"),
            "completed_tasks": sum(1 for t in schedule["tasks"] if t["status"] == "completed"),
            "pending_tasks": sum(1 for t in schedule["tasks"] if t["status"] == "pending"),
            "conflict_count": schedule.get("conflict_count", 0),
            "priority": schedule["priority"],
        }

        return {
            "schedule_id": schedule_id,
            "summary": summary,
            "task_details": task_summary,
        }

    def get_assistant_performance(self, assistant_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific assistant.

        Args:
            assistant_id (str): Assistant ID.

        Returns:
            assistant_id (str): Assistant ID.
            performance (Dict): Performance metrics.
            personality_impact (Dict): Personality-based metrics.
        """
        if assistant_id not in self.assistants:
            return {"error": f"Assistant '{assistant_id}' not found."}

        assistant = self.assistants[assistant_id]
        personality = self.personalities.get(assistant["personality_id"], {})
        
        # Calculate completion rate
        total_tasks = assistant["task_count"]
        completed = assistant["completed_count"]
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0

        performance = {
            "name": assistant["name"],
            "personality": assistant["personality_traits"]["primary"],
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "completion_rate": f"{completion_rate:.1f}%",
            "current_status": assistant["status"],
            "capabilities": assistant["capabilities"],
            "availability": assistant["availability"],
        }

        personality_impact = {
            "primary_trait": personality.get("primary_trait"),
            "responsiveness": personality.get("responsiveness"),
            "flexibility": personality.get("flexibility"),
            "usage_count": personality.get("usage_count", 0),
        }

        return {
            "assistant_id": assistant_id,
            "performance": performance,
            "personality_impact": personality_impact,
        }

    # ── Helper Methods ───────────────────────────────────────────────────

    def _find_task(self, schedule: Dict, task_id: str) -> Optional[Dict[str, Any]]:
        """Find a task within a schedule by task_id."""
        for t in schedule["tasks"]:
            if t["task_id"] == task_id:
                return t
        return None

    def _check_schedule_conflict(
        self,
        assistant_id: str,
        task_id: str,
        time_slot: str,
    ) -> Optional[Dict[str, Any]]:
        """Check if assigning this task would create a schedule conflict."""
        assistant = self.assistants[assistant_id]
        for scheduled in assistant["current_schedule"]:
            if scheduled["time_slot"] == time_slot:
                # Check if the other task is still active
                other_schedule = self.schedules.get(scheduled["schedule_id"])
                if other_schedule:
                    other_task = self._find_task(other_schedule, scheduled["task_id"])
                    if other_task and other_task["status"] in ("assigned", "pending"):
                        return {
                            "conflicting_task": scheduled["task_id"],
                            "conflicting_schedule": scheduled["schedule_id"],
                            "time_slot": time_slot,
                        }
        return None

    def _simulate_task_execution(self, task: Dict, assistant: Dict) -> Tuple[bool, Dict]:
        """Simulate task execution based on assistant's personality."""
        personality = assistant["personality_traits"]["primary"]
        
        # Personality-specific success rates
        success_rates = {
            "gentle": 0.9,
            "strict": 0.95,
            "humorous": 0.85,
            "grumpy": 0.7,
            "energetic": 0.88,
            "calm": 0.92,
            "sarcastic": 0.75,
        }
        
        success_rate = success_rates.get(personality, 0.8)
        success = random.random() < success_rate
        
        if success:
            result = {
                "task_id": task["task_id"],
                "assistant": assistant["name"],
                "personality": personality,
                "message": f"{assistant['name']} ({personality}) successfully completed: {task['description']}",
                "quality_score": random.randint(7, 10),
            }
        else:
            result = {
                "task_id": task["task_id"],
                "assistant": assistant["name"],
                "personality": personality,
                "error": f"{assistant['name']} ({personality}) failed to complete: {task['description']}",
                "suggestion": "Consider reassigning with different personality or time slot",
            }
        
        return success, result

    def _log(self, event: str, detail: Dict) -> None:
        """Append an entry to the execution log."""
        self.execution_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat(),
        })