from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .environment import FaultPostmortemKbEnvironment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke concurrency test for fault_postmortem_kb_env.")
    parser.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)
    state_root = Path(tempfile.mkdtemp(prefix="fault_postmortem_")).resolve()
    try:
        env = FaultPostmortemKbEnvironment(state_root=str(state_root))
        env.create_session("s1", "fault_postmortem_checkout_q2_2026", overwrite=True)
        env.create_session("s2", "fault_postmortem_checkout_q2_2026", overwrite=True)
        env.get_fault_case("s1", "fault_checkout_001")
        env.read_attachment("s1", "postmortem_template.md")
        env.generate_postmortem("s1", "fault_checkout_001")
        report = {"s1_eval": env.evaluate_session("s1"), "s1_summary": env.session_summary("s1"), "s2_summary": env.session_summary("s2")}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    finally:
        if not args.keep_state:
            shutil.rmtree(state_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
