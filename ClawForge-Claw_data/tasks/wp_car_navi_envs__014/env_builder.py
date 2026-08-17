import os
import json

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)

    # ---- 最新版 POI 数据 (v2) ----
    pois_v2 = {
        "version": "2025.03",
        "pois": [
            {"poi_id": "poi_101", "name": "故宫博物院", "category": "attraction", "lat": 39.9163, "lon": 116.3972},
            {"poi_id": "poi_102", "name": "天安门广场", "category": "attraction", "lat": 39.9054, "lon": 116.3976},
            {"poi_id": "poi_103", "name": "颐和园", "category": "attraction", "lat": 39.9999, "lon": 116.2755},
            {"poi_id": "poi_104", "name": "国家博物馆", "category": "attraction", "lat": 39.9051, "lon": 116.3944},
            {"poi_id": "poi_105", "name": "鸟巢", "category": "attraction", "lat": 39.9945, "lon": 116.3964},
            {"poi_id": "poi_106", "name": "望京SOHO", "category": "charging", "lat": 39.9882, "lon": 116.4745}
        ]
    }
    with open("data/pois_v2.json", "w", encoding="utf-8") as f:
        json.dump(pois_v2, f, ensure_ascii=False)

    # ---- 旧版 POI 数据 (v1) - 干扰：ID 不同，但名称部分相同 ----
    pois_v1 = {
        "version": "2024.10",
        "pois": [
            {"poi_id": "poi_001", "name": "故宫博物院", "category": "attraction", "lat": 39.9160, "lon": 116.3970},
            {"poi_id": "poi_002", "name": "天安门", "category": "attraction", "lat": 39.9050, "lon": 116.3975},
            {"poi_id": "poi_003", "name": "颐和园", "category": "attraction", "lat": 39.9990, "lon": 116.2750},
        ]
    }
    with open("data/pois_v1.json", "w", encoding="utf-8") as f:
        json.dump(pois_v1, f, ensure_ascii=False)

    # ---- 损坏的假数据 (v3) - 格式错误 ----
    with open("data/pois_v3.json", "w", encoding="utf-8") as f:
        f.write("这不是JSON，是一段乱码。")

    # ---- 其他业务数据（干扰） ----
    regions = {
        "regions": [
            {"region_id": "R01", "name": "北京市中心", "center": {"lat": 39.9042, "lon": 116.4074}, "radius_km": 10},
            {"region_id": "R02", "name": "朝阳区", "center": {"lat": 39.9219, "lon": 116.4431}, "radius_km": 15}
        ]
    }
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump(regions, f, ensure_ascii=False)

    traffic = {
        "road_segments": [
            {"segment_id": "S01", "name": "中环路", "condition": "congested", "congestion_level": 8}
        ]
    }
    with open("data/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump(traffic, f, ensure_ascii=False)

    # ---- 创建 ops 目录（空，等待 agent 写入） ----
    os.makedirs("ops", exist_ok=True)

    # ---- 用户手写行程 plan.txt ----
    plan_content = """故宫博物院
天安门广场
颐和园
国家博物馆
"""
    with open("plan.txt", "w", encoding="utf-8") as f:
        f.write(plan_content)

if __name__ == "__main__":
    build_env()
