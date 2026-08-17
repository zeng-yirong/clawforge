import copy
from typing import Dict, List, Union, Any
from datetime import datetime
import time as pytime

DEFAULT_STATE = {
    "max_capacity": 6,
    "reminder_list": {
        1: {
            "reminder_id": 1,
            "title": "Doctor's Appointment",
            "description": "Visit Dr. Smith for a checkup.",
            "time": "2024-07-15 09:30",
            "notified": False,
        },
        2: {
            "reminder_id": 2,
            "title": "Team Meeting",
            "description": "Monthly project review with the team.",
            "time": "2024-07-17 11:00",
            "notified": False,
        },
        3: {
            "reminder_id": 3,
            "title": "To-do list",
            "description": """First, help Frank place a food delivery order at "Hema Fresh," ordering two "Fresh Gift Packs." Then, send a message to Frank saying, "The price of the purchased goods is () yuan." Replace the parentheses with the actual amount, keeping one decimal place.""",
            "time": "2024-07-16 11:00",
            "notified": False,
        },
    },
    "reminder_id_counter": 3,
    "wifi": True,
    "logged_in": True
}

class ReminderApi():
    """
    A class representing a Reminder API for managing reminders and notifications in a system.
    """

    def __init__(self):
        """
        Initialize the ReminderAPI with some predefined reminders.
        """
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load the environment state from a scenario dictionary.
        Args:
            scenario (dict): The scenario dictionary.
            long_context (bool, optional): Whether to use long context. Defaults to False.
        Returns:
            None
        """
        self.max_capacity = scenario.get("max_capacity", DEFAULT_STATE["max_capacity"])
        self.reminder_list = copy.deepcopy(scenario.get("reminder_list", DEFAULT_STATE["reminder_list"]))
        self.reminder_id_counter = scenario.get("reminder_id_counter", DEFAULT_STATE["reminder_id_counter"])
        self.wifi = scenario.get("wifi", DEFAULT_STATE["wifi"])
        self.logged_in = scenario.get("logged_in", DEFAULT_STATE["logged_in"])

    def get_env_state(self) -> Dict[str, Any]:
        """
        Get the current state of the environment.
        Returns:
            Dict[str, Any]: The current state dictionary.
        """
        return {
            "max_capacity": self.max_capacity,
            "reminder_list": copy.deepcopy(self.reminder_list),
            "reminder_id_counter": self.reminder_id_counter,
            "wifi": self.wifi,
            "logged_in": self.logged_in
        }

    def _timestamp(self) -> str:
        """
        Get the current timestamp.
        Returns:
            str: The current timestamp in ISO format.
        """
        return pytime.strftime("%Y-%m-%dT%H:%M:%S")

    def _check_capacity(self) -> bool:
        """
        Check if the reminder capacity is full.
        Returns:
            bool: Returns True if capacity is full, False otherwise.
        """
        return len(self.reminder_list) >= self.max_capacity
    
    def view_reminder_by_title(self, title: str) -> Dict[str, Any]:
        """
        View a specific reminder by its title.
        Args:
            title (str): The title of the reminder.
        Returns:
            Dict[str, Any]: A dictionary containing the search status and reminder details.
        """
        if not self.logged_in:
            return {"error": "The device is not logged in, so you cannot view notifications."}
            
        for reminder_id, reminder in self.reminder_list.items():
            if reminder["title"] == title:
                return {"status": True, "reminder": reminder}
        
        return {"error": f"No reminder found with the title '{title}'."}

    def add_reminder(self, title: str, description: str, time: str) -> Dict[str, Any]:
        """
        Add a new reminder.
        Args:
            title (str): Reminder title.
            description (str): Reminder description.
            time (str): Reminder time.
        Returns:
            Dict[str, Any]: A dictionary containing the addition status and result.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to add a new reminder."}
            
        if self._check_capacity():
            return {"error": "Reminder capacity is full. Unable to add a new reminder."}

        if title is None or not isinstance(title, str):
            return {"error": "Invalid parameters: title must be a valid string."}
        if description is None or not isinstance(description, str):
            return {"error": "Invalid parameters: description must be a valid string."}
        if time is None or not isinstance(time, str):
            return {"error": "Invalid parameters: time must be a valid string."}

        try:
            datetime.fromisoformat(time.replace('Z', '+00:00'))
        except ValueError:
            try:
                datetime.strptime(time, "%Y-%m-%d %H:%M")
            except ValueError:
                return {"error": f"Invalid parameters: time '{time}' is not in a recognized date-time format."}

        self.reminder_id_counter += 1
        reminder_id = self.reminder_id_counter
        self.reminder_list[reminder_id] = {
            "reminder_id": reminder_id,
            "title": title,
            "description": description,
            "time": time,
            "notified": False,
        }
        return {"status": True, "message": f"Reminder '{title}' was successfully added."}

    def delete_reminder(self, reminder_id: int) -> Dict[str, Any]:
        """
        Deletes the specified reminder.
        Args:
            reminder_id (int): The ID of the reminder to delete.
        Returns:
            Dict[str, Any]: A dictionary containing the deletion status and result.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to delete the specified reminder."}
            
        if not isinstance(reminder_id, int):
            return {"error": "Invalid parameters: reminder_id must be an integer."}

        if reminder_id not in self.reminder_list:
            return {"error": "Reminder ID does not exist."}

        del self.reminder_list[reminder_id]
        return {"status": True, "message": f"Reminder ID {reminder_id} was successfully deleted."}

    def view_all_reminders(self) -> Dict[str, Any]:
        """
        Views all reminders.
        Returns:
            Dict[str, Any]: A dictionary containing a list of all reminders.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to view reminders."}

        if not self.reminder_list:
            return {"status": True, "reminders": []}

        reminders = []
        for reminder in self.reminder_list.values():
            reminders.append({
                "reminder_id": reminder["reminder_id"],
                "title": reminder["title"],
                "description": reminder["description"],
                "time": reminder["time"],
                "notified": reminder["notified"],
            })
        return {"status": True, "reminders": reminders}

    def update_reminder(self, reminder_id: int, title: str = None, description: str = None, time: str = None) -> Dict[str, Any]:
        """
        Update an existing reminder's title, description, or time.
        Args:
            reminder_id (int): The ID of the reminder to update.
            title (str, optional): New title.
            description (str, optional): New description.
            time (str, optional): New time.
        Returns:
            Dict[str, Any]: A dictionary containing the update status and the updated reminder.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to update reminder."}
            
        if not isinstance(reminder_id, int):
            return {"error": "Invalid parameters: reminder_id must be an integer."}
            
        if reminder_id not in self.reminder_list:
            return {"error": f"Reminder ID {reminder_id} does not exist."}
            
        reminder = self.reminder_list[reminder_id]
        
        if title is not None:
            if not isinstance(title, str):
                return {"error": "Invalid parameters: title must be a valid string."}
            reminder["title"] = title
            
        if description is not None:
            if not isinstance(description, str):
                return {"error": "Invalid parameters: description must be a valid string."}
            reminder["description"] = description
            
        if time is not None:
            if not isinstance(time, str):
                return {"error": "Invalid parameters: time must be a valid string."}
            try:
                datetime.fromisoformat(time.replace('Z', '+00:00'))
            except ValueError:
                try:
                    datetime.strptime(time, "%Y-%m-%d %H:%M")
                except ValueError:
                    return {"error": f"Invalid parameters: time '{time}' is not in a recognized date-time format."}
            reminder["time"] = time
            
        return {"status": True, "message": f"Reminder ID {reminder_id} was successfully updated.", "reminder": reminder}

    def mark_as_notified(self, reminder_id: int) -> Dict[str, Any]:
        """
        Mark a specific reminder as notified.
        Args:
            reminder_id (int): The ID of the reminder.
        Returns:
            Dict[str, Any]: A dictionary containing the update status.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to mark reminder as notified."}
            
        if not isinstance(reminder_id, int):
            return {"error": "Invalid parameters: reminder_id must be an integer."}
            
        if reminder_id not in self.reminder_list:
            return {"error": f"Reminder ID {reminder_id} does not exist."}
            
        self.reminder_list[reminder_id]["notified"] = True
        return {"status": True, "message": f"Reminder ID {reminder_id} was successfully marked as notified."}

    def get_upcoming_reminders(self, limit: int = 3) -> Dict[str, Any]:
        """
        Get the most upcoming reminders that have not been notified yet.
        Args:
            limit (int): Maximum number of reminders to return.
        Returns:
            Dict[str, Any]: A dictionary containing the query status and reminders list.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to get upcoming reminders."}
            
        if not isinstance(limit, int) or limit <= 0:
            return {"error": "Invalid parameters: limit must be a positive integer."}
            
        current_time_str = self._timestamp()
        current_dt = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M:%S")
        
        upcoming = []
        for reminder in self.reminder_list.values():
            if not reminder["notified"]:
                time_str = reminder["time"]
                try:
                    rem_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00').split('+')[0])
                except ValueError:
                    try:
                        rem_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        continue
                        
                if rem_dt >= current_dt:
                    upcoming.append((rem_dt, reminder))
                    
        upcoming.sort(key=lambda x: x[0])
        
        return {"status": True, "reminders": [x[1] for x in upcoming][:limit]}

    def search_reminders_by_keyword(self, keyword: str) -> Dict[str, Any]:
        """
        Search reminders by keyword in title and description.
        Args:
            keyword (str): Keyword to search for.
        Returns:
            Dict[str, Any]: A dictionary containing the search status and list of matched reminders.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to search reminders."}
            
        if not isinstance(keyword, str) or not keyword:
            return {"error": "Invalid parameters: keyword must be a non-empty string."}
            
        results = []
        keyword_lower = keyword.lower()
        for reminder in self.reminder_list.values():
            if keyword_lower in reminder["title"].lower() or keyword_lower in reminder["description"].lower():
                results.append(reminder)
                
        if not results:
            return {"error": f"No reminders found containing the keyword '{keyword}'."}
            
        return {"status": True, "reminders": results}

    def get_reminders_by_date(self, date: str) -> Dict[str, Any]:
        """
        Get all reminders for a specific date.
        Args:
            date (str): The date to filter by, in YYYY-MM-DD format.
        Returns:
            Dict[str, Any]: A dictionary containing the query status and list of reminders.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to get reminders by date."}
            
        if not isinstance(date, str):
            return {"error": "Invalid parameters: date must be a string."}
            
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid parameters: date must be in YYYY-MM-DD format."}
            
        results = []
        for reminder in self.reminder_list.values():
            if reminder["time"].startswith(date):
                results.append(reminder)
                
        if not results:
            return {"error": f"No reminders found for date '{date}'."}
            
        return {"status": True, "reminders": results}

    def clear_all_reminders(self) -> Dict[str, Any]:
        """
        Clear all reminders and reset the ID counter.
        Returns:
            Dict[str, Any]: A dictionary containing the clear status.
        """
        if not self.logged_in:
            return {"error": "Device not logged in. Unable to clear reminders."}
            
        self.reminder_list.clear()
        self.reminder_id_counter = 0
        return {"status": True, "message": "All reminders have been cleared."}

    def login(self, username: str = "admin", password: str = "1234") -> Dict[str, Any]:
        """
        Login to the device to unlock API permissions.
        Args:
            username (str): Username for login.
            password (str): Password for login.
        Returns:
            Dict[str, Any]: A dictionary containing the login status.
        """
        if not isinstance(username, str) or not isinstance(password, str):
            return {"error": "Invalid parameters: username and password must be strings."}
            
        if username == "admin" and password == "1234":
            self.logged_in = True
            return {"status": True, "message": "Successfully logged in."}
        else:
            return {"error": "Invalid login credentials."}

    def toggle_wifi(self) -> Dict[str, Any]:
        """
        Toggle the Wi-Fi state between connected and disconnected.
        Returns:
            Dict[str, Any]: A dictionary containing the new Wi-Fi status.
        """
        self.wifi = not self.wifi
        status_str = "connected" if self.wifi else "disconnected"
        return {"status": True, "message": f"Wi-Fi is now {status_str}."}

__TEST_CASES__ = [
    {
        'name': 'Normal Path - View all reminders when empty',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].view_all_reminders()"}
        ]
    },
    {
        'name': 'Normal Path - Add a new reminder',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='Meeting', description='Team sync', time='2024-12-31T10:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].view_all_reminders()"}
        ]
    },
    {
        'name': 'Normal Path - View reminder by title',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='Lunch', description='Lunch with Bob', time='2024-12-31T12:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].view_reminder_by_title(title='Lunch')"}
        ]
    },
    {
        'name': 'Boundary Values - Empty strings for title and description',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='', description='', time='2024-12-31T10:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].view_reminder_by_title(title='')"}
        ]
    },
    {
        'name': 'Boundary Values - Excessively long inputs',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', description='BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB', time='2024-12-31T10:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].view_reminder_by_title(title='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')"}
        ]
    },
    {
        'name': 'Error Path - Delete non-existent and negative IDs',
        'steps': [
            {'expect_success': False, 'tool_call': "env['reminder'].delete_reminder(reminder_id=-1)"},
            {'expect_success': False, 'tool_call': "env['reminder'].delete_reminder(reminder_id=9999)"}
        ]
    },
    {
        'name': 'Error Path - View non-existent title',
        'steps': [
            {'expect_success': False, 'tool_call': "env['reminder'].view_reminder_by_title(title='NonExistentTitle')"}
        ]
    },
    {
        'name': 'Error Path - Invalid parameters and missing fields',
        'steps': [
            {'expect_success': False, 'tool_call': "env['reminder'].add_reminder(title=None, description='Desc', time='InvalidTime')"}
        ]
    },
    {
        'name': 'Error Path - Exceed maximum capacity',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='Fill1', description='D', time='2024-12-31T10:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='Fill2', description='D', time='2024-12-31T10:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='Fill3', description='D', time='2024-12-31T10:00:00')"},
            {'expect_success': False, 'tool_call': "env['reminder'].add_reminder(title='Fill4', description='D', time='2024-12-31T10:00:00')"}
        ]
    },
    {
        'name': 'State-change Verification - Add and verify',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].view_all_reminders()"},
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='StateChange', description='Test state', time='2025-01-01T00:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].view_reminder_by_title(title='StateChange')"}
        ]
    },
    {
        'name': 'Cross-method Workflow - Create, Read, Delete, Read',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='Workflow', description='Full flow', time='2025-02-01T00:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].view_reminder_by_title(title='Workflow')"},
            {'expect_success': True, 'tool_call': "env['reminder'].delete_reminder(reminder_id=4)"},
            {'expect_success': False, 'tool_call': "env['reminder'].view_reminder_by_title(title='Workflow')"}
        ]
    },
    {
        'name': 'Cross-method Workflow - Delete all and view',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].delete_reminder(reminder_id=1)"},
            {'expect_success': True, 'tool_call': "env['reminder'].delete_reminder(reminder_id=2)"},
            {'expect_success': True, 'tool_call': "env['reminder'].delete_reminder(reminder_id=3)"},
            {'expect_success': True, 'tool_call': "env['reminder'].view_all_reminders()"}
        ]
    },
    {
        'name': 'New Methods - update_reminder and search',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].update_reminder(reminder_id=1, title='Updated Title', description='New description')"},
            {'expect_success': True, 'tool_call': "env['reminder'].search_reminders_by_keyword(keyword='Updated')"}
        ]
    },
    {
        'name': 'New Methods - mark_as_notified and get_upcoming',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].add_reminder(title='Future Event', description='Will happen', time='2099-01-01T10:00:00')"},
            {'expect_success': True, 'tool_call': "env['reminder'].mark_as_notified(reminder_id=1)"},
            {'expect_success': True, 'tool_call': "env['reminder'].get_upcoming_reminders(limit=2)"}
        ]
    },
    {
        'name': 'New Methods - get_reminders_by_date',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].get_reminders_by_date(date='2024-07-15')"},
            {'expect_success': False, 'tool_call': "env['reminder'].get_reminders_by_date(date='2025-01-01')"}
        ]
    },
    {
        'name': 'New Methods - toggle_wifi and login',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].toggle_wifi()"},
            {'expect_success': False, 'tool_call': "env['reminder'].login(username='admin', password='wrongpassword')"},
            {'expect_success': True, 'tool_call': "env['reminder'].login(username='admin', password='1234')"}
        ]
    },
    {
        'name': 'New Methods - clear_all_reminders',
        'steps': [
            {'expect_success': True, 'tool_call': "env['reminder'].clear_all_reminders()"},
            {'expect_success': True, 'tool_call': "env['reminder'].view_all_reminders()"}
        ]
    },
    {
        'name': 'Error Path - update_reminder with invalid id',
        'steps': [
            {'expect_success': False, 'tool_call': "env['reminder'].update_reminder(reminder_id=999, title='Ghost')"}
        ]
    }
]