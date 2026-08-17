"""
Verify the agent's output for wp_flight_delay_envs__021.
Expected: ops/affected_bookings.json contains:
{
    "hotel_bookings": ["HB001", "HB002"],
    "transport_bookings": ["TB001"]
}
No extra keys allowed. Order must be ascending.
"""
import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 目录结构检查 (10)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({"item": "ops/ 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops directory found"})
        total_score += 10
    else:
        score_details.append({"item": "ops/ 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops directory not found"})
        # 如果目录不存在，后续检查无法进行，直接输出并退出
        write_score(total_score, score_details, workspace)
        return

    # 2. 文件存在 (10)
    target_file = os.path.join(ops_dir, "affected_bookings.json")
    if os.path.isfile(target_file):
        score_details.append({"item": "affected_bookings.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "file exists"})
        total_score += 10
    else:
        score_details.append({"item": "affected_bookings.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        write_score(total_score, score_details, workspace)
        return

    # 3. JSON 格式合法 (10)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {e}"})
        write_score(total_score, score_details, workspace)
        return

    # 4. 包含 hotel_bookings 字段 (5)
    if "hotel_bookings" in data:
        score_details.append({"item": "hotel_bookings 字段存在", "score": 5, "max_score": 5, "passed": True, "reason": "field present"})
        total_score += 5
    else:
        score_details.append({"item": "hotel_bookings 字段存在", "score": 0, "max_score": 5, "passed": False, "reason": "field missing"})

    # 5. hotel_bookings 列表长度正确 (15)
    hb = data.get("hotel_bookings", [])
    if len(hb) == 2:
        score_details.append({"item": "hotel_bookings 长度 = 2", "score": 15, "max_score": 15, "passed": True, "reason": "correct number of affected hotel bookings"})
        total_score += 15
    else:
        score_details.append({"item": "hotel_bookings 长度 = 2", "score": 0, "max_score": 15, "passed": False, "reason": f"expected 2, got {len(hb)}"})

    # 6. hotel_bookings 内容与排序正确 (15)
    expected_hb = ["HB001", "HB002"]
    if hb == expected_hb:
        score_details.append({"item": "hotel_bookings 内容与排序", "score": 15, "max_score": 15, "passed": True, "reason": "IDs match and sorted"})
        total_score += 15
    else:
        score_details.append({"item": "hotel_bookings 内容与排序", "score": 0, "max_score": 15, "passed": False, "reason": f"expected {expected_hb}, got {hb}"})

    # 7. 包含 transport_bookings 字段 (5)
    if "transport_bookings" in data:
        score_details.append({"item": "transport_bookings 字段存在", "score": 5, "max_score": 5, "passed": True, "reason": "field present"})
        total_score += 5
    else:
        score_details.append({"item": "transport_bookings 字段存在", "score": 0, "max_score": 5, "passed": False, "reason": "field missing"})

    # 8. transport_bookings 列表长度正确 (15)
    tb = data.get("transport_bookings", [])
    if len(tb) == 1:
        score_details.append({"item": "transport_bookings 长度 = 1", "score": 15, "max_score": 15, "passed": True, "reason": "correct number of affected transport bookings"})
        total_score += 15
    else:
        score_details.append({"item": "transport_bookings 长度 = 1", "score": 0, "max_score": 15, "passed": False, "reason": f"expected 1, got {len(tb)}"})

    # 9. transport_bookings 内容正确 (10)
    expected_tb = ["TB001"]
    if tb == expected_tb:
        score_details.append({"item": "transport_bookings 内容", "score": 10, "max_score": 10, "passed": True, "reason": "ID matches"})
        total_score += 10
    else:
        score_details.append({"item": "transport_bookings 内容", "score": 0, "max_score": 10, "passed": False, "reason": f"expected {expected_tb}, got {tb}"})

    # 10. 无多余字段 (5)
    allowed_keys = {"hotel_bookings", "transport_bookings"}
    extra_keys = set(data.keys()) - allowed_keys
    if not extra_keys:
        score_details.append({"item": "无多余字段", "score": 5, "max_score": 5, "passed": True, "reason": "exactly 2 fields"})
        total_score += 5
    else:
        score_details.append({"item": "无多余字段", "score": 0, "max_score": 5, "passed": False, "reason": f"extra keys: {extra_keys}"})

    # 写入结果
    write_score(total_score, score_details, workspace)

def write_score(total, details, workspace):
    output = {
        "total_score": min(total, 100),
        "details": details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {output['total_score']}/100")

if __name__ == "__main__":
    main()
