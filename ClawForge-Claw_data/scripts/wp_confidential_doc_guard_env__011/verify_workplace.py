import os
import sys
import json
import csv  # not used but allowed

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    max_total = 100

    # 1. Check that ops/deny_targets.json exists (10 pts)
    target_path = os.path.join(workspace, "ops", "deny_targets.json")
    item = {"item": "ops/deny_targets.json exists", "max_score": 10}
    if os.path.isfile(target_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "File found."
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "File not found."
        score_details.append(item)
        # can't proceed, write partial score
        write_score(workspace, 0 if not item["passed"] else 10, score_details, max_total)
        return
    score_details.append(item)

    # 2. Parse JSON and check valid format (10 pts)
    item2 = {"item": "JSON is valid", "max_score": 10}
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        item2["score"] = 10
        item2["passed"] = True
        item2["reason"] = "Valid JSON."
    except Exception as e:
        item2["score"] = 0
        item2["passed"] = False
        item2["reason"] = f"JSON parse error: {e}"
        score_details.append(item2)
        write_score(workspace, sum(d["score"] for d in score_details), score_details, max_total)
        return
    score_details.append(item2)

    # 3. Check that it contains a list under key 'deny_ids' (or just a list? We'll be flexible: must be a dict with 'deny_ids' key containing list) (10 pts)
    item3 = {"item": "Structure contains 'deny_ids' list", "max_score": 10}
    if isinstance(data, dict) and "deny_ids" in data and isinstance(data["deny_ids"], list):
        item3["score"] = 10
        item3["passed"] = True
        item3["reason"] = "Found deny_ids list."
    else:
        item3["score"] = 0
        item3["passed"] = False
        item3["reason"] = f"Expected dict with 'deny_ids' list, got {type(data).__name__}."
        score_details.append(item3)
        write_score(workspace, sum(d["score"] for d in score_details), score_details, max_total)
        return
    score_details.append(item3)

    # 4. Compute ground truth answer from the initial env files (70 pts)
    # Re-read the asset and request files from the env (workspace)
    assets_path = os.path.join(workspace, "assets", "assets.json")
    requests_path = os.path.join(workspace, "requests", "requests.json")
    expected_deny_ids = set()
    try:
        with open(assets_path) as f:
            assets_data = json.load(f)
        assets_map = {a["asset_id"]: a for a in assets_data.get("assets", [])}
        with open(requests_path) as f:
            reqs_data = json.load(f)
        for req in reqs_data.get("requests", []):
            if req["status"] != "pending":
                continue
            target_id = req["target_asset_id"]
            if target_id in assets_map:
                asset = assets_map[target_id]
                if (asset["asset_type"] in ("technical_plan", "finance_archive") and
                        asset["classification"] == "confidential"):
                    expected_deny_ids.add(req["request_id"])
    except Exception as e:
        item4 = {"item": "Correct deny_ids content", "max_score": 70, "score": 0, "passed": False,
                 "reason": f"Error reading initial files: {e}"}
        score_details.append(item4)
        write_score(workspace, sum(d["score"] for d in score_details), score_details, max_total)
        return

    agent_ids = set(data["deny_ids"])
    # We expect exactly req-101, req-102, req-108 (ast-001 twice? req-101 and req-108 target ast-001; req-102 target ast-002)
    expected = {"req-101", "req-102", "req-108"}
    # Check for extra/missing
    extra = agent_ids - expected
    missing = expected - agent_ids
    correct = agent_ids == expected
    if correct:
        item4 = {"item": "Correct deny_ids content", "max_score": 70, "score": 70, "passed": True,
                 "reason": "Exactly matches expected: req-101, req-102, req-108"}
    else:
        reasons = []
        penalty = 0
        if missing:
            penalty += 15 * len(missing)
            reasons.append(f"Missing: {','.join(sorted(missing))}")
        if extra:
            penalty += 15 * len(extra)
            reasons.append(f"Extra: {','.join(sorted(extra))}")
        score = max(0, 70 - penalty)
        item4 = {"item": "Correct deny_ids content", "max_score": 70, "score": score, "passed": False,
                 "reason": "; ".join(reasons) if reasons else "No match"}
    score_details.append(item4)

    total_score = sum(d["score"] for d in score_details)
    write_score(workspace, total_score, score_details, max_total)

def write_score(workspace, score, details, max_total):
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
