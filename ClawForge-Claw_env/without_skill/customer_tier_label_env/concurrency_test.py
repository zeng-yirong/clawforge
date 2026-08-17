from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from .environment import CustomerTierLabelEnvironment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke concurrency test for customer_tier_label_env.")
    parser.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)
    state_root = Path(tempfile.mkdtemp(prefix="customer_tier_label_")).resolve()
    try:
        env = CustomerTierLabelEnvironment(state_root=str(state_root))
        env.create_session("s1", "customer_tier_labeling_q2_2026", overwrite=True)
        env.create_session("s2", "customer_tier_labeling_q2_2026", overwrite=True)
        env.read_attachment("s1", "segmentation_rules.md")
        env.get_customer_metrics("s1", "cust_fin_001")
        env.update_customer_labels("s1", "cust_fin_001")
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
