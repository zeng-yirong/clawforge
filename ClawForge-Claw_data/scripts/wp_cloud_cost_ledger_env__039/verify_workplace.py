"""
Verifier for cloud_cost_ledger_env task wp_cloud_cost_ledger_env__039.
Checks agent-generated reports/monthly_cost_summary.json against ground truth.
"""
import sys
import os
import json
import math


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_ground_truth(workspace):
    """Calculate expected cost report from initial data files."""
    clusters_path = os.path.join(workspace, "data/resources/clusters.json")
    ledger_path = os.path.join(workspace, "data/resources/resource_ledger.json")
    pricing_path = os.path.join(workspace, "data/pricing/pricing_catalogs.json")

    clusters = load_json(clusters_path)["clusters"]
    ledger = load_json(ledger_path)["resource_ledger"]
    catalogs = load_json(pricing_path)["pricing_catalogs"]

    # Find active catalog for June 2026
    active_catalog = None
    for cat in catalogs:
        if cat["status"] == "active" and cat["billing_month"] == "2026-06":
            active_catalog = cat
            break
    if active_catalog is None:
        raise ValueError("No active June 2026 catalog found")

    # Build rate map: (resource_family, metric) -> rate_per_unit
    rate_map = {}
    for r in active_catalog["rates"]:
        rate_map[(r["resource_family"], r["metric"])] = r["rate_per_unit"]

    # Map cluster_id to business clusters only
    business_ids = set()
    cluster_info = {}
    for c in clusters:
        if c["cluster_role"] == "business":
            business_ids.add(c["cluster_id"])
            cluster_info[c["cluster_id"]] = {
                "cluster_name": c["cluster_name"],
                "business_service": c["business_service"]
            }

    # Aggregate costs per cluster
    cluster_costs = {}
    for entry in ledger:
        cid = entry["cluster_id"]
        if cid not in business_ids:
            continue  # skip shared or orphan
        # Determine resource_family and metric_code from entry
        family = entry["resource_family"]
        metric = entry["metric_code"]
        key = (family, metric)
        if key not in rate_map:
            continue  # no rate, skip (shouldn't happen with our data)
        rate = rate_map[key]
        qty = entry["quantity"]
        cost = qty * rate

        if cid not in cluster_costs:
            cluster_costs[cid] = {"compute": 0.0, "storage": 0.0}
        if family == "compute":
            cluster_costs[cid]["compute"] += cost
        elif family == "storage":
            cluster_costs[cid]["storage"] += cost

    # Build expected report clusters list
    clusters_list = []
    grand_compute = 0.0
    grand_storage = 0.0
    for cid in sorted(business_ids):
        info = cluster_info[cid]
        costs = cluster_costs.get(cid, {"compute": 0.0, "storage": 0.0})
        comp = round(costs["compute"], 6)
        stor = round(costs["storage"], 6)
        total = round(comp + stor, 6)
        grand_compute += comp
        grand_storage += stor
        clusters_list.append({
            "cluster_id": cid,
            "cluster_name": info["cluster_name"],
            "business_service": info["business_service"],
            "costs": {
                "compute": comp,
                "storage": stor,
                "total": total
            }
        })

    grand_total = round(grand_compute + grand_storage, 6)
    grand_compute = round(grand_compute, 6)
    grand_storage = round(grand_storage, 6)

    return {
        "billing_month": "2026-06",
        "generated_by": "Cloud FinOps Bot",
        "clusters": clusters_list,
        "grand_total_compute": grand_compute,
        "grand_total_storage": grand_storage,
        "grand_total": grand_total
    }


