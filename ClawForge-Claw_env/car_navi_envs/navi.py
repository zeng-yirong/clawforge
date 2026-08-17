from __future__ import annotations

from typing import Any


class NaviController:
    def __init__(self, session: dict[str, Any], store: Any, session_id: str):
        self.session = session
        self.store = store
        self.session_id = session_id

    def _save(self) -> None:
        self.store.save_session(self.session_id, self.session)

    def _get_navigation_state(self) -> dict[str, Any]:
        return self.session.get("navigation_state", {})

    def _update_navigation_state(self, updates: dict[str, Any]) -> None:
        nav_state = self._get_navigation_state()
        nav_state.update(updates)
        self.session["navigation_state"] = nav_state
        self._save()


def start_navigation(controller: NaviController, poi_id: str, repo: Any) -> dict[str, Any]:
    nav_state = controller._get_navigation_state()
    
    if nav_state.get("navigation_active"):
        return {"status": "error", "message": "Navigation is already active"}
    
    poi = repo.get_poi(poi_id)
    if not poi:
        return {"status": "error", "message": f"POI {poi_id} not found"}
    
    destination = {
        "poi_id": poi.get("poi_id"),
        "lat": poi.get("lat"),
        "lon": poi.get("lon"),
        "name": poi.get("name"),
    }
    
    route = _calculate_route(
        nav_state.get("current_location", {}),
        destination,
        nav_state.get("route_preference", "fastest"),
        []
    )
    
    nav_state["destination"] = destination
    nav_state["waypoints"] = []
    nav_state["route"] = route.get("segments", [])
    nav_state["eta_minutes"] = route.get("total_eta_minutes", 30)
    nav_state["distance_remaining_km"] = route.get("total_distance_km", 10.0)
    nav_state["navigation_active"] = True
    
    controller._update_navigation_state(nav_state)
    
    return {
        "status": "success",
        "message": f"Navigation started to {poi.get('name')}",
        "data": {
            "destination": destination,
            "eta_minutes": route.get("total_eta_minutes", 30),
            "distance_km": route.get("total_distance_km", 10.0),
            "route": route.get("segments", []),
        },
    }


def search_poi(repo: Any, category: str | None = None, keyword: str | None = None) -> dict[str, Any]:
    pois = repo.get_pois(category=category, keyword=keyword)
    return {
        "status": "success",
        "message": f"Found {len(pois)} POIs",
        "data": {"pois": pois},
    }


def add_waypoint(controller: NaviController, poi_id: str, repo: Any) -> dict[str, Any]:
    nav_state = controller._get_navigation_state()
    
    if not nav_state.get("navigation_active"):
        return {"status": "error", "message": "No active navigation"}
    
    poi = repo.get_poi(poi_id)
    if not poi:
        return {"status": "error", "message": f"POI {poi_id} not found"}
    
    waypoint = {
        "poi_id": poi.get("poi_id"),
        "lat": poi.get("lat"),
        "lon": poi.get("lon"),
        "name": poi.get("name"),
        "arrived": False,
    }
    
    waypoints = nav_state.get("waypoints", [])
    waypoints.append(waypoint)
    
    route = _calculate_route(
        nav_state.get("current_location", {}),
        nav_state.get("destination", {}),
        nav_state.get("route_preference", "fastest"),
        waypoints,
    )
    
    nav_state["waypoints"] = waypoints
    nav_state["route"] = route.get("segments", [])
    nav_state["eta_minutes"] = route.get("total_eta_minutes", 30)
    nav_state["distance_remaining_km"] = route.get("total_distance_km", 10.0)
    
    controller._update_navigation_state(nav_state)
    
    return {
        "status": "success",
        "message": f"Added waypoint: {poi.get('name')}",
        "data": {"waypoints": waypoints, "eta_minutes": nav_state["eta_minutes"]},
    }


def remove_waypoint(controller: NaviController, waypoint_index: int) -> dict[str, Any]:
    nav_state = controller._get_navigation_state()
    
    if not nav_state.get("navigation_active"):
        return {"status": "error", "message": "No active navigation"}
    
    waypoints = nav_state.get("waypoints", [])
    
    if waypoint_index < 0 or waypoint_index >= len(waypoints):
        return {"status": "error", "message": f"Invalid waypoint index: {waypoint_index}"}
    
    removed = waypoints.pop(waypoint_index)
    
    route = _calculate_route(
        nav_state.get("current_location", {}),
        nav_state.get("destination", {}),
        nav_state.get("route_preference", "fastest"),
        waypoints,
    )
    
    nav_state["waypoints"] = waypoints
    nav_state["route"] = route.get("segments", [])
    nav_state["eta_minutes"] = route.get("total_eta_minutes", 30)
    nav_state["distance_remaining_km"] = route.get("total_distance_km", 10.0)
    
    controller._update_navigation_state(nav_state)
    
    return {
        "status": "success",
        "message": f"Removed waypoint: {removed.get('name')}",
        "data": {"waypoints": waypoints, "eta_minutes": nav_state["eta_minutes"]},
    }


def set_route_preference(controller: NaviController, preference: str, repo: Any) -> dict[str, Any]:
    valid_preferences = [p.get("preference_id") for p in repo.get_route_preferences()]
    if preference not in valid_preferences:
        return {"status": "error", "message": f"Invalid route preference: {preference}"}
    
    nav_state = controller._get_navigation_state()
    nav_state["route_preference"] = preference
    
    if nav_state.get("navigation_active"):
        route = _calculate_route(
            nav_state.get("current_location", {}),
            nav_state.get("destination", {}),
            preference,
            nav_state.get("waypoints", []),
        )
        nav_state["route"] = route.get("segments", [])
        nav_state["eta_minutes"] = route.get("total_eta_minutes", 30)
        nav_state["distance_remaining_km"] = route.get("total_distance_km", 10.0)
    
    controller._update_navigation_state(nav_state)
    
    return {
        "status": "success",
        "message": f"Route preference set to: {preference}",
        "data": {"route_preference": preference, "eta_minutes": nav_state.get("eta_minutes", 0)},
    }


