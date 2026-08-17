import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    details = []
    total_score = 0
    max_score = 100

    # 1. Check ops directory exists (5 points)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops directory found"})
        total_score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops directory not found"})

    # 2. Check current_timestamp.txt exists (5 points)
    ts_file = ops_dir / "current_timestamp.txt"
    if ts_file.is_file():
        details.append({"item": "current_timestamp.txt exists", "score": 5, "max_score": 5, "passed": True, "reason": "file found"})
        total_score += 5
    else:
        details.append({"item": "current_timestamp.txt exists", "score": 0, "max_score": 5, "passed": False, "reason": "file not found"})

    # 3. Check remediation_targets.json exists and is valid JSON (10 points)
    targets_file = ops_dir / "remediation_targets.json"
    targets = None
    if targets_file.is_file():
        try:
            with open(targets_file, "r") as f:
                targets = json.load(f)
            details.append({"item": "remediation_targets.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "file valid"})
            total_score += 10
        except json.JSONDecodeError:
            details.append({"item": "remediation_targets.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "invalid JSON"})
    else:
        details.append({"item": "remediation_targets.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})

    # 4. Check audit_trail.json exists and is valid JSON (10 points)
    audit_file = ops_dir / "audit_trail.json"
    audit = None
    if audit_file.is_file():
        try:
            with open(audit_file, "r") as f:
                audit = json.load(f)
            details.append({"item": "audit_trail.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "file valid"})
            total_score += 10
        except json.JSONDecodeError:
            details.append({"item": "audit_trail.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "invalid JSON"})
    else:
        details.append({"item": "audit_trail.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})

    # 5. Validate remediation_targets.json contents
    if targets is not None:
        # 5a. is list
        if isinstance(targets, list):
            details.append({"item": "remediation_targets is a list", "score": 5, "max_score": 5, "passed": True, "reason": "correct type"})
            total_score += 5
        else:
            details.append({"item": "remediation_targets is a list", "score": 0, "max_score": 5, "passed": False, "reason": f"expected list, got {type(targets).__name__}"})

        # 5b. length 2
        if len(targets) == 2:
            details.append({"item": "remediation_targets has 2 items", "score": 10, "max_score": 10, "passed": True, "reason": "correct count"})
            total_score += 10
        else:
            details.append({"item": "remediation_targets has 2 items", "score": 0, "max_score": 10, "passed": False, "reason": f"expected 2, got {len(targets)}"})

        # 5c. each item has required fields
        required_fields = ["incident_id", "title", "category", "severity", "status", "assigned_team", "service", "remediation_action"]
        field_score = 0
        field_max = 16  # 2 points per field per item, 2 items, total 2*8=16
        for idx, item in enumerate(targets):
            for field in required_fields:
                if field in item:
                    field_score += 1
        if field_score == len(required_fields) * len(targets):
            details.append({"item": "all required fields present in each target", "score": 16, "max_score": 16, "passed": True, "reason": f"all {len(required_fields)} fields present in both items"})
            total_score += 16
        else:
            details.append({"item": "all required fields present in each target", "score": field_score, "max_score": 16, "passed": False, "reason": f"only {field_score} out of {len(required_fields)*len(targets)} field presence checks passed"})

        # 5d. incident_id set equals expected
        expected_ids = {"INC-002", "INC-005"}
        actual_ids = {item.get("incident_id") for item in targets}
        if actual_ids == expected_ids:
            details.append({"item": "incident_ids match expected set", "score": 10, "max_score": 10, "passed": True, "reason": f"ids are {actual_ids}"})
            total_score += 10
        else:
            details.append({"item": "incident_ids match expected set", "score": 0, "max_score": 10, "passed": False, "reason": f"expected {expected_ids}, got {actual_ids}"})

        # 5e. remediation_action equals "initiate_ups_failover" for each
        action_ok = all(item.get("remediation_action") == "initiate_ups_failover" for item in targets)
        if action_ok:
            details.append({"item": "remediation_action is 'initiate_ups_failover'", "score": 5, "max_score": 5, "passed": True, "reason": "all actions correct"})
            total_score += 5
        else:
            details.append({"item": "remediation_action is 'initiate_ups_failover'", "score": 0, "max_score": 5, "passed": False, "reason": "some actions differ"})

        # 5f. category == "ups_outage" for each
        cat_ok = all(item.get("category") == "ups_outage" for item in targets)
        if cat_ok:
            details.append({"item": "category is 'ups_outage'", "score": 5, "max_score": 5, "passed": True, "reason": "all categories correct"})
            total_score += 5
        else:
            details.append({"item": "category is 'ups_outage'", "score": 0, "max_score": 5, "passed": False, "reason": "some categories differ"})

        # 5g. severity == "critical" for each
        sev_ok = all(item.get("severity") == "critical" for item in targets)
        if sev_ok:
            details.append({"item": "severity is 'critical'", "score": 5, "max_score": 5, "passed": True, "reason": "all severities correct"})
            total_score += 5
        else:
            details.append({"item": "severity is 'critical'", "score": 0, "max_score": 5, "passed": False, "reason": "some severities differ"})

        # 5h. status == "open" for each
        stat_ok = all(item.get("status") == "open" for item in targets)
        if stat_ok:
            details.append({"item": "status is 'open'", "score": 5, "max_score": 5, "passed": True, "reason": "all statuses correct"})
            total_score += 5
        else:
            details.append({"item": "status is 'open'", "score": 0, "max_score": 5, "passed": False, "reason": "some statuses differ"})

    # 6. Validate audit_trail.json contents
    if audit is not None:
        # 6a. is list
        if isinstance(audit, list):
            details.append({"item": "audit_trail is a list", "score": 5, "max_score": 5, "passed": True, "reason": "correct type"})
            total_score += 5
        else:
            details.append({"item": "audit_trail is a list", "score": 0, "max_score": 5, "passed": False, "reason": f"expected list, got {type(audit).__name__}"})

        # 6b. length 2
        if len(audit) == 2:
            details.append({"item": "audit_trail has 2 entries", "score": 10, "max_score": 10, "passed": True, "reason": "correct count"})
            total_score += 10
        else:
            details.append({"item": "audit_trail has 2 entries", "score": 0, "max_score": 10, "passed": False, "reason": f"expected 2, got {len(audit)}"})

        # 6c. each entry has required fields
        audit_fields = ["timestamp", "user", "action", "target"]
        audit_field_score = 0
        audit_field_max = 8  # 2 points per field per entry, 2 entries, total 8
        for idx, entry in enumerate(audit):
            for field in audit_fields:
                if field in entry:
                    audit_field_score += 1
        if audit_field_score == len(audit_fields) * len(audit):
            details.append({"item": "all required fields in each audit entry", "score": 8, "max_score": 8, "passed": True, "reason": "all fields present"})
            total_score += 8
        else:
            details.append({"item": "all required fields in each audit entry", "score": audit_field_score, "max_score": 8, "passed": False, "reason": f"only {audit_field_score} out of {len(audit_fields)*len(audit)} checks passed"})

        # 6d. user equals "nikhil.rao@northstar.example.com"
        user_ok = all(entry.get("user") == "nikhil.rao@northstar.example.com" for entry in audit)
        if user_ok:
            details.append({"item": "audit user is 'nikhil.rao@northstar.example.com'", "score": 5, "max_score": 5, "passed": True, "reason": "all users correct"})
            total_score += 5
        else:
            details.append({"item": "audit user is 'nikhil.rao@northstar.example.com'", "score": 0, "max_score": 5, "passed": False, "reason": "some users differ"})

        # 6e. action equals "remediate_and_write"
        action_ok = all(entry.get("action") == "remediate_and_write" for entry in audit)
        if action_ok:
            details.append({"item": "audit action is 'remediate_and_write'", "score": 5, "max_score": 5, "passed": True, "reason": "all actions correct"})
            total_score += 5
        else:
            details.append({"item": "audit action is 'remediate_and_write'", "score": 0, "max_score": 5, "passed": False, "reason": "some actions differ"})

        # 6f. target must match one of the incident_ids from remediation_targets (and cover both)
        if targets is not None and isinstance(targets, list):
            target_ids = {t.get("incident_id") for t in targets}
            audit_targets = {entry.get("target") for entry in audit}
            if target_ids == audit_targets:
                details.append({"item": "audit targets match remediation incident ids", "score": 5, "max_score": 5, "passed": True, "reason": f"targets {audit_targets} match"})
                total_score += 5
            else:
                details.append({"item": "audit targets match remediation incident ids", "score": 0, "max_score": 5, "passed": False, "reason": f"expected {target_ids}, got {audit_targets}"})
        else:
            details.append({"item": "audit targets match remediation incident ids", "score": 0, "max_score": 5, "passed": False, "reason": "remediation_targets not available"})

        # 6g. timestamp equals content of current_timestamp.txt
        if ts_file.is_file():
            with open(ts_file, "r") as f:
                expected_ts = f.read().strip()
            ts_ok = all(entry.get("timestamp") == expected_ts for entry in audit)
            if ts_ok:
                details.append({"item": "audit timestamps match current_timestamp.txt", "score": 5, "max_score": 5, "passed": True, "reason": "timestamps correct"})
                total_score += 5
            else:
                details.append({"item": "audit timestamps match current_timestamp.txt", "score": 0, "max_score": 5, "passed": False, "reason": "some timestamps differ from expected"})
        else:
            details.append({"item": "audit timestamps match current_timestamp.txt", "score": 0, "max_score": 5, "passed": False, "reason": "current_timestamp.txt missing"})

    # Cap score to 100
    total_score = min(total_score, 100)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
