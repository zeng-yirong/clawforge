import os
import sys
import json
import math

def verify(workspace):
    details = []
    total_score = 0

    # ------------------------------------------------------------
    # item 1: File existence
    # ------------------------------------------------------------
    report_path = os.path.join(workspace, "cost_report.json")
    if os.path.isfile(report_path):
        details.append({
            "item": "cost_report.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        total_score += 10
    else:
        # Cannot proceed without file, return early
        details.append({
            "item": "cost_report.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ------------------------------------------------------------
    # item 2: Valid JSON
    # ------------------------------------------------------------
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "cost_report.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully."
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "cost_report.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ------------------------------------------------------------
    # item 3: cluster_id field
    # ------------------------------------------------------------
    if isinstance(data, dict) and data.get("cluster_id") == "retail-core":
        details.append({
            "item": "cluster_id is 'retail-core'",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct cluster ID."
        })
        total_score += 10
    else:
        details.append({
            "item": "cluster_id is 'retail-core'",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 'retail-core', got {data.get('cluster_id')}."
        })

    # ------------------------------------------------------------
    # item 4: billing_month field
    # ------------------------------------------------------------
    if isinstance(data, dict) and data.get("billing_month") == "2026-06":
        details.append({
            "item": "billing_month is '2026-06'",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct billing month."
        })
        total_score += 10
    else:
        details.append({
            "item": "billing_month is '2026-06'",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected '2026-06', got {data.get('billing_month')}."
        })

    # ------------------------------------------------------------
    # item 5: catalog_id field
    # ------------------------------------------------------------
    if isinstance(data, dict) and data.get("catalog_id") == "cp-2026-06":
        details.append({
            "item": "catalog_id is 'cp-2026-06' (active June catalog)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Correct catalog ID."
        })
        total_score += 15
    else:
        details.append({
            "item": "catalog_id is 'cp-2026-06' (active June catalog)",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Expected 'cp-2026-06', got {data.get('catalog_id')}."
        })

    # ------------------------------------------------------------
    # item 6: total_cost field exists and is numeric
    # ------------------------------------------------------------
    total_cost = data.get("total_cost")
    if isinstance(total_cost, (int, float)):
        details.append({
            "item": "total_cost field exists and is numeric",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "total_cost is present."
        })
        total_score += 15
    else:
        details.append({
            "item": "total_cost field exists and is numeric",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"total_cost missing or non-numeric: {total_cost}."
        })
        # cannot check value, skip next item
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # ------------------------------------------------------------
    # item 7: exact total_cost value (2142.40)
    # ------------------------------------------------------------
    # Expected: 16 vcpu * 720h * 0.12 = 1382.40
    #           2 gpu * 720h * 0.50 = 720.00
    #           500 GiB * 0.08 = 40.00
    # Sum = 2142.40
    expected = 2142.40
    rounded = round(float(total_cost), 2)
    if math.isclose(rounded, expected, rel_tol=1e-9):
        details.append({
            "item": "total_cost equals 2142.40 (USD, two decimals)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"Computed {rounded} matches expected {expected}."
        })
        total_score += 30
    else:
        details.append({
            "item": "total_cost equals 2142.40 (USD, two decimals)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Got {rounded}, expected {expected}."
        })

    # ------------------------------------------------------------
    # write score
    # ------------------------------------------------------------
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
