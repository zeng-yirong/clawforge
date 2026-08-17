from copy import deepcopy
from typing import Dict, List, Optional, Union

DEFAULT_TODO_STATE = {
    "current_user": None,
    "projects": {
        10: {"id": 10, "name": "Website Redesign", "owner": "admin"},
    },
    "tasks": {
        1001: {
            "id": 1001,
            "project_id": 10,
            "title": "Design Mockups",
            "description": "Create Figma mockups for homepage",
            "status": "In Progress",
            "priority": 4,
            "assignee": "alice",
            "subtasks": [{"id": 1, "title": "Header", "done": True}, {"id": 2, "title": "Footer", "done": False}],
            "dependencies": [],  # List of task IDs that must be completed first
        },
        1002: {
            "id": 1002,
            "project_id": 10,
            "title": "Frontend Implementation",
            "description": "Convert mockups to React components",
            "status": "Blocked",
            "priority": 5,
            "assignee": "bob",
            "subtasks": [],
            "dependencies": [1001],
        }
    },
    "project_counter": 11,
    "task_counter": 1003,
}


class TodoListAPI:
    """
    A class representing a complex TodoList and Task Management API.

    Features include project organization, task assignment, multi-stage statuses,
    subtasks, and task dependencies (blockers).

    Attributes:
        current_user (Optional[str]): Currently authenticated user.
        projects (Dict[int, Dict]): Active projects keyed by project ID.
        tasks (Dict[int, Dict]): Tasks keyed by task ID.
        project_counter (int): Counter for projects.
        task_counter (int): Counter for tasks.
    """

    VALID_STATUSES = ["Todo", "In Progress", "In Review", "Blocked", "Done"]

    def __init__(self):
        self.current_user: Optional[str]
        self.projects: Dict[int, Dict[str, Union[int, str]]]
        self.tasks: Dict[int, Dict[str, Union[int, str, List]]]
        self.project_counter: int
        self.task_counter: int
        self._api_description = "A project and task management system handling assignments, statuses, subtasks, and blockers."

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load a scenario into the TodoList API.
        
        Args:
            scenario (dict): State dictionary to load.
            long_context (bool): Whether to load long context features.
            
        Returns:
            None
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_TODO_STATE)
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])

        projects_raw = scenario.get("projects", DEFAULT_STATE_COPY["projects"])
        self.projects = {int(k) if str(k).isdigit() else k: v for k, v in projects_raw.items()}

        tasks_raw = scenario.get("tasks", DEFAULT_STATE_COPY["tasks"])
        self.tasks = {int(k) if str(k).isdigit() else k: v for k, v in tasks_raw.items()}

        self.project_counter = scenario.get("project_counter", DEFAULT_STATE_COPY["project_counter"])
        self.task_counter = scenario.get("task_counter", DEFAULT_STATE_COPY["task_counter"])

    def get_env_state(self) -> Dict:
        """
        Retrieve the current environment state.
        
        Returns:
            Dict: Dictionary containing current user, projects, tasks, and counters.
        """
        return {
            "current_user": self.current_user,
            "projects": self.projects,
            "tasks": self.tasks,
            "project_counter": self.project_counter,
            "task_counter": self.task_counter,
        }

    def auth_login(self, username: str) -> Dict[str, bool]:
        """
        Authenticate as a user.
        
        Args:
            username (str): The username of the user to log in as.
            
        Returns:
            Dict[str, bool]: Dictionary indicating successful authentication.
        """
        self.current_user = username
        return {"success": True}

    def create_project(self, name: str, owner: str) -> Dict[str, Union[int, str]]:
        """
        Create a new project.
        
        Args:
            name (str): The name of the project.
            owner (str): The owner of the project.
            
        Returns:
            Dict[str, Union[int, str]]: Dictionary containing the new project ID and status, or an error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if not name:
            return {"error": "Project name cannot be empty."}

        project_id = self.project_counter
        self.projects[project_id] = {
            "id": project_id,
            "name": name,
            "owner": owner
        }
        self.project_counter += 1
        return {"id": project_id, "status": "Project created successfully."}

    def create_task(self, project_id: int, title: str, description: str = "", priority: int = 3,
                    assignee: Optional[str] = None) -> Dict[str, Union[int, str]]:
        """
        Create a new task within a project.
        
        Args:
            project_id (int): The ID of the project to create the task in.
            title (str): The title of the new task.
            description (str): Detailed description of the task.
            priority (int): Priority level between 1 and 5.
            assignee (Optional[str]): Username of the person assigned to the task.
            
        Returns:
            Dict[str, Union[int, str]]: Dictionary containing the new task ID and status, or an error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if project_id not in self.projects:
            return {"error": f"Project ID {project_id} not found."}
        if priority < 1 or priority > 5:
            return {"error": "Priority must be between 1 and 5."}

        task_id = self.task_counter
        self.tasks[task_id] = {
            "id": task_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "status": "Todo",
            "priority": priority,
            "assignee": assignee,
            "subtasks": [],
            "dependencies": []
        }
        self.task_counter += 1
        return {"id": task_id, "status": "Task created successfully"}

    def assign_task(self, task_id: int, assignee: str) -> Dict[str, str]:
        """
        Modify the assignee of an existing task.
        
        Args:
            task_id (int): The ID of the task.
            assignee (str): Username of the new assignee.
            
        Returns:
            Dict[str, str]: Dictionary containing the result status or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if task_id not in self.tasks:
            return {"error": "Task not found."}

        self.tasks[task_id]["assignee"] = assignee
        return {"status": f"Task {task_id} assigned to {assignee}."}

    def update_task_details(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None,
                            priority: Optional[int] = None) -> Dict[str, str]:
        """
        Update task metadata such as title, description, and priority.
        
        Args:
            task_id (int): The ID of the task to update.
            title (Optional[str]): New title for the task.
            description (Optional[str]): New description.
            priority (Optional[int]): New priority (1-5).
            
        Returns:
            Dict[str, str]: Dictionary containing the result status or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if task_id not in self.tasks:
            return {"error": "Task not found."}
        if priority is not None and (priority < 1 or priority > 5):
            return {"error": "Priority must be between 1 and 5."}

        task = self.tasks[task_id]
        if title is not None:
            task["title"] = title
        if description is not None:
            task["description"] = description
        if priority is not None:
            task["priority"] = priority

        return {"status": f"Task {task_id} details updated."}

    def update_task_status(self, task_id: int, status: str) -> Dict[str, str]:
        """
        Update the status of a task. Checks dependencies if attempting to mark as 'Done' or 'In Progress'.
        
        Args:
            task_id (int): The ID of the task to update.
            status (str): The new status to set.
            
        Returns:
            Dict[str, str]: Dictionary containing the result status or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if task_id not in self.tasks:
            return {"error": "Task not found."}
        if status not in self.VALID_STATUSES:
            return {"error": f"Invalid status. Must be one of {self.VALID_STATUSES}."}

        task = self.tasks[task_id]

        # Dependency check
        if status in ["In Progress", "In Review", "Done"]:
            for dep_id in task["dependencies"]:
                dep_task = self.tasks.get(dep_id)
                if dep_task and dep_task["status"] != "Done":
                    return {"error": f"Cannot change status. Task is blocked by incomplete dependency ID {dep_id}."}

        task["status"] = status
        return {"status": f"Task {task_id} marked as {status}."}

    def add_dependency(self, task_id: int, depends_on_task_id: int) -> Dict[str, str]:
        """
        Add a dependency to a task (task_id is blocked by depends_on_task_id).
        
        Args:
            task_id (int): The ID of the task that will depend on another task.
            depends_on_task_id (int): The ID of the task that must be completed first.
            
        Returns:
            Dict[str, str]: Dictionary containing the result status or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if task_id not in self.tasks or depends_on_task_id not in self.tasks:
            return {"error": "One or both task IDs not found."}
        if task_id == depends_on_task_id:
            return {"error": "A task cannot depend on itself."}

        # Cycle detection
        visited = set()
        queue = [depends_on_task_id]
        while queue:
            curr = queue.pop(0)
            if curr == task_id:
                return {"error": "Dependency cycle detected."}
            if curr not in visited:
                visited.add(curr)
                if curr in self.tasks:
                    queue.extend(self.tasks[curr].get("dependencies", []))

        task = self.tasks[task_id]
        if depends_on_task_id not in task["dependencies"]:
            task["dependencies"].append(depends_on_task_id)
            # Automatically set task to blocked if the dependency isn't done
            if self.tasks[depends_on_task_id]["status"] != "Done":
                task["status"] = "Blocked"

        return {"status": f"Task {task_id} now depends on Task {depends_on_task_id}."}

    def remove_dependency(self, task_id: int, depends_on_task_id: int) -> Dict[str, str]:
        """
        Remove a dependency from a task and unblock if conditions are met.
        
        Args:
            task_id (int): The ID of the task that currently depends on another task.
            depends_on_task_id (int): The ID of the dependency task to remove.
            
        Returns:
            Dict[str, str]: Dictionary containing the result status or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if task_id not in self.tasks:
            return {"error": "Task not found."}

        task = self.tasks[task_id]
        if depends_on_task_id not in task["dependencies"]:
            return {"error": f"Task {task_id} does not depend on task {depends_on_task_id}."}

        task["dependencies"].remove(depends_on_task_id)

        # Check if we can unblock the task
        if task["status"] == "Blocked":
            still_blocked = False
            for dep_id in task["dependencies"]:
                dep_task = self.tasks.get(dep_id)
                if dep_task and dep_task["status"] != "Done":
                    still_blocked = True
                    break
            if not still_blocked:
                task["status"] = "Todo"

        return {"status": f"Dependency {depends_on_task_id} removed from Task {task_id}."}

    def delete_task(self, task_id: int) -> Dict[str, str]:
        """
        Delete a specific task. Prevent deletion if other tasks depend on it.
        
        Args:
            task_id (int): The ID of the task to delete.
            
        Returns:
            Dict[str, str]: Dictionary containing the result status or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if task_id not in self.tasks:
            return {"error": "Task not found."}

        # Check if any task depends on this task
        for t in self.tasks.values():
            if task_id in t.get("dependencies", []):
                return {"error": f"Cannot delete task. Task {t['id']} depends on it."}

        del self.tasks[task_id]
        return {"status": f"Task {task_id} deleted."}

    def manage_subtask(self, task_id: int, action: str, subtask_title: str = "", subtask_id: int = -1) -> Dict[str, str]:
        """
        Add or toggle completion of a subtask.
        
        Args:
            task_id (int): The ID of the task containing the subtask.
            action (str): "add" to create a new subtask, or "toggle" to switch completion status.
            subtask_title (str): The title of the subtask (required if action is "add").
            subtask_id (int): The ID of the subtask to toggle (required if action is "toggle").
            
        Returns:
            Dict[str, str]: Dictionary containing the result status or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if task_id not in self.tasks:
            return {"error": "Task not found."}

        task = self.tasks[task_id]
        if action == "add":
            if not subtask_title:
                return {"error": "Title required to add subtask."}
            new_id = len(task["subtasks"]) + 1
            task["subtasks"].append({"id": new_id, "title": subtask_title, "done": False})
            return {"status": f"Subtask '{subtask_title}' added with id {new_id}."}

        elif action == "toggle":
            for st in task["subtasks"]:
                if st["id"] == subtask_id:
                    st["done"] = not st["done"]
                    return {"status": f"Subtask {subtask_id} toggled to {st['done']}."}
            return {"error": "Subtask ID not found."}

        return {"error": "Invalid action. Use 'add' or 'toggle'."}

    def get_dashboard(self, project_id: Optional[int] = None) -> Dict[str, Union[str, List[Dict[str, Union[int, str]]]]]:
        """
        Retrieve tasks, optionally filtered by project, sorting by priority.
        
        Args:
            project_id (Optional[int]): If provided, only returns tasks for this project ID.
            
        Returns:
            Dict: Dictionary containing dashboard task list or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if project_id is not None and project_id not in self.projects:
            return {"error": "Project not found."}

        filtered_tasks = []
        for task in self.tasks.values():
            if project_id and task["project_id"] != project_id:
                continue
            # Return a simplified task view for the dashboard
            filtered_tasks.append({
                "id": task["id"],
                "title": task["title"],
                "status": task["status"],
                "priority": task["priority"],
                "assignee": task["assignee"]
            })

        # Sort by priority descending
        filtered_tasks.sort(key=lambda x: x["priority"], reverse=True)
        return {"dashboard": filtered_tasks}

    def search_tasks(self, assignee: Optional[str] = None, status: Optional[str] = None,
                     keyword: Optional[str] = None) -> Dict[str, Union[str, List[Dict[str, Union[int, str]]]]]:
        """
        Search tasks using multiple filter conditions.
        
        Args:
            assignee (Optional[str]): Filter by assignee username.
            status (Optional[str]): Filter by task status.
            keyword (Optional[str]): Search keyword in title or description.
            
        Returns:
            Dict: Dictionary containing search results or an error message.
        """
        if not self.current_user:
            return {"error": "Authentication required."}

        results = []
        for task in self.tasks.values():
            if assignee and task.get("assignee") != assignee:
                continue
            if status and task.get("status") != status:
                continue
            if keyword:
                kw = keyword.lower()
                title = task.get("title", "").lower()
                desc = task.get("description", "").lower()
                if kw not in title and kw not in desc:
                    continue
            results.append({
                "id": task["id"],
                "project_id": task["project_id"],
                "title": task["title"],
                "status": task["status"],
                "priority": task["priority"],
                "assignee": task.get("assignee")
            })

        return {"results": results}


