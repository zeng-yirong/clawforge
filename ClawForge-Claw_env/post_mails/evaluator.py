from __future__ import annotations

from typing import Any


def _lower_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _contains_all(text: str, snippets: list[str]) -> tuple[bool, list[str]]:
    missing = [snippet for snippet in snippets if snippet.lower() not in text]
    return len(missing) == 0, missing


def _count_forbidden_hits(text: str, forbidden_phrases: list[str]) -> list[str]:
    return [phrase for phrase in forbidden_phrases if phrase.lower() in text]


def _score_post_requirement(posts: list[dict[str, Any]], requirement: dict[str, Any], forbidden_phrases: list[str]) -> dict[str, Any]:
    candidate_posts = [post for post in posts if post["platform"] == requirement["platform"]]
    if requirement.get("community"):
        candidate_posts = [post for post in candidate_posts if post.get("community") == requirement["community"]]

    best_result = {
        "requirement_id": requirement["requirement_id"],
        "matched": False,
        "matched_post_id": None,
        "missing_terms": requirement.get("must_include", []),
        "missing_title_terms": requirement.get("title_must_include", []),
        "forbidden_hits": [],
        "score": 0.0,
    }

    for post in candidate_posts:
        body_text = _lower_text(post.get("content"))
        title_text = _lower_text(post.get("title"))
        include_ok, missing_terms = _contains_all(body_text, requirement.get("must_include", []))
        title_ok, missing_title_terms = _contains_all(title_text, requirement.get("title_must_include", []))
        forbidden_hits = _count_forbidden_hits(body_text, forbidden_phrases + requirement.get("must_not_include", []))
        length_ok = len(post.get("content", "")) >= requirement.get("min_length", 0)
        score_components = [include_ok, title_ok, length_ok, len(forbidden_hits) == 0]
        score = sum(1.0 for component in score_components if component) / len(score_components)
        if score > best_result["score"]:
            best_result = {
                "requirement_id": requirement["requirement_id"],
                "matched": include_ok and title_ok and length_ok and not forbidden_hits,
                "matched_post_id": post["post_id"],
                "missing_terms": missing_terms,
                "missing_title_terms": missing_title_terms,
                "forbidden_hits": forbidden_hits,
                "score": score,
            }
    return best_result


def _score_reply_requirement(
    replies: list[dict[str, Any]],
    requirement: dict[str, Any],
    forbidden_phrases: list[str],
) -> dict[str, Any]:
    candidate_replies = [
        reply
        for reply in replies
        if reply["platform"] == requirement["platform"] and reply["parent_post_id"] == requirement["target_post_id"]
    ]
    best_result = {
        "requirement_id": requirement["requirement_id"],
        "matched": False,
        "matched_reply_id": None,
        "missing_terms": requirement.get("must_include", []),
        "forbidden_hits": [],
        "score": 0.0,
    }

    for reply in candidate_replies:
        body_text = _lower_text(reply["content"])
        include_ok, missing_terms = _contains_all(body_text, requirement.get("must_include", []))
        forbidden_hits = _count_forbidden_hits(body_text, forbidden_phrases + requirement.get("must_not_include", []))
        length_ok = len(reply.get("content", "")) >= requirement.get("min_length", 0)
        score_components = [include_ok, length_ok, len(forbidden_hits) == 0]
        score = sum(1.0 for component in score_components if component) / len(score_components)
        if score > best_result["score"]:
            best_result = {
                "requirement_id": requirement["requirement_id"],
                "matched": include_ok and length_ok and not forbidden_hits,
                "matched_reply_id": reply["reply_id"],
                "missing_terms": missing_terms,
                "forbidden_hits": forbidden_hits,
                "score": score,
            }
    return best_result


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    required_attachment_ids = scenario.get("required_attachment_ids", [])
    read_attachment_ids = {
        attachment["attachment_id"]
        for email in session["mail"]["emails"]
        for attachment in email.get("attachments", [])
        if attachment.get("read")
    }
    read_score = (
        sum(1 for attachment_id in required_attachment_ids if attachment_id in read_attachment_ids) / len(required_attachment_ids)
        if required_attachment_ids
        else 1.0
    )

    agent_posts = session["social"]["agent_posts"]
    agent_replies = session["social"]["agent_replies"]
    forbidden_phrases = scenario.get("forbidden_phrases", [])

    post_results = [
        _score_post_requirement(agent_posts, requirement, forbidden_phrases)
        for requirement in scenario.get("required_posts", [])
    ]
    reply_results = [
        _score_reply_requirement(agent_replies, requirement, forbidden_phrases)
        for requirement in scenario.get("required_replies", [])
    ]

    avg_post_score = sum(item["score"] for item in post_results) / len(post_results) if post_results else 1.0
    avg_reply_score = sum(item["score"] for item in reply_results) / len(reply_results) if reply_results else 1.0

    actions = session.get("actions", [])
    first_publish_or_reply = next(
        (action["action_index"] for action in actions if action["action_type"] in {"publish_post", "reply_to_post"}),
        None,
    )
    first_required_read = next(
        (
            action["action_index"]
            for action in actions
            if action["action_type"] == "read_attachment"
            and action["details"].get("attachment_id") in required_attachment_ids
        ),
        None,
    )
    order_ok = first_publish_or_reply is None or (
        first_required_read is not None and first_required_read < first_publish_or_reply
    )

    forbidden_hits_total = []
    for post in agent_posts:
        forbidden_hits_total.extend(_count_forbidden_hits(_lower_text(post["content"]), forbidden_phrases))
    for reply in agent_replies:
        forbidden_hits_total.extend(_count_forbidden_hits(_lower_text(reply["content"]), forbidden_phrases))

    weighted_score = (
        (0.30 * read_score)
        + (0.35 * avg_post_score)
        + (0.25 * avg_reply_score)
        + (0.10 * (1.0 if order_ok else 0.0))
    )
    penalty = min(0.30, 0.10 * len(forbidden_hits_total))
    overall_score = max(0.0, min(1.0, weighted_score - penalty))

    return {
        "session_id": session["session_id"],
        "scenario_id": scenario["scenario_id"],
        "read_score": round(read_score, 4),
        "post_score": round(avg_post_score, 4),
        "reply_score": round(avg_reply_score, 4),
        "order_ok": order_ok,
        "forbidden_hits_total": forbidden_hits_total,
        "overall_score": round(overall_score, 4),
        "required_attachment_ids": required_attachment_ids,
        "read_attachment_ids": sorted(read_attachment_ids),
        "post_results": post_results,
        "reply_results": reply_results,
    }
