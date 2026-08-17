import sys
import json
import math
import os
from pathlib import Path

# 哈弗辛距离（km）
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)

    details = []
    total_score = 0

    # ===================== 1. 检查输出目录存在 =====================
    ops_dir = ws / "ops"
    max_ops = 10
    if ops_dir.is_dir():
        details.append({"item": "ops目录存在", "score": max_ops, "max_score": max_ops, "passed": True, "reason": "ops目录已创建"})
        total_score += max_ops
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": max_ops, "passed": False, "reason": "ops目录不存在"})

    # ===================== 2. 检查输出文件存在且JSON合法 =====================
    result_file = ws / "ops" / "charge_waypoints.json"
    max_file = 10
    if not result_file.exists():
        details.append({"item": "输出文件存在且合法", "score": 0, "max_score": max_file, "passed": False, "reason": "ops/charge_waypoints.json 不存在"})
        # 无法继续
        write_score(details, total_score)
        return
    try:
        result = load_json(result_file)
        if not isinstance(result, list):
            raise ValueError("不是数组")
        if len(result) != 3:
            details.append({"item": "输出文件存在且合法", "score": 0, "max_score": max_file, "passed": False, "reason": f"预期数组长度3，实际{len(result)}"})
            write_score(details, total_score)
            return
        # 检查每个元素字段
        for i, item in enumerate(result):
            if not isinstance(item, dict):
                raise ValueError(f"第{i}个元素不是对象")
            for field in ['poi_id', 'name', 'distance_km']:
                if field not in item:
                    raise ValueError(f"第{i}个元素缺少{field}")
            if not isinstance(item['distance_km'], (int, float)):
                raise ValueError(f"第{i}个元素distance_km非数值")
        details.append({"item": "输出文件存在且合法", "score": max_file, "max_score": max_file, "passed": True, "reason": "文件存在，JSON合法，数组长度3，字段完整"})
        total_score += max_file
    except Exception as e:
        details.append({"item": "输出文件存在且合法", "score": 0, "max_score": max_file, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(details, total_score)
        return

    # ===================== 3. 构建期望答案 =====================
    try:
        # 读取最新区域数据
        regions_path = ws / "data" / "regions.json"
        if not regions_path.exists():
            details.append({"item": "期望答案构建", "score": 0, "max_score": 0, "passed": False, "reason": "data/regions.json 不存在，无法评测"})
            write_score(details, total_score)
            return
        regions_data = load_json(regions_path)
        regions = regions_data.get("regions", [])
        # 找“市中心区域”且版本最新（这里只有一个）
        target_region = None
        for r in regions:
            if r["name"] == "市中心区域":
                if target_region is None:
                    target_region = r
                else:
                    # 如果有多个，选版本大的
                    if r["map_version"] > target_region["map_version"]:
                        target_region = r
        if target_region is None:
            details.append({"item": "期望答案构建", "score": 0, "max_score": 0, "passed": False, "reason": "未找到市中心区域"})
            write_score(details, total_score)
            return

        center = target_region["center"]
        radius = target_region["radius_km"]

        # 读取POI数据
        pois_path = ws / "data" / "pois.json"
        if not pois_path.exists():
            details.append({"item": "期望答案构建", "score": 0, "max_score": 0, "passed": False, "reason": "data/pois.json 不存在"})
            write_score(details, total_score)
            return
        pois_data = load_json(pois_path)
        pois = pois_data.get("pois", [])

        # 筛选充电站且在区域内
        candidates = []
        for p in pois:
            if p.get("category") != "charging":
                continue
            lat, lon = p["lat"], p["lon"]
            dist = haversine(center["lat"], center["lon"], lat, lon)
            if dist <= radius:
                candidates.append((p, dist))

        if len(candidates) < 3:
            details.append({"item": "期望答案构建", "score": 0, "max_score": 0, "passed": False, "reason": f"区域内充电站不足3个 (实际{len(candidates)})"})
            write_score(details, total_score)
            return

        # 按距离排序取前3
        candidates.sort(key=lambda x: x[1])
        expected = [{"poi_id": c[0]["poi_id"], "name": c[0]["name"], "distance_km": round(c[1], 2)} for c in candidates[:3]]
    except Exception as e:
        details.append({"item": "期望答案构建", "score": 0, "max_score": 0, "passed": False, "reason": f"构建失败: {str(e)}"})
        write_score(details, total_score)
        return

    # ===================== 4. 比对结果（60分） =====================
    max_match = 60
    match_score = 0
    reason_parts = []
    # 先检查是否有不在期望中的POI（多选或错选）
    expected_ids = [e["poi_id"] for e in expected]
    result_ids = [r["poi_id"] for r in result]
    extra_ids = [rid for rid in result_ids if rid not in expected_ids]
    if extra_ids:
        reason_parts.append(f"包含不在期望中的POI: {extra_ids}")
    missing_ids = [eid for eid in expected_ids if eid not in result_ids]
    if missing_ids:
        reason_parts.append(f"缺少期望POI: {missing_ids}")

    # 逐项比对
    errors = []
    for i, (e, r) in enumerate(zip(expected, result)):
        poi_err = []
        if e["poi_id"] != r["poi_id"]:
            poi_err.append(f"第{i+1}个poi_id期望{e['poi_id']}得到{r['poi_id']}")
        if e["name"] != r["name"]:
            poi_err.append(f"第{i+1}个name期望{e['name']}得到{r['name']}")
        dist_diff = abs(e["distance_km"] - r["distance_km"])
        if dist_diff > 0.01:
            poi_err.append(f"第{i+1}个distance_km偏差{dist_diff:.4f}km (期望{e['distance_km']})")
        if poi_err:
            errors.extend(poi_err)

    if not errors and not extra_ids and not missing_ids:
        match_score = max_match
        reason_parts.append("所有POI完全正确")
    else:
        # 扣分：每个错误POI扣20分，最多扣完
        error_count = len(errors) + len(extra_ids) + len(missing_ids)
        match_score = max(0, max_match - error_count * 20)
        if match_score < 0:
            match_score = 0
        reason_parts.append(f"发现{error_count}处错误，得分{match_score}/{max_match}")

    details.append({
        "item": "结果比对",
        "score": match_score,
        "max_score": max_match,
        "passed": match_score == max_match,
        "reason": "; ".join(reason_parts)
    })
    total_score += match_score

    # ===================== 5. 写入评分 =====================
    write_score(details, total_score)

def write_score(details, total_score):
    # 确保details中每个item都有score, max_score, passed, reason
    # 如果有缺失，补0分
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
