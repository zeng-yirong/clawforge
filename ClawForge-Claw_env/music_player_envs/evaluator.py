from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    scoring_rules = scenario.get("scoring_rules", {})
    dimensions = scoring_rules.get("dimensions", [])
    bonus_def = scoring_rules.get("bonus", {})

    actions = session.get("actions", [])
    player = session.get("player", {})

    scores: dict[str, float] = {}
    total_weight = sum(d.get("weight", 0) for d in dimensions)

    for dim in dimensions:
        name = dim["name"]
        weight = dim.get("weight", 0)
        if name == "playback_control":
            scores[name] = _evaluate_playback_control(actions, player) * weight
        elif name == "search_accuracy":
            scores[name] = _evaluate_search_accuracy(actions, player) * weight
        elif name == "status_query":
            scores[name] = _evaluate_status_query(actions) * weight
        elif name == "command_understanding":
            scores[name] = _evaluate_command_understanding(actions) * weight
        else:
            scores[name] = 0.5 * weight

    total_score = sum(scores.values())

    bonus = 0.0
    if bonus_def and len(actions) <= 5:
        bonus = bonus_def.get("max_bonus", 0.1)

    overall = min(1.0, total_score + bonus)

    return {
        "overall_score": round(overall, 4),
        "dimension_scores": {k: round(v, 4) for k, v in scores.items()},
        "bonus": round(bonus, 4),
        "total_actions": len(actions),
        "playback_status": player.get("status"),
        "current_song": player.get("current_song_id"),
    }


def _evaluate_playback_control(actions: list[dict[str, Any]], player: dict[str, Any]) -> float:
    playback_actions = {"play", "pause", "resume", "next", "previous", "seek", "set_mode", "switch_player"}
    relevant = [a for a in actions if a.get("action_type") in playback_actions]
    if not relevant:
        return 0.0
    has_play = any(a.get("action_type") == "play" for a in relevant)
    has_control = any(a.get("action_type") in {"pause", "resume", "next", "previous"} for a in relevant)
    if has_play and has_control:
        return 1.0
    elif has_play:
        return 0.7
    return 0.3


def _evaluate_search_accuracy(actions: list[dict[str, Any]], player: dict[str, Any]) -> float:
    search_actions = {"search", "list_songs"}
    relevant = [a for a in actions if a.get("action_type") in search_actions]
    if not relevant:
        return 0.0
    has_song_played = player.get("current_song_id") is not None
    if has_song_played:
        return 1.0
    return 0.5


def _evaluate_status_query(actions: list[dict[str, Any]]) -> float:
    status_actions = [a for a in actions if a.get("action_type") == "status"]
    if status_actions:
        return 1.0
    return 0.0


def _evaluate_command_understanding(actions: list[dict[str, Any]]) -> float:
    if not actions:
        return 0.0
    error_actions = [a for a in actions if a.get("result", {}).get("status") == "error"]
    error_rate = len(error_actions) / len(actions)
    return max(0.0, 1.0 - error_rate)