__TEST_CASES__ = [
    {
        'name': 'Normal Path - Authentication and Dashboard retrieval',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['todo'].get_dashboard(project_id=10)"}
        ]
    },
    {
        'name': 'Normal Path - Create a new task',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': True, 'tool_call': "env['todo'].create_task(project_id=10, title='Backend API', description='Create API for tasks', priority=3, assignee='charlie')"},
            {'expect_success': True, 'tool_call': "env['todo'].get_env_state()"}
        ]
    },
    {
        'name': 'Normal Path - Add and toggle subtasks',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['todo'].manage_subtask(task_id=1001, action='add', subtask_title='Sidebar', subtask_id=0)"},
            {'expect_success': True, 'tool_call': "env['todo'].manage_subtask(task_id=1001, action='toggle', subtask_title='', subtask_id=1)"}
        ]
    },
    {
        'name': 'State-change verification - Resolve dependency and update blocked task',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['todo'].update_task_status(task_id=1001, status='Done')"},
            {'expect_success': True, 'tool_call': "env['todo'].update_task_status(task_id=1002, status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['todo'].get_dashboard(project_id=10)"}
        ]
    },
    {
        'name': 'Boundary Values - Create task with empty strings and negative priority',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': False, 'tool_call': "env['todo'].create_task(project_id=10, title='', description='', priority=-1, assignee='')"},
            {'expect_success': False, 'tool_call': "env['todo'].create_task(project_id=10, title='Very long title exceeding normal limits to test boundary conditions of the task creation endpoint', description='A', priority=999999, assignee='admin')"}
        ]
    },
    {
        'name': 'Error Path - Operations on non-existent IDs',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': False, 'tool_call': "env['todo'].update_task_status(task_id=9999, status='Done')"},
            {'expect_success': False, 'tool_call': "env['todo'].add_dependency(task_id=1001, depends_on_task_id=9999)"},
            {'expect_success': False, 'tool_call': "env['todo'].manage_subtask(task_id=9999, action='add', subtask_title='Test', subtask_id=0)"},
            {'expect_success': False, 'tool_call': "env['todo'].get_dashboard(project_id=9999)"}
        ]
    },
    {
        'name': 'Error Path - Invalid parameters in manage_subtask and update_task_status',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': False, 'tool_call': "env['todo'].manage_subtask(task_id=1001, action='delete', subtask_title='Test', subtask_id=0)"},
            {'expect_success': False, 'tool_call': "env['todo'].update_task_status(task_id=1001, status='InvalidStatus')"}
        ]
    },
    {
        'name': 'Error Path - Attempt to start a blocked task',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='bob')"},
            {'expect_success': False, 'tool_call': "env['todo'].update_task_status(task_id=1002, status='In Progress')"}
        ]
    },
    {
        'name': 'Cross-method workflow - Create task, add subtask, add dependency, update status',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': True, 'tool_call': "env['todo'].create_task(project_id=10, title='Integration Tests', description='Write tests', priority=1, assignee='admin')"},
            {'expect_success': True, 'tool_call': "env['todo'].manage_subtask(task_id=1003, action='add', subtask_title='Test 1', subtask_id=0)"},
            {'expect_success': True, 'tool_call': "env['todo'].add_dependency(task_id=1003, depends_on_task_id=1001)"},
            {'expect_success': False, 'tool_call': "env['todo'].update_task_status(task_id=1003, status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['todo'].get_dashboard(project_id=10)"}
        ]
    },
    {
        'name': 'Error Path - Add dependency cycle',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': False, 'tool_call': "env['todo'].add_dependency(task_id=1001, depends_on_task_id=1002)"}
        ]
    },
    {
        'name': 'New Methods - Create Project and Task Details Update',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': True, 'tool_call': "env['todo'].create_project(name='New App', owner='admin')"},
            {'expect_success': True, 'tool_call': "env['todo'].create_task(project_id=11, title='Setup DB', description='SQL setup', priority=5)"},
            {'expect_success': True, 'tool_call': "env['todo'].update_task_details(task_id=1003, title='Setup Database', priority=4)"}
        ]
    },
    {
        'name': 'New Methods - Search, Assign, Delete Task',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': True, 'tool_call': "env['todo'].assign_task(task_id=1001, assignee='dave')"},
            {'expect_success': True, 'tool_call': "env['todo'].search_tasks(assignee='dave', status='In Progress')"},
            {'expect_success': False, 'tool_call': "env['todo'].delete_task(task_id=1001)"},
            {'expect_success': True, 'tool_call': "env['todo'].delete_task(task_id=1002)"}
        ]
    },
    {
        'name': 'New Methods - Remove Dependency unblocks task',
        'steps': [
            {'expect_success': True, 'tool_call': "env['todo'].auth_login(username='admin')"},
            {'expect_success': True, 'tool_call': "env['todo'].remove_dependency(task_id=1002, depends_on_task_id=1001)"},
            {'expect_success': True, 'tool_call': "env['todo'].search_tasks(status='Todo')"}
        ]
    }
]