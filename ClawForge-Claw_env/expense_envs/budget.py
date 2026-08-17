from __future__ import annotations

from typing import Any


class ExpenseController:
    def __init__(self, session: dict[str, Any], store: Any, session_id: str):
        self.session = session
        self.store = store
        self.session_id = session_id

    def _save(self) -> None:
        self.store.save_session(self.session_id, self.session)

    def _get_expense_state(self) -> dict[str, Any]:
        return self.session.get("expense_state", {})

    def _update_expense_state(self, updates: dict[str, Any]) -> None:
        expense_state = self._get_expense_state()
        expense_state.update(updates)
        self.session["expense_state"] = expense_state
        self._save()


def calculate_budget(
    repo: Any,
    tier: str,
    destination: str,
    duration_days: int,
) -> dict[str, Any]:
    policy = repo.get_travel_policy(tier)
    if not policy:
        return {"status": "error", "message": f"Policy tier {tier} not found"}

    transport_limit = policy.get("transport_local_budget", 150)
    accommodation_limit = policy.get("daily_accommodation_budget", 500)
    meals_limit = policy.get("daily_food_budget", 200)
    taxi_limit = policy.get("taxi_limit_per_day", 100)
    misc_limit = policy.get("misc_limit_per_day", 50)

    transportation_total = transport_limit * duration_days
    accommodation_total = accommodation_limit * duration_days
    meals_total = meals_limit * duration_days
    other_total = (taxi_limit + misc_limit) * duration_days

    total_budget = transportation_total + accommodation_total + meals_total + other_total

    return {
        "status": "success",
        "data": {
            "tier": tier,
            "destination": destination,
            "duration_days": duration_days,
            "breakdown": {
                "transportation": {
                    "daily": transport_limit,
                    "total": transportation_total,
                },
                "accommodation": {
                    "daily": accommodation_limit,
                    "total": accommodation_total,
                },
                "meals": {
                    "daily": meals_limit,
                    "total": meals_total,
                },
                "other": {
                    "daily": taxi_limit + misc_limit,
                    "total": other_total,
                },
            },
            "total_budget": total_budget,
            "policy_name": policy.get("name", ""),
        },
    }


def apply_policy_rules(
    policy: dict[str, Any],
    consumption_records: dict[str, Any],
) -> dict[str, Any]:
    if not consumption_records:
        return {"status": "success", "data": {"adjusted_total": 0, "adjustments": []}}

    records = consumption_records.get("records", [])
    limits = policy.get("limits", {})
    daily_budgets = policy.get("daily_budgets", {})

    adjustments = []
    total_actual = 0.0

    for record in records:
        category = record.get("category", "other")
        amount = float(record.get("amount", 0))
        total_actual += amount

        daily_limit_key = f"{category}_per_day"
        daily_limit = limits.get(daily_limit_key, 0)
        day_limit = daily_budgets.get(category, {}).get("day_limit", daily_limit)

        if amount > day_limit:
            excess = amount - day_limit
            adjustments.append({
                "category": category,
                "excess_amount": excess,
                "reason": f"Exceeds daily limit of {day_limit}",
            })

    total_adjustment = sum(adj["excess_amount"] for adj in adjustments)

    return {
        "status": "success",
        "data": {
            "total_actual": total_actual,
            "adjustments": adjustments,
            "total_adjustment": total_adjustment,
            "adjusted_total": total_actual - total_adjustment,
        },
    }
