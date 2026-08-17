from __future__ import annotations

from copy import deepcopy


def build_price_book_summary(price_book: dict[str, object]) -> dict[str, object]:
    return {
        "price_book_id": price_book["price_book_id"],
        "version": price_book["version"],
        "region": price_book["region"],
        "status": price_book["status"],
        "is_current": price_book["is_current"],
        "effective_from": price_book["effective_from"],
        "entry_count": len(price_book.get("entries", [])),
    }


def list_price_books(
    session: dict[str, object],
    *,
    status: str | None = None,
    current_only: bool = False,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    status_lower = status.strip().lower() if status else None

    for price_book in session["price_books"]:
        if status_lower and str(price_book["status"]).lower() != status_lower:
            continue
        if current_only and not price_book.get("is_current", False):
            continue
        results.append(build_price_book_summary(price_book))

    results.sort(key=lambda item: (not bool(item["is_current"]), str(item["effective_from"])), reverse=False)
    return results


def get_price_book(session: dict[str, object], price_book_id: str) -> dict[str, object]:
    for price_book in session["price_books"]:
        if price_book["price_book_id"] == price_book_id:
            return deepcopy(price_book)
    raise KeyError(f"Price book not found: {price_book_id}")


def get_price_book_entry_map(session: dict[str, object], price_book_id: str) -> dict[str, dict[str, object]]:
    price_book = get_price_book(session, price_book_id)
    return {entry["sku_id"]: entry for entry in price_book.get("entries", [])}
