from __future__ import annotations

import sys

from .environment import PrivilegeExportGuardEnvironment
from without_skill._shared.security_guard_cli import run_security_cli


DEFAULT_SCENARIO_ID = "bulk_export_privilege_guard_q2_2026"


def main(argv: list[str] | None = None) -> int:
    return run_security_cli(
        argv=argv,
        env_class=PrivilegeExportGuardEnvironment,
        description="Privilege export guard training environment CLI.",
        session_env_var="PRIVILEGE_EXPORT_GUARD_SESSION_ID",
        state_root_env_var="PRIVILEGE_EXPORT_GUARD_STATE_ROOT",
        scenario_env_var="PRIVILEGE_EXPORT_GUARD_SCENARIO_ID",
        default_scenario_id=DEFAULT_SCENARIO_ID,
        session_prefix="export-guard",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
