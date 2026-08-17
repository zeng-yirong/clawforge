import os
import json
import math

def build_env():
    # 创建必要的目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 构造 scenarios.json（包含目标 scenario 和干扰）
    scenarios = {
        "scenarios": [
            {
                "id": "navi_021",
                "start": {"lat": 39.9042, "lon": 116.4074},
                "radius_km": 50
            },
            {
                "id": "navi_022",
                "start": {"lat": 31.2304, "lon": 121.4737},
                "radius_km": 30
            },
            {
                "id": "navi_023",
                "start": {"lat": 30.5728, "lon": 104.0668},
                "radius_km": 40
            }
        ]
    }
    with open("data/scenarios.json", "w", encoding="utf-8") as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

    # 2. 构造 pois.json（包含合格充电站、不合格充电站、其他类别干扰）
    pois = {
        "pois": [
            # 合格充电站（3个）
            {
                "poi_id": "ch_001",
                "name": "国网快充站-建国门",
                "category": "charging",
                "lat": 39.9200,
                "lon": 116.4100,
                "address": "东城区建国门外大街1号",
                "charge_rate_kw": 120,
                "hourly_rate": 0
            },
            {
                "poi_id": "ch_002",
                "name": "星星充电站-崇文门",
                "category": "charging",
                "lat": 39.8800,
                "lon": 116.3800,
                "address": "东城区崇文门内大街15号",
                "charge_rate_kw": 60,
                "hourly_rate": 0
            },
            {
                "poi_id": "ch_003",
                "name": "特斯拉超充-三里屯",
                "category": "charging",
                "lat": 39.9500,
                "lon": 116.4500,
                "address": "朝阳区三里屯路19号",
                "charge_rate_kw": 150,
                "hourly_rate": 0
            },
            # 不合格充电站：功率不足
            {
                "poi_id": "ch_004",
                "name": "慢充站-东单",
                "category": "charging",
                "lat": 39.9000,
                "lon": 116.4000,
                "address": "东城区东单北大街3号",
                "charge_rate_kw": 58,
                "hourly_rate": 5
            },
            # 不合格充电站：距离超出50km（约83km）
            {
                "poi_id": "ch_005",
                "name": "高速快充-张家口",
                "category": "charging",
                "lat": 40.5000,
                "lon": 117.0000,
                "address": "张家口市桥东区",
                "charge_rate_kw": 250,
                "hourly_rate": 0
            },
            # 干扰：其他类别（rest_area）
            {
                "poi_id": "rest_001",
                "name": "京藏高速服务区",
                "category": "rest_area",
                "lat": 39.9300,
                "lon": 116.3800,
                "address": "京藏高速48km处",
                "hourly_rate": 0
            },
            # 干扰：其他类别（food）
            {
                "poi_id": "food_001",
                "name": "全聚德烤鸭店",
                "category": "food",
                "lat": 39.9150,
                "lon": 116.4150,
                "address": "东城区前门大街32号",
                "hourly_rate": 0
            },
            # 干扰：其他类别（parking）
            {
                "poi_id": "park_001",
                "name": "王府井地下停车场",
                "category": "parking",
                "lat": 39.9080,
                "lon": 116.4080,
                "address": "东城区王府井大街",
                "hourly_rate": 10
            }
        ]
    }
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
