import json
import sys
import os
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # ---------- 1. 目录结构 (10分) ----------
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录存在"})
        total_score += 10
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ 目录不存在"})

    # ---------- 2. 结果文件存在 (10分) ----------
    result_path = ops_dir / "processing_result.json"
    if result_path.is_file():
        details.append({"item": "processing_result.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "processing_result.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 提前返回，后续无法检查
        result = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # ---------- 3. JSON 格式合法 (10分) ----------
    try:
        with open(result_path, "r") as f:
            agent_result = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        agent_result = None

    if agent_result is None:
        result = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # ---------- 4. 退货处理正确 (30分) ----------
    # 读取原始 returns.json
    try:
        with open(ws / "data/returns.json", "r") as f:
            returns_data = json.load(f)
    except Exception as e:
        details.append({"item": "退货处理", "score": 0, "max_score": 30, "passed": False, "reason": f"无法读取原始 returns.json: {e}"})
        returns_data = []

    expected_returns = []
    for r in returns_data:
        if r["status"] == "pending_review":
            if r["reason"] == "defective":
                expected_returns.append({"return_id": r["return_id"], "action": "approve", "new_status": "approved"})
            elif r["reason"] == "wrong item":
                expected_returns.append({"return_id": r["return_id"], "action": "inspect", "new_status": "pending_inspection"})

    actual_returns = agent_result.get("processed_returns", [])
    # 标准化排序后比较
    def sort_key(x):
        return x.get("return_id", "")
    expected_sorted = sorted(expected_returns, key=sort_key)
    actual_sorted = sorted(actual_returns, key=sort_key)
    if expected_sorted == actual_sorted:
        details.append({"item": "退货处理", "score": 30, "max_score": 30, "passed": True, "reason": "退货操作完全正确"})
        total_score += 30
    else:
        details.append({"item": "退货处理", "score": 0, "max_score": 30, "passed": False,
                        "reason": f"预期: {expected_sorted}, 实际: {actual_sorted}"})

    # ---------- 5. 发货更新正确 (20分) ----------
    try:
        with open(ws / "data/shipments.json", "r") as f:
            shipments_data = json.load(f)
    except Exception as e:
        details.append({"item": "发货更新", "score": 0, "max_score": 20, "passed": False, "reason": f"无法读取 shipments.json: {e}"})
        shipments_data = []

    expected_shipments = []
    for s in shipments_data:
        if s["shipment_id"] == "ship_005" and s["status"] == "processing":
            expected_shipments.append({"shipment_id": "ship_005", "new_status": "shipped"})

    actual_shipments = agent_result.get("shipment_updates", [])
    if expected_shipments == actual_shipments:
        details.append({"item": "发货更新", "score": 20, "max_score": 20, "passed": True, "reason": "发货更新正确"})
        total_score += 20
    else:
        details.append({"item": "发货更新", "score": 0, "max_score": 20, "passed": False,
                        "reason": f"预期: {expected_shipments}, 实际: {actual_shipments}"})

    # ---------- 6. 库存调整正确 (20分) ----------
    try:
        with open(ws / "data/inventory/inventory.json", "r") as f:
            inventory_data = json.load(f)
    except Exception as e:
        details.append({"item": "库存调整", "score": 0, "max_score": 20, "passed": False, "reason": f"无法读取 inventory.json: {e}"})
        inventory_data = []

    expected_inv = []
    for i in inventory_data:
        if i["warehouse_id"] == "wh_001" and i["sku"] == "SKU-1002":
            new_stock = i["stock_level"] - 5
            expected_inv.append({"sku": "SKU-1002", "warehouse": "wh_001", "adjustment": -5, "new_stock_level": new_stock})
            break

    actual_inv = agent_result.get("inventory_adjustments", [])
    if expected_inv == actual_inv:
        details.append({"item": "库存调整", "score": 20, "max_score": 20, "passed": True, "reason": "库存调整正确"})
        total_score += 20
    else:
        details.append({"item": "库存调整", "score": 0, "max_score": 20, "passed": False,
                        "reason": f"预期: {expected_inv}, 实际: {actual_inv}"})

    # 总分
    final_score = min(total_score, 100)
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
