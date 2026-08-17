import sys
import json
import os
import math

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check output directory and file existence (10 points)
    report_path = os.path.join(workspace, "output", "cost_report.json")
    if os.path.isfile(report_path):
        score_details.append({
            "item": "output/cost_report.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        total_score += 10
    else:
        score_details.append({
            "item": "output/cost_report.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found at 'output/cost_report.json'."
        })
        # Cannot proceed, return partial score
        _write_score(total_score, score_details)
        return

    # 2. JSON valid (10 points)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        score_details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully."
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        _write_score(total_score, score_details)
        return

    # 3. Required fields present (10 points)
    required_fields = ["report_month", "cluster_name", "total_cost", "currency", "details"]
    missing = [f for f in required_fields if f not in report]
    if not missing:
        score_details.append({
            "item": "Required fields present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required fields found."
        })
        total_score += 10
    else:
        score_details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing fields: {missing}"
        })

    # 4. Details structure and metric correctness (30 points)
    details = report.get("details", [])
    expected_metrics = {
        "vcpu": {"quantity": 10, "unit_price": 0.12, "billing_hours": 720},
        "gpu": {"quantity": 2, "unit_price": 0.50, "billing_hours": 720},
        "block_storage_gb": {"quantity": 100, "unit_price": 0.02, "billing_hours": 720},
        "object_storage_gb": {"quantity": 500, "unit_price": 0.01, "billing_hours": 720}
    }

    # Check that details is a list of dicts with metric_code, quantity, cost
    passed_detail_check = True
    reason_parts = []
    detail_map = {}
    for det in details:
        if not isinstance(det, dict) or "metric_code" not in det or "quantity" not in det or "cost" not in det:
            passed_detail_check = False
            reason_parts.append("Each detail must have metric_code, quantity, cost")
            break
        mc = det["metric_code"]
        detail_map[mc] = det

    if not passed_detail_check:
        score_details.append({
            "item": "Detail items structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })
        total_score += 0
    else:
        # Check that all expected metrics are present and no extras
        missing_metrics = set(expected_metrics.keys()) - set(detail_map.keys())
        extra_metrics = set(detail_map.keys()) - set(expected_metrics.keys())
        if missing_metrics or extra_metrics:
            score_details.append({
                "item": "Detail items completeness",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Missing metrics: {missing_metrics}, Extra metrics: {extra_metrics}"
            })
            total_score += 0
        else:
            # Check quantity and cost for each metric
            all_correct = True
            for mc, exp in expected_metrics.items():
                det = detail_map[mc]
                qty_ok = det["quantity"] == exp["quantity"]
                expected_cost = round(exp["quantity"] * exp["unit_price"] * exp["billing_hours"], 2)
                cost_ok = math.isclose(det["cost"], expected_cost, rel_tol=1e-6)
                if not qty_ok or not cost_ok:
                    all_correct = False
                    reason_parts.append(f"{mc}: qty={det['quantity']} (expected {exp['quantity']}), cost={det['cost']} (expected {expected_cost})")
            if all_correct:
                score_details.append({
                    "item": "Detail metric quantities and costs",
                    "score": 30,
                    "max_score": 30,
                    "passed": True,
                    "reason": "All metrics correct."
                })
                total_score += 30
            else:
                score_details.append({
                    "item": "Detail metric quantities and costs",
                    "score": 0,
                    "max_score": 30,
                    "passed": False,
                    "reason": "; ".join(reason_parts)
                })

    # 5. Total cost (30 points)
    expected_total = sum(exp["quantity"] * exp["unit_price"] * exp["billing_hours"] for exp in expected_metrics.values())
    expected_total = round(expected_total, 2)
    if math.isclose(report.get("total_cost", 0), expected_total, rel_tol=1e-6):
        score_details.append({
            "item": "Total cost accuracy",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"Total cost {report['total_cost']} matches expected {expected_total}."
        })
        total_score += 30
    else:
        score_details.append({
            "item": "Total cost accuracy",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Got {report.get('total_cost')}, expected {expected_total}."
        })

    # 6. Currency and month correctness (10 points)
    currency_ok = report.get("currency") == "USD"
    month_ok = report.get("report_month") == "2026-06"
    cluster_ok = report.get("cluster_name") == "ads-ranking"
    if currency_ok and month_ok and cluster_ok:
        score_details.append({
            "item": "Metadata fields (currency, month, cluster)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All metadata correct."
        })
        total_score += 10
    else:
        score_details.append({
            "item": "Metadata fields (currency, month, cluster)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"currency={report.get('currency')}, month={report.get('report_month')}, cluster={report.get('cluster_name')}"
        })

    total_score = min(total_score, 100)  # cap
    _write_score(total_score, score_details)

def _write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    verify()
