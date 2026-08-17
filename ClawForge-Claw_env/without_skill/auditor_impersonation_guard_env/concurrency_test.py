from __future__ import annotations

import sys

from .environment import AuditorImpersonationGuardEnvironment
from without_skill._shared.security_guard_concurrency import run_security_concurrency


SCENARIO_ID = "auditor_impersonation_access_q2_2026"
TARGET_REQUEST_ID = "req_audit_001"
REASON_CODE = "identity_fraud_block"


def good_flow(env: AuditorImpersonationGuardEnvironment, session_id: str) -> dict[str, object]:
    env.list_requests(session_id, risk_level="high")
    env.get_request(session_id, TARGET_REQUEST_ID)
    env.list_assets(session_id, classification="restricted")
    env.read_attachment(session_id, "identity_verification_policy.md")
    env.deny_request(session_id, TARGET_REQUEST_ID, reason_code=REASON_CODE, comment="Failed auditor identity verification.")
    return env.evaluate_session(session_id)


def main(argv: list[str] | None = None) -> int:
    return run_security_concurrency(
        argv=argv,
        env_class=AuditorImpersonationGuardEnvironment,
        scenario_id=SCENARIO_ID,
        flow=good_flow,
        contention_request_id=TARGET_REQUEST_ID,
        contention_reason_code=REASON_CODE,
        description="Concurrent stress test for auditor_impersonation_guard_env.",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
