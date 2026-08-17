import json
import os
import sys
from pathlib import Path

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workpath = Path(workspace)

    details = []
    total_score = 0

    # ------------------------------------------------------------
    # 1. Check reports directory and report file existence (10 pts)
    # ------------------------------------------------------------
    report_path = workpath / "reports" / "2026-06-cost-report.json"
    report_exists = report_path.is_file()
    details.append({
        "item": "Report file exists",
        "score": 10 if report_exists else 0,
        "max_score": 10,
        "passed": report_exists,
        "reason": "File found" if report_exists else "Missing reports/2026-06-cost-report.json"
    })
    total_score += 10 if report_exists else 0

    if not report_exists:
        # Early exit if file missing; other checks would fail
        result = {"total_score": total_score, "details": details}
        with open(workpath / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # ------------------------------------------------------------
    # 2. Report JSON validity and required fields (10 pts)
    # ------------------------------------------------------------
    try:
        report = load_json(report_path)
        required_fields = ["report_month", "generated_at", "clusters", "total_cost"]
        cluster_fields = ["cluster_id", "cluster_name", "compute_cost", "storage_cost", "total_cost"]
        missing = [f for f in required_fields if f not in report]
        if not missing and isinstance(report["clusters"], list):
            cluster_ok = True
            for c in report["clusters"]:
                if not all(k in c for k in cluster_fields):
                    cluster_ok = False
                    break
            if cluster_ok:
                details.append({
                    "item": "Report JSON format and required fields",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "All required fields present"
                })
                total_score += 10
            else:
                details.append({
                    "item": "Report JSON format and required fields",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "Missing fields in cluster objects"
                })
        else:
            details.append({
                "item": "Report JSON format and required fields",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Missing top-level fields: {missing}" if missing else "clusters is not a list"
            })
    except Exception as e:
        details.append({
            "item": "Report JSON format and required fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })

    # ------------------------------------------------------------
    # 3. Expected cluster list (3 business clusters, no shared-ops) (20 pts)
    # ------------------------------------------------------------
    expected_cluster_ids = {"cl-ads", "cl-lake", "cl-retail"}
    actual_ids = {c.get("cluster_id") for c in report.get("clusters", [])}
    # Also check that no extra cluster (like cl-shared) is present
    if actual_ids == expected_cluster_ids:
        details.append({
            "item": "Correct cluster inclusion (business only, no shared-ops)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Clusters match expected: {sorted(expected_cluster_ids)}"
        })
        total_score += 20
    elif len(actual_ids - expected_cluster_ids) > 0:
        extra = actual_ids - expected_cluster_ids
        details.append({
            "item": "Correct cluster inclusion (business only, no shared-ops)",
            "score": 10,
            "max_score": 20,
            "passed": False,
            "reason": f"Extra clusters found: {extra}"
        })
        total_score += 10
    elif expected_cluster_ids - actual_ids:
        missing = expected_cluster_ids - actual_ids
        details.append({
            "item": "Correct cluster inclusion (business only, no shared-ops)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing clusters: {missing}"
        })
    else:
        details.append({
            "item": "Correct cluster inclusion (business only, no shared-ops)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Unexpected cluster set"
        })

    # ------------------------------------------------------------
    # 4. Compute exact expected costs by re-reading input data (60 pts total)
    #   - compute_cost per cluster: 20 pts
    #   - storage_cost per cluster: 20 pts
    #   - total_cost top-level: 20 pts
    # ------------------------------------------------------------
    try:
        # Load input data from workspace
        pricing_path = workpath / "data/pricing/pricing_catalogs.json"
        ledger_path = workpath / "data/resources/resource_ledger.json"
        clusters_path = workpath / "data/resources/clusters.json"

        catalogs = load_json(pricing_path)
        ledger = load_json(ledger_path)
        clusters = load_json(clusters_path)

        # Find active June 2026 catalog
        active_catalog = None
        for cat in catalogs:
            if cat.get("status") == "active" and cat.get("billing_month") == "2026-06":
                active_catalog = cat
                break
        if not active_catalog:
            raise ValueError("No active June 2026 catalog found")

        # Build rate lookup: (resource_family, metric_code) -> unit_price
        rates = {}
        for r in active_catalog["rates"]:
            rates[(r["resource_family"], r["metric_code"])] = r["unit_price"]

        # Build set of business cluster IDs
        business_cluster_ids = set()
        for cl in clusters:
            if cl.get("cluster_role") == "business":
                business_cluster_ids.add(cl["cluster_id"])

        # Aggregate usage per cluster, per metric (sum over all entries)
        usage = {}  # cluster_id -> { metric_code: total_quantity }
        for entry in ledger:
            cid = entry.get("cluster_id")
            if cid not in business_cluster_ids:
                continue
            mcode = entry.get("metric_code")
            qty = entry.get("quantity", 0)
            usage.setdefault(cid, {}).setdefault(mcode, 0)
            usage[cid][mcode] += qty

        # Compute expected costs per cluster
        expected_cluster_costs = {}
        for cid in business_cluster_ids:
            compute_cost = 0.0
            storage_cost = 0.0
            for mcode, qty in usage.get(cid, {}).items():
                rf = None
                # Determine resource_family from any entry with same cluster and metric?
                # We need mapping; simplest: from rates keys
                # We'll loop rates to find matching family
                for (fam, mc), price in rates.items():
                    if mc == mcode:
                        rf = fam
                        break
                if rf is None:
                    continue
                cost = qty * price
                if rf == "compute":
                    compute_cost += cost
                elif rf == "storage":
                    storage_cost += cost
            expected_cluster_costs[cid] = {
                "compute_cost": round(compute_cost, 2),
                "storage_cost": round(storage_cost, 2),
                "total_cost": round(compute_cost + storage_cost, 2)
            }
        expected_total_cost = round(sum(v["total_cost"] for v in expected_cluster_costs.values()), 2)

        # Build lookup from agent report
        agent_costs = {}
        for c in report.get("clusters", []):
            cid = c.get("cluster_id")
            agent_costs[cid] = {
                "compute_cost": c.get("compute_cost", 0),
                "storage_cost": c.get("storage_cost", 0),
                "total_cost": c.get("total_cost", 0)
            }

        # ---------- Sub-check: compute_cost per cluster (20 pts) ----------
        compute_ok = True
        for cid in expected_cluster_ids:
            exp = expected_cluster_costs[cid]["compute_cost"]
            got = agent_costs.get(cid, {}).get("compute_cost", -1)
            if abs(exp - got) > 0.01:
                compute_ok = False
                break
        if compute_ok:
            details.append({
                "item": "Compute costs per business cluster",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "All compute costs match expected"
            })
            total_score += 20
        else:
            details.append({
                "item": "Compute costs per business cluster",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Mismatch in compute_cost for one or more clusters"
            })

        # ---------- Sub-check: storage_cost per cluster (20 pts) ----------
        storage_ok = True
        for cid in expected_cluster_ids:
            exp = expected_cluster_costs[cid]["storage_cost"]
            got = agent_costs.get(cid, {}).get("storage_cost", -1)
            if abs(exp - got) > 0.01:
                storage_ok = False
                break
        if storage_ok:
            details.append({
                "item": "Storage costs per business cluster",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "All storage costs match expected"
            })
            total_score += 20
        else:
            details.append({
                "item": "Storage costs per business cluster",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Mismatch in storage_cost for one or more clusters"
            })

        # ---------- Sub-check: total_cost (20 pts) ----------
        agent_total = report.get("total_cost", -1)
        if abs(expected_total_cost - agent_total) < 0.01:
            details.append({
                "item": "Top-level total_cost",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": f"Total {expected_total_cost} matches"
            })
            total_score += 20
        else:
            details.append({
                "item": "Top-level total_cost",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Expected {expected_total_cost}, got {agent_total}"
            })

    except Exception as e:
        details.append({
            "item": "Input data loading & cost calculation",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": f"Error reading input files or computing: {e}"
        })

    # ------------------------------------------------------------
    # Finalize
    # ------------------------------------------------------------
    total_score = min(total_score, 100)  # cap
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(workpath / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
