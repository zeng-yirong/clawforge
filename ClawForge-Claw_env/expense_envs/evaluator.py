from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    scoring_rules = scenario.get("scoring_rules", {})
    dimensions = scoring_rules.get("dimensions", [])

    actions = session.get("actions", [])
    expense_state = session.get("expense_state", {})

    scores: dict[str, float] = {}
    total_weight = sum(d.get("weight", 0) for d in dimensions)

    for dim in dimensions:
        name = dim.get("dimension", dim.get("name", ""))
        weight = dim.get("weight", 0)
        if name == "policy_loading":
            scores[name] = _evaluate_policy_loading(actions, expense_state) * weight
        elif name == "budget_calculation":
            scores[name] = _evaluate_budget_calculation(actions, expense_state) * weight
        elif name == "consumption_loading":
            scores[name] = _evaluate_consumption_loading(actions, expense_state) * weight
        elif name == "analysis_generation":
            scores[name] = _evaluate_analysis_generation(actions, expense_state) * weight
        elif name == "report_export":
            scores[name] = _evaluate_report_export(actions, expense_state) * weight
        else:
            scores[name] = 0.5 * weight

    total_score = sum(scores.values())

    return {
        "overall_score": round(total_score, 4),
        "dimension_scores": {k: round(v, 4) for k, v in scores.items()},
        "total_actions": len(actions),
        "report_generated": expense_state.get("report_generated", False),
    }


def _evaluate_policy_loading(actions: list[dict[str, Any]], expense_state: dict[str, Any]) -> float:
    policy_actions = [a for a in actions if a.get("action_type") == "load_policy"]
    if not policy_actions:
        return 0.0
    for action in policy_actions:
        result = action.get("result", {})
        if result.get("status") == "success" and result.get("data", {}).get("policy"):
            return 1.0
    return 0.5


def _evaluate_budget_calculation(actions: list[dict[str, Any]], expense_state: dict[str, Any]) -> float:
    budget_actions = [a for a in actions if a.get("action_type") == "calculate_budget"]
    if not budget_actions:
        return 0.0
    budget = expense_state.get("calculated_budget")
    if budget and budget.get("status") == "success":
        return 1.0
    return 0.5


def _evaluate_consumption_loading(actions: list[dict[str, Any]], expense_state: dict[str, Any]) -> float:
    consumption_actions = [a for a in actions if a.get("action_type") == "load_consumption"]
    if not consumption_actions:
        return 0.0
    consumption = expense_state.get("loaded_consumption")
    if consumption and consumption.get("records"):
        return 1.0
    return 0.5


def _evaluate_analysis_generation(actions: list[dict[str, Any]], expense_state: dict[str, Any]) -> float:
    analysis_actions = [a for a in actions if a.get("action_type") == "generate_analysis"]
    if not analysis_actions:
        return 0.0
    analysis = expense_state.get("analysis_result")
    if analysis and analysis.get("status") == "success":
        return 1.0
    return 0.5


def _evaluate_report_export(actions: list[dict[str, Any]], expense_state: dict[str, Any]) -> float:
    export_actions = [a for a in actions if a.get("action_type") == "export_report"]
    if not export_actions:
        return 0.0
    for action in export_actions:
        result = action.get("result", {})
        if result.get("status") == "success":
            return 1.0
    return 0.5
