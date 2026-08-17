from __future__ import annotations

import random
import secrets
import string
from typing import Any


class PasswordGenerator:
    CHARSETS = {
        "alphanumeric": string.ascii_letters + string.digits,
        "complex": string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?",
        "pin": string.digits,
    }

    def generate_password(
        self,
        length: int = 16,
        charset: str = "alphanumeric",
        policy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if charset not in self.CHARSETS:
            return {
                "status": "error",
                "message": f"Unknown charset: {charset}. Use: {list(self.CHARSETS.keys())}",
            }

        chars = self.CHARSETS[charset]

        if policy is None:
            policy = {}

        min_length = policy.get("min_length", length)
        require_uppercase = policy.get("require_uppercase", False)
        require_lowercase = policy.get("require_lowercase", False)
        require_digits = policy.get("require_digits", False)
        require_special = policy.get("require_special", False)

        actual_length = max(length, min_length)

        password_chars = []

        if require_uppercase:
            password_chars.append(random.choice(string.ascii_uppercase))
        if require_lowercase:
            password_chars.append(random.choice(string.ascii_lowercase))
        if require_digits:
            password_chars.append(random.choice(string.digits))
        if require_special:
            password_chars.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))

        remaining_length = actual_length - len(password_chars)
        if remaining_length > 0:
            password_chars.extend(secrets.choice(chars) for _ in range(remaining_length))

        secrets.SystemRandom().shuffle(password_chars)
        password = "".join(password_chars)

        if not self._meets_policy(password, policy):
            return self.generate_password(length, charset, policy)

        return {
            "status": "success",
            "data": {
                "password": password,
                "length": len(password),
                "charset": charset,
                "policy_met": self._meets_policy(password, policy),
            },
        }

    def _meets_policy(self, password: str, policy: dict[str, Any]) -> bool:
        if len(password) < policy.get("min_length", 0):
            return False
        if policy.get("require_uppercase") and not any(c.isupper() for c in password):
            return False
        if policy.get("require_lowercase") and not any(c.islower() for c in password):
            return False
        if policy.get("require_digits") and not any(c.isdigit() for c in password):
            return False
        if policy.get("require_special") and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        return True
