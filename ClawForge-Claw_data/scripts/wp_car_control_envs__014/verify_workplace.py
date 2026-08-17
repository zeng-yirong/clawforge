import sys, json, os, pathlib

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    w = pathlib.Path(workspace)
    details = []
    total = 0

    # 1. 检查 ops 目录是否存在
    ops_dir = w / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops目录存在", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        total += 5
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops目录不存在"})

    # 2. 检查 abnormal_presets.json 文件存在
    target = ops_dir / "abnormal_presets.json"
    if target.is_file():
        details.append({"item": "目标文件存在", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        total += 5
    else:
        details.append({"item": "目标文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops/abnormal_presets.json 未找到"})
        # 后续检查无法进行，提前输出
        _write_score(total, details)
        return

    # 3. 检查 JSON 合法性
    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        _write_score(total, details)
        return

    # 4. 检查是否包含预期的字段结构（必须是一个对象，包含 abnormal_presets 数组）
    if not isinstance(data, dict) or "abnormal_presets" not in data:
        details.append({"item": "字段结构正确", "score": 0, "max_score": 10, "passed": False,
                        "reason": "期望 JSON 对象包含字段 'abnormal_presets'"})
        _write_score(total, details)
        return
    arr = data["abnormal_presets"]
    if not isinstance(arr, list):
        details.append({"item": "字段结构正确", "score": 0, "max_score": 10, "passed": False,
                        "reason": "'abnormal_presets' 的值应为数组"})
        _write_score(total, details)
        return
    details.append({"item": "字段结构正确", "score": 10, "max_score": 10, "passed": True, "reason": ""})
    total += 10

    # 5. 检查数组元素是否都是预设ID（字符串），并验证内容
    expected_ids = {"p5", "p6"}
    actual_ids = set()
    for item in arr:
        if isinstance(item, str):
            actual_ids.add(item)
        else:
            details.append({"item": "预设ID为字符串", "score": 0, "max_score": 5, "passed": False,
                            "reason": f"数组元素 {item} 不是字符串"})
            total += 0  # 不额外扣分，但下面会处理
            break

    # 缺失检查
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids
    # 防止意外多扣分：先计算基础分
    # 完全正确得分30
    if missing == set() and extra == set():
        details.append({"item": "预设ID内容正确", "score": 30, "max_score": 30, "passed": True, "reason": "包含 p5, p6 且无多余"})
        total += 30
    else:
        score = 0
        reason_parts = []
        if missing:
            score += 0
            reason_parts.append(f"缺失: {', '.join(sorted(missing))}")
        if extra:
            score += 0
            reason_parts.append(f"多余: {', '.join(sorted(extra))}")
        # 部分正确给予一些分数：每正确一个预设ID给10分，最多20，再减去每多一个ID扣5分（但最低0）
        base = 0
        for eid in expected_ids:
            if eid in actual_ids:
                base += 10
        base = min(base, 20)
        penalty = len(extra) * 5
        final = max(0, base - penalty)
        details.append({"item": "预设ID内容正确", "score": final, "max_score": 30, "passed": False,
                        "reason": "; ".join(reason_parts) if reason_parts else "部分错误"})
        total += final

    # 6. 额外检查：判断是否引用了备份中的预设（b1），如果出现则扣5分
    if "b1" in actual_ids:
        details.append({"item": "未引入备份数据", "score": 0, "max_score": 5, "passed": False, "reason": "包含了备份中的预设 b1"})
    else:
        details.append({"item": "未引入备份数据", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        total += 5

    # 7. 加分项：输出数组长度恰好为2（防止重复或多余）
    if len(arr) == 2 and missing == set() and extra == set():
        details.append({"item": "数组长度正确", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        total += 5
    else:
        details.append({"item": "数组长度正确", "score": 0, "max_score": 5, "passed": False, "reason": f"实际长度 {len(arr)}"})

    _write_score(total, details)

def _write_score(total, details):
    # 确保总分为0-100整数
    total = max(0, min(100, total))
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    verify()
