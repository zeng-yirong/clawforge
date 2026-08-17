import json
import os
import sys

def verify(workspace):
    score = 0
    details = []
    total_max = 100

    # ---------- 1. Check ops directory exists ----------
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score += 10
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "found ops/"})
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})
        # fail fast as remaining checks depend on it
        return dump_score(score, details, total_max)

    # ---------- 2. Check urgent_incidents.json exists ----------
    result_path = os.path.join(ops_dir, "urgent_incidents.json")
    if not os.path.isfile(result_path):
        score += 0
        details.append({"item": "urgent_incidents.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        return dump_score(score, details, total_max)
    else:
        try:
            with open(result_path, "r") as f:
                data = json.load(f)
            details.append({"item": "urgent_incidents.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found and valid JSON"})
            score += 10
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "urgent_incidents.json exists", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {str(e)[:80]}"})
            return dump_score(score, details, total_max)

    # ---------- 3. JSON structure: must be a list of dicts with incident_id and title ----------
    if not isinstance(data, list):
        details.append({"item": "JSON format: list of objects", "score": 0, "max_score": 10, "passed": False, "reason": "root is not a list"})
        score += 0
        return dump_score(score, details, total_max)
    if len(data) == 0:
        details.append({"item": "JSON format: list of objects", "score": 0, "max_score": 10, "passed": False, "reason": "list is empty"})
        return dump_score(score, details, total_max)
    for entry in data:
        if not isinstance(entry, dict):
            details.append({"item": "JSON format: list of objects", "score": 0, "max_score": 10, "passed": False, "reason": "entry is not a dict"})
            return dump_score(score, details, total_max)
        if "incident_id" not in entry or "title" not in entry:
            details.append({"item": "JSON format: list of objects", "score": 0, "max_score": 10, "passed": False, "reason": "missing incident_id or title in entry"})
            return dump_score(score, details, total_max)
    score += 10
    details.append({"item": "JSON format: list of objects", "score": 10, "max_score": 10, "passed": True, "reason": "valid list of dicts with required fields"})

    # ---------- 4. Read reference incident pool and compute ground truth ----------
    pool_path = os.path.join(workspace, "incidents", "incident_pool.json")
    if not os.path.isfile(pool_path):
        details.append({"item": "Ground truth match", "score": 0, "max_score": 70, "passed": False, "reason": "incident_pool.json not found for reference"})
        return dump_score(score, details, total_max)

    with open(pool_path) as f:
        pool_data = json.load(f)
    incidents = pool_data.get("incidents", [])

    # correct filter: category in ['ups_outage','service_down'], severity='critical', status='open'
    correct_entries = []
    for inc in incidents:
        if inc.get("category") in ("ups_outage", "service_down") and inc.get("severity") == "critical" and inc.get("status") == "open":
            correct_entries.append({"incident_id": inc["incident_id"], "title": inc["title"]})
    # sort by incident_id for deterministic comparison
    correct_entries.sort(key=lambda x: x["incident_id"])
    correct_ids = [e["incident_id"] for e in correct_entries]

    # compare agent result (sorted)
    agent_entries = sorted(data, key=lambda x: x["incident_id"])
    agent_ids = [e["incident_id"] for e in agent_entries]

    if correct_ids == agent_ids:
        score += 40
        details.append({"item": "Correct incident IDs selected", "score": 40, "max_score": 40, "passed": True, "reason": f"IDs match: {correct_ids}"})
    else:
        details.append({"item": "Correct incident IDs selected", "score": 0, "max_score": 40, "passed": False, "reason": f"expected {correct_ids}, got {agent_ids}"})

    # compare titles (order-insensitive after sorting)
    correct_titles = {e["incident_id"]: e["title"] for e in correct_entries}
    agent_titles = {e["incident_id"]: e["title"] for e in agent_entries}
    title_ok = True
    for cid, ctitle in correct_titles.items():
        if cid not in agent_titles or agent_titles[cid] != ctitle:
            title_ok = False
            break
    if title_ok and correct_ids == agent_ids:
        score += 20
        details.append({"item": "Correct titles for selected incidents", "score": 20, "max_score": 20, "passed": True, "reason": "all titles match"})
    else:
        details.append({"item": "Correct titles for selected incidents", "score": 0, "max_score": 20, "passed": False, "reason": "titles mismatch or IDs mismatch"})

    # finalize
    return dump_score(score, details, total_max)

def dump_score(score, details, max_score):
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/{max_score}")
    return score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
