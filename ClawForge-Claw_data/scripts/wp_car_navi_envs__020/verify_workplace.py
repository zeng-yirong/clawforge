import json
import os
import sys

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 route/waypoints.json 是否存在 (15分)
    waypoints_path = os.path.join(workspace, "route", "waypoints.json")
    if os.path.isfile(waypoints_path):
        details.append({
            "item": "waypoints.json exists",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "文件 route/waypoints.json 存在"
        })
        total_score += 15
    else:
        details.append({
            "item": "waypoints.json exists",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "文件 route/waypoints.json 不存在"
        })
        # 如果文件不存在，后续检查跳过，总分直接返回
        return {
            "total_score": total_score,
            "details": details
        }

    # 2. 检查JSON格式合法性 (10分)
    try:
        with open(waypoints_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({
                "item": "JSON is valid list",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "根节点是一个列表"
            })
            total_score += 10
        else:
            details.append({
                "item": "JSON is valid list",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"根节点不是列表，而是 {type(data).__name__}"
            })
            return {"total_score": total_score, "details": details}
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "JSON is valid list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {e}"
        })
        return {"total_score": total_score, "details": details}

    # 3. 检查列表长度是否为3 (20分)
    if len(data) == 3:
        details.append({
            "item": "list length is 3",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"途径点数量正确，共 {len(data)} 个"
        })
        total_score += 20
    else:
        details.append({
            "item": "list length is 3",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望3个途径点，实际 {len(data)} 个"
        })
        # 即使数量不对，继续检查其他项（但后续可能出错）

    # 4. 每个元素必须包含 poi_id 和 name 字段，且无其他额外字段 (15分)
    field_ok = True
    for i, wp in enumerate(data):
        if not isinstance(wp, dict):
            field_ok = False
            details.append({
                "item": f"第 {i+1} 个元素非字典",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"元素类型应为dict，实际 {type(wp).__name__}"
            })
            break
        if "poi_id" not in wp or "name" not in wp:
            field_ok = False
            details.append({
                "item": f"第 {i+1} 个元素缺少关键字段",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"应包含 poi_id 和 name，实际键为 {list(wp.keys())}"
            })
            break
        if set(wp.keys()) != {"poi_id", "name"}:
            field_ok = False
            details.append({
                "item": f"第 {i+1} 个元素有多余字段",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"仅允许 poi_id 和 name，发现额外键: {set(wp.keys()) - {'poi_id', 'name'}}"
            })
            break
    if field_ok:
        details.append({
            "item": "每个元素只有 poi_id 和 name",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "所有元素字段合规"
        })
        total_score += 15
    else:
        # 如果前面已经添加了失败项，这里不再重复添加
        if not any(d["item"].startswith("第") for d in details):
            details.append({
                "item": "每个元素只有 poi_id 和 name",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "字段检查失败"
            })

    # 5. 检查poi_id是否正确：期望顺序 CHG-001, FOO-001, CHG-002 (40分)
    expected_ids = ["CHG-001", "FOO-001", "CHG-002"]
    expected_names = ["超充站A", "麦当劳", "超充站B"]  # 仅用于提示
    id_correct = True
    for i, (wp, eid) in enumerate(zip(data, expected_ids)):
        if wp.get("poi_id") != eid:
            id_correct = False
            details.append({
                "item": f"第 {i+1} 个元素poi_id正确",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"期望 '{eid}'，实际 '{wp.get('poi_id', '')}'"
            })
            break
    if id_correct:
        details.append({
            "item": "所有poi_id与顺序正确",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": f"顺序: {expected_ids}"
        })
        total_score += 40

    # 汇总总分
    # 如果前面某些子项失败已经扣分，这里计算实际总分（但上面已经累加）
    # 确保不超过100
    total_score = min(total_score, 100)

    return {
        "total_score": total_score,
        "details": details
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 将结果写入 workplace_score.json
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Score: {result['total_score']}/100")
    for d in result["details"]:
        print(f"  {d['item']}: {d['score']}/{d['max_score']} - {'PASS' if d['passed'] else 'FAIL'} - {d['reason']}")

if __name__ == "__main__":
    main()
