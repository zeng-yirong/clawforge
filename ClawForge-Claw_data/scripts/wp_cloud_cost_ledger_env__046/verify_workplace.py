"""
Verify the agent-generated cost report for task wp_cloud_cost_ledger_env__046.
Reads workspace files and checks correctness.
"""
import sys
import os
import json
from decimal import Decimal, ROUND_HALF_UP

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. Check directory structure existence (5 points)
    required_dirs = ["data", "data/pricing"]
    all_dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in required_dirs)
    if all_dirs_exist:
        details.append({"item": "Required directories exist", "score": 5, "max_score": 5, "passed": True, "reason": "data/ and data/pricing/ present"})
        score += 5
    else:
        missing = [d for d in required_dirs if not os.path.isdir(os.path.join(workspace, d))]
        details.append({"item": "Required directories exist", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing: {missing}"})

    # 2. Check cost_report_2026_06.json exists (5 points)
    report_path = os.path.join(workspace, "cost_report_2026_06.json")
    if os.path.isfile(report_path):
        details.append({"item": "Report file exists", "score": 5, "max_score": 5, "passed": True, "reason": "cost_report_2026_06.json found"})
        score += 5
    else:
        details.append({"item": "Report file exists", "score": 0, "max_score": 5, "passed": False, "reason": "cost_report_2026_06.json not found"})
        # No further checks possible
        write_score(score, details)
        return

    # 3. Parse report JSON (10 points)
    try:
        report = load_json(report_path)
        details.append({"item": "Report JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        score += 10
    except Exception as e:
        details.append({"item": "Report JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        write_score(score, details)
        return

    # 4. Check required fields (20 points)
    field_score = 0
    field_messages = []
    # report_month
    if report.get("report_month") == "2026-06":
        field_score += 5
        field_messages.append("report_month correct")
    else:
        field_messages.append(f"report_month expected '2026-06', got {report.get('report_month')}")
    # clusters must be a list
    clusters = report.get("clusters")
    if isinstance(clusters, list) and len(clusters) > 0:
        field_score += 5
        field_messages.append("clusters is a non-empty list")
    else:
        field_messages.append(f"clusters missing or not a list, got {type(clusters)}")
    # Each cluster must have cluster_id, cluster_name, total_cost
    cluster_items_ok = True
    for cl in clusters:
        if not all(k in cl for k in ("cluster_id", "cluster_name", "total_cost")):
            cluster_items_ok = False
            field_messages.append(f"Cluster {cl.get('cluster_id','?')} missing required fields")
            break
    if cluster_items_ok:
        field_score += 10
        field_messages.append("All clusters have required fields")
    else:
        field_messages.append("Some clusters lack required fields")
    details.append({"item": "Report field structure", "score": field_score, "max_score": 20, "passed": field_score == 20, "reason": "; ".join(field_messages)})
    score += field_score

    # 5. Validate data integrity: must contain exactly three business clusters (ads-ranking, lakehouse-analytics, retail-core) with correct costs (30 points)
    # Compute expected costs from source data
    try:
        clusters_data = load_json(os.path.join(workspace, "data/clusters.json"))["clusters"]
        pricing = load_json(os.path.join(workspace, "data/pricing/pricing_catalogs.json"))["pricing_catalogs"]
        ledger = load_json(os.path.join(workspace, "data/resource_ledger.json"))["resource_ledger"]
    except Exception as e:
        details.append({"item": "Data integrity and cost computation", "score": 0, "max_score": 30, "passed": False, "reason": f"Failed to load source data: {str(e)}"})
        write_score(score, details)
        return

    # Find active pricing catalog (2026.06-live)
    active_pricing = None
    for cat in pricing:
        if cat["version"] == "2026.06-live" and cat["status"] == "active":
            active_pricing = cat
            break
    if not active_pricing:
        details.append({"item": "Data integrity and cost computation", "score": 0, "max_score": 30, "passed": False, "reason": "Active pricing catalog not found"})
        write_score(score, details)
        return

    # Build rate lookup: (resource_family, metric_code) -> unit_price
    rate_map = {}
    for r in active_pricing["rates"]:
        rate_map[(r["resource_family"], r["metric_code"])] = Decimal(str(r["unit_price"]))

    # Build business cluster IDs
    business_ids = {c["cluster_id"] for c in clusters_data if c["cluster_role"] == "business"}

    # Compute expected costs per cluster
    expected_costs = {}
    for entry in ledger:
        cid = entry.get("cluster_id")
        if cid not in business_ids:
            continue
        qty = Decimal(str(entry.get("quantity", 0)))
        if qty <= 0:
            continue
        rf = entry.get("resource_family")
        mc = entry.get("metric_code")
        if not mc or not rf:
            continue
        key = (rf, mc)
        if key not in rate_map:
            continue
        cost = qty * rate_map[key]
        expected_costs[cid] = expected_costs.get(cid, Decimal('0')) + cost

    # Round to 2 decimal places
    expected_costs = {k: v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for k, v in expected_costs.items()}

    # Map cluster_id to cluster_name
    id_to_name = {c["cluster_id"]: c["cluster_name"] for c in clusters_data}

    # Build expected report clusters
    expected_clusters = []
    for cid in sorted(expected_costs.keys()):
        expected_clusters.append({
            "cluster_id": cid,
            "cluster_name": id_to_name[cid],
            "total_cost": float(expected_costs[cid])
        })

    # Compare with agent report
    agent_clusters = report.get("clusters", [])
    # Build agent map by cluster_id
    agent_by_id = {c["cluster_id"]: c for c in agent_clusters}

    integrity_score = 0
    integrity_messages = []
    # Expect exactly 3 clusters
    expected_ids = {"c-ads-ranking", "c-lakehouse-analytics", "c-retail-core"}
    agent_ids = set(agent_by_id.keys())
    if agent_ids == expected_ids:
        integrity_score += 5
        integrity_messages.append("Exactly 3 business clusters present")
    else:
        extra = agent_ids - expected_ids
        missing = expected_ids - agent_ids
        msg_parts = []
        if extra:
            msg_parts.append(f"Extra clusters: {extra}")
        if missing:
            msg_parts.append(f"Missing clusters: {missing}")
        integrity_messages.append("; ".join(msg_parts))

    # Check each cluster cost
    cost_score = 0
    cost_max = 25  # remaining from 30
    for cid in expected_ids:
        if cid not in agent_by_id:
            continue
        act = agent_by_id[cid].get("total_cost")
        exp = float(expected_costs[cid])
        if act is None:
            continue
        # Allow small floating epsilon? Use math.isclose with tolerance 0.005 because we rounded to 2 decimals
        if abs(act - exp) < 0.005:
            cost_score += 25 // len(expected_ids)  # 25/3 ≈ 8.33, use int division? Better assign 8,8,9
        else:
            integrity_messages.append(f"{id_to_name[cid]}: expected {exp}, got {act}")

    # Since we cannot split 25 evenly, assign 9,8,8 based on order
    if cost_score == 0:
        # recalc precisely
        cost_score = 0
        assignments = {"c-ads-ranking": 9, "c-lakehouse-analytics": 8, "c-retail-core": 8}
        for cid in expected_ids:
            if cid not in agent_by_id:
                continue
            act = agent_by_id[cid].get("total_cost")
            exp = float(expected_costs[cid])
            if act is not None and abs(act - exp) < 0.005:
                cost_score += assignments[cid]
            else:
                integrity_messages.append(f"{id_to_name[cid]}: expected {exp}, got {act} (0 pt)")
        if cost_score == 25:
            integrity_messages.append("All cluster costs correct")
        else:
            integrity_messages.append(f"Partial cost accuracy: {cost_score}/25")

    total_integrity = 5 + cost_score
    details.append({"item": "Data integrity and cost computation", "score": total_integrity, "max_score": 30, "passed": total_integrity == 30, "reason": "; ".join(integrity_messages)})
    score += total_integrity

    # Write final score
    write_score(score, details)

def write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {score}/100")

if __name__ == "__main__":
    verify()
