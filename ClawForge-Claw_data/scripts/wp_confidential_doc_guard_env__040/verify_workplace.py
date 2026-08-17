import sys
import json
import os

def verify(workspace):
    results = []
    total_score = 0

    # 1. Check that ops/deny_list.json exists
    deny_path = os.path.join(workspace, "ops/deny_list.json")
    item = {"item": "ops/deny_list.json exists", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.isfile(deny_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "File found."
    else:
        item["reason"] = "File not found."
        results.append(item)
        total_score += item["score"]
        # cannot proceed without the file
        final = {"total_score": total_score, "details": results}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    results.append(item)
    total_score += item["score"]

    # 2. Validate JSON format and structure
    item2 = {"item": "deny_list.json is valid JSON with a top-level array", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            item2["score"] = 10
            item2["passed"] = True
            item2["reason"] = f"Valid array with {len(data)} elements."
        else:
            item2["reason"] = "Top-level element is not a list."
    except Exception as e:
        item2["reason"] = f"JSON parse error: {e}"
    results.append(item2)
    total_score += item2["score"]

    # 3. Load requests and assets to compute ground truth
    item3 = {"item": "Deny list matches expected request IDs (sorted, exact match)", "max_score": 80, "score": 0, "passed": False, "reason": ""}
    try:
        req_path = os.path.join(workspace, "data/requests/requests.json")
        with open(req_path, "r") as f:
            req_data = json.load(f)["requests"]
        asset_path = os.path.join(workspace, "data/assets/assets.json")
        with open(asset_path, "r") as f:
            asset_data = json.load(f)["assets"]

        # Build lookup for assets by id
        asset_lookup = {a["asset_id"]: a for a in asset_data}

        # Determine ground truth: risk_type == "unauthorized_access" and target asset classification == "unpublished"
        ground_truth = set()
        for r in req_data:
            target = asset_lookup.get(r["target_asset_id"])
            if target and r["risk_type"] == "unauthorized_access" and target["classification"] == "unpublished":
                ground_truth.add(r["request_id"])

        # Expected sorted list
        expected = sorted(list(ground_truth))

        # Agent's list, sorted
        agent_list = data  # already a list
        if not isinstance(agent_list, list):
            raise ValueError("Agent output is not a list")
        agent_sorted = sorted([str(x) for x in agent_list])  # ensure strings

        if agent_sorted == expected:
            item3["score"] = 80
            item3["passed"] = True
            item3["reason"] = f"Exact match: {expected}"
        else:
            item3["reason"] = f"Expected {expected}, got {agent_sorted}"
            # Partial credit: each correct ID
            correct = set(agent_sorted) & ground_truth
            wrong = set(agent_sorted) - ground_truth
            missing = ground_truth - set(agent_sorted)
            if len(correct) > 0 and len(wrong) == 0 and len(missing) == 0:
                # shouldn't happen, but fallback
                pass
            # Score proportionally: each correct ID gives (80 / len(expected)) points
            if len(expected) > 0:
                partial = int(80 * len(correct) / len(expected))
                item3["score"] = partial
                item3["reason"] = f"Partial: {len(correct)}/{len(expected)} correct, wrong={len(wrong)}, missing={len(missing)}"
            else:
                item3["score"] = 0
    except Exception as e:
        item3["reason"] = f"Error computing ground truth: {e}"
    results.append(item3)
    total_score += item3["score"]

    # Clamp total to 0-100
    total_score = max(0, min(100, total_score))
    final = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
