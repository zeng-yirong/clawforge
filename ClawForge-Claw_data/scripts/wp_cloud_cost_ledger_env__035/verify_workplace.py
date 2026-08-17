import sys
import json
import os
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import csv

def validate_report(workspace: str) -> dict:
    details = []
    total_score = 0

    # Paths
    report_path = Path(workspace) / "reports" / "cost_report.json"
    clusters_path = Path(workspace) / "data" / "resources" / "clusters.json"
    ledger_path = Path(workspace) / "data" / "resources" / "resource_ledger.json"
    catalog_path = Path(workspace) / "data" / "pricing" / "pricing_catalogs.json"

    # ---------- 1. Check report file exists (10pts) ----------
    if not report_path.exists():
        return {
            "total_score": 0,
            "details": [{"item": "report file exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/cost_report.json not found"}]
        }
    details.append({"item": "report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
    total_score += 10

    # ---------- 2. Load and validate JSON (10pts) ----------
    try:
        with open(report_path) as f:
            report = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        return {"total_score": total_score, "details": details + [{"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": str(e)}]}
    if not isinstance(report, dict) or "clusters" not in report:
        details.append({"item": "valid JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "missing 'clusters' key or not a dict"})
        return {"total_score": total_score, "details": details}
    details.append({"item": "valid JSON structure", "score": 10, "max_score": 10, "passed": True, "reason": "JSON is valid dict with clusters"})
    total_score += 10

    # ---------- 3. Load reference data ----------
    with open(clusters_path) as f:
        clusters_data = json.load(f)["clusters"]
    with open(ledger_path) as f:
        ledger_data = json.load(f)["resource_ledger"]
    with open(catalog_path) as f:
        catalogs_data = json.load(f)["pricing_catalogs"]

    # Active pricing catalog
    live_catalog = None
    for c in catalogs_data:
        if c["status"] == "active":
            live_catalog = c
            break
    if live_catalog is None:
        details.append({"item": "pricing catalog usage", "score": 0, "max_score": 20, "passed": False, "reason": "no active catalog found in source"})
        return {"total_score": total_score, "details": details}

    # Build rate map from active catalog
    rate_map = {}
    for r in live_catalog["rates"]:
        rate_map[r["metric_code"]] = Decimal(str(r["rate"]))

    # Identify business clusters (cluster_role == 'business')
    business_cluster_ids = set()
    business_cluster_names = {}
    for cl in clusters_data:
        if cl["cluster_role"] == "business":
            business_cluster_ids.add(cl["cluster_id"])
            business_cluster_names[cl["cluster_id"]] = cl["cluster_name"]

    # Compute expected totals per business cluster from ledger
    expected_clusters = {}
    for entry in ledger_data:
        cid = entry["cluster_id"]
        if cid not in business_cluster_ids:
            continue
        if cid not in expected_clusters:
            expected_clusters[cid] = {"cluster_name": entry["cluster_name"], "details": []}
        mc = entry["metric_code"]
        qty = Decimal(str(entry["quantity"]))
        rate = rate_map.get(mc)
        if rate is None:
            # metric not in catalog, skip?
            continue
        cost = (qty * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        expected_clusters[cid]["details"].append({
            "resource_family": entry["resource_family"],
            "metric_code": mc,
            "quantity": int(qty),
            "rate": float(rate),
            "cost": float(cost)
        })
    # Calculate expected total_cost per cluster
    for cid, info in expected_clusters.items():
        total = sum(Decimal(str(d["cost"])) for d in info["details"])
        info["total_cost"] = float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    # ---------- 4. Validate report clusters (20pts) ----------
    report_clusters = report.get("clusters", [])
    if not isinstance(report_clusters, list):
        details.append({"item": "clusters list", "score": 0, "max_score": 20, "passed": False, "reason": "clusters is not a list"})
        return {"total_score": total_score, "details": details}

    # Check that all business clusters are present and no extra business clusters
    reported_cids = {c["cluster_id"] for c in report_clusters}
    missing_business = sorted(business_cluster_ids - reported_cids)
    extra_business = sorted(reported_cids - business_cluster_ids)
    if missing_business:
        details.append({"item": "cluster coverage", "score": 0, "max_score": 20, "passed": False, "reason": f"missing business clusters: {missing_business}"})
        return {"total_score": total_score, "details": details}
    if extra_business:
        details.append({"item": "cluster coverage", "score": 0, "max_score": 20, "passed": False, "reason": f"extra clusters reported: {extra_business}"})
        return {"total_score": total_score, "details": details}
    # Check that non-business clusters not included
    for c in report_clusters:
        if c["cluster_id"] not in business_cluster_ids:
            details.append({"item": "cluster coverage", "score": 0, "max_score": 20, "passed": False, "reason": f"non-business cluster reported: {c['cluster_id']}"})
            return {"total_score": total_score, "details": details}
    details.append({"item": "cluster coverage", "score": 20, "max_score": 20, "passed": True, "reason": "all business clusters present, no extra"})
    total_score += 20

    # ---------- 5. Validate each cluster's details and total (50pts) ----------
    # We'll assign 10 points per cluster (3 clusters) for total cost accuracy, plus 20 for details correctness.
    cluster_score_breakdown = {
        "cls-ads-rnk-01": 17,  # 17/50
        "cls-lake-an-01": 17,
        "cls-retail-c-01": 16
    }
    assigned = 0
    for c in report_clusters:
        cid = c["cluster_id"]
        if cid not in expected_clusters:
            continue
        exp = expected_clusters[cid]
        # Check total_cost
        reported_total = Decimal(str(c.get("total_cost", "0")))
        expected_total = Decimal(str(exp["total_cost"]))
        if reported_total != expected_total:
            details.append({"item": f"total_cost for {cid}", "score": 0, "max_score": cluster_score_breakdown.get(cid, 15), "passed": False, "reason": f"expected {expected_total}, got {reported_total}"})
            assigned += cluster_score_breakdown.get(cid, 15)
            continue
        # Check details array
        reported_details = c.get("details", [])
        if not isinstance(reported_details, list):
            details.append({"item": f"details for {cid}", "score": 0, "max_score": cluster_score_breakdown.get(cid, 15), "passed": False, "reason": "details is not a list"})
            assigned += cluster_score_breakdown.get(cid, 15)
            continue
        # Build map of expected detail entries (by metric_code for simplicity, but need to handle duplicates)
        # Since duplicates are allowed, we'll sort both lists and compare element-wise
        exp_details_sorted = sorted(exp["details"], key=lambda x: (x["metric_code"], x["quantity"], x["rate"]))
        # Note: we expect agent to output details entries that match ones we computed.
        # We will check that the set of (metric_code, quantity, rate, cost) matches
        reported_set = {(d["metric_code"], d["quantity"], d["rate"], d["cost"]) for d in reported_details}
        expected_set = {(d["metric_code"], d["quantity"], d["rate"], d["cost"]) for d in exp_details_sorted}
        if reported_set != expected_set:
            details.append({"item": f"details content for {cid}", "score": 0, "max_score": cluster_score_breakdown.get(cid, 15), "passed": False, "reason": f"reported details mismatch expected. Expected: {expected_set}, Got: {reported_set}"})
            assigned += cluster_score_breakdown.get(cid, 15)
            continue
        # Also verify that total_cost == sum(details.cost) within cluster
        sum_cost = sum(Decimal(str(d["cost"])) for d in reported_details)
        if sum_cost.quantize(Decimal('0.01')) != reported_total:
            details.append({"item": f"total_cost sum check for {cid}", "score": 0, "max_score": cluster_score_breakdown.get(cid, 15), "passed": False, "reason": "total_cost does not match sum of details costs"})
            assigned += cluster_score_breakdown.get(cid, 15)
            continue
        # Pass
        details.append({"item": f"cluster {cid} correctness", "score": cluster_score_breakdown.get(cid, 15), "max_score": cluster_score_breakdown.get(cid, 15), "passed": True, "reason": "total and details match expected"})
        assigned += cluster_score_breakdown.get(cid, 15)

    # If some clusters missing, we already returned earlier; here all present.
    total_score += assigned

    # ---------- 6. Check report_month and currency (10pts) ----------
    extra_points = 0
    if report.get("report_month") == "2026-06":
        extra_points += 5
        details.append({"item": "report_month field", "score": 5, "max_score": 5, "passed": True, "reason": "correct month"})
    else:
        details.append({"item": "report_month field", "score": 0, "max_score": 5, "passed": False, "reason": f"got {report.get('report_month')}"})

    if report.get("currency") == "USD":
        extra_points += 5
        details.append({"item": "currency field", "score": 5, "max_score": 5, "passed": True, "reason": "correct currency"})
    else:
        details.append({"item": "currency field", "score": 0, "max_score": 5, "passed": False, "reason": f"got {report.get('currency')}"})
    total_score += extra_points

    # ---------- Final ----------
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = validate_report(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
    sys.exit(0 if result['total_score'] >= 60 else 1)

if __name__ == "__main__":
    main()
