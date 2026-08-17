from __future__ import annotations

import re
from typing import Any


def list_platforms(repo) -> list[dict[str, Any]]:
    platform_ids = repo.list_platform_ids()
    platforms = []
    for pid in platform_ids:
        p = repo.get_platform(pid)
        p["platform_id"] = pid
        platforms.append(p)
    return platforms


def get_platform(repo, platform_id: str) -> dict[str, Any]:
    platform = repo.get_platform(platform_id)
    platform["platform_id"] = platform_id
    return platform


def search_flights(
    repo,
    platform_id: str,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    cabin_class: str = "economy",
    passengers: int = 1,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    platform = repo.get_platform(platform_id)
    if not platform.get("is_active", True):
        return {"success": False, "error": f"Platform {platform_id} is not active"}

    flights = _generate_mock_flights(origin, destination, departure_date, cabin_class, passengers, platform)
    return {
        "success": True,
        "platform_id": platform_id,
        "platform_name": platform["name"],
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "cabin_class": cabin_class,
        "passengers": passengers,
        "flights": flights,
        "searched_at": event_at,
    }


def compare_platform_prices(
    repo,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    cabin_class: str = "economy",
    passengers: int = 1,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    platform_ids = repo.list_platform_ids()
    results = []
    for pid in platform_ids:
        p = repo.get_platform(pid)
        if not p.get("is_active", True):
            continue
        flights = _generate_mock_flights(origin, destination, departure_date, cabin_class, passengers, p)
        best_price = min(f["price"] for f in flights) if flights else None
        results.append({
            "platform_id": pid,
            "platform_name": p["name"],
            "best_price": best_price,
            "flight_count": len(flights),
            "flights": flights[:3],
        })
    results.sort(key=lambda x: x["best_price"] if x["best_price"] else float("inf"))
    return {
        "success": True,
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "cabin_class": cabin_class,
        "passengers": passengers,
        "platform_comparison": results,
        "best_platform": results[0]["platform_id"] if results else None,
        "best_price": results[0]["best_price"] if results else None,
        "compared_at": event_at,
    }


def get_platform_fee_structure(
    repo,
    platform_id: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    platform = repo.get_platform(platform_id)
    return {
        "success": True,
        "platform_id": platform_id,
        "platform_name": platform["name"],
        "transaction_fees": platform.get("transaction_fee", 0),
        "service_fees": platform.get("service_fee", 0),
        "payment_methods": platform.get("payment_methods", []),
        "cancellation_policy": platform.get("cancellation_policy", ""),
    }


def filter_platforms_by_region(
    repo,
    region: str,
    event_at: str = "",
    action_index: int = 0,
) -> list[dict[str, Any]]:
    all_platforms = list_platforms(repo)
    region_lower = region.lower()
    return [p for p in all_platforms if region_lower in p.get("region", "").lower()]


def get_platform_discounts(
    repo,
    platform_id: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    platform = repo.get_platform(platform_id)
    return {
        "success": True,
        "platform_id": platform_id,
        "platform_name": platform["name"],
        "discounts": platform.get("discounts", []),
        "promotions": platform.get("promotions", []),
        "loyalty_program": platform.get("loyalty_program", {}),
    }


def calculate_total_cost(
    repo,
    platform_id: str,
    base_price: float,
    cabin_class: str = "economy",
    baggage_fee: float = 0,
    seat_selection_fee: float = 0,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    platform = repo.get_platform(platform_id)
    tx_fee = base_price * platform.get("transaction_fee", 0)
    svc_fee = platform.get("service_fee", 0)
    cabin_multiplier = {"economy": 1.0, "premium_economy": 1.5, "business": 2.5, "first": 4.0}
    cabin_adj = base_price * (cabin_multiplier.get(cabin_class, 1.0) - 1.0)
    total = base_price + tx_fee + svc_fee + baggage_fee + seat_selection_fee + cabin_adj
    return {
        "success": True,
        "platform_id": platform_id,
        "base_price": base_price,
        "cabin_class": cabin_class,
        "cabin_adjustment": cabin_adj,
        "transaction_fee": tx_fee,
        "service_fee": svc_fee,
        "baggage_fee": baggage_fee,
        "seat_selection_fee": seat_selection_fee,
        "total_cost": total,
        "currency": platform.get("currency", "USD"),
    }


def _generate_mock_flights(
    origin: str,
    destination: str,
    departure_date: str,
    cabin_class: str,
    passengers: int,
    platform: dict[str, Any],
) -> list[dict[str, Any]]:
    airlines = ["AirGlobal", "SkyConnect", "AeroLine", "Pacific Wings", "EuroJet"]
    flights = []
    for i in range(min(5, hash(f"{origin}{destination}{platform['platform_id']}") % 10 + 1)):
        base_price = 200 + (hash(f"{platform['platform_id']}{i}") % 800)
        flights.append({
            "flight_number": f"{airlines[i % len(airlines)]}{100 + i}",
            "origin": origin,
            "destination": destination,
            "departure_time": f"{departure_date}T{8 + i * 2}:00",
            "arrival_time": f"{departure_date}T{12 + i * 2}:00",
            "duration_minutes": 240 + (i * 30),
            "price": base_price * ({"economy": 1, "premium_economy": 1.5, "business": 2.5, "first": 4.0}.get(cabin_class, 1)),
            "seats_available": 10 + (i * 5),
            "cabin_class": cabin_class,
            "airline": airlines[i % len(airlines)],
        })
    return flights
