import os
import json
from datetime import datetime, timedelta

def build_env():
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 创建干扰的日志行（其他session）
    other_session_rows = [
        "2025-03-01 10:00:00 session=navi-xyz001 poi_id=poi_dummy1",
        "2025-03-01 10:05:12 session=navi-xyz001 poi_id=poi_dummy2",
        "2025-03-01 10:10:30 session=navi-xyz002 poi_id=poi_garbage",
        "2025-03-01 10:12:00 session=navi-xyz002 poi_id=poi_garbage",  # 重复
        "2025-03-01 10:15:00 session=navi-xyz003 poi_id=poi_invalid999",  # 无效ID
    ]

    # 目标session的三次搜索（按时间顺序）
    target_rows = [
        "2025-03-01 14:20:00 session=navi-20250301-abc poi_id=poi_001",
        "2025-03-01 14:25:30 session=navi-20250301-abc poi_id=poi_002",
        "2025-03-01 14:32:15 session=navi-20250301-abc poi_id=poi_003",
    ]

    # 混合写入日志（保证目标session的行在文件中按时间顺序出现，但穿插干扰行）
    # 为了增加难度，顺序打乱：先写两条干扰，再写目标第一条，再写一条干扰，再写目标第二、三条，再写剩余干扰
    all_lines = [
        other_session_rows[0],
        other_session_rows[1],
        target_rows[0],
        other_session_rows[2],
        target_rows[1],
        target_rows[2],
        other_session_rows[3],
        other_session_rows[4],
    ]

    with open("logs/search_history.log", "w", encoding="utf-8") as f:
        for line in all_lines:
            f.write(line + "\n")

    # 创建data/pois.json，包含三个有效的poi和一些干扰poi
    pois = {
        "pois": [
            {"poi_id": "poi_001", "name": "服务区A", "category": "rest_area", "lat": 31.2, "lon": 121.5, "address": "沪渝高速"},
            {"poi_id": "poi_002", "name": "充电站B", "category": "charging", "lat": 31.3, "lon": 121.6, "address": "外环高速", "charge_rate_kw": 120},
            {"poi_id": "poi_003", "name": "餐厅C", "category": "food", "lat": 31.4, "lon": 121.7, "address": "市中心"},
            {"poi_id": "poi_dummy1", "name": "干扰点1", "category": "attraction", "lat": 30.0, "lon": 120.0, "address": "郊区"},
            {"poi_id": "poi_dummy2", "name": "干扰点2", "category": "parking", "lat": 30.1, "lon": 120.1, "address": "机场"},
            {"poi_id": "poi_invalid999", "name": "已关闭点", "category": "hospital", "lat": 29.0, "lon": 119.0, "address": "废弃"}
        ]
    }
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

    # 创建route_preferences.json，包含“最短路线”
    preferences = {
        "preferences": [
            {"preference_id": "pref_01", "name": "最快路线", "description": "优先选择时间最短的路线"},
            {"preference_id": "pref_02", "name": "最短路线", "description": "优先选择距离最短的路线"},
            {"preference_id": "pref_03", "name": "避开拥堵", "description": "优先选择交通畅通的路线"},
        ]
    }
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump(preferences, f, ensure_ascii=False, indent=2)

    # 其他数据文件（纯装饰，不参与评分）
    traffic = {
        "road_segments": [
            {"segment_id": "seg_01", "name": "中环路", "condition": "congested", "congestion_level": 8},
            {"segment_id": "seg_02", "name": "外环高速", "condition": "smooth", "congestion_level": 2},
        ]
    }
    with open("data/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump(traffic, f, ensure_ascii=False, indent=2)

    regions = {
        "regions": [
            {"region_id": "reg_01", "name": "北京市中心", "center": {"lat": 39.9, "lon": 116.4}, "radius_km": 10},
        ]
    }
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump(regions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
