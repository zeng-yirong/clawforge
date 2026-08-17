import sys
import json
import os
from datetime import datetime, timedelta

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops", "reschedule.json")
    details = []
    total_score = 0

    # 1. 文件存在性 (10分)
    if not os.path.isfile(result_path):
        details.append({"item": "文件存在", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"未找到 ops/reschedule.json"})
        write_score(total_score, details)
        return

    details.append({"item": "文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10

    # 2. JSON 合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"JSON解析失败: {e}"})
        write_score(total_score, details)
        return

    details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
    total_score += 10

    # 3. 必须包含 hotel_adjustments 和 transport_adjustments (5分)
    if not isinstance(data, dict):
        details.append({"item": "顶层结构为字典", "score": 0, "max_score": 5, "passed": False, "reason": "顶层不是字典"})
        write_score(total_score, details)
        return
    has_hotel = "hotel_adjustments" in data
    has_transport = "transport_adjustments" in data
    if not (has_hotel and has_transport):
        missing = []
        if not has_hotel: missing.append("hotel_adjustments")
        if not has_transport: missing.append("transport_adjustments")
        details.append({"item": "包含所需字段", "score": 0, "max_score": 5, "passed": False,
                        "reason": f"缺少字段: {missing}"})
        write_score(total_score, details)
        return
    details.append({"item": "包含所需字段", "score": 5, "max_score": 5, "passed": True, "reason": "包含两个调整列表"})
    total_score += 5

    hotel_adjs = data["hotel_adjustments"]
    transport_adjs = data["transport_adjustments"]

    # 4. 酒店调整正确性 (40分) — 只应包含 HB001
    # 干扰项 HB002(已取消) HB003(正常航班) HB004(过期) 不应出现
    hotel_expected = {
        "HB001": {
            "new_check_in": "2025-04-11",
            "new_check_out": "2025-04-14"
        }
    }
    hotel_score = 0
    hotel_passed = True
    hotel_reason = []

    # 检查数量
    if len(hotel_adjs) != 1:
        hotel_passed = False
        hotel_reason.append(f"期望1条酒店调整，实际{len(hotel_adjs)}条")
    else:
        adj = hotel_adjs[0]
        if not isinstance(adj, dict):
            hotel_passed = False
            hotel_reason.append("调整项不是字典")
        else:
            # 检查原booking_id
            bid = adj.get("booking_id")
            if bid != "HB001":
                hotel_passed = False
                hotel_reason.append(f"期望booking_id HB001，实际{bid}")
            # 检查日期
            new_ci = adj.get("new_check_in")
            new_co = adj.get("new_check_out")
            if new_ci != "2025-04-11":
                hotel_passed = False
                hotel_reason.append(f"期望new_check_in 2025-04-11，实际{new_ci}")
            if new_co != "2025-04-14":
                hotel_passed = False
                hotel_reason.append(f"期望new_check_out 2025-04-14，实际{new_co}")

    if hotel_passed:
        hotel_score = 40
    else:
        hotel_score = 0

    details.append({"item": "酒店调整正确", "score": hotel_score, "max_score": 40, "passed": hotel_passed,
                    "reason": "; ".join(hotel_reason) if hotel_reason else "完全正确"})
    total_score += hotel_score

    # 5. 交通调整正确性 (35分) — 只应包含 TB001
    transport_expected = {
        "TB001": {
            "new_pickup_datetime": "2025-04-11 00:30"
        }
    }
    transport_score = 0
    transport_passed = True
    transport_reason = []

    if len(transport_adjs) != 1:
        transport_passed = False
        transport_reason.append(f"期望1条交通调整，实际{len(transport_adjs)}条")
    else:
        adj = transport_adjs[0]
        if not isinstance(adj, dict):
            transport_passed = False
            transport_reason.append("调整项不是字典")
        else:
            bid = adj.get("booking_id")
            if bid != "TB001":
                transport_passed = False
                transport_reason.append(f"期望booking_id TB001，实际{bid}")
            new_pickup = adj.get("new_pickup_datetime")
            if new_pickup != "2025-04-11 00:30":
                transport_passed = False
                transport_reason.append(f"期望new_pickup_datetime 2025-04-11 00:30，实际{new_pickup}")

    if transport_passed:
        transport_score = 35
    else:
        transport_score = 0

    details.append({"item": "交通调整正确", "score": transport_score, "max_score": 35, "passed": transport_passed,
                    "reason": "; ".join(transport_reason) if transport_reason else "完全正确"})
    total_score += transport_score

    # 6. 额外检查：不得包含无关字段（比如 status 等不期望的顶层字段） (作为扣分项，但这里简单给分)
    # 实际上若包含多余顶层 key，自动扣10分？为了简单，我们增加一个“无多余字段”检查
    expected_keys = {"hotel_adjustments", "transport_adjustments"}
    actual_keys = set(data.keys())
    extra = actual_keys - expected_keys
    extra_score = 0
    if extra:
        details.append({"item": "无多余顶层字段", "score": 0, "max_score": 0, "passed": False,
                        "reason": f"包含额外字段: {extra}"})
        # 不扣分，但记录
    else:
        details.append({"item": "无多余顶层字段", "score": 0, "max_score": 0, "passed": True, "reason": "无多余字段"})

    # 最终总分
    total_score = min(total_score, 100)  # 保险
    write_score(total_score, details)

def write_score(total, details):
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
