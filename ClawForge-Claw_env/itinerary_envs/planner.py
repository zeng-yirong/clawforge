from __future__ import annotations

from typing import Any


class ItineraryController:
    def __init__(self, session: dict[str, Any], store: Any, session_id: str):
        self.session = session
        self.store = store
        self.session_id = session_id

    def _save(self) -> None:
        self.store.save_session(self.session_id, self.session)

    def _get_itinerary_state(self) -> dict[str, Any]:
        return self.session.get("itinerary_state", {})

    def _update_itinerary_state(self, updates: dict[str, Any]) -> None:
        itinerary_state = self._get_itinerary_state()
        itinerary_state.update(updates)
        self.session["itinerary_state"] = itinerary_state
        self._save()


def search_routes(
    repo: Any,
    origin: str,
    destination: str,
) -> dict[str, Any]:
    route = repo.get_route(origin, destination)
    if not route:
        return {"status": "error", "message": f"No route found from {origin} to {destination}"}

    transport_options = []
    for key in ["high_speed_train", "direct_flight", "普通火车"]:
        if key in route:
            transport_options.append({
                "mode": key,
                "duration_min": route[key].get("duration_min"),
                "price_cny": route[key].get("price_cny"),
                "frequency": route[key].get("frequency"),
            })

    return {
        "status": "success",
        "data": {
            "route_id": route.get("route_id"),
            "origin": origin,
            "destination": destination,
            "distance_km": route.get("distance_km"),
            "transport_options": transport_options,
        },
    }


def compare_transport(route: dict[str, Any]) -> dict[str, Any]:
    if route.get("status") == "error":
        return route

    data = route.get("data", {})
    options = data.get("transport_options", [])

    if not options:
        return {"status": "error", "message": "No transport options to compare"}

    comparison = []
    for opt in options:
        duration_hours = opt.get("duration_min", 0) / 60
        price = opt.get("price_cny", 0)
        cost_per_hour = price / duration_hours if duration_hours > 0 else 0
        comparison.append({
            "mode": opt.get("mode"),
            "duration_min": opt.get("duration_min"),
            "duration_hours": round(duration_hours, 2),
            "price_cny": price,
            "cost_per_hour": round(cost_per_hour, 2),
            "recommendation": _get_recommendation(opt.get("mode"), duration_hours, price),
        })

    comparison.sort(key=lambda x: x["duration_min"])
    fastest = comparison[0] if comparison else None
    comparison.sort(key=lambda x: x["price_cny"])
    cheapest = comparison[0] if comparison else None

    return {
        "status": "success",
        "data": {
            "options": comparison,
            "fastest": fastest,
            "cheapest": cheapest,
            "summary": {
                "total_options": len(comparison),
                "duration_range": {
                    "min_minutes": min(o["duration_min"] for o in comparison) if comparison else 0,
                    "max_minutes": max(o["duration_min"] for o in comparison) if comparison else 0,
                },
                "price_range": {
                    "min_cny": min(o["price_cny"] for o in comparison) if comparison else 0,
                    "max_cny": max(o["price_cny"] for o in comparison) if comparison else 0,
                },
            },
        },
    }


def _get_recommendation(mode: str, duration_hours: float, price: float) -> str:
    if mode == "high_speed_train":
        if duration_hours < 3:
            return "推荐：高铁便捷舒适"
        return "推荐：高铁性价比高"
    elif mode == "direct_flight":
        if duration_hours > 4:
            return "推荐：飞机速度快"
        return "考虑：飞行时间短但价格较高"
    elif mode == "普通火车":
        return "经济选择：普通火车最便宜"
    return ""


