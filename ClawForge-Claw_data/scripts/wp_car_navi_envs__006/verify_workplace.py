import os
import sys
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    result = {
        "total_score": 0,
        "details": []
    }
    
    # ---------- 1. 检查 output 文件存在 ----------
    plan_path = os.path.join(workspace, "plan", "trip_plan.json")
    if not os.path.isfile(plan_path):
        result["details"].append({
            "item": "output文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "plan/trip_plan.json 不存在"
        })
        result["total_score"] = 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return
    
    result["details"].append({
        "item": "output文件存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "plan/trip_plan.json 存在"
    })
    
    # ---------- 2. 解析 JSON 并验证是数组 ----------
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            trip_plan = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        result["details"].append({
            "item": "JSON格式合法且为数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {e}"
        })
        result["total_score"] = 10  # 仅文件存在分
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return
    
    if not isinstance(trip_plan, list):
        result["details"].append({
            "item": "JSON格式合法且为数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "trip_plan 不是数组"
        })
        result["total_score"] = 10
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return
    
    result["details"].append({
        "item": "JSON格式合法且为数组",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "合法JSON数组"
    })
    
    # ---------- 3. 数组长度 ----------
    expected_length = 4  # 2个充电站 + 2个餐厅
    actual_length = len(trip_plan)
    if actual_length == expected_length:
        result["details"].append({
            "item": "数组长度正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"长度 = {actual_length}"
        })
    else:
        result["details"].append({
            "item": "数组长度正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 {expected_length}，实际 {actual_length}"
        })
    
    # ---------- 4. 每个元素包含必要字段 ----------
    required_fields = {"poi_id", "name", "category", "lat", "lon", "address"}
    all_fields_ok = True
    for i, entry in enumerate(trip_plan):
        if not isinstance(entry, dict):
            all_fields_ok = False
            break
        if not required_fields.issubset(entry.keys()):
            all_fields_ok = False
            break
    
    if all_fields_ok:
        result["details"].append({
            "item": "每个元素包含必要字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有元素包含 poi_id, name, category, lat, lon, address"
        })
    else:
        result["details"].append({
            "item": "每个元素包含必要字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "某些元素缺失必要字段或类型错误"
        })
    
    # ---------- 5. 内容正确性：筛选逻辑 ----------
    # 从原始数据计算期望列表
    expected_poi_ids = set()
    # 读取最新地图，找到郊区扩展区域
    maps_path = os.path.join(workspace, "data", "offline_maps.json")
    if not os.path.isfile(maps_path):
        result["details"].append({
            "item": "内容正确性（筛选）",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "data/offline_maps.json 无法读取，无法验证"
        })
        # 继续执行但总分受影响
    else:
        with open(maps_path, "r", encoding="utf-8") as f:
            maps_data = json.load(f)
        suburb_region_id = None
        for reg in maps_data.get("regions", []):
            if reg.get("name") == "郊区扩展区域" and reg.get("map_version") == "2024.06.01":
                suburb_region_id = reg["region_id"]
                break
        if suburb_region_id is None:
            result["details"].append({
                "item": "内容正确性（筛选）",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "未找到郊区扩展区域(版本2024.06.01)的region_id"
            })
        else:
            # 读取POI数据
            pois_path = os.path.join(workspace, "data", "pois.json")
            if not os.path.isfile(pois_path):
                result["details"].append({
                    "item": "内容正确性（筛选）",
                    "score": 0,
                    "max_score": 30,
                    "passed": False,
                    "reason": "data/pois.json 无法读取"
                })
            else:
                with open(pois_path, "r", encoding="utf-8") as f:
                    pois_data = json.load(f)
                expected_list = []
                seen_ids = set()
                for poi in pois_data.get("pois", []):
                    # 过滤重复poi_id (取第一次出现)
                    pid = poi.get("poi_id")
                    if pid in seen_ids:
                        continue
                    seen_ids.add(pid)
                    # 检查region_id
                    if poi.get("region_id") != suburb_region_id:
                        continue
                    cat = poi.get("category")
                    if cat == "charging":
                        # 需要 charge_rate_kw >= 50
                        cr = poi.get("charge_rate_kw")
                        if cr is None or cr < 50:
                            continue
                    elif cat == "food":
                        pass  # 所有餐厅都接受
                    else:
                        continue
                    expected_list.append(poi)
                # 按lon降序
                expected_list.sort(key=lambda x: x["lon"], reverse=True)
                expected_ids = [p["poi_id"] for p in expected_list]
                actual_ids = [e.get("poi_id","") for e in trip_plan]
                
                if expected_ids == actual_ids:
                    result["details"].append({
                        "item": "内容正确性（筛选与排序）",
                        "score": 30,
                        "max_score": 30,
                        "passed": True,
                        "reason": f"POI ID 序列完全匹配期望: {expected_ids}"
                    })
                else:
                    result["details"].append({
                        "item": "内容正确性（筛选与排序）",
                        "score": 0,
                        "max_score": 30,
                        "passed": False,
                        "reason": f"期望ID顺序 {expected_ids}，实际 {actual_ids}"
                    })
    
    # ---------- 6. 排序正确性（经度降序） ----------
    lon_vals = [e.get("lon") for e in trip_plan if isinstance(e, dict)]
    if len(lon_vals) > 1 and all(lon_vals[i] >= lon_vals[i+1] for i in range(len(lon_vals)-1)):
        result["details"].append({
            "item": "排序正确（经度降序）",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "经度非递增顺序"
        })
    else:
        result["details"].append({
            "item": "排序正确（经度降序）",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "经度未正确降序排列"
        })
    
    # 计算总分
    total = sum(d["score"] for d in result["details"])
    result["total_score"] = total
    
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
