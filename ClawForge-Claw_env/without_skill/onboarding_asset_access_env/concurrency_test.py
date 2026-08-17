from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .environment import OnboardingAssetAccessEnvironment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke concurrency test for onboarding_asset_access_env.")
    parser.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)
    state_root = Path(tempfile.mkdtemp(prefix="onboarding_asset_access_")).resolve()
    try:
        env = OnboardingAssetAccessEnvironment(state_root=str(state_root))
        env.create_session("s1", "onboarding_asset_access_q2_2026", overwrite=True)
        env.create_session("s2", "onboarding_asset_access_q2_2026", overwrite=True)
        env.get_contract("s1", "emp_new_001")
        env.create_email_profile("s1", "emp_new_001")
        env.assign_system_access("s1", "emp_new_001", "pack_engineering_standard")
        env.allocate_equipment("s1", "emp_new_001", "LT-3001")
        env.post_welcome_message("s1", "emp_new_001")
        report = {"s1_eval": env.evaluate_session("s1"), "s1_summary": env.session_summary("s1"), "s2_summary": env.session_summary("s2")}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    finally:
        if not args.keep_state:
            shutil.rmtree(state_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
