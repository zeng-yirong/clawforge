import json
import os
import sys
from datetime import datetime, timedelta

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # --- 1. 文件是否存在 (10分) ---
    plan_path = os.path.join(workspace, "ops", "delay_plan.json")
    if os.path.isfile(plan_path):
        details.append({
            "item": "ops/delay_plan.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "目标文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/delay_plan.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 后续检查无意义，直接输出
        write_score(total_score, details, workspace)
        return

    # --- 2. JSON 格式合法 (10分) ---
    try:
        with open(plan_path, "r") as f:
            plan = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        write_score(total_score, details, workspace)
        return

    # --- 3. 字段结构正确 (20分) ---
    need_keys = ["affected_hotel_bookings", "affected_transport_bookings"]
    missing = [k for k in need_keys if k not in plan]
    if not missing:
        details.append({
            "item": "必填字段存在",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"包含 {need_keys}"
        })
        total_score += 20
    else:
        details.append({
            "item": "必填字段存在",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"缺少字段: {missing}"
        })
        write_score(total_score, details, workspace)
        return

    # --- 4. 数量与数值计算 (40分) ---
    # 从原始数据计算预期
    # 读取 flights
    flights_path = os.path.join(workspace, "data", "flights", "flights.json")
    flights_data = load_json(flights_path)
    delayed_flights = [f for f in flights_data["flights"] if f["status"] == "delayed"]
    if not delayed_flights:
        details.append({"item": "数值计算", "score": 0, "max_score": 40, "passed": False, "reason": "未找到延误航班"})
        write_score(total_score, details, workspace)
        return
    # 假设只有一个延误航班
    delayed = delayed_flights[0]
    delay_min = delayed["delay_minutes"]
    flight_id = delayed["flight_id"]

    # 读取 hotel_bookings
    hb_path = os.path.join(workspace, "data", "bookings", "hotel_bookings.json")
    hb_data = load_json(hb_path)
    active_hb = [b for b in hb_data["hotel_bookings"] if b["flight_id"] == flight_id and b["status"] == "active"]

    # 读取 transport_bookings
    tb_path = os.path.join(workspace, "data", "bookings", "transport_bookings.json")
    tb_data = load_json(tb_path)
    active_tb = [b for b in tb_data["transport_bookings"] if b["flight_id"] == flight_id and b["status"] == "active"]

    # 检查 agent 结果
    agent_hb = plan["affected_hotel_bookings"]
    agent_tb = plan["affected_transport_bookings"]

    # 数量检查
    correct_len = (len(agent_hb) == len(active_hb)) and (len(agent_tb) == len(active_tb))
    if not correct_len:
        details.append({
            "item": "数量匹配",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": f"预期 hotel:{len(active_hb)} transport:{len(active_tb)}，实际 hotel:{len(agent_hb)} transport:{len(agent_tb)}"
        })
        write_score(total_score, details, workspace)
        return

    # 逐一验证数值
    def parse_dt(s):
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

    def add_delay(orig_str, delay):
        dt = parse_dt(orig_str)
        new_dt = dt + timedelta(minutes=delay)
        return new_dt.strftime("%Y-%m-%dT%H:%M:%S")

    all_ok = True
    for b in active_hb:
        expected_new_checkin = add_delay(b["check_in"], delay_min)
        # 在 agent 列表中找对应 booking
        match = [a for a in agent_hb if a.get("booking_id") == b["booking_id"]]
        if not match:
            all_ok = False
            reason = f"缺少 hotel booking {b['booking_id']}"
            break
        a = match[0]
        if a.get("new_check_in") != expected_new_checkin:
            all_ok = False
            reason = f"hotel {b['booking_id']}: 预期 {expected_new_checkin}, 得到 {a.get('new_check_in')}"
            break
    if all_ok:
        for b in active_tb:
            expected_new_pickup = add_delay(b["pickup_time"], delay_min)
            match = [a for a in agent_tb if a.get("booking_id") == b["booking_id"]]
            if not match:
                all_ok = False
                reason = f"缺少 transport booking {b['booking_id']}"
                break
            a = match[0]
            if a.get("new_pickup_time") != expected_new_pickup:
                all_ok = False
                reason = f"transport {b['booking_id']}: 预期 {expected_new_pickup}, 得到 {a.get('new_pickup_time')}"
                break

    if all_ok:
        details.append({
            "item": "数值计算精确",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": "所有受影响的预订新时间正确"
        })
        total_score += 40
    else:
        details.append({
            "item": "数值计算精确",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": reason
        })
        write_score(total_score, details, workspace)
        return

    # --- 5. 无多余字段/节点 (20分) ---
    # 检查 agent 产物中每个条目是否只含必要字段
    allowed_hotel_keys = {"booking_id", "new_check_in", "reason"}
    allowed_transport_keys = {"booking_id", "new_pickup_time", "reason"}
    extra = False
    for a in plan["affected_hotel_bookings"]:
        if not set(a.keys()).issubset(allowed_hotel_keys):
            extra = True
            break
    if not extra:
        for a in plan["affected_transport_bookings"]:
            if not set(a.keys()).issubset(allowed_transport_keys):
                extra = True
                break
    if not extra:
        details.append({
            "item": "无多余字段",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "所有条目的字段均在允许范围内"
        })
        total_score += 20
    else:
        details.append({
            "item": "无多余字段",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "存在不允许的字段"
        })
        # 不提前返回，仍然写总分

    write_score(total_score, details, workspace)

def write_score(score, details, workspace):
    result = {
        "total_score": score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
