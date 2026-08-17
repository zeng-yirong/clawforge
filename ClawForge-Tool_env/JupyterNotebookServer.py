"""
Jupyter Notebook Server Environment API

A web-based interactive environment that allows users to create and manage documents
combining live code, equations, visualizations, and narrative text.
"""

import time
import uuid
from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

# Default initial state with sample data for all entities
DEFAULT_STATE: Dict[str, Any] = {
    "notebooks": {
        "nb_001": {
            "notebook_id": "nb_001",
            "name": "Data Analysis",
            "path": "/home/user/notebooks/data_analysis.ipynb",
            "cells": ["cell_001", "cell_002", "cell_003"],
            "language": "python",
            "saved_version": 1,
            "current_version": 1,
            "last_modified": "2024-01-15T10:30:00",
            "created_at": "2024-01-15T10:00:00",
            "metadata": {}
        },
        "nb_002": {
            "notebook_id": "nb_002",
            "name": "Machine Learning",
            "path": "/home/user/notebooks/ml_project.ipynb",
            "cells": ["cell_004", "cell_005"],
            "language": "python",
            "saved_version": 2,
            "current_version": 3,
            "last_modified": "2024-01-15T11:45:00",
            "created_at": "2024-01-15T11:00:00",
            "metadata": {}
        },
        "nb_003": {
            "notebook_id": "nb_003",
            "name": "Statistics Report",
            "path": "/home/user/notebooks/stats_report.ipynb",
            "cells": ["cell_006", "cell_007", "cell_008"],
            "language": "r",
            "saved_version": 1,
            "current_version": 1,
            "last_modified": "2024-01-14T09:00:00",
            "created_at": "2024-01-14T08:30:00",
            "metadata": {}
        }
    },
    "cells": {
        "cell_001": {
            "cell_id": "cell_001",
            "notebook_id": "nb_001",
            "cell_type": "code",
            "source": "import pandas as pd\ndf = pd.read_csv('data.csv')",
            "execution_count": 1,
            "outputs": [{"output_type": "stream", "text": ""}],
            "metadata": {}
        },
        "cell_002": {
            "cell_id": "cell_002",
            "notebook_id": "nb_001",
            "cell_type": "markdown",
            "source": "# Data Analysis\nThis notebook analyzes the dataset.",
            "execution_count": None,
            "outputs": [],
            "metadata": {}
        },
        "cell_003": {
            "cell_id": "cell_003",
            "notebook_id": "nb_001",
            "cell_type": "code",
            "source": "df.head()",
            "execution_count": 2,
            "outputs": [{"output_type": "execute_result", "data": {"text/plain": "DataFrame output"}}],
            "metadata": {}
        },
        "cell_004": {
            "cell_id": "cell_004",
            "notebook_id": "nb_002",
            "cell_type": "code",
            "source": "from sklearn.model_selection import train_test_split",
            "execution_count": 1,
            "outputs": [],
            "metadata": {}
        },
        "cell_005": {
            "cell_id": "cell_005",
            "notebook_id": "nb_002",
            "cell_type": "code",
            "source": "X_train, X_test = train_test_split(X, test_size=0.2)",
            "execution_count": None,
            "outputs": [],
            "metadata": {}
        },
        "cell_006": {
            "cell_id": "cell_006",
            "notebook_id": "nb_003",
            "cell_type": "markdown",
            "source": "# Statistics Report",
            "execution_count": None,
            "outputs": [],
            "metadata": {}
        },
        "cell_007": {
            "cell_id": "cell_007",
            "notebook_id": "nb_003",
            "cell_type": "code",
            "source": "summary(data)",
            "execution_count": 1,
            "outputs": [{"output_type": "stream", "text": "Summary statistics"}],
            "metadata": {}
        },
        "cell_008": {
            "cell_id": "cell_008",
            "notebook_id": "nb_003",
            "cell_type": "code",
            "source": "plot(data$x, data$y)",
            "execution_count": 2,
            "outputs": [{"output_type": "display_data", "data": {"image/png": "base64..."}}],
            "metadata": {}
        }
    },
    "kernels": {
        "kernel_001": {
            "kernel_id": "kernel_001",
            "notebook_id": "nb_001",
            "kernel_type": "Python 3",
            "status": "idle",
            "last_activity": "2024-01-15T10:30:00",
            "execution_count": 0
        },
        "kernel_002": {
            "kernel_id": "kernel_002",
            "notebook_id": "nb_002",
            "kernel_type": "Python 3",
            "status": "busy",
            "last_activity": "2024-01-15T11:45:00",
            "execution_count": 0
        },
        "kernel_003": {
            "kernel_id": "kernel_003",
            "notebook_id": "nb_003",
            "kernel_type": "R",
            "status": "idle",
            "last_activity": "2024-01-14T09:00:00",
            "execution_count": 0
        }
    },
    "sessions": {
        "session_001": {
            "session_id": "session_001",
            "notebook_id": "nb_001",
            "kernel_id": "kernel_001",
            "connection_time": "2024-01-15T10:00:00",
            "status": "active"
        },
        "session_002": {
            "session_id": "session_002",
            "notebook_id": "nb_002",
            "kernel_id": "kernel_002",
            "connection_time": "2024-01-15T11:00:00",
            "status": "active"
        },
        "session_003": {
            "session_id": "session_003",
            "notebook_id": "nb_003",
            "kernel_id": "kernel_003",
            "connection_time": "2024-01-14T08:30:00",
            "status": "active"
        }
    },
    "supported_kernel_types": ["Python 3", "Python 2", "R", "Julia", "Scala"],
    "next_notebook_id": 4,
    "next_cell_id": 9,
    "next_kernel_id": 4,
    "next_session_id": 4
}


