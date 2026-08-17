from __future__ import annotations

import sys

from without_skill._shared.cache_env_concurrency import run_cache_env_concurrency
from .environment import ChurnRetentionMailEnvironment


SCENARIO_ID = "churn_retention_mail_fintech_q2_2026"


def good_flow(env: ChurnRetentionMailEnvironment, session_id: str) -> dict[str, object]:
    env.list_customers(session_id, risk_level="high")
    env.get_customer(session_id, "cust_fin_001")
    env.list_news_samples(session_id, industry="fintech")
    env.generate_retention_email(session_id, "cust_fin_001")
    return env.evaluate_session(session_id)


def contention_action(env: ChurnRetentionMailEnvironment, session_id: str, _loop_idx: int) -> None:
    env.generate_retention_email(session_id, "cust_fin_001")


def main(argv: list[str] | None = None) -> int:
    return run_cache_env_concurrency(
        argv=argv,
        env_class=ChurnRetentionMailEnvironment,
        scenario_id=SCENARIO_ID,
        flow=good_flow,
        contention_action=contention_action,
        description="Concurrent stress test for churn_retention_mail_env.",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
