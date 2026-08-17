import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def read_json(rel_path):
    full_path = os.path.join(workspace, rel_path)
    if not os.path.isfile(full_path):
        return None
    with open(full_path, "r") as f:
        return json.load(f)

def write_score(total, details):
    path = os.path.join(workspace, "workplace_score.json")
    with open(path, "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)

def main():
    details = []
    score = 0

    # --- 1. Check that cost_report directory exists ---
    report_dir = os.path.join(workspace, "cost_report")
    dir_exists = os.path.isdir(report_dir)
    details.append({
        "item": "cost_report directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "cost_report directory found" if dir_exists else "cost_report directory missing"
    })
    if dir_exists:
        score += 10

    # --- 2. Check that business_compute_cost.json exists ---
    report_file = "cost_report/business_compute_cost.json"
    data = read_json(report_file)
    file_exists = data is not None
    details.append({
        "item": "business_compute_cost.json exists and is valid JSON",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File exists and is valid JSON" if file_exists else "File missing or not valid JSON"
    })
    if file_exists:
        score += 10
    else:
        write_score(score, details)
        return

    # --- 3. Check top-level structure ---
    has_report_month = "report_month" in data
    has_clusters = "clusters" in data
    has_total = "total_cost" in data
    struct_ok = has_report_month and has_clusters and has_total
    details.append({
        "item": "Top-level fields: report_month, clusters, total_cost",
        "score": 15 if struct_ok else 0,
        "max_score": 15,
        "passed": struct_ok,
        "reason": f"report_month: {has_report_month}, clusters: {has_clusters}, total_cost: {has_total}" if struct_ok else "Missing one or more top-level fields"
    })
    if struct_ok:
        score += 15

    # --- 4. Check report_month value ---
    month_ok = data.get("report_month") == "2026-06"
    details.append({
        "item": "report_month equals '2026-06'",
        "score": 5 if month_ok else 0,
        "max_score": 5,
        "passed": month_ok,
        "reason": f"report_month is '{data.get('report_month')}'" if month_ok else f"Expected '2026-06', got '{data.get('report_month')}'"
    })
    if month_ok:
        score += 5

    # --- 5. Check clusters list ---
    clusters = data.get("clusters", [])
    if not isinstance(clusters, list):
        clusters = []
    cluster_names = [c.get("cluster_name") for c in clusters]

    # Expected clusters: ads-ranking and retail-core only
    expected_names = {"ads-ranking", "retail-core"}
    extra = set(cluster_names) - expected_names
    missing = expected_names - set(cluster_names)
    cluster_correct = len(clusters) == 2 and not extra and not missing
    details.append({
        "item": "Exactly 2 business clusters (ads-ranking, retail-core), no extra",
        "score": 15 if cluster_correct else 0,
        "max_score": 15,
        "passed": cluster_correct,
        "reason": f"Clusters: {cluster_names}. Missing: {missing}, Extra: {extra}" if not cluster_correct else f"Found exactly {clusters}"
    })
    if cluster_correct:
        score += 15

    # --- 6. Verify per-cluster costs (decimal arithmetic) ---
    # Pre-computed expected values using active catalog:
    # vcpu: 0.02 USD/unit, gpu: 0.50 USD/unit
    # ads-ranking: vcpu 1000 -> 20.00, gpu 50 -> 25.00 => total 45.00
    # retail-core: vcpu 2000 -> 40.00, gpu 0 -> 0.00 => total 40.00
    # grand total 85.00
    expected_clusters = {
        "ads-ranking": {"vcpu": Decimal("0.02") * 1000, "gpu": Decimal("0.50") * 50, "total": Decimal("45.00")},
        "retail-core": {"vcpu": Decimal("0.02") * 2000, "gpu": Decimal("0.00"), "total": Decimal("40.00")}
    }

    cluster_cost_ok = True
    cluster_cost_errors = []

    # Build a lookup by name
    cluster_map = {c.get("cluster_name"): c for c in clusters}

    for cname in ["ads-ranking", "retail-core"]:
        if cname not in cluster_map:
            cluster_cost_ok = False
            cluster_cost_errors.append(f"Missing cluster '{cname}'")
            continue
        c = cluster_map[cname]
        exp = expected_clusters[cname]
        # check total_cost
        try:
            total = Decimal(str(c.get("total_cost", 0))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except:
            total = Decimal("0")
        if total != exp["total"]:
            cluster_cost_ok = False
            cluster_cost_errors.append(f"{cname} total: expected {exp['total']}, got {total}")
        # check details
        details_obj = c.get("details", {})
        for metric in ["vcpu", "gpu"]:
            try:
                detail_val = Decimal(str(details_obj.get(metric, 0))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except:
                detail_val = Decimal("0")
            if detail_val != exp[metric]:
                cluster_cost_ok = False
                cluster_cost_errors.append(f"{cname} {metric}: expected {exp[metric]}, got {detail_val}")

    details.append({
        "item": "Per-cluster cost details (vcpu, gpu, total) match expected values",
        "score": 30 if cluster_cost_ok else 0,
        "max_score": 30,
        "passed": cluster_cost_ok,
        "reason": "All cluster costs correct" if cluster_cost_ok else "; ".join(cluster_cost_errors)
    })
    if cluster_cost_ok:
        score += 30

    # --- 7. Check grand total ---
    try:
        grand_total = Decimal(str(data.get("total_cost", 0))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except:
        grand_total = Decimal("0")
    grand_ok = grand_total == Decimal("85.00")
    details.append({
        "item": "total_cost equals 85.00 (sum of both clusters)",
        "score": 10 if grand_ok else 0,
        "max_score": 10,
        "passed": grand_ok,
        "reason": f"total_cost = {grand_total}" if grand_ok else f"Expected 85.00, got {grand_total}"
    })
    if grand_ok:
        score += 10

    # --- 8. Penalty for including extra fields or wrong data? (not needed, already covered) ---
    # Additional integrity: ensure no non-business clusters leaked
    # (already checked in cluster count, but we can add a small deduction if extra)
    # We'll trust the previous check.

    # Write final score
    write_score(score, details)

if __name__ == "__main__":
    main()
