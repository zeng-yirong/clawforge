"""
验证 agent 生成的 ops/reconciliation_result.json 是否符合预期。
满分100分，细粒度扣分项见 details。
"""
import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = Path(workspace) / "ops" / "reconciliation_result.json"
    details = []
    total_score = 0

    # 1. 文件存在且合法 JSON（10分）
    if not result_path.exists():
        details.append({"item": "文件存在", "score": 0, "max_score": 10, "passed": False,
                        "reason": "ops/reconciliation_result.json 不存在"})
        write_score(details, total_score)
        return
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
        details.append({"item": "文件存在且JSON合法", "score": 10, "max_score": 10, "passed": True,
                        "reason": "文件存在且解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "文件存在且JSON合法", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"JSON解析失败: {str(e)}"})
        write_score(details, total_score)
        return

    # 定义辅助函数
    def check_object(obj, expected_keys, allowed_extra_keys=None):
        """检查对象是否包含所有预期键，返回 (缺失, 多余)"""
        if allowed_extra_keys is None:
            allowed_extra_keys = set()
        keys = set(obj.keys())
        missing = set(expected_keys) - keys
        extra = keys - set(expected_keys) - allowed_extra_keys
        return missing, extra

    # ===== 退货处理（40分）=====
    processed_returns = data.get("processed_returns", [])
    if not isinstance(processed_returns, list):
        details.append({"item": "processed_returns 类型", "score": 0, "max_score": 5, "passed": False,
                        "reason": "processed_returns 不是列表"})
        # 注意：这里我们给5分权重，但后面还有具体检查，为了简化我们合并到后面的项中。
        # 实际我们单独给 processed_returns 存在性5分，后面具体内容35分。
        # 但为了计算方便，我们把存在性和内容一起处理。
        # 我们重新组织：先检查存在性，再遍历检查每一项。
    # 重新设计：processed_returns 存在且为list 给5分
    if not isinstance(processed_returns, list):
        details.append({"item": "processed_returns 存在且为列表", "score": 0, "max_score": 5, "passed": False,
                        "reason": "processed_returns 不存在或不是列表"})
        total_score += 0
    else:
        details.append({"item": "processed_returns 存在且为列表", "score": 5, "max_score": 5, "passed": True,
                        "reason": "processed_returns 是有效列表"})
        total_score += 5

        # 检查 ret_001
        ret001 = None
        ret003 = None
        for item in processed_returns:
            if item.get("return_id") == "ret_001":
                ret001 = item
            elif item.get("return_id") == "ret_003":
                ret003 = item

        # ret_001 评分（15分：return_id 正确5 + action 正确5 + resolution 正确5，无多余键另算）
        def score_return(ret_item, expected_id, expected_action, expected_resolution):
            sub_details = []
            sub_score = 0
            # return_id
            if ret_item.get("return_id") == expected_id:
                sub_details.append({"item": f"{expected_id} return_id", "score": 5, "max_score": 5, "passed": True,
                                    "reason": f"return_id 正确"})
                sub_score += 5
            else:
                sub_details.append({"item": f"{expected_id} return_id", "score": 0, "max_score": 5, "passed": False,
                                    "reason": f"return_id 应为 {expected_id}，实际为 {ret_item.get('return_id')}"})
            # action
            if ret_item.get("action") == expected_action:
                sub_details.append({"item": f"{expected_id} action", "score": 5, "max_score": 5, "passed": True,
                                    "reason": f"action 正确"})
                sub_score += 5
            else:
                sub_details.append({"item": f"{expected_id} action", "score": 0, "max_score": 5, "passed": False,
                                    "reason": f"action 应为 {expected_action}，实际为 {ret_item.get('action')}"})
            # resolution
            if ret_item.get("resolution") == expected_resolution:
                sub_details.append({"item": f"{expected_id} resolution", "score": 5, "max_score": 5, "passed": True,
                                    "reason": f"resolution 正确"})
                sub_score += 5
            else:
                sub_details.append({"item": f"{expected_id} resolution", "score": 0, "max_score": 5, "passed": False,
                                    "reason": f"resolution 应为 {expected_resolution}，实际为 {ret_item.get('resolution')}"})
            # 无多余键（允许额外键，但额外键扣2分，最多扣到0）
            expected_keys = ["return_id", "action", "resolution"]
            missing, extra = check_object(ret_item, expected_keys)
            extra_penalty = min(len(extra) * 2, 5)  # 每个多余键扣2分，最多扣5分
            if extra_penalty > 0:
                sub_details.append({"item": f"{expected_id} 无多余字段", "score": max(0, 5 - extra_penalty),
                                    "max_score": 5, "passed": extra_penalty == 0,
                                    "reason": f"存在额外字段: {extra}"})
                sub_score += max(0, 5 - extra_penalty)
            else:
                sub_details.append({"item": f"{expected_id} 无多余字段", "score": 5, "max_score": 5, "passed": True,
                                    "reason": "无多余字段"})
                sub_score += 5
            return sub_score, sub_details

        if ret001 is None:
            details.append({"item": "ret_001 存在", "score": 0, "max_score": 20, "passed": False,
                            "reason": "未找到 return_id=ret_001 的项"})
        else:
            sub_score, sub_det = score_return(ret001, "ret_001", "approve", "refund_approved")
            total_score += sub_score
            details.extend(sub_det)

        if ret003 is None:
            details.append({"item": "ret_003 存在", "score": 0, "max_score": 20, "passed": False,
                            "reason": "未找到 return_id=ret_003 的项"})
        else:
            sub_score, sub_det = score_return(ret003, "ret_003", "inspect", "exchange")
            total_score += sub_score
            details.extend(sub_det)

    # ===== 发货更新（20分）=====
    updated_shipments = data.get("updated_shipments", [])
    if not isinstance(updated_shipments, list):
        details.append({"item": "updated_shipments 存在且为列表", "score": 0, "max_score": 5, "passed": False,
                        "reason": "updated_shipments 不存在或不是列表"})
        total_score += 0
    else:
        details.append({"item": "updated_shipments 存在且为列表", "score": 5, "max_score": 5, "passed": True,
                        "reason": "updated_shipments 是有效列表"})
        total_score += 5

        ship_005 = None
        for item in updated_shipments:
            if item.get("shipment_id") == "ship_005":
                ship_005 = item
                break
        if ship_005 is None:
            details.append({"item": "ship_005 存在", "score": 0, "max_score": 15, "passed": False,
                            "reason": "未找到 shipment_id=ship_005 的项"})
        else:
            # shipment_id 正确（5分）
            if ship_005.get("shipment_id") == "ship_005":
                details.append({"item": "ship_005 shipment_id", "score": 5, "max_score": 5, "passed": True,
                                "reason": "shipment_id 正确"})
                total_score += 5
            else:
                details.append({"item": "ship_005 shipment_id", "score": 0, "max_score": 5, "passed": False,
                                "reason": f"shipment_id 应为 ship_005，实际为 {ship_005.get('shipment_id')}"})
            # new_status 正确（10分）
            if ship_005.get("new_status") == "shipped":
                details.append({"item": "ship_005 new_status", "score": 10, "max_score": 10, "passed": True,
                                "reason": "new_status 正确"})
                total_score += 10
            else:
                details.append({"item": "ship_005 new_status", "score": 0, "max_score": 10, "passed": False,
                                "reason": f"new_status 应为 shipped，实际为 {ship_005.get('new_status')}"})
            # 无多余字段
            expected_keys = ["shipment_id", "new_status"]
            missing, extra = check_object(ship_005, expected_keys)
            extra_penalty = min(len(extra) * 2, 5)
            if extra_penalty > 0:
                details.append({"item": "ship_005 无多余字段", "score": max(0, 5 - extra_penalty),
                                "max_score": 5, "passed": extra_penalty == 0,
                                "reason": f"存在额外字段: {extra}"})
                total_score += max(0, 5 - extra_penalty)
            else:
                details.append({"item": "ship_005 无多余字段", "score": 5, "max_score": 5, "passed": True,
                                "reason": "无多余字段"})
                total_score += 5

    # ===== 库存调整（20分）=====
    inventory_adjustments = data.get("inventory_adjustments", [])
    if not isinstance(inventory_adjustments, list):
        details.append({"item": "inventory_adjustments 存在且为列表", "score": 0, "max_score": 5, "passed": False,
                        "reason": "inventory_adjustments 不存在或不是列表"})
        total_score += 0
    else:
        details.append({"item": "inventory_adjustments 存在且为列表", "score": 5, "max_score": 5, "passed": True,
                        "reason": "inventory_adjustments 是有效列表"})
        total_score += 5

        adj_target = None
        for item in inventory_adjustments:
            if item.get("sku") == "SKU-1002" and item.get("warehouse") == "wh_001":
                adj_target = item
                break
        if adj_target is None:
            details.append({"item": "SKU-1002/wh_001 调整存在", "score": 0, "max_score": 15, "passed": False,
                            "reason": "未找到 sku=SKU-1002, warehouse=wh_001 的调整项"})
        else:
            # sku 正确（3分）
            if adj_target.get("sku") == "SKU-1002":
                details.append({"item": "调整 sku", "score": 3, "max_score": 3, "passed": True,
                                "reason": "sku 正确"})
                total_score += 3
            else:
                details.append({"item": "调整 sku", "score": 0, "max_score": 3, "passed": False,
                                "reason": f"sku 应为 SKU-1002，实际为 {adj_target.get('sku')}"})
            # warehouse 正确（2分）
            if adj_target.get("warehouse") == "wh_001":
                details.append({"item": "调整 warehouse", "score": 2, "max_score": 2, "passed": True,
                                "reason": "warehouse 正确"})
                total_score += 2
            else:
                details.append({"item": "调整 warehouse", "score": 0, "max_score": 2, "passed": False,
                                "reason": f"warehouse 应为 wh_001，实际为 {adj_target.get('warehouse')}"})
            # adjustment 正确（5分）
            if adj_target.get("adjustment") == -5:
                details.append({"item": "调整 adjustment", "score": 5, "max_score": 5, "passed": True,
                                "reason": "adjustment 正确"})
                total_score += 5
            else:
                details.append({"item": "调整 adjustment", "score": 0, "max_score": 5, "passed": False,
                                "reason": f"adjustment 应为 -5，实际为 {adj_target.get('adjustment')}"})
            # reason 正确（5分）
            if adj_target.get("reason") == "damage":
                details.append({"item": "调整 reason", "score": 5, "max_score": 5, "passed": True,
                                "reason": "reason 正确"})
                total_score += 5
            else:
                details.append({"item": "调整 reason", "score": 0, "max_score": 5, "passed": False,
                                "reason": f"reason 应为 damage，实际为 {adj_target.get('reason')}"})
            # 无多余字段
            expected_keys = ["sku", "warehouse", "adjustment", "reason"]
            missing, extra = check_object(adj_target, expected_keys)
            extra_penalty = min(len(extra) * 2, 5)
            if extra_penalty > 0:
                details.append({"item": "调整项无多余字段", "score": max(0, 5 - extra_penalty),
                                "max_score": 5, "passed": extra_penalty == 0,
                                "reason": f"存在额外字段: {extra}"})
                total_score += max(0, 5 - extra_penalty)
            else:
                details.append({"item": "调整项无多余字段", "score": 5, "max_score": 5, "passed": True,
                                "reason": "无多余字段"})
                total_score += 5

    # ===== 无多余项（10分）=====
    # processed_returns 只能有 ret_001 和 ret_003
    if isinstance(processed_returns, list):
        actual_ids = {item.get("return_id") for item in processed_returns}
        expected_ids = {"ret_001", "ret_003"}
        if actual_ids == expected_ids:
            details.append({"item": "processed_returns 无多余退货", "score": 3, "max_score": 3, "passed": True,
                            "reason": "只包含 ret_001 和 ret_003"})
            total_score += 3
        else:
            extra_ids = actual_ids - expected_ids
            missing_ids = expected_ids - actual_ids
            details.append({"item": "processed_returns 无多余退货", "score": 0, "max_score": 3, "passed": False,
                            "reason": f"多余退货: {extra_ids}, 缺失: {missing_ids}"})

    if isinstance(updated_shipments, list):
        actual_ship_ids = {item.get("shipment_id") for item in updated_shipments if item.get("shipment_id")}
        expected_ship_ids = {"ship_005"}
        if actual_ship_ids == expected_ship_ids:
            details.append({"item": "updated_shipments 无多余发货", "score": 3, "max_score": 3, "passed": True,
                            "reason": "只包含 ship_005"})
            total_score += 3
        else:
            extra = actual_ship_ids - expected_ship_ids
            missing = expected_ship_ids - actual_ship_ids
            details.append({"item": "updated_shipments 无多余发货", "score": 0, "max_score": 3, "passed": False,
                            "reason": f"多余: {extra}, 缺失: {missing}"})

    if isinstance(inventory_adjustments, list):
        actual_adj_keys = {(item.get("sku"), item.get("warehouse")) for item in inventory_adjustments if item.get("sku") and item.get("warehouse")}
        expected_adj_keys = {("SKU-1002", "wh_001")}
        if actual_adj_keys == expected_adj_keys:
            details.append({"item": "inventory_adjustments 无多余调整", "score": 4, "max_score": 4, "passed": True,
                            "reason": "只包含 (SKU-1002, wh_001)"})
            total_score += 4
        else:
            extra = actual_adj_keys - expected_adj_keys
            missing = expected_adj_keys - actual_adj_keys
            details.append({"item": "inventory_adjustments 无多余调整", "score": 0, "max_score": 4, "passed": False,
                            "reason": f"多余: {extra}, 缺失: {missing}"})

    # 保证总分不超过100
    total_score = min(total_score, 100)
    write_score(details, total_score)

def write_score(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"评分完成，总分: {total_score}")

if __name__ == "__main__":
    main()
