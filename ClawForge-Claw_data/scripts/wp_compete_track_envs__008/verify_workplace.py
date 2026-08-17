import json
import os
import sys
import re
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    errors = []
    details = []

    # 1. 检查目录结构 (5分)
    dirs_to_check = ["ops/alerts", "data/competitors", "data/policies"]
    dir_score = 0
    dir_max = 5
    dir_reasons = []
    for d in dirs_to_check:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 2
            dir_reasons.append(f"Directory '{d}' exists")
        else:
            dir_reasons.append(f"Directory '{d}' missing")
    details.append({
        "item": "Required directories exist",
        "score": min(dir_score, 5),
        "max_score": dir_max,
        "passed": dir_score == 6,
        "reason": "; ".join(dir_reasons)
    })

    # 2. 产物文件是否存在 (10分)
    target_path = os.path.join(workspace, "ops/alerts/top_risks.json")
    file_exists = os.path.isfile(target_path)
    if file_exists:
        details.append({
            "item": "ops/alerts/top_risks.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found"
        })
    else:
        details.append({
            "item": "ops/alerts/top_risks.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 如果文件不存在，后续检查直接失败
        summary = {"total_score": details[-1]["score"], "details": details}
        write_score(workspace, summary)
        sys.exit(0)

    # 3. JSON 合法性 (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        json_valid = True
        details.append({
            "item": "top_risks.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully"
        })
    except Exception as e:
        details.append({
            "item": "top_risks.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        write_score(workspace, {"total_score": sum(d["score"] for d in details), "details": details})
        sys.exit(0)

    # 4. 数据结构合法性 (15分)
    # 预期是列表，元素含 competitor_id, name, score
    struct_score = 0
    struct_max = 15
    struct_reasons = []
    if isinstance(data, list):
        struct_score += 3
        struct_reasons.append("Root is a list")
    else:
        struct_reasons.append("Root is not a list")
    # 至少有两个元素
    if len(data) >= 2:
        struct_score += 3
        struct_reasons.append("Has at least 2 entries")
    else:
        struct_reasons.append("Less than 2 entries")
    # 每个元素检查字段
    all_fields_ok = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            all_fields_ok = False
            struct_reasons.append(f"Entry {i} is not a dict")
            continue
        for key in ["competitor_id", "name", "score"]:
            if key not in entry:
                all_fields_ok = False
                struct_reasons.append(f"Entry {i} missing key '{key}'")
    if all_fields_ok:
        struct_score += 9
        struct_reasons.append("All entries have required fields")
    else:
        struct_reasons.append("Some entries missing required fields")
    details.append({
        "item": "Data structure (list of dicts with competitor_id, name, score)",
        "score": struct_score,
        "max_score": struct_max,
        "passed": struct_score == struct_max,
        "reason": "; ".join(struct_reasons)
    })
    if not all_fields_ok or len(data) < 2:
        write_score(workspace, {"total_score": sum(d["score"] for d in details), "details": details})
        sys.exit(0)

    # 5. 内容正确性 —— 关键计算 (60分)
    # 提取第一个（最高威胁）和第二个条目
    first = data[0]
    second = data[1]

    # 5a. 检查 competitor_id 和 name 的期望值 (20分)
    expected_ids = {"nn004": "NeuralNet", "df001": "DataFlow AI"}
    id_name_score = 0
    id_name_max = 20
    id_reasons = []
    # 两个条目必须分别对应这两个竞品（顺序可交换？但我们按得分排序，DataFlow AI 得分应更高）
    # 期望 DataFlow AI 是第一，NeuralNet 第二
    if first["competitor_id"] == "df001" and first["name"] == "DataFlow AI":
        id_name_score += 10
        id_reasons.append("First entry is DataFlow AI (correct ID and name)")
    elif first["competitor_id"] == "nn004" and first["name"] == "NeuralNet":
        id_name_score += 10
        id_reasons.append("First entry is NeuralNet (correct ID and name) — but expected DataFlow AI as highest risk")
        # 允许这种顺序吗？若得分算法不同，可能顺序反了，我们后面检查得分排序再扣分
    else:
        id_reasons.append(f"First entry is {first.get('competitor_id')}/{first.get('name')}, expected DataFlow AI or NeuralNet")

    if second["competitor_id"] == "nn004" and second["name"] == "NeuralNet":
        id_name_score += 10
        id_reasons.append("Second entry is NeuralNet (correct)")
    elif second["competitor_id"] == "df001" and second["name"] == "DataFlow AI":
        id_name_score += 10
        id_reasons.append("Second entry is DataFlow AI (correct) — but order may be swapped")
    else:
        id_reasons.append(f"Second entry is {second.get('competitor_id')}/{second.get('name')}, expected the other")

    details.append({
        "item": "Competitor IDs and names match required entries",
        "score": id_name_score,
        "max_score": id_name_max,
        "passed": id_name_score == id_name_max,
        "reason": "; ".join(id_reasons)
    })

    # 5b. 检查得分计算 (20分)
    # 基准公式：score = market_cap * 0.001 + user_count * 0.01
    # DataFlow AI: market_cap=2000000, user_count=500000 → 2000 + 5000 = 7000
    # NeuralNet: market_cap=500000, user_count=100000 → 500 + 1000 = 1500
    expected_scores = {"df001": 7000.0, "nn004": 1500.0}
    score_calc_score = 0
    score_calc_max = 20
    score_reasons = []
    # 允许误差 0.5 以内
    def approx_eq(a, b, tol=0.5):
        return abs(a - b) <= tol

    for entry in data:
        cid = entry["competitor_id"]
        if cid in expected_scores:
            exp = expected_scores[cid]
            actual = entry["score"]
            if approx_eq(actual, exp):
                score_calc_score += 10
                score_reasons.append(f"{cid}: score {actual} ≈ expected {exp}")
            else:
                score_reasons.append(f"{cid}: score {actual} != expected {exp}, diff={abs(actual-exp)}")
        else:
            # 不应该有其他ID
            score_reasons.append(f"Unexpected competitor_id {cid} in result")
    details.append({
        "item": "Score calculation (approx market_cap*0.001 + user_count*0.01)",
        "score": score_calc_score,
        "max_score": score_calc_max,
        "passed": score_calc_score == score_calc_max,
        "reason": "; ".join(score_reasons)
    })

    # 5c. 排序检查 (20分)
    sort_score = 0
    sort_max = 20
    sort_reasons = []
    if len(data) >= 2:
        if data[0]["score"] >= data[1]["score"]:
            sort_score += 10
            sort_reasons.append("Entries sorted descending by score")
        else:
            sort_reasons.append("Entries not sorted descending")
        # 额外检查没有其他条目得分高于第一
        if all(data[0]["score"] >= entry["score"] for entry in data):
            sort_score += 10
            sort_reasons.append("First entry is truly highest")
        else:
            sort_reasons.append("First entry is not the highest")
    details.append({
        "item": "Result sorted correctly (descending score)",
        "score": sort_score,
        "max_score": sort_max,
        "passed": sort_score == sort_max,
        "reason": "; ".join(sort_reasons)
    })

    # 6. 无多余条目 (10分) – 只应有2个条目
    extra_score = 0
    extra_max = 10
    if len(data) == 2:
        extra_score = 10
        details.append({
            "item": "Exactly 2 entries in result",
            "score": extra_score,
            "max_score": extra_max,
            "passed": True,
            "reason": "No extra entries"
        })
    else:
        details.append({
            "item": "Exactly 2 entries in result",
            "score": 0,
            "max_score": extra_max,
            "passed": False,
            "reason": f"Found {len(data)} entries, expected 2"
        })

    # 计算总分
    total_score = sum(d["score"] for d in details)
    summary = {
        "total_score": min(total_score, 100),
        "details": details
    }
    write_score(workspace, summary)

def write_score(workspace, summary):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
