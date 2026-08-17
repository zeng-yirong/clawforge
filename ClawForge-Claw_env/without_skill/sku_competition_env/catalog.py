from __future__ import annotations

from copy import deepcopy


def _normalize_query(value: str | None) -> str:
    return value.strip().lower() if value else ""


def build_brand_summary(brand: dict[str, object]) -> dict[str, object]:
    return {
        "brand_id": brand["brand_id"],
        "brand_name": brand["brand_name"],
        "hero_category_id": brand["hero_category_id"],
        "hero_category_name": brand["hero_category_name"],
        "positioning": brand["positioning"],
        "region_focus": brand["region_focus"],
    }


def list_brands(
    session: dict[str, object],
    *,
    query: str = "",
    category_id: str | None = None,
    limit: int | None = None,
) -> list[dict[str, object]]:
    query_lower = _normalize_query(query)
    category_lower = _normalize_query(category_id)
    results: list[dict[str, object]] = []

    for brand in session["brands"]:
        searchable = " ".join(
            [
                str(brand["brand_name"]),
                str(brand["positioning"]),
                str(brand["hero_category_name"]),
            ]
        ).lower()
        if query_lower and query_lower not in searchable:
            continue
        if category_lower and str(brand["hero_category_id"]).lower() != category_lower:
            continue
        results.append(build_brand_summary(brand))

    results.sort(key=lambda item: str(item["brand_name"]))
    return results[:limit] if limit is not None else results


def get_brand(session: dict[str, object], brand_id: str) -> dict[str, object]:
    for brand in session["brands"]:
        if brand["brand_id"] == brand_id:
            return deepcopy(brand)
    raise KeyError(f"Brand not found: {brand_id}")


def build_sku_summary(sku: dict[str, object]) -> dict[str, object]:
    return {
        "sku_id": sku["sku_id"],
        "brand_id": sku["brand_id"],
        "brand_name": sku["brand_name"],
        "category_id": sku["category_id"],
        "category_name": sku["category_name"],
        "sku_name": sku["sku_name"],
        "size_value": sku["size_value"],
        "size_unit": sku["size_unit"],
        "pack_count": sku["pack_count"],
        "status": sku["status"],
    }


def list_skus(
    session: dict[str, object],
    *,
    brand_id: str | None = None,
    category_id: str | None = None,
    query: str = "",
    status: str | None = "active",
    limit: int | None = None,
) -> list[dict[str, object]]:
    query_lower = _normalize_query(query)
    category_lower = _normalize_query(category_id)
    status_lower = _normalize_query(status)
    results: list[dict[str, object]] = []

    for sku in session["skus"]:
        if brand_id and sku["brand_id"] != brand_id:
            continue
        if category_lower and str(sku["category_id"]).lower() != category_lower:
            continue
        if status_lower and str(sku["status"]).lower() != status_lower:
            continue
        searchable = " ".join(
            [
                str(sku["sku_name"]),
                str(sku["brand_name"]),
                " ".join(str(item) for item in sku.get("selling_points", [])),
                " ".join(str(item) for item in sku.get("ingredients", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable:
            continue
        results.append(build_sku_summary(sku))

    results.sort(key=lambda item: (str(item["brand_name"]), str(item["sku_name"])))
    return results[:limit] if limit is not None else results


def get_sku(session: dict[str, object], sku_id: str) -> dict[str, object]:
    for sku in session["skus"]:
        if sku["sku_id"] == sku_id:
            return deepcopy(sku)
    raise KeyError(f"SKU not found: {sku_id}")
