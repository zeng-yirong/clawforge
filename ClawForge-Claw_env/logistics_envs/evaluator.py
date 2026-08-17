from __future__ import annotations

from typing import Any


def _lower_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _contains_all(text: str, snippets: list[str]) -> tuple[bool, list[str]]:
    missing = [snippet for snippet in snippets if snippet.lower() not in text]
    return len(missing) == 0, missing


def _count_forbidden_hits(text: str, forbidden_phrases: list[str]) -> list[str]:
    return [phrase for phrase in forbidden_phrases if phrase.lower() in text]


def _score_action_requirement(actions: list[dict[str, Any]], requirement: dict[str, Any], forbidden_phrases: list[str]) -> dict[str, Any]:
    action_type = requirement["action_type"]
    target_key = requirement.get("target_key")
    target_value = requirement.get("target_value")
    must_include = requirement.get("must_include", [])
    must_not_include = requirement.get("must_not_include", [])

    matching_actions = []
    for action in actions:
        if action["action_type"] != action_type:
            continue
        if target_key and action.get("details", {}).get(target_key) != target_value:
            continue
        matching_actions.append(action)

    best_result = {
        "requirement_id": requirement["requirement_id"],
        "matched": False,
        "matched_action_index": None,
        "missing_terms": must_include[:],
        "forbidden_hits": [],
        "score": 0.0,
    }

    for action in matching_actions:
        details_text = _lower_text(str(action.get("details", {})))
        include_ok, missing_terms = _contains_all(details_text, must_include)
        forbidden_hits = _count_forbidden_hits(details_text, forbidden_phrases + must_not_include)
        score_components = [include_ok, len(forbidden_hits) == 0]
        score = sum(1.0 for component in score_components if component) / len(score_components)

        if score > best_result["score"]:
            best_result = {
                "requirement_id": requirement["requirement_id"],
                "matched": include_ok and not forbidden_hits,
                "matched_action_index": action.get("action_index"),
                "missing_terms": missing_terms,
                "forbidden_hits": forbidden_hits,
                "score": score,
            }

    return best_result


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    required_attachment_ids = scenario.get("required_attachment_ids", [])
    read_attachment_ids = set()

    actions = session.get("actions", [])
    forbidden_phrases = scenario.get("forbidden_phrases", [])
    required_actions = scenario.get("required_actions", [])

    action_results = [
        _score_action_requirement(actions, requirement, forbidden_phrases)
        for requirement in required_actions
    ]

    avg_action_score = sum(item["score"] for item in action_results) / len(action_results) if action_results else 1.0

    action_types_performed = set(action["action_type"] for action in actions)
    all_action_types_required = set(req["action_type"] for req in required_actions)
    coverage = len(action_types_performed & all_action_types_required) / len(all_action_types_required) if all_action_types_required else 1.0

    forbidden_hits_total = []
    for action in actions:
        details_text = _lower_text(str(action.get("details", {})))
        forbidden_hits_total.extend(_count_forbidden_hits(details_text, forbidden_phrases))

    read_score = 1.0
    action_score_component = avg_action_score * 0.7 + coverage * 0.3

    weighted_score = 0.40 * read_score + 0.60 * action_score_component
    penalty = min(0.30, 0.10 * len(forbidden_hits_total))
    overall_score = max(0.0, min(1.0, weighted_score - penalty))

    return {
        "session_id": session["session_id"],
        "scenario_id": scenario["scenario_id"],
        "read_score": round(read_score, 4),
        "action_score": round(avg_action_score, 4),
        "coverage_score": round(coverage, 4),
        "forbidden_hits_total": forbidden_hits_total,
        "overall_score": round(overall_score, 4),
        "required_attachment_ids": required_attachment_ids,
        "action_results": action_results,
    }
