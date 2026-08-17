import sys
import json
import os
import re

def verify(workspace):
    details = []
    total_score = 0

    # 辅助函数
    def check(condition, score, max_score, item_name, reason=""):
        nonlocal total_score
        if condition:
            total_score += score
            details.append({"item": item_name, "score": score, "max_score": max_score, "passed": True, "reason": reason})
        else:
            details.append({"item": item_name, "score": 0, "max_score": max_score, "passed": False, "reason": reason})

    # 1. 目录结构 (10分)
    dirs = ["ops", "data/customers", "data/logs"]
    all_dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in dirs)
    check(all_dirs_exist, 10, 10, "Required directories exist", "ops/, data/customers/, data/logs/ all present" if all_dirs_exist else "Missing directories")

    # 2. 结果文件是否存在 (10分)
    result_path = os.path.join(workspace, "ops/customer_tier_label_update.json")
    file_exists = os.path.isfile(result_path)
    check(file_exists, 10, 10, "Result file ops/customer_tier_label_update.json exists", "File found" if file_exists else "File not found")
    if not file_exists:
        # 无法继续，写分数并退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. JSON合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        json_valid = True
    except:
        json_valid = False
    check(json_valid, 10, 10, "Result file is valid JSON", "Valid JSON" if json_valid else "Invalid JSON")
    if not json_valid:
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. 字段完整性 (10分)
    has_updates = isinstance(data, dict) and "updates" in data
    if has_updates:
        updates = data["updates"]
        all_records_valid = all(
            isinstance(r, dict) and all(k in r for k in ("customer_id", "new_label", "reason"))
            for r in updates
        )
    else:
        all_records_valid = False
    check(has_updates and all_records_valid, 10, 10, "Correct structure with updates array and required fields",
          "Structure valid" if all_records_valid else "Missing 'updates' or malformed records")

    if not (has_updates and all_records_valid):
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 构建期望结果（根据env_builder的数据和prompt规则）
    # 期望的客户ID列表（来自customers.json）：C001-C008
    expected_customers = {"C001","C002","C003","C004","C005","C006","C007","C008"}
    # 从updates中提取客户ID集合
    actual_customer_ids = set(r["customer_id"] for r in updates)
    # 检查是否有缺失或多出
    missing = expected_customers - actual_customer_ids
    extra = actual_customer_ids - expected_customers
    check(len(missing) == 0 and len(extra) == 0, 5, 5, "All and only expected customers present",
          f"Missing: {missing}, Extra: {extra}" if missing or extra else "Correct")

    # 现在逐客户检查标签和原因 (每个客户5分，共40分，因为还有10分覆盖+10分忽略高风险)
    # 预定义正确结果
    correct_labels = {
        "C001": {"new_label": "VIP", "reason": "spend≥10000 & active≤30"},
        "C002": {"new_label": "Premium", "reason": "spend≥5000 & active≤60"},
        "C003": {"new_label": "vip", "reason": "risk high, skipped"},
        "C004": {"new_label": "Standard", "reason": "default"},
        "C005": {"new_label": "VIP", "reason": "overridden by ops/overrides.txt"},
        "C006": {"new_label": "VIP", "reason": "spend≥10000 & active≤30"},
        "C007": {"new_label": "silver", "reason": "risk high, skipped"},
        "C008": {"new_label": "Standard", "reason": "default"}
    }

    # 将updates转为字典
    updates_dict = {r["customer_id"]: r for r in updates}
    for cid in expected_customers:
        if cid not in updates_dict:
            check(False, 0, 5, f"Customer {cid} present", "Missing")
            continue
        rec = updates_dict[cid]
        expected = correct_labels[cid]
        label_ok = rec.get("new_label") == expected["new_label"]
        reason_ok = rec.get("reason") == expected["reason"]
        if label_ok and reason_ok:
            check(True, 5, 5, f"Customer {cid} label and reason correct", f"label={expected['new_label']}, reason={expected['reason']}")
        else:
            reason_str = f"Expected label={expected['new_label']}, got={rec.get('new_label')}; Expected reason={expected['reason']}, got={rec.get('reason')}"
            check(False, 0, 5, f"Customer {cid} label and reason correct", reason_str)

    # 5. 覆盖优先级 (已经包含在C005检查中，但为确保权重，额外扣分已在上面体现，不用重复)
    # 6. 忽略高风险 (C003和C007已检查)

    # 额外卫生检查：如果有多余的C009或C010，已经在extra中扣分，这里不再重复
    # 总分已累计

    # 写出评分
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
