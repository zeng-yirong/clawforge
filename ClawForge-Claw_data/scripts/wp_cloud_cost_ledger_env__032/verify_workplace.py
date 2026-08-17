import sys, json, os, math
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    wp = Path(workspace)
    scores = []

    # 1. Report file existence
    report_path = wp / "ops" / "cost_report.json"
    if not report_path.exists():
        scores.append({"item": "Report file existence", "score": 0, "max_score": 10,
                       "passed": False, "reason": "ops/cost_report.json not found"})
        total = sum(s["score"] for s in scores)
        with open(wp / "workplace_score.json", "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        return
    scores.append({"item": "Report file existence", "score": 10, "max_score": 10,
                   "passed": True, "reason": "File exists"})

    # 2. JSON validity
    try:
        with open(report_path) as f:
            report = json.load(f)
        scores.append({"item": "JSON format valid", "score": 10, "max_score": 10,
                       "passed": True, "reason": "Valid JSON"})
    except Exception as e:
        scores.append({"item": "JSON format valid", "score": 0, "max_score": 10,
                       "passed": False, "reason": f"Invalid JSON: {e}"})
        total = sum(s["score"] for s in scores)
        with open(wp / "workplace_score.json", "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        return

    # 3. cluster_name
    cluster_name = report.get("cluster_name")
    if cluster_name == "ads-ranking":
        scores.append({"item": "cluster_name", "score": 10, "max_score": 10,
                       "passed": True, "reason": "Correct cluster"})
    else:
        scores.append({"item": "cluster_name", "score": 0, "max_score": 10,
                       "passed": False, "reason": f"Expected ads-ranking, got {cluster_name}"})

    # 4. billing_month
    billing_month = report.get("billing_month")
    if billing_month == "2026-06":
        scores.append({"item": "billing_month", "score": 10, "max_score": 10,
                       "passed": True, "reason": "Correct month"})
    else:
        scores.append({"item": "billing_month", "score": 0, "max_score": 10,
                       "passed": False, "reason": f"Expected 2026-06, got {billing_month}"})

    # 5. items count (must be exactly 4 for ads‑ranking: gpu-monthly, vcpu-autoscale, block_reserved, gpu-autoscale)
    items = report.get("items")
    if not isinstance(items, list):
        scores.append({"item": "items count", "score": 0, "max_score": 10,
                       "passed": False, "reason": "items is not a list"})
    else:
        if len(items) == 4:
            scores.append({"item": "items count", "score": 10, "max_score": 10,
                           "passed": True, "reason": "Exactly 4 items"})
        else:
            scores.append({"item": "items count", "score": 0, "max_score": 10,
                           "passed": False, "reason": f"Expected 4 items, got {len(items)}"})

    # 6. total_cost (calculated: 8*3.75 + 64*0.12 + 5000*0.09 + 2*4.25 = 30.0 + 7.68 + 450.0 + 8.5 = 496.18)
    expected_total = 496.18
    total_cost = report.get("total_cost")
    if total_cost is None:
        scores.append({"item": "total_cost accuracy", "score": 0, "max_score": 30,
                       "passed": False, "reason": "total_cost missing"})
    else:
        if math.isclose(total_cost, expected_total, rel_tol=1e-5, abs_tol=0.01):
            scores.append({"item": "total_cost accuracy", "score": 30, "max_score": 30,
                           "passed": True, "reason": f"Total cost {total_cost} matches expected"})
        else:
            scores.append({"item": "total_cost accuracy", "score": 0, "max_score": 30,
                           "passed": False, "reason": f"Expected {expected_total}, got {total_cost}"})

    # 7. items sum self‑consistency
    if isinstance(items, list) and len(items) > 0:
        sum_items = sum(item.get("cost", 0) for item in items)
        if math.isclose(sum_items, total_cost, rel_tol=1e-5, abs_tol=0.01):
            scores.append({"item": "items sum consistency", "score": 20, "max_score": 20,
                           "passed": True, "reason": "Items sum matches total_cost"})
        else:
            scores.append({"item": "items sum consistency", "score": 0, "max_score": 20,
                           "passed": False, "reason": f"Sum of items {sum_items} != total_cost {total_cost}"})
    else:
        scores.append({"item": "items sum consistency", "score": 0, "max_score": 20,
                       "passed": False, "reason": "No items to sum"})

    # Final score
    total_score = sum(s["score"] for s in scores)
    with open(wp / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": scores}, f, indent=2)

if __name__ == "__main__":
    main()
