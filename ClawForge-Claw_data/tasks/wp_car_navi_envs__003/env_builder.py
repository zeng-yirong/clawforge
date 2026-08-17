import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/sessions", exist_ok=True)
    os.makedirs("traffic", exist_ok=True)
    os.makedirs("pois", exist_ok=True)

    # ========== 交通数据 ==========
    traffic_data = {
        "road_segments": [
            {"segment_id": "seg_01", "name": "中环路", "condition": "smooth", "congestion_level": 1},
            {"segment_id": "seg_02", "name": "外环高速", "condition": "congested", "congestion_level": 4},
            {"segment_id": "seg_03", "name": "延安高架路", "condition": "slow", "congestion_level": 2},
            {"segment_id": "seg_04", "name": "沪渝高速", "condition": "smooth", "congestion_level": 0},
            {"segment_id": "seg_05", "name": "陆家嘴环路", "condition": "smooth", "congestion_level": 1},
            {"segment_id": "seg_06", "name": "中环路(北段)", "condition": "congested", "congestion_level": 5},
        ]
    }
    with open("traffic/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump(traffic_data, f, ensure_ascii=False, indent=2)

    # ========== POI数据 ==========
    pois_data = {
        "pois": [
            {"poi_id": "poi_charge_01", "name": "超充站A", "category": "charging", "lat": 31.22, "lon": 121.48, "address": "浦东大道100号", "charge_rate_kw": 120},
            {"poi_id": "poi_charge_02", "name": "快充站B", "category": "charging", "lat": 31.30, "lon": 121.50, "address": "世纪大道200号", "charge_rate_kw": 60},
            {"poi_id": "poi_charge_03", "name": "超充站C", "category": "charging", "lat": 31.14, "lon": 121.56, "address": "南京路300号", "charge_rate_kw": 120},
            {"poi_id": "poi_charge_04", "name": "快充站D", "category": "charging", "lat": 31.20, "lon": 121.60, "address": "延安路400号", "charge_rate_kw": 60},
            {"poi_id": "poi_food_01", "name": "麦当劳", "category": "food", "lat": 31.25, "lon": 121.45, "address": "人民广场1号", "hourly_rate": 0},
            {"poi_id": "poi_hospital_01", "name": "瑞金医院", "category": "hospital", "lat": 31.20, "lon": 121.47, "address": "瑞金二路", "hourly_rate": 0},
        ]
    }
    with open("pois/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois_data, f, ensure_ascii=False, indent=2)

    # ========== 会话数据 ==========
    sessions = [
        {
            "session_id": "session_001",
            "status": "active",
            "current_location": {"lat": 31.23, "lon": 121.47},
            "destination": {"lat": 31.45, "lon": 121.80},
            "route_segments": ["seg_01", "seg_02", "seg_03"],
            "waypoints": []
        },
        {
            "session_id": "session_002",
            "status": "active",
            "current_location": {"lat": 31.15, "lon": 121.55},
            "destination": {"lat": 31.30, "lon": 121.70},
            "route_segments": ["seg_05", "seg_06"],
            "waypoints": []
        },
        {
            "session_id": "session_003",
            "status": "active",
            "current_location": {"lat": 31.28, "lon": 121.50},
            "destination": {"lat": 31.35, "lon": 121.65},
            "route_segments": ["seg_01", "seg_03"],
            "waypoints": []
        },
        {
            "session_id": "session_004",
            "status": "completed",
            "current_location": {"lat": 31.30, "lon": 121.55},
            "destination": {"lat": 31.40, "lon": 121.70},
            "route_segments": ["seg_02"],
            "waypoints": ["poi_food_01"]
        },
        {
            "session_id": "session_005",
            "status": "cancelled",
            "current_location": {"lat": 31.20, "lon": 121.50},
            "destination": {"lat": 31.25, "lon": 121.60},
            "route_segments": ["seg_06"],
            "waypoints": []
        },
    ]
    for sess in sessions:
        fname = f"data/sessions/{sess['session_id']}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(sess, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