def plan_transfer(
    repo: Any,
    origin: str,
    destination: str,
    waypoints: list[str],
) -> dict[str, Any]:
    all_cities = {c["city_id"]: c for c in repo.list_cities()}
    if origin not in all_cities:
        return {"status": "error", "message": f"Origin city {origin} not found"}
    if destination not in all_cities:
        return {"status": "error", "message": f"Destination city {destination} not found"}

    for wp in waypoints:
        if wp not in all_cities:
            return {"status": "error", "message": f"Waypoint city {wp} not found"}

    stops = [origin] + waypoints + [destination]
    legs = []
    total_duration = 0
    total_cost = 0

    for i in range(len(stops) - 1):
        leg_origin = stops[i]
        leg_dest = stops[i + 1]
        route = repo.get_route(leg_origin, leg_dest)

        if not route:
            direct_route = _find_alternative_route(repo, leg_origin, leg_dest)
            if direct_route:
                route = direct_route

        if not route:
            return {
                "status": "error",
                "message": f"No route found from {leg_origin} to {leg_dest}",
            }

        best_option = None
        for key in ["high_speed_train", "direct_flight", "普通火车"]:
            if key in route:
                if best_option is None:
                    best_option = {"mode": key, **route[key]}
                elif route[key].get("duration_min", 999) < best_option.get("duration_min", 999):
                    best_option = {"mode": key, **route[key]}

        if best_option:
            total_duration += best_option.get("duration_min", 0)
            total_cost += best_option.get("price_cny", 0)
            legs.append({
                "leg_index": i + 1,
                "from": leg_origin,
                "to": leg_dest,
                "route_id": route.get("route_id"),
                "distance_km": route.get("distance_km"),
                "transport": best_option,
            })

    hubs = repo.get_transfer_hubs()
    hub_names = {h["city"]: h["name"] for h in hubs}

    return {
        "status": "success",
        "data": {
            "stops": stops,
            "legs": legs,
            "total_duration_min": total_duration,
            "total_cost_cny": total_cost,
            "hub_connections": [
                {
                    "from_city": leg["from"],
                    "from_hub": hub_names.get(leg["from"], leg["from"]),
                    "to_city": leg["to"],
                    "to_hub": hub_names.get(leg["to"], leg["to"]),
                    "mode": leg["transport"].get("mode"),
                }
                for leg in legs
            ],
        },
    }


def _find_alternative_route(repo: Any, origin: str, destination: str) -> dict[str, Any] | None:
    routes_from_origin = repo.list_routes_from(origin)
    for route in routes_from_origin:
        if route.get("destination") == destination:
            return route
    return None


def generate_itinerary(
    ctrl: Any,
    routes: dict[str, Any],
    preferences: dict[str, Any],
) -> dict[str, Any]:
    if routes.get("status") == "error":
        return routes

    route_data = routes.get("data", {})
    legs = route_data.get("legs", [])
    origin = route_data.get("stops", [None])[0] if route_data.get("stops") else None
    destination = route_data.get("stops", [None])[-1] if route_data.get("stops") else None

    if not legs:
        return {"status": "error", "message": "No route legs available"}

    total_duration = sum(leg["transport"].get("duration_min", 0) for leg in legs)
    total_cost = sum(leg["transport"].get("price_cny", 0) for leg in legs)

    itinerary_segments = []
    for leg in legs:
        transport = leg["transport"]
        mode_name = _get_mode_display_name(transport.get("mode", ""))
        itinerary_segments.append({
            "segment_number": leg["leg_index"],
            "from": leg["from"],
            "to": leg["to"],
            "distance_km": leg.get("distance_km", 0),
            "transport_mode": transport.get("mode", ""),
            "transport_name": mode_name,
            "duration_min": transport.get("duration_min", 0),
            "price_cny": transport.get("price_cny", 0),
        })

    preference = preferences.get("route_preference", "balanced")
    optimized_for = _get_optimization_note(preference, itinerary_segments)

    itinerary = {
        "status": "success",
        "data": {
            "origin": origin,
            "destination": destination,
            "total_segments": len(itinerary_segments),
            "total_duration_min": total_duration,
            "total_duration_hours": round(total_duration / 60, 2),
            "total_cost_cny": total_cost,
            "segments": itinerary_segments,
            "route_preference": preference,
            "optimization_note": optimized_for,
            "generated_timestamp": None,
        },
    }

    ctrl._update_itinerary_state({
        "origin": origin,
        "destination": destination,
        "waypoints": route_data.get("stops", [])[1:-1] if route_data.get("stops") else [],
        "search_results": [routes],
        "generated_itinerary": itinerary,
        "route_preference": preference,
    })

    return itinerary


def _get_mode_display_name(mode: str) -> str:
    names = {
        "high_speed_train": "高铁",
        "direct_flight": "直飞航班",
        "普通火车": "普通火车",
    }
    return names.get(mode, mode)


def _get_optimization_note(preference: str, segments: list[dict[str, Any]]) -> str:
    if preference == "fastest":
        return "已按最快时间优化路线"
    elif preference == "cheapest":
        return "已按最低成本优化路线"
    return "已按时间成本平衡优化路线"
