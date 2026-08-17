"""
Workflow Management System Environment API

A stateful environment for defining, executing, and monitoring workflow instances,
including task nodes, progress tracking, and status transitions.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

# Default state containing initial sample data for all entities
DEFAULT_STATE: Dict[str, Any] = {
    # Workflow definitions (blueprints)
    "workflow_definitions": [
        {
            "definition_id": "def_001",
            "name": "Data Processing Pipeline",
            "stages": ["extract", "transform", "load", "validate"],
            "dependencies": {"transform": ["extract"], "load": ["transform"], "validate": ["load"]},
            "timeout_policy": {"max_duration_minutes": 120, "retry_on_timeout": True}
        },
        {
            "definition_id": "def_002",
            "name": "User Onboarding Workflow",
            "stages": ["create_account", "verify_email", "setup_profile", "welcome_notification"],
            "dependencies": {"verify_email": ["create_account"], "setup_profile": ["verify_email"], "welcome_notification": ["setup_profile"]},
            "timeout_policy": {"max_duration_minutes": 60, "retry_on_timeout": False}
        },
        {
            "definition_id": "def_003",
            "name": "Report Generation",
            "stages": ["gather_data", "analyze", "generate_report", "distribute"],
            "dependencies": {"analyze": ["gather_data"], "generate_report": ["analyze"], "distribute": ["generate_report"]},
            "timeout_policy": {"max_duration_minutes": 180, "retry_on_timeout": True}
        }
    ],
    # Workflow instances (executions)
    "workflow_instances": [
        {
            "n_id": "inst_001",
            "status": "running",
            "progress_percentage": 45,
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:30:00",
            "workflow_type": "def_001"
        },
        {
            "n_id": "inst_002",
            "status": "pending",
            "progress_percentage": 0,
            "created_at": "2024-01-15T11:00:00",
            "updated_at": "2024-01-15T11:00:00",
            "workflow_type": "def_002"
        },
        {
            "n_id": "inst_003",
            "status": "completed",
            "progress_percentage": 100,
            "created_at": "2024-01-14T08:00:00",
            "updated_at": "2024-01-14T09:30:00",
            "workflow_type": "def_003"
        },
        {
            "n_id": "inst_004",
            "status": "failed",
            "progress_percentage": 67,
            "created_at": "2024-01-13T14:00:00",
            "updated_at": "2024-01-13T15:45:00",
            "workflow_type": "def_001"
        }
    ],
    # Task nodes within workflow instances
    "task_nodes": [
        {
            "node_id": "node_001",
            "run_id": "run_001",
            "instance_id": "inst_001",
            "status": "completed",
            "start_time": "2024-01-15T10:00:00",
            "end_time": "2024-01-15T10:15:00",
            "error_log": None
        },
        {
            "node_id": "node_002",
            "run_id": "run_002",
            "instance_id": "inst_001",
            "status": "running",
            "start_time": "2024-01-15T10:15:00",
            "end_time": None,
            "error_log": None
        },
        {
            "node_id": "node_003",
            "run_id": "run_003",
            "instance_id": "inst_003",
            "status": "completed",
            "start_time": "2024-01-14T08:00:00",
            "end_time": "2024-01-14T09:30:00",
            "error_log": None
        },
        {
            "node_id": "node_004",
            "run_id": "run_004",
            "instance_id": "inst_004",
            "status": "failed",
            "start_time": "2024-01-13T15:00:00",
            "end_time": "2024-01-13T15:45:00",
            "error_log": "Connection timeout during data load stage"
        }
    ],
    # Valid status transitions
    "valid_transitions": {
        "pending": ["running", "cancelled"],
        "running": ["completed", "failed", "cancelled"],
        "completed": [],
        "failed": ["pending", "running"],
        "cancelled": ["pending"]
    },
    # Counter for generating unique IDs
    "id_counter": {
        "instance": 5,
        "node": 5,
        "run": 5
    }
}


class WorkflowManagementSystem:
    """
    A workflow management system environment for defining, executing, and monitoring
    sequences of tasks with state tracking, progress management, and status transitions.
    
    This environment supports creating workflow instances from definitions, tracking
    progress, managing task nodes, and handling status transitions with proper validation.
    """
    
    def __init__(self) -> None:
        """
        Initialize the WorkflowManagementSystem with default state attributes.
        
        Sets up all state variables with type hints and initializes the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.workflow_definitions: List[Dict[str, Any]] = []
        self.workflow_instances: List[Dict[str, Any]] = []
        self.task_nodes: List[Dict[str, Any]] = []
        self.valid_transitions: Dict[str, List[str]] = {}
        self.id_counter: Dict[str, int] = {}
        
        self._api_description: str = "A workflow management system for defining, executing, and monitoring task sequences with progress tracking and status management."
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data. If empty or keys missing,
                     falls back to DEFAULT_STATE values.
            long_context: Flag for extended context scenarios (reserved for future use).
        
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
        
        Provides a complete snapshot of all state variables for inspection,
        debugging, or state persistence purposes.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all current state variables:
                - workflow_definitions: List of workflow blueprints
                - workflow_instances: List of workflow executions
                - task_nodes: List of individual task records
                - valid_transitions: Map of allowed status transitions
                - id_counter: Current counters for ID generation
        """
        return {
            "workflow_definitions": deepcopy(self.workflow_definitions),
            "workflow_instances": deepcopy(self.workflow_instances),
            "task_nodes": deepcopy(self.task_nodes),
            "valid_transitions": deepcopy(self.valid_transitions),
            "id_counter": deepcopy(self.id_counter)
        }
    
    def _timestamp(self) -> str:
        """
        Generate a consistent ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _generate_instance_id(self) -> str:
        """
        Generate a unique workflow instance ID.
        
        Args:
            None
        
        Returns:
            str: A unique instance ID in format 'inst_XXX'.
        """
        new_id = f"inst_{self.id_counter['instance']:03d}"
        self.id_counter['instance'] += 1
        return new_id
    
    def _generate_node_id(self) -> str:
        """
        Generate a unique task node ID.
        
        Args:
            None
        
        Returns:
            str: A unique node ID in format 'node_XXX'.
        """
        new_id = f"node_{self.id_counter['node']:03d}"
        self.id_counter['node'] += 1
        return new_id
    
    def _generate_run_id(self) -> str:
        """
        Generate a unique run ID.
        
        Args:
            None
        
        Returns:
            str: A unique run ID in format 'run_XXX'.
        """
        new_id = f"run_{self.id_counter['run']:03d}"
        self.id_counter['run'] += 1
        return new_id
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_workflow_instance_by_id(self, n_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a workflow instance using its unique n_id.
        
        Args:
            n_id: The unique identifier of the workflow instance to retrieve.
        
        Returns:
            Dict[str, Any]: The workflow instance data if found, or an error dictionary
                           if the instance does not exist.
        """
        for instance in self.workflow_instances:
            if instance["n_id"] == n_id:
                return {"success": True, "instance": deepcopy(instance)}
        return {"error": f"Workflow instance with n_id '{n_id}' not found"}
    
    def get_workflow_definition_by_id(self, definition_id: str) -> Dict[str, Any]:
        """
        Retrieve the definition (blueprint) of a workflow by definition_id.
        
        Args:
            definition_id: The unique identifier of the workflow definition.
        
        Returns:
            Dict[str, Any]: The workflow definition data including stages and dependencies,
                           or an error dictionary if not found.
        """
        for definition in self.workflow_definitions:
            if definition["definition_id"] == definition_id:
                return {"success": True, "definition": deepcopy(definition)}
        return {"error": f"Workflow definition with definition_id '{definition_id}' not found"}
    
    def list_all_workflow_definitions(self) -> Dict[str, Any]:
        """
        List all available workflow templates in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing a list of all workflow definitions.
        """
        return {"success": True, "definitions": deepcopy(self.workflow_definitions)}
    
    def list_workflow_instances(
        self, 
        status: Optional[str] = None, 
        workflow_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve all workflow instances, optionally filtered by status or workflow type.
        
        Args:
            status: Optional filter for instance status (e.g., "running", "pending").
            workflow_type: Optional filter for workflow definition type.
        
        Returns:
            Dict[str, Any]: A dictionary containing the filtered list of workflow instances.
        """
        results = []
        for instance in self.workflow_instances:
            if status is not None and instance["status"] != status:
                continue
            if workflow_type is not None and instance["workflow_type"] != workflow_type:
                continue
            results.append(deepcopy(instance))
        return {"success": True, "instances": results}
    
    def list_running_workflow_instances(self) -> Dict[str, Any]:
        """
        Retrieve all workflow instances currently in "running" status.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing the list of running workflow instances.
        """
        running = [deepcopy(inst) for inst in self.workflow_instances if inst["status"] == "running"]
        return {"success": True, "instances": running}
    
    def get_workflow_status(self, n_id: str) -> Dict[str, Any]:
        """
        Return the current status of a given workflow instance.
        
        Args:
            n_id: The unique identifier of the workflow instance.
        
        Returns:
            Dict[str, Any]: The current status of the instance, or an error if not found.
        """
        for instance in self.workflow_instances:
            if instance["n_id"] == n_id:
                return {"success": True, "n_id": n_id, "status": instance["status"]}
        return {"error": f"Workflow instance with n_id '{n_id}' not found"}
    
    def get_workflow_progress(self, n_id: str) -> Dict[str, Any]:
        """
        Return the current progress percentage of a workflow instance.
        
        Args:
            n_id: The unique identifier of the workflow instance.
        
        Returns:
            Dict[str, Any]: The current progress percentage, or an error if not found.
        """
        for instance in self.workflow_instances:
            if instance["n_id"] == n_id:
                return {
                    "success": True, 
                    "n_id": n_id, 
                    "progress_percentage": instance["progress_percentage"]
                }
        return {"error": f"Workflow instance with n_id '{n_id}' not found"}
    
    def get_task_node_by_run_id(self, run_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific task node using its run_id.
        
        Args:
            run_id: The unique run identifier of the task node.
        
        Returns:
            Dict[str, Any]: The task node data if found, or an error dictionary if not found.
        """
        for node in self.task_nodes:
            if node["run_id"] == run_id:
                return {"success": True, "task_node": deepcopy(node)}
        return {"error": f"Task node with run_id '{run_id}' not found"}
    
    def list_task_nodes_by_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Retrieve all task nodes associated with a given workflow instance.
        
        Args:
            instance_id: The n_id of the workflow instance.
        
        Returns:
            Dict[str, Any]: A dictionary containing the list of task nodes for the instance.
        """
        # Verify instance exists
        instance_exists = any(inst["n_id"] == instance_id for inst in self.workflow_instances)
        if not instance_exists:
            return {"error": f"Workflow instance with n_id '{instance_id}' not found"}
        
        nodes = [deepcopy(node) for node in self.task_nodes if node["instance_id"] == instance_id]
        return {"success": True, "task_nodes": nodes}
    
    def get_workflow_error_log(self, n_id: str) -> Dict[str, Any]:
        """
        Retrieve error logs from task nodes of a workflow instance for debugging.
        
        Args:
            n_id: The unique identifier of the workflow instance.
        
        Returns:
            Dict[str, Any]: A dictionary containing error logs from failed task nodes,
                           or an error if the instance is not found.
        """
        instance_exists = any(inst["n_id"] == n_id for inst in self.workflow_instances)
        if not instance_exists:
            return {"error": f"Workflow instance with n_id '{n_id}' not found"}
        
        error_logs = []
        for node in self.task_nodes:
            if node["instance_id"] == n_id and node["error_log"]:
                error_logs.append({
                    "node_id": node["node_id"],
                    "run_id": node["run_id"],
                    "error_log": node["error_log"]
                })
        return {"success": True, "error_logs": error_logs}
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def start_workflow_instance(
        self, 
        definition_id: str, 
        initial_status: str = "pending"
    ) -> Dict[str, Any]:
        """
        Initialize a new workflow instance from a definition.
        
        Args:
            definition_id: The ID of the workflow definition to instantiate.
            initial_status: Initial status, either "pending" or "running".
        
        Returns:
            Dict[str, Any]: The created workflow instance data, or an error dictionary.
        """
        # Validate definition exists
        definition = None
        for d in self.workflow_definitions:
            if d["definition_id"] == definition_id:
                definition = d
                break
        if definition is None:
            return {"error": f"Workflow definition with definition_id '{definition_id}' not found"}
        
        # Validate initial status
        if initial_status not in ["pending", "running"]:
            return {"error": f"Invalid initial_status '{initial_status}'. Must be 'pending' or 'running'"}
        
        timestamp = self._timestamp()
        new_instance = {
            "n_id": self._generate_instance_id(),
            "status": initial_status,
            "progress_percentage": 0,
            "created_at": timestamp,
            "updated_at": timestamp,
            "workflow_type": definition_id
        }
        self.workflow_instances.append(new_instance)
        return {"success": True, "instance": deepcopy(new_instance)}
    
    def update_workflow_progress(self, n_id: str, progress_percentage: int) -> Dict[str, Any]:
        """
        Update the progress_percentage of a workflow instance if its status is "running".
        
        Args:
            n_id: The unique identifier of the workflow instance.
            progress_percentage: The new progress value (must be between 0 and 100).
        
        Returns:
            Dict[str, Any]: Updated instance data, or an error dictionary if validation fails.
        """
        # Validate progress range
        if not isinstance(progress_percentage, int) or progress_percentage < 0 or progress_percentage > 100:
            return {"error": "progress_percentage must be an integer between 0 and 100"}
        
        for instance in self.workflow_instances:
            if instance["n_id"] == n_id:
                # Check status constraint
                if instance["status"] != "running":
                    return {"error": f"Cannot update progress for instance with status '{instance['status']}'. Only 'running' instances can be updated"}
                
                instance["progress_percentage"] = progress_percentage
                instance["updated_at"] = self._timestamp()
                return {"success": True, "instance": deepcopy(instance)}
        
        return {"error": f"Workflow instance with n_id '{n_id}' not found"}
    
    def transition_workflow_status(self, n_id: str, new_status: str) -> Dict[str, Any]:
        """
        Change the status of a workflow instance only along valid transitions.
        
        Args:
            n_id: The unique identifier of the workflow instance.
            new_status: The target status to transition to.
        
        Returns:
            Dict[str, Any]: Updated instance data, or an error if transition is invalid.
        """
        for instance in self.workflow_instances:
            if instance["n_id"] == n_id:
                current_status = instance["status"]
                allowed = self.valid_transitions.get(current_status, [])
                
                if new_status not in allowed:
                    return {
                        "error": f"Invalid status transition from '{current_status}' to '{new_status}'. Allowed transitions: {allowed}"
                    }
                
                instance["status"] = new_status
                instance["updated_at"] = self._timestamp()
                return {"success": True, "instance": deepcopy(instance)}
        
        return {"error": f"Workflow instance with n_id '{n_id}' not found"}
    
    def cancel_workflow_instance(self, n_id: str) -> Dict[str, Any]:
        """
        Set the status of a running or pending workflow instance to "cancelled".
        
        Args:
            n_id: The unique identifier of the workflow instance to cancel.
        
        Returns:
            Dict[str, Any]: Updated instance data, or an error if cancellation is not allowed.
        """
        for instance in self.workflow_instances:
            if instance["n_id"] == n_id:
                current_status = instance["status"]
                if current_status not in ["running", "pending"]:
                    return {
                        "error": f"Cannot cancel instance with status '{current_status}'. Only 'running' or 'pending' instances can be cancelled"
                    }
                
                instance["status"] = "cancelled"
                instance["updated_at"] = self._timestamp()
                return {"success": True, "instance": deepcopy(instance)}
        
        return {"error": f"Workflow instance with n_id '{n_id}' not found"}
    
    def retry_failed_workflow(
        self, 
        n_id: str, 
        reset_to: str = "pending"
    ) -> Dict[str, Any]:
        """
        Reset a failed workflow instance to "pending" or "running" if allowed by policy.
        
        Args:
            n_id: The unique identifier of the failed workflow instance.
            reset_to: The target status to reset to ("pending" or "running").
        
        Returns:
            Dict[str, Any]: Updated instance data, or an error if retry is not allowed.
        """
        if reset_to not in ["pending", "running"]:
            return {"error": f"Invalid reset_to status '{reset_to}'. Must be 'pending' or 'running'"}
        
        for instance in self.workflow_instances:
            if instance["n_id"] == n_id:
                if instance["status"] != "failed":
                    return {
                        "error": f"Cannot retry instance with status '{instance['status']}'. Only 'failed' instances can be retried"
                    }
                
                instance["status"] = reset_to
                instance["progress_percentage"] = 0
                instance["updated_at"] = self._timestamp()
                return {"success": True, "instance": deepcopy(instance)}
        
        return {"error": f"Workflow instance with n_id '{n_id}' not found"}
    
    def create_task_node(
        self, 
        instance_id: str, 
        node_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new task node for a workflow instance with unique run_id.
        
        Args:
            instance_id: The n_id of the workflow instance this node belongs to.
            node_id: Optional custom node ID (auto-generated if not provided).
            run_id: Optional custom run ID (auto-generated if not provided).
        
        Returns:
            Dict[str, Any]: Created task node data, or an error if validation fails.
        """
        # Verify instance exists
        instance_exists = any(inst["n_id"] == instance_id for inst in self.workflow_instances)
        if not instance_exists:
            return {"error": f"Workflow instance with n_id '{instance_id}' not found"}
        
        # Use provided or generate IDs
        actual_node_id = node_id if node_id else self._generate_node_id()
        actual_run_id = run_id if run_id else self._generate_run_id()
        
        # Check run_id uniqueness
        for node in self.task_nodes:
            if node["run_id"] == actual_run_id:
                return {"error": f"Task node with run_id '{actual_run_id}' already exists. run_id must be unique"}
        
        new_node = {
            "node_id": actual_node_id,
            "run_id": actual_run_id,
            "instance_id": instance_id,
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "error_log": None
        }
        self.task_nodes.append(new_node)
        return {"success": True, "task_node": deepcopy(new_node)}
    
    def update_task_node_status(
        self, 
        run_id: str, 
        status: str,
        error_log: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a task node, setting start/end times and error logs as appropriate.
        
        Args:
            run_id: The unique run identifier of the task node.
            status: The new status (e.g., "running", "completed", "failed").
            error_log: Optional error message if status is "failed".
        
        Returns:
            Dict[str, Any]: Updated task node data, or an error if not found.
        """
        valid_statuses = ["pending", "running", "completed", "failed"]
        if status not in valid_statuses:
            return {"error": f"Invalid status '{status}'. Must be one of {valid_statuses}"}
        
        for node in self.task_nodes:
            if node["run_id"] == run_id:
                timestamp = self._timestamp()
                
                # Set start_time when transitioning to running
                if status == "running" and node["start_time"] is None:
                    node["start_time"] = timestamp
                
                # Set end_time when completing or failing
                if status in ["completed", "failed"]:
                    node["end_time"] = timestamp
                
                node["status"] = status
                
                if error_log and status == "failed":
                    node["error_log"] = error_log
                
                return {"success": True, "task_node": deepcopy(node)}
        
        return {"error": f"Task node with run_id '{run_id}' not found"}
    
    def complete_workflow_instance(self, n_id: str) -> Dict[str, Any]:
        """
        Mark a running workflow instance as "completed", updating progress to 100.
        
        Args:
            n_id: The unique identifier of the workflow instance to complete.
        
        Returns:
            Dict[str, Any]: Updated instance data, or an error if completion is not allowed.
        """
        for instance in self.workflow_instances:
            if instance["n_id"] == n_id:
                if instance["status"] != "running":
                    return {
                        "error": f"Cannot complete instance with status '{instance['status']}'. Only 'running' instances can be completed"
                    }
                
                instance["status"] = "completed"
                instance["progress_percentage"] = 100
                instance["updated_at"] = self._timestamp()
                return {"success": True, "instance": deepcopy(instance)}
        
        return {"error": f"Workflow instance with n_id '{n_id}' not found"}
    
    def record_task_node_error(self, run_id: str, error_message: str) -> Dict[str, Any]:
        """
        Append or update an error log for a specific task node during execution failure.
        
        Args:
            run_id: The unique run identifier of the task node.
            error_message: The error message to record.
        
        Returns:
            Dict[str, Any]: Updated task node data, or an error if not found.
        """
        if not error_message or not error_message.strip():
            return {"error": "error_message cannot be empty"}
        
        for node in self.task_nodes:
            if node["run_id"] == run_id:
                # Append to existing error log or create new
                if node["error_log"]:
                    node["error_log"] = f"{node['error_log']}\n{error_message}"
                else:
                    node["error_log"] = error_message
                return {"success": True, "task_node": deepcopy(node)}
        
        return {"error": f"Task node with run_id '{run_id}' not found"}


# Test cases for validating the environment API
__TEST_CASES__ = [
    {
        "name": "Complete workflow lifecycle: start, update progress, and complete",
        "steps": [
            {"tool_call": "start_workflow_instance(definition_id='def_001', initial_status='running')", "expect_success": True},
            {"tool_call": "update_workflow_progress(n_id='inst_005', progress_percentage=50)", "expect_success": True},
            {"tool_call": "update_workflow_progress(n_id='inst_005', progress_percentage=90)", "expect_success": True},
            {"tool_call": "complete_workflow_instance(n_id='inst_005')", "expect_success": True},
            {"tool_call": "get_workflow_status(n_id='inst_005')", "expect_success": True}
        ]
    },
    {
        "name": "Query operations on existing data",
        "steps": [
            {"tool_call": "get_workflow_instance_by_id(n_id='inst_001')", "expect_success": True},
            {"tool_call": "get_workflow_definition_by_id(definition_id='def_001')", "expect_success": True},
            {"tool_call": "list_running_workflow_instances()", "expect_success": True},
            {"tool_call": "list_task_nodes_by_instance(instance_id='inst_001')", "expect_success": True},
            {"tool_call": "get_workflow_error_log(n_id='inst_004')", "expect_success": True}
        ]
    },
    {
        "name": "Task node creation and status updates",
        "steps": [
            {"tool_call": "create_task_node(instance_id='inst_001')", "expect_success": True},
            {"tool_call": "update_task_node_status(run_id='run_005', status='running')", "expect_success": True},
            {"tool_call": "update_task_node_status(run_id='run_005', status='completed')", "expect_success": True},
            {"tool_call": "get_task_node_by_run_id(run_id='run_005')", "expect_success": True}
        ]
    },
    {
        "name": "Error path: invalid operations and constraints",
        "steps": [
            {"tool_call": "get_workflow_instance_by_id(n_id='nonexistent')", "expect_success": False},
            {"tool_call": "update_workflow_progress(n_id='inst_002', progress_percentage=50)", "expect_success": False},
            {"tool_call": "update_workflow_progress(n_id='inst_001', progress_percentage=150)", "expect_success": False},
            {"tool_call": "transition_workflow_status(n_id='inst_003', new_status='running')", "expect_success": False},
            {"tool_call": "complete_workflow_instance(n_id='inst_002')", "expect_success": False}
        ]
    },
    {
        "name": "Retry failed workflow and cancel operations",
        "steps": [
            {"tool_call": "retry_failed_workflow(n_id='inst_004', reset_to='running')", "expect_success": True},
            {"tool_call": "get_workflow_status(n_id='inst_004')", "expect_success": True},
            {"tool_call": "cancel_workflow_instance(n_id='inst_004')", "expect_success": True},
            {"tool_call": "cancel_workflow_instance(n_id='inst_003')", "expect_success": False}
        ]
    }
]