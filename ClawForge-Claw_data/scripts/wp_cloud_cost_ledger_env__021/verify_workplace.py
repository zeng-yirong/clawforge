import sys
import os
import json
from pathlib import Path

WORKPLACE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

# --------------------------------------------------------------------------
# Expected values (precomputed from the env_builder)
# --------------------------------------------------------------------------
EXPECTED = {
    "report_month": "2026-06",
    "clusters": [
        {
            "cluster_id": "ads-ranking",
            "resources": [
                {"metric_code": "vcpu",  "total_quantity": 10, "unit_price": 0.05, "billing_hours": 730, "total_cost": 365.0},
                {"metric_code": "memory_gb", "total_quantity": 64, "unit_price": 0.01, "billing_hours": 730, "total_cost": 467.2}
            ]
        },
        {
            "cluster_id": "lakehouse-analytics",
            "resources": [
                {"metric_code": "vcpu",  "total_quantity": 20, "unit_price": 0.05, "billing_hours": 730, "total_cost": 730.0},
                {"metric_code": "memory_gb", "total_quantity": 128, "unit_price": 0.01, "billing_hours": 730, "total_cost": 934.4}
            ]
        },
        {
            "cluster_id": "retail-core",
            "resources": [
                {"metric_code": "vcpu",  "total_quantity": 30, "unit_price": 0.05, "billing_hours": 730, "total_cost": 1095.0},
                {"metric_code": "memory_gb", "total_quantity": 256, "unit_price": 0.01, "billing_hours": 730, "total_cost": 1868.8}
            ]
        }
    ]
}

# Simplify expected lookup: cluster -> metric -> (qty, price, hours, cost)
exp_map = {}
for cl in EXPECTED["clusters"]:
    cid = cl["cluster_id"]
    exp_map[cid] = {}
    for r in cl["resources"]:
        exp_map[cid][r["metric_code"]] = (
            r["total_quantity"],
            r["unit_price"],
            r["billing_hours"],
            r["total_cost"]
        )

# --------------------------------------------------------------------------
# Scoring configuration
# --------------------------------------------------------------------------
SCORE_CONFIG = [
    ("report file exists", 5),
    ("report file is valid JSON", 5),
    ("report_month equals '2026-06'", 5),
    ("report contains exactly 3 business clusters", 10),
    ("each cluster has correct cluster_id", 10),
    ("each cluster contains expected resource metrics", 15),
    ("each resource entry has total_quantity correct", 25),
    ("each resource entry has total_cost correct (within 0.01)", 25),
]

total_max = sum(max_s for _, max_s in SCORE_CONFIG)

def check_resource(actual, exp_qty, exp_price, exp_hours, exp_cost, tol=0.01):
    """Return list of (passed, field_name)."""
    checks = []
    qty_ok = actual.get("total_quantity") == exp_qty
    checks.append((qty_ok, "total_quantity"))
    # unit_price and billing_hours are structural, not strictly checked but we note
    price_ok = abs(actual.get("unit_price", 0) - exp_price) < tol
    checks.append((price_ok, "unit_price"))
    hours_ok = actual.get("billing_hours") == exp_hours
    checks.append((hours_ok, "billing_hours"))
    cost_ok = abs(actual.get("total_cost", 0) - exp_cost) < tol
    checks.append((cost_ok, "total_cost"))
    return checks

results = []
details = []

# 1) File existence
report_path = WORKPLACE / "report" / "cost_detail_202606.json"
if report_path.exists():
    details.append({"item": "report file exists", "score": 5, "max_score": 5, "passed": True, "reason": "file found"})
