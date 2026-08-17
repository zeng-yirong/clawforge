"""
Workplace verifier for wp_server_fault_supabase_env__005.
Checks the agent's output files: ops/kill_target.json and ops/resolution.json.
"""

import sys
import json
import os
import csv
import re
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []
    total_score = 0

    def check(condition, item, score, max_score, reason=""):
        nonlocal total_score
        passed = bool(condition)
        if passed:
            total_score += score
        details.append({
            "item": item,
            "score": score if passed else 0,
            "max_score": max_score,
            "passed": passed,
            "reason": reason if not passed else ""
        })

    # --- 1. Check required input files exist (verifier doesn't strictly need them, but ensure env is correct) ---
    # We check them to give partial points for directory structure
    required_files = [
        "data/incidents/incident_pool.json",
        "data/attachments.json",
        "runbooks/manage_long_txns.md",
        "logs/active_transactions.csv"
    ]
    for fp in required_files:
        check(
            (ws / fp).exists(),
            f"Input file {fp} exists",
            2, 2
        )

    # --- 2. Check output files exist ---
    kill_target_path = ws / "ops" / "kill_target.json"
    resolution_path = ws / "ops" / "resolution.json"

    kill_exists = kill_target_path.exists()
    resolution_exists = resolution_path.exists()
    check(kill_exists, "ops/kill_target.json exists", 10, 10)
    check(resolution_exists, "ops/resolution.json exists", 10, 10)

    if not kill_exists and not resolution_exists:
        # Nothing to check further
        return write_score(details, total_score)

    # --- 3. Parse and validate JSON ---
    kill_data = None
    resolution_data = None
    if kill_exists:
        try:
            with open(kill_target_path) as f:
                kill_data = json.load(f)
            check(True, "kill_target.json is valid JSON", 5, 5)
        except (json.JSONDecodeError, Exception):
            check(False, "kill_target.json is valid JSON", 0, 5, "Invalid JSON")

    if resolution_exists:
        try:
            with open(resolution_path) as f:
                resolution_data = json.load(f)
            check(True, "resolution.json is valid JSON", 5, 5)
        except (json.JSONDecodeError, Exception):
            check(False, "resolution.json is valid JSON", 0, 5, "Invalid JSON")

    # --- 4. Content checks ---
    # Expected killed IDs (from CSV filter: duration>30 AND state=active)
    expected_killed_ids = {"txn-002", "txn-003", "txn-005", "txn-007"}

    # 4a. kill_target.json
    if isinstance(kill_data, dict):
        if "killed_ids" in kill_data:
            ids = kill_data["killed_ids"]
            if isinstance(ids, list):
                id_set = set(ids)
                if id_set == expected_killed_ids:
                    check(True, "kill_target.json killed_ids match expected set", 30, 30)
                else:
                    check(False, "kill_target.json killed_ids match expected set", 0, 30,
                           f"Expected {sorted(expected_killed_ids)}, got {sorted(id_set)}")
                # Check no extra keys
                extra_keys = set(kill_data.keys()) - {"killed_ids"}
                if extra_keys:
                    check(False, "kill_target.json has no extra keys", 0, 5,
                           f"Extra keys: {extra_keys}")
                else:
                    check(True, "kill_target.json has no extra keys", 5, 5)
            else:
                check(False, "kill_target.json killed_ids is a list", 0, 30, "killed_ids is not a list")
        else:
            check(False, "kill_target.json contains killed_ids key", 0, 30, "Missing key")
    elif isinstance(kill_data, list):
        # Allow plain list as alternative
        id_set = set(kill_data)
        if id_set == expected_killed_ids:
            check(True, "kill_target.json list matches expected set", 30, 30)
        else:
            check(False, "kill_target.json list matches expected set", 0, 30,
                   f"Expected {sorted(expected_killed_ids)}, got {sorted(id_set)}")
        # No extra keys check irrelevant for list
    elif kill_data is not None:
        check(False, "kill_target.json is a dict or list", 0, 30, "Unsupported structure")

    # 4b. resolution.json
    if isinstance(resolution_data, dict):
        required_res_keys = {"incident_id", "action", "killed_ids"}
        missing = required_res_keys - set(resolution_data.keys())
        if not missing:
            check(True, "resolution.json has all required keys", 5, 5)
            # Check incident_id
            if resolution_data["incident_id"] == "INC-003":
                check(True, "resolution.json incident_id is INC-003", 5, 5)
            else:
                check(False, "resolution.json incident_id is INC-003", 0, 5,
                       f"Got {resolution_data['incident_id']}")
            # Check action
            if resolution_data["action"] == "kill_long_transactions":
                check(True, "resolution.json action is kill_long_transactions", 5, 5)
            else:
                check(False, "resolution.json action is kill_long_transactions", 0, 5,
                       f"Got {resolution_data['action']}")
            # Check killed_ids consistency with kill_target
            res_ids = set(resolution_data["killed_ids"])
            if res_ids == expected_killed_ids:
                check(True, "resolution.json killed_ids match expected set", 15, 15)
            else:
                check(False, "resolution.json killed_ids match expected set", 0, 15,
                       f"Expected {sorted(expected_killed_ids)}, got {sorted(res_ids)}")
            # Check no extra keys
            extra = set(resolution_data.keys()) - required_res_keys
            if extra:
                check(False, "resolution.json has no extra keys", 0, 5, f"Extra keys: {extra}")
            else:
                check(True, "resolution.json has no extra keys", 5, 5)
        else:
            check(False, "resolution.json missing keys", 0, 30, f"Missing: {missing}")
    elif resolution_data is not None:
        check(False, "resolution.json is a dict", 0, 30, "Not a dict")

    return write_score(details, total_score)


def write_score(details, total_score):
    # Cap total at 100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    verify()
