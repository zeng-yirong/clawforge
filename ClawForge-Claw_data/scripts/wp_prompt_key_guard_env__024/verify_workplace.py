import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # ---- 1. check directory existence ----
    audit_dir = os.path.join(workspace, "audit")
    if os.path.isdir(audit_dir):
        details.append({"item": "audit directory", "score": 10, "max_score": 10, "passed": True, "reason": "audit/ exists"})
        total += 10
    else:
        details.append({"item": "audit directory", "score": 0, "max_score": 10, "passed": False, "reason": "audit/ missing"})
        # no point checking further if dir missing
        _write_score(details, total)
        return

    # ---- 2. check blocked_requests.json exists ----
    result_path = os.path.join(audit_dir, "blocked_requests.json")
    if os.path.isfile(result_path):
        details.append({"item": "blocked_requests.json file", "score": 10, "max_score": 10, "passed": True, "reason": "file exists"})
        total += 10
    else:
        details.append({"item": "blocked_requests.json file", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        _write_score(details, total)
        return

    # ---- 3. JSON parse ----
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parse succeeded"})
        total += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse failed: {e}"})
        _write_score(details, total)
        return

    # ---- 4. check structure ----
    if isinstance(data, dict) and "blocked_ids" in data and isinstance(data["blocked_ids"], list):
        details.append({"item": "JSON structure", "score": 10, "max_score": 10, "passed": True, "reason": "contains blocked_ids list"})
        total += 10
    else:
        details.append({"item": "JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "missing blocked_ids or not a list"})
        _write_score(details, total)
        return

    # ---- 5. count of blocked IDs (must be exactly 2) ----
    blocked_ids = data["blocked_ids"]
    if len(blocked_ids) == 2:
        details.append({"item": "number of blocked IDs", "score": 20, "max_score": 20, "passed": True, "reason": f"got {len(blocked_ids)} IDs"})
        total += 20
    else:
        details.append({"item": "number of blocked IDs", "score": 0, "max_score": 20, "passed": False, "reason": f"expected 2, got {len(blocked_ids)}"})
        _write_score(details, total)
        return

    # ---- 6. exact IDs (req_001 and req_004) ----
    id_set = set(blocked_ids)
    expected = {"req_001", "req_004"}
    if id_set == expected:
        details.append({"item": "correct blocked IDs", "score": 40, "max_score": 40, "passed": True, "reason": "found req_001 and req_004"})
        total += 40
    else:
        missing = expected - id_set
        extra = id_set - expected
        reason_parts = []
        if missing:
            reason_parts.append(f"missing: {missing}")
        if extra:
            reason_parts.append(f"extra: {extra}")
        details.append({"item": "correct blocked IDs", "score": 0, "max_score": 40, "passed": False, "reason": "; ".join(reason_parts)})
        # partial credit? we give 0 for simplicity

    # ---- final ----
    _write_score(details, total)


def _write_score(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete: total_score = {total_score}")
    sys.exit(0 if total_score == 100 else 1)


if __name__ == "__main__":
    main()
