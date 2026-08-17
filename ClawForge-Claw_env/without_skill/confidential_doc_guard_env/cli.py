from __future__ import annotations

import sys

from .environment import ConfidentialDocGuardEnvironment
from without_skill._shared.security_guard_cli import run_security_cli


DEFAULT_SCENARIO_ID = "confidential_doc_leak_prevention_q2_2026"


def main(argv: list[str] | None = None) -> int:
    return run_security_cli(
        argv=argv,
        env_class=ConfidentialDocGuardEnvironment,
        description="Confidential document leak prevention training environment CLI.",
        session_env_var="CONFIDENTIAL_DOC_GUARD_SESSION_ID",
        state_root_env_var="CONFIDENTIAL_DOC_GUARD_STATE_ROOT",
        scenario_env_var="CONFIDENTIAL_DOC_GUARD_SCENARIO_ID",
        default_scenario_id=DEFAULT_SCENARIO_ID,
        session_prefix="confdoc-guard",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
