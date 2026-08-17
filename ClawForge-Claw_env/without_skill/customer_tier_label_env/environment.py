from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from without_skill._shared.base_env import LoggedEnvironmentBase, utc_now_iso
from without_skill._shared.customer_memory import CustomerMemoryRepository, get_customer, list_customers
from without_skill._shared.records import append_indexed_record, get_indexed_record, list_indexed_records, make_action_record_id
from without_skill._shared.json_repository import load_json


class CustomerTierRepository(CustomerMemoryRepository):
    def __init__(self, data_root: str | Path | None = None):
        super().__init__(data_root)
        self.consumption_logs_file = self.data_root / "data" / "logs" / "consumption_logs.json"

    def load_consumption_logs(self) -> dict[str, dict[str, object]]:
        payload = load_json(self.consumption_logs_file)
        return {item["customer_id"]: item for item in payload["consumption_logs"]}


class CustomerTierLabelEnvironment(LoggedEnvironmentBase):
    state_root_env_var = "CUSTOMER_TIER_LABEL_STATE_ROOT"
    default_state_dir_name = ".customer_tier_label_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        resolved_data_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.repository = CustomerTierRepository(resolved_data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()
        self.attachment_manifest = self.repository.load_attachment_manifest()

    def list_customers(self, session_id: str, *, query: str = "", industry: str | None = None, risk_level: str | None = None, limit: int | None = None) -> dict[str, object]:
        def handler(session: dict[str, object], _event_at: str, _action_index: int) -> list[dict[str, object]]:
            data = list_customers(session, query=query, industry=industry, risk_level=risk_level, limit=limit)
            for item in data:
                self._append_unique(session["observations"]["customer_ids_seen"], str(item["customer_id"]))
            return data
        return self._run_logged_action(session_id, "list_customers", {"query": query, "industry": industry, "risk_level": risk_level}, handler)

    def get_customer(self, session_id: str, customer_id: str) -> dict[str, object]:
        def handler(session: dict[str, object], _event_at: str, _action_index: int) -> dict[str, object]:
            payload = get_customer(session, customer_id)
            payload["consumption_log"] = deepcopy(session["consumption_logs"].get(customer_id, {}))
            self._append_unique(session["observations"]["customer_ids_seen"], customer_id)
            return payload
        return self._run_logged_action(session_id, "get_customer", {"customer_id": customer_id}, handler)

    def get_customer_metrics(self, session_id: str, customer_id: str) -> dict[str, object]:
        def handler(session: dict[str, object], _event_at: str, _action_index: int) -> dict[str, object]:
            customer = get_customer(session, customer_id)
            self._append_unique(session["observations"]["customer_ids_seen"], customer_id)
            return {
                "customer_id": customer_id,
                "activity_log": deepcopy(session["activity_logs"].get(customer_id, {})),
                "consumption_log": deepcopy(session["consumption_logs"].get(customer_id, {})),
            }
        return self._run_logged_action(session_id, "get_customer_metrics", {"customer_id": customer_id}, handler)

    def read_attachment(self, session_id: str, attachment_path: str) -> dict[str, object]:
        def handler(session: dict[str, object], _event_at: str, _action_index: int) -> dict[str, object]:
            if attachment_path not in self.attachment_manifest:
                raise FileNotFoundError(f"Attachment not found: {attachment_path}")
            metadata = deepcopy(self.attachment_manifest[attachment_path])
            metadata["content"] = self.repository.read_attachment(attachment_path)
            self._append_unique(session["observations"]["attachments_read"], attachment_path)
            return metadata
        return self._run_logged_action(session_id, "read_attachment", {"attachment_path": attachment_path}, handler)

    def update_customer_labels(self, session_id: str, customer_id: str) -> dict[str, object]:
        def handler(session: dict[str, object], event_at: str, action_index: int) -> dict[str, object]:
            for customer in session["customers"]:
                if customer["customer_id"] != customer_id:
                    continue
                activity = session["activity_logs"].get(customer_id, {})
                consumption = session["consumption_logs"].get(customer_id, {})
                labels: list[str] = []
                if float(consumption.get("quarter_spend_usd", 0)) >= 100000 and int(activity.get("last_active_days", 999)) <= 7:
                    labels.append("vip_active")
                if float(consumption.get("quarter_spend_usd", 0)) < 30000 and int(activity.get("last_active_days", 999)) >= 20:
                    labels.append("low_engagement")
                if activity.get("risk_level") == "high":
                    labels.append("retention_risk")
                customer["labels"] = labels
                record = {
                    "update_id": make_action_record_id("labelupd", action_index),
                    "record_type": "customer_label_update",
                    "created_at": event_at,
                    "customer_id": customer_id,
                    "labels": labels,
                }
                append_indexed_record(
                    session,
                    collection_name="update_logs",
                    index_name="update_log_index",
                    id_field="update_id",
                    record=record,
                )
                self._append_unique(session["observations"]["updated_customer_ids"], customer_id)
                return deepcopy(record)
            raise KeyError(f"Customer not found: {customer_id}")
        return self._run_logged_action(session_id, "update_customer_labels", {"customer_id": customer_id}, handler)

    def list_update_logs(self, session_id: str, *, limit: int | None = None) -> dict[str, object]:
        return self._run_logged_action(
            session_id,
            "list_update_logs",
            {},
            lambda session, _event_at, _action_index: list_indexed_records(
                session,
                collection_name="update_logs",
                limit=limit,
                summary_builder=lambda record: {
                    "update_id": record["update_id"],
                    "customer_id": record["customer_id"],
                    "labels": record["labels"],
                    "created_at": record["created_at"],
                },
            ),
        )

    def get_update_log(self, session_id: str, update_id: str) -> dict[str, object]:
        return self._run_logged_action(
            session_id,
            "get_update_log",
            {"update_id": update_id},
            lambda session, _event_at, _action_index: get_indexed_record(
                session,
                collection_name="update_logs",
                index_name="update_log_index",
                record_id=update_id,
                error_label="Update log",
            ),
        )

    def evaluate_session(self, session_id: str) -> dict[str, object]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, object]) -> dict[str, object]:
        all_customers = self.repository.load_customers()
        all_activity = self.repository.load_activity_logs()
        all_consumption = self.repository.load_consumption_logs()
        attachments = [
            deepcopy(self.attachment_manifest[path])
            for path in scenario.get("attachment_paths", [])
            if path in self.attachment_manifest
        ]
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "customers": [deepcopy(all_customers[cid]) for cid in scenario["customer_ids"]],
            "activity_logs": {cid: deepcopy(all_activity[cid]) for cid in scenario["customer_ids"]},
            "consumption_logs": {cid: deepcopy(all_consumption[cid]) for cid in scenario["customer_ids"]},
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "update_logs": [],
            "update_log_index": {},
            "observations": {
                "customer_ids_seen": [],
                "attachments_read": [],
                "updated_customer_ids": [],
            },
            "actions": [],
        }

    def _build_task_payload(self, session_id: str, session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
            "customer_count": len(session["customers"]),
        }

    def session_summary(self, session_id: str) -> dict[str, object]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "customer_count": len(session["customers"]),
            "updated_customer_count": len(session["observations"]["updated_customer_ids"]),
            "update_log_count": len(session["update_logs"]),
            "action_count": len(session["actions"]),
        }
