import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. ops directory exists (10)
    ops_dir = ws / "ops"
    item = {"item": "ops directory exists", "max_score": 10}
    if ops_dir.is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops/ directory found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops/ directory missing"
    details.append(item)
    total_score += item["score"]

    # 2. report file exists (10)
    report_file = ops_dir / "ads_cost_report.json"
    item = {"item": "report file exists", "max_score": 10}
    if report_file.is_file():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops/ads_cost_report.json found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops/ads_cost_report.json missing"
    details.append(item)
    total_score += item["score"]

    # If file missing, skip further checks
    if not report_file.is_file():
        final = {
            "total_score": total_score,
            "details": details
        }
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. JSON valid (10)
    item = {"item": "report file is valid JSON", "max_score": 10}
    try:
        with open(report_file, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "valid JSON"
    except Exception as e:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"invalid JSON: {e}"
        details.append(item)
        total_score += item["score"]
        # can't proceed
        final = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return
    details.append(item)
    total_score += item["score"]

    # 4. required top-level fields (20)
    required_fields = ["total_cost", "breakdown", "currency", "billing_month", "cluster_id"]
    item = {"item": "top-level fields present", "max_score": 20}
    missing = [f for f in required_fields if f not in data]
    extra = [k for k in data if k not in required_fields]
    if not missing and not extra:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "all required fields present, no extra fields"
    else:
        deductions = 0
        if missing:
            deductions += 5 * len(missing)
            reason = f"missing: {missing}"
        if extra:
            deductions += 5 * len(extra)
            reason = f"extra fields: {extra}"
        item["score"] = max(0, 20 - deductions)
        item["passed"] = item["score"] > 0
        item["reason"] = reason if 'reason' in locals() else "field check failed"
    details.append(item)
    total_score += item["score"]

    # 5. cluster_id (10)
    item = {"item": "cluster_id equals 'ads-ranking'", "max_score": 10}
    if data.get("cluster_id") == "ads-ranking":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "correct cluster_id"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"expected 'ads-ranking', got {data.get('cluster_id')}"
    details.append(item)
    total_score += item["score"]

    # 6. billing_month (10)
    item = {"item": "billing_month equals '2026-06'", "max_score": 10}
    if data.get("billing_month") == "2026-06":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "correct billing_month"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"expected '2026-06', got {data.get('billing_month')}"
    details.append(item)
    total_score += item["score"]

    # 7. currency (10)
    item = {"item": "currency equals 'USD'", "max_score": 10}
    if data.get("currency") == "USD":
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "correct currency"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"expected 'USD', got {data.get('currency')}"
    details.append(item)
    total_score += item["score"]

    # 8. breakdown structure and values (20, critical)
    item = {"item": "breakdown correct structure and totals", "max_score": 20}
    breakdown = data.get("breakdown")
    if not isinstance(breakdown, list) or len(breakdown) != 2:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "breakdown must be a list of 2 dicts"
        details.append(item)
        total_score += item["score"]
    else:
        # expected compute cost = (24*0.1 + 128*0.05 + 4*1.0) * 720 = (2.4+6.4+4)*720 = 12.8*720 = 9216
        # expected storage cost = 2048*0.1 * 720 = 204.8 * 720 = 147456
        expected = {"compute": 9216.0, "storage": 147456.0}
        actual = {}
        ok = True
        for entry in breakdown:
            fam = entry.get("resource_family")
            cost = entry.get("total_cost")
            if fam in expected:
                actual[fam] = cost
            else:
                ok = False
        if not ok or set(actual.keys()) != {"compute", "storage"}:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"breakdown entries missing or unexpected families: actual {list(actual.keys())}"
        else:
            score = 20
            reason_parts = []
            for fam, exp in expected.items():
                if abs(actual[fam] - exp) > 0.01:
                    score -= 10
                    reason_parts.append(f"{fam} expected {exp}, got {actual[fam]}")
            if reason_parts:
                item["score"] = max(0, score)
                item["passed"] = False
                item["reason"] = "; ".join(reason_parts)
            else:
                item["score"] = 20
                item["passed"] = True
                item["reason"] = "breakdown values correct"
        details.append(item)
        total_score += item["score"]

    # 9. total_cost consistency (10)
    item = {"item": "total_cost matches sum of breakdown", "max_score": 10}
    if "breakdown" in data and isinstance(data["breakdown"], list):
        sum_breakdown = sum(entry.get("total_cost", 0) for entry in data["breakdown"])
        if abs(data.get("total_cost", 0) - sum_breakdown) < 0.01:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "total_cost equals sum of breakdown"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"total_cost {data.get('total_cost')} != breakdow sum {sum_breakdown}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "breakdown missing"
    details.append(item)
    total_score += item["score"]

    # write final score
    final = {
        "total_score": total_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
