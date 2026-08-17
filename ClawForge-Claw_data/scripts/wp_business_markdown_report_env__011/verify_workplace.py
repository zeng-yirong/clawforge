import sys
import os
import re
import json

def verify(workspace):
    result = {"total_score": 0, "details": []}
    score = 0
    max_score = 100

    # 1) Check report file exists
    report_path = os.path.join(workspace, "reports", "monthly_summary.md")
    if not os.path.isfile(report_path):
        result["details"].append({
            "item": "Report file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "reports/monthly_summary.md not found"
        })
        # no further checks possible
        result["total_score"] = 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return

    result["details"].append({
        "item": "Report file exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "reports/monthly_summary.md found"
    })
    score += 10

    # 2) Check title
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    title_pattern = r"#\s*Monthly Summary \(2025-01\)"
    if re.search(title_pattern, content):
        result["details"].append({
            "item": "Title correct",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Title '# Monthly Summary (2025-01)' found"
        })
        score += 10
    else:
        result["details"].append({
            "item": "Title correct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Expected title '# Monthly Summary (2025-01)' not found"
        })

    # 3) Extract key-value pairs from list items
    # Pattern: - **any text**: digits
    pattern = r"-\s*\*\*([^*]+)\*\*:\s*(\d+)"
    matches = re.findall(pattern, content)
    # Normalise metric names: lowercase, strip
    extracted = {}
    for name, value in matches:
        key = name.strip().lower()
        extracted[key] = int(value)

    # Expected metrics (case-insensitive)
    expected = {
        "active customers": 125,
        "product count": 80,
        "revenue": 45000
    }
    metrics_score = 0
    metrics_max = 80  # 3 items, roughly 26.67 each, round to integer
    # We'll assign 27 for each correct, but total 80 -> 27+27+26 = 80
    # To be simple: each correct metric = 27, but keep total 80.
    metric_weights = {
        "active customers": 27,
        "product count": 27,
        "revenue": 26
    }
    for metric_name, expected_val in expected.items():
        if metric_name in extracted:
            if extracted[metric_name] == expected_val:
                metrics_score += metric_weights[metric_name]
                result["details"].append({
                    "item": f"Metric '{metric_name}' correct",
                    "score": metric_weights[metric_name],
                    "max_score": metric_weights[metric_name],
                    "passed": True,
                    "reason": f"Found value {extracted[metric_name]} matches expected {expected_val}"
                })
            else:
                result["details"].append({
                    "item": f"Metric '{metric_name}' value wrong",
                    "score": 0,
                    "max_score": metric_weights[metric_name],
                    "passed": False,
                    "reason": f"Found value {extracted[metric_name]}, expected {expected_val}"
                })
        else:
            result["details"].append({
                "item": f"Metric '{metric_name}' missing",
                "score": 0,
                "max_score": metric_weights[metric_name],
                "passed": False,
                "reason": f"Metric not found in report"
            })
    score += metrics_score

    # 4) Final total
    result["total_score"] = min(score, 100)  # cap at 100

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
