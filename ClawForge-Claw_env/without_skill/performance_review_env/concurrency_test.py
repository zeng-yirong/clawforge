from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .environment import PerformanceReviewEnvironment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke concurrency test for performance_review_env.")
    parser.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)
    state_root = Path(tempfile.mkdtemp(prefix="performance_review_")).resolve()
    try:
        env = PerformanceReviewEnvironment(state_root=str(state_root))
        env.create_session("s1", "performance_review_engineering_q2_2026", overwrite=True)
        env.create_session("s2", "performance_review_engineering_q2_2026", overwrite=True)
        env.get_output_ledger("s1", "emp_eng_001")
        env.get_scoring_rule("s1", "software_engineer")
        env.generate_performance_profile("s1", "emp_eng_001")
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
