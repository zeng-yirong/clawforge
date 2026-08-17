from __future__ import annotations

from copy import deepcopy
from typing import Any

from .pricing import get_price_book, get_price_book_entry_map


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _top_terms(values: list[str], limit: int = 3) -> list[str]:
    counts: dict[str, int] = {}
    for item in values:
        normalized = item.strip()
        if not normalized:
            continue
        counts[normalized] = counts.get(normalized, 0) + 1
    ordered = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return [item for item, _count in ordered[:limit]]


def _total_volume_ml(sku: dict[str, Any]) -> float:
    size_value = float(sku.get("size_value", 0))
    pack_count = int(sku.get("pack_count", 1))
    if str(sku.get("size_unit", "")).lower() != "ml" or size_value <= 0:
        return 0.0
    return size_value * pack_count


def _price_payload(sku: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    total_volume_ml = _total_volume_ml(sku)
    sale_price = float(entry["sale_price"])
    list_price = float(entry["list_price"])
    member_price = float(entry["member_price"])
    return {
        "currency": entry["currency"],
        "channel": entry["channel"],
        "list_price": list_price,
        "sale_price": sale_price,
        "member_price": member_price,
        "price_per_ml": round(sale_price / total_volume_ml, 2) if total_volume_ml else None,
        "list_price_per_ml": round(list_price / total_volume_ml, 2) if total_volume_ml else None,
        "member_price_per_ml": round(member_price / total_volume_ml, 2) if total_volume_ml else None,
        "effective_from": entry["effective_from"],
    }


def _cache_entry_id(action_index: int) -> str:
    return f"cache_{action_index:06d}"


def _append_cache_entry(
    session: dict[str, Any],
    *,
    cache_key: str,
    entry_type: str,
    payload: dict[str, Any],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    entry = {
        "entry_id": _cache_entry_id(action_index),
        "cache_key": cache_key,
        "entry_type": entry_type,
        "created_at": event_at,
        "action_index": action_index,
        "payload": payload,
    }
    session["cache"]["entries"].append(entry)
    session["cache"]["latest"][cache_key] = entry["entry_id"]
    _append_unique(session["observations"]["cache_entry_ids"], entry["entry_id"])
    return deepcopy(entry)


def _latest_cache_entry(session: dict[str, Any], cache_key: str) -> dict[str, Any] | None:
    entry_id = session["cache"]["latest"].get(cache_key)
    if not entry_id:
        return None
    for entry in reversed(session["cache"]["entries"]):
        if entry["entry_id"] == entry_id:
            return deepcopy(entry)
    return None


def list_cache_entries(
    session: dict[str, Any],
    *,
    entry_type: str | None = None,
    cache_key: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    entry_type_lower = entry_type.strip().lower() if entry_type else None

    for entry in reversed(session["cache"]["entries"]):
        if entry_type_lower and str(entry["entry_type"]).lower() != entry_type_lower:
            continue
        if cache_key and entry["cache_key"] != cache_key:
            continue
        payload = entry["payload"]
        results.append(
            {
                "entry_id": entry["entry_id"],
                "cache_key": entry["cache_key"],
                "entry_type": entry["entry_type"],
                "created_at": entry["created_at"],
                "action_index": entry["action_index"],
                "brand_id": payload.get("brand_id"),
                "category_id": payload.get("category_id"),
                "price_book_id": payload.get("price_book_id"),
                "sku_count": payload.get("sku_count"),
                "competitor_brand_count": len(payload.get("competitor_brand_ids", [])),
            }
        )

    return results[:limit] if limit is not None else results


def get_cache_entry(session: dict[str, Any], entry_id: str) -> dict[str, Any]:
    for entry in session["cache"]["entries"]:
        if entry["entry_id"] == entry_id:
            return deepcopy(entry)
    raise KeyError(f"Cache entry not found: {entry_id}")


def extract_brand_catalog(
    session: dict[str, Any],
    brand_id: str,
    price_book_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    brand = None
    for item in session["brands"]:
        if item["brand_id"] == brand_id:
            brand = item
            break
    if brand is None:
        raise KeyError(f"Brand not found: {brand_id}")

    price_book = get_price_book(session, price_book_id)
    entry_map = get_price_book_entry_map(session, price_book_id)
    brand_skus = [sku for sku in session["skus"] if sku["brand_id"] == brand_id]
    if not brand_skus:
        raise ValueError(f"No SKUs available for brand: {brand_id}")

    category_ids = sorted({sku["category_id"] for sku in brand_skus})
    records: list[dict[str, Any]] = []
    ingredient_pool: list[str] = []
    selling_point_pool: list[str] = []

    for sku in sorted(brand_skus, key=lambda item: str(item["sku_name"])):
        if sku["sku_id"] not in entry_map:
            raise KeyError(f"Price book {price_book_id} does not include SKU: {sku['sku_id']}")
        ingredient_pool.extend(str(item) for item in sku.get("ingredients", []))
        selling_point_pool.extend(str(item) for item in sku.get("selling_points", []))
        records.append(
            {
                "sku_id": sku["sku_id"],
                "sku_name": sku["sku_name"],
                "category_id": sku["category_id"],
                "category_name": sku["category_name"],
                "status": sku["status"],
                "selling_points": deepcopy(sku.get("selling_points", [])),
                "ingredients": deepcopy(sku.get("ingredients", [])),
                "pricing": _price_payload(sku, entry_map[sku["sku_id"]]),
            }
        )
        _append_unique(session["observations"]["sku_ids_seen"], sku["sku_id"])

    _append_unique(session["observations"]["brand_ids_seen"], brand_id)
    _append_unique(session["observations"]["price_book_ids_seen"], price_book_id)

    payload = {
        "brand_id": brand_id,
        "brand_name": brand["brand_name"],
        "category_id": category_ids[0] if len(category_ids) == 1 else None,
        "category_ids": category_ids,
        "price_book_id": price_book_id,
        "price_book_version": price_book["version"],
        "sku_count": len(records),
        "records": records,
        "top_ingredients": _top_terms(ingredient_pool, limit=5),
        "top_selling_points": _top_terms(selling_point_pool, limit=5),
    }
    cache_key = f"brand_extract::{brand_id}::{price_book_id}"
    return _append_cache_entry(
        session,
        cache_key=cache_key,
        entry_type="brand_catalog_extract",
        payload=payload,
        event_at=event_at,
        action_index=action_index,
    )


def _infer_category_for_brand(session: dict[str, Any], brand_id: str, category_id: str | None) -> str:
    if category_id:
        return category_id
    category_ids = sorted({sku["category_id"] for sku in session["skus"] if sku["brand_id"] == brand_id})
    if len(category_ids) == 1:
        return category_ids[0]
    raise ValueError("Brand spans multiple categories. Provide --category-id explicitly.")


def _brand_name(session: dict[str, Any], brand_id: str) -> str:
    for brand in session["brands"]:
        if brand["brand_id"] == brand_id:
            return str(brand["brand_name"])
    return brand_id


def _benchmark_row(
    session: dict[str, Any],
    brand_id: str,
    category_id: str,
    price_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    skus = [sku for sku in session["skus"] if sku["brand_id"] == brand_id and sku["category_id"] == category_id]
    sale_prices: list[float] = []
    price_per_ml_values: list[float] = []
    all_ingredients: list[str] = []
    all_selling_points: list[str] = []

    for sku in skus:
        entry = price_map.get(sku["sku_id"])
        if not entry:
            continue
        pricing = _price_payload(sku, entry)
        sale_prices.append(float(pricing["sale_price"]))
        if pricing["price_per_ml"] is not None:
            price_per_ml_values.append(float(pricing["price_per_ml"]))
        all_ingredients.extend(str(item) for item in sku.get("ingredients", []))
        all_selling_points.extend(str(item) for item in sku.get("selling_points", []))

    return {
        "brand_id": brand_id,
        "brand_name": _brand_name(session, brand_id),
        "sku_count": len(skus),
        "avg_sale_price": round(sum(sale_prices) / len(sale_prices), 2) if sale_prices else None,
        "avg_price_per_ml": round(sum(price_per_ml_values) / len(price_per_ml_values), 2) if price_per_ml_values else None,
        "hero_ingredients": _top_terms(all_ingredients, limit=3),
        "hero_selling_points": _top_terms(all_selling_points, limit=3),
    }


def _price_positioning(target_value: float | None, competitor_values: list[float]) -> str:
    if target_value is None or not competitor_values:
        return "unclassified"
    competitor_avg = sum(competitor_values) / len(competitor_values)
    if target_value >= competitor_avg * 1.12:
        return "premium"
    if target_value <= competitor_avg * 0.9:
        return "value"
    return "mid-premium"


def generate_category_report(
    session: dict[str, Any],
    brand_id: str,
    price_book_id: str,
    event_at: str,
    action_index: int,
    *,
    category_id: str | None = None,
) -> dict[str, Any]:
    resolved_category_id = _infer_category_for_brand(session, brand_id, category_id)
    price_book = get_price_book(session, price_book_id)
    price_map = get_price_book_entry_map(session, price_book_id)
    target_skus = [
        sku
        for sku in session["skus"]
        if sku["brand_id"] == brand_id and sku["category_id"] == resolved_category_id
    ]
    if not target_skus:
        raise ValueError(f"No target SKUs found for brand {brand_id} in category {resolved_category_id}")

    competitor_skus = [
        sku
        for sku in session["skus"]
        if sku["brand_id"] != brand_id and sku["category_id"] == resolved_category_id
    ]
    competitor_brand_ids = sorted({sku["brand_id"] for sku in competitor_skus})
    category_name = str(target_skus[0]["category_name"])

    benchmark_rows = [_benchmark_row(session, brand_id, resolved_category_id, price_map)]
    competitor_rows = [_benchmark_row(session, item, resolved_category_id, price_map) for item in competitor_brand_ids]
    benchmark_rows.extend(competitor_rows)

    competitor_price_values = [
        float(item["avg_price_per_ml"])
        for item in competitor_rows
        if item.get("avg_price_per_ml") is not None
    ]
    target_avg_ppml = benchmark_rows[0].get("avg_price_per_ml")

    target_selling_points = {
        str(point)
        for sku in target_skus
        for point in sku.get("selling_points", [])
    }
    competitor_selling_points = {
        str(point)
        for sku in competitor_skus
        for point in sku.get("selling_points", [])
    }
    target_ingredients = {
        str(item)
        for sku in target_skus
        for item in sku.get("ingredients", [])
    }
    competitor_ingredients = {
        str(item)
        for sku in competitor_skus
        for item in sku.get("ingredients", [])
    }

    sku_comparison: list[dict[str, Any]] = []
    for target_sku in sorted(target_skus, key=lambda item: str(item["sku_name"])):
        target_entry = price_map.get(target_sku["sku_id"])
        if not target_entry:
            raise KeyError(f"Price book {price_book_id} does not include SKU: {target_sku['sku_id']}")
        target_pricing = _price_payload(target_sku, target_entry)
        ranked_competitors: list[dict[str, Any]] = []

        for competitor_sku in competitor_skus:
            competitor_entry = price_map.get(competitor_sku["sku_id"])
            if not competitor_entry:
                continue
            competitor_pricing = _price_payload(competitor_sku, competitor_entry)
            ranked_competitors.append(
                {
                    "brand_id": competitor_sku["brand_id"],
                    "brand_name": competitor_sku["brand_name"],
                    "sku_id": competitor_sku["sku_id"],
                    "sku_name": competitor_sku["sku_name"],
                    "sale_price": competitor_pricing["sale_price"],
                    "price_per_ml": competitor_pricing["price_per_ml"],
                    "ingredients": deepcopy(competitor_sku.get("ingredients", [])),
                    "selling_points": deepcopy(competitor_sku.get("selling_points", [])),
                    "price_gap_vs_target": round(
                        float(competitor_pricing["sale_price"]) - float(target_pricing["sale_price"]),
                        2,
                    ),
                }
            )

        ranked_competitors.sort(
            key=lambda item: (
                abs(float(item["sale_price"]) - float(target_pricing["sale_price"])),
                str(item["brand_name"]),
                str(item["sku_name"]),
            )
        )
        sku_comparison.append(
            {
                "target_sku_id": target_sku["sku_id"],
                "target_sku_name": target_sku["sku_name"],
                "target_pricing": target_pricing,
                "target_ingredients": deepcopy(target_sku.get("ingredients", [])),
                "target_selling_points": deepcopy(target_sku.get("selling_points", [])),
                "closest_competitors": ranked_competitors[:3],
            }
        )
        _append_unique(session["observations"]["sku_ids_seen"], target_sku["sku_id"])

    extract_cache_key = f"brand_extract::{brand_id}::{price_book_id}"
    latest_extract = _latest_cache_entry(session, extract_cache_key)

    payload = {
        "brand_id": brand_id,
        "brand_name": _brand_name(session, brand_id),
        "category_id": resolved_category_id,
        "category_name": category_name,
        "price_book_id": price_book_id,
        "price_book_version": price_book["version"],
        "sku_count": len(target_skus),
        "competitor_brand_ids": competitor_brand_ids,
        "competitor_brand_count": len(competitor_brand_ids),
        "benchmark_rows": benchmark_rows,
        "summary": {
            "target_positioning": _price_positioning(target_avg_ppml, competitor_price_values),
            "shared_ingredients": sorted(target_ingredients & competitor_ingredients)[:6],
            "distinctive_selling_points": sorted(target_selling_points - competitor_selling_points)[:6],
        },
        "sku_comparison": sku_comparison,
        "source_extract_entry_id": latest_extract["entry_id"] if latest_extract else None,
    }
    cache_key = f"category_report::{brand_id}::{resolved_category_id}::{price_book_id}"
    _append_unique(session["observations"]["brand_ids_seen"], brand_id)
    _append_unique(session["observations"]["price_book_ids_seen"], price_book_id)
    return _append_cache_entry(
        session,
        cache_key=cache_key,
        entry_type="category_competition_report",
        payload=payload,
        event_at=event_at,
        action_index=action_index,
    )
