from __future__ import annotations

from typing import Any


def create_formula(
    session: dict[str, Any],
    name: str,
    expression: str,
    description: str = ""
) -> dict[str, Any]:
    if "cleaned_data" not in session:
        return {
            "success": False,
            "error": "Run deduplication first"
        }
    
    formula = {
        "name": name,
        "expression": expression,
        "description": description,
        "calculated_value": None
    }
    
    cleaned = session["cleaned_data"]
    rows = cleaned["rows"]
    
    values = []
    for row in rows:
        val = row.get("sales_amount")
        if val is not None:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                pass
    
    if expression.upper().startswith("SUM("):
        result = sum(values) if values else 0.0
        formula["calculated_value"] = round(result, 2)
        formula["result_type"] = "sum"
    elif expression.upper().startswith("AVERAGE("):
        result = sum(values) / len(values) if values else 0.0
        formula["calculated_value"] = round(result, 2)
        formula["result_type"] = "average"
    elif expression.upper().startswith("COUNT("):
        formula["calculated_value"] = len(values)
        formula["result_type"] = "count"
    elif expression.upper().startswith("MIN("):
        formula["calculated_value"] = min(values) if values else 0.0
        formula["result_type"] = "min"
    elif expression.upper().startswith("MAX("):
        formula["calculated_value"] = max(values) if values else 0.0
        formula["result_type"] = "max"
    else:
        formula["calculated_value"] = None
        formula["result_type"] = "unknown"
    
    if "formulas" not in session:
        session["formulas"] = []
    session["formulas"].append(formula)
    
    return {
        "success": True,
        "formula_name": name,
        "expression": expression,
        "calculated_value": formula["calculated_value"]
    }


def create_total_revenue_formula(session: dict[str, Any]) -> dict[str, Any]:
    return create_formula(
        session,
        name="Total Revenue",
        expression="SUM(sales_amount)",
        description="Sum of all sales after deduplication"
    )


def create_average_order_value_formula(session: dict[str, Any]) -> dict[str, Any]:
    return create_formula(
        session,
        name="Average Order Value",
        expression="AVERAGE(sales_amount)",
        description="Average sales amount per transaction"
    )


def create_total_transactions_formula(session: dict[str, Any]) -> dict[str, Any]:
    return create_formula(
        session,
        name="Total Transactions",
        expression="COUNT(transaction_id)",
        description="Count of unique transactions after deduplication"
    )


def create_total_quantity_formula(session: dict[str, Any]) -> dict[str, Any]:
    return create_formula(
        session,
        name="Total Quantity Sold",
        expression="SUM(quantity)",
        description="Total quantity of items sold"
    )


def create_total_discount_formula(session: dict[str, Any]) -> dict[str, Any]:
    return create_formula(
        session,
        name="Total Discount Given",
        expression="SUM(discount)",
        description="Total discount amount given"
    )


def get_all_formulas(session: dict[str, Any]) -> dict[str, Any]:
    if "formulas" not in session:
        return {
            "success": True,
            "formula_count": 0,
            "formulas": []
        }
    
    return {
        "success": True,
        "formula_count": len(session["formulas"]),
        "formulas": session["formulas"]
    }


def get_formula(session: dict[str, Any], name: str) -> dict[str, Any]:
    if "formulas" not in session:
        return {
            "success": False,
            "error": "No formulas available"
        }
    
    for formula in session["formulas"]:
        if formula["name"] == name:
            return {
                "success": True,
                "formula": formula
            }
    
    return {
        "success": False,
        "error": f"Formula not found: {name}"
    }
