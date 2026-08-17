from __future__ import annotations

import sys

from without_skill._shared.cache_env_concurrency import run_cache_env_concurrency
from .environment import BusinessMarkdownReportEnvironment


SCENARIO_ID = "business_markdown_report_weekly_q2_2026"


def good_flow(env: BusinessMarkdownReportEnvironment, session_id: str) -> dict[str, object]:
    env.list_ledgers(session_id)
    env.preview_ledger(session_id, "customer_ledger")
    env.preview_ledger(session_id, "product_ledger")
    env.preview_ledger(session_id, "ops_ledger")
    env.generate_markdown_report(session_id, "2026-W25")
    return env.evaluate_session(session_id)


def contention_action(env: BusinessMarkdownReportEnvironment, session_id: str, _loop_idx: int) -> None:
    env.generate_markdown_report(session_id, "2026-W25")


def main(argv: list[str] | None = None) -> int:
    return run_cache_env_concurrency(
        argv=argv,
        env_class=BusinessMarkdownReportEnvironment,
        scenario_id=SCENARIO_ID,
        flow=good_flow,
        contention_action=contention_action,
        description="Concurrent stress test for business_markdown_report_env.",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
