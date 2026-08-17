import sys
import json
import os
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = pathlib.Path(workspace)
    score_file = workspace / "workplace_score.json"
    details = []
    total_score = 0

    # 1) Check that output/cost_report.json exists (5 points)
    report_path = workspace / "output" / "cost_report.json"
    if report_path.exists():
        details.append({"item": "Report file exists", "score": 5, "max_score": 5, "passed": True, "reason": "output/cost_report.json found"})
        total_score += 5
    else:
        details.append({"item": "Report file exists", "score": 0, "max_score": 5, "passed": False, "reason": "output/cost_report.json missing"})
        # Cannot proceed further
        with open(score_file, "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 2) Parse JSON and check validity (5 points)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        details.append({"item": "JSON is valid", "score": 5, "max_score": 5, "passed": True, "reason": "Parsed successfully"})
        total_score += 5
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 5, "passed": False, "reason": f"Invalid JSON: {e}"})
        with open(score_file, "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 3) Check required top-level fields (10 points)
    required_fields = ["cluster_name", "billing_month", "currency", "catalog_id", "total_cost", "details"]
    missing = [f for f in required_fields if f not in report]
    if missing:
        details.append({"item": "Required fields present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields: {missing}"})
    else:
        details.append({"item": "Required fields present", "score": 10, "max_score": 10, "passed": True, "reason": "All required fields found"})
        total_score += 10

    # 4) Check cluster_name is "ads-ranking" (10 points)
    if report.get("cluster_name") == "ads-ranking":
        details.append({"item": "Correct cluster", "score": 10, "max_score": 10, "passed": True, "reason": "cluster_name = ads-ranking"})
        total_score += 10
    else:
        details.append({"item": "Correct cluster", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected ads-ranking, got {report.get('cluster_name')}"})

    # 5) Check billing_month is "2026-06" (5 points)
    if report.get("billing_month") == "2026-06":
        details.append({"item": "Correct billing month", "score": 5, "max_score": 5, "passed": True, "reason": "billing_month = 2026-06"})
        total_score += 5
    else:
        details.append({"item": "Correct billing month", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected 2026-06, got {report.get('billing_month')}"})

    # 6) Check currency is "USD" (5 points)
    if report.get("currency") == "USD":
        details.append({"item": "Correct currency", "score": 5, "max_score": 5, "passed": True, "reason": "currency = USD"})
        total_score += 5
    else:
        details.append({"item": "Correct currency", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected USD, got {report.get('currency')}"})

    # 7) Check catalog_id is the active one: "cat_2026_06_live" (5 points)
    if report.get("catalog_id") == "cat_2026_06_live":
        details.append({"item": "Active catalog used", "score": 5, "max_score": 5, "passed": True, "reason": "catalog_id = cat_2026_06_live"})
        total_score += 5
    else:
        details.append({"item": "Active catalog used", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected cat_2026_06_live, got {report.get('catalog_id')}"})

    # 8) Validate total_cost (50 points) – must be 124.32 (allow float tolerance 0.005)
    expected_cost = 124.32
    actual_cost = report.get("total_cost")
    if isinstance(actual_cost, (int, float)) and abs(actual_cost - expected_cost) < 0.005:
        details.append({"item": "Correct total cost", "score": 50, "max_score": 50, "passed": True, "reason": f"total_cost = {actual_cost:.2f}"})
        total_score += 50
    else:
        details.append({"item": "Correct total cost", "score": 0, "max_score": 50, "passed": False, "reason": f"Expected ~124.32, got {actual_cost}"})

    # 9) Validate that dirty data was excluded (5 points)
    #   The report's details list should contain exactly 5 entries (only valid ads-ranking ones)
    #   and no entry with erroneous metric_codes or zero/negative quantities.
    details_list = report.get("details", [])
    if isinstance(details_list, list) and len(details_list) == 5:
        # Check that none of the entries have metric_code "storage_gb" or quantity <= 0
        clean = True
        for entry in details_list:
            mc = entry.get("metric_code", "")
            qty = entry.get("quantity", 1)
            if mc == "storage_gb" or qty <= 0:
                clean = False
                break
        if clean:
            details.append({"item": "Dirty data excluded", "score": 5, "max_score": 5, "passed": True, "reason": "Details contain 5 clean entries"})
            total_score += 5
        else:
            details.append({"item": "Dirty data excluded", "score": 0, "max_score": 5, "passed": False, "reason": "Found invalid metric or non-positive quantity in details"})
    else:
        details.append({"item": "Dirty data excluded", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected 5 detail entries, got {len(details_list) if isinstance(details_list, list) else 'non-list'}"})

    # Write score
    score_dict = {"total_score": total_score, "details": details}
    with open(score_file, "w") as f:
        json.dump(score_dict, f)

if __name__ == "__main__":
    main()
