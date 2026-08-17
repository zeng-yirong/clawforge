"""
Verify the agent's output for expense budget analysis task.
Checks:
- ops/budget_analysis.json exists and is valid JSON
- Contains required fields (trip_id, tier, budget, overall)
- Each category budget/actual values match ground truth
- Overall budget vs actual computation
"""
import sys
import json
import os
from pathlib import Path

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    base = workspace.resolve()
    scores = []
    total = 0

    # 1. Check ops directory exists (10 pts)
    ops_dir = base / "ops"
    if ops_dir.is_dir():
        scores.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "found"})
        total += 10
    else:
        scores.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "missing"})

    # 2. Check budget_analysis.json exists and valid JSON (10 pts)
    analysis_file = ops_dir / "budget_analysis.json"
    if analysis_file.is_file():
        try:
            data = load_json(analysis_file)
            scores.append({"item": "budget_analysis.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "valid"})
            total += 10
        except Exception as e:
            scores.append({"item": "budget_analysis.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {e}"})
            # Cannot proceed further
            return write_score(scores, total)
    else:
        scores.append({"item": "budget_analysis.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        return write_score(scores, total)

    # 3. Check required fields (20 pts)
    required_fields = ["trip_id", "tier", "budget", "overall"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        scores.append({"item": "JSON contains required fields: trip_id, tier, budget, overall", "score": 20, "max_score": 20, "passed": True, "reason": "all present"})
        total += 20
    else:
        scores.append({"item": "JSON contains required fields", "score": 0, "max_score": 20, "passed": False, "reason": f"missing fields: {missing}"})

    # 4. Load ground truth from policy and consumption files (40 pts for category accuracy)
    try:
        policy = load_json(base / "data" / "policies" / "senior_policy.json")
        consumption = load_json(base / "data" / "consumption" / "trip_202312.json")
    except Exception as e:
        scores.append({"item": "Load ground truth files", "score": 0, "max_score": 40, "passed": False, "reason": f"error reading source files: {e}"})
        return write_score(scores, total)

    # Build ground truth budget limits per category
    duration = policy["duration_days"]  # 3
    limits = {}
    for cat in policy["categories"]:
        limits[cat["category_id"]] = cat["daily_limit"] * duration

    # Calculate actual totals from consumption records
    actuals = {}
    for rec in consumption["records"]:
        cat = rec["category"]
        actuals[cat] = actuals.get(cat, 0.0) + rec["amount"]

    categories_gt = {}
    all_over_budget = []
    for cat_id, limit in limits.items():
        actual = actuals.get(cat_id, 0.0)
        over = actual > limit
        over_amount = round(actual - limit, 2) if over else 0.0
        categories_gt[cat_id] = {
            "limit": limit,
            "actual": round(actual, 2),
            "over_budget": over,
            "over_amount": over_amount
        }
        if over:
            all_over_budget.append(cat_id)

    overall_gt = {
        "total_budget": round(sum(limits.values()), 2),
        "total_actual": round(sum(actuals.values()), 2),
        "over_budget": sum(actuals.values()) > sum(limits.values()),
        "over_amount": round(max(0, sum(actuals.values()) - sum(limits.values())), 2)
    }

    # Now compare with agent output
    agent_budget = data.get("budget", {})
    agent_overall = data.get("overall", {})
    comparison_errors = []
    for cat_id, gt in categories_gt.items():
        if cat_id not in agent_budget:
            comparison_errors.append(f"missing category '{cat_id}' in agent budget")
            continue
        agent_cat = agent_budget[cat_id]
        for field in ["limit", "actual", "over_budget", "over_amount"]:
            if field not in agent_cat:
                comparison_errors.append(f"category '{cat_id}' missing field '{field}'")
                continue
            if field == "over_budget":
                if agent_cat[field] != gt[field]:
                    comparison_errors.append(f"category '{cat_id}' over_budget mismatch: agent {agent_cat[field]}, expected {gt[field]}")
            else:
                if abs(agent_cat[field] - gt[field]) > 0.01:
                    comparison_errors.append(f"category '{cat_id}' {field} mismatch: agent {agent_cat[field]}, expected {gt[field]}")
    # Check overall
    for field in ["total_budget", "total_actual", "over_budget", "over_amount"]:
        if field not in agent_overall:
            comparison_errors.append(f"overall missing field '{field}'")
            continue
        if field == "over_budget":
            if agent_overall[field] != overall_gt[field]:
                comparison_errors.append(f"overall over_budget mismatch: agent {agent_overall[field]}, expected {overall_gt[field]}")
        else:
            if abs(agent_overall[field] - overall_gt[field]) > 0.01:
                comparison_errors.append(f"overall {field} mismatch: agent {agent_overall[field]}, expected {overall_gt[field]}")

    if not comparison_errors:
        scores.append({"item": "Category and overall budget analysis correct", "score": 40, "max_score": 40, "passed": True, "reason": "all values match ground truth"})
        total += 40
    else:
        detail = "; ".join(comparison_errors[:5])
        scores.append({"item": "Category and overall budget analysis correct", "score": 0, "max_score": 40, "passed": False, "reason": f"errors: {detail}"})

    # 5. Check trip_id and tier (20 pts)
    expected_trip_id = "T-202312-01"
    expected_tier = "senior"
    trip_ok = data.get("trip_id") == expected_trip_id
    tier_ok = data.get("tier") == expected_tier
    if trip_ok and tier_ok:
        scores.append({"item": "trip_id and tier correct", "score": 20, "max_score": 20, "passed": True, "reason": "match expected"})
        total += 20
    else:
        issues = []
        if not trip_ok: issues.append(f"trip_id expected {expected_trip_id}, got {data.get('trip_id')}")
        if not tier_ok: issues.append(f"tier expected {expected_tier}, got {data.get('tier')}")
        scores.append({"item": "trip_id and tier correct", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(issues)})

    write_score(scores, total)

def write_score(scores, total):
    result = {
        "total_score": total,
        "details": scores
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete: total_score = {total}/100")

if __name__ == "__main__":
    verify()
