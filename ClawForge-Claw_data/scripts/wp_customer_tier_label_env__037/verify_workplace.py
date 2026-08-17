import json
import sys
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace)
    details = []
    total_score = 0

    # ---- 1. 检查预期输出文件是否存在 (10分) ----
    output_path = workspace / "ops" / "label_updates.json"
    if not output_path.exists():
        details.append({
            "item": "输出文件 ops/label_updates.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 文件不存在则后续检查无法进行，直接汇总
        total_score = 0
        _write_score(total_score, details)
        return
    else:
        details.append({
            "item": "输出文件 ops/label_updates.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })

    # ---- 2. 检查 JSON 格式合法性 (10分) ----
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        _write_score(10, details)
        return

    # ---- 3. 检查输出结构是否包含 label_updates 列表 (10分) ----
    if not isinstance(data, dict) or "label_updates" not in data:
        details.append({
            "item": "输出包含 label_updates 键",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 label_updates 键或顶层不是字典"
        })
        _write_score(20, details)
        return
    if not isinstance(data["label_updates"], list):
        details.append({
            "item": "label_updates 是列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "label_updates 不是列表"
        })
        _write_score(20, details)
        return
    details.append({
        "item": "输出结构有 label_updates 列表",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "结构正确"
    })

    updates = data["label_updates"]

    # ---- 4. 检查应处理的客户数量 (20分) ----
    # 有效客户：C001, C002, C003, C004
    expected_customers = {"C001", "C002", "C003", "C004"}
    actual_ids = {u.get("customer_id") for u in updates if isinstance(u, dict)}
    if actual_ids == expected_customers:
        details.append({
            "item": "覆盖所有有效客户 (C001~C004)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"客户ID集合正确: {sorted(actual_ids)}"
        })
    else:
        missing = expected_customers - actual_ids
        extra = actual_ids - expected_customers
        reason_parts = []
        if missing:
            reason_parts.append(f"缺少: {sorted(missing)}")
        if extra:
            reason_parts.append(f"多余: {sorted(extra)}")
        details.append({
            "item": "覆盖所有有效客户 (C001~C004)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "; ".join(reason_parts) if reason_parts else "客户ID集合不一致"
        })

    # ---- 5. 检查每个客户的标签是否正确 (每个15分，共60分) ----
    # 构建预期结果字典
    expected_labels = {
        "C001": ["VIP"],           # 消费15000>=10000, 活跃25<=30
        "C002": ["At_Risk"],       # 消费3000<10000, 活跃120>90
        "C003": ["Standard"],      # 消费8000<10000, 活跃60<=90
        "C004": ["High_Value"]     # 消费12000>=10000, 活跃45>30
    }

    # 将 updates 转为 dict 方便查找
    update_dict = {}
    for u in updates:
        if isinstance(u, dict) and "customer_id" in u:
            update_dict[u["customer_id"]] = u.get("labels", [])

    for cid, expected in expected_labels.items():
        if cid not in update_dict:
            details.append({
                "item": f"客户 {cid} 标签正确",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "未找到该客户"
            })
            continue
        actual_labels = update_dict[cid]
        # 标签必须是列表，且内容完全一致（顺序允许不同？规则仅有一个标签，所以顺序不重要）
        if isinstance(actual_labels, list) and set(actual_labels) == set(expected):
            details.append({
                "item": f"客户 {cid} 标签正确",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": f"标签为 {actual_labels}"
            })
        else:
            details.append({
                "item": f"客户 {cid} 标签正确",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"期望 {expected}，实际 {actual_labels}"
            })

    # ---- 汇总总分 ----
    total_score = sum(d["score"] for d in details)
    _write_score(total_score, details)

def _write_score(total, details):
    score_data = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
