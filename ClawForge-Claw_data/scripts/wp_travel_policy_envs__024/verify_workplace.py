import os
import sys
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []

    # 1. 检查 ops/recommendation.json 是否存在 (10分)
    rec_path = os.path.join(workspace, "ops", "recommendation.json")
    if os.path.isfile(rec_path):
        results.append({"item": "推荐文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/recommendation.json 已创建"})
    else:
        results.append({"item": "推荐文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/recommendation.json 不存在"})
        # 如果文件不存在，后续检查无法进行，直接输出
        write_score(results, workspace)
        return

    # 2. 检查文件是否为合法 JSON (10分)
    try:
        with open(rec_path, "r") as f:
            rec = json.load(f)
        results.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件可正常解析"})
    except Exception as e:
        results.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(results, workspace)
        return

    # 3. 检查必填字段 (20分)
    required_fields = ["platform_id", "flight_id", "price", "reason"]
    missing = [f for f in required_fields if f not in rec]
    if not missing:
        results.append({"item": "必填字段完整", "score": 20, "max_score": 20, "passed": True, "reason": "包含所有必需字段"})
    else:
        results.append({"item": "必填字段完整", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {missing}"})
        # 字段不全，无法进行后续数值比较，但可以继续检查已有字段
        # 但为了公平，只给部分分数，我们只在这个项目扣分，后面仍尝试推理

    # 4. 读取政策文件和平台数据，验证推荐是否正确 (60分)
    # 首先加载政策
    policy_path = os.path.join(workspace, "data", "policies", "policy.json")
    if not os.path.isfile(policy_path):
        results.append({"item": "推荐航班正确性", "score": 0, "max_score": 60, "passed": False, "reason": "无法读取政策文件"})
        write_score(results, workspace)
        return

    with open(policy_path, "r") as f:
        policy = json.load(f)

    max_cost = policy["max_cost_per_booking"]
    allowed_cabin = set(policy["allowed_cabin_classes"])  # {"business","first"}

    # 加载所有平台文件
    platform_files = [
        "aero_cheap.json",
        "flight_pro.json",
        "sky_book.json"
    ]
    all_flights = []
    for pf_name in platform_files:
        pf_path = os.path.join(workspace, "data", "platforms", pf_name)
        if not os.path.isfile(pf_path):
            continue
        with open(pf_path, "r") as f:
            flights = json.load(f)
            all_flights.extend(flights)

    # 过滤符合政策的：舱位允许、价格 <= max_cost
    valid_flights = []
    for fl in all_flights:
        if fl.get("cabin_class") in allowed_cabin and fl.get("price", float('inf')) <= max_cost:
            valid_flights.append(fl)

    if not valid_flights:
        results.append({"item": "推荐航班正确性", "score": 0, "max_score": 60, "passed": False, "reason": "没有符合政策的航班候选"})
        write_score(results, workspace)
        return

    # 找出价格最低的（如果多个同价，取第一个）
    best = min(valid_flights, key=lambda x: x["price"])

    # 现在检查和 agent 输出的匹配
    # 从 rec 中提取字段
    rec_platform = rec.get("platform_id", "")
    rec_flight = rec.get("flight_id", "")
    rec_price = rec.get("price")

    correct = (rec_platform == best["platform_id"] and 
               rec_flight == best["flight_id"] and 
               rec_price == best["price"])

    if correct:
        results.append({"item": "推荐航班正确性", "score": 60, "max_score": 60, "passed": True, "reason": "推荐的航班正确且价格最低符合政策"})
    else:
        # 部分正确：检查可能有一些匹配但价格不对等
        partial_score = 0
        reason_parts = []
        if rec_platform == best["platform_id"]:
            partial_score += 20
            reason_parts.append("平台正确")
        else:
            reason_parts.append(f"平台应为 {best['platform_id']}")
        if rec_flight == best["flight_id"]:
            partial_score += 20
            reason_parts.append("航班号正确")
        else:
            reason_parts.append(f"航班号应为 {best['flight_id']}")
        if isinstance(rec_price, (int, float)) and rec_price == best["price"]:
            partial_score += 20
            reason_parts.append("价格正确")
        else:
            reason_parts.append(f"价格应为 {best['price']}")
        results.append({"item": "推荐航班正确性", "score": partial_score, "max_score": 60, "passed": False, "reason": "; ".join(reason_parts)})

    # 计算总分
    write_score(results, workspace)

def write_score(results, workspace):
    total = sum(r["score"] for r in results)
    max_total = sum(r["max_score"] for r in results)
    score_obj = {
        "total_score": total,
        "details": results
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(score_obj, f, indent=2)
    print(f"Score written to {score_path}: {total}/{max_total}")

if __name__ == "__main__":
    main()
