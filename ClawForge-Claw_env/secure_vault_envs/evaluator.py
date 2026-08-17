from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    scoring_rules = scenario.get("scoring_rules", {})

    actions = session.get("actions", [])
    vault_state = session.get("vault_state", {})

    scores: dict[str, float] = {}
    total_score = 0.0

    password_gen_score = _evaluate_password_generation(actions, vault_state, scoring_rules.get("password_generation", {}))
    scores["password_generation"] = password_gen_score

    credential_storage_score = _evaluate_credential_storage(actions, vault_state, scoring_rules.get("credential_storage", {}))
    scores["credential_storage"] = credential_storage_score

    autofill_score = _evaluate_autofill_setup(actions, vault_state, scoring_rules.get("auto_fill", {}))
    scores["autofill_setup"] = autofill_score

    security_score = _evaluate_security_best_practices(actions, vault_state, scoring_rules.get("security_best_practices", {}))
    scores["security_best_practices"] = security_score

    total_score = sum(scores.values())

    return {
        "overall_score": round(total_score, 4),
        "dimension_scores": {k: round(v, 4) for k, v in scores.items()},
        "total_actions": len(actions),
    }


def _evaluate_password_generation(actions: list[dict[str, Any]], vault_state: dict[str, Any], rules: dict[str, Any]) -> float:
    gen_actions = [a for a in actions if a.get("action_type") == "generate_password"]
    if not gen_actions:
        return 0.0

    score = 0.0
    high_strength_count = 0
    policy_met_count = 0

    for action in gen_actions:
        result = action.get("result", {})
        if result.get("status") == "success":
            data = result.get("data", {})
            password = data.get("password", "")
            policy_met = data.get("policy_met", False)

            if len(password) >= 14:
                high_strength_count += 1
            if policy_met:
                policy_met_count += 1

    total = len(gen_actions)
    if total > 0:
        score += rules.get("high_strength_generated", 0.2) * (high_strength_count / total)
        score += rules.get("meets_policy", 0.1) * (policy_met_count / total)

        password_history = vault_state.get("password_history", [])
        if password_history:
            platforms = [p.get("platform") for p in password_history]
            unique_platforms = set(platforms)
            score += rules.get("unique_per_platform", 0.05) * min(1.0, len(unique_platforms) / max(1, len(platforms)))

    return min(score, 1.0)


def _evaluate_credential_storage(actions: list[dict[str, Any]], vault_state: dict[str, Any], rules: dict[str, Any]) -> float:
    store_actions = [a for a in actions if a.get("action_type") == "store_credential"]
    if not store_actions:
        return 0.0

    score = 0.0
    encrypted_count = 0
    classified_count = 0
    complete_count = 0

    stored_creds = vault_state.get("stored_credentials", [])

    for action in store_actions:
        result = action.get("result", {})
        if result.get("status") == "success":
            data = result.get("data", {})
            if data.get("encrypted"):
                encrypted_count += 1
            if data.get("credential_id"):
                for cred in stored_creds:
                    if cred.get("credential_id") == data.get("credential_id") and cred.get("category_id"):
                        classified_count += 1
                        break
            if data.get("platform") and data.get("username"):
                complete_count += 1

    total = len(store_actions)
    if total > 0:
        score += rules.get("encrypted_storage", 0.15) * (encrypted_count / total)
        score += rules.get("proper_classification", 0.1) * (classified_count / total)
        score += rules.get("complete_record", 0.1) * (complete_count / total)

    return min(score, 1.0)


def _evaluate_autofill_setup(actions: list[dict[str, Any]], vault_state: dict[str, Any], rules: dict[str, Any]) -> float:
    autofill_actions = [a for a in actions if a.get("action_type") == "setup_autofill"]
    if not autofill_actions:
        return 0.0

    score = 0.0
    configured_count = 0
    correct_mapping_count = 0

    autofill_rules = vault_state.get("autofill_rules", {})

    for action in autofill_actions:
        result = action.get("result", {})
        if result.get("status") == "success":
            data = result.get("data", {})
            if data.get("configured"):
                configured_count += 1
            field_mappings = data.get("field_mappings", {})
            if field_mappings and len(field_mappings) >= 2:
                correct_mapping_count += 1

    total = len(autofill_actions)
    if total > 0:
        score += rules.get("rules_configured", 0.1) * (configured_count / total)
        score += rules.get("correct_field_mapping", 0.05) * (correct_mapping_count / total)

    return min(score, 1.0)


def _evaluate_security_best_practices(actions: list[dict[str, Any]], vault_state: dict[str, Any], rules: dict[str, Any]) -> float:
    score = 0.0

    password_history = vault_state.get("password_history", [])
    if password_history:
        passwords = [p.get("password") for p in password_history if p.get("password")]
        unique_passwords = set(passwords)
        if len(passwords) > 0 and len(unique_passwords) == len(passwords):
            score += rules.get("no_duplicate_passwords", 0.1)

    stored_creds = vault_state.get("stored_credentials", [])
    critical_mfa = 0
    for cred in stored_creds:
        category_id = cred.get("category_id")
        if category_id in ["work_email", "banking"]:
            if cred.get("mfa_enabled"):
                critical_mfa += 1

    if stored_creds:
        score += rules.get("mfa_enabled_for_critical", 0.05) * (critical_mfa / max(1, len([c for c in stored_creds if c.get("category_id") in ["work_email", "banking"]])))

    return min(score, 1.0)
