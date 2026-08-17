import sys
import os
import json
import math

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. Directory structure (10 points)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        details.append({"item": "reports/ directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found reports/ directory."})
        total_score += 5
    else:
        details.append({"item": "reports/ directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing reports/ directory."})

    report_path = os.path.join(reports_dir, "monthly_cost_2026_06.json")
    if os.path.isfile(report_path):
        details.append({"item": "report file exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found monthly_cost_2026_06.json in reports/."})
        total_score += 5
    else:
        details.append({"item": "report file exists", "score": 5, "max_score": 5, "passed": False, "reason": "Missing monthly_cost_2026_06.json in reports/."})
        # exit early since can't check anything else
        total_score = sum(d["score"] for d in details)
        details.append({"item": "file structure", "score": total_score, "max_score": max_total, "passed": False, "reason": "Report file missing, cannot proceed."})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as out:
            json.dump({"total_score": total_score, "details": details}, out, indent=2)
        return total_score

    # 2. File is valid JSON (10 points)
    try:
        data = load_json(report_path)
        details.append({"item": "report is valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Successfully parsed JSON."})
        total_score += 10
    except (json.JSONDecodeError, ValueError) as e:
        details.append({"item": "report is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        total_score = total_score  # already added
        with open(os.path.join(workspace, "workplace_score.json"), "w") as out:
            json.dump({"total_score": total_score, "details": details}, out, indent=2)
        return total_score

    # 3. Report must be a list of clusters (or an object with cluster key?) The prompt says per-cluster totals. We expect a dict keyed by cluster_name or a list. We'll be flexible: expect a JSON object where each key is a cluster name and value is cluster cost breakdown.
    # For robustness, accept either a list or an object. We'll standardize: if it's a list, assume each element has "cluster_name". If it's an object, keys are cluster names.
    # Load ground truth data from workspace to recompute.
    try:
        clusters_data = load_json(os.path.join(workspace, "data/clusters.json"))["clusters"]
        pricing_data = load_json(os.path.join(workspace, "data/pricing_catalogs.json"))["pricing_catalogs"]
        ledger_data = load_json(os.path.join(workspace, "data/resource_ledger.json"))["resource_ledger"]
    except Exception as e:
        details.append({"item": "reference data loading", "score": 0, "max_score": 5, "passed": False, "reason": f"Cannot load reference data: {e}"})
        total_score += 0
        # can't verify further
        with open(os.path.join(workspace, "workplace_score.json"), "w") as out:
            json.dump({"total_score": total_score, "details": details}, out, indent=2)
        return total_score

    # Find active catalog (status == "active")
    active_catalog = None
    for cat in pricing_data:
        if cat["status"] == "active":
            active_catalog = cat
            break
    if not active_catalog:
        details.append({"item": "active pricing catalog", "score": 0, "max_score": 5, "passed": False, "reason": "No active catalog found."})
        total_score += 0
    else:
        details.append({"item": "active pricing catalog found", "score": 5, "max_score": 5, "passed": True, "reason": f"Using catalog {active_catalog['catalog_id']}"})
        total_score += 5

    # Build cluster_role map
    cluster_role = {}
    for cl in clusters_data:
        cluster_role[cl["cluster_id"]] = cl["cluster_role"]
    # Build cluster_name map
    cluster_name_map = {}
    for cl in clusters_data:
        cluster_name_map[cl["cluster_id"]] = cl["cluster_name"]

    # Business clusters (cluster_role == "business")
    business_cluster_ids = {cl["cluster_id"] for cl in clusters_data if cl["cluster_role"] == "business"}
    # Expected business cluster names: ads-ranking, lakehouse-analytics, retail-core
    expected_clusters = {"ads-ranking", "lakehouse-analytics", "retail-core"}

    # Compute expected cost per business cluster using active catalog rates
    rates_by_key = {}
    for r in active_catalog["rates"]:
        key = (r["resource_family"], r["metric_code"])
        rates_by_key[key] = r["unit_price"]

    expected_cost = {}
    for entry in ledger_data:
        cid = entry["cluster_id"]
        if cid not in business_cluster_ids:
            continue  # skip non-business
        # skip entries with metric_code not in catalog (like tape_storage_gb)
        key = (entry["resource_family"], entry["metric_code"])
        if key not in rates_by_key:
            continue
        price = rates_by_key[key]
        qty = entry["quantity"]
        cost = price * qty
        cname = cluster_name_map.get(cid, entry["cluster_name"])
        if cname not in expected_cost:
            expected_cost[cname] = {"total": 0.0, "resources": []}
        expected_cost[cname]["total"] += cost
        expected_cost[cname]["resources"].append({
            "resource_family": entry["resource_family"],
            "metric_code": entry["metric_code"],
            "quantity": qty,
            "unit_price": price,
            "cost": round(cost, 4)
        })
    # Round totals to 2 decimals
    for cname in expected_cost:
        expected_cost[cname]["total"] = round(expected_cost[cname]["total"], 2)

    # Now check the agent's report
    # Determine format
    if isinstance(data, dict):
        # Assume keys are cluster names
        agent_report = data
    elif isinstance(data, list):
        # Convert list to dict keyed by cluster_name
        agent_report = {}
        for item in data:
            if "cluster_name" in item:
                agent_report[item["cluster_name"]] = item
    else:
        agent_report = {}

    # 4. Check that all three business clusters are present (20 points)
    missing_clusters = expected_clusters - set(agent_report.keys())
    extra_clusters = set(agent_report.keys()) - expected_clusters
    if missing_clusters:
        details.append({"item": "all business clusters present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing clusters: {missing_clusters}"})
        total_score += 0
    else:
        details.append({"item": "all business clusters present", "score": 10, "max_score": 10, "passed": True, "reason": "Found ads-ranking, lakehouse-analytics, retail-core."})
        total_score += 10

    if extra_clusters:
        # likely includes shared-ops or ghost cluster – penalty
        details.append({"item": "no extra clusters", "score": 0, "max_score": 10, "passed": False, "reason": f"Extra clusters found: {extra_clusters}. Should exclude shared_platform and unknown clusters."})
        total_score += 0
    else:
        details.append({"item": "no extra clusters", "score": 10, "max_score": 10, "passed": True, "reason": "No extra clusters."})
        total_score += 10

    # 5. Per-cluster cost breakdown accuracy (40 points)
    # For each business cluster, check total cost and resource details
    resource_score_per_cluster = 40 / len(expected_clusters)  # ~13.33 each
    resource_score_per_cluster = 13  # integer easier, total 39 then add 1 for rounding? We'll allocate 40 total: 10 for totals + 30 for resource details.
    # Let's do: totals part 20 points (6.67 each cluster), resource details part 20 points (6.67 each). We'll sum manually.
    correct_total_points = 0
    correct_resource_points = 0
    for cname in expected_clusters:
        if cname not in agent_report:
            continue
        agent_cluster = agent_report[cname]
        exp = expected_cost.get(cname, {"total": 0.0, "resources": []})
        # Check total cost (allow small floating point rounding)
        agent_total = agent_cluster.get("total_cost", agent_cluster.get("total", None))
        if agent_total is None:
            Correct_total = False
        else:
            if abs(agent_total - exp["total"]) < 0.02:
                correct_total_points += 6
            else:
                pass  # no points
        # Check resource breakdown: we need list of resources with cost
        agent_resources = agent_cluster.get("resources", agent_cluster.get("resource_breakdown", []))
        if not isinstance(agent_resources, list):
            continue
        # For each resource in expected, check if exists with same quantity and cost
        matched = 0
        for er in exp["resources"]:
            for ar in agent_resources:
                if (ar.get("resource_family") == er["resource_family"] and
                    ar.get("metric_code") == er["metric_code"] and
                    abs(ar.get("quantity", 0) - er["quantity"]) < 1 and
                    abs(ar.get("cost", 0) - er["cost"]) < 0.02):
                    matched += 1
                    break
        if matched == len(exp["resources"]):
            correct_resource_points += 6
        elif matched > 0:
            correct_resource_points += 3  # partial

    # Add up resource details
    total_resource_points = correct_total_points + correct_resource_points
    details.append({"item": "cluster total cost accuracy", "score": correct_total_points, "max_score": 20, "passed": correct_total_points >= 18, "reason": f"Correct totals for {correct_total_points//6} clusters."})
    details.append({"item": "resource line-item accuracy", "score": correct_resource_points, "max_score": 20, "passed": correct_resource_points >= 18, "reason": f"Matched {correct_resource_points//6} clusters' resources correctly."})
    total_score += correct_total_points + correct_resource_points

    # Ensure total does not exceed max
    total_score = min(total_score, max_total)
    # produce final summary
    details.append({"item": "overall", "score": total_score, "max_score": max_total, "passed": total_score >= 80, "reason": "Verification complete."})

    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as out:
        json.dump(result, out, indent=2)
    return total_score

if __name__ == "__main__":
    sys.exit(0 if verify() >= 80 else 1)
