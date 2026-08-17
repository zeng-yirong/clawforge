import os
import sys
import csv
import json
from decimal import Decimal, ROUND_HALF_UP

def load_valid_pricing(base_dir):
    pricing_dir = os.path.join(base_dir, "data", "pricing")
    for fname in os.listdir(pricing_dir):
        if fname.endswith(".json"):
            fpath = os.path.join(pricing_dir, fname)
            with open(fpath) as f:
                catalog = json.load(f)
            if catalog.get("status") == "active" and catalog.get("approved_for_reporting") == True:
                rates = {}
                for r in catalog["rates"]:
                    rates[r["metric_code"]] = Decimal(str(r["unit_price"]))
                return rates
    return None

def compute_expected(base_dir):
    rates = load_valid_pricing(base_dir)
    if rates is None:
        return None, "No valid pricing catalog found"
    ledger_path = os.path.join(base_dir, "data", "resource_ledger.csv")
    if not os.path.isfile(ledger_path):
        return None, "resource_ledger.csv missing"
    
    costs = {}
    with open(ledger_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row["cluster_id"]
            cname = row["cluster_name"]
            metric = row["metric_code"]
            try:
                qty = int(row["quantity"])
            except ValueError:
                continue
            unit_price = rates.get(metric)
            if unit_price is None:
                continue
            cost = Decimal(qty) * unit_price
            key = (cid, cname)
            costs[key] = costs.get(key, Decimal('0')) + cost
    # round to 2 decimals
    expected = []
    for (cid, cname), total in costs.items():
        total_rounded = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        expected.append((cid, cname, str(total_rounded)))
    # sort by cluster_id for stable order
    expected.sort(key=lambda x: x[0])
    return expected, None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []  # list of dicts

    # 1. check reports/ directory exists
    reports_dir = os.path.join(workspace, "reports")
    dir_exists = os.path.isdir(reports_dir)
    results.append({
        "item": "reports/ directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Directory exists" if dir_exists else "Directory not found"
    })

    # 2. check cost_report.csv exists
    csv_path = os.path.join(reports_dir, "cost_report.csv")
    csv_exists = os.path.isfile(csv_path)
    results.append({
        "item": "reports/cost_report.csv exists",
        "score": 10 if csv_exists else 0,
        "max_score": 10,
        "passed": csv_exists,
        "reason": "File exists" if csv_exists else "File not found"
    })

    if not csv_exists:
        # cannot check further, fill zeros
        results.append({
            "item": "CSV header schema",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "No file to check"
        })
        results.append({
            "item": "Row count (expected 4 clusters)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "No file to check"
        })
        results.append({
            "item": "Per-cluster cost correctness",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "No file to check"
        })
        total = sum(r["score"] for r in results)
        out = {"total_score": total, "details": results}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(out, f, indent=2)
        return

    # 3. check CSV header
    with open(csv_path) as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            header = []
    expected_header = ["cluster_id", "cluster_name", "total_cost", "currency"]
    header_ok = header == expected_header
    results.append({
        "item": "CSV header schema",
        "score": 10 if header_ok else 0,
        "max_score": 10,
        "passed": header_ok,
        "reason": f"Header: {header}" if header_ok else f"Expected {expected_header}, got {header}"
    })

    # 4. parse rows and compare with expected
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    expected_data, err = compute_expected(workspace)
    if err:
        # cannot compute expected, give partial
        results.append({
            "item": "Row count (expected 4 clusters)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Could not compute expected: {err}"
        })
        results.append({
            "item": "Per-cluster cost correctness",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"Could not compute expected: {err}"
        })
    else:
        # row count check
        row_count_ok = len(rows) == len(expected_data)
        results.append({
            "item": "Row count (expected 4 clusters)",
            "score": 20 if row_count_ok else 0,
            "max_score": 20,
            "passed": row_count_ok,
            "reason": f"Rows: {len(rows)}" if row_count_ok else f"Expected {len(expected_data)} rows, got {len(rows)}"
        })

        # build lookup from agent rows
        agent_map = {}
        for r in rows:
            cid = r.get("cluster_id", "").strip()
            cname = r.get("cluster_name", "").strip()
            cost_str = r.get("total_cost", "").strip()
            currency = r.get("currency", "").strip()
            agent_map[(cid, cname)] = (cost_str, currency)

        # compare each expected
        cost_score = 0
        cost_max = 50
        per_item_max = 12  # 4 items * 12 = 48, plus 2 bonus for exact match? simpler: 50 distributed evenly
        per_item = cost_max // len(expected_data)  # 12 for 4 items
        remainder = cost_max % len(expected_data)  # 2
        passed_items = 0
        for idx, (ecid, ecname, ecost) in enumerate(expected_data):
            expected_currency = "USD"  # from pricing catalog
            key = (ecid, ecname)
            agent_val = agent_map.get(key)
            if agent_val is None:
                # try matching only by cluster_id? require both match
                reason = f"Cluster {ecid}/{ecname} not found in agent output"
                cost_score += 0
                continue
            agent_cost_str, agent_currency = agent_val
            cost_ok = agent_cost_str == ecost and agent_currency == expected_currency
            if cost_ok:
                passed_items += 1
                cost_score += per_item + (1 if idx < remainder else 0)  # distribute remainder to first items
            # else no score
        cost_score = min(cost_score, cost_max)  # cap
        results.append({
            "item": "Per-cluster cost correctness",
            "score": cost_score,
            "max_score": cost_max,
            "passed": cost_score == cost_max,
            "reason": f"Accurate clusters: {passed_items}/{len(expected_data)}"
        })

    total = sum(r["score"] for r in results)
    out = {"total_score": total, "details": results}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
