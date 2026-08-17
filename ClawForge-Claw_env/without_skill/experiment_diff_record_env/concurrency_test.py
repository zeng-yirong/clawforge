from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .environment import ExperimentDiffRecordEnvironment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke concurrency test for experiment_diff_record_env.")
    parser.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)
    state_root = Path(tempfile.mkdtemp(prefix="experiment_diff_")).resolve()
    try:
        env = ExperimentDiffRecordEnvironment(state_root=str(state_root))
        env.create_session("s1", "experiment_diff_record_q2_2026", overwrite=True)
        env.create_session("s2", "experiment_diff_record_q2_2026", overwrite=True)
        env.get_batch("s1", "batch_alpha")
        env.get_batch("s1", "batch_beta")
        env.generate_diff_record("s1", batch_ids=["batch_alpha", "batch_beta"])
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
