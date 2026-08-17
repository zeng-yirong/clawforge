from __future__ import annotations

from collections import defaultdict
from typing import Any


CHART_TYPES = ["bar", "pie", "line", "column", "area", "scatter"]


def create_bar_chart(
    session: dict[str, Any],
    chart_id: str,
    title: str,
    x_axis_column: str,
    y_axis_column: str,
    aggregation: str = "sum"
) -> dict[str, Any]:
    if "cleaned_data" not in session:
        return {
            "success": False,
            "error": "Run deduplication first"
        }
    
    cleaned = session["cleaned_data"]
    rows = cleaned["rows"]
    
    aggregated_data = defaultdict(list)
    for row in rows:
        x_val = str(row.get(x_axis_column) or "N/A")
        y_val = row.get(y_axis_column)
        if y_val is not None:
            try:
                aggregated_data[x_val].append(float(y_val))
            except (ValueError, TypeError):
                aggregated_data[x_val].append(0.0)
    
    chart_data = []
    for x_val, y_vals in aggregated_data.items():
        if aggregation == "sum":
            y_agg = sum(y_vals)
        elif aggregation == "average":
            y_agg = sum(y_vals) / len(y_vals) if y_vals else 0.0
        elif aggregation == "count":
            y_agg = len(y_vals)
        elif aggregation == "min":
            y_agg = min(y_vals) if y_vals else 0.0
        elif aggregation == "max":
            y_agg = max(y_vals) if y_vals else 0.0
        else:
            y_agg = sum(y_vals)
        chart_data.append({"label": x_val, "value": round(y_agg, 2)})
    
    chart = {
        "chart_id": chart_id,
        "type": "bar",
        "title": title,
        "x_axis": x_axis_column,
        "y_axis": y_axis_column,
        "aggregation": aggregation,
        "data": chart_data
    }
    
    _save_chart(session, chart)
    
    return {
        "success": True,
        "chart_id": chart_id,
        "chart_type": "bar",
        "data_points": len(chart_data)
    }


def create_pie_chart(
    session: dict[str, Any],
    chart_id: str,
    title: str,
    label_column: str,
    value_column: str,
    aggregation: str = "sum"
) -> dict[str, Any]:
    if "cleaned_data" not in session:
        return {
            "success": False,
            "error": "Run deduplication first"
        }
    
    cleaned = session["cleaned_data"]
    rows = cleaned["rows"]
    
    aggregated_data = defaultdict(list)
    for row in rows:
        label = str(row.get(label_column) or "N/A")
        val = row.get(value_column)
        if val is not None:
            try:
                aggregated_data[label].append(float(val))
            except (ValueError, TypeError):
                aggregated_data[label].append(0.0)
    
    total = 0.0
    chart_data = []
    for label, vals in aggregated_data.items():
        if aggregation == "sum":
            agg_val = sum(vals)
        elif aggregation == "average":
            agg_val = sum(vals) / len(vals) if vals else 0.0
        elif aggregation == "count":
            agg_val = len(vals)
        else:
            agg_val = sum(vals)
        total += agg_val
        chart_data.append({"label": label, "value": round(agg_val, 2)})
    
    for item in chart_data:
        item["percentage"] = round((item["value"] / total * 100) if total > 0 else 0.0, 2)
    
    chart = {
        "chart_id": chart_id,
        "type": "pie",
        "title": title,
        "labels": label_column,
        "values": value_column,
        "aggregation": aggregation,
        "data": chart_data,
        "total": round(total, 2)
    }
    
    _save_chart(session, chart)
    
    return {
        "success": True,
        "chart_id": chart_id,
        "chart_type": "pie",
        "data_points": len(chart_data)
    }


def create_line_chart(
    session: dict[str, Any],
    chart_id: str,
    title: str,
    x_axis_column: str,
    y_axis_column: str,
    aggregation: str = "sum"
) -> dict[str, Any]:
    if "cleaned_data" not in session:
        return {
            "success": False,
            "error": "Run deduplication first"
        }
    
    cleaned = session["cleaned_data"]
    rows = cleaned["rows"]
    
    aggregated_data = defaultdict(list)
    for row in rows:
        x_val = str(row.get(x_axis_column) or "N/A")
        y_val = row.get(y_axis_column)
        if y_val is not None:
            try:
                aggregated_data[x_val].append(float(y_val))
            except (ValueError, TypeError):
                aggregated_data[x_val].append(0.0)
    
    chart_data = []
    for x_val, y_vals in aggregated_data.items():
        if aggregation == "sum":
            y_agg = sum(y_vals)
        elif aggregation == "average":
            y_agg = sum(y_vals) / len(y_vals) if y_vals else 0.0
        elif aggregation == "count":
            y_agg = len(y_vals)
        else:
            y_agg = sum(y_vals)
        chart_data.append({"label": x_val, "value": round(y_agg, 2)})
    
    chart_data.sort(key=lambda x: x["label"])
    
    chart = {
        "chart_id": chart_id,
        "type": "line",
        "title": title,
        "x_axis": x_axis_column,
        "y_axis": y_axis_column,
        "aggregation": aggregation,
        "data": chart_data
    }
    
    _save_chart(session, chart)
    
    return {
        "success": True,
        "chart_id": chart_id,
        "chart_type": "line",
        "data_points": len(chart_data)
    }


def create_column_chart(
    session: dict[str, Any],
    chart_id: str,
    title: str,
    x_axis_column: str,
    y_axis_column: str,
    aggregation: str = "sum"
) -> dict[str, Any]:
    if "cleaned_data" not in session:
        return {
            "success": False,
            "error": "Run deduplication first"
        }
    
    cleaned = session["cleaned_data"]
    rows = cleaned["rows"]
    
    aggregated_data = defaultdict(list)
    for row in rows:
        x_val = str(row.get(x_axis_column) or "N/A")
        y_val = row.get(y_axis_column)
        if y_val is not None:
            try:
                aggregated_data[x_val].append(float(y_val))
            except (ValueError, TypeError):
                aggregated_data[x_val].append(0.0)
    
    chart_data = []
    for x_val, y_vals in aggregated_data.items():
        if aggregation == "sum":
            y_agg = sum(y_vals)
        elif aggregation == "average":
            y_agg = sum(y_vals) / len(y_vals) if y_vals else 0.0
        elif aggregation == "count":
            y_agg = len(y_vals)
        else:
            y_agg = sum(y_vals)
        chart_data.append({"label": x_val, "value": round(y_agg, 2)})
    
    chart = {
        "chart_id": chart_id,
        "type": "column",
        "title": title,
        "x_axis": x_axis_column,
        "y_axis": y_axis_column,
        "aggregation": aggregation,
        "data": chart_data
    }
    
    _save_chart(session, chart)
    
    return {
        "success": True,
        "chart_id": chart_id,
        "chart_type": "column",
        "data_points": len(chart_data)
    }


def _save_chart(session: dict[str, Any], chart: dict[str, Any]) -> None:
    if "charts" not in session:
        session["charts"] = []
    session["charts"].append(chart)


def get_all_charts(session: dict[str, Any]) -> dict[str, Any]:
    if "charts" not in session:
        return {
            "success": True,
            "chart_count": 0,
            "charts": []
        }
    
    return {
        "success": True,
        "chart_count": len(session["charts"]),
        "charts": session["charts"]
    }


def get_chart(session: dict[str, Any], chart_id: str) -> dict[str, Any]:
    if "charts" not in session:
        return {
            "success": False,
            "error": "No charts available"
        }
    
    for chart in session["charts"]:
        if chart["chart_id"] == chart_id:
            return {
                "success": True,
                "chart": chart
            }
    
    return {
        "success": False,
        "error": f"Chart not found: {chart_id}"
    }
