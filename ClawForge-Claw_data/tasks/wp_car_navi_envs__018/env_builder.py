import os
import json
import math

def build_env():
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Offline maps (two versions, one obsolete)
    offline_maps = {
        "regions": [
            {
                "region_id": "r1",
                "name": "北京市中心",
                "center": {"lat": 39.9, "lon": 116.4},
                "radius_km": 50,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "r2",
                "name": "朝阳区",
                "center": {"lat": 39.92, "lon": 116.46},
                "radius_km": 30,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "r3",
                "name": "上海市中心",
                "center": {"lat": 31.2, "lon": 121.5},
                "radius_km": 50,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "r_obsolete",
                "name": "旧版北京",
                "center": {"lat": 39.9, "lon": 116.4},
                "radius_km": 100,
                "map_version": "2023.11.20"
            }
        ]
    }
    with open("data/offline_maps.json", "w") as f:
        json.dump(offline_maps, f, indent=2)

    # POIs (charging stations with various traps)
    pois = {
        "pois": [
            # Valid charging stations (map version >= 2024.06.01, category=charging, charge_rate>=50)
            {
                "poi_id": "ch01",
                "name": "天津武清超充站",
                "category": "charging",
                "lat": 39.37,
                "lon": 117.04,
                "address": "天津市武清区",
                "charge_rate_kw": 120,
                "hourly_rate": 0
            },
            {
                "poi_id": "ch03",
                "name": "济南西充电站",
                "category": "charging",
                "lat": 36.65,
                "lon": 116.98,
                "address": "济南市槐荫区",
                "charge_rate_kw": 90,
                "hourly_rate": 0
            },
            {
                "poi_id": "ch05",
                "name": "徐州潘塘充电站",
                "category": "charging",
                "lat": 34.28,
                "lon": 117.21,
                "address": "徐州市云龙区",
                "charge_rate_kw": 60,
                "hourly_rate": 0
            },
            # Trap: obsolete map version (only in old region)
            {
                "poi_id": "ch02",
                "name": "旧版天津充电站",
                "category": "charging",
                "lat": 39.13,
                "lon": 117.20,
                "address": "天津市东丽区（旧版）",
                "charge_rate_kw": 100,
                "hourly_rate": 0
            },
            # Trap: wrong category (hospital)
            {
                "poi_id": "ch04",
                "name": "北京协和医院充电桩",
                "category": "hospital",
                "lat": 39.91,
                "lon": 116.42,
                "address": "北京市东城区",
                "charge_rate_kw": 7,
                "hourly_rate": 0
            },
            # Trap: charge rate too low (<50)
            {
                "poi_id": "ch06",
                "name": "保定慢充站",
                "category": "charging",
                "lat": 38.87,
                "lon": 115.48,
                "address": "保定市竞秀区",
                "charge_rate_kw": 30,
                "hourly_rate": 0
            },
            # Trap: duplicate ID (different name, but same coordinates as ch01)
            {
                "poi_id": "ch07",
                "name": "天津武清充电站（旧名）",
                "category": "charging",
                "lat": 39.37,
                "lon": 117.04,
                "address": "天津市武清区（重复）",
                "charge_rate_kw": 120,
                "hourly_rate": 0
            }
        ]
    }
    with open("data/pois.json", "w") as f:
        json.dump(pois, f, indent=2)

    # Regions (unused for this task but present for realism)
    regions = {
        "regions": [
            {"region_id": "reg_bj", "name": "北京市中心", "center": {"lat": 39.9, "lon": 116.4}, "radius_km": 50},
            {"region_id": "reg_sh", "name": "上海市中心", "center": {"lat": 31.2, "lon": 121.5}, "radius_km": 50}
        ]
    }
    with open("data/regions.json", "w") as f:
        json.dump(regions, f, indent=2)

    # Route preferences (distractor)
    preferences = {
        "preferences": [
            {"preference_id": "p1", "name": "最快路线", "description": "优先选择时间最短的路线"},
            {"preference_id": "p2", "name": "最短路线", "description": "优先选择距离最短的路线"}
        ]
    }
    with open("data/route_preferences.json", "w") as f:
        json.dump(preferences, f, indent=2)

    # Traffic data (distractor)
    traffic = {
        "road_segments": [
            {"segment_id": "s1", "name": "中环路", "condition": "smooth", "congestion_level": 1}
        ]
    }
    with open("data/traffic_data.json", "w") as f:
        json.dump(traffic, f, indent=2)

    # Placeholder for ops directory
    open("ops/.gitkeep", "w").close()

if __name__ == "__main__":
    build_env()
