import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # Helper to read JSON file safely
    def read_json(rel_path):
        abs_path = os.path.join(workspace, rel_path)
        if not os.path.isfile(abs_path):
            return None
        try:
            with open(abs_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    # --- 1. ops directory existence (5 points) ---
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    points_dir = 5 if dir_exists else 0
    total_score += points_dir
    details.append({
        "item": "ops/ directory exists",
        "score": points_dir,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "Found" if dir_exists else "Directory ops/ not found"
    })

    # --- 2. ops/screened.json existence and content (20 + 5 = 25 points) ---
    screened = read_json("ops/screened.json")
    screened_exists = screened is not None
    points_screened_exist = 5 if screened_exists else 0
    total_score += points_screened_exist
    details.append({
        "item": "ops/screened.json exists and is valid JSON",
        "score": points_screened_exist,
        "max_score": 5,
        "passed": screened_exists,
        "reason": "Valid JSON" if screened_exists else "Missing or invalid JSON"
    })

    # Content check
    expected_ids = {"INC-001", "INC-002"}
    screened_ok = False
    screened_reason = ""
    if screened_exists:
        if isinstance(screened, list) and all(isinstance(x, str) for x in screened):
            screened_set = set(screened)
            if screened_set == expected_ids:
                screened_ok = True
                screened_reason = "Contains exactly INC-001 and INC-002"
            else:
                screened_reason = f"Extra or missing IDs: {screened_set ^ expected_ids}"
        else:
            screened_reason = "Expected a list of strings"
    points_screened_content = 20 if screened_ok else 0
    total_score += points_screened_content
    details.append({
        "item": "ops/screened.json content correctness",
        "score": points_screened_content,
        "max_score": 20,
        "passed": screened_ok,
        "reason": screened_reason
    })

    # --- 3. ops/remediation.json existence and content (5 + 25 = 30 points) ---
    remediation = read_json("ops/remediation.json")
    remediation_exists = remediation is not None
    points_remediation_exist = 5 if remediation_exists else 0
    total_score += points_remediation_exist
    details.append({
        "item": "ops/remediation.json exists and is valid JSON",
        "score": points_remediation_exist,
        "max_score": 5,
        "passed": remediation_exists,
        "reason": "Valid JSON" if remediation_exists else "Missing or invalid JSON"
    })

    remediation_ok = False
    remediation_reason = ""
    if remediation_exists:
        if isinstance(remediation, dict):
            keys = set(remediation.keys())
            if keys == expected_ids:
                values_ok = all(
                    isinstance(v, dict) and v.get("action") == "remediated"
                    for v in remediation.values()
                )
                if values_ok:
                    remediation_ok = True
                    remediation_reason = "All entries have action=remediated"
                else:
                    remediation_reason = "Some entries missing 'action' field or value not 'remediated'"
            else:
                remediation_reason = f"Extra or missing keys: {keys ^ expected_ids}"
        else:
            remediation_reason = "Expected a dict (object)"
    points_remediation_content = 25 if remediation_ok else 0
    total_score += points_remediation_content
    details.append({
        "item": "ops/remediation.json content correctness",
        "score": points_remediation_content,
        "max_score": 25,
        "passed": remediation_ok,
        "reason": remediation_reason
    })

    # --- 4. ops/resolution.json existence and content (5 + 35 = 40 points) ---
    resolution = read_json("ops/resolution.json")
    resolution_exists = resolution is not None
    points_resolution_exist = 5 if resolution_exists else 0
    total_score += points_resolution_exist
    details.append({
        "item": "ops/resolution.json exists and is valid JSON",
        "score": points_resolution_exist,
        "max_score": 5,
        "passed": resolution_exists,
        "reason": "Valid JSON" if resolution_exists else "Missing or invalid JSON"
    })

    resolution_ok = False
    resolution_reason = ""
    if resolution_exists:
        if isinstance(resolution, list) and len(resolution) == 2:
            ids_in_resolution = {r.get("incident_id") for r in resolution if isinstance(r, dict)}
            statuses = {r.get("status") for r in resolution if isinstance(r, dict)}
            if ids_in_resolution == expected_ids and statuses == {"remediated"}:
                resolution_ok = True
                resolution_reason = "Contains both incidents with status 'remediated'"
            else:
                extra = ids_in_resolution ^ expected_ids
                resolution_reason = f"IDs mismatch {extra} or status not 'remediated' (got {statuses})"
        else:
            resolution_reason = "Expected a list of exactly 2 objects"
    points_resolution_content = 35 if resolution_ok else 0
    total_score += points_resolution_content
    details.append({
        "item": "ops/resolution.json content correctness",
        "score": points_resolution_content,
        "max_score": 35,
        "passed": resolution_ok,
        "reason": resolution_reason
    })

    # --- Write score file ---
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Total score: {total_score}/100")

if __name__ == "__main__":
    main()
