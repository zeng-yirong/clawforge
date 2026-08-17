import sys
import json
import os
import math

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. Check workspace directory exists (we already have it, but for safety)
    if not os.path.isdir(workspace):
        details.append({"item": "workspace exists", "score": 0, "max_score": 5, "passed": False, "reason": "Workspace directory not found"})
        return write_score(details, workspace)

    details.append({"item": "workspace exists", "score": 5, "max_score": 5, "passed": True, "reason": "Workspace directory found"})
    total_score += 5

    # 2. Check required report file exists
    report_path = os.path.join(workspace, "ops", "cost_report_june_2026.json")
    if not os.path.isfile(report_path):
        details.append({"item": "report file exists", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected file at ops/cost_report_june_2026.json not found"})
        return write_score(details, workspace)
    details.append({"item": "report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "Report file present"})
    total_score += 10

    # 3. Parse JSON and validate format
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        return write_score(details, workspace)
    if not isinstance(report, list):
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "Report root is not a list"})
        return write_score(details, workspace)
    details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Report is a valid JSON list"})
    total_score += 10

    # 4. Check each report item has required fields
    required_fields = {"cluster_name", "compute_cost", "storage_cost", "total_cost"}
    field_ok = True
    for item in report:
        if not isinstance(item, dict):
            field_ok = False
            break
        if not required_fields.issubset(item.keys()):
            field_ok = False
            break
    if not field_ok:
        details.append({"item": "report fields", "score": 0, "max_score": 10, "passed": False, "reason": "Each entry must have cluster_name, compute_cost, storage_cost, total_cost (all numeric)"})
        return write_score(details, workspace)
    details.append({"item": "report fields", "score": 10, "max_score": 10, "passed": True, "reason": "All required fields present"})
    total_score += 10

    # 5. Count business clusters (should be exactly 3: ads-ranking, lakehouse-analytics, retail-core)
    business_clusters = ["ads-ranking", "lakehouse-analytics", "retail-core"]
    reported_names = {item["cluster_name"] for item in report}
    extra_clusters = reported_names - set(business_clusters)
    missing_clusters = set(business_clusters) - reported_names
    if missing_clusters:
        details.append({"item": "correct cluster list", "score": 0, "max_score": 15, "passed": False, "reason": f"Missing clusters: {missing_clusters}"})
        return write_score(details, workspace)
    if extra_clusters:
        details.append({"item": "no extra clusters", "score": 0, "max_score": 10, "passed": False, "reason": f"Extra clusters found (shared-ops should be excluded): {extra_clusters}"})
        return write_score(details, workspace)
    details.append({"item": "correct cluster list", "score": 15, "max_score": 15, "passed": True, "reason": "All three business clusters present, no extras"})
    total_score += 15

    # 6. Build expected costs using the live pricing catalog (cat-2026-06)
    # We need to read resource_ledger and clusters from the workspace to compute
    ledger_path = os.path.join(workspace, "data", "resources", "resource_ledger.json")
    clusters_path = os.path.join(workspace, "data", "resources", "clusters.json")
    catalog_path = os.path.join(workspace, "data", "pricing", "pricing_catalogs.json")

    try:
        with open(ledger_path) as f:
            ledger_data = json.load(f)["resource_ledger"]
        with open(clusters_path) as f:
            clusters_data = json.load(f)["clusters"]
        with open(catalog_path) as f:
            catalogs_data = json.load(f)["pricing_catalogs"]
    except Exception as e:
        details.append({"item": "source data loading", "score": 0, "max_score": 5, "passed": False, "reason": f"Could not load source data: {str(e)}"})
        return write_score(details, workspace)

    # Find the active '2026-06' catalog
    live_catalog = None
    for cat in catalogs_data:
        if cat["status"] == "active" and cat["approved_for_reporting"] and cat["billing_month"] == "2026-06":
            live_catalog = cat
            break
    if not live_catalog:
        details.append({"item": "live catalog", "score": 0, "max_score": 5, "passed": False, "reason": "No active, approved catalog for 2026-06 found"})
        return write_score(details, workspace)

    # Build rate lookup
    rates = {}
    for rate in live_catalog["rates"]:
        rates[rate["metric_code"]] = rate["unit_price"]

    # Build cluster_role lookup
    cluster_role = {}
    for cl in clusters_data:
        cluster_role[cl["cluster_id"]] = cl["cluster_role"]

    # Compute expected costs per business cluster
    expected = {}
    for entry in ledger_data:
        cid = entry["cluster_id"]
        role = cluster_role.get(cid, "")
        if role != "business":
            continue
        cname = entry["cluster_name"]
        if cname not in business_clusters:
            continue  # safety
        qty = entry["quantity"]
        mc = entry["metric_code"]
        unit_price = rates.get(mc, 0.0)
        cost = qty * unit_price

        if cname not in expected:
            expected[cname] = {"compute": 0.0, "storage": 0.0}
        # classify compute vs storage by resource_family
        if entry["resource_family"] == "compute":
            expected[cname]["compute"] += cost
        elif entry["resource_family"] == "storage":
            expected[cname]["storage"] += cost
        else:
            # shouldn't happen
            pass

    # Compare with reported values (allow 0.005 rounding)
    compute_ok = True
    storage_ok = True
    for cluster_name in business_clusters:
        rep_item = None
        for item in report:
            if item["cluster_name"] == cluster_name:
                rep_item = item
                break
        if rep_item is None:
            # should not happen because we already checked presence
            continue
        exp = expected.get(cluster_name, {"compute": 0.0, "storage": 0.0})
        exp_compute = round(exp["compute"], 2)
        exp_storage = round(exp["storage"], 2)
        exp_total = round(exp_compute + exp_storage, 2)

        rep_compute = round(rep_item["compute_cost"], 2)
        rep_storage = round(rep_item["storage_cost"], 2)
        rep_total = round(rep_item["total_cost"], 2)

        if abs(rep_compute - exp_compute) > 0.005:
            compute_ok = False
        if abs(rep_storage - exp_storage) > 0.005:
            storage_ok = False
        if abs(rep_total - exp_total) > 0.005:
            compute_ok = False  # total must match as well

    if compute_ok and storage_ok:
        details.append({"item": "cost values accuracy", "score": 35, "max_score": 35, "passed": True, "reason": "All cluster compute and storage costs match expected (within 0.005)"})
        total_score += 35
    else:
        detail_str = ""
        if not compute_ok:
            detail_str += "Compute costs mismatch. "
        if not storage_ok:
            detail_str += "Storage costs mismatch."
        details.append({"item": "cost values accuracy", "score": 0, "max_score": 35, "passed": False, "reason": detail_str})
        # We could assign partial credit but for simplicity we give 0 if any mismatch.
        # However, we can break down further for better grading? Let's do per-cluster partial.
        # Actually we already gave structure. Let's do per-cluster scoring to be more granular.
        # Rewrite: replace the above with per-cluster check.
        # But we already appended a detail. To keep code clean, we'll rewrite the whole block.
        # For simplicity, we'll revert to a single item but with partial scoring inside.
        # We'll pop the last item and recalc.
        details.pop()  # remove the inaccurate entry
        total_score -= 35  # remove the tentative points
        # Now do per-cluster scoring
        cluster_score = 0
        cluster_max = 35
        cluster_items = []
        for cluster_name in business_clusters:
            rep_item = None
            for item in report:
                if item["cluster_name"] == cluster_name:
                    rep_item = item
                    break
            if rep_item is None:
                cluster_items.append((cluster_name, 0, 12, False, "Cluster missing in report"))
                continue
            exp = expected.get(cluster_name, {"compute": 0.0, "storage": 0.0})
            exp_compute = round(exp["compute"], 2)
            exp_storage = round(exp["storage"], 2)
            rep_compute = round(rep_item["compute_cost"], 2)
            rep_storage = round(rep_item["storage_cost"], 2)
            rep_total = round(rep_item["total_cost"], 2)
            compute_match = abs(rep_compute - exp_compute) <= 0.005
            storage_match = abs(rep_storage - exp_storage) <= 0.005
            total_match = abs(rep_total - (exp_compute+exp_storage)) <= 0.005
            if compute_match and storage_match and total_match:
                cluster_items.append((cluster_name, 12, 12, True, f"Costs for {cluster_name} correct"))
                cluster_score += 12
            elif compute_match and storage_match:
                cluster_items.append((cluster_name, 10, 12, False, f"Total mismatch for {cluster_name}"))
                cluster_score += 10
            elif compute_match or storage_match:
                cluster_items.append((cluster_name, 6, 12, False, f"Partial cost mismatch for {cluster_name}"))
                cluster_score += 6
            else:
                cluster_items.append((cluster_name, 0, 12, False, f"All costs wrong for {cluster_name}"))
        # Adjust cluster_max to 36 (3*12) but we only have 35, so scale
        # We'll set max for per-cluster to 35 total (11.666 per cluster? better to make 35 = 3 x 11.666? We'll keep 12 each, but then total 36. Over budget? We'll adjust.
        # Simpler: just give cluster_score as is, with max 36, but we cap total at 100. We'll reduce previous items' max slightly.
        # But already committed. Let's just continue with cluster_score out of 36, then later normalize? Complicated.
        # For simplicity, we'll revert to a single 35-point item with all-or-nothing? But we already have fine structure in details.
        # I think the initial all-or-nothing is acceptable. We'll keep the initial approach and just set score=0 for accuracy if any mismatch.
        # But we already popped. Let's redo: we'll not pop, just accept the first approach and continue.
        # Since we popped and didn't write, we need to append a new detail. Let's just write a single item with 0.
        details.append({"item": "cost values accuracy", "score": 0, "max_score": 35, "passed": False, "reason": "One or more cluster costs do not match expected values"})
        # Keep total_score unchanged (already subtracted 35)
    # End of cost accuracy block

    # 7. Check that no unexpected extra fields exist (optional, not penalized)
    # All checks done, now compute final total
    total = sum(d["score"] for d in details)
    # We've been accumulating total_score in parallel; ensure consistency
    total_score = total
    write_score(details, workspace, total_score)

def write_score(details, workspace, total_score=None):
    if total_score is None:
        total_score = sum(d["score"] for d in details)
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    # Also print to stdout for debugging
    print(f"Score: {total_score}/100")
    for d in details:
        print(f"  {d['item']}: {d['score']}/{d['max_score']} {'PASS' if d['passed'] else 'FAIL'}")
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
