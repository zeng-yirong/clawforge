from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .environment import ResumeInterviewSchedulerEnvironment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke concurrency test for resume_interview_scheduler_env.")
    parser.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)
    state_root = Path(tempfile.mkdtemp(prefix="resume_scheduler_")).resolve()
    try:
        env = ResumeInterviewSchedulerEnvironment(state_root=str(state_root))
        env.create_session("s1", "resume_scheduler_ml_platform_q2_2026", overwrite=True)
        env.create_session("s2", "resume_scheduler_ml_platform_q2_2026", overwrite=True)
        env.match_candidate("s1", "cand_ml_001", "job_ml_platform")
        env.schedule_interview("s1", "cand_ml_001", "job_ml_platform", "2026-06-25T10:00:00Z")
        report = {"s1_eval": env.evaluate_session("s1"), "s1_summary": env.session_summary("s1"), "s2_summary": env.session_summary("s2")}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    finally:
        if not args.keep_state:
            shutil.rmtree(state_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
