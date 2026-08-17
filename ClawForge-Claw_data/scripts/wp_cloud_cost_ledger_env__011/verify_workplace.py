"""
Verify that the agent produced a correct monthly_cost_report.json
for the cloud_cost_ledger_env scenario based on business clusters
and the active pricing catalog.
"""
import json
import os
import sys

EXPECTED_REPORT = [
    {
        "cluster_id": "c01",
        "cluster_name": "ads-ranking",
        "total_compute_cost": 16.00,
        "total_storage_cost": 80.00
    },
    {
        "cluster_id": "c02",
        "cluster_name": "lakehouse-analytics",
        "total_compute_cost": 73.60,
        "total_storage_cost": 150.00
    }
]

def verify(workspace):
    details = []
    total_score = 0
    max_score = 100

    # 1. File exists (10 pts)
    report_path = os.path.join(workspace, "monthly_cost_report.json")
    if not os.path.isfile(report_path):
        details.append({"item": "report file exists", "score": 0, "max_score": 10, "passed": False,
                        "reason": "monthly_cost_report.json not found in workspace root"})
        # cannot proceed further, return zero
        return {"total_score": 0, "details": details}

    details.append({"item": "report file exists", "score": 10, "max_score": 10, "passed": True,
                    "reason": "file monthly_cost_report.json exists"})
    total_score += 10

    # 2. File is valid JSON (10 pts)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"invalid JSON: {e}"})
        return {"total_score": total_score, "details": details}
    details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True,
                    "reason": "file parses as valid JSON"})
    total_score += 10

    # 3. Structure: top-level key (e.g. "reports") or list directly? Accept either.
    # We expect a list of dicts with the four fields.
    # Let the agent choose; we'll check the content.
    if isinstance(data, list):
        reports = data
    elif isinstance(data, dict) and "reports" in data:
        reports = data["reports"]
    else:
        details.append({"item": "report structure", "score": 0, "max_score": 10, "passed": False,
                        "reason": "expected a list of reports or a dict with 'reports' key"})
        return {"total_score": total_score, "details": details}
    if not isinstance(reports, list) or len(reports) == 0:
        details.append({"item": "report structure", "score": 0, "max_score": 10, "passed": False,
                        "reason": "reports is not a non-empty list"})
        return {"total_score": total_score, "details": details}
    details.append({"item": "report structure", "score": 10, "max_score": 10, "passed": True,
                    "reason": "valid list of reports"})
    total_score += 10

    # 4. Number of business clusters (should be exactly 2) (15 pts)
    # We need to check only entries where cluster_role is business.
    # The agent may have included only business clusters; we'll compare to expected length.
    # But we cannot know from the report alone. Instead we count the number of reports.
    if len(reports) != 2:
        details.append({"item": "number of business clusters", "score": 0, "max_score": 15, "passed": False,
                        "reason": f"expected 2 reports (ads-ranking, lakehouse-analytics), got {len(reports)}"})
        total_score += 0  # don't add
    else:
        details.append({"item": "number of business clusters", "score": 15, "max_score": 15, "passed": True,
                        "reason": "exactly 2 cluster reports"})
        total_score += 15

    # 5. Check each expected cluster (25 pts for correct IDs/names, 30 pts for costs)
    # We'll build a dict from the reports for easy lookup
    report_map = {}
    for r in reports:
        cid = r.get("cluster_id")
        cname = r.get("cluster_name")
        comp = r.get("total_compute_cost")
        stor = r.get("total_storage_cost")
        if cid and cname:
            report_map[(cid, cname)] = (comp, stor)

    # 5a. Verify cluster IDs and names (15 pts)
    id_name_ok = True
    for exp in EXPECTED_REPORT:
        key = (exp["cluster_id"], exp["cluster_name"])
        if key not in report_map:
            id_name_ok = False
            break
    if id_name_ok:
        details.append({"item": "cluster ID and name match", "score": 15, "max_score": 15, "passed": True,
                        "reason": "both expected cluster IDs and names present"})
        total_score += 15
    else:
        details.append({"item": "cluster ID and name match", "score": 0, "max_score": 15, "passed": False,
                        "reason": "missing or mismatched cluster_id / cluster_name"})

    # 5b. Verify cost values (30 pts – 15 per cluster)
    cost_ok = True
    for exp in EXPECTED_REPORT:
        key = (exp["cluster_id"], exp["cluster_name"])
        if key not in report_map:
            cost_ok = False
            continue
        comp_actual, stor_actual = report_map[key]
        # Allow small floating point tolerance (2 decimals)
        if abs(comp_actual - exp["total_compute_cost"]) > 0.005 or abs(stor_actual - exp["total_storage_cost"]) > 0.005:
            cost_ok = False
            break
    if cost_ok:
        details.append({"item": "cost accuracy", "score": 30, "max_score": 30, "passed": True,
                        "reason": "compute and storage costs match expected values (within 0.01 tolerance)"})
        total_score += 30
    else:
        details.append({"item": "cost accuracy", "score": 0, "max_score": 30, "passed": False,
                        "reason": "one or more cost values deviate from expected"})

    # Final score
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
