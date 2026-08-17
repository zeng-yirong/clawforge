#!/usr/bin/env python3
"""
verify_workplace.py – Pure code verification for wp_server_fault_supabase_env__037.

Checks that the agent produced 'ops/remediation_plan.json' containing
exactly two entries (INC-001 and INC-003) with the correct actions
from the runbook.  Scoring is granular: directory existence, JSON validity,
correct length, required fields, and action exact match.
"""
import json
import os
import sys
from pathlib import Path

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path: str):
    p = Path(WORKSPACE) / rel_path
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def verify_workspace():
    details = []
    total_score = 0

    # --- 1. ops directory exists (10 pts) ---
    ops_dir = Path(WORKSPACE) / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found."
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing."
        })

    # --- 2. remediation_plan.json exists and is valid JSON (10 pts) ---
    plan_path = ops_dir / "remediation_plan.json"
    if not plan_path.is_file():
        details.append({
            "item": "remediation_plan.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # cannot continue without file
        write_score(details, total_score)
        return

    plan = load_json("ops/remediation_plan.json")
    if plan is None:
        details.append({
            "item": "valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Failed to parse JSON."
        })
        write_score(details, total_score)
        return

    details.append({
        "item": "valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File is valid JSON."
    })
    total_score += 10

    # --- 3. Must be a list (or wrap as list if top-level object) ---
    if isinstance(plan, list):
        entries = plan
    elif isinstance(plan, dict):
        # tolerate a wrapper like {"remediation": [...]}
        for val in plan.values():
            if isinstance(val, list):
                entries = val
                break
        else:
            entries = None
    else:
        entries = None

    if not isinstance(entries, list):
        details.append({
            "item": "remediation plan structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Top-level is not a list or a dict containing a list."
        })
        write_score(details, total_score)
        return

    details.append({
        "item": "remediation plan structure",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Top-level is a list."
    })
    total_score += 10

    # --- 4. Length check (20 pts) – we expect exactly 2 entries ---
    expected_ids = {"INC-001", "INC-003"}
    if len(entries) == 2:
        details.append({
            "item": "number of entries",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Exactly 2 entries present."
        })
        total_score += 20
    else:
        details.append({
            "item": "number of entries",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected 2 entries, got {len(entries)}."
        })
        # still continue to evaluate each entry for partial credit

    # --- 5. Each entry must have incident_id and action (20 pts) ---
    fields_score = 0
    fields_ok = True
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            reason = f"Entry {i}: not a dict."
            details.append({
                "item": f"Entry {i} structure",
                "score": 0,
                "max_score": 10 if i == 0 else 10,
                "passed": False,
                "reason": reason
            })
            fields_ok = False
            continue
        has_id = "incident_id" in entry
        has_action = "action" in entry
        if has_id and has_action:
            details.append({
                "item": f"Entry {i} fields (incident_id & action)",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Both fields present."
            })
            fields_score += 10
        else:
            missing = []
            if not has_id: missing.append("incident_id")
            if not has_action: missing.append("action")
            details.append({
                "item": f"Entry {i} fields (incident_id & action)",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Missing: {', '.join(missing)}."
            })
            fields_ok = False
    total_score += fields_score

    # --- 6. Action correctness per incident (40 pts total, 20 each) ---
    action_score = 0
    expected_actions = {
        "INC-001": "Activate backup generator and notify facilities team.",
        "INC-003": "Restart service on the affected host. Verify health after restart."
    }

    # Build lookup from entries
    entry_map = {}
    for e in entries:
        if isinstance(e, dict) and "incident_id" in e:
            entry_map[e["incident_id"]] = e.get("action", "")

    for inc_id, expected_action in expected_actions.items():
        if inc_id in entry_map:
            actual = entry_map[inc_id]
            if actual == expected_action:
                details.append({
                    "item": f"Action for {inc_id}",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": "Action matches exactly."
                })
                action_score += 20
            else:
                details.append({
                    "item": f"Action for {inc_id}",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"Expected '{expected_action}', got '{actual}'."
                })
        else:
            details.append({
                "item": f"Action for {inc_id}",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Incident ID not present in remediation plan."
            })
    total_score += action_score

    # --- Final ---
    write_score(details, total_score)

def write_score(details, total_score):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    score_path = Path(WORKSPACE) / "workplace_score.json"
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(score_data, f, indent=2)
    print(f"Verified. Total score: {total_score}/100")
    sys.exit(0 if total_score == 100 else 1)

if __name__ == "__main__":
    verify_workspace()
