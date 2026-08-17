"""
Task Tracking System Environment API

A stateful environment for managing, organizing, and monitoring tasks within workflows or projects.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    "tasks": {
        "task_001": {
            "task_id": "task_001",
            "description": "Implement user authentication module",
            "status": "in progress",
            "created_at": "2024-01-15T09:00:00",
            "completed_at": None,
            "due_date": "2024-02-01",
            "priority": "high",
            "assigned_to": "user_001"
        },
        "task_002": {
            "task_id": "task_002",
            "description": "Write unit tests for payment service",
            "status": "pending",
            "created_at": "2024-01-16T10:30:00",
            "completed_at": None,
            "due_date": "2024-02-15",
            "priority": "medium",
            "assigned_to": "user_002"
        },
        "task_003": {
            "task_id": "task_003",
            "description": "Update database schema documentation",
            "status": "completed",
            "created_at": "2024-01-10T08:00:00",
            "completed_at": "2024-01-14T16:00:00",
            "due_date": "2024-01-20",
            "priority": "low",
            "assigned_to": "user_001"
        },
        "task_004": {
            "task_id": "task_004",
            "description": "Review code for API endpoints",
            "status": "blocked",
            "created_at": "2024-01-17T11:00:00",
            "completed_at": None,
            "due_date": "2024-02-10",
            "priority": "high",
            "assigned_to": "user_003"
        }
    },
    "users": {
        "user_001": {
            "user_id": "user_001",
            "name": "Alice Johnson",
            "role": "developer"
        },
        "user_002": {
            "user_id": "user_002",
            "name": "Bob Smith",
            "role": "tester"
        },
        "user_003": {
            "user_id": "user_003",
            "name": "Carol Williams",
            "role": "tech_lead"
        }
    },
    "projects": {
        "proj_001": {
            "project_id": "proj_001",
            "name": "E-Commerce Platform",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "tasks": ["task_001", "task_002"]
        },
        "proj_002": {
            "project_id": "proj_002",
            "name": "Internal Tools Migration",
            "start_date": "2024-02-01",
            "end_date": "2024-04-30",
            "tasks": ["task_003"]
        },
        "proj_003": {
            "project_id": "proj_003",
            "name": "Mobile App Development",
            "start_date": "2024-03-01",
            "end_date": "2024-09-30",
            "tasks": ["task_004"]
        }
    },
    "valid_statuses": ["pending", "in progress", "completed", "blocked"],
    "current_user": "user_001",
    "next_task_id": 5
}


class TaskTrackingSystem:
    """
    A task tracking system environment for managing tasks, users, and projects.
    
    This environment provides operations for creating, updating, querying, and
    completing tasks within a project management context. It enforces business
    rules around task status transitions and maintains referential integrity.
    """
    
    def __init__(self) -> None:
        """
        Initialize the TaskTrackingSystem with default state attributes.
        
        Args:
            None
        
        Returns:
            None
        """
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.valid_statuses: List[str] = []
        self.current_user: str = ""
        self.next_task_id: int = 1
        
        self._api_description: str = "A task tracking system for managing, organizing, and monitoring tasks within workflows and projects."
    
    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values for the environment.
            long_context: Flag for extended context loading (unused in base implementation).
        
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
        Retrieve the current state of the entire environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - tasks: All tasks in the system
                - users: All users in the system
                - projects: All projects in the system
                - valid_statuses: List of allowed task status values
                - current_user: The currently active user ID
                - next_task_id: Counter for generating unique task IDs
        """
        return {
            "tasks": deepcopy(self.tasks),
            "users": deepcopy(self.users),
            "projects": deepcopy(self.projects),
            "valid_statuses": deepcopy(self.valid_statuses),
            "current_user": self.current_user,
            "next_task_id": self.next_task_id
        }
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a task given its task_id.
        
        Args:
            task_id: The unique identifier of the task to retrieve.
        
        Returns:
            Dict[str, Any]: The task details if found, or an error dictionary
                containing {"error": "..."} if the task does not exist.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        return deepcopy(self.tasks[task_id])
    
    def list_all_tasks(self) -> Dict[str, Any]:
        """
        Retrieve all tasks in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tasks: List of all task objects in the system
                - count: Total number of tasks
        """
        tasks_list = list(self.tasks.values())
        return {
            "tasks": deepcopy(tasks_list),
            "count": len(tasks_list)
        }
    
    def list_tasks_by_status(self, status: str) -> Dict[str, Any]:
        """
        Retrieve tasks filtered by a specific status.
        
        Args:
            status: The status to filter by (e.g., "pending", "in progress", "completed", "blocked").
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tasks: List of tasks matching the status
                - count: Number of matching tasks
                - status: The filter status used
                Or an error dictionary if the status is invalid.
        """
        if status not in self.valid_statuses:
            return {"error": f"Invalid status '{status}'. Valid statuses are: {self.valid_statuses}"}
        
        filtered_tasks = [
            task for task in self.tasks.values()
            if task["status"] == status
        ]
        return {
            "tasks": deepcopy(filtered_tasks),
            "count": len(filtered_tasks),
            "status": status
        }
    
    def list_tasks_by_user(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve all tasks assigned to a specific user.
        
        Args:
            user_id: The unique identifier of the user.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tasks: List of tasks assigned to the user
                - count: Number of assigned tasks
                - user_id: The user ID used for filtering
                Or an error dictionary if the user does not exist.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        
        user_tasks = [
            task for task in self.tasks.values()
            if task.get("assigned_to") == user_id
        ]
        return {
            "tasks": deepcopy(user_tasks),
            "count": len(user_tasks),
            "user_id": user_id
        }
    
    def list_tasks_in_project(self, project_id: str) -> Dict[str, Any]:
        """
        Retrieve all tasks associated with a given project_id.
        
        Args:
            project_id: The unique identifier of the project.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tasks: List of task objects in the project
                - count: Number of tasks in the project
                - project_id: The project ID used for filtering
                Or an error dictionary if the project does not exist.
        """
        if project_id not in self.projects:
            return {"error": f"Project with id '{project_id}' not found"}
        
        project = self.projects[project_id]
        project_tasks = [
            self.tasks[task_id] for task_id in project.get("tasks", [])
            if task_id in self.tasks
        ]
        return {
            "tasks": deepcopy(project_tasks),
            "count": len(project_tasks),
            "project_id": project_id
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the current status of a task without retrieving full details.
        
        Args:
            task_id: The unique identifier of the task.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - task_id: The task identifier
                - status: The current status of the task
                Or an error dictionary if the task does not exist.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        return {
            "task_id": task_id,
            "status": self.tasks[task_id]["status"]
        }
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user information by user_id.
        
        Args:
            user_id: The unique identifier of the user.
        
        Returns:
            Dict[str, Any]: The user details if found, or an error dictionary
                containing {"error": "..."} if the user does not exist.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        return deepcopy(self.users[user_id])
    
    def get_project_by_id(self, project_id: str) -> Dict[str, Any]:
        """
        Retrieve project details by project_id.
        
        Args:
            project_id: The unique identifier of the project.
        
        Returns:
            Dict[str, Any]: The project details if found, or an error dictionary
                containing {"error": "..."} if the project does not exist.
        """
        if project_id not in self.projects:
            return {"error": f"Project with id '{project_id}' not found"}
        return deepcopy(self.projects[project_id])
    
    def get_incomplete_tasks(self) -> Dict[str, Any]:
        """
        Retrieve all tasks that are not in "completed" status.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tasks: List of incomplete task objects
                - count: Number of incomplete tasks
        """
        incomplete = [
            task for task in self.tasks.values()
            if task["status"] != "completed"
        ]
        return {
            "tasks": deepcopy(incomplete),
            "count": len(incomplete)
        }
    
    def is_task_completable(self, task_id: str) -> Dict[str, Any]:
        """
        Check whether a task can be marked as completed.
        
        A task is completable if it exists and its current status is not "completed".
        
        Args:
            task_id: The unique identifier of the task.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - task_id: The task identifier
                - completable: Boolean indicating if the task can be completed
                - current_status: The current status of the task
                Or an error dictionary if the task does not exist.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        task = self.tasks[task_id]
        is_completable = task["status"] != "completed"
        return {
            "task_id": task_id,
            "completable": is_completable,
            "current_status": task["status"]
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Mark a task as "completed" and set the completed_at timestamp.
        
        Enforces the constraint that a task can only be completed if its
        current status is not already "completed".
        
        Args:
            task_id: The unique identifier of the task to complete.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if the operation succeeded
                - task_id: The task identifier
                - previous_status: The status before completion
                - completed_at: The timestamp when completed
                Or an error dictionary if the operation fails.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        task = self.tasks[task_id]
        if task["status"] == "completed":
            return {"error": f"Task '{task_id}' is already completed"}
        
        previous_status = task["status"]
        completed_timestamp = self._timestamp()
        
        task["status"] = "completed"
        task["completed_at"] = completed_timestamp
        
        return {
            "success": True,
            "task_id": task_id,
            "previous_status": previous_status,
            "completed_at": completed_timestamp
        }
    
    def update_task_status(self, task_id: str, new_status: str) -> Dict[str, Any]:
        """
        Change the status of a task to any valid value.
        
        Enforces that the status must be from the predefined set of valid statuses.
        If updating to "completed", the completed_at timestamp is set.
        
        Args:
            task_id: The unique identifier of the task.
            new_status: The new status to set for the task.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if the operation succeeded
                - task_id: The task identifier
                - previous_status: The status before the update
                - new_status: The new status that was set
                Or an error dictionary if the operation fails.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        if new_status not in self.valid_statuses:
            return {"error": f"Invalid status '{new_status}'. Valid statuses are: {self.valid_statuses}"}
        
        task = self.tasks[task_id]
        previous_status = task["status"]
        
        # Constraint: Cannot set to completed if already completed
        if new_status == "completed" and previous_status == "completed":
            return {"error": f"Task '{task_id}' is already completed"}
        
        task["status"] = new_status
        
        # Set completed_at timestamp when marking as completed
        if new_status == "completed":
            task["completed_at"] = self._timestamp()
        
        return {
            "success": True,
            "task_id": task_id,
            "previous_status": previous_status,
            "new_status": new_status
        }
    
    def create_task(
        self,
        description: str,
        status: str = "pending",
        due_date: Optional[str] = None,
        priority: str = "medium",
        assigned_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new task with unique task_id, description, and initial status.
        
        Args:
            description: A text description of the task.
            status: Initial status of the task (default: "pending").
            due_date: Optional due date string for the task.
            priority: Priority level of the task (default: "medium").
            assigned_to: Optional user_id to assign the task to.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if the task was created
                - task: The newly created task object
                Or an error dictionary if creation fails.
        """
        if status not in self.valid_statuses:
            return {"error": f"Invalid status '{status}'. Valid statuses are: {self.valid_statuses}"}
        
        if assigned_to is not None and assigned_to not in self.users:
            return {"error": f"User with id '{assigned_to}' not found"}
        
        task_id = f"task_{self.next_task_id:03d}"
        self.next_task_id += 1
        
        new_task = {
            "task_id": task_id,
            "description": description,
            "status": status,
            "created_at": self._timestamp(),
            "completed_at": None,
            "due_date": due_date,
            "priority": priority,
            "assigned_to": assigned_to
        }
        
        self.tasks[task_id] = new_task
        
        return {
            "success": True,
            "task": deepcopy(new_task)
        }
    
    def assign_task_to_user(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """
        Assign a task to a user by updating the assigned_to field.
        
        Args:
            task_id: The unique identifier of the task.
            user_id: The unique identifier of the user to assign.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if the assignment succeeded
                - task_id: The task identifier
                - assigned_to: The user ID the task is now assigned to
                - previous_assignee: The previous assignee (if any)
                Or an error dictionary if the operation fails.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        
        task = self.tasks[task_id]
        previous_assignee = task.get("assigned_to")
        task["assigned_to"] = user_id
        
        return {
            "success": True,
            "task_id": task_id,
            "assigned_to": user_id,
            "previous_assignee": previous_assignee
        }
    
    def update_task_due_date(self, task_id: str, due_date: str) -> Dict[str, Any]:
        """
        Modify the due date of a task.
        
        Args:
            task_id: The unique identifier of the task.
            due_date: The new due date string to set.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if the update succeeded
                - task_id: The task identifier
                - previous_due_date: The previous due date
                - new_due_date: The new due date that was set
                Or an error dictionary if the operation fails.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        task = self.tasks[task_id]
        previous_due_date = task.get("due_date")
        task["due_date"] = due_date
        
        return {
            "success": True,
            "task_id": task_id,
            "previous_due_date": previous_due_date,
            "new_due_date": due_date
        }
    
    def update_task_priority(self, task_id: str, priority: str) -> Dict[str, Any]:
        """
        Change the priority level of a task.
        
        Args:
            task_id: The unique identifier of the task.
            priority: The new priority level to set.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if the update succeeded
                - task_id: The task identifier
                - previous_priority: The previous priority level
                - new_priority: The new priority level that was set
                Or an error dictionary if the operation fails.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        task = self.tasks[task_id]
        previous_priority = task.get("priority")
        task["priority"] = priority
        
        return {
            "success": True,
            "task_id": task_id,
            "previous_priority": previous_priority,
            "new_priority": priority
        }
    
    def add_task_to_project(self, task_id: str, project_id: str) -> Dict[str, Any]:
        """
        Add an existing task to a project by linking its task_id.
        
        Args:
            task_id: The unique identifier of the task to add.
            project_id: The unique identifier of the project.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if the task was added
                - task_id: The task identifier
                - project_id: The project identifier
                Or an error dictionary if the operation fails.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with id '{task_id}' not found"}
        
        if project_id not in self.projects:
            return {"error": f"Project with id '{project_id}' not found"}
        
        project = self.projects[project_id]
        if task_id in project["tasks"]:
            return {"error": f"Task '{task_id}' is already in project '{project_id}'"}
        
        project["tasks"].append(task_id)
        
        return {
            "success": True,
            "task_id": task_id,
            "project_id": project_id
        }
    
    def remove_task_from_project(self, task_id: str, project_id: str) -> Dict[str, Any]:
        """
        Remove a task from a project's task list.
        
        Args:
            task_id: The unique identifier of the task to remove.
            project_id: The unique identifier of the project.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if the task was removed
                - task_id: The task identifier
                - project_id: The project identifier
                Or an error dictionary if the operation fails.
        """
        if project_id not in self.projects:
            return {"error": f"Project with id '{project_id}' not found"}
        
        project = self.projects[project_id]
        if task_id not in project["tasks"]:
            return {"error": f"Task '{task_id}' is not in project '{project_id}'"}
        
        project["tasks"].remove(task_id)
        
        return {
            "success": True,
            "task_id": task_id,
            "project_id": project_id
        }
    
    def bulk_complete_tasks(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Mark multiple tasks as completed in a single operation.
        
        Each task is validated individually before completion. Tasks that
        cannot be completed (not found or already completed) are reported
        in the failed list.
        
        Args:
            task_ids: List of task identifiers to complete.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success: True if at least one task was completed
                - completed: List of task_ids that were successfully completed
                - failed: List of dictionaries with task_id and error for failures
                - completed_count: Number of tasks completed
                - failed_count: Number of tasks that failed
        """
        completed = []
        failed = []
        completed_timestamp = self._timestamp()
        
        for task_id in task_ids:
            if task_id not in self.tasks:
                failed.append({"task_id": task_id, "error": "Task not found"})
                continue
            
            task = self.tasks[task_id]
            if task["status"] == "completed":
                failed.append({"task_id": task_id, "error": "Task is already completed"})
                continue
            
            task["status"] = "completed"
            task["completed_at"] = completed_timestamp
            completed.append(task_id)
        
        return {
            "success": len(completed) > 0,
            "completed": completed,
            "failed": failed,
            "completed_count": len(completed),
            "failed_count": len(failed)
        }


__TEST_CASES__ = [
    {
        "name": "Complete task workflow",
        "steps": [
            {"tool_call": "get_task_by_id(task_id='task_001')", "expect_success": True},
            {"tool_call": "is_task_completable(task_id='task_001')", "expect_success": True},
            {"tool_call": "complete_task(task_id='task_001')", "expect_success": True},
            {"tool_call": "get_task_status(task_id='task_001')", "expect_success": True}
        ]
    },
    {
        "name": "Create and assign task to project",
        "steps": [
            {"tool_call": "create_task(description='New feature implementation', status='pending', priority='high', assigned_to='user_002')", "expect_success": True},
            {"tool_call": "add_task_to_project(task_id='task_005', project_id='proj_001')", "expect_success": True},
            {"tool_call": "list_tasks_in_project(project_id='proj_001')", "expect_success": True}
        ]
    },
    {
        "name": "Query tasks by status and user",
        "steps": [
            {"tool_call": "list_tasks_by_status(status='pending')", "expect_success": True},
            {"tool_call": "list_tasks_by_user(user_id='user_001')", "expect_success": True},
            {"tool_call": "get_incomplete_tasks()", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - invalid operations",
        "steps": [
            {"tool_call": "get_task_by_id(task_id='nonexistent_task')", "expect_success": False},
            {"tool_call": "complete_task(task_id='task_003')", "expect_success": False},
            {"tool_call": "update_task_status(task_id='task_001', new_status='invalid_status')", "expect_success": False},
            {"tool_call": "list_tasks_by_status(status='unknown')", "expect_success": False},
            {"tool_call": "assign_task_to_user(task_id='task_001', user_id='nonexistent_user')", "expect_success": False}
        ]
    },
    {
        "name": "Bulk complete tasks with mixed results",
        "steps": [
            {"tool_call": "list_all_tasks()", "expect_success": True},
            {"tool_call": "bulk_complete_tasks(task_ids=['task_002', 'task_003', 'task_004'])", "expect_success": True},
            {"tool_call": "get_incomplete_tasks()", "expect_success": True}
        ]
    }
]