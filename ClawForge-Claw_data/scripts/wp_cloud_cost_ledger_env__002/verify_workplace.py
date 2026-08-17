import os
import sys
import json
import math

def get_decimal(value, places=2):
    """Round to fixed number of decimal places for comparison."""
    return round(value, places)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # ------------------------------------------------------------------
    # 1. Directory existence (10 pts)
    # ------------------------------------------------------------------
    ops_dir = os.path.join(workspace, "ops")
    ops_exists = os.path.isdir(ops_dir)
    score_details.append({
        "item": "ops/ directory exists",
        "score": 10 if ops_exists else 0,
        "max_score": 10,
        "passed": ops_exists,
        "reason": "ops/ found" if ops_exists else "ops/ not found"
    })
    if ops_exists:
        total_score += 10

    # ------------------------------------------------------------------
    # 2. Report file exists (10 pts)
    # ------------------------------------------------------------------
    report_path = os.path.join(ops_dir, "cluster_cost_report.json")
    report_exists = os.path.isfile(report_path)
    score_details.append({
        "item": "ops/cluster_cost_report.json exists",
        "score": 10 if report_exists else 0,
        "max_score": 10,
        "passed": report_exists,
        "reason": "file found" if report_exists else "file missing"
    })
    if report_exists:
        total_score += 10

    # ------------------------------------------------------------------
    # 3. JSON valid & mandatory fields (20 pts)
    # ------------------------------------------------------------------
    if not report_exists:
        score_details.append({
            "item": "JSON fields (cluster_name, month, total_cost, breakdown)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "file missing"
        })
        # Stop early, cannot proceed
        final_score = total_score
        result = {"total_score": final_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Score: {final_score}/100")
        sys.exit(0)

    try:
        with open(report_path, "r") as f:
            report = json.load(f)
    except json.JSONDecodeError as e:
        score_details.append({
            "item": "JSON valid & mandatory fields",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        final_score = total_score + 0
        result = {"total_score": final_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Score: {final_score}/100")
        sys.exit(0)

    required_fields = ["cluster_name", "month", "total_cost", "breakdown"]
    present = all(field in report for field in required_fields)
    if present:
        score_details.append({
            "item": "JSON fields (cluster_name, month, total_cost, breakdown)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All mandatory fields present"
        })
        total_score += 20
    else:
        missing = [f for f in required_fields if f not in report]
        score_details.append({
            "item": "JSON fields",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing fields: {missing}"
        })

    # ------------------------------------------------------------------
    # 4. Correct cluster_name and month (15 pts)
    # ------------------------------------------------------------------
    cluster_ok = report.get("cluster_name") == "ads-ranking"
    month_ok = report.get("month") == "2026-06"
    field_ok = cluster_ok and month_ok
    score_details.append({
        "item": "cluster_name = 'ads-ranking', month = '2026-06'",
        "score": 15 if field_ok else 0,
        "max_score": 15,
        "passed": field_ok,
        "reason": f"cluster={report.get('cluster_name')}, month={report.get('month')}" if not field_ok else "correct"
    })
    if field_ok:
        total_score += 15

    # ------------------------------------------------------------------
    # 5. Breakdown structure (10 pts)
    # ------------------------------------------------------------------
    breakdown = report.get("breakdown", {})
    if isinstance(breakdown, dict) and "compute" in breakdown and "storage" in breakdown:
        score_details.append({
            "item": "breakdown contains 'compute' and 'storage' keys",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "both families present"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "breakdown contains 'compute' and 'storage' keys",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"breakdown keys: {list(breakdown.keys()) if isinstance(breakdown, dict) else 'not a dict'}"
        })

    # ------------------------------------------------------------------
    # 6. Correct cost calculation (35 pts total)
    #    Known ground truth:
    #    vcpu: 24 * 0.05 * 720 = 864.0
    #    memory_gb: 256 * 0.01 * 720 = 1843.2
    #    block_storage_gb: 2000 * 0.0002 * 720 = 288.0
    #    object_storage_gb: 5000 * 0.0001 * 720 = 360.0
    #    compute total = 864.0 + 1843.2 = 2707.2
    #    storage total = 288.0 + 360.0 = 648.0
    #    grand total = 3355.2
    # ------------------------------------------------------------------
    expected_compute = 864.0 + 1843.2   # 2707.2
    expected_storage = 288.0 + 360.0     # 648.0
    expected_total = 3355.2

    breakdown_compute = breakdown.get("compute", None)
    breakdown_storage = breakdown.get("storage", None)
    total_cost = report.get("total_cost", None)

    compute_ok = isinstance(breakdown_compute, (int, float)) and math.isclose(breakdown_compute, expected_compute, rel_tol=1e-6)
    storage_ok = isinstance(breakdown_storage, (int, float)) and math.isclose(breakdown_storage, expected_storage, rel_tol=1e-6)
    total_ok = isinstance(total_cost, (int, float)) and math.isclose(total_cost, expected_total, rel_tol=1e-6)

    calc_ok = compute_ok and storage_ok and total_ok
    if calc_ok:
        score_details.append({
            "item": "Cost calculation (compute, storage, total) accurate",
            "score": 35,
            "max_score": 35,
            "passed": True,
            "reason": "All values match expected ground truth"
        })
        total_score += 35
    else:
        # Partial credit
        partial = 0
        reasons = []
        if compute_ok:
            partial += 15
        else:
            reasons.append(f"compute={breakdown_compute} (expected {expected_compute})")
        if storage_ok:
            partial += 10
        else:
            reasons.append(f"storage={breakdown_storage} (expected {expected_storage})")
        if total_ok:
            partial += 10
        else:
            reasons.append(f"total={total_cost} (expected {expected_total})")
        score_details.append({
            "item": "Cost calculation (compute, storage, total) accurate",
            "score": partial,
            "max_score": 35,
            "passed": partial == 35,
            "reason": "; ".join(reasons) if reasons else "partial (not all correct)"
        })
        total_score += partial

    # Ensure total_score is integer between 0 and 100
    final_score = min(100, max(0, total_score))

    result = {"total_score": final_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {final_score}/100")

if __name__ == "__main__":
    main()
