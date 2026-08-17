from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .environment import OffboardingRecoveryEnvironment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke concurrency test for offboarding_recovery_env.")
    parser.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)
    state_root = Path(tempfile.mkdtemp(prefix="offboarding_recovery_")).resolve()
    try:
        env = OffboardingRecoveryEnvironment(state_root=str(state_root))
        env.create_session("s1", "offboarding_recovery_q2_2026", overwrite=True)
        env.create_session("s2", "offboarding_recovery_q2_2026", overwrite=True)
        env.get_exit_request("s1", "emp_ops_001")
        env.revoke_system_access("s1", "emp_ops_001")
        env.reclaim_equipment("s1", "emp_ops_001")
        env.generate_handover_checklist("s1", "emp_ops_001")
        report = {
            "s1_eval": env.evaluate_session("s1"),
            "s1_summary": env.session_summary("s1"),
            "s2_summary": env.session_summary("s2"),
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    finally:
        if not args.keep_state:
            shutil.rmtree(state_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