def reroute(controller: NaviController) -> dict[str, Any]:
    nav_state = controller._get_navigation_state()
    
    if not nav_state.get("navigation_active"):
        return {"status": "error", "message": "No active navigation"}
    
    route = _calculate_route(
        nav_state.get("current_location", {}),
        nav_state.get("destination", {}),
        nav_state.get("route_preference", "fastest"),
        nav_state.get("waypoints", []),
    )
    
    nav_state["route"] = route.get("segments", [])
    nav_state["eta_minutes"] = route.get("total_eta_minutes", 30)
    nav_state["distance_remaining_km"] = route.get("total_distance_km", 10.0)
    
    controller._update_navigation_state(nav_state)
    
    return {
        "status": "success",
        "message": "Route recalculated",
        "data": {
            "eta_minutes": nav_state["eta_minutes"],
            "distance_km": nav_state["distance_remaining_km"],
            "route": nav_state["route"],
        },
    }


def arrive_waypoint(controller: NaviController, waypoint_index: int) -> dict[str, Any]:
    nav_state = controller._get_navigation_state()
    
    if not nav_state.get("navigation_active"):
        return {"status": "error", "message": "No active navigation"}
    
    waypoints = nav_state.get("waypoints", [])
    
    if waypoint_index < 0 or waypoint_index >= len(waypoints):
        return {"status": "error", "message": f"Invalid waypoint index: {waypoint_index}"}
    
    waypoints[waypoint_index]["arrived"] = True
    
    current = waypoints[waypoint_index]
    nav_state["current_location"] = {
        "lat": current.get("lat"),
        "lon": current.get("lon"),
        "name": current.get("name"),
    }
    
    route = _calculate_route(
        nav_state.get("current_location", {}),
        nav_state.get("destination", {}),
        nav_state.get("route_preference", "fastest"),
        waypoints[waypoint_index + 1:],
    )
    
    nav_state["waypoints"] = waypoints[waypoint_index + 1:]
    nav_state["route"] = route.get("segments", [])
    nav_state["eta_minutes"] = route.get("total_eta_minutes", 30)
    nav_state["distance_remaining_km"] = route.get("total_distance_km", 10.0)
    
    controller._update_navigation_state(nav_state)
    
    return {
        "status": "success",
        "message": f"Arrived at waypoint: {current.get('name')}",
        "data": {
            "remaining_waypoints": len(nav_state["waypoints"]),
            "eta_minutes": nav_state["eta_minutes"],
        },
    }


def arrive_destination(controller: NaviController) -> dict[str, Any]:
    nav_state = controller._get_navigation_state()
    
    if not nav_state.get("navigation_active"):
        return {"status": "error", "message": "No active navigation"}
    
    destination = nav_state.get("destination", {})
    
    nav_state["current_location"] = {
        "lat": destination.get("lat"),
        "lon": destination.get("lon"),
        "name": destination.get("name"),
    }
    nav_state["destination"] = None
    nav_state["waypoints"] = []
    nav_state["route"] = []
    nav_state["eta_minutes"] = 0
    nav_state["distance_remaining_km"] = 0.0
    nav_state["navigation_active"] = False
    
    controller._update_navigation_state(nav_state)
    
    return {
        "status": "success",
        "message": "Arrived at destination",
        "data": {"destination": destination.get("name")},
    }


def cancel_navigation(controller: NaviController) -> dict[str, Any]:
    nav_state = controller._get_navigation_state()
    
    nav_state["destination"] = None
    nav_state["waypoints"] = []
    nav_state["route"] = []
    nav_state["eta_minutes"] = 0
    nav_state["distance_remaining_km"] = 0.0
    nav_state["navigation_active"] = False
    
    controller._update_navigation_state(nav_state)
    
    return {
        "status": "success",
        "message": "Navigation cancelled",
    }


def _calculate_route(
    origin: dict[str, Any],
    destination: dict[str, Any],
    preference: str,
    waypoints: list[dict[str, Any]],
) -> dict[str, Any]:
    if not destination:
        return {"segments": [], "total_eta_minutes": 0, "total_distance_km": 0.0}
    
    origin_lat = origin.get("lat", 0)
    origin_lon = origin.get("lon", 0)
    dest_lat = destination.get("lat", 0)
    dest_lon = destination.get("lon", 0)
    
    import math
    lat_diff = abs(dest_lat - origin_lat)
    lon_diff = abs(dest_lon - origin_lon)
    distance_deg = math.sqrt(lat_diff ** 2 + lon_diff ** 2)
    distance_km = distance_deg * 111.0
    
    eta_minutes = int(distance_km * 2) if preference == "fastest" else int(distance_km * 2.5)
    
    segments = []
    all_points = [origin] + waypoints + [destination]
    
    for i in range(len(all_points) - 1):
        p1 = all_points[i]
        p2 = all_points[i + 1]
        seg_lat_diff = abs(p2.get("lat", 0) - p1.get("lat", 0))
        seg_lon_diff = abs(p2.get("lon", 0) - p1.get("lon", 0))
        seg_distance = math.sqrt(seg_lat_diff ** 2 + seg_lon_diff ** 2) * 111.0
        segments.append({
            "name": f"Segment {i + 1}",
            "distance": round(seg_distance, 1),
            "eta": int(seg_distance * 2),
        })
    
    return {
        "segments": segments,
        "total_eta_minutes": eta_minutes,
        "total_distance_km": round(distance_km, 1),
    }
