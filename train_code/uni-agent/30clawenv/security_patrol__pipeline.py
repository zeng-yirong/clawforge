# 我来分析需求，设计一个家庭/办公区安全巡检的管道处理型环境。

# 核心管道流程：
# - `add_zone` / `ingest_alert` 注册监控区域或摄入告警事件
# - `process` 执行响应处理（锁门、报警、视频备份、短信通知）
# - `aggregate` 聚合多个告警事件的处理结果
# - `generate_output` 输出巡检报告

import json
from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE = {
    "zones": {
        "front_door": {
            "type": "entry_point",
            "description": "正门入口摄像头及门锁",
            "lock_status": "locked",
            "camera_online": True,
            "active": True,
        },
        "back_door": {
            "type": "entry_point",
            "description": "后门入口摄像头及门锁",
            "lock_status": "locked",
            "camera_online": True,
            "active": True,
        },
        "living_room": {
            "type": "indoor",
            "description": "客厅红外移动传感器及摄像头",
            "lock_status": "n/a",
            "camera_online": True,
            "active": True,
        },
        "office_a": {
            "type": "office",
            "description": "A区办公室门禁及摄像头",
            "lock_status": "locked",
            "camera_online": True,
            "active": True,
        },
        "garage": {
            "type": "entry_point",
            "description": "车库卷帘门及摄像头",
            "lock_status": "locked",
            "camera_online": True,
            "active": True,
        },
        "server_room": {
            "type": "restricted",
            "description": "服务器机房门禁及双重摄像头",
            "lock_status": "locked",
            "camera_online": True,
            "active": True,
        },
    },
    "contacts": {
        "owner": {
            "name": "负责人",
            "phone": "138xxxxxxxx",
            "role": "owner",
            "notify_sms": True,
            "notify_call": True,
        },
        "security": {
            "name": "安保主管",
            "phone": "139xxxxxxxx",
            "role": "security",
            "notify_sms": True,
            "notify_call": False,
        },
    },
    "alerts": [],
    "actions": [],
    "outputs": [],
    "processing_log": [],
    "alert_counter": 1,
    "action_counter": 1,
    "output_counter": 1,
}

VALID_ALERT_TYPES = ("intrusion", "motion", "door_forced", "camera_offline", "sensor_tamper", "unknown")
VALID_ALERT_STATUSES = ("pending", "processing", "responded", "false_alarm", "escalated")
VALID_ACTION_TYPES = ("lock_door", "call_police", "backup_video", "send_sms", "unlock_door", "trigger_alarm")
VALID_ACTION_STATUSES = ("pending", "executing", "completed", "failed")
VALID_OUTPUT_FORMATS = ("markdown", "bullet", "json", "timeline")
VALID_SEVERITY_LEVELS = ("low", "medium", "high", "critical")


