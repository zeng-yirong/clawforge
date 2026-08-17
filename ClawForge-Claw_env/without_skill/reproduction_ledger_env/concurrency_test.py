from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .environment import ReproductionLedgerEnvironment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke concurrency test for reproduction_ledger_env.")
    parser.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)
    state_root = Path(tempfile.mkdtemp(prefix="reproduction_ledger_")).resolve()
    try:
        env = ReproductionLedgerEnvironment(state_root=str(state_root))
        env.create_session("s1", "reproduction_ledger_langgraph_q2_2026", overwrite=True)
        env.create_session("s2", "reproduction_ledger_langgraph_q2_2026", overwrite=True)
        env.get_project_doc("s1", "doc_langgraph_readme")
        env.archive_reproduction_ledger("s1", project_id="proj_langgraph_sim", steps="1. docker compose up 2. run pytest", result="Graph execution reproduced with passing smoke tests.")
        report = {"s1_eval": env.evaluate_session("s1"), "s1_summary": env.session_summary("s1"), "s2_summary": env.session_summary("s2")}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    finally:
        if not args.keep_state:
            shutil.rmtree(state_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
