"""
验证 Agent 生成的工作产物：ops/overbudget_items.json
要求：
- 文件存在且为合法 JSON
- 内容为列表，每个元素包含 category, actual, budget, over 四个字段
- 计算正确：只包含实际超支的类别（actual > budget），数值精确匹配预设
- 超支类别顺序按 category 字符串升序排列
"""
import sys, os, json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    # 定义预期结果（与 env_builder 中 Alice SH-2024-01 和标准政策一致）
    # 住宿：实际 500.0，预算 400.0，超支 100.0
    # 机票：实际 1200.0，预算 1000.0，超支 200.0
    # 其余类别均未超支（食品 250<300，出租车 50<100，地铁 无记录视为0<50，通讯0<80，杂费100<200 但 misc 不计入？注意 misc 有一笔100，预算200，未超支；夜班费？不涉及）
    expected = [
        {"category": "accommodation", "actual": 500.0, "budget": 400.0, "over": 100.0},
        {"category": "flight",      "actual": 1200.0, "budget": 1000.0, "over": 200.0}
    ]

    details = []

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops 目录不存在"})
        # 后续无法继续，提前结束
        write_score(details)
        return

    # 2. 检查 overbudget_items.json 文件存在 (10分)
    report_path = os.path.join(ops_dir, "overbudget_items.json")
    if os.path.isfile(report_path):
        details.append({"item": "overbudget_items.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    else:
        details.append({"item": "overbudget_items.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        write_score(details)
        return

    # 3. 解析 JSON (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        details.append({"item": "JSON 解析合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(details)
        return

    if not isinstance(data, list):
        details.append({"item": "JSON 类型为列表", "score": 0, "max_score": 10, "passed": False, "reason": "根元素不是列表"})
        write_score(details)
        return
    details.append({"item": "JSON 解析合法且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})

    # 4. 检查列表长度 (10分)
    if len(data) != len(expected):
        details.append({"item": "超支项数量正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {len(expected)} 项，实际 {len(data)} 项"})
        write_score(details)
        return
    details.append({"item": "超支项数量正确", "score": 10, "max_score": 10, "passed": True, "reason": "数量匹配"})

    # 5. 字段完整性 (10分)
    required_fields = {"category", "actual", "budget", "over"}
    all_fields_ok = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            all_fields_ok = False
            break
        if not required_fields.issubset(set(item.keys())):
            all_fields_ok = False
            break
        # 检查数值类型
        for key in ["actual","budget","over"]:
            if not isinstance(item.get(key), (int, float)):
                all_fields_ok = False
                break
    if all_fields_ok:
        details.append({"item": "字段完整性及类型", "score": 10, "max_score": 10, "passed": True, "reason": "每项均包含 category, actual, budget, over 且数值类型正确"})
    else:
        details.append({"item": "字段完整性及类型", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必要字段或数值类型错误"})
        write_score(details)
        return

    # 6. 排序检查（按 category 升序，预期已排序） (10分)
    sorted_data = sorted(data, key=lambda x: x.get("category", ""))
    if data == sorted_data:
        details.append({"item": "按 category 排序", "score": 10, "max_score": 10, "passed": True, "reason": "列表已按 category 升序排列"})
    else:
        details.append({"item": "按 category 排序", "score": 0, "max_score": 10, "passed": False, "reason": "列表未排序或排序错误"})
        # 后续检查仍可进行，但扣分

    # 7. 精确数值比对 (40分，每个超支项 20分)
    # 先将 expected 和 data 按 category 排序后一一比对
    expected_sorted = sorted(expected, key=lambda x: x["category"])
    data_sorted = sorted(data, key=lambda x: x.get("category", ""))
    score_per_item = 20  # 2项共40分
    for i, (exp, act) in enumerate(zip(expected_sorted, data_sorted)):
        passed = True
        reason_parts = []
        for key in ["category", "actual", "budget", "over"]:
            exp_val = exp[key]
            act_val = act.get(key)
            # 数值比较允许极小浮点误差
            if isinstance(exp_val, float):
                if abs(act_val - exp_val) > 0.01:
                    passed = False
                    reason_parts.append(f"{key} 期望 {exp_val} 实际 {act_val}")
            else:
                if act_val != exp_val:
                    passed = False
                    reason_parts.append(f"{key} 期望 {exp_val} 实际 {act_val}")
        if passed:
            details.append({"item": f"超支项 {exp['category']} 精确值", "score": score_per_item, "max_score": score_per_item, "passed": True, "reason": f"数值完全匹配 {exp}"})
        else:
            details.append({"item": f"超支项 {exp['category']} 精确值", "score": 0, "max_score": score_per_item, "passed": False, "reason": "；".join(reason_parts)})

    # 防漏：如果 data 包含预期之外的额外项，扣分（但前面数量已检查，这里不再重复）
    # 所有检查完毕，计算总分
    write_score(details)

def write_score(details):
    total = sum(d["score"] for d in details)
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"总分: {total}/100")
    sys.exit(0)

if __name__ == "__main__":
    main()
