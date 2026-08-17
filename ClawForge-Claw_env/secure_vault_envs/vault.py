from __future__ import annotations

import base64
import hashlib
import json
import secrets
from typing import Any


class VaultController:
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

    def _encrypt_value(self, value: str) -> str:
        key = hashlib.sha256(self.session_id.encode()).digest()
        encrypted = bytes(a ^ b for a, b in zip(value.encode(), (key * (len(value) // len(key) + 1))[:len(value)]))
        return base64.b64encode(encrypted).decode()

    def _decrypt_value(self, encrypted: str) -> str:
        key = hashlib.sha256(self.session_id.encode()).digest()
        encrypted_bytes = base64.b64decode(encrypted.encode())
        decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, (key * (len(encrypted_bytes) // len(key) + 1))[:len(encrypted_bytes)]))
        return decrypted.decode()

    def store_credential(self, credential_data: dict[str, Any]) -> dict[str, Any]:
        platform = credential_data.get("platform")
        if not platform:
            return {"status": "error", "message": "Platform is required"}

        vault_state = self._get_vault_state()
        credentials = vault_state.get("stored_credentials", [])

        credential_id = f"cred_{secrets.token_hex(8)}"
        encrypted_credential = {
            "credential_id": credential_id,
            "platform": platform,
            "username": credential_data.get("username"),
            "encrypted_password": self._encrypt_value(credential_data.get("password", "")),
            "category_id": credential_data.get("category_id"),
            "url": credential_data.get("url"),
            "notes": credential_data.get("notes"),
            "mfa_enabled": credential_data.get("mfa_enabled", False),
            "created_at": credential_data.get("created_at"),
        }
        credentials.append(encrypted_credential)
        self._update_vault_state({"stored_credentials": credentials})

        if credential_data.get("password"):
            password_history = vault_state.get("password_history", [])
            password_history.append({
                "platform": platform,
                "password": credential_data["password"],
                "stored_at": credential_data.get("created_at"),
            })
            self._update_vault_state({"password_history": password_history})

        self.store.save_session(self.session_id, self.session)

        return {
            "status": "success",
            "data": {
                "credential_id": credential_id,
                "platform": platform,
                "encrypted": True,
            },
        }

    def retrieve_credential(self, platform: str) -> dict[str, Any]:
        vault_state = self._get_vault_state()
        credentials = vault_state.get("stored_credentials", [])

        for cred in credentials:
            if cred.get("platform") == platform:
                return {
                    "status": "success",
                    "data": {
                        "credential_id": cred.get("credential_id"),
                        "platform": cred.get("platform"),
                        "username": cred.get("username"),
                        "password": self._decrypt_value(cred.get("encrypted_password", "")),
                        "category_id": cred.get("category_id"),
                        "url": cred.get("url"),
                        "mfa_enabled": cred.get("mfa_enabled", False),
                    },
                }

        return {"status": "error", "message": f"No credential found for platform: {platform}"}

    def list_credentials(self) -> dict[str, Any]:
        vault_state = self._get_vault_state()
        credentials = vault_state.get("stored_credentials", [])

        safe_credentials = []
        for cred in credentials:
            safe_credentials.append({
                "credential_id": cred.get("credential_id"),
                "platform": cred.get("platform"),
                "username": cred.get("username"),
                "category_id": cred.get("category_id"),
                "url": cred.get("url"),
                "mfa_enabled": cred.get("mfa_enabled", False),
            })

        return {
            "status": "success",
            "data": {
                "credentials": safe_credentials,
                "total": len(safe_credentials),
            },
        }

    def classify_credential(self, credential_id: str, category_id: str) -> dict[str, Any]:
        vault_state = self._get_vault_state()
        credentials = vault_state.get("stored_credentials", [])

        for cred in credentials:
            if cred.get("credential_id") == credential_id:
                cred["category_id"] = category_id
                self._update_vault_state({"stored_credentials": credentials})
                self.store.save_session(self.session_id, self.session)
                return {
                    "status": "success",
                    "data": {
                        "credential_id": credential_id,
                        "category_id": category_id,
                    },
                }

        return {"status": "error", "message": f"Credential {credential_id} not found"}

    def check_password_strength(self, password: str, policy: dict[str, Any]) -> dict[str, Any]:
        min_length = policy.get("min_length", 8)
        require_uppercase = policy.get("require_uppercase", False)
        require_lowercase = policy.get("require_lowercase", False)
        require_digits = policy.get("require_digits", False)
        require_special = policy.get("require_special", False)

        score = 0
        checks = {
            "length_ok": len(password) >= min_length,
            "has_uppercase": any(c.isupper() for c in password) if require_uppercase else True,
            "has_lowercase": any(c.islower() for c in password) if require_lowercase else True,
            "has_digits": any(c.isdigit() for c in password) if require_digits else True,
            "has_special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password) if require_special else True,
        }

        if checks["length_ok"]:
            score += 0.2
        if checks["has_uppercase"]:
            score += 0.2
        if checks["has_lowercase"]:
            score += 0.2
        if checks["has_digits"]:
            score += 0.2
        if checks["has_special"]:
            score += 0.2

        strength = "weak"
        if score >= 0.8:
            strength = "strong"
        elif score >= 0.5:
            strength = "medium"

        return {
            "status": "success",
            "data": {
                "score": round(score, 2),
                "strength": strength,
                "checks": checks,
                "meets_policy": all(checks.values()),
            },
        }
