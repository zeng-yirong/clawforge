import os
import json

def build_env():
    # --- 主数据目录 ---
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("data/tmp", exist_ok=True)
    
    # POI 数据
    pois = [
        {
            "poi_id": "charger_01",
            "name": "市中心快充站",
            "category": "charging",
            "lat": 39.9087,
            "lon": 116.3976,
            "address": "北京市东城区东长安街12号",
            "charge_rate_kw": 120,
            "available": True
        },
        {
            "poi_id": "charger_02",
            "name": "机场慢充站",
            "category": "charging",
            "lat": 40.0785,
            "lon": 116.5971,
            "address": "首都机场T3停车场",
            "charge_rate_kw": 0,
            "available": False
        },
        {
            "poi_id": "rest_01",
            "name": "老字号茶楼",
            "category": "food",
            "lat": 39.9112,
            "lon": 116.4213,
            "address": "北京市东城区王府井大街88号",
            "closing_time": "22:00",
            "available": True
        },
        {
            "poi_id": "rest_02",
            "name": "机场快餐",
            "category": "food",
            "lat": 40.0801,
            "lon": 116.5847,
            "address": "首都机场航站楼内",
            "closing_time": "21:00",
            "available": False
        },
        # 干扰项
        {
            "poi_id": "park_01",
            "name": "北海公园",
            "category": "attraction",
            "lat": 39.9263,
            "lon": 116.3891,
            "address": "北京市西城区文津街1号"
        },
        {
            "poi_id": "shop_01",
            "name": "国贸商城",
            "category": "shopping",
            "lat": 39.9095,
            "lon": 116.4595,
            "address": "北京市朝阳区建国门外大街1号"
        },
        {
            "poi_id": "charger_03",
            "name": "朝阳充电站",
            "category": "charging",
            "lat": 39.9209,
            "lon": 116.4432,
            "address": "朝阳区建国路91号",
            "charge_rate_kw": 60,
            "available": True
        },
        {
            "poi_id": "rest_03",
            "name": "朝阳小吃",
            "category": "food",
            "lat": 39.9224,
            "lon": 116.4419,
            "address": "朝阳区工人体育场北路",
            "closing_time": "23:00",
            "available": True
        }
    ]
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump({"pois": pois}, f, ensure_ascii=False, indent=2)

    # 区域数据
    regions = [
        {
            "region_id": "downtown",
            "name": "北京市中心",
            "center": {"lat": 39.9042, "lon": 116.4074},
            "radius_km": 5
        },
        {
            "region_id": "airport",
            "name": "机场区域",
            "center": {"lat": 40.0789, "lon": 116.5909},
            "radius_km": 3
        }
    ]
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump({"regions": regions}, f, ensure_ascii=False, indent=2)

    # 路况数据
    traffic = [
        {"segment_id": "s1", "name": "北二环", "condition": "congested", "congestion_level": 9},
        {"segment_id": "s2", "name": "东二环", "condition": "smooth", "congestion_level": 2},
        {"segment_id": "s3", "name": "机场高速", "condition": "smooth", "congestion_level": 1},
        {"segment_id": "s4", "name": "长安街", "condition": "slow", "congestion_level": 4}
    ]
    with open("data/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump({"road_segments": traffic}, f, ensure_ascii=False, indent=2)

    # 路线偏好（干扰）
    preferences = [
        {"preference_id": "p1", "name": "最短路线", "description": "优先选择距离最短的路线"},
        {"preference_id": "p2", "name": "避开拥堵", "description": "优先选择交通畅通的路线"},
        {"preference_id": "p3", "name": "最快路线", "description": "优先选择时间最短的路线"}
    ]
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump({"preferences": preferences}, f, ensure_ascii=False, indent=2)

    # 干扰文件和目录
    with open("data/backup/pois_backup.json", "w", encoding="utf-8") as f:
        json.dump({"pois": []}, f)
    with open("data/tmp/.lock", "w") as f:
        f.write("")
    with open("data/old_regions.json", "w", encoding="utf-8") as f:
        json.dump({"regions": []}, f)

if __name__ == "__main__":
    build_env()
