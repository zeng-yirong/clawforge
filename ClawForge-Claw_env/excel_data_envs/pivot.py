from __future__ import annotations

from collections import defaultdict
from typing import Any


def _get_nested_value(row: dict[str, Any], key: str) -> Any:
    return row.get(key)


def create_pivot_table(
    session: dict[str, Any],
    row_dimensions: list[str],
    value_column: str,
    aggregation: str = "sum",
    filter_columns: dict[str, Any] | None = None
) -> dict[str, Any]:
    if "cleaned_data" not in session:
        return {
            "success": False,
            "error": "Run deduplication first"
        }
    
    cleaned = session["cleaned_data"]
    rows = cleaned["rows"]
    
    if filter_columns:
        filtered_rows = []
        for row in rows:
            match = True
            for col, val in filter_columns.items():
                if row.get(col) != val:
                    match = False
                    break
            if match:
                filtered_rows.append(row)
        rows = filtered_rows
    
    pivot_data = defaultdict(lambda: defaultdict(list))
    
    for row in rows:
        key_parts = []
        for dim in row_dimensions:
            key_parts.append(str(_get_nested_value(row, dim) or "N/A"))
        key = tuple(key_parts)
        
        val = _get_nested_value(row, value_column)
        if val is not None:
            try:
                pivot_data[key][value_column].append(float(val))
            except (ValueError, TypeError):
                pivot_data[key][value_column].append(0.0)
    
    result_rows = []
    for key, values in pivot_data.items():
        row_result = {}
        for i, dim in enumerate(row_dimensions):
            row_result[dim] = key[i]
        
        num_values = values.get(value_column, [])
        if aggregation == "sum":
            row_result[f"{value_column}_aggregated"] = sum(num_values)
        elif aggregation == "average":
            row_result[f"{value_column}_aggregated"] = sum(num_values) / len(num_values) if num_values else 0.0
        elif aggregation == "count":
            row_result[f"{value_column}_aggregated"] = len(num_values)
        elif aggregation == "min":
            row_result[f"{value_column}_aggregated"] = min(num_values) if num_values else 0.0
        elif aggregation == "max":
            row_result[f"{value_column}_aggregated"] = max(num_values) if num_values else 0.0
        else:
            row_result[f"{value_column}_aggregated"] = sum(num_values)
        
        result_rows.append(row_result)
    
    return {
        "success": True,
        "pivot_id": f"pivot_{'_'.join(row_dimensions)}_{value_column}_{aggregation}",
        "row_dimensions": row_dimensions,
        "value_column": value_column,
        "aggregation": aggregation,
        "row_count": len(result_rows),
        "rows": result_rows
    }


def create_pivot_by_category_region(session: dict[str, Any]) -> dict[str, Any]:
    return create_pivot_table(
        session,
        row_dimensions=["category", "region"],
        value_column="sales_amount",
        aggregation="sum"
    )


def create_pivot_by_salesperson(session: dict[str, Any]) -> dict[str, Any]:
    return create_pivot_table(
        session,
        row_dimensions=["salesperson_name"],
        value_column="sales_amount",
        aggregation="sum"
    )


def create_pivot_by_city(session: dict[str, Any]) -> dict[str, Any]:
    return create_pivot_table(
        session,
        row_dimensions=["city"],
        value_column="sales_amount",
        aggregation="average"
    )


def create_pivot_by_product(session: dict[str, Any]) -> dict[str, Any]:
    return create_pivot_table(
        session,
        row_dimensions=["product_name"],
        value_column="sales_amount",
        aggregation="sum"
    )


def create_pivot_by_channel(session: dict[str, Any]) -> dict[str, Any]:
    return create_pivot_table(
        session,
        row_dimensions=["channel"],
        value_column="sales_amount",
        aggregation="sum"
    )


def get_all_pivots(session: dict[str, Any]) -> dict[str, Any]:
    if "pivot_tables" not in session:
        return {
            "success": True,
            "pivot_count": 0,
            "pivots": []
        }
    
    return {
        "success": True,
        "pivot_count": len(session["pivot_tables"]),
        "pivots": session["pivot_tables"]
    }


def save_pivot(session: dict[str, Any], pivot_result: dict[str, Any]) -> dict[str, Any]:
    if not pivot_result.get("success"):
        return pivot_result
    
    if "pivot_tables" not in session:
        session["pivot_tables"] = []
    
    pivot_summary = {
        "pivot_id": pivot_result["pivot_id"],
        "row_dimensions": pivot_result["row_dimensions"],
        "value_column": pivot_result["value_column"],
        "aggregation": pivot_result["aggregation"],
        "row_count": pivot_result["row_count"]
    }
    session["pivot_tables"].append(pivot_summary)
    
    return {
        "success": True,
        "pivot_id": pivot_result["pivot_id"],
        "saved": True
    }