class SecurityInspectionEnv:
    """
    A home/office security inspection pipeline environment.

    This class models a closed-loop security response pipeline:
    alert ingestion → multi-action processing (lock doors, call police,
    backup video, send SMS) → cross-alert aggregation → structured report generation.
    Agents can register monitoring zones and contacts, ingest intrusion alerts,
    trigger response actions, aggregate multi-zone incidents, and generate
    audit reports or incident summaries.

    Attributes:
        zones (Dict): Registry of monitored zones with lock and camera status.
        contacts (Dict): Registry of responsible persons for notifications.
        alerts (List[Dict]): All ingested security alert records.
        actions (List[Dict]): All executed or pending response actions.
        outputs (List[Dict]): Generated output records (reports, summaries).
        processing_log (List[Dict]): Audit log of all pipeline operations.
        alert_counter (int): Auto-incrementing alert ID counter.
        action_counter (int): Auto-incrementing action ID counter.
        output_counter (int): Auto-incrementing output ID counter.
    """

    def __init__(self):
        self.zones: Dict[str, Dict[str, Any]]
        self.contacts: Dict[str, Dict[str, Any]]
        self.alerts: List[Dict[str, Any]]
        self.actions: List[Dict[str, Any]]
        self.outputs: List[Dict[str, Any]]
        self.processing_log: List[Dict[str, Any]]
        self.alert_counter: int
        self.action_counter: int
        self.output_counter: int
        self._api_description = (
            "This tool provides a closed-loop home/office security inspection pipeline covering "
            "zone and contact management, intrusion alert ingestion, automated response actions "
            "(lock doors, call police, backup video, send SMS), multi-alert aggregation, "
            "and structured incident report generation."
        )

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.zones = scenario.get("zones", DEFAULT_STATE_COPY["zones"])
        self.contacts = scenario.get("contacts", DEFAULT_STATE_COPY["contacts"])
        self.alerts = scenario.get("alerts", DEFAULT_STATE_COPY["alerts"])
        self.actions = scenario.get("actions", DEFAULT_STATE_COPY["actions"])
        self.outputs = scenario.get("outputs", DEFAULT_STATE_COPY["outputs"])
        self.processing_log = scenario.get("processing_log", DEFAULT_STATE_COPY["processing_log"])
        self.alert_counter = scenario.get("alert_counter", DEFAULT_STATE_COPY["alert_counter"])
        self.action_counter = scenario.get("action_counter", DEFAULT_STATE_COPY["action_counter"])
        self.output_counter = scenario.get("output_counter", DEFAULT_STATE_COPY["output_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including zones, contacts, alerts,
                  actions, outputs, processing log, and counters.
        """
        return {
            "zones": self.zones,
            "contacts": self.contacts,
            "alerts": self.alerts,
            "actions": self.actions,
            "outputs": self.outputs,
            "processing_log": self.processing_log,
            "alert_counter": self.alert_counter,
            "action_counter": self.action_counter,
            "output_counter": self.output_counter,
        }

    # ── Zone management ──────────────────────────────────────────────────

    def add_zone(self, name: str, zone_type: str, description: str = "") -> Dict[str, Any]:
        """
        Register a new monitoring zone.

        Args:
            name (str): Unique zone identifier (e.g. 'warehouse_b').
            zone_type (str): Zone category, e.g. 'entry_point', 'indoor', 'office', 'restricted'.
            description (str): [Optional] Human-readable description of the zone.

        Returns:
            zone (Dict): The registered zone entry with name, type, lock_status, and camera_online.
        """
        if name in self.zones:
            return {"error": f"Zone '{name}' already exists."}
        self.zones[name] = {
            "type": zone_type,
            "description": description,
            "lock_status": "locked",
            "camera_online": True,
            "active": True,
        }
        self._log("zone_added", {"name": name, "zone_type": zone_type})
        return {"zone": {"name": name, **self.zones[name]}}

    def list_zones(self, zone_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered monitoring zones, optionally filtered by type.

        Args:
            zone_type (str): [Optional] Filter by zone type (e.g. 'entry_point', 'restricted').

        Returns:
            zones (List[Dict]): Matching zone entries with name, type, lock_status, and camera_online.
        """
        result = []
        for name, meta in self.zones.items():
            if zone_type and meta["type"] != zone_type:
                continue
            result.append({
                "name": name,
                "type": meta["type"],
                "lock_status": meta["lock_status"],
                "camera_online": meta["camera_online"],
                "active": meta["active"],
            })
        return {"zones": result}

    def get_zone_status(self, name: str) -> Dict[str, Any]:
        """
        Retrieve the current status of a specific monitoring zone.

        Args:
            name (str): Zone identifier.

        Returns:
            zone (Dict): Full zone record including lock_status, camera_online, and active flag.
        """
        if name not in self.zones:
            return {"error": f"Zone '{name}' not found."}
        return {"zone": {"name": name, **self.zones[name]}}

    # ── Contact management ───────────────────────────────────────────────

    def add_contact(
        self,
        contact_id: str,
        name: str,
        phone: str,
        role: str = "staff",
        notify_sms: bool = True,
        notify_call: bool = False,
    ) -> Dict[str, Any]:
        """
        Register a new responsible contact for security notifications.

        Args:
            contact_id (str): Unique contact identifier (e.g. 'manager_b').
            name (str): Full name of the contact person.
            phone (str): Phone number for SMS and call notifications.
            role (str): [Optional] Role label, e.g. 'owner', 'security', 'staff'. Defaults to 'staff'.
            notify_sms (bool): [Optional] Whether to send SMS notifications. Defaults to True.
            notify_call (bool): [Optional] Whether to trigger voice call notifications. Defaults to False.

        Returns:
            contact (Dict): The registered contact entry.
        """
        if contact_id in self.contacts:
            return {"error": f"Contact '{contact_id}' already exists."}
        self.contacts[contact_id] = {
            "name": name,
            "phone": phone,
            "role": role,
            "notify_sms": notify_sms,
            "notify_call": notify_call,
        }
        self._log("contact_added", {"contact_id": contact_id, "role": role})
        return {"contact": {"contact_id": contact_id, **self.contacts[contact_id]}}

    def list_contacts(self, role: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered contacts, optionally filtered by role.

        Args:
            role (str): [Optional] Filter by role (e.g. 'owner', 'security').

        Returns:
            contacts (List[Dict]): Matching contact entries with id, name, phone, and role.
        """
        result = []
        for cid, meta in self.contacts.items():
            if role and meta["role"] != role:
                continue
            result.append({"contact_id": cid, "name": meta["name"], "phone": meta["phone"], "role": meta["role"]})
        return {"contacts": result}

    # ── Alert ingestion ──────────────────────────────────────────────────

    def ingest_alert(
        self,
        zone: str,
        alert_type: str,
        severity: str = "high",
        description: str = "",
        snapshot_url: str = "",
    ) -> Dict[str, Any]:
        """
        Ingest a security alert into the pipeline for response processing.

        The ingested alert becomes a processing record with status 'pending'.
        Each alert is tied to a registered zone and carries severity metadata
        to guide downstream response actions.

        Args:
            zone (str): Zone identifier where the alert was triggered. Must be registered.
            alert_type (str): Type of security event. Must be one of:
                intrusion, motion, door_forced, camera_offline, sensor_tamper, unknown.
            severity (str): [Optional] Severity level — 'low', 'medium', 'high', or 'critical'.
                Defaults to 'high'.
            description (str): [Optional] Free-text description of the observed anomaly.
            snapshot_url (str): [Optional] URL or path to the triggering camera snapshot.

        Returns:
            alert_id (int): Unique alert identifier for downstream processing.
            alert (Dict): The created alert record with status 'pending'.
        """
        if zone not in self.zones:
            return {"error": f"Zone '{zone}' not found. Register it first with add_zone."}
        if alert_type not in VALID_ALERT_TYPES:
            return {"error": f"Invalid alert_type '{alert_type}'. Must be one of: {', '.join(VALID_ALERT_TYPES)}"}
        if severity not in VALID_SEVERITY_LEVELS:
            return {"error": f"Invalid severity '{severity}'. Must be one of: {', '.join(VALID_SEVERITY_LEVELS)}"}

        alert_id = self.alert_counter
        self.alert_counter += 1

        alert = {
            "alert_id": alert_id,
            "zone": zone,
            "alert_type": alert_type,
            "severity": severity,
            "description": description,
            "snapshot_url": snapshot_url,
            "status": "pending",
            "actions_taken": [],
            "result": None,
            "processed_at": None,
        }
        self.alerts.append(alert)
        self._log("alert_ingested", {"alert_id": alert_id, "zone": zone, "alert_type": alert_type, "severity": severity})
        return {"alert_id": alert_id, "alert": alert}

    # ── Processing ────────────────────────────────────────────────────────

    def process(
        self,
        alert_id: int = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute the full closed-loop response pipeline for a pending alert.

        The response actions are automatically selected based on alert severity
        and zone type, then executed in sequence:
        1. lock_door — lock the affected zone (if applicable).
        2. call_police — dial emergency services for high/critical alerts.
        3. backup_video — capture and upload a video clip to cloud storage.
        4. send_sms — notify all registered contacts via SMS.

        Individual actions can be overridden via the params argument.

        Args:
            alert_id (int): The alert ID returned by ingest_alert().
            params (Dict): [Optional] Processing overrides:
                - actions (List[str]): Explicit list of actions to execute. Overrides auto-selection.
                  Valid values: lock_door, call_police, backup_video, send_sms, unlock_door, trigger_alarm.
                - contact_ids (List[str]): Specific contacts to notify. Defaults to all contacts.
                - video_duration_seconds (int): Duration of video clip to backup. Defaults to 30.
                - cloud_bucket (str): Target cloud storage bucket name. Defaults to 'security-backup'.
                - police_number (str): Emergency number to dial. Defaults to '110'.

        Returns:
            alert_id (int): The processed alert ID.
            status (str): Processing status ('responded' or 'failed').
            actions_taken (List[Dict]): List of executed action records with results.
        """
        if not isinstance(alert_id, int):
            return {"error": "alert_id must be an integer."}
        if params is not None and not isinstance(params, dict):
            return {"error": "params must be a dictionary if provided."}
        params = params or {}
        alert = self._find_alert(alert_id)
        if not alert:
            return {"error": f"Alert ID {alert_id} not found."}

        if alert["status"] not in ("pending", "escalated"):
            return {"error": f"Alert {alert_id} is already '{alert['status']}'. Re-ingest to reprocess."}

        alert["status"] = "processing"
        self._log("processing_started", {"alert_id": alert_id, "params": params})

        # Determine which actions to execute
        requested_actions = params.get("actions", None)
        if requested_actions is not None:
            invalid_actions = [a for a in requested_actions if a not in VALID_ACTION_TYPES]
            if invalid_actions:
                alert["status"] = "pending"
                return {"error": f"Invalid action(s): {', '.join(invalid_actions)}. Must be one of: {', '.join(VALID_ACTION_TYPES)}"}
            action_list = requested_actions
        else:
            action_list = self._select_actions(alert)

        executed_actions = []
        for action in action_list:
            # action_list may contain strings (from params override) or dicts (from _select_actions)
            action_type = action if isinstance(action, str) else action["action_type"]
            action_result = self._execute_action(action_type, alert, params)
            executed_actions.append(action_result)
            alert["actions_taken"].append(action_result["action_id"])

        alert["status"] = "responded"
        alert["result"] = {
            "actions_executed": len(executed_actions),
            "action_ids": [a["action_id"] for a in executed_actions],
            "summary": self._build_response_summary(executed_actions, alert),
        }
        alert["processed_at"] = f"t+{alert_id}"

        self._log("processing_completed", {
            "alert_id": alert_id,
            "actions_executed": len(executed_actions),
            "action_ids": alert["result"]["action_ids"],
        })
        return {
            "alert_id": alert_id,
            "status": "responded",
            "actions_taken": executed_actions,
        }

    def get_alert(self, alert_id: int) -> Dict[str, Any]:
        """
        Retrieve the full state of a security alert record.

        Args:
            alert_id (int): Alert ID.

        Returns:
            alert (Dict): Full alert record including status, actions_taken, and result.
        """
        alert = self._find_alert(alert_id)
        if not alert:
            return {"error": f"Alert ID {alert_id} not found."}
        return {"alert": alert}

    def list_alerts(
        self,
        status: Optional[str] = None,
        zone: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all security alerts, optionally filtered by status, zone, or severity.

        Args:
            status (str): [Optional] Filter by alert status. Must be one of:
                pending, processing, responded, false_alarm, escalated.
            zone (str): [Optional] Filter by zone identifier.
            severity (str): [Optional] Filter by severity level (low, medium, high, critical).

        Returns:
            alerts (List[Dict]): Matching alert summaries with id, zone, type, severity, and status.
        """
        if status and status not in VALID_ALERT_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_ALERT_STATUSES)}"}
        if severity and severity not in VALID_SEVERITY_LEVELS:
            return {"error": f"Invalid severity '{severity}'. Must be one of: {', '.join(VALID_SEVERITY_LEVELS)}"}

        results = self.alerts
        if status:
            results = [a for a in results if a["status"] == status]
        if zone:
            results = [a for a in results if a["zone"] == zone]
        if severity:
            results = [a for a in results if a["severity"] == severity]

        summaries = [
            {
                "alert_id": a["alert_id"],
                "zone": a["zone"],
                "alert_type": a["alert_type"],
                "severity": a["severity"],
                "status": a["status"],
                "actions_count": len(a["actions_taken"]),
            }
            for a in results
        ]
        return {"alerts": summaries}

    def mark_false_alarm(self, alert_id: int, reason: str = "") -> Dict[str, Any]:
        """
        Mark a responded or pending alert as a false alarm.

        This closes the alert without escalation and optionally unlocks any
        doors that were locked during the response.

        Args:
            alert_id (int): Alert ID to mark as false alarm.
            reason (str): [Optional] Explanation for the false alarm classification.

        Returns:
            success (bool): True if the alert was successfully marked.
            alert_id (int): The updated alert ID.
            previous_status (str): The status before this update.
        """
        alert = self._find_alert(alert_id)
        if not alert:
            return {"error": f"Alert ID {alert_id} not found."}
        if alert["status"] == "false_alarm":
            return {"error": f"Alert {alert_id} is already marked as false_alarm."}

        previous_status = alert["status"]
        alert["status"] = "false_alarm"
        if reason:
            alert["description"] = alert["description"] + f" [False alarm: {reason}]"

        self._log("false_alarm_marked", {"alert_id": alert_id, "reason": reason, "previous_status": previous_status})
        return {"success": True, "alert_id": alert_id, "previous_status": previous_status}

    def escalate_alert(self, alert_id: int, reason: str = "") -> Dict[str, Any]:
        """
        Escalate an alert for additional response actions.

        Escalated alerts can be re-processed via process() to trigger
        additional or different response actions.

        Args:
            alert_id (int): Alert ID to escalate.
            reason (str): [Optional] Reason for escalation.

        Returns:
            success (bool): True if escalation was applied.
            alert_id (int): The escalated alert ID.
        """
        alert = self._find_alert(alert_id)
        if not alert:
            return {"error": f"Alert ID {alert_id} not found."}
        if alert["status"] in ("false_alarm",):
            return {"error": f"Cannot escalate a false_alarm alert."}

        alert["status"] = "escalated"
        self._log("alert_escalated", {"alert_id": alert_id, "reason": reason})
        return {"success": True, "alert_id": alert_id, "status": "escalated"}

    def get_action(self, action_id: int) -> Dict[str, Any]:
        """
        Retrieve the full record of a specific response action.

        Args:
            action_id (int): Action ID.

        Returns:
            action (Dict): Full action record including type, status, and result details.
        """
        action = self._find_action(action_id)
        if not action:
            return {"error": f"Action ID {action_id} not found."}
        return {"action": action}

    def list_actions(
        self,
        action_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all executed response actions, optionally filtered by type or status.

        Args:
            action_type (str): [Optional] Filter by action type (e.g. 'lock_door', 'send_sms').
            status (str): [Optional] Filter by action status (pending, executing, completed, failed).

        Returns:
            actions (List[Dict]): Matching action summaries with id, type, alert_id, and status.
        """
        if action_type and action_type not in VALID_ACTION_TYPES:
            return {"error": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(VALID_ACTION_TYPES)}"}
        if status and status not in VALID_ACTION_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_ACTION_STATUSES)}"}

        results = self.actions
        if action_type:
            results = [a for a in results if a["action_type"] == action_type]
        if status:
            results = [a for a in results if a["status"] == status]

        summaries = [
            {
                "action_id": a["action_id"],
                "action_type": a["action_type"],
                "alert_id": a["alert_id"],
                "zone": a.get("zone"),
                "status": a["status"],
            }
            for a in results
        ]
        return {"actions": summaries}

    # ── Aggregation ──────────────────────────────────────────────────────

    def aggregate(
        self,
        alert_ids: List[int] = None,
        dedup_key: str = "zone",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Aggregate response results from multiple completed security alerts.

        Merges action records across alerts, deduplicates by the specified key,
        and produces a unified incident summary with zone coverage and action statistics.
        Useful for correlating multi-zone intrusion events into a single incident view.

        Args:
            alert_ids (List[int]): List of alert IDs to aggregate. Minimum 2 required.
            dedup_key (str): Field name used for deduplication across alerts.
                Defaults to 'zone'. Other useful values: 'alert_type', 'action_type'.

        Returns:
            aggregated (Dict): Merged incident summary with:
                - items: deduplicated list of action records with source traceability.
                - total: count of deduplicated items.
                - source_alerts: original alert IDs included.
                - severity_summary: count of alerts per severity level.
                - zones_affected: list of unique zones involved.
        """
        if not isinstance(alert_ids, list):
            return {"error": "alert_ids must be a list."}
        for aid in alert_ids:
            if not isinstance(aid, int):
                return {"error": f"Each element in alert_ids must be an integer, got {type(aid).__name__}."}
        if len(alert_ids) < 2:
            return {"error": "At least 2 alert IDs are required for aggregation."}

        all_items = []
        severity_summary: Dict[str, int] = {}
        zones_affected = set()

        for aid in alert_ids:
            alert = self._find_alert(aid)
            if not alert:
                return {"error": f"Alert ID {aid} not found."}
            if alert["status"] not in ("responded", "false_alarm", "escalated"):
                return {"error": f"Alert {aid} has not been processed yet (status='{alert['status']}'). Process it first."}

            sev = alert["severity"]
            severity_summary[sev] = severity_summary.get(sev, 0) + 1
            zones_affected.add(alert["zone"])

            # Collect action records for this alert
            for action_id in alert["actions_taken"]:
                action = self._find_action(action_id)
                if action:
                    item = dict(action)
                    item["_source_alert"] = aid
                    item["_alert_severity"] = sev
                    all_items.append(item)

        # Deduplicate by dedup_key
        seen = set()
        deduped = []
        for item in all_items:
            key = str(item.get(dedup_key, "")).lower().strip()
            if key and key not in seen:
                seen.add(key)
                deduped.append(item)
            elif not key:
                deduped.append(item)

        self._log("aggregated", {
            "alert_ids": alert_ids,
            "total_items": len(all_items),
            "deduped": len(deduped),
            "zones_affected": list(zones_affected),
        })
        return {
            "aggregated": {
                "items": deduped,
                "total": len(deduped),
                "source_alerts": alert_ids,
                "severity_summary": severity_summary,
                "zones_affected": sorted(zones_affected),
            }
        }

    # ── Output generation ─────────────────────────────────────────────────

    def generate_output(
        self,
        alert_ids: List[int],
        output_format: str = "markdown",
        title: str = "",
    ) -> Dict[str, Any]:
        """
        Generate a structured incident report from one or more responded alerts.

        Supports markdown reports, bullet summaries, JSON exports, and timeline diagrams.
        For a single alert, produces a detailed response record. For multiple alerts,
        produces an aggregated incident report with zone and action coverage.

        Args:
            alert_ids (List[int]): One or more alert IDs to include in the report.
                All referenced alerts must have status 'responded', 'false_alarm', or 'escalated'.
            output_format (str): Output format — 'markdown', 'bullet', 'json', or 'timeline'.
                Defaults to 'markdown'.
            title (str): Title for the generated report. Auto-generated if empty.

        Returns:
            output_id (int): Unique output identifier.
            output (Dict): The generated output record with content, format, and metadata.
        """
        if output_format not in VALID_OUTPUT_FORMATS:
            return {"error": f"Invalid output_format '{output_format}'. Must be one of: {', '.join(VALID_OUTPUT_FORMATS)}"}
        if not alert_ids:
            return {"error": "At least one alert_id is required."}

        terminal_statuses = ("responded", "false_alarm", "escalated")
        for aid in alert_ids:
            alert = self._find_alert(aid)
            if not alert:
                return {"error": f"Alert ID {aid} not found."}
            if alert["status"] not in terminal_statuses:
                return {"error": f"Alert {aid} is not yet processed (status='{alert['status']}'). Process it first."}

        output_id = self.output_counter
        self.output_counter += 1

        title = title or f"Security Incident Report #{output_id}"
        content = self._render_output(alert_ids, output_format, title)

        output = {
            "output_id": output_id,
            "title": title,
            "format": output_format,
            "alert_ids": alert_ids,
            "content": content,
            "created_at": f"t+{output_id}",
        }
        self.outputs.append(output)
        self._log("output_generated", {
            "output_id": output_id,
            "format": output_format,
            "alert_count": len(alert_ids),
        })
        return {"output_id": output_id, "output": output}

    def list_outputs(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all generated incident reports and output records.

        Returns:
            outputs (List[Dict]): Output summaries with output_id, title, format, and alert count.
        """
        summaries = [
            {
                "output_id": o["output_id"],
                "title": o["title"],
                "format": o["format"],
                "alert_count": len(o["alert_ids"]),
            }
            for o in self.outputs
        ]
        return {"outputs": summaries}

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_alert(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """Find an alert by ID. Returns None if not found."""
        for a in self.alerts:
            if a["alert_id"] == alert_id:
                return a
        return None

    def _find_action(self, action_id: int) -> Optional[Dict[str, Any]]:
        """Find an action by ID. Returns None if not found."""
        for a in self.actions:
            if a["action_id"] == action_id:
                return a
        return None

    def _select_actions(self, alert: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select applicable actions for an alert based on type and severity.

        Returns a list of pending action records (Dict) created in self.actions.
        """
        alert_type = alert.get("alert_type", "unknown")
        severity = alert.get("severity", "high")
        zone = alert.get("zone", "")

        # Map alert types to appropriate response action types
        action_type_map = {
            "intrusion": ["lock_door", "call_police", "backup_video", "send_sms"],
            "motion": ["backup_video", "send_sms"],
            "door_forced": ["lock_door", "call_police", "backup_video", "send_sms"],
            "camera_offline": ["send_sms", "backup_video"],
            "sensor_tamper": ["lock_door", "backup_video", "send_sms"],
            "unknown": ["backup_video", "send_sms"],
        }

        selected_types = list(action_type_map.get(alert_type, ["backup_video", "send_sms"]))

        # Escalate for critical severity: always include call_police
        if severity == "critical" and "call_police" not in selected_types:
            selected_types.append("call_police")

        # Create pending action records
        actions = []
        for atype in selected_types:
            action_id = self.action_counter
            self.action_counter += 1
            record = {
                "action_id": action_id,
                "action_type": atype,
                "alert_id": alert["alert_id"],
                "zone": zone,
                "status": "pending",
                "result": None,
            }
            self.actions.append(record)
            actions.append(record)

        self._log("actions_selected", {
            "alert_id": alert["alert_id"],
            "action_types": selected_types,
            "count": len(actions),
        })
        return actions

    def _execute_action(
        self, action_type: str, alert: Dict[str, Any], params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate executing a security response action.

        Args:
            action_type: One of VALID_ACTION_TYPES (lock_door, call_police, etc.).
            alert: The alert dict that triggered this action.
            params: Processing overrides from process().

        Returns:
            Dict: The action record with updated status and result details.
        """
        # Locate the pending action record created by _select_actions
        action_record = None
        for a in self.actions:
            if (
                a["alert_id"] == alert["alert_id"]
                and a["action_type"] == action_type
                and a["status"] == "pending"
            ):
                action_record = a
                break

        # Fallback: create a new record if none was pre-created
        if action_record is None:
            action_id = self.action_counter
            self.action_counter += 1
            action_record = {
                "action_id": action_id,
                "action_type": action_type,
                "alert_id": alert["alert_id"],
                "zone": alert.get("zone", ""),
                "status": "pending",
                "result": None,
            }
            self.actions.append(action_record)

        action_record["status"] = "executing"

        zone = alert.get("zone", "")
        zone_info = self.zones.get(zone, {})
        success = True
        result_detail: Dict[str, Any] = {}

        if action_type == "lock_door":
            if zone_info.get("lock_status") == "n/a":
                success = False
                result_detail = {"message": f"Zone '{zone}' has no lock to engage."}
            else:
                zone_info["lock_status"] = "locked"
                result_detail = {
                    "message": f"Door locked in zone '{zone}'.",
                    "lock_status": "locked",
                }

        elif action_type == "unlock_door":
            if zone_info.get("lock_status") == "n/a":
                success = False
                result_detail = {"message": f"Zone '{zone}' has no lock to disengage."}
            else:
                zone_info["lock_status"] = "unlocked"
                result_detail = {
                    "message": f"Door unlocked in zone '{zone}'.",
                    "lock_status": "unlocked",
                }

        elif action_type == "call_police":
            police_number = params.get("police_number", "110")
            result_detail = {
                "message": f"Emergency services called at {police_number} for zone '{zone}'.",
                "police_number": police_number,
                "response_time_estimate": "5-10 minutes",
            }

        elif action_type == "backup_video":
            duration = params.get("video_duration_seconds", 30)
            bucket = params.get("cloud_bucket", "security-backup")
            if not zone_info.get("camera_online", False):
                success = False
                result_detail = {
                    "message": f"Camera offline in zone '{zone}'. Cannot backup video."
                }
            else:
                result_detail = {
                    "message": (
                        f"Video clip ({duration}s) from zone '{zone}' "
                        f"backed up to cloud bucket '{bucket}'."
                    ),
                    "duration_seconds": duration,
                    "cloud_bucket": bucket,
                    "camera_online": True,
                }

        elif action_type == "send_sms":
            contact_ids = params.get("contact_ids", list(self.contacts.keys()))
            notified = []
            for cid in contact_ids:
                if cid in self.contacts and self.contacts[cid].get("notify_sms", False):
                    notified.append(cid)
            result_detail = {
                "message": (
                    f"SMS alert sent to {len(notified)} contact(s)"
                    + (f": {', '.join(notified)}" if notified else "")
                    + "."
                ),
                "contacts_notified": notified,
                "contact_count": len(notified),
            }

        elif action_type == "trigger_alarm":
            result_detail = {
                "message": f"Audible alarm triggered in zone '{zone}'.",
                "alarm_active": True,
            }

        else:
            success = False
            result_detail = {"message": f"Unknown or unsupported action type: '{action_type}'."}

        action_record["status"] = "completed" if success else "failed"
        action_record["result"] = result_detail

        self._log("action_executed", {
            "action_id": action_record["action_id"],
            "action_type": action_type,
            "alert_id": alert["alert_id"],
            "status": action_record["status"],
        })
        return action_record

    def _build_response_summary(
        self, executed_actions: List[Dict[str, Any]], alert: Dict[str, Any]
    ) -> str:
        """Build a human-readable summary of the executed response actions.

        Args:
            executed_actions: List of action records returned by _execute_action.
            alert: The alert dict that triggered the response.

        Returns:
            str: A single-line summary of what happened.
        """
        action_labels = {
            "lock_door": "Door locked",
            "unlock_door": "Door unlocked",
            "call_police": "Police called",
            "backup_video": "Video backed up",
            "send_sms": "SMS sent",
            "trigger_alarm": "Alarm triggered",
        }

        completed = [a for a in executed_actions if a.get("status") == "completed"]
        failed = [a for a in executed_actions if a.get("status") == "failed"]

        parts = [
            action_labels.get(a["action_type"], a["action_type"])
            for a in completed
        ]

        summary = (
            f"Alert #{alert['alert_id']} ({alert['alert_type']}) "
            f"in zone '{alert['zone']}': "
        )
        if parts:
            summary += "; ".join(parts) + "."
        else:
            summary += "no actions completed."

        if failed:
            failed_types = [a["action_type"] for a in failed]
            summary += f" Failed: {', '.join(failed_types)}."

        return summary

    def _render_output(
        self, alert_ids: List[int], output_format: str, title: str
    ) -> str:
        """Render output content in the specified format for one or more alerts.

        Args:
            alert_ids: List of alert IDs to include in the output.
            output_format: One of 'markdown', 'bullet', 'json', 'timeline'.
            title: Report title.

        Returns:
            str: The rendered output content.
        """
        alerts_data: List[Dict[str, Any]] = []
        for aid in alert_ids:
            a = self._find_alert(aid)
            if a:
                alerts_data.append(a)

        if output_format == "json":
            output_data = {
                "title": title,
                "alert_count": len(alerts_data),
                "alerts": [
                    {
                        "alert_id": a["alert_id"],
                        "zone": a["zone"],
                        "alert_type": a["alert_type"],
                        "severity": a["severity"],
                        "status": a["status"],
                        "description": a.get("description", ""),
                        "actions_taken": a["actions_taken"],
                        "result": a.get("result"),
                        "processed_at": a.get("processed_at"),
                    }
                    for a in alerts_data
                ],
                "generated_at": datetime.now().isoformat(),
            }
            return json.dumps(output_data, indent=2, ensure_ascii=False)

        if output_format == "bullet":
            lines = [f"# {title}", ""]
            for a in alerts_data:
                lines.append(
                    f"- **Alert #{a['alert_id']}**: {a['alert_type']} "
                    f"in zone '{a['zone']}' ({a['severity']} severity)"
                )
                lines.append(f"  - Status: {a['status']}")
                lines.append(f"  - Actions taken: {len(a['actions_taken'])}")
                if a.get("result") and isinstance(a["result"], dict):
                    summary = a["result"].get("summary")
                    if summary:
                        lines.append(f"  - Summary: {summary}")
                lines.append("")
            return "\n".join(lines)

        if output_format == "timeline":
            lines = [
                f"# {title}",
                "",
                "```mermaid",
                "timeline",
                f"    title {title}",
            ]
            for a in alerts_data:
                lines.append(
                    f"    Alert #{a['alert_id']} ({a['zone']}) : "
                    f"{a['alert_type']} : {a['severity']} : {a['status']}"
                )
            lines.append("```")
            return "\n".join(lines)

        # Default: markdown
        lines = [
            f"# {title}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Alert Summary",
            "",
            f"- **Total Alerts:** {len(alerts_data)}",
        ]

        severities: Dict[str, int] = {}
        for a in alerts_data:
            sev = a.get("severity", "unknown")
            severities[sev] = severities.get(sev, 0) + 1
        severity_str = ", ".join(f"{k}: {v}" for k, v in sorted(severities.items()))
        lines.append(f"- **Severity Breakdown:** {severity_str}")

        zones_list = sorted(set(a.get("zone", "?") for a in alerts_data))
        lines.append(f"- **Zones Affected:** {', '.join(zones_list)}")
        lines.append("")

        if len(alerts_data) == 1:
            lines.append("## Incident Detail")
        else:
            lines.append("## Incident Details")
        lines.append("")

        for a in alerts_data:
            atype_title = a["alert_type"].replace("_", " ").title()
            lines.append(f"### Alert #{a['alert_id']} -- {atype_title}")
            lines.append("")
            lines.append(f"- **Zone:** {a.get('zone', '?')}")
            lines.append(f"- **Severity:** {a.get('severity', '?')}")
            lines.append(f"- **Status:** {a.get('status', '?')}")
            desc = a.get("description")
            if desc:
                lines.append(f"- **Description:** {desc}")
            lines.append(f"- **Actions Executed:** {len(a.get('actions_taken', []))}")
            result = a.get("result")
            if isinstance(result, dict) and result.get("summary"):
                lines.append(f"- **Summary:** {result['summary']}")
            processed = a.get("processed_at")
            if processed:
                lines.append(f"- **Processed:** {processed}")
            lines.append("")

        lines.append("---")
        lines.append("*Report generated by Security Patrol Pipeline*")
        return "\n".join(lines)

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })