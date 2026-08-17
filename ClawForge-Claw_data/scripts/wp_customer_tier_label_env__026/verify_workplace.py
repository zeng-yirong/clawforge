import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score_details = []
    total_score = 0

    # ---------- 1. 目录结构检查 (10分) ----------
    required_files = [
        "ops/tier_labels_result.json",
        "data/customers/customers.json",
        "data/logs/consumption_logs.json",
        "data/logs/activity_logs.json",
        "ops/tier_rules.txt"
    ]
    dir_score = 0
    for f in required_files:
        if (ws / f).exists():
            dir_score += 2
    score_details.append({
        "item": "目录结构完整性",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": f"存在 {dir_score//2}/5 个必需文件"
    })
    total_score += dir_score

    # ---------- 2. 结果文件格式合法性 (10分) ----------
    result_path = ws / "ops/tier_labels_result.json"
    if not result_path.exists():
        score_details.append({
            "item": "结果文件格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/tier_labels_result.json 不存在"
        })
        # 直接输出总分
        finalize(total_score, score_details, ws)
        return

    try:
        with open(result_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        score_details.append({
            "item": "结果文件格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "JSON 解析失败"
        })
        finalize(total_score, score_details, ws)
        return

    if not isinstance(data, dict) or "customers" not in data:
        score_details.append({
            "item": "结果文件格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 customers 字段或顶层非对象"
        })
        finalize(total_score, score_details, ws)
        return

    customers_list = data["customers"]
    if not isinstance(customers_list, list):
        score_details.append({
            "item": "结果文件格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "customers 不是数组"
        })
        finalize(total_score, score_details, ws)
        return

    # 检查每个元素的结构
    format_ok = True
    for c in customers_list:
        if not isinstance(c, dict) or "customer_id" not in c or "labels" not in c:
            format_ok = False
            break
        if not isinstance(c["labels"], list):
            format_ok = False
            break
    if not format_ok:
        score_details.append({
            "item": "结果文件格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "数组元素缺少 customer_id 或 labels，或 labels 不是列表"
        })
        finalize(total_score, score_details, ws)
        return

    score_details.append({
        "item": "结果文件格式",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON 结构合法，所有元素包含必需字段"
    })
    total_score += 10

    # ---------- 3. 内容正确性 (80分：4个客户各20分) ----------
    # 预期结果（基于 env_builder 生成的数据和规则）
    expected = {
        "C001": ["vip", "Gold"],
        "C002": ["Silver", "attention"],
        "C003": ["new", "Bronze"],
        "C004": ["old_partner", "Bronze", "attention"]
    }
    # 将预期标签排序以便比较（标签顺序不重要）
    expected_sorted = {k: sorted(v) for k, v in expected.items()}

    # 从结果中构建实际字典
    result_dict = {}
    for c in customers_list:
        cid = c["customer_id"]
        labels = sorted(c["labels"])
        result_dict[cid] = labels

    # 检查是否有额外客户（不在预期中）
    extra_customers = [cid for cid in result_dict.keys() if cid not in expected_sorted]
    if extra_customers:
        score_details.append({
            "item": "无多余客户",
            "score": 0,
            "max_score": 0,  # 不单独扣分，已在下面客户正确性中体现
            "passed": False,
            "reason": f"发现不应存在的客户: {extra_customers}"
        })
        # 此处我们可以在每个客户分数中体现，但为了简化，直接扣10分
        total_score -= 10  # 从总分子扣
        score_details.append({
            "item": "多余客户惩罚",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"包含额外客户，扣10分"
        })
    else:
        score_details.append({
            "item": "无多余客户",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "没有出现预期之外的客户"
        })
        total_score += 10

    # 检查缺失客户
    missing = [cid for cid in expected_sorted if cid not in result_dict]
    if missing:
        score_details.append({
            "item": "缺失客户",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"缺少客户: {missing}"
        })
        # 同样扣分
        total_score -= 20
        score_details.append({
            "item": "缺失客户惩罚",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"缺少 {len(missing)} 个客户，扣20分"
        })

    # 逐客户比对
    correct_count = 0
    for cid in expected_sorted:
        if cid in result_dict:
            if result_dict[cid] == expected_sorted[cid]:
                correct_count += 1
            else:
                total_score -= 20  # 每个错误客户扣20分
                score_details.append({
                    "item": f"客户 {cid} 标签",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"期望 {expected_sorted[cid]}，实际 {result_dict[cid]}"
                })
        else:
            total_score -= 20
            score_details.append({
                "item": f"客户 {cid} 标签",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "客户缺失"
            })
    # 如果全部正确，加分
    if correct_count == len(expected_sorted):
        score_details.append({
            "item": "所有客户标签正确",
            "score": 80,
            "max_score": 80,
            "passed": True,
            "reason": "4个客户端标签完全匹配"
        })
        total_score += 80

    # 确保总分在 0-100 之间
    total_score = max(0, min(100, total_score))
    finalize(total_score, score_details, ws)

def finalize(total_score, details, ws):
    # 写入 score 文件
    score_obj = {
        "total_score": total_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(score_obj, f, indent=2)
    print(f"总分: {total_score}/100")
    sys.exit(0 if total_score == 100 else 1)

if __name__ == "__main__":
    main()
