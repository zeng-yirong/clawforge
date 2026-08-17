from __future__ import annotations

from typing import Any


def generate_analysis(
    ctrl: Any,
    repo: Any,
) -> dict[str, Any]:
    expense_state = ctrl._get_expense_state()
    budget = expense_state.get("calculated_budget")
    consumption = expense_state.get("loaded_consumption")

    if not budget:
        return {"status": "error", "message": "No budget calculated yet"}
    if not consumption:
        return {"status": "error", "message": "No consumption records loaded"}

    budget_data = budget.get("data", {})
    budget_breakdown = budget_data.get("breakdown", {})
    total_budget = budget_data.get("total_budget", 0)

    actual_records = consumption.get("consumption_records", [])
    categorized = categorize_expenses(actual_records)

    total_actual = sum(float(r.get("amount", 0)) for r in actual_records)

    overrunning_categories = identify_overruns(budget_breakdown, categorized)

    variance = total_actual - total_budget
    variance_percent = (variance / total_budget * 100) if total_budget > 0 else 0

    analysis = {
        "status": "success",
        "data": {
            "budget_total": total_budget,
            "actual_total": total_actual,
            "variance": variance,
            "variance_percent": round(variance_percent, 2),
            "over_budget": variance > 0,
            "by_category": {
                cat: {
                    "budget": budget_breakdown.get(cat, {}).get("total", 0),
                    "actual": sum(float(r.get("amount", 0)) for r in categorized.get(cat, [])),
                }
                for cat in ["transportation", "accommodation", "meals", "other"]
            },
            "overrunning_categories": overrunning_categories,
            "record_count": len(actual_records),
        },
    }

    ctrl._update_expense_state({"analysis_result": analysis})
    return analysis


def identify_overruns(
    budget: dict[str, Any],
    actual: dict[str, Any],
) -> list[dict[str, Any]]:
    overruns = []
    for category in budget:
        budget_total = budget.get(category, {}).get("total", 0)
        actual_total = sum(float(r.get("amount", 0)) for r in actual.get(category, []))
        if actual_total > budget_total:
            overruns.append({
                "category": category,
                "budget_amount": budget_total,
                "actual_amount": actual_total,
                "overrun_amount": actual_total - budget_total,
            })
    return overruns


def categorize_expenses(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    categories: dict[str, list[dict[str, Any]]] = {
        "transportation": [],
        "accommodation": [],
        "meals": [],
        "other": [],
    }

    transportation_cats = {"flight", "train", "taxi", "metro"}
    meals_cats = {"food"}

    for record in records:
        category = record.get("category", "other")
        if category in transportation_cats:
            categories["transportation"].append(record)
        elif category in meals_cats:
            categories["meals"].append(record)
        elif category == "accommodation":
            categories["accommodation"].append(record)
        else:
            categories["other"].append(record)

    return categories
