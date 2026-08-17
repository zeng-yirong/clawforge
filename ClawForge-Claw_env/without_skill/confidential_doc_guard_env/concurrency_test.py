from __future__ import annotations

import sys

from .environment import ConfidentialDocGuardEnvironment
from without_skill._shared.security_guard_concurrency import run_security_concurrency


SCENARIO_ID = "confidential_doc_leak_prevention_q2_2026"
TARGET_REQUEST_ID = "req_confdoc_001"
REASON_CODE = "confidential_doc_leak_block"


def good_flow(env: ConfidentialDocGuardEnvironment, session_id: str) -> dict[str, object]:
    env.list_requests(session_id, risk_level="high")
    env.get_request(session_id, TARGET_REQUEST_ID)
    env.list_assets(session_id, classification="high_confidential")
    env.read_attachment(session_id, "external_disclosure_policy.md")
    env.deny_request(session_id, TARGET_REQUEST_ID, reason_code=REASON_CODE, comment="External disclosure not allowed.")
    return env.evaluate_session(session_id)


def main(argv: list[str] | None = None) -> int:
    return run_security_concurrency(
        argv=argv,
        env_class=ConfidentialDocGuardEnvironment,
        scenario_id=SCENARIO_ID,
        flow=good_flow,
        contention_request_id=TARGET_REQUEST_ID,
        contention_reason_code=REASON_CODE,
        description="Concurrent stress test for confidential_doc_guard_env.",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
