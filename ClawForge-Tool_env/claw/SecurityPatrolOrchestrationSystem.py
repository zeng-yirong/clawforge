from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE = {
    "pipelines": [],
    "workers": {},
    "execution_log": [],
    "pipeline_counter": 1,
    "worker_counter": 1,
    "zones": {},
    "alerts": [],
    "alert_counter": 1,
}

VALID_PIPELINE_STATUSES = ("pending", "in_progress", "awaiting_approval", "completed", "failed", "cancelled", "rolled_back")
VALID_STAGE_STATUSES = ("pending", "in_progress", "completed", "failed", "skipped", "rolled_back")
VALID_EXEC_MODES = ("sequential", "parallel")
VALID_FAILURE_POLICIES = ("abort", "skip", "retry")
VALID_WORKER_STATUSES = ("idle", "busy", "offline", "error")
VALID_WORKER_TYPES = ("door_controller", "alarm_dialer", "camera", "sms_gateway", "sensor")
VALID_ZONE_STATUSES = ("normal", "alert", "lockdown", "offline")
VALID_ALERT_LEVELS = ("low", "medium", "high", "critical")


class SecurityPatrolOrchestrationEnv:
    """
    A unified orchestration environment for home/office security patrol and incident response.

    This class models a closed-loop security system where intrusion detection triggers
    a response pipeline: lock doors, dial emergency services, back up video footage to
    the cloud, and notify responsible personnel via SMS. The unit of work is a 'stage'
    within a 'pipeline'. Stages are executed by registered workers (door controllers,
    cameras, alarm dialers, SMS gateways) in sequential or parallel mode with dependency
    management, rollback, and retry support.

    Attributes:
        pipelines (List[Dict]): All defined response pipelines with their stage definitions.
        workers (Dict[str, Dict]): Registered security devices/workers keyed by worker_id.
        execution_log (List[Dict]): History of every stage execution and status change.
        pipeline_counter (int): Auto-incrementing pipeline ID counter.
        worker_counter (int): Auto-incrementing worker ID counter.
        zones (Dict[str, Dict]): Monitored security zones keyed by zone_id.
        alerts (List[Dict]): All intrusion alerts that have been raised.
        alert_counter (int): Auto-incrementing alert ID counter.
    """

    def __init__(self):
        self.pipelines: List[Dict[str, Any]]
        self.workers: Dict[str, Dict[str, Any]]
        self.execution_log: List[Dict[str, Any]]
        self.pipeline_counter: int
        self.worker_counter: int
        self.zones: Dict[str, Dict[str, Any]]
        self.alerts: List[Dict[str, Any]]
        self.alert_counter: int
        self._api_description = (
            "This tool provides a closed-loop security patrol orchestration system: "
            "register security devices as workers, define zones, raise intrusion alerts, "
            "and execute response pipelines that lock doors, dial emergency services, "
            "back up video footage to the cloud, and notify responsible personnel via SMS."
        )

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.pipelines = scenario.get("pipelines", DEFAULT_STATE_COPY["pipelines"])
        self.workers = scenario.get("workers", DEFAULT_STATE_COPY["workers"])
        self.execution_log = scenario.get("execution_log", DEFAULT_STATE_COPY["execution_log"])
        self.pipeline_counter = scenario.get("pipeline_counter", DEFAULT_STATE_COPY["pipeline_counter"])
        self.worker_counter = scenario.get("worker_counter", DEFAULT_STATE_COPY["worker_counter"])
        self.zones = scenario.get("zones", DEFAULT_STATE_COPY["zones"])
        self.alerts = scenario.get("alerts", DEFAULT_STATE_COPY["alerts"])
        self.alert_counter = scenario.get("alert_counter", DEFAULT_STATE_COPY["alert_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including pipelines, workers,
                  execution log, counters, zones, and alerts.
        """
        return {
            "pipelines": self.pipelines,
            "workers": self.workers,
            "execution_log": self.execution_log,
            "pipeline_counter": self.pipeline_counter,
            "worker_counter": self.worker_counter,
            "zones": self.zones,
            "alerts": self.alerts,
            "alert_counter": self.alert_counter,
        }

    # ── Zone management ───────────────────────────────────────────────────

    def register_zone(
        self,
        zone_id: str,
        name: str,
        location: str,
        responsible_contact: str,
    ) -> Dict[str, Any]:
        """
        Register a new security zone to be monitored.

        Args:
            zone_id (str): Unique identifier for the zone (e.g. 'zone_front_door').
            name (str): Human-readable zone name (e.g. 'Front Entrance').
            location (str): Physical location description (e.g. 'Building A, Floor 1').
            responsible_contact (str): Phone number or contact ID of the person responsible for this zone.

        Returns:
            zone_id (str): The registered zone identifier.
            zone (Dict): The created zone record.
        """
        if not zone_id.strip() or not name.strip():
            return {"error": "Zone ID and name must both be non-empty."}
        if zone_id in self.zones:
            return {"error": f"Zone '{zone_id}' is already registered."}
        if not responsible_contact.strip():
            return {"error": "A responsible contact must be provided for the zone."}

        zone = {
            "zone_id": zone_id,
            "name": name,
            "location": location,
            "responsible_contact": responsible_contact,
            "status": "normal",
            "assigned_workers": [],
        }
        self.zones[zone_id] = zone
        self._log("zone_registered", {"zone_id": zone_id, "name": name, "location": location})
        return {"zone_id": zone_id, "zone": zone}

    def get_zone(self, zone_id: str) -> Dict[str, Any]:
        """
        Retrieve the current state of a security zone.

        Args:
            zone_id (str): Zone identifier.

        Returns:
            zone (Dict): Full zone record including status and assigned workers.
        """
        if zone_id not in self.zones:
            return {"error": f"Zone '{zone_id}' not found."}
        return {"zone": self.zones[zone_id]}

    def list_zones(self, status: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all registered security zones, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by zone status. Must be one of:
                          'normal', 'alert', 'lockdown', 'offline'.

        Returns:
            zones (List[Dict]): Matching zone records.
        """
        if status and status not in VALID_ZONE_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_ZONE_STATUSES)}"}
        zones = list(self.zones.values())
        if status:
            zones = [z for z in zones if z["status"] == status]
        return {"zones": zones}

    def update_zone_status(self, zone_id: str, status: str) -> Dict[str, Any]:
        """
        Update the operational status of a security zone.

        Args:
            zone_id (str): Zone identifier.
            status (str): New status. Must be one of: 'normal', 'alert', 'lockdown', 'offline'.

        Returns:
            zone_id (str): The updated zone identifier.
            status (str): The new zone status.
        """
        if zone_id not in self.zones:
            return {"error": f"Zone '{zone_id}' not found."}
        if status not in VALID_ZONE_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_ZONE_STATUSES)}"}
        self.zones[zone_id]["status"] = status
        self._log("zone_status_updated", {"zone_id": zone_id, "status": status})
        return {"zone_id": zone_id, "status": status}

    # ── Alert management ──────────────────────────────────────────────────

    def raise_alert(
        self,
        zone_id: str,
        level: str,
        description: str,
        sensor_worker_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Raise an intrusion alert for a monitored zone.

        This is the entry point for the security response loop. Once an alert is raised,
        a response pipeline should be defined and executed to handle the incident.

        Args:
            zone_id (str): Zone where the intrusion was detected.
            level (str): Alert severity level. Must be one of: 'low', 'medium', 'high', 'critical'.
            description (str): Human-readable description of the detected anomaly.
            sensor_worker_id (str): [Optional] Worker ID of the sensor that detected the intrusion.

        Returns:
            alert_id (int): Unique alert identifier.
            alert (Dict): The created alert record.
        """
        if zone_id not in self.zones:
            return {"error": f"Zone '{zone_id}' not found."}
        if level not in VALID_ALERT_LEVELS:
            return {"error": f"Invalid alert level '{level}'. Must be one of: {', '.join(VALID_ALERT_LEVELS)}"}
        if not description.strip():
            return {"error": "Alert description must be non-empty."}
        if sensor_worker_id and sensor_worker_id not in self.workers:
            return {"error": f"Sensor worker '{sensor_worker_id}' not found."}

        alert_id = self.alert_counter
        self.alert_counter += 1

        alert = {
            "alert_id": alert_id,
            "zone_id": zone_id,
            "level": level,
            "description": description,
            "sensor_worker_id": sensor_worker_id,
            "status": "open",
            "linked_pipeline_id": None,
            "timestamp": datetime.now().isoformat(),
        }
        self.alerts.append(alert)
        self.zones[zone_id]["status"] = "alert"
        self._log("alert_raised", {
            "alert_id": alert_id,
            "zone_id": zone_id,
            "level": level,
            "description": description,
        })
        return {"alert_id": alert_id, "alert": alert}

    def get_alert(self, alert_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific alert by its ID.

        Args:
            alert_id (int): Alert identifier.

        Returns:
            alert (Dict): Full alert record including status and linked pipeline.
        """
        alert = self._find_alert(alert_id)
        if not alert:
            return {"error": f"Alert ID {alert_id} not found."}
        return {"alert": alert}

    def list_alerts(
        self,
        zone_id: Optional[str] = None,
        status: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all alerts, optionally filtered by zone, status, or severity level.

        Args:
            zone_id (str): [Optional] Filter by zone identifier.
            status (str): [Optional] Filter by alert status ('open', 'resolved', 'false_alarm').
            level (str): [Optional] Filter by severity level ('low', 'medium', 'high', 'critical').

        Returns:
            alerts (List[Dict]): Matching alert records.
        """
        if level and level not in VALID_ALERT_LEVELS:
            return {"error": f"Invalid level '{level}'. Must be one of: {', '.join(VALID_ALERT_LEVELS)}"}
        alerts = self.alerts
        if zone_id:
            alerts = [a for a in alerts if a["zone_id"] == zone_id]
        if status:
            alerts = [a for a in alerts if a["status"] == status]
        if level:
            alerts = [a for a in alerts if a["level"] == level]
        return {"alerts": alerts}

    def resolve_alert(self, alert_id: int, resolution: str) -> Dict[str, Any]:
        """
        Mark an alert as resolved or a false alarm, and restore the zone to normal status.

        Args:
            alert_id (int): Alert identifier.
            resolution (str): Resolution type. Must be one of: 'resolved', 'false_alarm'.

        Returns:
            alert_id (int): The resolved alert identifier.
            status (str): New alert status.
        """
        valid_resolutions = ("resolved", "false_alarm")
        if resolution not in valid_resolutions:
            return {"error": f"Invalid resolution '{resolution}'. Must be one of: {', '.join(valid_resolutions)}"}
        alert = self._find_alert(alert_id)
        if not alert:
            return {"error": f"Alert ID {alert_id} not found."}
        if alert["status"] != "open":
            return {"error": f"Alert {alert_id} is already '{alert['status']}', cannot resolve again."}

        alert["status"] = resolution
        zone_id = alert["zone_id"]
        if zone_id in self.zones and self.zones[zone_id]["status"] == "alert":
            self.zones[zone_id]["status"] = "normal"
        self._log("alert_resolved", {"alert_id": alert_id, "resolution": resolution, "zone_id": zone_id})
        return {"alert_id": alert_id, "status": resolution}

    def link_alert_to_pipeline(self, alert_id: int, pipeline_id: int) -> Dict[str, Any]:
        """
        Link an alert to a response pipeline for traceability.

        Args:
            alert_id (int): Alert identifier.
            pipeline_id (int): Pipeline identifier.

        Returns:
            alert_id (int): The alert identifier.
            linked_pipeline_id (int): The linked pipeline identifier.
        """
        alert = self._find_alert(alert_id)
        if not alert:
            return {"error": f"Alert ID {alert_id} not found."}
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        alert["linked_pipeline_id"] = pipeline_id
        self._log("alert_linked_to_pipeline", {"alert_id": alert_id, "pipeline_id": pipeline_id})
        return {"alert_id": alert_id, "linked_pipeline_id": pipeline_id}

    # ── Worker management ─────────────────────────────────────────────────

    def register_worker(
        self,
        name: str = None,
        worker_type: str = None,
        capabilities: Optional[List[str]] = None,
        zone_id: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Register a new security device or service worker.

        Args:
            name (str): Display name for the worker (e.g. 'Front Door Lock', 'Camera-01').
            worker_type (str): Device/service type. Must be one of:
                               'door_controller', 'alarm_dialer', 'camera', 'sms_gateway', 'sensor'.
            capabilities (List[str]): [Optional] List of action types this worker can perform
                                      (e.g. ['lock_door', 'unlock_door']).
            zone_id (str): [Optional] Zone this worker is assigned to.

        Returns:
            worker_id (str): Unique worker identifier.
            worker (Dict): The registered worker record.
        """
        if not isinstance(name, str):
            return {"error": "name must be a string."}
        if not isinstance(worker_type, str):
            return {"error": "worker_type must be a string."}
        if capabilities is not None and not isinstance(capabilities, list):
            return {"error": "capabilities must be a list if provided."}
        if zone_id is not None and not isinstance(zone_id, str):
            return {"error": "zone_id must be a string if provided."}
        if not name.strip():
            return {"error": "Worker name must be non-empty."}
        if worker_type not in VALID_WORKER_TYPES:
            return {"error": f"Invalid worker_type '{worker_type}'. Must be one of: {', '.join(VALID_WORKER_TYPES)}"}
        if zone_id and zone_id not in self.zones:
            return {"error": f"Zone '{zone_id}' not found. Register the zone first."}

        worker_id = str(self.worker_counter)
        self.worker_counter += 1

        worker = {
            "worker_id": worker_id,
            "name": name,
            "worker_type": worker_type,
            "capabilities": capabilities or [],
            "zone_id": zone_id,
            "status": "idle",
            "task_count": 0,
            "completed_count": 0,
        }
        self.workers[worker_id] = worker

        if zone_id and zone_id in self.zones:
            if worker_id not in self.zones[zone_id]["assigned_workers"]:
                self.zones[zone_id]["assigned_workers"].append(worker_id)

        self._log("worker_registered", {"worker_id": worker_id, "worker_type": worker_type, "zone_id": zone_id})
        return {"worker_id": worker_id, "worker": worker}

    def unregister_worker(self, worker_id: str) -> Dict[str, str]:
        """
        Remove a security device or service worker from the system.

        Args:
            worker_id (str): Worker ID to remove.

        Returns:
            status (str): Removal confirmation message.
        """
        if worker_id not in self.workers:
            return {"error": f"Worker '{worker_id}' not found."}
        if self.workers[worker_id]["status"] == "busy":
            return {"error": f"Worker '{worker_id}' is currently busy. Wait for task completion first."}

        zone_id = self.workers[worker_id].get("zone_id")
        if zone_id and zone_id in self.zones:
            assigned = self.zones[zone_id]["assigned_workers"]
            if worker_id in assigned:
                assigned.remove(worker_id)

        del self.workers[worker_id]
        return {"status": f"Worker '{worker_id}' unregistered."}

    def list_workers(
        self,
        worker_type: Optional[str] = None,
        status: Optional[str] = None,
        zone_id: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered workers, optionally filtered by type, status, or zone.

        Args:
            worker_type (str): [Optional] Filter by worker type.
            status (str): [Optional] Filter by worker status ('idle', 'busy', 'offline', 'error').
            zone_id (str): [Optional] Filter by assigned zone.

        Returns:
            workers (List[Dict]): Matching worker records.
        """
        if status and status not in VALID_WORKER_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_WORKER_STATUSES)}"}
        if worker_type and worker_type not in VALID_WORKER_TYPES:
            return {"error": f"Invalid worker_type '{worker_type}'. Must be one of: {', '.join(VALID_WORKER_TYPES)}"}
        workers = list(self.workers.values())
        if worker_type:
            workers = [w for w in workers if w["worker_type"] == worker_type]
        if status:
            workers = [w for w in workers if w["status"] == status]
        if zone_id:
            workers = [w for w in workers if w.get("zone_id") == zone_id]
        return {"workers": workers}

    # ── Pipeline definition ───────────────────────────────────────────────

    def define_pipeline(
        self,
        name: str,
        stages: List[Dict[str, Any]],
        mode: str = "sequential",
    ) -> Dict[str, Any]:
        """
        Define a new security response pipeline with an ordered list of stages.

        Typical stages for an intrusion response pipeline:
          1. lock_door — activate door controller to lock all entry points
          2. dial_emergency — use alarm dialer to call emergency services
          3. backup_video — trigger camera to capture and upload footage to cloud
          4. notify_contact — send SMS via gateway to the responsible person

        Args:
            name (str): Pipeline name (e.g. 'Intrusion Response - Zone A').
            stages (List[Dict]): Ordered list of stage definitions. Each stage requires:
                - stage_id (str): Unique stage identifier within this pipeline.
                - name (str): Human-readable stage name.
                - action (str): Action type to execute (e.g. 'lock_door', 'dial_emergency',
                                'backup_video', 'send_sms').
                - params (Dict): Parameters for the action (e.g. contact number, cloud bucket).
                - on_failure (str): [Optional] 'abort', 'skip', or 'retry'. Defaults to 'abort'.
                - max_retries (int): [Optional] Max retries if on_failure='retry'. Defaults to 1.
                - depends_on (List[str]): [Optional] Stage IDs that must complete first.
                - assigned_worker (str): [Optional] Worker ID for this stage.
            mode (str): Execution mode — 'sequential' or 'parallel'. Defaults to 'sequential'.

        Returns:
            pipeline_id (int): Unique pipeline identifier.
            pipeline (Dict): The created pipeline with all stages initialized.
        """
        if not stages:
            return {"error": "At least one stage is required."}
        if mode not in VALID_EXEC_MODES:
            return {"error": f"Invalid mode '{mode}'. Must be one of: {', '.join(VALID_EXEC_MODES)}"}

        stage_ids = [s.get("stage_id") for s in stages]
        if any(sid is None for sid in stage_ids):
            return {"error": "All stages must include a 'stage_id' field."}
        if len(stage_ids) != len(set(stage_ids)):
            return {"error": "Duplicate stage_id values are not allowed within a pipeline."}

        for stage in stages:
            for field in ("stage_id", "name", "action"):
                if field not in stage:
                    return {"error": f"Stage '{stage.get('stage_id', '?')}' missing required field '{field}'."}

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
            "mode": mode,
        })
        return {"pipeline_id": pipeline_id, "pipeline": pipeline}

    def get_pipeline(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Retrieve the full state of a response pipeline.

        Args:
            pipeline_id (int): Pipeline ID.

        Returns:
            pipeline (Dict): Full pipeline object with all stages and current status.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        return {"pipeline": pl}

    def list_pipelines(self, status: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all response pipelines, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by pipeline status. Must be one of:
                          'pending', 'in_progress', 'awaiting_approval', 'completed',
                          'failed', 'cancelled', 'rolled_back'.

        Returns:
            pipelines (List[Dict]): Matching pipeline summaries with progress info.
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

    # ── Stage execution ───────────────────────────────────────────────────

    def assign_stage(
        self,
        pipeline_id: int,
        stage_id: str,
        worker_id: str,
    ) -> Dict[str, Any]:
        """
        Assign a security worker/device to a specific stage in a pipeline.

        Args:
            pipeline_id (int): Pipeline ID.
            stage_id (str): Stage ID within the pipeline.
            worker_id (str): Worker ID to assign (must be a registered security device).

        Returns:
            stage_id (str): The stage that was updated.
            assigned_worker (str): The assigned worker ID.
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
            "worker_id": worker_id,
        })
        return {"stage_id": stage_id, "assigned_worker": worker_id}

    def execute_stage(self, pipeline_id: int, stage_id: str) -> Dict[str, Any]:
        """
        Execute a single security response stage within a pipeline.

        Validates dependencies, marks the assigned worker as busy, simulates
        the security action (lock door, dial emergency, backup video, send SMS),
        and handles the result according to the failure policy.

        Args:
            pipeline_id (int): Pipeline ID.
            stage_id (str): Stage ID to execute.

        Returns:
            stage_id (str): The executed stage ID.
            status (str): Execution result — 'completed' or 'failed'.
            result (Dict): Stage execution output including action details.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}

        stage = self._find_stage(pl, stage_id)
        if not stage:
            return {"error": f"Stage '{stage_id}' not found in pipeline {pipeline_id}."}
        if stage["status"] not in ("pending", "failed"):
            return {"error": f"Stage '{stage_id}' is already '{stage['status']}'."}

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

        success, result = self._simulate_stage_outcome(stage, pl)

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
                "result": result,
            })

        if worker_id and worker_id in self.workers:
            self.workers[worker_id]["status"] = "idle"
            self.workers[worker_id]["task_count"] += 1
            if success:
                self.workers[worker_id]["completed_count"] += 1

        return {"stage_id": stage_id, "status": stage["status"], "result": result}

    def execute_pipeline(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Execute all pending stages in a security response pipeline.

        In sequential mode, stages execute one by one respecting order and dependencies
        (e.g. lock door → dial emergency → backup video → notify contact).
        In parallel mode, all stages with satisfied dependencies execute together.

        Args:
            pipeline_id (int): Pipeline ID.

        Returns:
            pipeline_id (int): The executed pipeline ID.
            status (str): Overall pipeline status after execution.
            stage_results (Dict[str, str]): Execution status per stage ID.
        """
        pl = self._find_pipeline(pipeline_id)
        if not pl:
            return {"error": f"Pipeline ID {pipeline_id} not found."}
        if pl["status"] not in ("pending", "in_progress"):
            return {"error": f"Pipeline {pipeline_id} is already '{pl['status']}'."}

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

        pl["status"] = "completed"
        return {"pipeline_id": pipeline_id, "status": pl["status"], "stage_results": stage_results}

    # ── Helper Methods ──────────────────────────────────────────────────

    def _find_pipeline(self, pipeline_id: int) -> Optional[Dict[str, Any]]:
        """Find a pipeline by ID. Returns None if not found."""
        for p in self.pipelines:
            if p["pipeline_id"] == pipeline_id:
                return p
        return None

    def _find_stage(
        self, pipeline: Dict[str, Any], stage_id: str
    ) -> Optional[Dict[str, Any]]:
        """Find a stage within a pipeline by stage_id. Returns None if not found."""
        for s in pipeline["stages"]:
            if s["stage_id"] == stage_id:
                return s
        return None

    def _find_alert(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """Find an alert by ID. Returns None if not found."""
        for a in self.alerts:
            if a["alert_id"] == alert_id:
                return a
        return None

    def _simulate_stage_outcome(
        self, stage: Dict[str, Any], pl: Dict[str, Any]
    ) -> tuple:
        """Simulate executing a security response stage.

        Returns (success: bool, result: dict) based on the stage action.
        Supported actions: lock_door, dial_emergency, backup_video, send_sms.
        """
        action = stage["action"]
        params = stage.get("params", {})

        if action == "lock_door":
            door_id = params.get("door_id", "all")
            result = {
                "action": "lock_door",
                "door_id": door_id,
                "locked": True,
                "timestamp": datetime.now().isoformat(),
            }
            return True, result

        elif action == "dial_emergency":
            number = params.get("emergency_number", "911")
            result = {
                "action": "dial_emergency",
                "number": number,
                "connected": True,
                "duration_seconds": 3,
                "timestamp": datetime.now().isoformat(),
            }
            return True, result

        elif action == "backup_video":
            camera_id = params.get("camera_id", "default")
            cloud_bucket = params.get("cloud_bucket", "security-footage")
            result = {
                "action": "backup_video",
                "camera_id": camera_id,
                "cloud_bucket": cloud_bucket,
                "footage_uploaded_mb": 150,
                "timestamp": datetime.now().isoformat(),
            }
            return True, result

        elif action == "send_sms":
            contact = params.get("contact", "unknown")
            message = params.get("message", "Security alert triggered.")
            result = {
                "action": "send_sms",
                "recipient": contact,
                "message": message,
                "delivered": True,
                "timestamp": datetime.now().isoformat(),
            }
            return True, result

        return False, {"error": f"Unknown action type: {action}"}

    def _handle_stage_failure(
        self, pl: Dict[str, Any], stage: Dict[str, Any]
    ) -> None:
        """Apply the failure policy for a failed stage.

        on_failure='skip'   -> mark stage as 'skipped'
        on_failure='retry'  -> reset to 'pending' if retries remain
        on_failure='abort'  -> mark the pipeline as 'failed'
        """
        policy = stage.get("on_failure", "abort")
        if policy == "skip":
            stage["status"] = "skipped"
        elif policy == "retry":
            if stage["retry_count"] < stage.get("max_retries", 1):
                stage["status"] = "pending"
                stage["retry_count"] += 1
        elif policy == "abort":
            pl["status"] = "failed"

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })