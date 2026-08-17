from __future__ import annotations

from typing import Any


def _lower_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _score_deduplication(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    if "cleaned_data" not in session or session["cleaned_data"] is None:
        return {
            "score": 0.0,
            "has_cleaned_data": False,
            "original_count": 0,
            "deduplicated_count": 0,
            "duplicates_removed": 0
        }
    
    cleaned = session["cleaned_data"]
    original_count = cleaned.get("original_count", 0)
    deduplicated_count = cleaned.get("deduplicated_count", 0)
    duplicates_removed = cleaned.get("duplicates_removed", 0)
    
    expected_duplicates = scenario.get("expected_outputs", {}).get("deduplicated_data", {}).get("min_duplicates_to_remove", 5)
    
    score = 0.0
    if duplicates_removed >= expected_duplicates:
        score = 1.0
    elif duplicates_removed > 0:
        score = duplicates_removed / expected_duplicates
    
    return {
        "score": round(score, 4),
        "has_cleaned_data": True,
        "original_count": original_count,
        "deduplicated_count": deduplicated_count,
        "duplicates_removed": duplicates_removed
    }


def _score_pivot_tables(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    expected_pivots = scenario.get("expected_outputs", {}).get("pivot_by_category_region")
    if not expected_pivots:
        return {
            "score": 1.0,
            "pivot_count": 0,
            "missing_pivots": []
        }
    
    pivot_tables = session.get("pivot_tables", [])
    pivot_count = len(pivot_tables)
    
    required_dimensions = [
        ["category", "region"],
        ["salesperson_name"],
        ["city"]
    ]
    
    matched_dims = []
    for piv in pivot_tables:
        dims = tuple(piv.get("row_dimensions", []))
        if dims in required_dimensions:
            matched_dims.append(dims)
    
    missing = [d for d in required_dimensions if tuple(d) not in matched_dims]
    
    if not missing:
        score = 1.0
    elif pivot_count >= len(required_dimensions):
        score = 0.7
    elif pivot_count > 0:
        score = 0.4
    else:
        score = 0.0
    
    return {
        "score": round(score, 4),
        "pivot_count": pivot_count,
        "missing_pivots": [list(m) for m in missing]
    }


def _score_charts(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    expected_outputs = scenario.get("expected_outputs", {})
    expected_charts = expected_outputs.get("charts", [])
    
    if not expected_charts:
        return {
            "score": 1.0,
            "chart_count": 0,
            "created_charts": []
        }
    
    charts = session.get("charts", [])
    chart_count = len(charts)
    created_chart_types = [c.get("type") for c in charts]
    
    required_types = ["bar", "pie"]
    created_types_set = set(created_chart_types)
    missing_types = [t for t in required_types if t not in created_types_set]
    
    if not missing_types and chart_count >= 2:
        score = 1.0
    elif chart_count >= 2:
        score = 0.8
    elif chart_count > 0:
        score = 0.5
    else:
        score = 0.0
    
    return {
        "score": round(score, 4),
        "chart_count": chart_count,
        "created_charts": created_chart_types,
        "missing_chart_types": missing_types
    }


def _score_formulas(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    expected_outputs = scenario.get("expected_outputs", {})
    expected_formulas = expected_outputs.get("formulas", [])
    
    if not expected_formulas:
        return {
            "score": 1.0,
            "formula_count": 0,
            "created_formulas": []
        }
    
    formulas = session.get("formulas", [])
    formula_count = len(formulas)
    created_formula_names = [f.get("name") for f in formulas]
    
    required_names = ["Total Revenue", "Average Order Value", "Total Transactions"]
    missing_names = [n for n in required_names if n not in created_formula_names]
    
    if not missing_names and formula_count >= 3:
        score = 1.0
    elif formula_count >= 3:
        score = 0.8
    elif formula_count > 0:
        score = 0.5
    else:
        score = 0.0
    
    return {
        "score": round(score, 4),
        "formula_count": formula_count,
        "created_formulas": created_formula_names,
        "missing_formulas": missing_names
    }


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    deduplication_result = _score_deduplication(session, scenario)
    pivot_result = _score_pivot_tables(session, scenario)
    chart_result = _score_charts(session, scenario)
    formula_result = _score_formulas(session, scenario)
    
    eval_criteria = scenario.get("evaluation_criteria", {})
    deduplication_weight = eval_criteria.get("deduplication_score", 0.25)
    pivot_weight = eval_criteria.get("pivot_completeness_score", 0.30)
    chart_weight = eval_criteria.get("chart_quality_score", 0.20)
    formula_weight = eval_criteria.get("formula_accuracy_score", 0.25)
    
    overall_score = (
        deduplication_result["score"] * deduplication_weight +
        pivot_result["score"] * pivot_weight +
        chart_result["score"] * chart_weight +
        formula_result["score"] * formula_weight
    )
    
    return {
        "session_id": session["session_id"],
        "scenario_id": scenario["scenario_id"],
        "deduplication_score": deduplication_result["score"],
        "pivot_score": pivot_result["score"],
        "chart_score": chart_result["score"],
        "formula_score": formula_result["score"],
        "overall_score": round(overall_score, 4),
        "deduplication_details": deduplication_result,
        "pivot_details": pivot_result,
        "chart_details": chart_result,
        "formula_details": formula_result,
    }
