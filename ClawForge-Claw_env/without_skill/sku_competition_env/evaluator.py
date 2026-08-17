from __future__ import annotations

from typing import Any


def _latest_entry_of_type(session: dict[str, Any], entry_type: str) -> dict[str, Any] | None:
    for entry in reversed(session.get("cache", {}).get("entries", [])):
        if entry.get("entry_type") == entry_type:
            return entry
    return None


def _action_types(session: dict[str, Any]) -> list[str]:
    return [str(item.get("action_type")) for item in session.get("actions", [])]


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    action_types = _action_types(session)
    required_actions = scenario.get("required_actions", [])
    required_action_score = 0.0
    if required_actions:
        matched = len({item for item in required_actions if item in action_types})
        required_action_score = (matched / len(required_actions)) * 25.0
    else:
        matched = 0

    target_brand_id = scenario["target_brand_id"]
    target_category_id = scenario["target_category_id"]
    active_price_book_id = scenario["active_price_book_id"]
    stale_price_book_ids = set(scenario.get("stale_price_book_ids", []))
    expected_target_sku_ids = set(scenario.get("expected_target_sku_ids", []))
    expected_competitor_brand_ids = set(scenario.get("expected_competitor_brand_ids", []))
    required_attachment_paths = set(scenario.get("required_attachment_paths", []))

    extract_entry = _latest_entry_of_type(session, "brand_catalog_extract")
    report_entry = _latest_entry_of_type(session, "category_competition_report")

    extraction_score = 0.0
    extraction_checks = {
        "exists": False,
        "correct_brand": False,
        "correct_price_book": False,
        "complete_target_skus": False,
        "contains_pricing_fields": False,
    }
    if extract_entry:
        payload = extract_entry["payload"]
        extraction_checks["exists"] = True
        extraction_checks["correct_brand"] = payload.get("brand_id") == target_brand_id
        extraction_checks["correct_price_book"] = payload.get("price_book_id") == active_price_book_id
        extracted_ids = {item.get("sku_id") for item in payload.get("records", [])}
        extraction_checks["complete_target_skus"] = expected_target_sku_ids.issubset(extracted_ids)
        extraction_checks["contains_pricing_fields"] = all(
            {"selling_points", "ingredients", "pricing"} <= set(item.keys()) for item in payload.get("records", [])
        )
        extraction_score += 10.0 if extraction_checks["correct_brand"] else 0.0
        extraction_score += 10.0 if extraction_checks["correct_price_book"] else 0.0
        extraction_score += 12.5 if extraction_checks["complete_target_skus"] else 0.0
        extraction_score += 7.5 if extraction_checks["contains_pricing_fields"] else 0.0

    report_score = 0.0
    report_checks = {
        "exists": False,
        "correct_brand": False,
        "correct_category": False,
        "correct_price_book": False,
        "covers_competitors": False,
        "stored_in_cache": False,
    }
    if report_entry:
        payload = report_entry["payload"]
        report_checks["exists"] = True
        report_checks["stored_in_cache"] = True
        report_checks["correct_brand"] = payload.get("brand_id") == target_brand_id
        report_checks["correct_category"] = payload.get("category_id") == target_category_id
        report_checks["correct_price_book"] = payload.get("price_book_id") == active_price_book_id
        competitor_ids = set(payload.get("competitor_brand_ids", []))
        report_checks["covers_competitors"] = expected_competitor_brand_ids.issubset(competitor_ids)
        report_score += 10.0 if report_checks["correct_brand"] else 0.0
        report_score += 7.5 if report_checks["correct_category"] else 0.0
        report_score += 10.0 if report_checks["correct_price_book"] else 0.0
        report_score += 12.5 if report_checks["covers_competitors"] else 0.0

    reading_score = 0.0
    attachments_read = set(session.get("observations", {}).get("attachments_read", []))
    price_books_seen = set(session.get("observations", {}).get("price_book_ids_seen", []))
    if required_attachment_paths:
        reading_score += 7.5 * (len(attachments_read & required_attachment_paths) / len(required_attachment_paths))
    if active_price_book_id in price_books_seen:
        reading_score += 7.5

    penalty = 0.0
    for entry in session.get("cache", {}).get("entries", []):
        payload = entry.get("payload", {})
        if payload.get("price_book_id") in stale_price_book_ids:
            penalty -= 15.0
        if payload.get("brand_id") and payload.get("brand_id") != target_brand_id:
            penalty -= 10.0

    overall_score = max(0.0, min(100.0, required_action_score + extraction_score + report_score + reading_score + penalty))

    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "extraction_score": round(extraction_score, 4),
            "report_score": round(report_score, 4),
            "reading_score": round(reading_score, 4),
            "penalty": round(penalty, 4),
        },
        "required_actions": {
            "expected": required_actions,
            "matched_count": matched,
            "observed_actions": action_types,
        },
        "checks": {
            "extraction": extraction_checks,
            "report": report_checks,
            "attachments_read": sorted(attachments_read),
            "price_books_seen": sorted(price_books_seen),
        },
    }
