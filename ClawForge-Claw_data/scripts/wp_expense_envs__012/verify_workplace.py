"""
verify_workplace.py — 验证 agent 生成的超支分析报告
检查项：
1. 目录结构 (report/ 存在)
2. 文件存在且为合法 JSON
3. 包含所有期望字段 (overspend_items, total_overspend)
4. 超支类别及金额精确匹配预期
5. 无多余或缺失类别
6. 总计金额正确
"""
import sys
import json
import os

def verify(workspace: str):
    errors = []
    details = []
    total_score = 0

    # ========== 检查目录 ==========
    report_dir = os.path.join(workspace, "report")
    dir_ok = os.path.isdir(report_dir)
    details.append({
        "item": "报告目录 report/ 存在",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "目录存在" if dir_ok else "缺少 report/ 目录"
    })
    if not dir_ok:
        total_score = sum(d["score"] for d in details)
        _write_score(workspace, total_score, details)
        return

    # ========== 文件存在且合法 JSON ==========
    report_path = os.path.join(report_dir, "overspend.json")
    file_exists = os.path.isfile(report_path)
    details.append({
        "item": "报告文件 report/overspend.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "缺少文件"
    })
    if not file_exists:
        total_score = sum(d["score"] for d in details)
        _write_score(workspace, total_score, details)
        return

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        json_ok = True
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        json_ok = False
        errors.append(str(e))

    details.append({
        "item": "报告文件为合法 JSON",
        "score": 10 if json_ok else 0,
        "max_score": 10,
        "passed": json_ok,
        "reason": "合法 JSON" if json_ok else f"JSON 解析失败: {errors[-1] if errors else '未知错误'}"
    })
    if not json_ok:
        total_score = sum(d["score"] for d in details)
        _write_score(workspace, total_score, details)
        return

    # ========== 字段完整性 ==========
    required_fields = ["overspend_items", "total_overspend"]
    missing_fields = [f for f in required_fields if f not in data]
    fields_ok = len(missing_fields) == 0
    details.append({
        "item": "JSON 包含必需字段 (overspend_items, total_overspend)",
        "score": 20 if fields_ok else 0,
        "max_score": 20,
        "passed": fields_ok,
        "reason": "字段完整" if fields_ok else f"缺少字段: {missing_fields}"
    })
    if not fields_ok:
        total_score = sum(d["score"] for d in details)
        _write_score(workspace, total_score, details)
        return

    # ========== 超支条目验证 ==========
    # 预期超支：
    # accommodation: 预算 600*2=1200, 实际 1300 -> 超 100
    # food: 预算 250*2=500, 实际 420+200=620 (注意干扰日期18日的不计入预算周期) -> 超 120
    # taxi: 预算 100*2=200, 实际 120 -> 超 -? 实际120，未超？等等：第一天120，第二天0，共120，预算200，未超！但第一天120 > 100日限额，所以按每日限额看：第一天超20，第二天0，总超20。我们按累计预算 vs 累计实际？最好按每日预算累计？政策描述日限额，但出差2天，应该按总预算？题目说“按小李的级别（senior），这次北京出差（2天）里，哪些费用类别超了预算”，通常理解是总预算（日限额*天数）。所以住宿总预算1200，实际1300，超100；餐饮总预算500，实际620（不含第三天干扰），超120；出租车总预算200，实际120，未超；机票总预算2000，实际1950，未超；地铁总预算80，实际25，未超。
    # 注意餐饮：第三天180元是干扰，不应计入。因此超支类别：accommodation (100), food (120)
    expected_overspend = {
        "accommodation": 100.0,
        "food": 120.0
    }
    expected_total = 220.0

    overspend_items = data.get("overspend_items", {})
    # 检查类别数
    actual_categories = set(overspend_items.keys())
    expected_categories = set(expected_overspend.keys())
    cat_match = actual_categories == expected_categories
    # 检查每个金额
    amount_errors = []
    for cat, expected_amt in expected_overspend.items():
        actual_amt = overspend_items.get(cat)
        if actual_amt is None:
            amount_errors.append(f"缺少类别 {cat}")
        elif abs(actual_amt - expected_amt) > 0.001:
            amount_errors.append(f"{cat} 金额期望 {expected_amt}，实际 {actual_amt}")
    # 检查多余类别
    extra_cats = actual_categories - expected_categories
    if extra_cats:
        amount_errors.append(f"多余类别: {extra_cats}")

    items_ok = len(amount_errors) == 0 and cat_match
    details.append({
        "item": "超支条目类别与金额正确",
        "score": 30 if items_ok else 0,
        "max_score": 30,
        "passed": items_ok,
        "reason": "正确" if items_ok else f"错误: {'; '.join(amount_errors)}"
    })

    # ========== 总计金额验证 ==========
    total_in_report = data.get("total_overspend")
    total_ok = total_in_report is not None and abs(total_in_report - expected_total) < 0.001
    details.append({
        "item": "总计超支金额正确 (期望 220.0)",
        "score": 20 if total_ok else 0,
        "max_score": 20,
        "passed": total_ok,
        "reason": "正确" if total_ok else f"期望 {expected_total}，实际 {total_in_report}"
    })

    # 计算总分
    total_score = sum(d["score"] for d in details)
    _write_score(workspace, total_score, details)


def _write_score(workspace, total_score, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
    print(f"评分完成: {total_score}/100")


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
