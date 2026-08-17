from copy import deepcopy
from typing import Dict, List, Optional, Union, Any

DEFAULT_STATE = {
    "pipelines": [],
    "workers": {},
    "execution_log": [],
    "pipeline_counter": 1,
    "worker_counter": 1,
    "return_counter": 1,
    "inventory": {},  # Product ID -> stock quantity
    "pending_returns": [],  # Pending return/exchange requests
    "tracking_entries": []  # Logistics tracking records
}

VALID_PIPELINE_STATUSES = ("pending", "in_progress", "awaiting_approval", "completed", "failed", "cancelled", "rolled_back")
VALID_STAGE_STATUSES = ("pending", "in_progress", "completed", "failed", "skipped", "rolled_back")
VALID_EXEC_MODES = ("sequential", "parallel")
VALID_FAILURE_POLICIES = ("abort", "skip", "retry")
VALID_WORKER_STATUSES = ("idle", "busy", "offline", "error")
VALID_RETURN_STATUSES = ("pending", "approved", "rejected", "processed", "shipped_back", "closed")
VALID_INVENTORY_ACTIONS = ("check", "update", "reconcile", "adjust")


class ECommerceOrchestrationEnv:
    """
    E-commerce logistics orchestration environment: a multi-stage orchestration system for automated logistics querying, return/exchange tickets, and inventory reconciliation.

    Attributes:
        pipelines (List[Dict]): All defined pipelines, containing stage definitions.
        workers (Dict[str, Dict]): Registered workers, indexed by worker_id.
        execution_log (List[Dict]): History of all stage executions and state changes.
        pipeline_counter (int): Auto-incrementing pipeline ID counter.
        worker_counter (int): Auto-incrementing worker ID counter.
        inventory (Dict[str, int]): Product ID to stock quantity mapping.
        pending_returns (List[Dict]): List of pending return/exchange requests.
        tracking_entries (List[Dict]): List of logistics tracking records.
    """

    def __init__(self):
        self.pipelines: List[Dict[str, Any]]
        self.workers: Dict[str, Dict[str, Any]]
        self.execution_log: List[Dict[str, Any]]
        self.pipeline_counter: int
        self.worker_counter: int
        self.return_counter: int
        self.inventory: Dict[str, int]
        self.pending_returns: List[Dict[str, Any]]
        self.tracking_entries: List[Dict[str, Any]]
        self._api_description = (
            "This tool provides e-commerce logistics orchestration: define multi-stage pipelines, "
            "register workers (customer service, warehouse, logistics), assign stage tasks, "
            "execute in sequential or parallel mode, with dependency management and failure handling."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load initial state from scenario dictionary.

        Args:
            scenario (dict): Scenario dictionary containing initial state.
            long_context (bool): Reserved parameter, currently unused.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.pipelines = scenario.get("pipelines", DEFAULT_STATE_COPY["pipelines"])
        self.workers = scenario.get("workers", DEFAULT_STATE_COPY["workers"])
        self.execution_log = scenario.get("execution_log", DEFAULT_STATE_COPY["execution_log"])
        self.pipeline_counter = scenario.get("pipeline_counter", DEFAULT_STATE_COPY["pipeline_counter"])
        self.worker_counter = scenario.get("worker_counter", DEFAULT_STATE_COPY["worker_counter"])
        self.return_counter = scenario.get("return_counter", DEFAULT_STATE_COPY["return_counter"])
        self.inventory = scenario.get("inventory", DEFAULT_STATE_COPY["inventory"])
        self.pending_returns = scenario.get("pending_returns", DEFAULT_STATE_COPY["pending_returns"])
        self.tracking_entries = scenario.get("tracking_entries", DEFAULT_STATE_COPY["tracking_entries"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: Dictionary containing all environment state variables, including pipelines,
                  workers, execution log, counters, inventory, pending returns, and logistics tracking records.
        """
        return {
            "pipelines": self.pipelines,
            "workers": self.workers,
            "execution_log": self.execution_log,
            "pipeline_counter": self.pipeline_counter,
            "worker_counter": self.worker_counter,
            "return_counter": self.return_counter,
            "inventory": self.inventory,
            "pending_returns": self.pending_returns,
            "tracking_entries": self.tracking_entries,
        }

    # ── Worker management ───────────────────────────────────────────────────────

    def register_worker(
        self,
        name: str,
        role: str,
        capabilities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Register a new worker that can execute pipeline stages.

        Args:
            name (str): Worker display name.
            role (str): Functional role (e.g. 'customer_service', 'warehouse_manager', 'logistics_coordinator').
            capabilities (List[str]): [Optional] List of operation types this worker can execute.

        Returns:
            worker_id (str): Unique worker identifier.
            worker (Dict): Registered worker record.
        """
        if not name.strip() or not role.strip():
            return {"error": "Worker name and role cannot be empty."}

        worker_id = str(self.worker_counter)
        self.worker_counter += 1

        worker = {
            "worker_id": worker_id,
            "name": name,
            "role": role,
            "capabilities": capabilities or [],
            "status": "idle",
            "task_count": 0,
            "completed_count": 0,
        }
        self.workers[worker_id] = worker
        self._log("worker_registered", {"worker_id": worker_id, "role": role})
        return {"worker_id": worker_id, "worker": worker}

    def unregister_worker(self, worker_id: str) -> Dict[str, str]:
        """
        Remove a worker from the orchestration system.

        Args:
            worker_id (str): ID of the worker to remove.

        Returns:
            status (str): Removal confirmation message.
        """
        if worker_id not in self.workers:
            return {"error": f"Worker '{worker_id}' not found."}
        if self.workers[worker_id]["status"] == "busy":
            return {"error": f"Worker '{worker_id}' is currently busy. Please wait for task completion."}
        del self.workers[worker_id]
        return {"status": f"Worker '{worker_id}' has been unregistered."}

    def list_workers(
        self, role: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered workers, optionally filtered by role or status.

        Args:
            role (str): [Optional] Filter by role.
            status (str): [Optional] Filter by status.

        Returns:
            workers (List[Dict]): List of matching worker records.
        """
        if status and status not in VALID_WORKER_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_WORKER_STATUSES)}"}
        workers = list(self.workers.values())
        if role:
            workers = [w for w in workers if w["role"] == role]
        if status:
            workers = [w for w in workers if w["status"] == status]
        return {"workers": workers}

    # ── Pipeline definition ─────────────────────────────────────────────────────────

    def define_pipeline(
        self,
        name: str,
        stages: List[Dict[str, Any]],
        mode: str = "sequential",
    ) -> Dict[str, Any]:
        """
        Define a new pipeline with an ordered list of stages.

        Args:
            name (str): Pipeline name.
            stages (List[Dict]): Ordered list of stage definitions. Each stage must contain:
                - stage_id (str): Unique stage identifier within this pipeline.
                - name (str): Human-readable stage name.
                - action (str): Type of operation to perform.
                - params (Dict): Parameters for the operation.
                - on_failure (str): [Optional] 'abort', 'skip', or 'retry'. Defaults to 'abort'.
                - max_retries (int): [Optional] Maximum retry count when on_failure='retry'. Defaults to 1.
                - depends_on (List[str]): [Optional] List of other stage IDs that must complete first.
                - assigned_worker (str): [Optional] Worker ID assigned to this stage.
            mode (str): Execution mode -- 'sequential' or 'parallel'. Defaults to 'sequential'.

        Returns:
            pipeline_id (int): Unique pipeline identifier.
            pipeline (Dict): Created pipeline with all initialized stages.
        """
        if not stages:
            return {"error": "At least one stage is required."}
        if mode not in VALID_EXEC_MODES:
            return {"error": f"Invalid mode '{mode}'. Must be one of: {', '.join(VALID_EXEC_MODES)}"}

        stage_ids = [s["stage_id"] for s in stages]
        if len(stage_ids) != len(set(stage_ids)):
            return {"error": "Duplicate stage_id values are not allowed within a pipeline."}

        for stage in stages:
            required = ("stage_id", "name", "action")
            for field in required:
                if field not in stage:
                    return {"error": f"Stage '{stage.get('stage_id', '?')}' is missing required field '{field}'."}

        pipeline_id = self.pipeline_counter
        self.pipeline_counter += 1

        initialized_stages = []
        for i, stage in enumerate(stages):
            failure_policy = stage.get("on_failure", "abort")
            if failure_policy not in VALID_FAILURE_POLICIES:
                failure_policy = "abort"

            s = {
                "stage_id": stage["stage_id"],
                "name": stage["name"],
                "action": stage["action"],
                "params": stage.get("params", {}),
                "on_failure": failure_policy,
                "max_retries": stage.get("max_retries", 1),
                "depends_on": stage.get("depends_on", []),
                "assigned_worker": stage.get("assigned_worker"),
                "status": "pending",
                "result": None,
                "order": i,
                "retry_count": 0,
            }
            initialized_stages.append(s)

        pipeline = {
            "pipeline_id": pipeline_id,
            "name": name,
            "mode": mode,
            "status": "pending",
            "stages": initialized_stages,
            "current_stage_index": 0,
            "rollback_log": [],
        }
        self.pipelines.append(pipeline)
        self._log("pipeline_defined", {
            "pipeline_id": pipeline_id,
            "name": name,
            "stage_count": len(stages),
            "mode": mode
        })
        return {"pipeline_id": pipeline_id, "pipeline": pipeline}

    def get_pipeline(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Retrieve the full state of a pipeline.

        Args:
            pipeline_id (int): Pipeline ID.

        Returns:
            pipeline (Dict): Complete pipeline object containing all stages and state.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        return {"pipeline": pl}

    def list_pipelines(self, status: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all pipelines, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by pipeline status.

        Returns:
            pipelines (List[Dict]): List of matching pipeline summaries.
        """
        if status and status not in VALID_PIPELINE_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_PIPELINE_STATUSES)}"}
        pls = self.pipelines
        if status:
            pls = [p for p in pls if p["status"] == status]
        summaries = []
        for p in pls:
            completed = sum(1 for s in p["stages"] if s["status"] == "completed")
            summaries.append({
                "pipeline_id": p["pipeline_id"],
                "name": p["name"],
                "mode": p["mode"],
                "status": p["status"],
                "progress": f"{completed}/{len(p['stages'])}",
                "current_stage_index": p["current_stage_index"],
            })
        return {"pipelines": summaries}

    # ── Stage execution ─────────────────────────────────────────────────────────

    def assign_stage(self, pipeline_id: int, stage_id: str, worker_id: str) -> Dict[str, Any]:
        """
        Assign a worker to a specific stage in a pipeline.

        Args:
            pipeline_id (int): Pipeline ID.
            stage_id (str): Stage ID within the pipeline.
            worker_id (str): Worker ID to assign.

        Returns:
            stage_id (str): Updated stage ID.
            assigned_worker (str): Assigned worker ID.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        if worker_id not in self.workers:
            return {"error": f"Worker '{worker_id}' not found."}
        stage = self._find_stage(pl, stage_id)
        if not stage:
            return {"error": f"Stage '{stage_id}' not found in pipeline {pipeline_id}."}
        stage["assigned_worker"] = worker_id
        self._log("stage_assigned", {
            "pipeline_id": pipeline_id,
            "stage_id": stage_id,
            "worker_id": worker_id
        })
        return {"stage_id": stage_id, "assigned_worker": worker_id}

    def execute_stage(self, pipeline_id: int, stage_id: str) -> Dict[str, Any]:
        """
        Execute a single stage within a pipeline.

        Validates dependencies, marks assigned worker as busy, simulates execution,
        and handles result based on failure policy.

        Args:
            pipeline_id (int): Pipeline ID.
            stage_id (str): Stage ID to execute.

        Returns:
            stage_id (str): Executed stage ID.
            status (str): Execution result -- 'completed' or 'failed'.
            result (Dict): Stage execution output.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}

        stage = self._find_stage(pl, stage_id)
        if not stage:
            return {"error": f"Stage '{stage_id}' not found in pipeline {pipeline_id}."}
        if stage["status"] not in ("pending", "failed"):
            return {"error": f"Stage '{stage_id}' is already in {stage['status']} status."}

        for dep_id in stage.get("depends_on", []):
            dep_stage = self._find_stage(pl, dep_id)
            if not dep_stage:
                return {"error": f"Dependency '{dep_id}' not found in pipeline."}
            if dep_stage["status"] != "completed":
                return {"error": f"Cannot execute '{stage_id}': dependency '{dep_id}' is not completed."}

        worker_id = stage.get("assigned_worker")
        if worker_id and worker_id in self.workers:
            self.workers[worker_id]["status"] = "busy"

        stage["status"] = "in_progress"
        self._log("stage_started", {"pipeline_id": pipeline_id, "stage_id": stage_id})

        success, result = self._simulate_ecommerce_stage_outcome(stage, pl)

        if success:
            stage["status"] = "completed"
            stage["result"] = result
            self._log("stage_completed", {"pipeline_id": pipeline_id, "stage_id": stage_id})
        else:
            stage["status"] = "failed"
            stage["result"] = result
            self._handle_stage_failure(pl, stage)
            self._log("stage_failed", {
                "pipeline_id": pipeline_id,
                "stage_id": stage_id,
                "result": result
            })

        if worker_id and worker_id in self.workers:
            self.workers[worker_id]["status"] = "idle"
            self.workers[worker_id]["task_count"] += 1
            if success:
                self.workers[worker_id]["completed_count"] += 1

        return {"stage_id": stage_id, "status": stage["status"], "result": result}

    def execute_pipeline(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Execute all pending stages in a pipeline sequentially or in parallel.

        In sequential mode, stages are executed in order, respecting ordering and dependencies.
        In parallel mode, all stages whose dependencies are satisfied execute together.

        Args:
            pipeline_id (int): Pipeline ID.

        Returns:
            pipeline_id (int): Executed pipeline ID.
            status (str): Overall pipeline status.
            stage_results (Dict[str, str]): Status of each stage.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        if pl["status"] not in ("pending", "in_progress"):
            return {"error": f"Pipeline {pipeline_id} is already in {pl['status']} status."}

        pl["status"] = "in_progress"
        stage_results = {}

        if pl["mode"] == "parallel":
            pending = [s for s in pl["stages"] if s["status"] == "pending"]
            for stage in pending:
                deps_met = all(
                    self._find_stage(pl, d) and self._find_stage(pl, d)["status"] == "completed"
                    for d in stage.get("depends_on", [])
                )
                if deps_met:
                    result = self.execute_stage(pipeline_id, stage["stage_id"])
                    stage_results[stage["stage_id"]] = result.get("status", "unknown")
        else:
            for stage in pl["stages"]:
                if stage["status"] == "pending":
                    result = self.execute_stage(pipeline_id, stage["stage_id"])
                    stage_results[stage["stage_id"]] = result.get("status", "unknown")
                    if stage["status"] == "failed" and stage.get("on_failure") == "abort":
                        break

        all_done = all(s["status"] in ("completed", "skipped", "failed") for s in pl["stages"])
        if all_done:
            had_failure = any(s["status"] == "failed" for s in pl["stages"])
            pl["status"] = "failed" if had_failure else "completed"

        return {"pipeline_id": pipeline_id, "status": pl["status"], "stage_results": stage_results}

    # ── E-commerce specific features ─────────────────────────────────────────────────────

    def query_logistics_status(self, tracking_number: str) -> Dict[str, Any]:
        """
        Query the logistics status of a specified tracking number.

        Args:
            tracking_number (str): The tracking number to query.

        Returns:
            tracking_number (str): Tracking number.
            status (str): Logistics status.
            location (str): Current location.
            timestamp (str): Status update timestamp.
        """
        if not tracking_number.strip():
            return {"error": "Tracking number cannot be empty."}
        
        entry = None
        for track in self.tracking_entries:
            if track.get("tracking_number") == tracking_number:
                entry = track
                break
        
        if not entry:
            entry = {
                "tracking_number": tracking_number,
                "status": "Shipped",
                "location": "Transit hub",
                "timestamp": f"t+{self.pipeline_counter}"
            }
            self.tracking_entries.append(entry)
        
        self._log("logistics_queried", {
            "tracking_number": tracking_number,
            "status": entry["status"]
        })
        return {
            "tracking_number": tracking_number,
            "status": entry["status"],
            "location": entry.get("location", "Unknown"),
            "timestamp": entry["timestamp"]
        }

    def submit_return_request(self, order_id: str, product_id: str, reason: str) -> Dict[str, Any]:
        """
        Submit a return/exchange request.

        Args:
            order_id (str): Order ID.
            product_id (str): Product ID.
            reason (str): Return/exchange reason.

        Returns:
            return_id (str): Return/exchange request ID.
            request (Dict): Request details.
        """
        if not all([order_id.strip(), product_id.strip(), reason.strip()]):
            return {"error": "Order ID, product ID, and reason cannot be empty."}
        
        return_id = f"RTN{self.return_counter:06d}"
        self.return_counter += 1
        return_request = {
            "return_id": return_id,
            "order_id": order_id,
            "product_id": product_id,
            "reason": reason,
            "status": "pending",
            "submitted_at": f"t+{self.pipeline_counter}",
            "assigned_to": None
        }
        
        self.pending_returns.append(return_request)
        self._log("return_submitted", {
            "return_id": return_id,
            "order_id": order_id,
            "product_id": product_id
        })
        return {"return_id": return_id, "request": return_request}

    def process_return_request(self, return_id: str, action: str, notes: str = "") -> Dict[str, Any]:
        """
        Process a return/exchange request.

        Args:
            return_id (str): Return/exchange request ID.
            action (str): Processing action -- 'approve' or 'reject'.
            notes (str): [Optional] Processing notes.

        Returns:
            return_id (str): Processed return/exchange request ID.
            action (str): Action performed.
            new_status (str): New request status.
        """
        if action not in ("approve", "reject"):
            return {"error": "Invalid action, must be 'approve' or 'reject'."}
        
        request = None
        for req in self.pending_returns:
            if req.get("return_id") == return_id:
                request = req
                break
        
        if not request:
            return {"error": f"Return/exchange request '{return_id}' not found."}
        
        new_status = "approved" if action == "approve" else "rejected"
        request["status"] = new_status
        request["processed_at"] = f"t+{self.pipeline_counter}"
        request["processor_notes"] = notes
        
        if action == "approve" and "product_id" in request:
            product_id = request["product_id"]
            if product_id in self.inventory:
                self.inventory[product_id] += 1
        
        self._log("return_processed", {
            "return_id": return_id,
            "action": action,
            "new_status": new_status
        })
        return {
            "return_id": return_id,
            "action": action,
            "new_status": new_status,
            "notes": notes
        }

    def reconcile_inventory(self, product_id: str, actual_count: int) -> Dict[str, Any]:
        """
        Reconcile inventory for a specified product.

        Args:
            product_id (str): Product ID.
            actual_count (int): Actual inventory quantity.

        Returns:
            product_id (str): Product ID.
            discrepancy (int): Discrepancy amount (positive means system overcount, negative means undercount).
            system_count (int): Inventory quantity in system records.
            actual_count (int): Actual inventory quantity.
        """
        if actual_count < 0:
            return {"error": "Inventory quantity cannot be negative."}
        
        system_count = self.inventory.get(product_id, 0)
        discrepancy = system_count - actual_count
        
        self._log("inventory_reconciled", {
            "product_id": product_id,
            "system_count": system_count,
            "actual_count": actual_count,
            "discrepancy": discrepancy
        })
        
        return {
            "product_id": product_id,
            "discrepancy": discrepancy,
            "system_count": system_count,
            "actual_count": actual_count
        }

    def adjust_inventory(self, product_id: str, adjustment: int, reason: str) -> Dict[str, Any]:
        """
        Adjust the inventory quantity of a specified product.

        Args:
            product_id (str): Product ID.
            adjustment (int): Adjustment amount (positive increases, negative decreases).
            reason (str): Reason for adjustment.

        Returns:
            product_id (str): Product ID.
            new_count (int): Adjusted inventory quantity.
            adjustment (int): Adjustment amount.
        """
        current = self.inventory.get(product_id, 0)
        new_count = current + adjustment

        if new_count < 0:
            return {"error": f"Adjusted inventory cannot be negative. Current: {current}, Adjustment: {adjustment}"}
        
        self.inventory[product_id] = new_count
        self._log("inventory_adjusted", {
            "product_id": product_id,
            "old_count": current,
            "adjustment": adjustment,
            "new_count": new_count,
            "reason": reason
        })
        return {
            "product_id": product_id,
            "new_count": new_count,
            "adjustment": adjustment,
            "reason": reason
        }

    # ── Rollback and retry ───────────────────────────────────────────────────────

    def rollback_stage(self, pipeline_id: int, stage_id: str) -> Dict[str, Any]:
        """
        Roll back a completed stage by executing its compensation action.

        Args:
            pipeline_id (int): Pipeline ID.
            stage_id (str): Stage ID to roll back.

        Returns:
            stage_id (str): Rolled back stage ID.
            status (str): New status -- 'rolled_back'.
            rollback_result (Dict): Result of the compensation action.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        stage = self._find_stage(pl, stage_id)
        if not stage:
            return {"error": f"Stage '{stage_id}' not found in pipeline {pipeline_id}."}
        if stage["status"] != "completed":
            return {"error": f"Stage '{stage_id}' is in {stage['status']} status, not completed. Cannot roll back."}
        
        rollback_result = {
            "action": f"compensate_{stage['action']}",
            "original_result": stage["result"],
            "compensation_performed": True
        }
        stage["status"] = "rolled_back"
        stage["result"] = None
        pl["rollback_log"].append({
            "stage_id": stage_id,
            "rolled_back_at": f"t+{self.pipeline_counter}"
        })
        self._log("stage_rolled_back", {"pipeline_id": pipeline_id, "stage_id": stage_id})
        return {
            "stage_id": stage_id,
            "status": "rolled_back",
            "rollback_result": rollback_result
        }

    def retry_stage(self, pipeline_id: int, stage_id: str) -> Dict[str, Any]:
        """
        Re-execute a failed stage if it has remaining retry attempts.

        Args:
            pipeline_id (int): Pipeline ID.
            stage_id (str): Stage ID to retry.

        Returns:
            stage_id (str): Retried stage ID.
            status (str): New execution status.
            result (Dict): Execution result.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        stage = self._find_stage(pl, stage_id)
        if not stage:
            return {"error": f"Stage '{stage_id}' not found in pipeline {pipeline_id}."}
        if stage["status"] != "failed":
            return {"error": f"Stage '{stage_id}' is not in failed status."}
        if stage["retry_count"] >= stage.get("max_retries", 1):
            return {"error": f"Stage '{stage_id}' has exhausted all {stage['max_retries']} retry attempts."}
        
        stage["status"] = "pending"
        stage["retry_count"] += 1
        self._log("stage_retry", {
            "pipeline_id": pipeline_id,
            "stage_id": stage_id,
            "attempt": stage["retry_count"]
        })
        return self.execute_stage(pipeline_id, stage_id)

    # ── Results collection ─────────────────────────────────────────────────────────

    def collect_results(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Collect aggregated results from all completed stages in a pipeline.

        Args:
            pipeline_id (int): Pipeline ID.

        Returns:
            pipeline_id (int): Pipeline ID.
            results (Dict[str, Any]): Results indexed by stage_id.
            summary (Dict): Pipeline status summary.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        results = {}
        for stage in pl["stages"]:
            results[stage["stage_id"]] = {
                "status": stage["status"],
                "result": stage.get("result"),
                "assigned_worker": stage.get("assigned_worker"),
            }
        summary = {
            "total_stages": len(pl["stages"]),
            "completed": sum(1 for s in pl["stages"] if s["status"] == "completed"),
            "failed": sum(1 for s in pl["stages"] if s["status"] == "failed"),
            "rolled_back": sum(1 for s in pl["stages"] if s["status"] == "rolled_back"),
            "pipeline_status": pl["status"],
        }
        return {"pipeline_id": pipeline_id, "results": results, "summary": summary}

    # ── Inter-worker messaging ────────────────────────────────────────────────────

    def send_message(self, from_worker_id: str, to_worker_id: str, content: str) -> Dict[str, Any]:
        """
        Send a message from one worker to another in the orchestration context.

        Args:
            from_worker_id (str): Sender worker ID.
            to_worker_id (str): Receiver worker ID.
            content (str): Message content.

        Returns:
            message (Dict): Sent message record.
        """
        if from_worker_id not in self.workers:
            return {"error": f"Sender worker '{from_worker_id}' not found."}
        if to_worker_id not in self.workers:
            return {"error": f"Receiver worker '{to_worker_id}' not found."}
        if not content.strip():
            return {"error": "Message content cannot be empty."}
        
        msg = {
            "from": from_worker_id,
            "to": to_worker_id,
            "content": content,
            "timestamp": f"t+{self.pipeline_counter}",
        }
        self._log("worker_message", msg)
        return {"message": msg}

    # ── Helper functions ─────────────────────────────────────────────────────────

    def _find_pipeline(self, pipeline_id: int) -> Optional[Dict[str, Any]]:
        """Find pipeline by ID. Returns None if not found."""
        for p in self.pipelines:
            if p["pipeline_id"] == pipeline_id:
                return p
        return None

    def _find_stage(self, pipeline: Dict, stage_id: str) -> Optional[Dict[str, Any]]:
        """Find stage by stage_id in pipeline. Returns None if not found."""
        for s in pipeline["stages"]:
            if s["stage_id"] == stage_id:
                return s
        return None

    def _simulate_ecommerce_stage_outcome(self, stage: Dict, pipeline: Dict) -> tuple:
        """Simulate stage execution. Returns (success: bool, result: dict)."""
        action = stage["action"]
        params = stage.get("params", {})

        if action == "query_logistics":
            tracking_num = params.get("tracking_number", "UNKNOWN")
            success = True
            result = {
                "stage_id": stage["stage_id"],
                "action": action,
                "params": params,
                "output": f"Logistics query successful - Tracking number: {tracking_num}",
                "status": "In transit",
                "execution_time_ms": 120,
            }
        elif action == "process_return":
            return_id = params.get("return_id", "UNKNOWN")
            success = True
            result = {
                "stage_id": stage["stage_id"],
                "action": action,
                "params": params,
                "output": f"Return processing successful - Request ID: {return_id}",
                "execution_time_ms": 200,
            }
        elif action == "reconcile_inventory":
            product_id = params.get("product_id", "UNKNOWN")
            success = True
            result = {
                "stage_id": stage["stage_id"],
                "action": action,
                "params": params,
                "output": f"Inventory reconciliation successful - Product: {product_id}",
                "execution_time_ms": 180,
            }
        elif action == "adjust_inventory":
            product_id = params.get("product_id", "UNKNOWN")
            adjustment = params.get("adjustment", 0)
            success = adjustment >= 0 or self.inventory.get(product_id, 0) >= abs(adjustment)
            result = {
                "stage_id": stage["stage_id"],
                "action": action,
                "params": params,
                "output": f"Inventory adjustment {'successful' if success else 'failed'} - Product: {product_id}",
                "execution_time_ms": 150,
            }
        else:
            success = True
            result = {
                "stage_id": stage["stage_id"],
                "action": action,
                "params": params,
                "output": f"Simulated execution of stage '{stage['name']}' ({action}).",
                "execution_time_ms": 150,
            }

        return success, result

    def _handle_stage_failure(self, pipeline: Dict, stage: Dict):
        """Apply failure policy for a failed stage."""
        policy = stage.get("on_failure", "abort")
        if policy == "skip":
            stage["status"] = "skipped"
        elif policy == "retry":
            if stage["retry_count"] < stage.get("max_retries", 1):
                stage["status"] = "pending"
                stage["retry_count"] += 1
        elif policy == "abort":
            pipeline["status"] = "failed"

    def _log(self, event: str, detail: Dict) -> None:
        """Add an entry to the execution log."""
        self.execution_log.append({
            "event": event,
            "detail": detail,
            "timestamp": f"t+{self.pipeline_counter}"
        })