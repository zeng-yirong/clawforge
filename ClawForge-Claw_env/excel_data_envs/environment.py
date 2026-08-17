from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .charts import (
    create_bar_chart,
    create_column_chart,
    create_line_chart,
    create_pie_chart,
    get_all_charts,
    get_chart,
)
from .evaluator import evaluate_session
from .excel_data import (
    deduplicate_data,
    fill_missing_customers,
    get_cleaned_data,
    get_data_summary,
    list_raw_data,
    read_raw_data,
)
from .formulas import (
    create_average_order_value_formula,
    create_formula,
    create_total_revenue_formula,
    create_total_transactions_formula,
    get_all_formulas,
    get_formula,
)
from .pivot import (
    create_pivot_by_category_region,
    create_pivot_by_channel,
    create_pivot_by_city,
    create_pivot_by_product,
    create_pivot_by_salesperson,
    create_pivot_table,
    get_all_pivots,
    save_pivot,
)
from .repository import DatasetRepository
from .store import SessionStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class ExcelDataEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("EXCEL_DATA_STATE_ROOT", Path.cwd() / ".excel_data_state"))
        self.repository = DatasetRepository(data_root)
        self.store = SessionStore(state_root or default_state_root)
        self.accounts = self.repository.load_accounts()

    def list_scenarios(self) -> dict[str, Any]:
        return {
            "scenarios": [
                {
                    "scenario_id": item["scenario_id"],
                    "title": item["title"],
                    "task_prompt": item["task_prompt"],
                }
                for item in self.repository.list_scenarios()
            ]
        }

    def create_session(self, session_id: str, scenario_id: str, overwrite: bool = False) -> dict[str, Any]:
        scenario = self.repository.load_scenario(scenario_id)
        session_payload = self._build_session_payload(session_id=session_id, scenario=scenario)
        self.store.create_session(session_id, session_payload, overwrite=overwrite)
        return self.session_summary(session_id)

    def reset_session(self, session_id: str) -> dict[str, Any]:
        existing = self.store.load_session(session_id)
        return self.create_session(session_id, existing["scenario_id"], overwrite=True)

    def get_task(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
            "has_cleaned_data": "cleaned_data" in session,
            "pivot_count": len(session.get("pivot_tables", [])),
            "chart_count": len(session.get("charts", [])),
            "formula_count": len(session.get("formulas", [])),
        }

    def list_raw_datasets(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_raw_data(session)
        }

    def read_raw_dataset(self, session_id: str, data_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": read_raw_data(session, data_id)
        }

    def deduplicate(
        self,
        session_id: str,
        data_id: str,
        key_column: str = "transaction_id"
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = deduplicate_data(session, data_id, key_column)
            self._record_action(session, action_index, event_at, "deduplicate", {
                "data_id": data_id,
                "key_column": key_column,
                "duplicates_removed": payload.get("duplicates_removed", 0)
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def fill_missing(
        self,
        session_id: str,
        data_id: str
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = fill_missing_customers(session, data_id)
            self._record_action(session, action_index, event_at, "fill_missing_customers", {
                "data_id": data_id,
                "rows_filled": payload.get("rows_filled", 0)
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def get_cleaned_data(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_cleaned_data(session)
        }

    def get_data_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_data_summary(session)
        }

    def create_pivot(
        self,
        session_id: str,
        row_dimensions: list[str],
        value_column: str,
        aggregation: str = "sum"
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_pivot_table(session, row_dimensions, value_column, aggregation)
            if payload.get("success"):
                save_pivot(session, payload)
            self._record_action(session, action_index, event_at, "create_pivot", {
                "row_dimensions": row_dimensions,
                "value_column": value_column,
                "aggregation": aggregation,
                "pivot_id": payload.get("pivot_id")
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_pivot_category_region(self, session_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_pivot_by_category_region(session)
            if payload.get("success"):
                save_pivot(session, payload)
            self._record_action(session, action_index, event_at, "create_pivot_category_region", {
                "pivot_id": payload.get("pivot_id")
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_pivot_salesperson(self, session_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_pivot_by_salesperson(session)
            if payload.get("success"):
                save_pivot(session, payload)
            self._record_action(session, action_index, event_at, "create_pivot_salesperson", {
                "pivot_id": payload.get("pivot_id")
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_pivot_city(self, session_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_pivot_by_city(session)
            if payload.get("success"):
                save_pivot(session, payload)
            self._record_action(session, action_index, event_at, "create_pivot_city", {
                "pivot_id": payload.get("pivot_id")
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def get_all_pivots(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_all_pivots(session)
        }

    def create_bar_chart(
        self,
        session_id: str,
        chart_id: str,
        title: str,
        x_axis_column: str,
        y_axis_column: str,
        aggregation: str = "sum"
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_bar_chart(session, chart_id, title, x_axis_column, y_axis_column, aggregation)
            self._record_action(session, action_index, event_at, "create_bar_chart", {
                "chart_id": chart_id,
                "title": title
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_pie_chart(
        self,
        session_id: str,
        chart_id: str,
        title: str,
        label_column: str,
        value_column: str,
        aggregation: str = "sum"
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_pie_chart(session, chart_id, title, label_column, value_column, aggregation)
            self._record_action(session, action_index, event_at, "create_pie_chart", {
                "chart_id": chart_id,
                "title": title
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_line_chart(
        self,
        session_id: str,
        chart_id: str,
        title: str,
        x_axis_column: str,
        y_axis_column: str,
        aggregation: str = "sum"
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_line_chart(session, chart_id, title, x_axis_column, y_axis_column, aggregation)
            self._record_action(session, action_index, event_at, "create_line_chart", {
                "chart_id": chart_id,
                "title": title
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_column_chart(
        self,
        session_id: str,
        chart_id: str,
        title: str,
        x_axis_column: str,
        y_axis_column: str,
        aggregation: str = "sum"
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_column_chart(session, chart_id, title, x_axis_column, y_axis_column, aggregation)
            self._record_action(session, action_index, event_at, "create_column_chart", {
                "chart_id": chart_id,
                "title": title
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def get_all_charts(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_all_charts(session)
        }

    def get_chart(self, session_id: str, chart_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_chart(session, chart_id)
        }

    def create_formula(
        self,
        session_id: str,
        name: str,
        expression: str,
        description: str = ""
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_formula(session, name, expression, description)
            self._record_action(session, action_index, event_at, "create_formula", {
                "name": name,
                "expression": expression
            })
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_total_revenue(self, session_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_total_revenue_formula(session)
            self._record_action(session, action_index, event_at, "create_total_revenue", {})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_average_order_value(self, session_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_average_order_value_formula(session)
            self._record_action(session, action_index, event_at, "create_average_order_value", {})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def create_total_transactions(self, session_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = create_total_transactions_formula(session)
            self._record_action(session, action_index, event_at, "create_total_transactions", {})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def get_all_formulas(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_all_formulas(session)
        }

    def get_formula(self, session_id: str, name: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": get_formula(session, name)
        }

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "has_cleaned_data": "cleaned_data" in session,
            "pivot_count": len(session.get("pivot_tables", [])),
            "chart_count": len(session.get("charts", [])),
            "formula_count": len(session.get("formulas", [])),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        raw_data = {}
        for data_id in scenario.get("raw_data_ids", []):
            raw_data[data_id] = self.repository.load_raw_data(data_id)

        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": _utc_now_iso(),
            "meta": {
                "base_time": scenario["current_time"],
                "action_index": 0,
            },
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "raw_data": raw_data,
            "cleaned_data": None,
            "pivot_tables": [],
            "charts": [],
            "formulas": [],
            "actions": [],
        }

    def _next_event(self, session: dict[str, Any]) -> tuple[str, int]:
        action_index = int(session["meta"]["action_index"]) + 1
        session["meta"]["action_index"] = action_index
        event_at = (_coerce_iso_datetime(session["meta"]["base_time"]) + timedelta(minutes=action_index)).isoformat()
        return event_at, action_index

    def _record_action(
        self,
        session: dict[str, Any],
        action_index: int,
        event_at: str,
        action_type: str,
        details: dict[str, Any],
    ) -> None:
        session["actions"].append(
            {
                "action_index": action_index,
                "timestamp": event_at,
                "action_type": action_type,
                "details": details,
            }
        )
