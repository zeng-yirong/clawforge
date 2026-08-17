from __future__ import annotations

import sys

from .environment import PrivilegeExportGuardEnvironment
from without_skill._shared.security_guard_concurrency import run_security_concurrency


SCENARIO_ID = "bulk_export_privilege_guard_q2_2026"
TARGET_REQUEST_ID = "req_export_001"
REASON_CODE = "unauthorized_bulk_export_block"


def good_flow(env: PrivilegeExportGuardEnvironment, session_id: str) -> dict[str, object]:
    env.list_requests(session_id, request_type="bulk_export")
    env.get_request(session_id, TARGET_REQUEST_ID)
    env.list_assets(session_id)
    env.read_attachment(session_id, "bulk_export_policy.md")
    env.deny_request(session_id, TARGET_REQUEST_ID, reason_code=REASON_CODE, comment="Insufficient export privileges.")
    return env.evaluate_session(session_id)


def main(argv: list[str] | None = None) -> int:
    return run_security_concurrency(
        argv=argv,
        env_class=PrivilegeExportGuardEnvironment,
        scenario_id=SCENARIO_ID,
        flow=good_flow,
        contention_request_id=TARGET_REQUEST_ID,
        contention_reason_code=REASON_CODE,
        description="Concurrent stress test for privilege_export_guard_env.",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
