import sys
import os
import json
import csv
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    score_details = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (10 分)
    required_dirs = ["ops", "data/flights", "data/bookings"]
    dir_ok = all((ws / d).is_dir() for d in required_dirs)
    score_details.append({
        "item": "required directories exist (ops, data/flights, data/bookings)",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "all three directories found" if dir_ok else f"missing one or more of {required_dirs}"
    })
    if dir_ok:
        total_score += 10

    # 2. 目标文件 ops/impact_report.json 存在且合法 JSON (15 分)
    report_path = ws / "ops" / "impact_report.json"
    file_exists = report_path.is_file()
    json_valid = False
    data = None
    if file_exists:
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            json_valid = True
        except (json.JSONDecodeError, Exception):
            json_valid = False
    score_details.append({
        "item": "ops/impact_report.json exists and is valid JSON",
        "score": 15 if (file_exists and json_valid) else 0,
        "max_score": 15,
        "passed": file_exists and json_valid,
        "reason": "file present and parseable" if (file_exists and json_valid) else
                  ("file missing" if not file_exists else "invalid JSON")
    })
    if file_exists and json_valid:
        total_score += 15

    # 3. 字段结构检查：必须包含 flight_id, delay_minutes, affected_hotel_bookings, affected_transport_bookings (15 分)
    required_fields = ["flight_id", "delay_minutes", "affected_hotel_bookings", "affected_transport_bookings"]
    fields_ok = False
    if data and isinstance(data, dict):
        fields_ok = all(f in data for f in required_fields)
    score_details.append({
        "item": "report contains all four required fields (flight_id, delay_minutes, affected_hotel_bookings, affected_transport_bookings)",
        "score": 15 if fields_ok else 0,
        "max_score": 15,
        "passed": fields_ok,
        "reason": "all fields present" if fields_ok else f"missing fields: {[f for f in required_fields if f not in data]}"
    })
    if fields_ok:
        total_score += 15

    # 4. flight_id 正确值 (10 分)
    flight_value_ok = fields_ok and data["flight_id"] == "UA123"
    score_details.append({
        "item": "flight_id is 'UA123'",
        "score": 10 if flight_value_ok else 0,
        "max_score": 10,
        "passed": flight_value_ok,
        "reason": "correct" if flight_value_ok else f"got '{data.get('flight_id', 'N/A')}', expected 'UA123'"
    })
    if flight_value_ok:
        total_score += 10

    # 5. delay_minutes 正确值 (10 分)
    delay_ok = fields_ok and data["delay_minutes"] == 45
    score_details.append({
        "item": "delay_minutes is 45",
        "score": 10 if delay_ok else 0,
        "max_score": 10,
        "passed": delay_ok,
        "reason": "correct" if delay_ok else f"got {data.get('delay_minutes', 'N/A')}, expected 45"
    })
    if delay_ok:
        total_score += 10

    # 6. affected_hotel_bookings 正确值 (20 分)
    hotel_ok = fields_ok and data["affected_hotel_bookings"] == 2
    score_details.append({
        "item": "affected_hotel_bookings is 2 (only HB001 and HB002 linked to UA123)",
        "score": 20 if hotel_ok else 0,
        "max_score": 20,
        "passed": hotel_ok,
        "reason": "correct" if hotel_ok else f"got {data.get('affected_hotel_bookings', 'N/A')}, expected 2"
    })
    if hotel_ok:
        total_score += 20

    # 7. affected_transport_bookings 正确值 (20 分)
    transport_ok = fields_ok and data["affected_transport_bookings"] == 2
    score_details.append({
        "item": "affected_transport_bookings is 2 (TB001 and TB002 linked to UA123)",
        "score": 20 if transport_ok else 0,
        "max_score": 20,
        "passed": transport_ok,
        "reason": "correct" if transport_ok else f"got {data.get('affected_transport_bookings', 'N/A')}, expected 2"
    })
    if transport_ok:
        total_score += 20

    # 8. 额外字段扣分 (保险：不允许多余字段导致误判？不扣分，但我们可以检查没有额外字段)
    # 这里不需要扣分，但要求不检查无关字段。保留可选。

    # 写入结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete: total_score={total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
