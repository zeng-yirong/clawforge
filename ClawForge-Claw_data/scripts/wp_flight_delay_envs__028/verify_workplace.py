import json
import os
import sys
from datetime import datetime, timedelta

def verify(workspace):
    report = {
        "total_score": 0,
        "details": []
    }

    # ---------- 辅助函数 ----------
    def add_item(name, score, max_score, passed, reason):
        report["details"].append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # 1. 检查产物文件存在性
    result_path = os.path.join(workspace, "ops", "resolution.json")
    if not os.path.isfile(result_path):
        add_item("产物文件 existence", 0, 10, False, "文件 ops/resolution.json 不存在")
        report["total_score"] = sum(d["score"] for d in report["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(report, f, indent=2)
        return

    max_scores = {
        "file_exists": 10,
        "json_valid": 10,
        "correct_booking_ids": 30,  # HB-001 + TB-001 各15
        "correct_new_times": 30,    # 各15
        "no_extra": 10,
        "structure": 10
    }
    # 先给文件存在分
    add_item("产物文件 ops/resolution.json 存在", 10, 10, True, "文件存在")

    # 2. 解析 JSON
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        add_item("JSON 合法性", 0, 10, False, f"无法解析 JSON: {e}")
        report["total_score"] = sum(d["score"] for d in report["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(report, f, indent=2)
        return

    # 检查根是否为字典且包含关键字段
    if not isinstance(data, dict):
        add_item("JSON 结构", 0, 10, False, "根必须是字典")
        # 但继续检查内容?
        # 这里我们给0并返回
        report["total_score"] = sum(d["score"] for d in report["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(report, f, indent=2)
        return

    # 结构分：至少包含 "affected_bookings" 或类似列表
    # 允许不同键名，但要求有一个列表
    bookings_list = None
    for key in ["affected_bookings", "bookings", "affected", "items"]:
        if key in data and isinstance(data[key], list):
            bookings_list = data[key]
            break
    if bookings_list is None:
        add_item("JSON 结构", 0, 10, False, "未找到包含预订列表的键（expected 'affected_bookings' 或类似）")
        report["total_score"] = sum(d["score"] for d in report["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(report, f, indent=2)
        return
    else:
        add_item("JSON 结构包含预订列表", 10, 10, True, "找到列表键")

    # 3. 检查预订 ID 的正确性
    # 预期必须包含 HB-001 和 TB-001；不得包含 HB-003, TB-003 等
    found_ids = set()
    for entry in bookings_list:
        # 提取 booking_id
        bid = entry.get("booking_id") or entry.get("id") or entry.get("reservation_id")
        if bid:
            found_ids.add(bid)

    expected_ids = {"HB-001", "TB-001"}
    unwanted_ids = {"HB-003", "TB-003", "HB-002", "TB-002"}

    correct_ids_score = 0
    if expected_ids.issubset(found_ids):
        correct_ids_score = 30
        add_item("必须包含的预订 ID（HB-001、TB-001）", 30, 30, True, "已包含所有必需 ID")
    else:
        missing = expected_ids - found_ids
        add_item("必须包含的预订 ID", 0, 30, False, f"缺少 {missing}")

    extra = found_ids - expected_ids
    if extra:
        add_item("无多余预订 ID", 0, 10, False, f"包含不应出现的 ID: {extra}")
    else:
        add_item("无多余预订 ID", 10, 10, True, "没有多余预订")

    # 4. 检查新时间的正确性
    # 加载原始数据以获取 delay_minutes 和原时间
    flights_path = os.path.join(workspace, "data", "flights", "flights.json")
    if not os.path.isfile(flights_path):
        add_item("原始航班数据", 0, 30, False, "无法找到 data/flights/flights.json，跳过时间校验")
        report["total_score"] = sum(d["score"] for d in report["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(report, f, indent=2)
        return

    with open(flights_path) as f:
        flights_data = json.load(f)
    # 找 FL001
    flight = None
    for fl in flights_data.get("flights", []):
        if fl["flight_id"] == "FL001":
            flight = fl
            break
    if not flight:
        add_item("原始航班数据", 0, 30, False, "未找到 FL001 航班")
        report["total_score"] = sum(d["score"] for d in report["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(report, f, indent=2)
        return

    delay = flight["delay_minutes"]  # 120

    # 加载原始预订以获取原时间
    hotel_bookings_path = os.path.join(workspace, "data", "bookings", "hotel_bookings.json")
    transport_bookings_path = os.path.join(workspace, "data", "bookings", "transport_bookings.json")
    with open(hotel_bookings_path) as f:
        hb_data = json.load(f)
    with open(transport_bookings_path) as f:
        tb_data = json.load(f)

    original_times = {}
    for b in hb_data.get("hotel_bookings", []):
        original_times[b["booking_id"]] = b["check_in"]
    for b in tb_data.get("transport_bookings", []):
        original_times[b["booking_id"]] = b["pickup_time"]

    time_check_ok = True
    time_details = []
    for entry in bookings_list:
        bid = entry.get("booking_id") or entry.get("id") or entry.get("reservation_id")
        if bid not in ["HB-001", "TB-001"]:
            continue
        # 查找新时间字段：new_time, adjusted_time, new_check_in, new_pickup_time 等
        new_time_str = entry.get("new_time") or entry.get("adjusted_time") or \
                      entry.get("new_check_in") or entry.get("new_pickup_time") or \
                      entry.get("check_in") or entry.get("pickup_time")
        if not new_time_str:
            time_check_ok = False
            time_details.append(f"{bid}: 缺少新时间字段")
            continue

        orig_str = original_times.get(bid, "")
        if not orig_str:
            time_check_ok = False
            time_details.append(f"{bid}: 未找到原始时间")
            continue

        try:
            orig_dt = datetime.fromisoformat(orig_str)
            expected_dt = orig_dt + timedelta(minutes=delay)
            expected_str = expected_dt.isoformat()
        except:
            time_check_ok = False
            time_details.append(f"{bid}: 原始时间格式错误 {orig_str}")
            continue

        # 比较（精确到分钟）
        if new_time_str.endswith(":00"):
            # 去除秒
            new_time_clean = new_time_str[:-3] if new_time_str.endswith(":00") else new_time_str
        else:
            new_time_clean = new_time_str
        try:
            actual_dt = datetime.fromisoformat(new_time_clean)
        except:
            time_check_ok = False
            time_details.append(f"{bid}: 新时间格式错误 {new_time_str}")
            continue

        if actual_dt == expected_dt:
            time_details.append(f"{bid}: 正确 (新时间 {expected_str})")
        else:
            time_check_ok = False
            time_details.append(f"{bid}: 期望 {expected_str}，实际 {new_time_str}")

    if time_check_ok:
        add_item("新时间正确性（HB-001, TB-001）", 30, 30, True, "; ".join(time_details))
    else:
        add_item("新时间正确性", 0, 30, False, "; ".join(time_details))

    # 计算总分
    total = sum(d["score"] for d in report["details"])
    report["total_score"] = total
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
