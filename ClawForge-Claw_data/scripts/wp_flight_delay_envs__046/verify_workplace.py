import json, os, sys, math

def load_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def check_structure(data, required_keys, allowed_extra=False):
    """Check that data contains exactly the required keys."""
    if not isinstance(data, dict):
        return False
    keys = set(data.keys())
    req = set(required_keys)
    if allowed_extra:
        return req.issubset(keys)
    else:
        return keys == req

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    report_path = os.path.join(workspace, "ops", "cascade_report.json")
    if os.path.isfile(report_path):
        results.append({"item": "报告文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/cascade_report.json 存在"})
        total_score += 10
    else:
        results.append({"item": "报告文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ops/cascade_report.json"})
        # 后续检查依赖该文件，若不存在则直接结束
        finalize(results, total_score, workspace)
        return

    # 2. JSON合法性 (10分)
    try:
        report = load_json(report_path)
        if report is None:
            raise ValueError("文件为空或无法解析")
        results.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total_score += 10
    except Exception as e:
        results.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        finalize(results, total_score, workspace)
        return

    # 3. 顶级字段完整性 (15分): 必须包含 affected_hotel_bookings, affected_transport_bookings, total_affected_passengers, estimated_additional_costs
    required_top = ["affected_hotel_bookings", "affected_transport_bookings", "total_affected_passengers", "estimated_additional_costs"]
    if all(k in report for k in required_top):
        results.append({"item": "顶级字段完整性", "score": 15, "max_score": 15, "passed": True, "reason": "包含所有必需字段"})
        total_score += 15
    else:
        missing = [k for k in required_top if k not in report]
        results.append({"item": "顶级字段完整性", "score": 0, "max_score": 15, "passed": False, "reason": f"缺少字段: {missing}"})
        # 仍然继续检查已有字段

    # 4. affected_hotel_bookings 正确性 (25分)
    # 正确答案: 两个预订 HB01 (HTL12) 和 HB04 (HTL10) 都是 active 且关联 FL001
    expected_hotel = [
        {"booking_id": "HB01", "flight_id": "FL001", "hotel_id": "HTL12", "status": "active"},
        {"booking_id": "HB04", "flight_id": "FL001", "hotel_id": "HTL10", "status": "active"}
    ]
    hotel_list = report.get("affected_hotel_bookings", [])
    if not isinstance(hotel_list, list):
        results.append({"item": "酒店预订列表类型", "score": 0, "max_score": 25, "passed": False, "reason": "类型不是列表"})
    else:
        # 提取每个预订的关键字段，忽略顺序
        actual_set = {(b["booking_id"], b["flight_id"], b["hotel_id"], b["status"]) for b in hotel_list if isinstance(b, dict)}
        expected_set = {(e["booking_id"], e["flight_id"], e["hotel_id"], e["status"]) for e in expected_hotel}
        if actual_set == expected_set:
            results.append({"item": "酒店预订列表内容", "score": 25, "max_score": 25, "passed": True, "reason": "与预期完全匹配"})
            total_score += 25
        else:
            results.append({"item": "酒店预订列表内容", "score": 0, "max_score": 25, "passed": False,
                            "reason": f"实际: {actual_set}, 预期: {expected_set}"})

    # 5. affected_transport_bookings 正确性 (20分)
    # 正确答案: TB01 (TRN01) 和 TB02 (TRN03) 都是 active 且关联 FL001
    expected_transport = [
        {"booking_id": "TB01", "flight_id": "FL001", "transport_id": "TRN01", "status": "active"},
        {"booking_id": "TB02", "flight_id": "FL001", "transport_id": "TRN03", "status": "active"}
    ]
    trans_list = report.get("affected_transport_bookings", [])
    if not isinstance(trans_list, list):
        results.append({"item": "交通预订列表类型", "score": 0, "max_score": 20, "passed": False, "reason": "类型不是列表"})
    else:
        actual_t_set = {(b["booking_id"], b["flight_id"], b["transport_id"], b["status"]) for b in trans_list if isinstance(b, dict)}
        expected_t_set = {(e["booking_id"], e["flight_id"], e["transport_id"], e["status"]) for e in expected_transport}
        if actual_t_set == expected_t_set:
            results.append({"item": "交通预订列表内容", "score": 20, "max_score": 20, "passed": True, "reason": "与预期完全匹配"})
            total_score += 20
        else:
            results.append({"item": "交通预订列表内容", "score": 0, "max_score": 20, "passed": False,
                            "reason": f"实际: {actual_t_set}, 预期: {expected_t_set}"})

    # 6. total_affected_passengers 正确性 (10分)
    # 受影响旅客数：HB01和HB04对应两个不同旅客（预订ID不同），加上TB01、TB02可能重复？但通常一个预订对应一个旅客。
    # 这里简单认为 hotel 有2个不同预订，transport有2个，但可能同一个人既有酒店又有交通？为了简化，我们设答案为4（因为每个预订独立）。
    # 但更合理的是：每个预订代表一个旅客，酒店2个+交通2个 = 4。验证脚本采用此值。
    expected_passengers = 4
    actual_passengers = report.get("total_affected_passengers")
    if isinstance(actual_passengers, int) and actual_passengers == expected_passengers:
        results.append({"item": "受影响旅客数", "score": 10, "max_score": 10, "passed": True, "reason": f"值为{actual_passengers}"})
        total_score += 10
    else:
        results.append({"item": "受影响旅客数", "score": 0, "max_score": 10, "passed": False,
                        f"reason": "预期{expected_passengers}, 实际{actual_passengers}"})

    # 7. estimated_additional_costs 正确性 (10分)
    # 计算：酒店需要重新预订或调整产生的额外费用。假设因为延误，旅客需要在芝加哥多住一晚（原本当天的房间需要延长）。
    # 但为了可判定，我们直接设定一个固定值：酒店HB01和HB04两晚的额外费用？HB01在HTL12（220/晚）、HB04在HTL10（250/晚），
    # 交通TB01（150）、TB02（120）需要重新安排。但假设航空公司承担部分？为了简化，我们预设一个经过计算的数值：
    # 酒店: 每个预订因延误需多付一晚，HB01:220, HB04:250 => 470; 交通: 重新调度费每单50% base_price? TB01:75, TB02:60 =>135;
    # 合计605。但为了唯一，我们直接定605.0。验证时用math.isclose允许浮点误差。
    expected_cost = 605.0
    actual_cost = report.get("estimated_additional_costs")
    if isinstance(actual_cost, (int, float)) and math.isclose(actual_cost, expected_cost, rel_tol=1e-6):
        results.append({"item": "额外费用", "score": 10, "max_score": 10, "passed": True, "reason": f"值为{actual_cost}"})
        total_score += 10
    else:
        results.append({"item": "额外费用", "score": 0, "max_score": 10, "passed": False,
                        f"reason": "预期{expected_cost}, 实际{actual_cost}"})

    finalize(results, total_score, workspace)

def finalize(results, total_score, workspace):
    # 写入结果
    score_file = os.path.join(workspace, "workplace_score.json")
    output = {
        "total_score": min(total_score, 100),
        "details": results
    }
    with open(score_file, "w") as f:
        json.dump(output, f, indent=2)
    # 打印总分（用于日志）
    print(f"Total Score: {output['total_score']}/100")

if __name__ == "__main__":
    main()
