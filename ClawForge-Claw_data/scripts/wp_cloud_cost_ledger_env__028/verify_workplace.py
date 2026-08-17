import json
import os
import sys

def verify(workspace):
    errors = []
    details = []
    total_score = 0
    max_total = 100

    # ----- item 1: output directory exists (10 points) -----
    op_dir = os.path.join(workspace, "ops")
    if os.path.isdir(op_dir):
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing"
        })

    # ----- item 2: output file exists (10 points) -----
    report_path = os.path.join(workspace, "ops/corrected_cost_report.json")
    if os.path.isfile(report_path):
        details.append({
            "item": "output file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/corrected_cost_report.json found"
        })
        total_score += 10
    else:
        details.append({
            "item": "output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/corrected_cost_report.json missing"
        })
        # cannot proceed with further checks
        details.append({
            "item": "JSON valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file missing"
        })
        details.append({
            "item": "content structure",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "file missing"
        })
        details.append({
            "item": "cost accuracy",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "file missing"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        print(f"Total: {total_score}/100")
        return

    # ----- item 3: JSON is valid and is an array (10 points) -----
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({
                "item": "JSON valid and array",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "valid JSON, top-level list"
            })
            total_score += 10
        else:
            details.append({
                "item": "JSON valid and array",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"top-level is {type(data).__name__}, expected list"
            })
    except Exception as e:
        details.append({
            "item": "JSON valid and array",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        # abort further checks
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        print(f"Total: {total_score}/100")
        return

    # ----- item 4: each object has required fields and correct cluster_ids (20 points) -----
    required_fields = {"cluster_id", "total_cost"}
    expected_cluster_ids = {"c_ads_01", "c_retail_02"}  # only business clusters
    found_ids = set()
    structure_ok = True
    for item in data:
        if not isinstance(item, dict):
            structure_ok = False
            break
        if not required_fields.issubset(item.keys()):
            structure_ok = False
            break
        if not isinstance(item["total_cost"], (int, float)):
            structure_ok = False
            break
        found_ids.add(item["cluster_id"])
    # Check no extra cluster
    if found_ids != expected_cluster_ids:
        structure_ok = False
    if structure_ok:
        details.append({
            "item": "content structure",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Exactly two entries for {expected_cluster_ids} with required fields"
        })
        total_score += 20
    else:
        details.append({
            "item": "content structure",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Found cluster_ids: {found_ids}, expected {expected_cluster_ids} or structure violation"
        })

    # ----- item 5: cost calculation accuracy (50 points) -----
    # Compute expected costs manually: only active pricing catalog (pc_2026_06_live) for business clusters
    # Read pricing catalog from workspace
    with open(os.path.join(workspace, "data/pricing/pricing_catalogs.json")) as f:
        pc_data = json.load(f)["pricing_catalogs"]
    live_catalog = None
    for cat in pc_data:
        if cat["status"] == "active" and cat["billing_month"] == "2026-06":
            live_catalog = cat
            break
    if live_catalog is None:
        details.append({
            "item": "cost accuracy",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "Could not find active June 2026 pricing catalog in environment"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        print(f"Total: {total_score}/100")
        return

    # Build rate lookup
    rates = {}
    for r in live_catalog["rates"]:
        rates[r["metric_code"]] = r["unit_price"]

    # Read resource ledger
    with open(os.path.join(workspace, "data/resources/resource_ledger.json")) as f:
        ledger_data = json.load(f)["resource_ledger"]

    # Read clusters to get business cluster_ids
    with open(os.path.join(workspace, "data/resources/clusters.json")) as f:
        cluster_data = json.load(f)["clusters"]
    business_cluster_ids = set()
    for cl in cluster_data:
        if cl["cluster_role"] == "business":
            business_cluster_ids.add(cl["cluster_id"])

    # Compute expected cost per business cluster
    expected_costs = {}
    for entry in ledger_data:
        cid = entry.get("cluster_id")
        if cid not in business_cluster_ids:
            continue
        # Exclude entries with negative quantity, missing metric_code, missing resource_family
        qty = entry.get("quantity")
        if qty is None or (isinstance(qty, (int, float)) and qty <= 0):
            continue
        if not entry.get("metric_code") or not entry.get("resource_family"):
            continue
        mcode = entry["metric_code"]
        if mcode not in rates:
            continue
        cost = qty * rates[mcode]
        expected_costs[cid] = expected_costs.get(cid, 0.0) + cost

    # Round to two decimals
    expected_costs = {k: round(v, 2) for k, v in expected_costs.items()}

    # Compare
    accuracy_ok = True
    reason_parts = []
    for item in data:
        cid = item["cluster_id"]
        got = round(item["total_cost"], 2)
        exp = expected_costs.get(cid)
        if exp is None:
            accuracy_ok = False
            reason_parts.append(f"Unexpected cluster {cid}")
        elif abs(got - exp) > 0.01:
            accuracy_ok = False
            reason_parts.append(f"{cid}: got {got}, expected {exp}")
        else:
            reason_parts.append(f"{cid}: correct ({got})")
    # Check if any expected cluster missing
    for cid in expected_costs:
        if cid not in [it["cluster_id"] for it in data]:
            accuracy_ok = False
            reason_parts.append(f"Missing cluster {cid}")

    if accuracy_ok:
        details.append({
            "item": "cost accuracy",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": "; ".join(reason_parts)
        })
        total_score += 50
    else:
        details.append({
            "item": "cost accuracy",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })

    # Write final score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Total: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
