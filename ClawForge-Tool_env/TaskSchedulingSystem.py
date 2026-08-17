"""
Task Scheduling System Environment API

A task scheduling system that manages the execution of jobs at specified times or intervals,
maintaining state such as job IDs, schedules, statuses, and execution history.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

# Default initial state with sample data
DEFAULT_STATE: Dict[str, Any] = {
    "scheduled_tasks": {
        "task_001": {
            "task_id": "task_001",
            "command": "python /scripts/backup.py",
            "schedule_expression": "0 2 * * *",
            "status": "active",
            "created_at": "2024-01-15T10:00:00",
            "last_run_at": "2024-01-20T02:00:00",
            "next_run_at": "2024-01-21T02:00:00",
            "execution_history": ["exec_001", "exec_002"]
        },
        "task_002": {
            "task_id": "task_002",
            "command": "bash /scripts/cleanup.sh",
            "schedule_expression": "0 0 * * 0",
            "status": "pending",
            "created_at": "2024-01-16T14:30:00",
            "last_run_at": None,
            "next_run_at": "2024-01-21T00:00:00",
            "execution_history": []
        },
        "task_003": {
            "task_id": "task_003",
            "command": "python /scripts/report.py",
            "schedule_expression": "0 9 * * 1-5",
            "status": "active",
            "created_at": "2024-01-10T08:00:00",
            "last_run_at": "2024-01-19T09:00:00",
            "next_run_at": "2024-01-22T09:00:00",
            "execution_history": ["exec_003", "exec_004", "exec_005"]
        },
        "task_004": {
            "task_id": "task_004",
            "command": "python /scripts/sync.py",
            "schedule_expression": "*/30 * * * *",
            "status": "inactive",
            "created_at": "2024-01-05T12:00:00",
            "last_run_at": "2024-01-18T15:30:00",
            "next_run_at": None,
            "execution_history": ["exec_006"]
        }
    },
    "execution_records": {
        "exec_001": {
            "record_id": "exec_001",
            "task_id": "task_001",
            "execution_time": "2024-01-19T02:00:00",
            "success": True,
            "log_output": "Backup completed successfully. 150 files processed."
        },
        "exec_002": {
            "record_id": "exec_002",
            "task_id": "task_001",
            "execution_time": "2024-01-20T02:00:00",
            "success": True,
            "log_output": "Backup completed successfully. 152 files processed."
        },
        "exec_003": {
            "record_id": "exec_003",
            "task_id": "task_003",
            "execution_time": "2024-01-17T09:00:00",
            "success": True,
            "log_output": "Daily report generated and emailed."
        },
        "exec_004": {
            "record_id": "exec_004",
            "task_id": "task_003",
            "execution_time": "2024-01-18T09:00:00",
            "success": False,
            "log_output": "Error: Database connection timeout."
        },
        "exec_005": {
            "record_id": "exec_005",
            "task_id": "task_003",
            "execution_time": "2024-01-19T09:00:00",
            "success": True,
            "log_output": "Daily report generated and emailed."
        },
        "exec_006": {
            "record_id": "exec_006",
            "task_id": "task_004",
            "execution_time": "2024-01-18T15:30:00",
            "success": True,
            "log_output": "Data sync completed. 500 records updated."
        }
    },
    "scheduler_system": {
        "system_status": "running",
        "timezone": "UTC",
        "max_concurrent_tasks": 5
    },
    "archived_tasks": {}
}


class TaskSchedulingSystem:
    """
    A task scheduling system environment that manages job execution at specified times or intervals.
    
    This system maintains scheduled tasks, execution history, and system-wide scheduler settings.
    It supports operations like creating, querying, updating, and deleting scheduled tasks.
    """

    def __init__(self) -> None:
        """
        Initialize the TaskSchedulingSystem with default state attributes.
        
        Declares all state attributes with type hints and sets the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self._api_description: str = "A task scheduling system for managing automated job execution at specified times or intervals."
        
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.execution_records: Dict[str, Dict[str, Any]] = {}
        self.scheduler_system: Dict[str, Any] = {}
        self.archived_tasks: Dict[str, Dict[str, Any]] = {}

    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data. If empty or keys missing,
                     falls back to DEFAULT_STATE values.
            long_context: Flag for handling extended context scenarios (reserved for future use).
        
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
        Return the current internal state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all current state variables:
                - scheduled_tasks: All scheduled tasks indexed by task_id
                - execution_records: All execution records indexed by record_id
                - scheduler_system: Global scheduler settings
                - archived_tasks: Tasks that have been archived
        """
        return {
            "scheduled_tasks": deepcopy(self.scheduled_tasks),
            "execution_records": deepcopy(self.execution_records),
            "scheduler_system": deepcopy(self.scheduler_system),
            "archived_tasks": deepcopy(self.archived_tasks)
        }

    # ==================== Query Operations ====================

    def get_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a scheduled task by its task_id.
        
        Args:
            task_id: The unique identifier of the task to retrieve.
            
        Returns:
            Dict[str, Any]: Task details including command, schedule, status, and timing,
                          or an error dict if task not found.
        """
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        return {"task": deepcopy(self.scheduled_tasks[task_id])}

    def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Query the current status of a task.
        
        Args:
            task_id: The unique identifier of the task.
            
        Returns:
            Dict[str, Any]: The task's current status (e.g., active, pending, inactive),
                          or an error dict if task not found.
        """
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        return {
            "task_id": task_id,
            "status": self.scheduled_tasks[task_id]["status"]
        }

    def list_all_tasks(self) -> Dict[str, Any]:
        """
        Retrieve a list of all currently scheduled tasks in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing a list of all tasks with their details.
        """
        tasks = list(self.scheduled_tasks.values())
        return {
            "tasks": deepcopy(tasks),
            "count": len(tasks)
        }

    def list_tasks_by_status(self, status: str) -> Dict[str, Any]:
        """
        Get all tasks filtered by a specific status.
        
        Args:
            status: The status to filter by (e.g., 'active', 'pending', 'inactive').
            
        Returns:
            Dict[str, Any]: A list of tasks matching the specified status.
        """
        valid_statuses = ["active", "pending", "inactive"]
        if status not in valid_statuses:
            return {"error": f"Invalid status '{status}'. Must be one of: {valid_statuses}"}
        
        filtered_tasks = [
            task for task in self.scheduled_tasks.values()
            if task["status"] == status
        ]
        return {
            "tasks": deepcopy(filtered_tasks),
            "status_filter": status,
            "count": len(filtered_tasks)
        }

    def task_exists(self, task_id: str) -> Dict[str, Any]:
        """
        Check whether a task with the given task_id exists in the system.
        
        Args:
            task_id: The unique identifier of the task to check.
            
        Returns:
            Dict[str, Any]: A dictionary indicating whether the task exists.
        """
        exists = task_id in self.scheduled_tasks
        return {
            "task_id": task_id,
            "exists": exists
        }

    def get_execution_history(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve the list of execution records for a given task.
        
        Args:
            task_id: The unique identifier of the task.
            
        Returns:
            Dict[str, Any]: List of execution record IDs and their details,
                          or an error dict if task not found.
        """
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        task = self.scheduled_tasks[task_id]
        history_ids = task.get("execution_history", [])
        
        history_records = []
        for record_id in history_ids:
            if record_id in self.execution_records:
                history_records.append(deepcopy(self.execution_records[record_id]))
        
        return {
            "task_id": task_id,
            "execution_history": history_records,
            "count": len(history_records)
        }

    def get_execution_record(self, record_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information about a specific execution by record_id.
        
        Args:
            record_id: The unique identifier of the execution record.
            
        Returns:
            Dict[str, Any]: Execution record details including time, success status, and log,
                          or an error dict if record not found.
        """
        if record_id not in self.execution_records:
            return {"error": f"Execution record with id '{record_id}' not found"}
        return {"record": deepcopy(self.execution_records[record_id])}

    def get_system_status(self) -> Dict[str, Any]:
        """
        Retrieve the current global state of the scheduler.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: The current system status (e.g., running, paused).
        """
        return {
            "system_status": self.scheduler_system.get("system_status", "unknown")
        }

    def get_scheduler_config(self) -> Dict[str, Any]:
        """
        Get system-wide scheduler settings.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Configuration including timezone and max_concurrent_tasks.
        """
        return {
            "config": deepcopy(self.scheduler_system)
        }

    def get_next_run_time(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve the next scheduled execution time of a task.
        
        Args:
            task_id: The unique identifier of the task.
            
        Returns:
            Dict[str, Any]: The next run time, or an error dict if task not found.
        """
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        task = self.scheduled_tasks[task_id]
        return {
            "task_id": task_id,
            "next_run_at": task.get("next_run_at"),
            "status": task["status"]
        }

    # ==================== State Change Operations ====================

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Remove or deactivate a task if it exists and has status 'active' or 'pending'.
        
        The task will no longer appear in future execution plans.
        
        Args:
            task_id: The unique identifier of the task to delete.
            
        Returns:
            Dict[str, Any]: Success confirmation or error dict if constraints violated.
        """
        # Constraint 1: Task must exist
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' does not exist and cannot be deleted"}
        
        task = self.scheduled_tasks[task_id]
        
        # Constraint 2: Only active or pending tasks can be deleted
        if task["status"] not in ["active", "pending"]:
            return {"error": f"Task '{task_id}' has status '{task['status']}'. Only tasks with status 'active' or 'pending' can be deleted"}
        
        # Remove the task from scheduled_tasks
        deleted_task = self.scheduled_tasks.pop(task_id)
        
        return {
            "success": True,
            "message": f"Task '{task_id}' has been deleted",
            "deleted_task": deepcopy(deleted_task)
        }

    def deactivate_task(self, task_id: str) -> Dict[str, Any]:
        """
        Change a task's status to 'inactive' without fully removing it.
        
        Preserves metadata for audit purposes.
        
        Args:
            task_id: The unique identifier of the task to deactivate.
            
        Returns:
            Dict[str, Any]: Success confirmation or error dict if task not found.
        """
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        task = self.scheduled_tasks[task_id]
        
        if task["status"] == "inactive":
            return {"error": f"Task '{task_id}' is already inactive"}
        
        # Update status and clear next_run_at
        task["status"] = "inactive"
        task["next_run_at"] = None
        
        return {
            "success": True,
            "message": f"Task '{task_id}' has been deactivated",
            "task_id": task_id,
            "new_status": "inactive"
        }

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a task by deactivating it after checking constraints.
        
        This is an alias/wrapper for deactivation with constraint checking.
        
        Args:
            task_id: The unique identifier of the task to cancel.
            
        Returns:
            Dict[str, Any]: Success confirmation or error dict if constraints violated.
        """
        # Check if task exists
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' does not exist and cannot be cancelled"}
        
        task = self.scheduled_tasks[task_id]
        
        # Only active or pending tasks can be cancelled
        if task["status"] not in ["active", "pending"]:
            return {"error": f"Task '{task_id}' has status '{task['status']}'. Only 'active' or 'pending' tasks can be cancelled"}
        
        # Deactivate the task
        task["status"] = "inactive"
        task["next_run_at"] = None
        
        return {
            "success": True,
            "message": f"Task '{task_id}' has been cancelled",
            "task_id": task_id,
            "new_status": "inactive"
        }

    def update_task_status(self, task_id: str, new_status: str) -> Dict[str, Any]:
        """
        Modify the status of a task subject to valid transitions.
        
        Args:
            task_id: The unique identifier of the task.
            new_status: The new status to set (active, pending, or inactive).
            
        Returns:
            Dict[str, Any]: Success confirmation or error dict if invalid transition.
        """
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        valid_statuses = ["active", "pending", "inactive"]
        if new_status not in valid_statuses:
            return {"error": f"Invalid status '{new_status}'. Must be one of: {valid_statuses}"}
        
        task = self.scheduled_tasks[task_id]
        old_status = task["status"]
        
        if old_status == new_status:
            return {"error": f"Task '{task_id}' already has status '{new_status}'"}
        
        # Update the status
        task["status"] = new_status
        
        # If deactivating, clear next_run_at
        if new_status == "inactive":
            task["next_run_at"] = None
        
        return {
            "success": True,
            "message": f"Task '{task_id}' status updated from '{old_status}' to '{new_status}'",
            "task_id": task_id,
            "old_status": old_status,
            "new_status": new_status
        }

    def clear_execution_history(self, task_id: str) -> Dict[str, Any]:
        """
        Remove or archive execution records associated with a task.
        
        Args:
            task_id: The unique identifier of the task whose history to clear.
            
        Returns:
            Dict[str, Any]: Success confirmation with count of cleared records,
                          or error dict if task not found.
        """
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        task = self.scheduled_tasks[task_id]
        history_ids = task.get("execution_history", [])
        
        # Remove execution records
        cleared_count = 0
        for record_id in history_ids:
            if record_id in self.execution_records:
                del self.execution_records[record_id]
                cleared_count += 1
        
        # Clear the task's execution history list
        task["execution_history"] = []
        
        return {
            "success": True,
            "message": f"Execution history cleared for task '{task_id}'",
            "task_id": task_id,
            "records_cleared": cleared_count
        }

    def pause_scheduler(self) -> Dict[str, Any]:
        """
        Set system_status to 'paused' to prevent new task executions.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Success confirmation or error if already paused.
        """
        current_status = self.scheduler_system.get("system_status", "running")
        
        if current_status == "paused":
            return {"error": "Scheduler is already paused"}
        
        self.scheduler_system["system_status"] = "paused"
        
        return {
            "success": True,
            "message": "Scheduler has been paused",
            "previous_status": current_status,
            "new_status": "paused"
        }

    def resume_scheduler(self) -> Dict[str, Any]:
        """
        Restore system_status to 'running' to allow task executions to proceed.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Success confirmation or error if already running.
        """
        current_status = self.scheduler_system.get("system_status", "running")
        
        if current_status == "running":
            return {"error": "Scheduler is already running"}
        
        self.scheduler_system["system_status"] = "running"
        
        return {
            "success": True,
            "message": "Scheduler has been resumed",
            "previous_status": current_status,
            "new_status": "running"
        }

    def archive_task(self, task_id: str) -> Dict[str, Any]:
        """
        Move a deleted/inactive task to an archive for historical retention.
        
        Removes the task from active scheduling while preserving it for auditing.
        
        Args:
            task_id: The unique identifier of the task to archive.
            
        Returns:
            Dict[str, Any]: Success confirmation or error dict if constraints violated.
        """
        if task_id not in self.scheduled_tasks:
            return {"error": f"Task with id '{task_id}' not found in active tasks"}
        
        task = self.scheduled_tasks[task_id]
        
        # Only inactive tasks can be archived (must be deactivated first)
        if task["status"] != "inactive":
            return {"error": f"Task '{task_id}' must be inactive before archiving. Current status: '{task['status']}'"}
        
        # Move to archive
        archived_task = self.scheduled_tasks.pop(task_id)
        archived_task["archived_at"] = self._timestamp()
        self.archived_tasks[task_id] = archived_task
        
        return {
            "success": True,
            "message": f"Task '{task_id}' has been archived",
            "task_id": task_id,
            "archived_at": archived_task["archived_at"]
        }


# Test cases for the TaskSchedulingSystem
__TEST_CASES__ = [
    {
        "name": "Query task details and check status",
        "steps": [
            {"tool_call": "get_task_by_id(task_id='task_001')", "expect_success": True},
            {"tool_call": "check_task_status(task_id='task_001')", "expect_success": True},
            {"tool_call": "get_next_run_time(task_id='task_001')", "expect_success": True},
            {"tool_call": "get_execution_history(task_id='task_001')", "expect_success": True}
        ]
    },
    {
        "name": "List and filter tasks",
        "steps": [
            {"tool_call": "list_all_tasks()", "expect_success": True},
            {"tool_call": "list_tasks_by_status(status='active')", "expect_success": True},
            {"tool_call": "task_exists(task_id='task_002')", "expect_success": True},
            {"tool_call": "task_exists(task_id='nonexistent_task')", "expect_success": True}
        ]
    },
    {
        "name": "Deactivate and archive a task",
        "steps": [
            {"tool_call": "check_task_status(task_id='task_001')", "expect_success": True},
            {"tool_call": "deactivate_task(task_id='task_001')", "expect_success": True},
            {"tool_call": "check_task_status(task_id='task_001')", "expect_success": True},
            {"tool_call": "archive_task(task_id='task_001')", "expect_success": True}
        ]
    },
    {
        "name": "Pause and resume scheduler",
        "steps": [
            {"tool_call": "get_system_status()", "expect_success": True},
            {"tool_call": "pause_scheduler()", "expect_success": True},
            {"tool_call": "get_system_status()", "expect_success": True},
            {"tool_call": "resume_scheduler()", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - invalid operations",
        "steps": [
            {"tool_call": "get_task_by_id(task_id='nonexistent_task')", "expect_success": False},
            {"tool_call": "delete_task(task_id='task_004')", "expect_success": False},
            {"tool_call": "archive_task(task_id='task_001')", "expect_success": False},
            {"tool_call": "list_tasks_by_status(status='invalid_status')", "expect_success": False}
        ]
    }
]