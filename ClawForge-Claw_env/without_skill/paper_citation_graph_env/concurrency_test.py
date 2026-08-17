from __future__ import annotations

import sys

from without_skill._shared.cache_env_concurrency import run_cache_env_concurrency
from .environment import PaperCitationGraphEnvironment


SCENARIO_ID = "paper_citation_graph_snapshot_q2_2026"


def good_flow(env: PaperCitationGraphEnvironment, session_id: str) -> dict[str, object]:
    env.list_papers(session_id, direction="tool_augmented_reasoning")
    env.get_paper(session_id, "paper_tar_001")
    env.generate_citation_graph(session_id)
    return env.evaluate_session(session_id)


def contention_action(env: PaperCitationGraphEnvironment, session_id: str, _loop_idx: int) -> None:
    env.generate_citation_graph(session_id)


def main(argv: list[str] | None = None) -> int:
    return run_cache_env_concurrency(
        argv=argv,
        env_class=PaperCitationGraphEnvironment,
        scenario_id=SCENARIO_ID,
        flow=good_flow,
        contention_action=contention_action,
        description="Concurrent stress test for paper_citation_graph_env.",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
