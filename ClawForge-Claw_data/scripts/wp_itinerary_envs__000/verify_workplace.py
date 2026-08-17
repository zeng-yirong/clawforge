import os
import sys
import json
import csv
from datetime import datetime

VALID_YEAR = 2025  # 有效数据的年份门槛（>= 2025-01-01）
USD_RATE = 7.0

def load_effective_routes(data_dir):
    """读取所有有效路线（BJS→SHA，日期>=2025-01-01，货币统一为CNY）"""
    routes = []

    # flights
    flights_path = os.path.join(data_dir, "flights.csv")
    if os.path.exists(flights_path):
        with open(flights_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.strptime(row["date"], "%Y-%m-%d")
                    if date.year < VALID_YEAR:
                        continue
                    if row["origin"]!="BJS" or row["destination"]!="SHA":
                        continue
                    price = float(row["price_cny"])
                    routes.append({
                        "transport": "flight",
                        "route_id": row["route_id"],
                        "total_cost": price
                    })
                except:
                    continue

    # trains
    trains_path = os.path.join(data_dir, "trains.csv")
    if os.path.exists(trains_path):
        with open(trains_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.strptime(row["date"], "%Y-%m-%d")
                    if date.year < VALID_YEAR:
                        continue
                    if row["origin"]!="BJS" or row["destination"]!="SHA":
                        continue
                    price_raw = float(row["price"])
                    if row["currency"] == "USD":
                        price = price_raw * USD_RATE
                    else:
                        price = price_raw
                    routes.append({
                        "transport": "train",
                        "route_id": row["route_id"],
                        "total_cost": price
                    })
                except:
                    continue

    # buses
    buses_path = os.path.join(data_dir, "buses.csv")
    if os.path.exists(buses_path):
        with open(buses_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.strptime(row["date"], "%Y-%m-%d")
                    if date.year < VALID_YEAR:
                        continue
                    if row["origin"]!="BJS" or row["destination"]!="SHA":
                        continue
                    price = float(row["price_cny"])
                    routes.append({
                        "transport": "bus",
                        "route_id": row["route_id"],
                        "total_cost": price
                    })
                except:
                    continue

    return routes

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 ops 目录存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "目录 ops/ 存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ 目录存在"})
        total_score += 5
    else:
        details.append({"item": "目录 ops/ 存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺少 ops/ 目录"})

    # 2. best_option.json 存在 (5分)
    result_path = os.path.join(ops_dir, "best_option.json") if os.path.isdir(ops_dir) else None
    if result_path and os.path.isfile(result_path):
        details.append({"item": "best_option.json 文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        details.append({"item": "best_option.json 文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. JSON 解析合法 (5分)
    try:
        with open(result_path, "r") as f:
            agent_result = json.load(f)
        details.append({"item": "best_option.json 合法 JSON", "score": 5, "max_score": 5, "passed": True, "reason": "解析成功"})
        total_score += 5
    except Exception as e:
        details.append({"item": "best_option.json 合法 JSON", "score": 0, "max_score": 5, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. 必要字段完整性 (10分)
    required_fields = ["origin", "destination", "transport", "route_id", "total_cost"]
    missing = [f for f in required_fields if f not in agent_result]
    if not missing:
        details.append({"item": "结果包含所有必要字段", "score": 10, "max_score": 10, "passed": True, "reason": f"字段齐全: {required_fields}"})
        total_score += 10
    else:
        details.append({"item": "结果包含所有必要字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {missing}"})

    # 5. 数据清洗与正确性 (80分) —— 包含过滤过期、货币转换、最终答案匹配
    # 从源数据重新计算正确答案
    data_dir = os.path.join(workspace, "data")
    effective_routes = load_effective_routes(data_dir)
    if not effective_routes:
        details.append({"item": "有效路线计算", "score": 0, "max_score": 80, "passed": False, "reason": "未能从 data/ 下提取任何有效路线"})
        total_score += 0
    else:
        # 找出最小价格
        min_cost = min(r["total_cost"] for r in effective_routes)
        best_routes = [r for r in effective_routes if r["total_cost"] == min_cost]
        # 预期结果（假设只有一个，但如果有多个我们取第一个作为标准）
        expected = best_routes[0]
        # 检查 agent 结果是否与期望匹配
        agent_origin = agent_result.get("origin")
        agent_dest = agent_result.get("destination")
        agent_transport = agent_result.get("transport")
        agent_route_id = agent_result.get("route_id")
        agent_cost = agent_result.get("total_cost")

        # 先检查基础信息
        base_ok = (agent_origin == "BJS" and agent_dest == "SHA")
        # 再检查 transport/route_id 是否在最佳路线列表中
        match_route = any(
            r["transport"] == agent_transport and r["route_id"] == agent_route_id
            for r in best_routes
        )
        cost_ok = (agent_cost == min_cost)

        if base_ok and match_route and cost_ok:
            details.append({
                "item": "数据清洗与最终答案正确",
                "score": 80,
                "max_score": 80,
                "passed": True,
                "reason": f"正确过滤了过期/诱饵数据，正确转换货币，找到了最省钱的路线 {agent_transport} {agent_route_id} 花费 {agent_cost} 元"
            })
            total_score += 80
        else:
            reason_parts = []
            if not base_ok:
                reason_parts.append(f"起点/终点错误 (期望 BJS→SHA, 得到 {agent_origin}→{agent_dest})")
            if not match_route:
                reason_parts.append(f"交通工具/班次不在最佳路线中 (最佳是 {best_routes})")
            if not cost_ok:
                reason_parts.append(f"总花费 {agent_cost} 不等于最低价 {min_cost}")
            details.append({
                "item": "数据清洗与最终答案正确",
                "score": 0,
                "max_score": 80,
                "passed": False,
                "reason": "; ".join(reason_parts)
            })
            total_score += 0

    # 写入评分文件
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
