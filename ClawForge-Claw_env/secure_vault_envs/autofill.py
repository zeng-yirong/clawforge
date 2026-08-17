from __future__ import annotations

from typing import Any


class AutofillController:
    def __init__(self, session: dict[str, Any], store: Any, session_id: str):
        self.session = session
        self.store = store
        self.session_id = session_id

    def _get_vault_state(self) -> dict[str, Any]:
        return self.session.get("vault_state", {
            "stored_credentials": [],
            "autofill_rules": {},
            "password_history": [],
        })

    def _update_vault_state(self, updates: dict[str, Any]) -> None:
        vault_state = self._get_vault_state()
        vault_state.update(updates)
        self.session["vault_state"] = vault_state

    def setup_autofill(self, platform: str, field_mappings: dict[str, Any]) -> dict[str, Any]:
        vault_state = self._get_vault_state()
        autofill_rules = vault_state.get("autofill_rules", {})

        autofill_rules[platform] = {
            "platform": platform,
            "field_mappings": field_mappings,
            "enabled": True,
        }

        self._update_vault_state({"autofill_rules": autofill_rules})
        self.store.save_session(self.session_id, self.session)

        return {
            "status": "success",
            "data": {
                "platform": platform,
                "field_mappings": field_mappings,
                "configured": True,
            },
        }

    def get_autofill_data(self, platform: str) -> dict[str, Any]:
        vault_state = self._get_vault_state()
        autofill_rules = vault_state.get("autofill_rules", {})

        if platform in autofill_rules:
            return {
                "status": "success",
                "data": autofill_rules[platform],
            }

        return {"status": "error", "message": f"No autofill configuration found for platform: {platform}"}

    def match_field(self, field_name: str, mappings: dict[str, Any]) -> str | None:
        field_lower = field_name.lower()

        for stored_value, aliases in mappings.items():
            if isinstance(aliases, list):
                if field_lower in [alias.lower() for alias in aliases]:
                    return stored_value
            elif field_lower == aliases.lower():
                return stored_value

        return None

    def list_autofill_configurations(self) -> dict[str, Any]:
        vault_state = self._get_vault_state()
        autofill_rules = vault_state.get("autofill_rules", {})

        configs = []
        for platform, config in autofill_rules.items():
            configs.append({
                "platform": platform,
                "field_mappings": config.get("field_mappings", {}),
                "enabled": config.get("enabled", True),
            })

        return {
            "status": "success",
            "data": {
                "configurations": configs,
                "total": len(configs),
            },
        }
