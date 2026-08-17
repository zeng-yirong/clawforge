import json, os, sys, math

def verify(workspace):
    details = []
    total_score = 0

    # ----- 1. Directory and file existence -----
    # Required: reports/ads_june_cost.json
    required_file = os.path.join(workspace, "reports", "ads_june_cost.json")
    if not os.path.isfile(required_file):
        details.append({
            "item": "reports/ads_june_cost.json exists",
            "score": 0, "max_score": 10, "passed": False,
            "reason": "File not found at 'reports/ads_june_cost.json'."
        })
        total_score += 0
        # If file missing, further checks are impossible; return early.
        final_score = 0
        write_score(details, final_score)
        return

    details.append({
        "item": "reports/ads_june_cost.json exists",
        "score": 10, "max_score": 10, "passed": True,
        "reason": "File present."
    })
    total_score += 10

    # ----- 2. JSON parsing -----
    try:
        with open(required_file, "r") as f:
            report = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "Valid JSON",
            "score": 0, "max_score": 10, "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        write_score(details, total_score)
        return
    details.append({
        "item": "Valid JSON",
        "score": 10, "max_score": 10, "passed": True,
        "reason": "JSON parsed successfully."
    })
    total_score += 10

    # ----- 3. Required fields present -----
    required_fields = ["cluster", "month", "compute_cost", "storage_cost", "total_cost", "currency"]
    missing = [f for f in required_fields if f not in report]
    if missing:
        details.append({
            "item": "Required fields present",
            "score": 0, "max_score": 15, "passed": False,
            "reason": f"Missing fields: {', '.join(missing)}"
        })
        write_score(details, total_score)
        return
    details.append({
        "item": "Required fields present",
        "score": 15, "max_score": 15, "passed": True,
        "reason": "All fields (cluster, month, compute_cost, storage_cost, total_cost, currency) found."
    })
    total_score += 15

    # ----- 4. Field value correctness (cluster, month, currency) -----
    cluster_ok = report.get("cluster") == "ads-ranking"
    month_ok = report.get("month") == "2026-06"
    currency_ok = report.get("currency") == "USD"
    if not (cluster_ok and month_ok and currency_ok):
        failures = []
        if not cluster_ok: failures.append(f"cluster expected 'ads-ranking' got '{report.get('cluster')}'")
        if not month_ok: failures.append(f"month expected '2026-06' got '{report.get('month')}'")
        if not currency_ok: failures.append(f"currency expected 'USD' got '{report.get('currency')}'")
        details.append({
            "item": "Cluster, month, currency correct",
            "score": 0, "max_score": 15, "passed": False,
            "reason": "; ".join(failures)
        })
        write_score(details, total_score)
        return
    details.append({
        "item": "Cluster, month, currency correct",
        "score": 15, "max_score": 15, "passed": True,
        "reason": "cluster='ads-ranking', month='2026-06', currency='USD'."
    })
    total_score += 15

    # ----- 5. Cost calculation correctness -----
    # Expected values based on env_builder data:
    # vcpu: 10 * 720 * 0.12 = 864.0
    # memory_gb: 64 * 720 * 0.02 = 921.6
    # compute_cost = 864.0 + 921.6 = 1785.6
    # block_storage_gb: 500 * 720 * 0.08 = 28800.0
    # total_cost = 1785.6 + 28800.0 = 30585.6
    expected_compute = 1785.6
    expected_storage = 28800.0
    expected_total = 30585.6

    # Allow small floating point tolerance (0.01)
    def approx(a, b, eps=0.01):
        return abs(a - b) < eps

    compute_pass = approx(report.get("compute_cost", -1), expected_compute)
    storage_pass = approx(report.get("storage_cost", -1), expected_storage)
    total_pass = approx(report.get("total_cost", -1), expected_total)

    cost_items = []
    if not compute_pass:
        cost_items.append(f"compute_cost: got {report.get('compute_cost')}, expected {expected_compute}")
    if not storage_pass:
        cost_items.append(f"storage_cost: got {report.get('storage_cost')}, expected {expected_storage}")
    if not total_pass:
        cost_items.append(f"total_cost: got {report.get('total_cost')}, expected {expected_total}")

    if cost_items:
        details.append({
            "item": "Cost values correct",
            "score": 0, "max_score": 50, "passed": False,
            "reason": "; ".join(cost_items)
        })
        write_score(details, total_score)
        return

    details.append({
        "item": "Cost values correct",
        "score": 50, "max_score": 50, "passed": True,
        "reason": f"compute_cost={expected_compute}, storage_cost={expected_storage}, total_cost={expected_total}"
    })
    total_score += 50

    # ----- All checks passed -----
    write_score(details, total_score)

def write_score(details, total_score):
    # Cap at 100
    final_score = min(total_score, 100)
    result = {
        "total_score": final_score,
        "details": details
    }
    out_path = os.path.join(workspace if workspace else ".", "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {final_score}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
