from __future__ import annotations

import sys

from without_skill._shared.cache_env_concurrency import run_cache_env_concurrency
from .environment import ArxivReviewRoadmapEnvironment


SCENARIO_ID = "arxiv_review_tool_reasoning_q2_2026"


def good_flow(env: ArxivReviewRoadmapEnvironment, session_id: str) -> dict[str, object]:
    env.list_papers(session_id, direction="tool_augmented_reasoning")
    env.get_paper(session_id, "paper_tar_001")
    env.read_attachment(session_id, "review_style_guide.md")
    env.generate_review(session_id, direction="tool_augmented_reasoning")
    return env.evaluate_session(session_id)


def contention_action(env: ArxivReviewRoadmapEnvironment, session_id: str, _loop_idx: int) -> None:
    env.generate_review(session_id, direction="tool_augmented_reasoning")


def main(argv: list[str] | None = None) -> int:
    return run_cache_env_concurrency(
        argv=argv,
        env_class=ArxivReviewRoadmapEnvironment,
        scenario_id=SCENARIO_ID,
        flow=good_flow,
        contention_action=contention_action,
        description="Concurrent stress test for arxiv_review_roadmap_env.",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
