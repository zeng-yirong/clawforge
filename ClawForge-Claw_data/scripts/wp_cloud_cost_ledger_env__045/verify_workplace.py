import sys
import json
import os
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(workspace, rel_path)
    if not os.path.exists(full):
        return None
    with open(full) as f:
        return json.load(f)

def compute_expected():
    clusters = load_json("data/clusters.json")
    pricing = load_json("data/pricing_catalogs.json")
    ledger = load_json("data/resource_ledger.json")
    if not all([clusters, pricing, ledger]):
        return None

    # active pricing catalog
    active = None
    for pc in pricing.get("pricing_catalogs", []):
        if pc.get("status") == "active":
            active = pc
            break
    if active is None:
        return None
    hours = active.get("billing_hours", 720)
    rates = {}
    for r in active.get("rates", []):
        rates[(r["resource_family"], r["metric_code"])] = r["unit_price"]

    # business cluster IDs
    business_ids = {c["cluster_id"] for c in clusters.get("clusters", [])
                    if c.get("cluster_role") == "business"}

    # accumulate cost per business cluster, ignoring zero/negative quantity
    expected = {}
    for entry in ledger.get("resource_ledger", []):
        cid = entry.get("cluster_id")
        if cid not in business_ids:
            continue
        qty = entry.get("quantity", 0)
        if qty <= 0:
            continue
        key = (entry.get("resource_family"), entry.get("metric_code"))
        if key not in rates:
            continue
        cost = qty * rates[key] * hours
        expected[cid] = expected.get(cid, 0.0) + cost

    for cid in expected:
        expected[cid] = round(expected[cid], 2)
    return expected

def main():
    details = []
    total_score = 0

    # ── 1. Directory structure (10) ──
    # 1a. ops directory exists (5)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "found" if dir_exists else "not found"
    })
    total_score += 5 if dir_exists else 0

    # 1b. cost_report.json exists (5)
    report_path = os.path.join(workspace, "ops", "cost_report.json")
    file_exists = os.path.isfile(report_path)
    details.append({
        "item": "cost_report.json exists",
        "score": 5 if file_exists else 0,
        "max_score": 5,
        "passed": file_exists,
        "reason": "found" if file_exists else "not found"
    })
    total_score += 5 if file_exists else 0

    # ── 2. Format legality (10) ──
    report = None
    format_ok = False
    try:
        with open(report_path) as f:
            report = json.load(f)
        format_ok = True
    except:
        pass
    # 2a. valid JSON (5)
    details.append({
        "item": "valid JSON",
        "score": 5 if format_ok else 0,
        "max_score": 5,
        "passed": format_ok,
        "reason": "parsed successfully" if format_ok else "parse error"
    })
    total_score += 5 if format_ok else 0

    # 2b. top-level is list (5)
    is_list = isinstance(report, list)
    if not is_list and isinstance(report, dict) and "clusters" in report:
        report = report["clusters"]
        is_list = True
    details.append({
        "item": "top-level is array (or clusters key with array)",
        "score": 5 if is_list else 0,
        "max_score": 5,
        "passed": is_list,
        "reason": "is array" if is_list else "not array"
    })
    total_score += 5 if is_list else 0

    # ── 3. Field completeness (20) ──
    # build map: cluster_id -> total_cost from report
    report_map = {}
    if isinstance(report, list):
        for item in report:
            if isinstance(item, dict) and "cluster_id" in item and "total_cost" in item:
                cid = item["cluster_id"]
                try:
                    cost = float(item["total_cost"])
                    if cid not in report_map:   # only first occurrence
                        report_map[cid] = cost
                except:
                    pass

    expected = compute_expected()
    expected_business = ["ads-ranking", "retail-core", "lakehouse-analytics"]
    field_score = 0
    missing = []
    for cid in expected_business:
        if cid in report_map:
            field_score += 5
        else:
            missing.append(cid)
    # penalty if shared-ops appears
    if "shared-ops" not in report_map:
        field_score += 5
    else:
        field_score += 0  # no point for this part
    details.append({
        "item": "field completeness (business clusters present, no shared-ops)",
        "score": field_score,
        "max_score": 20,
        "passed": field_score == 20,
        "reason": f"missing: {missing}, shared-ops found: {'shared-ops' in report_map}"
    })
    total_score += field_score

    # ── 4. Cost accuracy (60) ──
    accuracy_score = 0
    if expected is not None:
        for cid in expected_business:
            exp_val = expected.get(cid, 0.0)
            if cid in report_map:
                act_val = report_map[cid]
                if isinstance(act_val, (int, float)) and math.isclose(act_val, exp_val, abs_tol=0.01):
                    accuracy_score += 20
                    details.append({
                        "item": f"cost accuracy for {cid}",
                        "score": 20,
                        "max_score": 20,
                        "passed": True,
                        "reason": f"expected {exp_val}, got {act_val}"
                    })
                else:
                    details.append({
                        "item": f"cost accuracy for {cid}",
                        "score": 0,
                        "max_score": 20,
                        "passed": False,
                        "reason": f"expected {exp_val}, got {act_val}"
                    })
            else:
                details.append({
                    "item": f"cost accuracy for {cid}",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": "cluster missing in report"
                })
        total_score += accuracy_score
    else:
        # cannot compute expected – give 0 for this section
        details.append({
            "item": "cost accuracy (all clusters)",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "could not compute expected costs from source data"
        })

    # write score file
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
