import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    score_details = []
    total_score = 0

    # 1. Reports directory exists (10 pts)
    reports_dir = os.path.join(workspace, "reports")
    dir_exists = os.path.isdir(reports_dir)
    score_details.append({
        "item": "reports directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Found reports/ directory" if dir_exists else "Missing reports/ directory"
    })
    if dir_exists:
        total_score += 10

    # 2. Report file exists (10 pts)
    report_path = os.path.join(reports_dir, "cost_report_2026_06.json")
    file_exists = os.path.isfile(report_path)
    score_details.append({
        "item": "report file cost_report_2026_06.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "Found cost_report_2026_06.json" if file_exists else "Missing cost_report_2026_06.json"
    })
    if file_exists:
        total_score += 10

    if not file_exists:
        # Cannot proceed further
        final_score = total_score
        _write_score(workspace, final_score, score_details)
        return

    # 3. JSON is valid (10 pts)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        json_valid = True
        reason = "Valid JSON"
    except (json.JSONDecodeError, Exception) as e:
        json_valid = False
        reason = f"Invalid JSON: {e}"
    score_details.append({
        "item": "report file is valid JSON",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    if json_valid:
        total_score += 10
    else:
        final_score = total_score
        _write_score(workspace, final_score, score_details)
        return

    # 4. Top-level fields (10 pts)
    has_report_month = isinstance(data, dict) and "report_month" in data
    has_clusters = isinstance(data, dict) and "clusters" in data and isinstance(data["clusters"], list)
    if not has_report_month or not has_clusters:
        score_details.append({
            "item": "top-level fields report_month and clusters",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing required top-level fields"
        })
    else:
        score_details.append({
            "item": "top-level fields report_month and clusters",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Has report_month and clusters"
        })
        total_score += 10

    if not has_report_month or not has_clusters:
        final_score = total_score
        _write_score(workspace, final_score, score_details)
        return

    if data["report_month"] != "2026-06":
        score_details[-1]["score"] = 0
        score_details[-1]["passed"] = False
        score_details[-1]["reason"] = f"report_month is '{data['report_month']}', expected '2026-06'"
        total_score -= 10  # revert the extra 10 we added

    # 5. Expected costs for each business cluster (15 each, 45 total)
    expected_costs = {
        "ads-ranking": 5493.20,
        "lakehouse-analytics": 10926.40,
        "retail-core": 7761.60
    }

    clusters_found = {}
    for entry in data["clusters"]:
        cid = entry.get("cluster_id")
        cost = entry.get("total_cost")
        if cid in expected_costs:
            clusters_found[cid] = cost

    for cluster_id, expected in expected_costs.items():
        found_cost = clusters_found.get(cluster_id)
        if found_cost is None:
            score_details.append({
                "item": f"cost for {cluster_id}",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Cluster {cluster_id} not found in report"
            })
        else:
            diff = abs(found_cost - expected)
            if diff < 0.01:
                score_details.append({
                    "item": f"cost for {cluster_id}",
                    "score": 15,
                    "max_score": 15,
                    "passed": True,
                    "reason": f"Correct: {found_cost}"
                })
                total_score += 15
            else:
                score_details.append({
                    "item": f"cost for {cluster_id}",
                    "score": 0,
                    "max_score": 15,
                    "passed": False,
                    "reason": f"Expected {expected}, got {found_cost}"
                })

    # 6. Grand total (15 pts)
    computed_total = sum(clusters_found.values()) if clusters_found else 0
    expected_total = sum(expected_costs.values())
    diff_total = abs(computed_total - expected_total)
    if diff_total < 0.02:
        score_details.append({
            "item": "grand total of all clusters",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"Correct total: {computed_total}"
        })
        total_score += 15
    else:
        score_details.append({
            "item": "grand total of all clusters",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Expected {expected_total}, got {computed_total}"
        })

    # Final score capped 0-100
    final_score = min(100, max(0, total_score))
    _write_score(workspace, final_score, score_details)

def _write_score(workspace, total, details):
    out_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total,
        "details": details
    }
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
