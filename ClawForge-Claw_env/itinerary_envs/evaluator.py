from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    scoring_rules = scenario.get("scoring_rules", {})
    dimensions = scoring_rules.get("dimensions", [])

    actions = session.get("actions", [])
    itinerary_state = session.get("itinerary_state", {})

    scores: dict[str, float] = {}
    total_weight = sum(d.get("weight", 0) for d in dimensions)

    for dim in dimensions:
        name = dim.get("dimension", dim.get("name", ""))
        weight = dim.get("weight", 0)
        if name == "city_loading":
            scores[name] = _evaluate_city_loading(actions, itinerary_state) * weight
        elif name == "route_search":
            scores[name] = _evaluate_route_search(actions, itinerary_state) * weight
        elif name == "transport_comparison":
            scores[name] = _evaluate_transport_comparison(actions, itinerary_state) * weight
        elif name == "transfer_planning":
            scores[name] = _evaluate_transfer_planning(actions, itinerary_state) * weight
        elif name == "itinerary_generation":
            scores[name] = _evaluate_itinerary_generation(actions, itinerary_state) * weight
        elif name == "route_optimization":
            scores[name] = _evaluate_route_optimization(actions, itinerary_state) * weight
        else:
            scores[name] = 0.5 * weight

    total_score = sum(scores.values())

    return {
        "overall_score": round(total_score, 4),
        "dimension_scores": {k: round(v, 4) for k, v in scores.items()},
        "total_actions": len(actions),
        "itinerary_generated": itinerary_state.get("generated_itinerary") is not None,
    }


def _evaluate_city_loading(actions: list[dict[str, Any]], itinerary_state: dict[str, Any]) -> float:
    city_actions = [a for a in actions if a.get("action_type") == "load_cities"]
    if not city_actions:
        return 0.0
    for action in city_actions:
        result = action.get("result", {})
        if result.get("status") == "success" and result.get("data"):
            return 1.0
    return 0.5


def _evaluate_route_search(actions: list[dict[str, Any]], itinerary_state: dict[str, Any]) -> float:
    search_actions = [a for a in actions if a.get("action_type") == "search_routes"]
    if not search_actions:
        return 0.0
    for action in search_actions:
        result = action.get("result", {})
        if result.get("status") == "success" and result.get("data", {}).get("transport_options"):
            return 1.0
    return 0.5


def _evaluate_transport_comparison(actions: list[dict[str, Any]], itinerary_state: dict[str, Any]) -> float:
    compare_actions = [a for a in actions if a.get("action_type") == "compare_transport"]
    if not compare_actions:
        return 0.0
    for action in compare_actions:
        result = action.get("result", {})
        if result.get("status") == "success" and result.get("data", {}).get("options"):
            return 1.0
    return 0.5


def _evaluate_transfer_planning(actions: list[dict[str, Any]], itinerary_state: dict[str, Any]) -> float:
    transfer_actions = [a for a in actions if a.get("action_type") == "plan_transfer"]
    if not transfer_actions:
        return 0.0
    for action in transfer_actions:
        result = action.get("result", {})
        if result.get("status") == "success" and result.get("data", {}).get("legs"):
            return 1.0
    return 0.5


def _evaluate_itinerary_generation(actions: list[dict[str, Any]], itinerary_state: dict[str, Any]) -> float:
    itinerary_actions = [a for a in actions if a.get("action_type") == "generate_itinerary"]
    if not itinerary_actions:
        return 0.0
    for action in itinerary_actions:
        result = action.get("result", {})
        if result.get("status") == "success" and result.get("data", {}).get("segments"):
            return 1.0
    return 0.5


def _evaluate_route_optimization(actions: list[dict[str, Any]], itinerary_state: dict[str, Any]) -> float:
    optimize_actions = [a for a in actions if a.get("action_type") == "optimize_route"]
    if not optimize_actions:
        return 0.0
    for action in optimize_actions:
        result = action.get("result", {})
        if result.get("status") == "success":
            return 1.0
    return 0.5
