import os, json, sys

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def check_workspace(workspace):
    total_score = 0
    details = []

    # Pre‑defined ground truth (based on env_builder data)
    expected_ids = {"req-001", "req-002", "req-005"}
    # map asset classification to item for quick lookup
    asset_class = {
        "ast-001": "highly_confidential",
        "ast-002": "confidential",
        "ast-003": "public"
    }
    external_roles = {"External Auditor", "Contractor", "Guest"}

    # ------------------------------------------------------------------
    # 1. Directory structure (10 pts) – ops/ must exist
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ directory found"})
        total_score += 10
    else:
        details.append({"item": "ops/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory missing"})

    # 2. Target file exists (10 pts)
    target_path = os.path.join(ops_dir, "deny_targets.json")
    if os.path.isfile(target_path):
        details.append({"item": "ops/deny_targets.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "ops/deny_targets.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # If file missing, further checks are impossible – return early
        final = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        sys.exit(0)

    # 3. JSON validity (10 pts)
    try:
        data = load_json(target_path)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        final = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        sys.exit(0)

    # 4. Is a list (10 pts)
    if isinstance(data, list):
        details.append({"item": "value is a list", "score": 10, "max_score": 10, "passed": True, "reason": "top-level element is list"})
        total_score += 10
    else:
        details.append({"item": "value is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"type is {type(data).__name__}"})
        final = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        sys.exit(0)

    # 5. All elements are strings (10 pts)
    all_strings = all(isinstance(x, str) for x in data)
    if all_strings and len(data) > 0:
        details.append({"item": "list elements are strings", "score": 10, "max_score": 10, "passed": True, "reason": f"all {len(data)} items are strings"})
        total_score += 10
    elif all_strings and len(data) == 0:
        details.append({"item": "list elements are strings", "score": 0, "max_score": 10, "passed": False, "reason": "list is empty"})
    else:
        details.append({"item": "list elements are strings", "score": 0, "max_score": 10, "passed": False, "reason": "some elements are not strings"})

    # 6. Exact match to ground truth (50 pts)
    agent_set = set(data)
    expected_set = expected_ids
    if agent_set == expected_set:
        details.append({"item": "exact set match", "score": 50, "max_score": 50, "passed": True, "reason": f"agent returned {sorted(agent_set)}"})
        total_score += 50
    else:
        missing = expected_set - agent_set
        extra = agent_set - expected_set
        reason_parts = []
        if missing:
            reason_parts.append(f"missing: {sorted(missing)}")
        if extra:
            reason_parts.append(f"extra: {sorted(extra)}")
        # Partial credit: perfect match gets full 50, otherwise proportional penalty
        # Simple approach: 0 for mismatch (strict)
        details.append({"item": "exact set match", "score": 0, "max_score": 50, "passed": False, "reason": "; ".join(reason_parts)})

    final = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    check_workspace(workspace)
