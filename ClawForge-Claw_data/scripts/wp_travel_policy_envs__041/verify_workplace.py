#!/usr/bin/env python3
import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    max_total = 100

    # 1. 检查目标文件是否存在 (10分)
    target_path = os.path.join(workspace, "ops/approval_request.json")
    item1 = {"item": "目标文件 ops/approval_request.json 存在", "max_score": 10}
    if os.path.exists(target_path):
        item1["score"] = 10
        item1["passed"] = True
        item1["reason"] = "文件存在"
    else:
        item1["score"] = 0
        item1["passed"] = False
        item1["reason"] = "文件不存在"
    details.append(item1)
    score += item1["score"]

    # 2. 文件格式合法性 (10分)
    item2 = {"item": "JSON 格式合法，可解析", "max_score": 10}
    if item1["passed"]:
        try:
            with open(target_path, "r") as f:
                data = json.load(f)
            item2["score"] = 10
            item2["passed"] = True
            item2["reason"] = "JSON 解析成功"
        except Exception as e:
            item2["score"] = 0
            item2["passed"] = False
            item2["reason"] = f"JSON 解析失败: {str(e)}"
    else:
        item2["score"] = 0
        item2["passed"] = False
        item2["reason"] = "文件不存在，跳过"
    details.append(item2)
    score += item2["score"]

    if not item1["passed"] or not item2["passed"]:
        # 无法继续，直接输出结果
        result = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 以下利用 data 进行字段校验
    # 期望的答案（由 env_builder 数据唯一确定）：
    # 最便宜且合规的航班：AeroCheap 的 AC301，base_price=7100, 总成本=7100*(1+0.03+0.01)=7384
    # 平台：aerocheap, 政策：BP001, 账户：ACC001, 日期：2026-06-15, 舱位: business
    expected = {
        "account_id": "ACC001",
        "policy_id": "BP001",
        "platform_id": "aerocheap",
        "flight_id": "AC301",
        "total_cost": 7384,  # 7100 * (1+0.04) 精确计算: 7100*1.04=7384.0，取整数7384
        "cabin_class": "business",
        "departure_date": "2026-06-15",
        "route": "JFK-LHR"
    }

    # 3. 检查必需字段完整性 (10分)
    required_fields = ["account_id", "policy_id", "platform_id", "flight_id", "total_cost", "cabin_class", "departure_date", "route"]
    item3 = {"item": "必备字段齐全", "max_score": 10}
    missing = [f for f in required_fields if f not in data]
    if not missing:
        item3["score"] = 10
        item3["passed"] = True
        item3["reason"] = "所有必需字段存在"
    else:
        item3["score"] = 0
        item3["passed"] = False
        item3["reason"] = f"缺少字段: {', '.join(missing)}"
    details.append(item3)
    score += item3["score"]

    # 4. 字段值准确性 (70分，分配权重)
    field_checks = [
        ("account_id", data.get("account_id"), "ACC001", 10),
        ("policy_id", data.get("policy_id"), "BP001", 10),
        ("platform_id", data.get("platform_id"), "aerocheap", 10),
        ("flight_id", data.get("flight_id"), "AC301", 10),
        ("total_cost", data.get("total_cost"), 7384, 15),
        ("cabin_class", data.get("cabin_class"), "business", 5),
        ("departure_date", data.get("departure_date"), "2026-06-15", 5),
        ("route", data.get("route"), "JFK-LHR", 5),
    ]
    for fname, actual, expect, weight in field_checks:
        item_sub = {"item": f"字段 '{fname}' 值正确", "max_score": weight}
        if actual == expect:
            item_sub["score"] = weight
            item_sub["passed"] = True
            item_sub["reason"] = f"值为 {repr(actual)}"
        else:
            item_sub["score"] = 0
            item_sub["passed"] = False
            item_sub["reason"] = f"期望 {repr(expect)}，实际 {repr(actual)}"
        details.append(item_sub)
        score += item_sub["score"]

    # 总分不超过100
    total = min(score, max_total)
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
