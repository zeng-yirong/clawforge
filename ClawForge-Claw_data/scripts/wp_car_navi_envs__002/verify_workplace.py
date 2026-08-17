import sys
import os
import json

EXPECTED_POI_ID = "poi-charge-suburb-02"

def verify(workspace):
    results = {
        "total_score": 0,
        "details": []
    }

    # 1) 检查ops/trip_plan.json是否存在
    plan_path = os.path.join(workspace, "ops", "trip_plan.json")
    if not os.path.isfile(plan_path):
        results["details"].append({
            "item": "文件ops/trip_plan.json存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        results["total_score"] = 0
        return results
    else:
        results["details"].append({
            "item": "文件ops/trip_plan.json存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已创建"
        })

    # 2) 解析JSON合法性
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        results["details"].append({
            "item": "JSON格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析"
        })
    except json.JSONDecodeError as e:
        results["details"].append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {e}"
        })
        results["total_score"] = sum(d["score"] for d in results["details"])
        return results

    # 3) 必须包含poi_id字段且为字符串
    if not isinstance(data, dict):
        results["details"].append({
            "item": "结果为字典类型",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望字典，实际类型 {type(data).__name__}"
        })
    else:
        poi_id = data.get("poi_id")
        if not isinstance(poi_id, str):
            results["details"].append({
                "item": "poi_id字段为字符串",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"poi_id不存在或不是字符串: {poi_id}"
            })
        else:
            results["details"].append({
                "item": "poi_id字段为字符串",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"poi_id = {poi_id}"
            })

    # 4) 关键值：poi_id必须等于预期ID
    if data.get("poi_id") == EXPECTED_POI_ID:
        results["details"].append({
            "item": "poi_id正确匹配预期快充站",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": f"正确ID: {EXPECTED_POI_ID}"
        })
    else:
        results["details"].append({
            "item": "poi_id正确匹配预期快充站",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": f"期望 {EXPECTED_POI_ID}，实际 {data.get('poi_id')}"
        })

    # 5) 禁止多余字段（仅允许poi_id）
    allowed_keys = {"poi_id"}
    extra = set(data.keys()) - allowed_keys
    if extra:
        results["details"].append({
            "item": "无多余字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"多余字段: {extra}"
        })
    else:
        results["details"].append({
            "item": "无多余字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "仅包含poi_id"
        })

    results["total_score"] = sum(d["score"] for d in results["details"])
    return results

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_data = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)
    print(json.dumps(score_data, ensure_ascii=False, indent=2))
