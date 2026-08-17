import os
import sys
import json
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
details = []

def abs_path(rel):
    return os.path.join(workspace, rel)

# ---------- helper ----------
def score_detail(item, passed, score, max_score, reason):
    details.append({
        "item": item,
        "score": score if passed else 0,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# ---------- 1. Check output file exists ----------
PRICE_PATH = abs_path("ops/cost_summary.json")
if os.path.isfile(PRICE_PATH):
    score_detail("Output file exists", True, 10, 10, "ops/cost_summary.json present")
else:
    score_detail("Output file exists", False, 0, 10, "ops/cost_summary.json not found")
    # cannot proceed; write partial score
    total = sum(d["score"] for d in details)
    with open(abs_path("workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    sys.exit(0)

# ---------- 2. JSON validity ----------
try:
    with open(PRICE_PATH) as f:
        report = json.load(f)
    score_detail("JSON parseable", True, 10, 10, "Valid JSON")
except (json.JSONDecodeError, Exception) as e:
    score_detail("JSON parseable", False, 0, 10, f"Invalid JSON: {e}")
    total = sum(d["score"] for d in details)
    with open(abs_path("workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)
    sys.exit(0)

# ---------- 3. Required top-level fields ----------
required_fields = ["cluster_name", "billing_month", "currency", "total_cost", "breakdown"]
missing = [f for f in required_fields if f not in report]
if not missing:
    score_detail("Top-level fields present", True, 10, 10, "All required fields exist")
else:
    score_detail("Top-level fields present", False, 0, 10, f"Missing: {missing}")

# ---------- 4. cluster_name correct ----------
if report.get("cluster_name") == "ads-ranking":
    score_detail("cluster_name correct", True, 5, 5, "ads-ranking")
else:
    score_detail("cluster_name correct", False, 0, 5, f"Got '{report.get('cluster_name')}'")

# ---------- 5. billing_month correct ----------
if report.get("billing_month") == "2026-06":
    score_detail("billing_month correct", True, 5, 5, "2026-06")
else:
    score_detail("billing_month correct", False, 0, 5, f"Got '{report.get('billing_month')}'")

# ---------- 6. currency ----------
if report.get("currency") == "USD":
    score_detail("currency correct", True, 5, 5, "USD")
else:
    score_detail("currency correct", False, 0, 5, f"Got '{report.get('currency')}'")

# ---------- 7. breakdown structure ----------
bd = report.get("breakdown", [])
if isinstance(bd, list) and all(isinstance(e, dict) and "resource_family" in e and "cost" in e for e in bd):
    score_detail("breakdown structure", True, 5, 5, "Valid list of objects with resource_family and cost")
else:
    score_detail("breakdown structure", False, 0, 5, "Missing fields or not a list")

# ---------- 8. breakdown completeness – must have exactly two entries: compute & storage ----------
families = [e.get("resource_family") for e in bd]
expected_families = {"compute", "storage"}
if set(families) == expected_families:
    score_detail("breakdown includes both compute and storage", True, 10, 10, "Both families present")
else:
    score_detail("breakdown includes both compute and storage", False, 0, 10, f"Found families: {set(families)}")

# ---------- 9. compute cost correct ----------
# Expected: vcpu=120*0.042=5.04, memory_gb=2560*0.01=25.6, gpu=8*0.80=6.4 => compute total = 37.04
expected_compute = round(120 * 0.042 + 2560 * 0.01 + 8 * 0.80, 2)
compute_entry = next((e for e in bd if e["resource_family"] == "compute"), None)
if compute_entry:
    actual_compute = round(compute_entry["cost"], 2)
    if math.isclose(actual_compute, expected_compute, rel_tol=1e-9):
        score_detail("Compute cost correct", True, 15, 15, f"Expected {expected_compute}, got {actual_compute}")
    else:
        score_detail("Compute cost correct", False, 0, 15, f"Expected {expected_compute}, got {actual_compute}")
else:
    score_detail("Compute cost correct", False, 0, 15, "No compute breakdown entry")

# ---------- 10. storage cost correct ----------
# block_storage_gb=15000*0.00012=1.8, object_storage_gb=50000*0.00002=1.0 => storage total = 2.80
expected_storage = round(15000 * 0.00012 + 50000 * 0.00002, 2)
storage_entry = next((e for e in bd if e["resource_family"] == "storage"), None)
if storage_entry:
    actual_storage = round(storage_entry["cost"], 2)
    if math.isclose(actual_storage, expected_storage, rel_tol=1e-9):
        score_detail("Storage cost correct", True, 15, 15, f"Expected {expected_storage}, got {actual_storage}")
    else:
        score_detail("Storage cost correct", False, 0, 15, f"Expected {expected_storage}, got {actual_storage}")
else:
    score_detail("Storage cost correct", False, 0, 15, "No storage breakdown entry")

# ---------- 11. total_cost correct ----------
expected_total = round(expected_compute + expected_storage, 2)
actual_total = round(report.get("total_cost", 0), 2)
if math.isclose(actual_total, expected_total, rel_tol=1e-9):
    score_detail("Total cost correct", True, 10, 10, f"Expected {expected_total}, got {actual_total}")
else:
    score_detail("Total cost correct", False, 0, 10, f"Expected {expected_total}, got {actual_total}")

# ---------- Final score ----------
total_score = sum(d["score"] for d in details)
with open(abs_path("workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": details}, f, indent=2)