class JupyterNotebookServerAPI:
    """
    Jupyter Notebook Server Environment API.
    
    A web-based interactive environment that allows users to create and manage
    documents combining live code, equations, visualizations, and narrative text.
    It maintains state through notebook files, active kernel sessions, and execution
    context, supporting operations like saving, running code cells, and creating
    new notebooks.
    """

    def __init__(self) -> None:
        """
        Initialize the Jupyter Notebook Server API.
        
        Declares all state attributes with type hints and sets the API description.
        """
        self.notebooks: Dict[str, Dict[str, Any]] = {}
        self.cells: Dict[str, Dict[str, Any]] = {}
        self.kernels: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.supported_kernel_types: List[str] = []
        self.next_notebook_id: int = 1
        self.next_cell_id: int = 1
        self.next_kernel_id: int = 1
        self.next_session_id: int = 1
        
        self._api_description: str = (
            "Jupyter Notebook Server API for managing interactive notebooks, "
            "code execution, and kernel sessions in a web-based computing environment."
        )
        # Fixed timestamp for reproducibility (None means use real time)
        self._fixed_timestamp: Optional[str] = None

    def _timestamp(self) -> str:
        """
        Generate a standardized timestamp string.
        Uses fixed timestamp if set, otherwise real system time.
        
        Returns:
            str: ISO format timestamp string.
        """
        if self._fixed_timestamp is not None:
            return self._fixed_timestamp
        return datetime.now().isoformat(timespec='seconds')

    def set_fixed_timestamp(self, timestamp: str) -> None:
        """
        Set a fixed timestamp for reproducible testing.
        
        Args:
            timestamp: ISO format timestamp string.
        """
        self._fixed_timestamp = timestamp

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data.
            long_context: Flag for extended context loading (not used currently).
        """
        if not scenario:
            scenario = {}
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
        # Optionally set fixed timestamp from scenario
        if "fixed_timestamp" in scenario:
            self._fixed_timestamp = scenario["fixed_timestamp"]
        # Ensure kernels have execution_count field
        for kernel in self.kernels.values():
            if "execution_count" not in kernel:
                kernel["execution_count"] = 0

    def get_env_state(self) -> Dict[str, Any]:
        """
        Return the current state of the environment.
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables
                including notebooks, cells, kernels, sessions, supported kernel
                types, and ID counters.
        """
        return {
            "notebooks": deepcopy(self.notebooks),
            "cells": deepcopy(self.cells),
            "kernels": deepcopy(self.kernels),
            "sessions": deepcopy(self.sessions),
            "supported_kernel_types": deepcopy(self.supported_kernel_types),
            "next_notebook_id": self.next_notebook_id,
            "next_cell_id": self.next_cell_id,
            "next_kernel_id": self.next_kernel_id,
            "next_session_id": self.next_session_id
        }

    # ==================== Query Operations ====================

    def get_notebook_by_id(self, notebook_id: str) -> Dict[str, Any]:
        """
        Retrieve metadata and structure of a notebook by its notebook_id.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            
        Returns:
            Dict[str, Any]: Notebook data including name, path, cells, and last
                modified time, or an error dictionary if not found.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        notebook = self.notebooks[notebook_id]
        return {
            "success": True,
            "notebook_id": notebook["notebook_id"],
            "name": notebook["name"],
            "path": notebook["path"],
            "cells": notebook["cells"],
            "language": notebook["language"],
            "saved_version": notebook["saved_version"],
            "current_version": notebook["current_version"],
            "last_modified": notebook["last_modified"],
            "created_at": notebook.get("created_at", ""),
            "metadata": notebook.get("metadata", {})
        }

    def get_notebook_cells(self, notebook_id: str) -> Dict[str, Any]:
        """
        List all cell_ids and their types in a given notebook.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            
        Returns:
            Dict[str, Any]: List of cells with their IDs and types, or an error
                dictionary if notebook not found.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        notebook = self.notebooks[notebook_id]
        cells_info = []
        for cell_id in notebook["cells"]:
            if cell_id in self.cells:
                cell = self.cells[cell_id]
                cells_info.append({
                    "cell_id": cell["cell_id"],
                    "cell_type": cell["cell_type"]
                })
        
        return {
            "success": True,
            "notebook_id": notebook_id,
            "cells": cells_info
        }

    def get_cell_by_id(self, cell_id: str) -> Dict[str, Any]:
        """
        Retrieve full content and execution state of a specific cell.
        
        Args:
            cell_id: The unique identifier of the cell.
            
        Returns:
            Dict[str, Any]: Cell data including source, outputs, and execution_count,
                or an error dictionary if not found.
        """
        if cell_id not in self.cells:
            return {"success": False, "error": f"Cell with id '{cell_id}' not found"}
        
        cell = self.cells[cell_id]
        return {
            "success": True,
            "cell_id": cell["cell_id"],
            "notebook_id": cell["notebook_id"],
            "cell_type": cell["cell_type"],
            "source": cell["source"],
            "execution_count": cell["execution_count"],
            "outputs": cell["outputs"],
            "metadata": cell.get("metadata", {})
        }

    def check_notebook_modified(self, notebook_id: str) -> Dict[str, Any]:
        """
        Determine whether the current notebook state differs from saved_version.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            
        Returns:
            Dict[str, Any]: Dictionary indicating if unsaved changes exist,
                or an error dictionary if notebook not found.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        notebook = self.notebooks[notebook_id]
        is_modified = notebook["current_version"] != notebook["saved_version"]
        
        return {
            "success": True,
            "notebook_id": notebook_id,
            "is_modified": is_modified,
            "saved_version": notebook["saved_version"],
            "current_version": notebook["current_version"]
        }

    def get_kernel_by_notebook_id(self, notebook_id: str) -> Dict[str, Any]:
        """
        Find the kernel associated with a notebook via session mapping.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            
        Returns:
            Dict[str, Any]: Kernel data if found, or an error dictionary if
                notebook or kernel not found.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        # Find session for this notebook
        session = None
        for s in self.sessions.values():
            if s["notebook_id"] == notebook_id and s["status"] == "active":
                session = s
                break
        
        if not session:
            return {"success": False, "error": f"No active session found for notebook '{notebook_id}'"}
        
        kernel_id = session["kernel_id"]
        if kernel_id not in self.kernels:
            return {"success": False, "error": f"Kernel '{kernel_id}' not found"}
        
        return {"success": True, **deepcopy(self.kernels[kernel_id])}

    def get_session_by_notebook_id(self, notebook_id: str) -> Dict[str, Any]:
        """
        Retrieve the active session for a notebook.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            
        Returns:
            Dict[str, Any]: Session data if found, or an error dictionary if
                notebook or session not found.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        for session in self.sessions.values():
            if session["notebook_id"] == notebook_id and session["status"] == "active":
                return {"success": True, **deepcopy(session)}
        
        return {"success": False, "error": f"No active session found for notebook '{notebook_id}'"}

    def list_running_kernels(self) -> Dict[str, Any]:
        """
        Get all kernels with status 'busy' to monitor active computations.
        
        Returns:
            Dict[str, Any]: List of busy kernels with their details.
        """
        busy_kernels = []
        for kernel in self.kernels.values():
            if kernel["status"] == "busy":
                busy_kernels.append(deepcopy(kernel))
        
        return {
            "success": True,
            "running_kernels": busy_kernels,
            "count": len(busy_kernels)
        }

    def get_notebook_last_modified(self, notebook_id: str) -> Dict[str, Any]:
        """
        Return the timestamp when the notebook was last updated.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            
        Returns:
            Dict[str, Any]: Last modified timestamp, or an error dictionary
                if notebook not found.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        notebook = self.notebooks[notebook_id]
        return {
            "success": True,
            "notebook_id": notebook_id,
            "last_modified": notebook["last_modified"]
        }

    def validate_kernel_type(self, kernel_type: str) -> Dict[str, Any]:
        """
        Check whether a given kernel type is supported by the server.
        
        Args:
            kernel_type: The kernel type to validate (e.g., "Python 3").
            
        Returns:
            Dict[str, Any]: Validation result with supported status.
        """
        is_valid = kernel_type in self.supported_kernel_types
        return {
            "success": True,
            "kernel_type": kernel_type,
            "is_valid": is_valid,
            "supported_types": self.supported_kernel_types
        }

    def list_notebooks(self) -> Dict[str, Any]:
        """
        List all notebooks in the environment.
        
        Returns:
            Dict[str, Any]: List of all notebooks with their basic info.
        """
        notebooks_list = []
        for nb_id, notebook in self.notebooks.items():
            notebooks_list.append({
                "notebook_id": nb_id,
                "name": notebook["name"],
                "path": notebook["path"],
                "language": notebook["language"],
                "last_modified": notebook["last_modified"]
            })
        
        return {
            "success": True,
            "notebooks": notebooks_list,
            "total_count": len(notebooks_list)
        }

    # ==================== State Change Operations ====================

    def save_notebook(self, notebook_id: str) -> Dict[str, Any]:
        """
        Persist the current state of the notebook to storage.
        
        Updates saved_version if changes exist.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            
        Returns:
            Dict[str, Any]: Success status with version info, or an error
                dictionary if notebook not found or no changes to save.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        notebook = self.notebooks[notebook_id]
        
        # Constraint: Only modified notebooks need to be saved
        if notebook["current_version"] == notebook["saved_version"]:
            return {
                "success": True,
                "notebook_id": notebook_id,
                "status": "no_changes",
                "message": "Notebook has no unsaved changes"
            }
        
        # Update saved version
        notebook["saved_version"] = notebook["current_version"]
        notebook["last_modified"] = self._timestamp()
        
        return {
            "success": True,
            "notebook_id": notebook_id,
            "saved_version": notebook["saved_version"],
            "last_modified": notebook["last_modified"]
        }

    def execute_code_cell(self, cell_id: str) -> Dict[str, Any]:
        """
        Run a code cell in the notebook's kernel.
        
        Updates execution_count and outputs, reflects kernel state changes.
        This is a simulated execution (no real code ran).
        
        Args:
            cell_id: The unique identifier of the cell to execute.
            
        Returns:
            Dict[str, Any]: Execution result with updated cell state, or an
                error dictionary if constraints are violated.
        """
        if cell_id not in self.cells:
            return {"success": False, "error": f"Cell with id '{cell_id}' not found"}
        
        cell = self.cells[cell_id]
        
        # Only code cells can be executed
        if cell["cell_type"] != "code":
            return {"success": False, "error": f"Cell '{cell_id}' is not a code cell"}
        
        notebook_id = cell["notebook_id"]
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook '{notebook_id}' not found"}
        
        # Constraint: Notebook must have active kernel session to execute
        session = None
        for s in self.sessions.values():
            if s["notebook_id"] == notebook_id and s["status"] == "active":
                session = s
                break
        
        if not session:
            return {"success": False, "error": f"No active kernel session for notebook '{notebook_id}'"}
        
        kernel_id = session["kernel_id"]
        if kernel_id not in self.kernels:
            return {"success": False, "error": f"Kernel '{kernel_id}' not found"}
        
        kernel = self.kernels[kernel_id]
        
        # Constraint: Kernel status reflects activity
        kernel["status"] = "busy"
        kernel["last_activity"] = self._timestamp()
        kernel["execution_count"] = kernel.get("execution_count", 0) + 1
        
        # Update cell execution state
        cell["execution_count"] = kernel["execution_count"]
        cell["outputs"] = [{"output_type": "execute_result", "data": {"text/plain": f"Executed (execution #{cell['execution_count']})"}}]
        
        # Mark notebook as modified
        notebook = self.notebooks[notebook_id]
        notebook["current_version"] += 1
        notebook["last_modified"] = self._timestamp()
        
        # Set kernel back to idle
        kernel["status"] = "idle"
        
        return {
            "success": True,
            "cell_id": cell_id,
            "execution_count": cell["execution_count"],
            "outputs": cell["outputs"],
            "kernel_status": kernel["status"]
        }

    def create_new_notebook(
        self, 
        name: str, 
        language: str = "python", 
        kernel_type: str = "Python 3",
        path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize a new notebook with specified name, language, and kernel type.
        Automatically starts a kernel and creates an active session.
        
        Args:
            name: The name for the new notebook.
            language: The programming language (e.g., "python", "r").
            kernel_type: The kernel type (e.g., "Python 3").
            path: Optional path for the notebook file.
            
        Returns:
            Dict[str, Any]: New notebook data with assigned ID, or an error
                dictionary if kernel type is invalid.
        """
        # Constraint: Must specify valid kernel type
        if kernel_type not in self.supported_kernel_types:
            return {
                "success": False,
                "error": f"Invalid kernel type '{kernel_type}'. Supported: {self.supported_kernel_types}"
            }
        
        notebook_id = f"nb_{self.next_notebook_id:03d}"
        self.next_notebook_id += 1
        
        if path is None:
            path = f"/home/user/notebooks/{name.lower().replace(' ', '_')}.ipynb"
        
        timestamp = self._timestamp()
        
        self.notebooks[notebook_id] = {
            "notebook_id": notebook_id,
            "name": name,
            "path": path,
            "cells": [],
            "language": language,
            "saved_version": 1,
            "current_version": 1,
            "last_modified": timestamp,
            "created_at": timestamp,
            "metadata": {}
        }
        
        # Auto-start kernel and create session
        kernel_result = self.start_kernel(kernel_type=kernel_type, notebook_id=notebook_id)
        if not kernel_result["success"]:
            return kernel_result
        kernel_id = kernel_result["kernel_id"]
        
        session_result = self.connect_kernel_to_notebook(notebook_id=notebook_id, kernel_id=kernel_id)
        if not session_result["success"]:
            return session_result
        
        return {
            "success": True,
            "notebook_id": notebook_id,
            "name": name,
            "path": path,
            "language": language,
            "kernel_type": kernel_type,
            "kernel_id": kernel_id,
            "session_id": session_result["session_id"],
            "created_at": timestamp
        }

    def add_cell(
        self, 
        notebook_id: str, 
        cell_type: str, 
        source: str = "",
        position: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add a new cell to a notebook.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            cell_type: The type of cell ("code" or "markdown").
            source: The initial source content for the cell.
            position: Optional position to insert the cell (default: end).
            
        Returns:
            Dict[str, Any]: New cell data with assigned ID, or an error
                dictionary if notebook not found or invalid cell type.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        valid_cell_types = ["code", "markdown"]
        if cell_type not in valid_cell_types:
            return {"success": False, "error": f"Invalid cell type '{cell_type}'. Supported: {valid_cell_types}"}
        
        cell_id = f"cell_{self.next_cell_id:03d}"
        self.next_cell_id += 1
        
        timestamp = self._timestamp()
        
        self.cells[cell_id] = {
            "cell_id": cell_id,
            "notebook_id": notebook_id,
            "cell_type": cell_type,
            "source": source,
            "execution_count": None,
            "outputs": [],
            "metadata": {}
        }
        
        notebook = self.notebooks[notebook_id]
        if position is None or position >= len(notebook["cells"]):
            notebook["cells"].append(cell_id)
        else:
            notebook["cells"].insert(position, cell_id)
        
        notebook["current_version"] += 1
        notebook["last_modified"] = timestamp
        
        return {
            "success": True,
            "cell_id": cell_id,
            "notebook_id": notebook_id,
            "cell_type": cell_type,
            "position": position if position is not None else len(notebook["cells"]) - 1
        }

    def delete_cell(self, cell_id: str) -> Dict[str, Any]:
        """
        Remove a cell from its notebook.
        
        Args:
            cell_id: The unique identifier of the cell to delete.
            
        Returns:
            Dict[str, Any]: Success status, or an error dictionary if cell
                not found.
        """
        if cell_id not in self.cells:
            return {"success": False, "error": f"Cell with id '{cell_id}' not found"}
        
        cell = self.cells[cell_id]
        notebook_id = cell["notebook_id"]
        
        # Remove cell from notebook's cell list
        if notebook_id in self.notebooks:
            notebook = self.notebooks[notebook_id]
            if cell_id in notebook["cells"]:
                notebook["cells"].remove(cell_id)
            notebook["current_version"] += 1
            notebook["last_modified"] = self._timestamp()
        
        # Remove cell from cells dict
        del self.cells[cell_id]
        
        return {
            "success": True,
            "cell_id": cell_id,
            "notebook_id": notebook_id,
            "message": "Cell deleted successfully"
        }

    def start_kernel(self, kernel_type: str, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Launch a new kernel process based on the specified kernel_type.
        
        Args:
            kernel_type: The type of kernel to start (e.g., "Python 3").
            notebook_id: Optional notebook ID to associate with the kernel.
            
        Returns:
            Dict[str, Any]: New kernel data with assigned ID, or an error
                dictionary if kernel type is invalid.
        """
        # Validate kernel type
        if kernel_type not in self.supported_kernel_types:
            return {
                "success": False,
                "error": f"Invalid kernel type '{kernel_type}'. Supported: {self.supported_kernel_types}"
            }
        
        if notebook_id and notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        kernel_id = f"kernel_{self.next_kernel_id:03d}"
        self.next_kernel_id += 1
        
        timestamp = self._timestamp()
        
        self.kernels[kernel_id] = {
            "kernel_id": kernel_id,
            "notebook_id": notebook_id,
            "kernel_type": kernel_type,
            "status": "idle",
            "last_activity": timestamp,
            "execution_count": 0
        }
        
        return {
            "success": True,
            "kernel_id": kernel_id,
            "kernel_type": kernel_type,
            "status": "idle"
        }

    def connect_kernel_to_notebook(self, notebook_id: str, kernel_id: str) -> Dict[str, Any]:
        """
        Establish a session linking a notebook to its kernel.
        
        Args:
            notebook_id: The unique identifier of the notebook.
            kernel_id: The unique identifier of the kernel.
            
        Returns:
            Dict[str, Any]: New session data, or an error dictionary if
                notebook or kernel not found.
        """
        if notebook_id not in self.notebooks:
            return {"success": False, "error": f"Notebook with id '{notebook_id}' not found"}
        
        if kernel_id not in self.kernels:
            return {"success": False, "error": f"Kernel with id '{kernel_id}' not found"}
        
        # Check if notebook already has an active session
        for session in self.sessions.values():
            if session["notebook_id"] == notebook_id and session["status"] == "active":
                return {"success": False, "error": f"Notebook '{notebook_id}' already has an active session"}
        
        session_id = f"session_{self.next_session_id:03d}"
        self.next_session_id += 1
        
        timestamp = self._timestamp()
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "notebook_id": notebook_id,
            "kernel_id": kernel_id,
            "connection_time": timestamp,
            "status": "active"
        }
        
        # Update kernel's notebook association
        self.kernels[kernel_id]["notebook_id"] = notebook_id
        
        return {
            "success": True,
            "session_id": session_id,
            "notebook_id": notebook_id,
            "kernel_id": kernel_id
        }

    def shutdown_kernel(self, kernel_id: str) -> Dict[str, Any]:
        """
        Terminate a kernel process and free associated resources.
        
        Args:
            kernel_id: The unique identifier of the kernel to shut down.
            
        Returns:
            Dict[str, Any]: Success status, or an error dictionary if kernel
                not found.
        """
        if kernel_id not in self.kernels:
            return {"success": False, "error": f"Kernel with id '{kernel_id}' not found"}
        
        # Shutdown any sessions using this kernel
        for session_id, session in self.sessions.items():
            if session["kernel_id"] == kernel_id:
                session["status"] = "disconnected"
        
        # Remove kernel
        del self.kernels[kernel_id]
        
        return {"success": True, "kernel_id": kernel_id}

    def list_kernels(self) -> Dict[str, Any]:
        """
        List all kernels.
        
        Returns:
            Dict[str, Any]: A dictionary with success flag and list of kernel info.
        """
        kernel_list = [
            {
                "kernel_id": kid,
                "language": kinfo.get("language", kinfo.get("kernel_type")),
                "status": kinfo["status"],
                "execution_count": kinfo.get("execution_count", 0)
            }
            for kid, kinfo in self.kernels.items()
        ]
        return {
            "success": True,
            "kernels": kernel_list,
            "count": len(kernel_list)
        }

    def create_session(self, name: str, kernel_id: str) -> Dict[str, Any]:
        """
        Create a new session attached to an existing kernel.
        NOTE: This method is kept for backward compatibility; prefer using
        connect_kernel_to_notebook with a notebook_id for full integration.
        Uses the standard session structure with auto-generated notebook_id.
        
        Args:
            name: A human-readable name for the session (ignored, kept for compatibility).
            kernel_id: The kernel to attach this session to.
            
        Returns:
            Dict[str, Any]: Session information including session_id, or an
                error dictionary if kernel not found.
        """
        if kernel_id not in self.kernels:
            return {"success": False, "error": f"Kernel with id '{kernel_id}' not found"}
        
        session_id = f"session_{self.next_session_id:03d}"
        self.next_session_id += 1
        
        timestamp = self._timestamp()
        notebook_id = self.kernels[kernel_id].get("notebook_id")
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "notebook_id": notebook_id,
            "kernel_id": kernel_id,
            "connection_time": timestamp,
            "status": "active"
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "name": name,
            "kernel_id": kernel_id,
            "status": "active"
        }

    def close_session(self, session_id: str) -> Dict[str, Any]:
        """
        Close a session without affecting the underlying kernel.
        
        Args:
            session_id: The unique identifier of the session to close.
            
        Returns:
            Dict[str, Any]: Success status, or an error dictionary if session
                not found.
        """
        if session_id not in self.sessions:
            return {"success": False, "error": f"Session with id '{session_id}' not found"}
        
        del self.sessions[session_id]
        
        return {"success": True, "session_id": session_id}

    def list_sessions(self) -> Dict[str, Any]:
        """
        List all active sessions.
        
        Returns:
            Dict[str, Any]: A dictionary with success flag and list of session info.
        """
        session_list = [
            {
                "session_id": sid,
                "notebook_id": sinfo.get("notebook_id"),
                "kernel_id": sinfo["kernel_id"],
                "status": sinfo["status"],
                "connection_time": sinfo.get("connection_time", "")
            }
            for sid, sinfo in self.sessions.items()
        ]
        return {
            "success": True,
            "sessions": session_list,
            "count": len(session_list)
        }

    def execute_code(self, kernel_id: str, code: str) -> Dict[str, Any]:
        """
        Execute code in a specified kernel (simulated).
        No real code execution; only updates kernel state.
        
        Args:
            kernel_id: The kernel to execute the code in.
            code: The code string to execute (simulated).
            
        Returns:
            Dict[str, Any]: Execution results including output, or an error
                dictionary if kernel not found.
        """
        if kernel_id not in self.kernels:
            return {"success": False, "error": f"Kernel with id '{kernel_id}' not found"}
        
        kernel = self.kernels[kernel_id]
        kernel["status"] = "busy"
        kernel["execution_count"] = kernel.get("execution_count", 0) + 1
        
        result = {
            "success": True,
            "execution_count": kernel["execution_count"],
            "kernel_id": kernel_id,
            "output": f"Code executed successfully (execution {kernel['execution_count']})",
            "error": None
        }
        
        # Simulate execution delay
        kernel["last_activity"] = self._timestamp()
        
        # No real exec: just simulate output
        kernel["status"] = "idle"
        
        return result

    def get_kernel_status(self, kernel_id: str) -> Dict[str, Any]:
        """
        Get the current status of a kernel.
        
        Args:
            kernel_id: The unique identifier of the kernel.
            
        Returns:
            Dict[str, Any]: Kernel status information, or an error dictionary
                if kernel not found.
        """
        if kernel_id not in self.kernels:
            return {"success": False, "error": f"Kernel with id '{kernel_id}' not found"}
        
        kernel = self.kernels[kernel_id]
        return {
            "success": True,
            "kernel_id": kernel_id,
            "status": kernel["status"],
            "language": kernel.get("language", kernel.get("kernel_type")),
            "execution_count": kernel.get("execution_count", 0)
        }


