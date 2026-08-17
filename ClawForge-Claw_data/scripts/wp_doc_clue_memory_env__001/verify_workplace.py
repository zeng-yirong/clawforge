import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def check_file_exists(path):
    return os.path.isfile(os.path.join(workspace, path))

def load_json(path):
    with open(os.path.join(workspace, path), "r") as f:
        return json.load(f)

def verify():
    score = 0
    details = []

    # 1. 检查目录结构 (10分)
    required_dirs = ["data", "data/reports", "data/presentations", "data/media_samples", "ops"]
    dirs_ok = all(check_file_exists(d+"/.") or os.path.isdir(os.path.join(workspace, d)) for d in required_dirs)
    if dirs_ok:
        score += 10
        details.append({"item": "目录结构", "score": 10, "max_score": 10, "passed": True, "reason": "所有必需目录存在"})
    else:
        details.append({"item": "目录结构", "score": 0, "max_score": 10, "passed": False, "reason": "缺失部分必需目录"})

    # 2. 检查 ops/clue_list.json 是否存在 (10分)
    clue_path = "ops/clue_list.json"
    if check_file_exists(clue_path):
        score += 10
        details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": f"{clue_path} 已生成"})
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"{clue_path} 未找到"})
        # 如果文件不存在，后续无法验证，直接返回
        return {"total_score": score, "details": details}

    # 3. 解析JSON合法性 (10分)
    try:
        clues = load_json(clue_path)
        if not isinstance(clues, list):
            raise ValueError("必须是JSON数组")
        score += 10
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "正确解析为数组"})
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        # 无法继续
        return {"total_score": score, "details": details}

    # 4. 检查每条记录结构 (每个对象必须有 id, clue_bullets) (15分)
    struct_ok = True
    for idx, item in enumerate(clues):
        if not isinstance(item, dict) or "id" not in item or "clue_bullets" not in item:
            struct_ok = False
            break
        if not isinstance(item["clue_bullets"], list):
            struct_ok = False
            break
    if struct_ok:
        score += 15
        details.append({"item": "记录字段结构", "score": 15, "max_score": 15, "passed": True, "reason": "每条记录含id和clue_bullets列表"})
    else:
        details.append({"item": "记录字段结构", "score": 0, "max_score": 15, "passed": False, "reason": "存在字段缺失或类型错误"})

    # 5. 检查匹配结果数量和ID正确性 (30分)
    # 预期哪些文档匹配 "HelioSync Edge Inference Fabric"
    expected_entries = [
        {"id": "RPT-2026-0421", "tags": ["edge inference", "industrial", "HelioSync"]},
        {"id": "RPT-2026-0418", "tags": ["logistics", "automation", "computer vision"]},
        {"id": "PRES-2026-0312", "tags": ["case study", "edge deployment", "HelioSync"]},
        {"id": "MED-2026-0503", "tags": ["interview", "HelioSync", "edge AI"]},
        {"id": "MED-2026-0428", "tags": ["whitepaper", "edge fabric", "inference"]}
    ]
    expected_ids = {e["id"] for e in expected_entries}
    actual_ids = {item["id"] for item in clues}

    if actual_ids == expected_ids:
        score += 15
        details.append({"item": "匹配ID集合", "score": 15, "max_score": 15, "passed": True, "reason": "ID集合完全正确"})
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason = ""
        if missing:
            reason += f"缺失ID: {missing}. "
        if extra:
            reason += f"多余ID: {extra}. "
        details.append({"item": "匹配ID集合", "score": 0, "max_score": 15, "passed": False, "reason": reason})

    # 6. 检查 clue_bullets 是否与对应文档的 tags 一致 (20分)
    # 构建一个映射 id -> 预期tags (上面已定义)
    id_to_tags = {e["id"]: e["tags"] for e in expected_entries}
    tags_ok = True
    for item in clues:
        eid = item["id"]
        if eid in id_to_tags:
            if sorted(item["clue_bullets"]) != sorted(id_to_tags[eid]):
                tags_ok = False
                break
        else:
            tags_ok = False  # 多余的ID
    if tags_ok and len(clues) == len(expected_entries):
        score += 20
        details.append({"item": "clue_bullets 与 tags 一致", "score": 20, "max_score": 20, "passed": True, "reason": "每条记录的clue_bullets与原始tags完全匹配"})
    else:
        details.append({"item": "clue_bullets 与 tags 一致", "score": 0, "max_score": 20, "passed": False, "reason": "存在不匹配或数量不对"})

    # 7. 检查是否包含多余字段 (如额外键) (5分)
    extra_keys_ok = True
    for item in clues:
        allowed_keys = {"id", "clue_bullets"}
        if set(item.keys()) != allowed_keys:
            extra_keys_ok = False
            break
    if extra_keys_ok:
        score += 5
        details.append({"item": "无多余字段", "score": 5, "max_score": 5, "passed": True, "reason": "每条记录只有id和clue_bullets"})
    else:
        details.append({"item": "无多余字段", "score": 0, "max_score": 5, "passed": False, "reason": "存在额外字段"})

    # 总分
    total = min(score, 100)
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    result = verify()
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
