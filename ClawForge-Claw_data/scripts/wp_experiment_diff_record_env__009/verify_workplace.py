import os
import sys
import json
import csv
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

SCORE = {"total": 0, "details": []}
MAX_SCORE = 100

def add_score(item, points, passed, reason):
    detail = {
        "item": item,
        "score": points if passed else 0,
        "max_score": points,
        "passed": passed,
        "reason": reason
    }
    SCORE["details"].append(detail)
    SCORE["total"] += detail["score"]

def main():
    # 1. 检查 ops/diff_record.json 是否存在
    diff_path = os.path.join(workspace, "ops", "diff_record.json")
    exists = os.path.isfile(diff_path)
    add_score("产物文件 ops/diff_record.json 存在", 10, exists,
              "文件存在" if exists else "文件缺失")

    if not exists:
        write_score()
        sys.exit(1)

    # 2. 解析 JSON 合法性
    try:
        with open(diff_path, "r") as f:
            data = json.load(f)
        is_valid_json = True
        reason = "JSON 解析成功"
    except Exception as e:
        is_valid_json = False
        reason = f"JSON 解析失败: {e}"
    add_score("JSON 格式合法", 10, is_valid_json, reason)

    if not is_valid_json:
        write_score()
        sys.exit(1)

    # 3. 必须包含 batch_a, batch_b, diff 三个顶层键
    required_keys = ["batch_a", "batch_b", "diff"]
    has_keys = all(k in data for k in required_keys)
    add_score("包含 batch_a, batch_b, diff 字段", 10, has_keys,
              "字段齐全" if has_keys else f"缺失字段: {set(required_keys) - set(data.keys())}")

    if not has_keys:
        write_score()
        sys.exit(1)

    # 4. 每个批次对象必须有 accuracy, latency_ms, cost_usd 平均值
    batch_fields = ["accuracy", "latency_ms", "cost_usd"]
    a_ok = all(f in data["batch_a"] for f in batch_fields)
    b_ok = all(f in data["batch_b"] for f in batch_fields)
    fields_ok = a_ok and b_ok
    add_score("批次对象包含 accuracy, latency_ms, cost_usd", 10, fields_ok,
              "字段正确" if fields_ok else "批次对象缺少必要字段")

    if not fields_ok:
        write_score()
        sys.exit(1)

    # 5. diff 对象必须有对应差值字段（diff_accuracy, diff_latency_ms, diff_cost_usd）
    diff_fields = ["diff_accuracy", "diff_latency_ms", "diff_cost_usd"]
    diff_ok = all(f in data["diff"] for f in diff_fields)
    add_score("diff 对象包含三个差值字段", 10, diff_ok,
              "字段存在" if diff_ok else f"缺失: {[f for f in diff_fields if f not in data['diff']]}")

    if not diff_ok:
        write_score()
        sys.exit(1)

    # 6. 核心计算：读取原始 CSV，过滤脏数据，计算平均值，验证结果
    csv_path = os.path.join(workspace, "data", "experiments", "experiment_results.csv")
    if not os.path.isfile(csv_path):
        add_score("数据源文件存在", 0, False, "experiment_results.csv 缺失")
        write_score()
        sys.exit(1)

    # 读取并解析，过滤无效行
    valid_rows = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                acc = float(row["accuracy"])
                lat = float(row["latency_ms"])
                cost = float(row["cost_usd"])
                bid = row["batch_id"].strip()
                if bid in ("A", "B"):
                    valid_rows.append((bid, acc, lat, cost))
            except (ValueError, KeyError, TypeError):
                continue

    # 按 batch_id 分组计算平均值
    from statistics import mean
    groups = {"A": [], "B": []}
    for bid, acc, lat, cost in valid_rows:
        groups[bid].append((acc, lat, cost))

    if len(groups["A"]) == 0 or len(groups["B"]) == 0:
        add_score("有效数据行数充足", 0, False, "某批次无有效数据")
        write_score()
        sys.exit(1)

    def avg(lst):
        return sum(lst) / len(lst)

    a_acc = avg([x[0] for x in groups["A"]])
    a_lat = avg([x[1] for x in groups["A"]])
    a_cost = avg([x[2] for x in groups["A"]])
    b_acc = avg([x[0] for x in groups["B"]])
    b_lat = avg([x[1] for x in groups["B"]])
    b_cost = avg([x[2] for x in groups["B"]])

    # 计算差值 (B - A)
    diff_acc = b_acc - a_acc
    diff_lat = b_lat - a_lat
    diff_cost = b_cost - a_cost

    # 读取 agent 输出的值
    agent_a_acc = float(data["batch_a"]["accuracy"])
    agent_a_lat = float(data["batch_a"]["latency_ms"])
    agent_a_cost = float(data["batch_a"]["cost_usd"])
    agent_b_acc = float(data["batch_b"]["accuracy"])
    agent_b_lat = float(data["batch_b"]["latency_ms"])
    agent_b_cost = float(data["batch_b"]["cost_usd"])
    agent_diff_acc = float(data["diff"]["diff_accuracy"])
    agent_diff_lat = float(data["diff"]["diff_latency_ms"])
    agent_diff_cost = float(data["diff"]["diff_cost_usd"])

    # 允许小误差（浮点）
    eps = 1e-5

    # 检查 A 平均值
    kor_a = (math.isclose(agent_a_acc, a_acc, abs_tol=eps) and
             math.isclose(agent_a_lat, a_lat, abs_tol=eps) and
             math.isclose(agent_a_cost, a_cost, abs_tol=eps))
    add_score("A 批次平均值计算正确", 20, kor_a,
              f"期望: acc={a_acc:.4f}, lat={a_lat:.4f}, cost={a_cost:.4f}; 实际: acc={agent_a_acc}, lat={agent_a_lat}, cost={agent_a_cost}" if not kor_a else "正确")

    # 检查 B 平均值
    kor_b = (math.isclose(agent_b_acc, b_acc, abs_tol=eps) and
             math.isclose(agent_b_lat, b_lat, abs_tol=eps) and
             math.isclose(agent_b_cost, b_cost, abs_tol=eps))
    add_score("B 批次平均值计算正确", 20, kor_b,
              f"期望: acc={b_acc:.4f}, lat={b_lat:.4f}, cost={b_cost:.4f}; 实际: acc={agent_b_acc}, lat={agent_b_lat}, cost={agent_b_cost}" if not kor_b else "正确")

    # 检查差值
    kor_diff = (math.isclose(agent_diff_acc, diff_acc, abs_tol=eps) and
                math.isclose(agent_diff_lat, diff_lat, abs_tol=eps) and
                math.isclose(agent_diff_cost, diff_cost, abs_tol=eps))
    add_score("差值计算正确 (B - A)", 10, kor_diff,
              f"期望: diff_acc={diff_acc:.4f}, diff_lat={diff_lat:.4f}, diff_cost={diff_cost:.4f}; 实际: diff_acc={agent_diff_acc}, diff_lat={agent_diff_lat}, diff_cost={agent_diff_cost}" if not kor_diff else "正确")

    write_score()

def write_score():
    SCORE["total_score"] = SCORE["total"]
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(SCORE, f, indent=2)
    print(f"验证完成，总分: {SCORE['total_score']}/{MAX_SCORE}")

if __name__ == "__main__":
    main()