__TEST_CASES__ = [
    {
        "name": "test_start_kernel",
        "input": {"kernel_type": "Python 3"},
        "method": "start_kernel",
        "expected_keys": ["success", "kernel_id"]
    },
    {
        "name": "test_shutdown_kernel_not_found",
        "input": {"kernel_id": "nonexistent"},
        "method": "shutdown_kernel",
        "expected_keys": ["success", "error"]
    },
    {
        "name": "test_list_kernels_empty",
        "input": {},
        "method": "list_kernels",
        "expected": {"success": True, "kernels": [], "count": 0}
    },
    {
        "name": "test_create_session_kernel_not_found",
        "input": {"name": "test_session", "kernel_id": "nonexistent"},
        "method": "create_session",
        "expected_keys": ["success", "error"]
    },
    {
        "name": "test_close_session_not_found",
        "input": {"session_id": "nonexistent"},
        "method": "close_session",
        "expected_keys": ["success", "error"]
    },
    {
        "name": "test_list_sessions_empty",
        "input": {},
        "method": "list_sessions",
        "expected": {"success": True, "sessions": [], "count": 0}
    },
    {
        "name": "test_execute_code_kernel_not_found",
        "input": {"kernel_id": "nonexistent", "code": "x = 1"},
        "method": "execute_code",
        "expected_keys": ["success", "error"]
    },
    {
        "name": "test_get_kernel_status_not_found",
        "input": {"kernel_id": "nonexistent"},
        "method": "get_kernel_status",
        "expected_keys": ["success", "error"]
    },
    {
        "name": "test_full_workflow",
        "workflow": [
            {"method": "create_new_notebook", "input": {"name": "Test Notebook", "language": "python", "kernel_type": "Python 3"}, "save_as": "notebook"},
            {"method": "start_kernel", "input_template": {"kernel_type": "Python 3", "notebook_id": "{notebook.notebook_id}"}, "save_as": "kernel"},
            {"method": "connect_kernel_to_notebook", "input_template": {"notebook_id": "{notebook.notebook_id}", "kernel_id": "{kernel.kernel_id}"}, "save_as": "session"},
            {"method": "execute_code", "input_template": {"kernel_id": "{kernel.kernel_id}", "code": "x = 42"}, "expected_keys": ["success", "output"]},
            {"method": "get_kernel_status", "input_template": {"kernel_id": "{kernel.kernel_id}"}, "expected": {"status": "idle"}},
            {"method": "list_kernels", "input": {}, "expected": {"success": True, "count": 1}},
            {"method": "list_sessions", "input": {}, "expected": {"success": True, "count": 1}},
            {"method": "close_session", "input_template": {"session_id": "{session.session_id}"}, "expected_keys": ["success"]},
            {"method": "shutdown_kernel", "input_template": {"kernel_id": "{kernel.kernel_id}"}, "expected_keys": ["success"]}
        ]
    }
]