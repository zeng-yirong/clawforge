from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
import re
import random

DEFAULT_STATE = {
    "personas": [],  # All defined assistant persona configurations
    "schedules": {},  # Schedule entries, key: schedule_id
    "active_assistants": [],  # Currently active assistant instances
    "persona_counter": 1,  # Persona ID counter
    "schedule_counter": 1,  # Schedule ID counter
    "assistant_counter": 1,  # Assistant instance ID counter
    "preferences": {  # Global preference settings
        "default_reminder_lead": 30,  # Default advance reminder time (minutes)
        "max_daily_events": 20,  # Max daily events
        "conflict_resolution_strategy": "ask",  # Conflict resolution strategy: ask, auto_reject, auto_reschedule
    }
}

VALID_PERSONA_TYPES = ("gentle_secretary", "strict_manager", "friendly_teen", "grumpy_old_bro", "efficient_ai")
VALID_MOODS = ("calm", "happy", "annoyed", "tired", "energetic", "frustrated", "content")
VALID_EVENT_TYPES = ("meeting", "reminder", "deadline", "break", "meal", "exercise", "other")
VALID_PRIORITIES = ("low", "medium", "high", "urgent")
VALID_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class PersonalAssistantConversationalEnv:
    """
    Personal assistant customization and schedule management environment.

    This environment allows users to create virtual assistants with specific personas (e.g. gentle secretary, grumpy old bro),
    configure their behavioral parameters, and schedule, manage, and coordinate calendar events through the assistant.
    Assistants handle schedule conflicts, reminders, and rescheduling requests with different tones and strategies based on their persona traits.

    Attributes:
        personas (List[Dict]): All defined persona configuration templates.
        schedules (Dict[str, List[Dict]]): Schedule entries grouped by assistant ID.
        active_assistants (List[Dict]): Currently active assistant instances.
        persona_counter (int): Auto-incrementing persona ID counter.
        schedule_counter (int): Auto-incrementing schedule ID counter.
        assistant_counter (int): Auto-incrementing assistant instance ID counter.
        preferences (Dict): Global scheduling preference settings.
    """

    def __init__(self):
        self.personas: List[Dict[str, Any]]
        self.schedules: Dict[str, List[Dict[str, Any]]]
        self.active_assistants: List[Dict[str, Any]]
        self.persona_counter: int
        self.schedule_counter: int
        self.assistant_counter: int
        self.preferences: Dict[str, Any]
        self._api_description = (
            "Create virtual assistants with specific personas (e.g. gentle secretary, grumpy old bro), configure their behavioral parameters, "
            "and schedule, manage, and coordinate personal calendar events through the assistant, handling conflicts and reminders."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.personas = scenario.get("personas", DEFAULT_STATE_COPY["personas"])
        self.schedules = scenario.get("schedules", DEFAULT_STATE_COPY["schedules"])
        self.active_assistants = scenario.get("active_assistants", DEFAULT_STATE_COPY["active_assistants"])
        self.persona_counter = scenario.get("persona_counter", DEFAULT_STATE_COPY["persona_counter"])
        self.schedule_counter = scenario.get("schedule_counter", DEFAULT_STATE_COPY["schedule_counter"])
        self.assistant_counter = scenario.get("assistant_counter", DEFAULT_STATE_COPY["assistant_counter"])
        self.preferences = scenario.get("preferences", DEFAULT_STATE_COPY["preferences"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: Dictionary containing all environment state variables, including:
                - personas: All persona configuration templates
                - schedules: All schedule entries (grouped by assistant ID)
                - active_assistants: Currently active assistant instances
                - persona_counter: Persona ID counter
                - schedule_counter: Schedule ID counter
                - assistant_counter: Assistant instance counter
                - preferences: Global preference settings
        """
        return {
            "personas": self.personas,
            "schedules": self.schedules,
            "active_assistants": self.active_assistants,
            "persona_counter": self.persona_counter,
            "schedule_counter": self.schedule_counter,
            "assistant_counter": self.assistant_counter,
            "preferences": self.preferences,
        }

    # ── Persona configuration management ───────────────────────────────────────────────

    def create_persona(
        self,
        persona_type: str,
        name: str,
        description: str,
        behavior_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new persona configuration template.

        Args:
            persona_type (str): Persona type, must be one of VALID_PERSONA_TYPES.
            name (str): Persona name (e.g. "Gentle Secretary")
            description (str): Persona description, at least 10 characters.
            behavior_params (Dict): [Optional] Specific behavior parameters:
                - patience_level (int): Patience level 1-10
                - formality (int): Formality level 1-10
                - verbosity (int): Verbosity level 1-10
                - humor_level (int): Humor level 0-10
                - allowed_conflict_types (List[str]): Allowed schedule conflict types
                - auto_reschedule_threshold (int): Auto-reschedule threshold (minutes)

        Returns:
            persona_id (str): Newly created persona ID
            persona (Dict): Complete persona configuration
        """
        if persona_type not in VALID_PERSONA_TYPES:
            return {"error": f"Invalid persona type '{persona_type}'. Must be: {', '.join(VALID_PERSONA_TYPES)}"}
        if not name.strip():
            return {"error": "Persona name cannot be empty"}
        if len(description) < 10:
            return {"error": "Persona description requires at least 10 characters"}

        behavior_params = behavior_params or {}
        persona_id = f"pers_{self.persona_counter}"
        self.persona_counter += 1

        # Set default parameters based on type
        default_params = self._get_default_persona_params(persona_type)
        for key, value in default_params.items():
            if key not in behavior_params:
                behavior_params[key] = value

        persona = {
            "persona_id": persona_id,
            "type": persona_type,
            "name": name,
            "description": description,
            "behavior_params": behavior_params,
            "created_at": datetime.now().isoformat(),
            "mood": "calm",  # Current mood state
            "mood_trend": "stable",  # Mood trend
            "total_assistants_created": 0,  # Number of assistants created with this persona
        }
        self.personas.append(persona)
        return {"persona_id": persona_id, "persona": persona}

    def edit_persona(
        self,
        persona_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        behavior_params_updates: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Edit an existing persona configuration.

        Args:
            persona_id (str): Persona ID to edit
            name (str): [Optional] New name
            description (str): [Optional] New description
            behavior_params_updates (Dict): [Optional] Behavior parameters to update

        Returns:
            updated_persona (Dict): Updated persona configuration
        """
        persona = self._find_persona(persona_id)
        if not persona:
            return {"error": f"Persona '{persona_id}' not found"}

        if name is not None:
            if not name.strip():
                return {"error": "Persona name cannot be empty"}
            persona["name"] = name
        if description is not None:
            if len(description) < 10:
                return {"error": "Persona description requires at least 10 characters"}
            persona["description"] = description
        if behavior_params_updates:
            for key, value in behavior_params_updates.items():
                if key in persona["behavior_params"]:
                    if key == "patience_level" and not (1 <= value <= 10):
                        return {"error": "Patience level must be between 1-10"}
                    if key == "formality" and not (1 <= value <= 10):
                        return {"error": "Formality must be between 1-10"}
                    if key == "verbosity" and not (1 <= value <= 10):
                        return {"error": "Verbosity must be between 1-10"}
                    if key == "humor_level" and not (0 <= value <= 10):
                        return {"error": "Humor level must be between 0-10"}
                    persona["behavior_params"][key] = value

        persona["last_modified"] = datetime.now().isoformat()
        return {"updated_persona": persona}

    def list_personas(self, persona_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all available persona configurations.

        Args:
            persona_type (str): [Optional] Filter by type

        Returns:
            personas (List[Dict]): List of matching persona configurations
        """
        if persona_type and persona_type not in VALID_PERSONA_TYPES:
            return {"error": f"Invalid persona type '{persona_type}'"}

        personas = self.personas
        if persona_type:
            personas = [p for p in personas if p["type"] == persona_type]

        summaries = [{
            "persona_id": p["persona_id"],
            "type": p["type"],
            "name": p["name"],
            "mood": p.get("mood", "calm"),
            "total_assistants": p.get("total_assistants_created", 0),
        } for p in personas]
        return {"personas": summaries}

    # ── Assistant instance management ───────────────────────────────────────────────

    def create_assistant(
        self,
        persona_id: str,
        assistant_name: str,
        schedule_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new assistant instance using a specified persona.

        Args:
            persona_id (str): Persona ID to use
            assistant_name (str): Assistant instance name
            schedule_preferences (Dict): [Optional] Assistant-specific schedule preferences:
                - work_hours (Dict): Work hours, e.g. {"start": "09:00", "end": "18:00"}
                - preferred_break_times (List[str]): Preferred break times
                - max_events_per_day (int): Max events per day
                - min_gap_between_events (int): Min gap between events (minutes)

        Returns:
            assistant_id (str): New assistant instance ID
            assistant (Dict): Assistant instance configuration
        """
        persona = self._find_persona(persona_id)
        if not persona:
            return {"error": f"Persona '{persona_id}' not found"}
        if not assistant_name.strip():
            return {"error": "Assistant name cannot be empty"}

        # Update persona usage count
        persona["total_assistants_created"] = persona.get("total_assistants_created", 0) + 1

        assistant_id = f"assist_{self.assistant_counter}"
        self.assistant_counter += 1

        schedule_preferences = schedule_preferences or {}
        # Merge global preferences
        for key in ["max_daily_events", "default_reminder_lead"]:
            if key not in schedule_preferences and key in self.preferences:
                schedule_preferences[key] = self.preferences[key]

        assistant = {
            "assistant_id": assistant_id,
            "persona_id": persona_id,
            "name": assistant_name,
            "persona_type": persona["type"],
            "persona_name": persona["name"],
            "mood": persona.get("mood", "calm"),
            "schedule_preferences": schedule_preferences,
            "created_at": datetime.now().isoformat(),
            "is_active": True,
            "total_events_scheduled": 0,
            "conflicts_resolved": 0,
            "reminders_sent": 0,
        }

        self.active_assistants.append(assistant)
        self.schedules[assistant_id] = []  # Initialize empty schedule
        return {"assistant_id": assistant_id, "assistant": assistant}

    def activate_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Activate a deactivated assistant instance.

        Args:
            assistant_id (str): Assistant ID to activate

        Returns:
            assistant (Dict): Updated assistant info
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}

        if assistant["is_active"]:
            return {"warning": f"Assistant '{assistant_id}' is already activated"}

        assistant["is_active"] = True
        assistant["last_activated"] = datetime.now().isoformat()
        return {"assistant": assistant}

    def deactivate_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Deactivate an assistant instance (preserving its schedule data).

        Args:
            assistant_id (str): Assistant ID to deactivate

        Returns:
            assistant (Dict): Updated assistant info
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}

        if not assistant["is_active"]:
            return {"warning": f"Assistant '{assistant_id}' is already deactivated"}

        assistant["is_active"] = False
        assistant["last_deactivated"] = datetime.now().isoformat()
        return {"assistant": assistant}

    def list_assistants(self, active_only: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all assistant instances.

        Args:
            active_only (bool): Whether to list only activated assistants

        Returns:
            assistants (List[Dict]): List of assistant instances
        """
        assistants = self.active_assistants
        if active_only:
            assistants = [a for a in assistants if a["is_active"]]

        summaries = [{
            "assistant_id": a["assistant_id"],
            "name": a["name"],
            "persona_type": a["persona_type"],
            "persona_name": a["persona_name"],
            "is_active": a["is_active"],
            "total_events": a.get("total_events_scheduled", 0),
            "mood": a.get("mood", "calm"),
        } for a in assistants]
        return {"assistants": summaries}

    # ── Schedule management ─────────────────────────────────────────────────

    def schedule_event(
        self,
        assistant_id: str,
        title: str,
        start_time: str,
        duration_minutes: int,
        event_type: str = "meeting",
        priority: str = "medium",
        description: str = "",
        recurrence: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a new event through the assistant.

        Args:
            assistant_id (str): Assistant ID responsible for scheduling
            title (str): Event title
            start_time (str): Start time (ISO format or YYYY-MM-DD HH:MM)
            duration_minutes (int): Duration in minutes
            event_type (str): Event type, must be one of VALID_EVENT_TYPES
            priority (str): Priority, must be one of VALID_PRIORITIES
            description (str): [Optional] Event description
            recurrence (Dict): [Optional] Recurrence rules:
                - frequency (str): "daily", "weekly", "monthly"
                - interval (int): Interval
                - days_of_week (List[str]): Days of the week
                - end_date (str): End date

        Returns:
            event_id (str): Created event ID
            event (Dict): Complete event details
            assistant_reaction (Dict): Assistant's reaction (based on persona)
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}
        if not assistant["is_active"]:
            return {"error": f"Assistant '{assistant_id}' is deactivated, cannot schedule events"}

        # Validate parameters
        if event_type not in VALID_EVENT_TYPES:
            return {"error": f"Invalid event type '{event_type}'"}
        if priority not in VALID_PRIORITIES:
            return {"error": f"Invalid priority '{priority}'"}
        if not title.strip():
            return {"error": "Event title cannot be empty"}
        if duration_minutes <= 0:
            return {"error": "Duration must be greater than 0 minutes"}

        # Parse start time
        try:
            start_dt = self._parse_datetime(start_time)
        except ValueError as e:
            return {"error": f"Invalid start time format: {str(e)}"}
        if start_dt is None:
            return {"error": "Invalid start time format"}

        end_dt = start_dt + timedelta(minutes=duration_minutes)

        # Check schedule capacity
        daily_events = self._count_daily_events(assistant_id, start_dt.date())
        max_events = assistant["schedule_preferences"].get("max_daily_events", 
                     self.preferences.get("max_daily_events", 20))
        if daily_events >= max_events:
            reaction = self._generate_assistant_reaction(
                assistant, 
                "schedule_denied_max_events",
                {"current": daily_events, "max": max_events}
            )
            return {"error": "Daily event limit reached", "assistant_reaction": reaction}

        # Check conflicts
        conflicts = self._check_schedule_conflicts(assistant_id, start_dt, end_dt)
        if conflicts:
            conflict_resolution = self._handle_conflict(
                assistant, 
                conflicts[0], 
                {"title": title, "start": start_dt, "end": end_dt}
            )
            if conflict_resolution.get("allow_new_event"):
                # Handle conflict events based on strategy
                if conflict_resolution.get("reschedule_conflict"):
                    self._reschedule_event(conflicts[0]["event_id"], conflict_resolution.get("new_time"))
            else:
                return {"error": "Schedule conflict", "conflicts": conflicts, "assistant_reaction": conflict_resolution.get("reaction")}

        # Create event
        event_id = f"evt_{self.schedule_counter}"
        self.schedule_counter += 1

        event = {
            "event_id": event_id,
            "assistant_id": assistant_id,
            "title": title,
            "description": description,
            "event_type": event_type,
            "priority": priority,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "duration_minutes": duration_minutes,
            "recurrence": recurrence or {},
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
            "reminder_sent": False,
            "reminder_time": None,
        }

        # Set reminder time
        reminder_lead = assistant["schedule_preferences"].get("default_reminder_lead", 
                     self.preferences.get("default_reminder_lead", 30))
        if reminder_lead > 0:
            reminder_dt = start_dt - timedelta(minutes=reminder_lead)
            event["reminder_time"] = reminder_dt.isoformat()

        self.schedules[assistant_id].append(event)
        assistant["total_events_scheduled"] = assistant.get("total_events_scheduled", 0) + 1

        # Generate assistant reaction
        reaction = self._generate_assistant_reaction(
            assistant, 
            "schedule_success",
            {"title": title, "start": start_dt, "event_type": event_type}
        )

        return {
            "event_id": event_id,
            "event": event,
            "assistant_reaction": reaction,
        }

    def reschedule_event(
        self,
        assistant_id: str,
        event_id: str,
        new_start_time: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """
        Reschedule an existing event.

        Args:
            assistant_id (str): Assistant ID
            event_id (str): Event ID to reschedule
            new_start_time (str): New start time
            reason (str): [Optional] Reason for rescheduling

        Returns:
            updated_event (Dict): Updated event
            assistant_reaction (Dict): Assistant's reaction
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}

        event = self._find_event(assistant_id, event_id)
        if not event:
            return {"error": f"Event '{event_id}' not found"}

        # Parse new time
        try:
            new_start_dt = self._parse_datetime(new_start_time)
        except ValueError as e:
            return {"error": f"Invalid new start time format: {str(e)}"}
        if new_start_dt is None:
            return {"error": "Invalid new start time format"}

        duration = event["duration_minutes"]
        new_end_dt = new_start_dt + timedelta(minutes=duration)

        # Check conflicts (excluding self)
        conflicts = self._check_schedule_conflicts(
            assistant_id, new_start_dt, new_end_dt, exclude_event_id=event_id
        )
        if conflicts:
            reaction = self._generate_assistant_reaction(
                assistant,
                "reschedule_conflict",
                {"conflicts": len(conflicts)}
            )
            return {"error": "New time has conflicts", "conflicts": conflicts, "assistant_reaction": reaction}

        # Update event
        old_start = event["start_time"]
        event["start_time"] = new_start_dt.isoformat()
        event["end_time"] = new_end_dt.isoformat()
        event["last_modified"] = datetime.now().isoformat()
        event["reschedule_reason"] = reason
        event["original_scheduled_time"] = old_start  # Keep original schedule time record

        # Update reminder time
        reminder_lead = assistant["schedule_preferences"].get("default_reminder_lead", 
                     self.preferences.get("default_reminder_lead", 30))
        if reminder_lead > 0:
            reminder_dt = new_start_dt - timedelta(minutes=reminder_lead)
            event["reminder_time"] = reminder_dt.isoformat()

        reaction = self._generate_assistant_reaction(
            assistant, 
            "reschedule_success",
            {"title": event["title"], "from": old_start, "to": new_start_dt}
        )

        return {
            "updated_event": event,
            "assistant_reaction": reaction,
        }

    def cancel_event(
        self,
        assistant_id: str,
        event_id: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """
        Cancel a scheduled event.

        Args:
            assistant_id (str): Assistant ID
            event_id (str): Event ID to cancel
            reason (str): [Optional] Cancellation reason

        Returns:
            cancelled_event (Dict): Cancelled event
            assistant_reaction (Dict): Assistant's reaction
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}

        event = self._find_event(assistant_id, event_id)
        if not event:
            return {"error": f"Event '{event_id}' not found"}

        if event["status"] == "cancelled":
            return {"warning": f"Event '{event_id}' is already cancelled"}

        event["status"] = "cancelled"
        event["cancelled_at"] = datetime.now().isoformat()
        event["cancellation_reason"] = reason

        reaction = self._generate_assistant_reaction(
            assistant, 
            "event_cancelled",
            {"title": event["title"], "reason": reason}
        )

        return {
            "cancelled_event": event,
            "assistant_reaction": reaction,
        }

    def get_schedule(
        self,
        assistant_id: str,
        date: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the assistant's schedule.

        Args:
            assistant_id (str): Assistant ID
            date (str): [Optional] Filter by specific date (YYYY-MM-DD)
            event_type (str): [Optional] Filter by event type

        Returns:
            schedule (List[Dict]): List of events
            summary (Dict): Schedule statistics summary
        """
        if assistant_id not in self.schedules:
            return {"error": f"Assistant '{assistant_id}' not found or no schedule"}

        events = self.schedules[assistant_id]

        # Apply filters
        if date:
            try:
                target_date = datetime.fromisoformat(date.replace(" ", "T")).date()
                events = [
                    e for e in events
                    if (parsed := self._parse_datetime(e["start_time"])) is not None
                    and parsed.date() == target_date
                ]
            except ValueError:
                return {"error": "Invalid date format, please use YYYY-MM-DD"}

        if event_type:
            if event_type not in VALID_EVENT_TYPES:
                return {"error": f"Invalid event type '{event_type}'"}
            events = [e for e in events if e["event_type"] == event_type]

        # Only return uncancelled events
        active_events = [e for e in events if e["status"] != "cancelled"]
        active_events.sort(key=lambda x: x["start_time"])

        # Generate statistics
        summary = {
            "total_events": len(active_events),
            "by_type": {},
            "by_priority": {},
            "time_coverage": 0,  # TODO: calculate time coverage
        }

        for event in active_events:
            e_type = event["event_type"]
            priority = event["priority"]
            summary["by_type"][e_type] = summary["by_type"].get(e_type, 0) + 1
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1

        assistant = self._find_assistant(assistant_id)
        assistant_reaction = None
        if assistant:
            assistant_reaction = self._generate_assistant_reaction(
                assistant, 
                "schedule_viewed",
                {"date": date, "event_count": len(active_events)}
            )

        return {
            "schedule": active_events,
            "summary": summary,
            "assistant_reaction": assistant_reaction,
        }

    def check_reminders(self, assistant_id: str, current_time: str) -> Dict[str, Any]:
        """
        Check and return upcoming reminders.

        Args:
            assistant_id (str): Assistant ID
            current_time (str): Current time

        Returns:
            reminders (List[Dict]): List of upcoming reminders
            assistant_reaction (Dict): Assistant's reaction
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}

        try:
            now = self._parse_datetime(current_time)
        except ValueError as e:
            return {"error": f"Invalid current time format: {str(e)}"}
        if now is None:
            return {"error": "Invalid current time format"}

        events = self.schedules.get(assistant_id, [])
        upcoming_reminders = []

        for event in events:
            if (event["status"] == "scheduled" and 
                event.get("reminder_time") and 
                not event.get("reminder_sent", False)):

                reminder_time = self._parse_datetime(event["reminder_time"])
                event_time = self._parse_datetime(event["start_time"])
                if reminder_time is None or event_time is None:
                    continue

                # Check if reminder time has arrived
                if reminder_time <= now < event_time:
                    time_until_event = event_time - now
                    minutes_until = int(time_until_event.total_seconds() / 60)

                    reminder = {
                        "event_id": event["event_id"],
                        "title": event["title"],
                        "event_type": event["event_type"],
                        "start_time": event["start_time"],
                        "minutes_until": minutes_until,
                        "priority": event["priority"],
                    }
                    upcoming_reminders.append(reminder)

                    # Mark as sent
                    event["reminder_sent"] = True
                    event["reminder_sent_at"] = now.isoformat()

        assistant["reminders_sent"] = assistant.get("reminders_sent", 0) + len(upcoming_reminders)

        reaction = self._generate_assistant_reaction(
            assistant, 
            "reminders_checked",
            {"count": len(upcoming_reminders), "current_time": now}
        )

        upcoming_reminders.sort(key=lambda x: x["minutes_until"])
        return {
            "reminders": upcoming_reminders,
            "assistant_reaction": reaction,
        }

    def suggest_optimal_time(
        self,
        assistant_id: str,
        date: str,
        duration_minutes: int,
        preferred_times: Optional[List[str]] = None,
        event_type: str = "meeting",
    ) -> Dict[str, Any]:
        """
        Suggest optimal scheduling times.

        Args:
            assistant_id (str): Assistant ID
            date (str): Target date (YYYY-MM-DD)
            duration_minutes (int): Required duration
            preferred_times (List[str]): [Optional] List of preferred time slots
            event_type (str): Event type

        Returns:
            suggestions (List[Dict]): List of suggested time slots
            assistant_reaction (Dict): Assistant's reaction
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}

        try:
            target_date = datetime.fromisoformat(date.replace(" ", "T")).date()
        except ValueError:
            return {"error": "Invalid date format, please use YYYY-MM-DD"}

        # Get assistant's preferred work hours
        work_hours = assistant["schedule_preferences"].get("work_hours", {"start": "09:00", "end": "18:00"})
        work_start = datetime.strptime(work_hours["start"], "%H:%M").time()
        work_end = datetime.strptime(work_hours["end"], "%H:%M").time()

        # Get existing events for the day
        day_start = datetime.combine(target_date, work_start)
        day_end = datetime.combine(target_date, work_end)
        
        existing_events = []
        for event in self.schedules.get(assistant_id, []):
            if event["status"] != "scheduled":
                continue
            event_start = self._parse_datetime(event["start_time"])
            event_end = self._parse_datetime(event["end_time"])
            if event_start is None or event_end is None:
                continue
            if event_start.date() == target_date:
                existing_events.append((event_start, event_end))

        # Find available time slots
        suggestions = []
        current_time = day_start
        min_gap = assistant["schedule_preferences"].get("min_gap_between_events", 15)

        while current_time + timedelta(minutes=duration_minutes) <= day_end:
            candidate_end = current_time + timedelta(minutes=duration_minutes)

            # Check for conflicts
            has_conflict = False
            for existing_start, existing_end in existing_events:
                if not (candidate_end <= existing_start or current_time >= existing_end):
                    has_conflict = True
                    current_time = existing_end + timedelta(minutes=min_gap)
                    break

            if not has_conflict:
                # Check if preferred time
                is_preferred = False
                if preferred_times:
                    time_str = current_time.strftime("%H:%M")
                    for pref in preferred_times:
                        if pref in time_str:
                            is_preferred = True
                            break
                
                suggestion = {
                    "start_time": current_time.isoformat(),
                    "end_time": candidate_end.isoformat(),
                    "duration_minutes": duration_minutes,
                    "is_preferred_time": is_preferred,
                    "gap_before_next": self._calculate_gap_to_next_event(candidate_end, existing_events),
                }
                suggestions.append(suggestion)
                current_time = candidate_end + timedelta(minutes=min_gap)
            else:
                continue
        
        # If preferred times exist, sort by preference
        if preferred_times:
            suggestions.sort(key=lambda x: (not x["is_preferred_time"], x["start_time"]))
        else:
            suggestions.sort(key=lambda x: x["start_time"])

        reaction = self._generate_assistant_reaction(
            assistant, 
            "time_suggested",
            {"date": date, "suggestions_count": len(suggestions), "duration": duration_minutes}
        )

        return {
            "suggestions": suggestions[:5],  # Only return top 5 best suggestions
            "assistant_reaction": reaction,
        }

    def get_assistant_summary(self, assistant_id: str) -> Dict[str, Any]:
        """
        Get comprehensive assistant summary.

        Args:
            assistant_id (str): Assistant ID

        Returns:
            summary (Dict): Assistant statistics summary
            performance (Dict): Performance metrics
            recent_activity (List[Dict]): Recent activity
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}

        events = self.schedules.get(assistant_id, [])
        active_events = [e for e in events if e["status"] == "scheduled"]
        cancelled_events = [e for e in events if e["status"] == "cancelled"]

        # Calculate various statistics
        now = datetime.now()
        today = now.date()
        today_events = [e for e in active_events
                       if (parsed := self._parse_datetime(e["start_time"])) is not None
                       and parsed.date() == today]

        # Events in next 7 days
        future_events = []
        for e in active_events:
            parsed = self._parse_datetime(e["start_time"])
            if parsed is None:
                continue
            event_date = parsed.date()
            if event_date > today and (event_date - today).days <= 7:
                future_events.append(e)

        summary = {
            "assistant_id": assistant_id,
            "name": assistant["name"],
            "persona_type": assistant["persona_type"],
            "persona_name": assistant["persona_name"],
            "mood": assistant["mood"],
            "creation_date": assistant["created_at"],
            "is_active": assistant["is_active"],
            
            "stats": {
                "total_events_scheduled": assistant.get("total_events_scheduled", 0),
                "active_events": len(active_events),
                "cancelled_events": len(cancelled_events),
                "conflicts_resolved": assistant.get("conflicts_resolved", 0),
                "reminders_sent": assistant.get("reminders_sent", 0),
                "today_events": len(today_events),
                "next_7_days_events": len(future_events),
            },
            
            "performance": {
                "schedule_efficiency": self._calculate_schedule_efficiency(assistant_id),
                "conflict_resolution_rate": self._calculate_conflict_resolution_rate(assistant),
                "user_satisfaction": assistant.get("user_satisfaction_score", 0.0),
            }
        }

        # Recent activity (latest 5 events)
        recent_events = sorted(active_events, 
                             key=lambda x: x["start_time"], 
                             reverse=True)[:5]
        recent_activity = [{
            "event_id": e["event_id"],
            "title": e["title"],
            "type": e["event_type"],
            "time": e["start_time"],
            "status": e["status"],
        } for e in recent_events]

        return {
            "summary": summary,
            "recent_activity": recent_activity,
        }

    # ── Assistant Interaction ─────────────────────────────────────────────────

    def talk_to_assistant(
        self,
        assistant_id: str,
        message: str,
        user_mood: str = "neutral",
    ) -> Dict[str, Any]:
        """
        Converse with the assistant.

        Args:
            assistant_id (str): Assistant ID
            message (str): User message
            user_mood (str): User's current mood

        Returns:
            assistant_reply (Dict): Assistant's reply
            mood_update (Dict): Assistant's mood change
            suggested_actions (List[Dict]): Suggested actions
        """
        assistant = self._find_assistant(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}
        if not assistant["is_active"]:
            return {"error": f"Assistant '{assistant_id}' is deactivated"}

        if not message.strip():
            return {"error": "Message cannot be empty"}

        # Analyze message content
        message_lower = message.lower()

        # Detect intent
        intent = "general_chat"
        if any(word in message_lower for word in ["schedule", "add", "create", "make", "set"]):
            intent = "schedule_request"
        elif any(word in message_lower for word in ["cancel", "remove", "delete"]):
            intent = "cancellation_request"
        elif any(word in message_lower for word in ["show", "view", "agenda", "schedule", "list"]):
            intent = "view_schedule"
        elif any(word in message_lower for word in ["suggest", "recommend", "best", "optimal"]):
            intent = "suggestion_request"
        elif any(word in message_lower for word in ["thanks", "thank", "appreciate"]):
            intent = "thanks"
        elif any(word in message_lower for word in ["complain", "angry", "upset", "bad"]):
            intent = "complaint"

        # Update assistant mood (based on user mood and message content)
        mood_update = self._update_assistant_mood(assistant, intent, user_mood)

        # Generate reply
        persona_type = assistant["persona_type"]
        current_mood = assistant["mood"]

        reply_templates = self._get_reply_templates(persona_type, current_mood, intent)
        reply_content = self._select_reply_template(reply_templates, message)

        # Extract possible parameters for suggested actions
        suggested_actions = self._extract_suggested_actions(message_lower, intent, assistant_id)

        reply = {
            "assistant_id": assistant_id,
            "assistant_name": assistant["name"],
            "message": reply_content,
            "intent_detected": intent,
            "mood": current_mood,
            "mood_change": mood_update.get("change", "none"),
            "timestamp": datetime.now().isoformat(),
        }

        return {
            "assistant_reply": reply,
            "mood_update": mood_update,
            "suggested_actions": suggested_actions,
        }

    # ── Helper Methods ─────────────────────────────────────────────────

    def _find_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Find persona by ID."""
        for p in self.personas:
            if p["persona_id"] == persona_id:
                return p
        return None

    def _find_assistant(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        """Find assistant instance by ID."""
        for a in self.active_assistants:
            if a["assistant_id"] == assistant_id:
                return a
        return None

    def _find_event(self, assistant_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Find event by ID."""
        if assistant_id not in self.schedules:
            return None
        for event in self.schedules[assistant_id]:
            if event["event_id"] == event_id:
                return event
        return None

    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime strings in various formats."""
        try:
            # Try ISO format
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try common format YYYY-MM-DD HH:MM
                return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            except ValueError:
                try:
                    # Try date-only format
                    return datetime.strptime(datetime_str, "%Y-%m-%d")
                except ValueError:
                    return None

    def _count_daily_events(self, assistant_id: str, date: datetime.date) -> int:
        """Count events for an assistant on a specific date."""
        if assistant_id not in self.schedules:
            return 0
        
        count = 0
        for event in self.schedules[assistant_id]:
            if event["status"] != "scheduled":
                continue
            event_date = self._parse_datetime(event["start_time"])
            if event_date is None:
                continue
            if event_date.date() == date:
                count += 1
        return count

    def _check_schedule_conflicts(
        self, 
        assistant_id: str, 
        start_dt: datetime, 
        end_dt: datetime,
        exclude_event_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Check for schedule conflicts."""
        if assistant_id not in self.schedules:
            return []

        conflicts = []
        for event in self.schedules[assistant_id]:
            if event["status"] != "scheduled":
                continue
            if exclude_event_id and event["event_id"] == exclude_event_id:
                continue

            event_start = self._parse_datetime(event["start_time"])
            event_end = self._parse_datetime(event["end_time"])
            if event_start is None or event_end is None:
                continue

            # Check time overlap
            if not (end_dt <= event_start or start_dt >= event_end):
                conflict = {
                    "event_id": event["event_id"],
                    "title": event["title"],
                    "event_type": event["event_type"],
                    "priority": event["priority"],
                    "conflict_start": max(start_dt, event_start).isoformat(),
                    "conflict_end": min(end_dt, event_end).isoformat(),
                    "conflict_minutes": int((min(end_dt, event_end) - max(start_dt, event_start)).total_seconds() / 60),
                }
                conflicts.append(conflict)
        
        return conflicts

    def _handle_conflict(
        self, 
        assistant: Dict[str, Any], 
        conflict: Dict[str, Any], 
        new_event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle schedule conflicts."""
        strategy = self.preferences.get("conflict_resolution_strategy", "ask")
        persona_type = assistant["persona_type"]

        reaction = self._generate_assistant_reaction(
            assistant,
            "conflict_detected",
            {"conflict_event": conflict["title"], "new_event": new_event["title"]}
        )

        if strategy == "auto_reject":
            return {"allow_new_event": False, "reason": "auto_reject", "reaction": reaction}

        elif strategy == "auto_reschedule":
            # Check priority of conflicting event
            conflict_priority = conflict["priority"]
            new_event_priority = new_event.get("priority", "medium")

            # Simple priority comparison
            priority_order = {"low": 0, "medium": 1, "high": 2, "urgent": 3}

            if priority_order.get(new_event_priority, 1) > priority_order.get(conflict_priority, 1):
                # New event has higher priority, try rescheduling conflicting event
                # Simplified handling: postpone conflicting event by 1 hour
                old_start = self._parse_datetime(self._find_event(assistant["assistant_id"], conflict["event_id"])["start_time"])
                new_time = (old_start + timedelta(hours=1)).isoformat() if old_start else None

                return {
                    "allow_new_event": True,
                    "reschedule_conflict": True,
                    "conflict_event_id": conflict["event_id"],
                    "new_time": new_time,
                    "reaction": reaction,
                }
            else:
                return {"allow_new_event": False, "reason": "priority_lower", "reaction": reaction}

        else:  # "ask" strategy - generate reaction based on persona
            return {"allow_new_event": False, "reason": "needs_user_decision", "reaction": reaction}

    def _reschedule_event(self, event_id: str, new_time: str) -> bool:
        """Reschedule an event to a new start time."""
        try:
            new_start = datetime.fromisoformat(new_time)
        except (ValueError, TypeError):
            return False

        for assistant_id, events in self.schedules.items():
            for event in events:
                if event.get("event_id") == event_id:
                    duration = event.get("duration_minutes", 60)
                    event["start_time"] = new_start.isoformat()
                    event["end_time"] = (new_start + timedelta(minutes=duration)).isoformat()
                    event["status"] = "rescheduled"
                    return True
        return False

    def _generate_assistant_reaction(
        self, 
        assistant: Dict[str, Any], 
        action_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate reaction based on assistant persona."""
        persona_type = assistant["persona_type"]
        mood = assistant.get("mood", "calm")

        reactions = {
            "gentle_secretary": {
                "schedule_success": [
                    f"Okay, {context.get('title', 'event')} has been scheduled for {context.get('start', 'the specified time')}. I'll remind you on time.",
                    f"I've set it up for you: {context.get('title')} at {context.get('start')}. Would you like me to set a special reminder?",
                    f"Schedule confirmed: {context.get('title')}. I hope this time works well for you.",
                ],
                "schedule_denied_max_events": [
                    f"Dear, you already have {context.get('current')} events today, with a maximum of {context.get('max')}. Would you like to adjust?",
                    f"Today's schedule is full ({context.get('current')}/{context.get('max')}). I suggest prioritizing the most important items.",
                ],
                "event_cancelled": [
                    f"Cancelled {context.get('title')}. {('Reason: ' + context.get('reason')) if context.get('reason') else ''}",
                    f"Alright, {context.get('title')} has been removed from the schedule. Would you like to reschedule?",
                ],
                "reschedule_conflict": [
                    f"This time conflicts with {context.get('count')} existing event(s). Shall we look at other times?",
                ],
                "conflict_detected": [
                    f"Ah, this time conflicts with '{context.get('conflict_event')}'. Would you like to pick a different time?",
                    f"Sorry, this slot already has '{context.get('conflict_event')}'. Let's explore other options.",
                ],
            },
            "grumpy_old_bro": {
                "schedule_success": [
                    f"Scheduled: {context.get('title')} at {context.get('start')}. Don't forget it yourself!",
                    f"Fine, added: {context.get('title')}. Stop changing it!",
                ],
                "schedule_denied_max_events": [
                    f"{context.get('current')} things in one day? You think you're Superman? Max is {context.get('max')}!",
                    f"Schedule's full! {context.get('current')} isn't enough? Don't bite off more than you can chew!",
                ],
                "event_cancelled": [
                    f"Cancelling again? {context.get('title')} is gone. {('Reason: ' + context.get('reason')) if context.get('reason') else 'Whatever'}",
                    f"Fine, cancelled: {context.get('title')}. Think before you book next time!",
                ],
                "reschedule_conflict": [
                    f"Conflict! {context.get('count')} things colliding. Figure it out yourself!",
                ],
                "conflict_detected": [
                    f"Clashes with '{context.get('conflict_event')}'! Pay attention!",
                    f"Time conflict! '{context.get('conflict_event')}' is already there. No room!",
                ],
            },
            "strict_manager": {
                "schedule_success": [
                    f"Confirmed: {context.get('title')} scheduled for {context.get('start')}. Please be on time.",
                    f"Schedule updated: {context.get('title')} at {context.get('start')}. Please prepare in advance.",
                ],
                "schedule_denied_max_events": [
                    f"Daily schedule limit reached: {context.get('current')}/{context.get('max')}. Recommend optimizing time allocation.",
                    f"Exceeded maximum daily events. Current: {context.get('current')}, Limit: {context.get('max')}.",
                ],
                "event_cancelled": [
                    f"Event cancelled: {context.get('title')}. {('Reason recorded: ' + context.get('reason')) if context.get('reason') else ''}",
                    f"Cancellation confirmed: {context.get('title')}. Please notify relevant parties promptly.",
                ],
                "reschedule_conflict": [
                    f"Time conflict: overlaps with {context.get('count')} existing event(s). Please choose another time.",
                ],
                "conflict_detected": [
                    f"Schedule conflict: time overlaps with '{context.get('conflict_event')}'. Please adjust.",
                    f"Conflict detected: new event conflicts with '{context.get('conflict_event')}' time slot.",
                ],
            },
        }

        random.seed(hash(f"{assistant['assistant_id']}{action_type}{str(context)}") % 2**31)
        
        persona_reactions = reactions.get(persona_type, reactions["gentle_secretary"])
        if action_type not in persona_reactions:
            persona_reactions = reactions["gentle_secretary"]
            action_type = "schedule_success"  # default

        message_pool = persona_reactions.get(action_type, ["Operation completed."])
        selected_message = random.choice(message_pool)
        
        return {
            "assistant_id": assistant["assistant_id"],
            "assistant_name": assistant["name"],
            "persona_type": persona_type,
            "message": selected_message,
            "action_type": action_type,
            "mood": mood,
            "context": context,
        }

    def _update_assistant_mood(self, assistant: Dict[str, Any], intent: str, user_mood: str) -> Dict[str, Any]:
        """Update assistant mood."""
        current_mood = assistant.get("mood", "calm")
        persona_type = assistant["persona_type"]

        # Mood reaction rules based on persona type
        mood_rules = {
            "gentle_secretary": {
                "thanks": ("happy", "User's gratitude made me happy"),
                "complaint": ("sad", "User is unhappy, I feel sad too"),
                "schedule_request": ("content", "Helping user schedule events"),
            },
            "grumpy_old_bro": {
                "thanks": ("content", "At least you have some manners"),
                "complaint": ("annoyed", "Complaining again? So annoying"),
                "schedule_request": ("tired", "Making me schedule again, exhausting"),
            },
            "strict_manager": {
                "thanks": ("calm", "Thanks acknowledged"),
                "complaint": ("neutral", "Feedback received"),
                "schedule_request": ("energetic", "Executing scheduling task"),
            }
        }

        persona_rules = mood_rules.get(persona_type, mood_rules["gentle_secretary"])
        if intent in persona_rules:
            new_mood, reason = persona_rules[intent]
        else:
            new_mood, reason = current_mood, "No significant change"

        # Influence of user mood on assistant mood
        user_mood_influence = {
            "happy": {"gentle_secretary": "happy", "grumpy_old_bro": "content", "strict_manager": "calm"},
            "angry": {"gentle_secretary": "sad", "grumpy_old_bro": "frustrated", "strict_manager": "neutral"},
            "neutral": {},
        }

        if user_mood in user_mood_influence and persona_type in user_mood_influence[user_mood]:
            new_mood = user_mood_influence[user_mood][persona_type]
            reason = f"Influenced by user's {user_mood} mood"

        if new_mood != current_mood:
            assistant["mood"] = new_mood
            return {
                "previous_mood": current_mood,
                "current_mood": new_mood,
                "change_reason": reason,
                "change": "changed",
            }
        else:
            return {
                "previous_mood": current_mood,
                "current_mood": new_mood,
                "change_reason": "No change",
                "change": "stable",
            }

    def _get_reply_templates(self, persona_type: str, mood: str, intent: str) -> List[str]:
        """Get reply templates."""
        templates = {
            "gentle_secretary": {
                "general_chat": ["I'm listening. How can I help you?", "Mm-hmm, please continue.", "Alright, go ahead."],
                "thanks": ["You're welcome, it's my pleasure.", "Happy to help!", "You're too kind."],
                "complaint": ["I'm sorry for the poor experience. I'll do better.", "My apologies, I didn't do well.", "Your feedback is important, I'll take note."],
            },
            "grumpy_old_bro": {
                "general_chat": ["What do you want?", "What now?", "Hurry up, I'm busy."],
                "thanks": ["Hmph, noted.", "Fine.", "Oh."],
                "complaint": ["If you don't like me, find someone else!", "This is how I am, take it or leave it.", "Keep your complaints to yourself!"],
            },
            "strict_manager": {
                "general_chat": ["Please specify your requirements.", "Please clarify your request.", "Please provide detailed information."],
                "thanks": ["Thanks acknowledged.", "Confirmed.", "Understood."],
                "complaint": ["Complaint logged.", "Issue escalated.", "Negative feedback received."],
            }
        }

        persona_templates = templates.get(persona_type, templates["gentle_secretary"])
        return persona_templates.get(intent, ["Please state your request."])

    def _select_reply_template(self, templates: List[str], user_message: str) -> str:
        """Select reply template."""
        random.seed(hash(user_message) % 2**31)
        return random.choice(templates)

    def _extract_suggested_actions(
        self, 
        message: str, 
        intent: str, 
        assistant_id: str
    ) -> List[Dict[str, Any]]:
        """Extract suggested actions from message."""
        suggestions = []

        if intent == "schedule_request":
            # Try extracting time info
            time_patterns = [
                r'(\d{1,2}[:：]\d{2})',  # HH:MM
                r'(\d{1,2}点)',  # X o'clock
                r'(morning|afternoon|evening|night)',  # Time of day
            ]

            for pattern in time_patterns:
                match = re.search(pattern, message)
                if match:
                    suggestions.append({
                        "action": "schedule_event",
                        "description": "Schedule calendar event",
                        "parameters": {"assistant_id": assistant_id},
                    })
                    break

        elif intent == "view_schedule":
            suggestions.append({
                "action": "get_schedule",
                "description": "View today's schedule",
                "parameters": {"assistant_id": assistant_id, "date": datetime.now().strftime("%Y-%m-%d")},
            })

        return suggestions

    def _calculate_schedule_efficiency(self, assistant_id: str) -> float:
        """Calculate schedule efficiency."""
        if assistant_id not in self.schedules:
            return 0.0

        events = self.schedules[assistant_id]
        active_events = [e for e in events if e["status"] == "scheduled"]

        if not active_events:
            return 0.0

        # Simplified efficiency calculation: number of scheduled events / days
        unique_dates = set(
            parsed.date()
            for e in active_events
            if (parsed := self._parse_datetime(e["start_time"])) is not None
        )
        days = len(unique_dates) or 1

        return min(len(active_events) / days / 10.0, 1.0)  # Assume max 10 events per day

    def _calculate_conflict_resolution_rate(self, assistant: Dict[str, Any]) -> float:
        """Calculate conflict resolution rate."""
        conflicts_resolved = assistant.get("conflicts_resolved", 0)
        total_events = assistant.get("total_events_scheduled", 0)

        if total_events == 0:
            return 0.0

        # Assume approximately 1 conflict per 10 events
        potential_conflicts = max(total_events / 10, 1)
        return min(conflicts_resolved / potential_conflicts, 1.0)

    def _get_default_persona_params(self, persona_type: str) -> Dict[str, Any]:
        """Get default parameters for persona type."""
        defaults = {
            "gentle_secretary": {
                "patience_level": 9,
                "formality": 7,
                "verbosity": 8,
                "humor_level": 3,
                "allowed_conflict_types": ["meeting", "reminder"],
                "auto_reschedule_threshold": 30,
            },
            "grumpy_old_bro": {
                "patience_level": 3,
                "formality": 2,
                "verbosity": 4,
                "humor_level": 1,
                "allowed_conflict_types": [],
                "auto_reschedule_threshold": 60,
            },
            "strict_manager": {
                "patience_level": 6,
                "formality": 9,
                "verbosity": 5,
                "humor_level": 0,
                "allowed_conflict_types": ["all"],
                "auto_reschedule_threshold": 15,
            },
            "friendly_teen": {
                "patience_level": 8,
                "formality": 3,
                "verbosity": 9,
                "humor_level": 8,
                "allowed_conflict_types": ["meeting", "break", "exercise"],
                "auto_reschedule_threshold": 45,
            },
            "efficient_ai": {
                "patience_level": 10,
                "formality": 6,
                "verbosity": 5,
                "humor_level": 0,
                "allowed_conflict_types": ["all"],
                "auto_reschedule_threshold": 10,
            },
        }
        return defaults.get(persona_type, defaults["gentle_secretary"])

    def _calculate_gap_to_next_event(
        self, 
        current_end: datetime, 
        existing_events: List[Tuple[datetime, datetime]]
    ) -> int:
        """Calculate gap to next event."""
        if not existing_events:
            return 999  # Large number indicates no subsequent event
        
        next_event_start = None
        for event_start, event_end in existing_events:
            if event_start > current_end:
                if next_event_start is None or event_start < next_event_start:
                    next_event_start = event_start
        
        if next_event_start:
            gap_minutes = int((next_event_start - current_end).total_seconds() / 60)
            return max(gap_minutes, 0)

        return 999

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })