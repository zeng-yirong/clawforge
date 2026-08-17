from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    scoring_rules = scenario.get("scoring_rules", {})
    dimensions = scoring_rules.get("dimensions", [])

    actions = session.get("actions", [])
    vehicle_state = session.get("vehicle_state", {})

    scores: dict[str, float] = {}
    total_weight = sum(d.get("weight", 0) for d in dimensions)

    for dim in dimensions:
        name = dim.get("dimension", dim.get("name", ""))
        weight = dim.get("weight", 0)
        if name == "climate_control":
            scores[name] = _evaluate_climate_control(actions, vehicle_state) * weight
        elif name == "seat_control":
            scores[name] = _evaluate_seat_control(actions, vehicle_state) * weight
        elif name == "window_control":
            scores[name] = _evaluate_window_control(actions, vehicle_state) * weight
        elif name == "light_control":
            scores[name] = _evaluate_light_control(actions, vehicle_state) * weight
        elif name == "driving_mode":
            scores[name] = _evaluate_driving_mode(actions, vehicle_state) * weight
        elif name == "status_query":
            scores[name] = _evaluate_status_query(actions) * weight
        elif name == "multimedia":
            scores[name] = _evaluate_multimedia(actions, vehicle_state) * weight
        else:
            scores[name] = 0.5 * weight

    total_score = sum(scores.values())

    return {
        "overall_score": round(total_score, 4),
        "dimension_scores": {k: round(v, 4) for k, v in scores.items()},
        "total_actions": len(actions),
        "driving_mode": vehicle_state.get("driving_mode"),
    }


def _evaluate_climate_control(actions: list[dict[str, Any]], vehicle_state: dict[str, Any]) -> float:
    ac_actions = [a for a in actions if a.get("action_type", "").startswith("ac_")]
    if not ac_actions:
        return 0.0
    ac_state = vehicle_state.get("ac", {})
    if ac_state.get("power"):
        return 1.0
    return 0.5


def _evaluate_seat_control(actions: list[dict[str, Any]], vehicle_state: dict[str, Any]) -> float:
    seat_actions = [a for a in actions if a.get("action_type", "").startswith("seat_")]
    if not seat_actions:
        return 0.0
    return 1.0


def _evaluate_window_control(actions: list[dict[str, Any]], vehicle_state: dict[str, Any]) -> float:
    window_actions = [a for a in actions if a.get("action_type", "").startswith("window_")]
    if not window_actions:
        return 0.0
    return 1.0


def _evaluate_light_control(actions: list[dict[str, Any]], vehicle_state: dict[str, Any]) -> float:
    light_actions = [a for a in actions if a.get("action_type", "").startswith(("ambient_", "reading_", "fog_", "light_"))]
    if not light_actions:
        return 0.0
    return 1.0


def _evaluate_driving_mode(actions: list[dict[str, Any]], vehicle_state: dict[str, Any]) -> float:
    mode_actions = [a for a in actions if a.get("action_type") == "driving_mode"]
    if mode_actions:
        return 1.0
    return 0.0


def _evaluate_status_query(actions: list[dict[str, Any]]) -> float:
    status_actions = [a for a in actions if a.get("action_type") == "status_query"]
    if status_actions:
        return 1.0
    return 0.0


def _evaluate_multimedia(actions: list[dict[str, Any]], vehicle_state: dict[str, Any]) -> float:
    media_actions = [a for a in actions if a.get("action_type", "").startswith(("media_", "volume_"))]
    if not media_actions:
        return 0.0
    return 1.0
