import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)  # 切换到工作区根目录

    score_details = []
    total_score = 0

    # ---------- 1. 检查 ops 目录 ----------
    ops_exists = os.path.isdir("ops")
    score_details.append({
        "item": "ops 目录存在",
        "score": 10 if ops_exists else 0,
        "max_score": 10,
        "passed": ops_exists,
        "reason": "" if ops_exists else "未找到 ops/ 目录"
    })
    if not ops_exists:
        total_score = 0
        dump_score(score_details, total_score)
        return

    # ---------- 2. 检查 ops/overbudget.json 文件 ----------
    file_path = "ops/overbudget.json"
    file_exists = os.path.isfile(file_path)
    score_details.append({
        "item": "ops/overbudget.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "" if file_exists else f"未找到 {file_path}"
    })
    if not file_exists:
        total_score = sum(d["score"] for d in score_details)
        dump_score(score_details, total_score)
        return

    # ---------- 3. 读取并解析 JSON ----------
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        total_score = sum(d["score"] for d in score_details)
        dump_score(score_details, total_score)
        return

    score_details.append({
        "item": "JSON 格式合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": ""
    })

    # ---------- 4. 检查是否为数组 ----------
    is_list = isinstance(data, list)
    score_details.append({
        "item": "内容为数组",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "" if is_list else "顶层结构不是数组"
    })
    if not is_list:
        total_score = sum(d["score"] for d in score_details)
        dump_score(score_details, total_score)
        return

    # ---------- 5. 读取初始文件，计算预期答案 ----------
    try:
        with open("data/travel_policy_senior.json", "r", encoding="utf-8") as f:
            policy = json.load(f)
        with open("consumption/records.json", "r", encoding="utf-8") as f:
            all_records = json.load(f)
    except Exception as e:
        score_details.append({
            "item": "读取初始文件",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"无法读取 policy 或 records 文件: {e}"
        })
        total_score = sum(d["score"] for d in score_details)
        dump_score(score_details, total_score)
        return

    duration = 3
    target_trip = "trip-2025-001"

    # 筛选目标差旅记录
    my_records = [r for r in all_records if r.get("trip_id") == target_trip]

    # 计算每条记录的预算和超支
    expected_list = []
    for r in my_records:
        cat = r["category"]
        pol = policy.get(cat)
        if pol is None:
            continue  # 忽略未在政策中的类别（本例中没有）
        if cat == "accommodation":
            budget = pol["nightly_budget"] * r.get("nights", 1)
        else:
            budget = pol["daily_budget"] * duration
        amount = r["amount"]
        overspend = round(amount - budget, 2)
        if overspend > 0:
            expected_list.append({
                "record_id": r["record_id"],
                "category": cat,
                "amount": amount,
                "budget": budget,
                "overspend": overspend
            })

    # 排序：先 overspend 降序，再 amount 降序，最后 record_id 升序
    expected_list.sort(key=lambda x: (-x["overspend"], -x["amount"], x["record_id"]))

    # ---------- 6. 比较数组长度 ----------
    len_ok = len(data) == len(expected_list)
    score_details.append({
        "item": "超支记录数量正确",
        "score": 10 if len_ok else 0,
        "max_score": 10,
        "passed": len_ok,
        "reason": f"期望 {len(expected_list)} 条，实际 {len(data)} 条" if not len_ok else ""
    })

    if not len_ok:
        total_score = sum(d["score"] for d in score_details)
        dump_score(score_details, total_score)
        return

    # ---------- 7. 检查每个元素结构 ----------
    fields_required = {"record_id", "category", "amount", "budget", "overspend"}
    all_fields_ok = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            all_fields_ok = False
            break
        if not fields_required.issubset(item.keys()):
            all_fields_ok = False
            break
    score_details.append({
        "item": "每个元素包含必要字段",
        "score": 10 if all_fields_ok else 0,
        "max_score": 10,
        "passed": all_fields_ok,
        "reason": "" if all_fields_ok else "缺少必要字段"
    })
    if not all_fields_ok:
        total_score = sum(d["score"] for d in score_details)
        dump_score(score_details, total_score)
        return

    # ---------- 8. 逐条验证数值和排序 ----------
    exact_match = True
    for i, (exp, act) in enumerate(zip(expected_list, data)):
        for key in fields_required:
            if math.isclose(exp[key], act[key], rel_tol=1e-9) if isinstance(exp[key], float) else exp[key] == act[key]:
                continue
            else:
                exact_match = False
                break
        if not exact_match:
            break

    score_details.append({
        "item": "数值准确（字段值、超支计算）",
        "score": 20 if exact_match else 0,
        "max_score": 20,
        "passed": exact_match,
        "reason": "" if exact_match else "存在数值不匹配"
    })

    # ---------- 9. 检查排序 ----------
    sort_ok = True
    if exact_match:
        # 排序已通过预期列表保证了，但可额外检查是否按 overspend 降序
        for i in range(len(data)-1):
            if data[i]["overspend"] < data[i+1]["overspend"]:
                sort_ok = False
                break
            if data[i]["overspend"] == data[i+1]["overspend"] and data[i]["amount"] < data[i+1]["amount"]:
                sort_ok = False
                break
    score_details.append({
        "item": "排序正确（超支降序→金额降序）",
        "score": 10 if sort_ok else 0,
        "max_score": 10,
        "passed": sort_ok,
        "reason": "" if sort_ok else "排序不符合要求"
    })

    # ---------- 10. 检查是否包含无关记录 ----------
    # 通过数量比对已隐含，但额外确认没有多余记录
    no_extra = True
    for item in data:
        if item["record_id"] not in [e["record_id"] for e in expected_list]:
            no_extra = False
            break
    score_details.append({
        "item": "未包含无关差旅记录",
        "score": 10 if no_extra else 0,
        "max_score": 10,
        "passed": no_extra,
        "reason": "" if no_extra else "发现了不属于目标差旅的记录"
    })

    # ---------- 汇总 ----------
    total_score = sum(d["score"] for d in score_details)
    dump_score(score_details, total_score)

def dump_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
