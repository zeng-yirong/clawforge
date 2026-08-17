import os
import json
import sys
from pathlib import Path

def verify(workspace: str):
    details = []
    total_max = 100
    score = 0

    # 1. 检查 ops/valid_waypoints.json 是否存在 (10分)
    file_path = Path(workspace) / "ops" / "valid_waypoints.json"
    if file_path.exists():
        details.append({
            "item": "检查文件 ops/valid_waypoints.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        score += 10
    else:
        details.append({
            "item": "检查文件 ops/valid_waypoints.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"文件不存在: {file_path}"
        })
        # 如果文件不存在，直接跳过后续检查
        total = sum(d["max_score"] for d in details)
        # 补全剩余项为0分并返回
        remaining = [
            ("合法 JSON 格式", 10),
            ("正确过滤无效 POI（长度应为4）", 20),
            ("顺序正确（poi_001, poi_002, poi_004, poi_007）", 20),
            ("仅包含有效 POI（无冗余元素）", 20),
            ("目录结构合规（仅需 ops 目录）", 10),
            ("无额外多余影响评分的文件？", 10)
        ]
        for item_name, max_s in remaining:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "前置文件缺失，无法检查"
            })
        total_score = 10  # 只有存在分
        out = {"total_score": total_score, "details": details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(out, f, indent=2)
        return

    # 2. 检查 JSON 合法性 (10分)
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "合法 JSON 格式",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON 解析成功"
        })
        score += 10
    except Exception as e:
        details.append({
            "item": "合法 JSON 格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        # 同样提前结束
        for item_name, max_s in [
            ("正确过滤无效 POI（长度应为4）", 20),
            ("顺序正确（poi_001, poi_002, poi_004, poi_007）", 20),
            ("仅包含有效 POI（无冗余元素）", 20),
            ("目录结构合规", 10),
            ("无多余文件干扰", 10)
        ]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "JSON 解析失败，无法继续"
            })
        total_score = score
        out = {"total_score": total_score, "details": details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(out, f, indent=2)
        return

    # 3. 检查 data 结构：期望是列表（每个元素为 poi_id 字符串）
    if isinstance(data, list):
        # 接受列表
        waypoints = data
    elif isinstance(data, dict) and "waypoints" in data:
        waypoints = data["waypoints"]
    elif isinstance(data, dict) and "valid_waypoints" in data:
        waypoints = data["valid_waypoints"]
    else:
        waypoints = None
        details.append({
            "item": "数据结构",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "期望 JSON 为包含 poi_id 的列表，或包含 waypoints/valid_waypoints 键的对象，但实际结构无法识别"
        })
        # 后续跳过
        # ... 简化处理：给0分然后结束
        for item_name, max_s in [
            ("正确过滤无效 POI（长度应为4）", 20),
            ("顺序正确", 20),
            ("仅含有效 POI", 20),
            ("目录结构", 10),
            ("无多余文件", 10)
        ]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "数据结构不符合预期"
            })
        total_score = score
        out = {"total_score": total_score, "details": details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(out, f, indent=2)
        return

    # 4. 检查长度必须为4 (20分)
    expected_ids = ["poi_001", "poi_002", "poi_004", "poi_007"]
    if len(waypoints) == 4:
        details.append({
            "item": "正确过滤无效 POI（长度应为4）",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"结果长度恰为4"
        })
        score += 20
    else:
        details.append({
            "item": "正确过滤无效 POI（长度应为4）",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望4个途经点，实际得到 {len(waypoints)} 个"
        })

    # 5. 检查顺序 (20分)
    # 提取 poi_id 列表（如果元素是字符串则直接用，如果是字典则取 poi_id 键）
    extracted_ids = []
    for item in waypoints:
        if isinstance(item, str):
            extracted_ids.append(item)
        elif isinstance(item, dict) and "poi_id" in item:
            extracted_ids.append(item["poi_id"])
        else:
            # 无法识别，直接失败
            pass

    if extracted_ids == expected_ids:
        details.append({
            "item": "顺序正确（poi_001, poi_002, poi_004, poi_007）",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "顺序完全匹配"
        })
        score += 20
    else:
        details.append({
            "item": "顺序正确（poi_001, poi_002, poi_004, poi_007）",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望顺序 {expected_ids}，实际得到 {extracted_ids}"
        })

    # 6. 检查是否包含所有有效POI且无额外 (20分)
    if set(extracted_ids) == set(expected_ids):
        details.append({
            "item": "仅包含有效 POI（无冗余元素）",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "集合完全一致，无多余或缺失"
        })
        score += 20
    else:
        details.append({
            "item": "仅包含有效 POI（无冗余元素）",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"有效ID集合不匹配，期望 {set(expected_ids)}，得到 {set(extracted_ids)}"
        })

    # 7. 目录结构合规检查 (10分)
    # 只需存在 ops/ 目录且不强制其他目录，但检查 ops/valid_waypoints.json 已通过
    ops_dir = Path(workspace) / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "目录结构合规（ops 目录存在）",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops 目录存在"
        })
        score += 10
    else:
        details.append({
            "item": "目录结构合规（ops 目录存在）",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops 目录不存在"
        })

    # 8. 额外奖励：检查是否严格按字符串列表输出（非强制，但作为额外检查，不影响总分？这里作为可选项，但我们分配10分给"无多余文件"实际上已包含在之前？）
    # 我决定分配10分给“无多余影响评分的文件”，但我们不强制agent只创建这一个文件，所以不扣分。因此将最后10分作为“格式干净”即结果无多余字段/对象
    # 我们可以检查结果中是否有意料之外的字段（假如是列表形式则干净，如果是字典且只有waypoints则干净）
    clean = False
    if isinstance(data, list):
        clean = True
    elif isinstance(data, dict):
        # 允许只有 waypoints 或 valid_waypoints 键，且没有其他无关键
        keys = set(data.keys())
        allowed_keys = {"waypoints", "valid_waypoints"}
        if keys.issubset(allowed_keys) and len(keys) <= 1:
            clean = True
    if clean:
        details.append({
            "item": "结果格式干净（无多余包装键）",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "结构简洁，无多余字段"
        })
        score += 10
    else:
        details.append({
            "item": "结果格式干净（无多余包装键）",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"结果包含额外键或结构复杂: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}"
        })

    # 汇总
    total_score = score
    out = {"total_score": total_score, "details": details}
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