else:
    details.append({"item": "report file exists", "score": 0, "max_score": 5, "passed": False, "reason": f"file not found at {report_path}"})
    # cannot proceed further
    total_score = 0
    with open(WORKPLACE / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    sys.exit(0)

# 2) Valid JSON
try:
    with open(report_path, "r") as f:
        data = json.load(f)
    details.append({"item": "report file is valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "parsed OK"})
except Exception as e:
    details.append({"item": "report file is valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": f"not valid JSON: {e}"})
    total_score = sum(d["score"] for d in details)
    with open(WORKPLACE / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    sys.exit(0)

# 3) report_month
if data.get("report_month") == EXPECTED["report_month"]:
    details.append({"item": "report_month equals '2026-06'", "score": 5, "max_score": 5, "passed": True, "reason": f"got {data['report_month']}"})
else:
    details.append({"item": "report_month equals '2026-06'", "score": 0, "max_score": 5, "passed": False, "reason": f"got {data.get('report_month')}"})

# 4) clusters list
clusters_reported = data.get("clusters", [])
reported_ids = [c.get("cluster_id","") for c in clusters_reported]
expected_ids = sorted(["ads-ranking", "lakehouse-analytics", "retail-core"])
if sorted(reported_ids) == expected_ids:
    details.append({"item": "report contains exactly 3 business clusters", "score": 10, "max_score": 10, "passed": True, "reason": f"clusters: {reported_ids}"})
else:
    details.append({"item": "report contains exactly 3 business clusters", "score": 0, "max_score": 10, "passed": False, "reason": f"got {reported_ids}, expected {expected_ids}"})

# 5) cluster_id correctness (each expected cluster must appear)
all_cid_ok = True
for cid in expected_ids:
    if cid not in reported_ids:
        all_cid_ok = False
        break
if all_cid_ok and len(reported_ids) == 3:
    details.append({"item": "each cluster has correct cluster_id", "score": 10, "max_score": 10, "passed": True, "reason": "all expected ids present"})
else:
    details.append({"item": "each cluster has correct cluster_id", "score": 0, "max_score": 10, "passed": False, "reason": "mismatch"})

# 6) resources per cluster
resource_ok = True
for cid in expected_ids:
    cluster_data = next((c for c in clusters_reported if c.get("cluster_id") == cid), None)
    if cluster_data is None:
        resource_ok = False
        break
    reported_metrics = {r.get("metric_code") for r in cluster_data.get("resources", [])}
    expected_metrics = set(exp_map[cid].keys())
    if reported_metrics != expected_metrics:
        resource_ok = False
        break
if resource_ok:
    details.append({"item": "each cluster contains expected resource metrics", "score": 15, "max_score": 15, "passed": True, "reason": "correct metric sets"})
else:
    details.append({"item": "each cluster contains expected resource metrics", "score": 0, "max_score": 15, "passed": False, "reason": f"mismatch in metric codes"})

# 7 & 8) quantity and cost checks
qty_score = 0
cost_score = 0
qty_max = 25
cost_max = 25

total_resources_checked = 0
qty_ok_count = 0
cost_ok_count = 0

for cid in expected_ids:
    cluster_data = next((c for c in clusters_reported if c.get("cluster_id") == cid), None)
    if cluster_data is None:
        continue
    for r in cluster_data.get("resources", []):
        mc = r.get("metric_code")
        if mc not in exp_map[cid]:
            continue
        total_resources_checked += 1
        exp_qty, exp_price, exp_hours, exp_cost = exp_map[cid][mc]
        checks = check_resource(r, exp_qty, exp_price, exp_hours, exp_cost)
        # only quantity and cost
        if checks[0][0]:
            qty_ok_count += 1
        if checks[3][0]:
            cost_ok_count += 1

# Scale scores proportionally (if any resource missing, treat as 0)
if total_resources_checked > 0:
    qty_score = int(round(qty_ok_count / total_resources_checked * qty_max))
    cost_score = int(round(cost_ok_count / total_resources_checked * cost_max))
else:
    qty_score = 0
    cost_score = 0

details.append({"item": "each resource entry has total_quantity correct", "score": qty_score, "max_score": qty_max, "passed": qty_score == qty_max, "reason": f"{qty_ok_count}/{total_resources_checked} correct"})
details.append({"item": "each resource entry has total_cost correct (within 0.01)", "score": cost_score, "max_score": cost_max, "passed": cost_score == cost_max, "reason": f"{cost_ok_count}/{total_resources_checked} correct"})

# Final score
total_score = sum(d["score"] for d in details)
with open(WORKPLACE / "workplace_score.json", "w") as f:
    json.dump({"total_score": total_score, "details": details}, f, indent=2)
