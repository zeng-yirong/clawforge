from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .repository import VaultRepository
from .store import SessionStore
from .vault import VaultController
from .generator import PasswordGenerator
from .autofill import AutofillController


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _action_timestamp(base_time: str, action_index: int) -> str:
    base = _coerce_iso_datetime(base_time)
    return (base + timedelta(seconds=action_index * 30)).isoformat()


class SecureVaultEnvironment:
    def __init__(
        self,
        data_root: Path | str,
        state_root: Path | str,
    ):
        self.data_root = Path(data_root)
        self.state_root = Path(state_root)
        self.repo = VaultRepository(data_root)
        self.store = SessionStore(state_root)
        self.generator = PasswordGenerator()

    def _get_binding(self, key: str) -> str | None:
        env_key = f"VAULT_{key}"
        return os.environ.get(env_key)

    def prepare_rollout(self, scenario_id: str, show_bindings: bool = False) -> dict[str, Any]:
        scenario = self.repo.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        base_time = scenario.get("base_time", _utc_now_iso())
        workspace_account_id = scenario.get("workspace_account_id", "acc_001")
        account = self.repo.get_account(workspace_account_id)
        if not account:
            raise ValueError(f"Account {workspace_account_id} not found")

        import uuid
        session_id = f"vault-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:4]}"

        state_root = str(self.state_root)
        self.store.create_session(
            session_id=session_id,
            scenario_id=scenario_id,
            base_time=base_time,
            workspace_account=account,
        )

        bindings = {
            "VAULT_SESSION_ID": session_id,
            "VAULT_STATE_ROOT": state_root,
            "VAULT_SCENARIO_ID": scenario_id,
        }

        result = {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "state_root": state_root,
            "bindings": bindings,
        }
        return result

    def reset_rollout(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        scenario = self.repo.get_scenario(session["scenario_id"])
        if not scenario:
            raise ValueError(f"Scenario {session['scenario_id']} not found")

        base_time = scenario.get("base_time", _utc_now_iso())
        workspace_account_id = scenario.get("workspace_account_id", "acc_001")
        account = self.repo.get_account(workspace_account_id)

        self.store.delete_session(session_id)
        self.store.create_session(
            session_id=session_id,
            scenario_id=session["scenario_id"],
            base_time=base_time,
            workspace_account=account,
        )

        return {"session_id": session_id, "status": "reset"}

    def execute_action(
        self,
        session_id: str,
        action_type: str,
        action_index: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        base_time = session["meta"]["base_time"]
        timestamp = _action_timestamp(base_time, action_index)

        vault_ctrl = VaultController(session, self.store, session_id)
        autofill_ctrl = AutofillController(session, self.store, session_id)
        result: dict[str, Any] = {"status": "ok"}

        if action_type == "generate_password":
            length = kwargs.get("length", 16)
            charset = kwargs.get("charset", "alphanumeric")
            policy = kwargs.get("policy", {})
            result = self.generator.generate_password(length, charset, policy)
        elif action_type == "store_credential":
            credential_data = kwargs.get("credential_data", {})
            if not credential_data:
                return {"status": "error", "message": "credential_data is required"}
            result = vault_ctrl.store_credential(credential_data)
        elif action_type == "retrieve_credential":
            platform = kwargs.get("platform")
            if not platform:
                return {"status": "error", "message": "platform is required"}
            result = vault_ctrl.retrieve_credential(platform)
        elif action_type == "list_credentials":
            result = vault_ctrl.list_credentials()
        elif action_type == "classify_credential":
            credential_id = kwargs.get("credential_id")
            category_id = kwargs.get("category_id")
            if not credential_id or not category_id:
                return {"status": "error", "message": "credential_id and category_id are required"}
            result = vault_ctrl.classify_credential(credential_id, category_id)
        elif action_type == "setup_autofill":
            platform = kwargs.get("platform")
            field_mappings = kwargs.get("field_mappings", {})
            if not platform:
                return {"status": "error", "message": "platform is required"}
            result = autofill_ctrl.setup_autofill(platform, field_mappings)
        elif action_type == "check_password_strength":
            password = kwargs.get("password")
            policy = kwargs.get("policy", {})
            if not password:
                return {"status": "error", "message": "password is required"}
            result = vault_ctrl.check_password_strength(password, policy)
        elif action_type == "get_autofill_data":
            platform = kwargs.get("platform")
            if not platform:
                return {"status": "error", "message": "platform is required"}
            result = autofill_ctrl.get_autofill_data(platform)
        elif action_type == "list_autofill_configurations":
            result = autofill_ctrl.list_autofill_configurations()
        else:
            result = {"status": "error", "message": f"Unknown action: {action_type}"}

        session["meta"]["action_index"] = action_index + 1
        session["actions"].append({
            "action_index": action_index,
            "timestamp": timestamp,
            "action_type": action_type,
            "details": kwargs,
            "result": result,
        })
        self.store.save_session(session_id, session)

        return result

    def get_session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "vault_state": session["vault_state"],
            "action_count": len(session.get("actions", [])),
        }

    def get_reward(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        scenario = self.repo.get_scenario(session["scenario_id"])
        if not scenario:
            raise ValueError(f"Scenario {session['scenario_id']} not found")
        return evaluate_session(session, scenario)
