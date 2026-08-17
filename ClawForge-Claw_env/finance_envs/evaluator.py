from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    required_actions = scenario.get("required_actions", [])
    completed_actions = {a["action_type"] for a in session.get("actions", [])}

    score = 0.0
    if required_actions:
        for req in required_actions:
            if req in completed_actions:
                score += 100.0 / len(required_actions)

    bonus_actions = {"update_brief", "submit_brief", "review_brief", "generate_sector_overview"}
    bonus_count = len(completed_actions & bonus_actions)
    score += bonus_count * 5

    return {
        "score": min(score, 100.0),
        "required_actions": len(required_actions),
        "completed_actions": len(completed_actions & set(required_actions)),
        "bonus_points": bonus_count * 5,
    }
