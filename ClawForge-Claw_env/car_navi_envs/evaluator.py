from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    scoring_rules = scenario.get("scoring_rules", {})
    dimensions = scoring_rules.get("dimensions", [])

    actions = session.get("actions", [])
    navigation_state = session.get("navigation_state", {})

    scores: dict[str, float] = {}
    total_weight = sum(d.get("weight", 0) for d in dimensions)

    for dim in dimensions:
        name = dim.get("dimension", dim.get("name", ""))
        weight = dim.get("weight", 0)
        if name == "poi_search":
            scores[name] = _evaluate_poi_search(actions) * weight
        elif name == "navigation_start":
            scores[name] = _evaluate_navigation_start(actions, navigation_state) * weight
        elif name == "waypoint_management":
            scores[name] = _evaluate_waypoint_management(actions, navigation_state) * weight
        elif name == "route_planning":
            scores[name] = _evaluate_route_planning(actions, navigation_state) * weight
        elif name == "traffic_info":
            scores[name] = _evaluate_traffic_info(actions) * weight
        elif name == "ev_planning":
            scores[name] = _evaluate_ev_planning(actions) * weight
        elif name == "nav_control":
            scores[name] = _evaluate_nav_control(actions, navigation_state) * weight
        else:
            scores[name] = 0.5 * weight

    total_score = sum(scores.values())

    return {
        "overall_score": round(total_score, 4),
        "dimension_scores": {k: round(v, 4) for k, v in scores.items()},
        "total_actions": len(actions),
        "navigation_active": navigation_state.get("navigation_active", False),
    }


def _evaluate_poi_search(actions: list[dict[str, Any]]) -> float:
    poi_actions = [a for a in actions if a.get("action_type") == "search_poi"]
    if not poi_actions:
        return 0.0
    for action in poi_actions:
        result = action.get("result", {})
        if result.get("status") == "success" and result.get("data", {}).get("pois"):
            return 1.0
    return 0.5


def _evaluate_navigation_start(actions: list[dict[str, Any]], navigation_state: dict[str, Any]) -> float:
    start_actions = [a for a in actions if a.get("action_type") == "start_navigation"]
    if not start_actions:
        return 0.0
    if navigation_state.get("navigation_active") and navigation_state.get("destination"):
        return 1.0
    return 0.5


def _evaluate_waypoint_management(actions: list[dict[str, Any]], navigation_state: dict[str, Any]) -> float:
    waypoint_actions = [a for a in actions if a.get("action_type") in ("add_waypoint", "remove_waypoint")]
    if not waypoint_actions:
        return 0.0
    waypoints = navigation_state.get("waypoints", [])
    if any(w.get("arrived") for w in waypoints):
        return 1.0
    return 0.5


def _evaluate_route_planning(actions: list[dict[str, Any]], navigation_state: dict[str, Any]) -> float:
    route_actions = [a for a in actions if a.get("action_type") in ("route_preference", "reroute")]
    if not route_actions:
        return 0.0
    route = navigation_state.get("route", [])
    if route:
        return 1.0
    return 0.5


def _evaluate_traffic_info(actions: list[dict[str, Any]]) -> float:
    traffic_actions = [a for a in actions if a.get("action_type") in ("traffic_query", "traffic_status")]
    if not traffic_actions:
        return 0.0
    return 1.0


def _evaluate_ev_planning(actions: list[dict[str, Any]]) -> float:
    charging_actions = [a for a in actions if a.get("action_type") == "charging_plan"]
    if not charging_actions:
        return 0.0
    for action in charging_actions:
        result = action.get("result", {})
        if result.get("status") == "success":
            return 1.0
    return 0.5


def _evaluate_nav_control(actions: list[dict[str, Any]], navigation_state: dict[str, Any]) -> float:
    control_actions = [a for a in actions if a.get("action_type") in ("arrive_waypoint", "arrive_destination", "cancel_navigation")]
    if not control_actions:
        return 0.0
    if not navigation_state.get("navigation_active"):
        return 1.0
    return 0.5
