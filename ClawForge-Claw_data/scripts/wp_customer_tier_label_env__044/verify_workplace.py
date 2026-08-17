import json
import sys
import os
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. 检查目标文件是否存在
    customers_path = ws / "data/customers/customers.json"
    if customers_path.exists():
        details.append({"item": "customers.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "customers.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        # 后续检查无法进行，直接写入结果并退出
        score_board = {"total_score": 0, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score_board, f, indent=2)
        return

    # 2. 检查 JSON 合法性
    try:
        with open(customers_path, "r") as f:
            data = json.load(f)
        details.append({"item": "customers.json 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "customers.json 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        score_board = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score_board, f, indent=2)
        return

    # 3. 检查是否有 customers 列表
    customers = data.get("customers")
    if customers is None or not isinstance(customers, list):
        details.append({"item": "customers 列表存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 customers 键或不是列表"})
        score_board = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score_board, f, indent=2)
        return
    else:
        details.append({"item": "customers 列表存在", "score": 10, "max_score": 10, "passed": True, "reason": "列表存在"})
        total_score += 10

    # 4. 找到 CarePulse 和 LedgerFlow
    carepulse = None
    ledgerflow = None
    for c in customers:
        if c.get("customer_id") == "CarePulse":
            carepulse = c
        elif c.get("customer_id") == "LedgerFlow":
            ledgerflow = c

    if carepulse is None:
        details.append({"item": "CarePulse 记录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 CarePulse"})
    else:
        details.append({"item": "CarePulse 记录存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到 CarePulse"})
        total_score += 10

    if ledgerflow is None:
        details.append({"item": "LedgerFlow 记录存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 LedgerFlow"})
    else:
        details.append({"item": "LedgerFlow 记录存在", "score": 5, "max_score": 5, "passed": True, "reason": "找到 LedgerFlow"})
        total_score += 5

    # 5. 检查 CarePulse 的 labels 字段
    if carepulse is not None:
        labels = carepulse.get("labels")
        if isinstance(labels, list):
            details.append({"item": "CarePulse labels 为列表", "score": 5, "max_score": 5, "passed": True, "reason": "labels 是列表"})
            total_score += 5
            if "VIP" in labels:
                details.append({"item": "CarePulse labels 包含 VIP", "score": 30, "max_score": 30, "passed": True, "reason": "正确升级为 VIP"})
                total_score += 30
            else:
                details.append({"item": "CarePulse labels 包含 VIP", "score": 0, "max_score": 30, "passed": False, "reason": f"labels 中未包含 VIP，当前值: {labels}"})
        else:
            details.append({"item": "CarePulse labels 为列表", "score": 0, "max_score": 5, "passed": False, "reason": "labels 不是列表"})
            details.append({"item": "CarePulse labels 包含 VIP", "score": 0, "max_score": 30, "passed": False, "reason": "labels 不是列表，无法检查"})

    # 6. 检查 LedgerFlow 的 labels 应保持不变（原始为空列表）
    if ledgerflow is not None:
        lf_labels = ledgerflow.get("labels")
        if isinstance(lf_labels, list) and lf_labels == []:
            details.append({"item": "LedgerFlow labels 未变动", "score": 20, "max_score": 20, "passed": True, "reason": "LedgerFlow 标签保持为空"})
            total_score += 20
        else:
            details.append({"item": "LedgerFlow labels 未变动", "score": 0, "max_score": 20, "passed": False, "reason": f"LedgerFlow 标签被不当修改为 {lf_labels}"})

    # 7. 检查是否修改了其他无关字段（可选加分项：未引入额外字段）
    if carepulse is not None:
        # 检查除了 customer_id, customer_name, industry, tier, labels, owner_name 外没有新增字段
        allowed_keys = {"customer_id", "customer_name", "industry", "tier", "labels", "owner_name"}
        if set(carepulse.keys()) - allowed_keys:
            details.append({"item": "CarePulse 无多余字段", "score": 0, "max_score": 5, "passed": False, "reason": "存在额外字段"})
        else:
            details.append({"item": "CarePulse 无多余字段", "score": 5, "max_score": 5, "passed": True, "reason": "未引入多余字段"})
            total_score += 5

    # 写入最终评分
    score_board = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(score_board, f, indent=2)

if __name__ == "__main__":
    verify()