def verify(workspace: str) -> dict:
    score = 0
    max_score = 100
    details = []

    # 1. Check reports directory exists (10 pts)
    report_dir = os.path.join(workspace, "reports")
    dir_exists = os.path.isdir(report_dir)
    details.append({
        "item": "reports directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Directory 'reports/' found" if dir_exists else "Missing reports/ directory"
    })
    if not dir_exists:
        return {"total_score": 0, "details": details}

    # 2. Check report file exists (10 pts)
    report_path = os.path.join(report_dir, "monthly_cost_summary.json")
    file_exists = os.path.isfile(report_path)
    details.append({
        "item": "monthly_cost_summary.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "Missing reports/monthly_cost_summary.json"
    })
    if not file_exists:
        return {"total_score": sum(d["score"] for d in details), "details": details}

    # 3. JSON parseable (10 pts)
    try:
        report = load_json(report_path)
        parse_ok = True
        details.append({
            "item": "Report file is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully"
        })
    except Exception as e:
        details.append({
            "item": "Report file is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {str(e)}"
        })
        return {"total_score": sum(d["score"] for d in details), "details": details}

    # Compute ground truth
    try:
        expected = compute_ground_truth(workspace)
    except Exception as e:
        details.append({
            "item": "Ground truth computation",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"Error in ground truth: {str(e)}"
        })
        return {"total_score": sum(d["score"] for d in details), "details": details}

    # 4. Check top-level fields (15 pts)
    top_fields = ["billing_month", "generated_by", "clusters", "grand_total_compute", "grand_total_storage", "grand_total"]
    missing = [f for f in top_fields if f not in report]
    if missing:
        details.append({
            "item": "Top-level fields present",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Missing fields: {', '.join(missing)}"
        })
    else:
        details.append({
            "item": "Top-level fields present",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "All required top-level fields exist"
        })

    # 5. Billing month correctness (5 pts)
    bill_ok = report.get("billing_month") == "2026-06"
    details.append({
        "item": "billing_month is 2026-06",
        "score": 5 if bill_ok else 0,
        "max_score": 5,
        "passed": bill_ok,
        "reason": "billing_month correct" if bill_ok else f"Got '{report.get('billing_month')}'"
    })

    # 6. Clusters list structure (15 pts – check each cluster has required subfields)
    clusters_ok = True
    if not isinstance(report.get("clusters"), list):
        clusters_ok = False
        details.append({
            "item": "clusters is a list",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "clusters is not a list"
        })
    else:
        cluster_fields = ["cluster_id", "cluster_name", "business_service", "costs"]
        cost_fields = ["compute", "storage", "total"]
        errors = []
        for i, cl in enumerate(report["clusters"]):
            for f in cluster_fields:
                if f not in cl:
                    errors.append(f"Cluster {i}: missing '{f}'")
            costs = cl.get("costs", {})
            for f in cost_fields:
                if f not in costs:
                    errors.append(f"Cluster {i} costs: missing '{f}'")
        if errors:
            clusters_ok = False
            details.append({
                "item": "Cluster list structure",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "; ".join(errors)
            })
        else:
            details.append({
                "item": "Cluster list structure",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": f"All {len(report['clusters'])} clusters have correct structure"
            })

    # 7. Numerical accuracy – grand totals (35 pts)
    # Compare with tolerance 0.001
    tol = 1e-3
    grand_correct = True
    for key, expected_val in [("grand_total_compute", expected["grand_total_compute"]),
                               ("grand_total_storage", expected["grand_total_storage"]),
                               ("grand_total", expected["grand_total"])]:
        actual = report.get(key)
        if not isinstance(actual, (int, float)):
            grand_correct = False
            continue
        if abs(actual - expected_val) > tol:
            grand_correct = False
    if grand_correct:
        details.append({
            "item": "Grand total numbers accurate",
            "score": 35,
            "max_score": 35,
            "passed": True,
            "reason": "All grand total values match expected"
        })
    else:
        # Partial credit: give 15 if at least one correct
        correct_count = 0
        for key, expected_val in [("grand_total_compute", expected["grand_total_compute"]),
                                   ("grand_total_storage", expected["grand_total_storage"]),
                                   ("grand_total", expected["grand_total"])]:
            actual = report.get(key)
            if isinstance(actual, (int, float)) and abs(actual - expected_val) <= tol:
                correct_count += 1
        partial = int(35 * (correct_count / 3))
        details.append({
            "item": "Grand total numbers accurate",
            "score": partial,
            "max_score": 35,
            "passed": correct_count == 3,
            "reason": f"Correct: {correct_count}/3 grand totals"
        })

    # 8. Per-cluster cost accuracy (0 pts standalone, but we deduct if mismatched?
    # We'll just note but not add separate points; totals already cover.
    # Instead, we add a small check: the number of clusters should be 2 (ads, retail)
    expected_cluster_ids = set(cl["cluster_id"] for cl in expected["clusters"])
    actual_cluster_ids = set(cl.get("cluster_id") for cl in report.get("clusters", []))
    cluster_count_ok = (actual_cluster_ids == expected_cluster_ids)
    details.append({
        "item": "Cluster IDs match expected business clusters",
        "score": 0,  # not scored separately, but informative
        "max_score": 0,
        "passed": cluster_count_ok,
        "reason": f"Expected {expected_cluster_ids}, got {actual_cluster_ids}" if not cluster_count_ok else "Cluster IDs correct"
    })

    # Compute total score from scorable items
    total_score = sum(d["score"] for d in details if d["max_score"] > 0)
    return {"total_score": total_score, "details": details}


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
