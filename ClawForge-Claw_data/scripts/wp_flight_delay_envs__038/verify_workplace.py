import os
import sys
import json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. 检查ops目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Directory ops/ found."
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Directory ops/ not found."
        })

    # 2. 检查impact_report.json存在且合法JSON (10分)
    report_path = os.path.join(workspace, "ops", "impact_report.json")
    if os.path.isfile(report_path):
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            details.append({
                "item": "impact_report.json exists and is valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "File found and JSON parsed successfully."
            })
            total_score += 10
        except (json.JSONDecodeError, IOError) as e:
            details.append({
                "item": "impact_report.json exists and is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"File is not valid JSON: {str(e)}"
            })
            # 无法继续检查字段，返回当前得分
            return {"total_score": total_score, "details": details}
    else:
        details.append({
            "item": "impact_report.json exists and is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File ops/impact_report.json not found."
        })
        return {"total_score": total_score, "details": details}

    # 3. 检查必需字段存在且类型正确 (20分)
    required_fields = {
        "flight_id": (str, "string"),
        "affected_hotel_bookings": (int, "integer"),
        "affected_transport_bookings": (int, "integer")
    }
    field_score = 0
    field_ok = True
    for field, (expected_type, type_name) in required_fields.items():
        if field not in data:
            details.append({
                "item": f"Required field '{field}' present",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Field '{field}' missing."
            })
            field_ok = False
        elif not isinstance(data[field], expected_type):
            details.append({
                "item": f"Required field '{field}' present",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Field '{field}' has wrong type: {type(data[field]).__name__}, expected {type_name}."
            })
            field_ok = False
        else:
            details.append({
                "item": f"Required field '{field}' present",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": f"Field '{field}' present and correct type."
            })
            field_score += 5

    total_score += field_score

    # 如果字段不全，后续不能根据值评分 (跳过大分项)
    if not field_ok:
        # 额外字段检查仍进行
        extra_keys = set(data.keys()) - {"flight_id", "affected_hotel_bookings", "affected_transport_bookings"}
        if extra_keys:
            details.append({
                "item": "No extra fields",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Extra fields found: {', '.join(sorted(extra_keys))}"
            })
        else:
            details.append({
                "item": "No extra fields",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "No extra fields."
            })
            total_score += 10
        return {"total_score": total_score, "details": details}

    # 4. 检查 flight_id 值 (10分)
    if data["flight_id"] == "UA123":
        details.append({
            "item": "flight_id value is 'UA123'",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Correct flight ID."
        })
        total_score += 10
    else:
        details.append({
            "item": "flight_id value is 'UA123'",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 'UA123', got '{data['flight_id']}'."
        })

    # 5. 检查 affected_hotel_bookings 值 (20分)
    if data["affected_hotel_bookings"] == 2:
        details.append({
            "item": "affected_hotel_bookings equals 2",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct count of affected hotel bookings."
        })
        total_score += 20
    else:
        details.append({
            "item": "affected_hotel_bookings equals 2",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected 2, got {data['affected_hotel_bookings']}."
        })

    # 6. 检查 affected_transport_bookings 值 (20分)
    if data["affected_transport_bookings"] == 2:
        details.append({
            "item": "affected_transport_bookings equals 2",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct count of affected transport bookings."
        })
        total_score += 20
    else:
        details.append({
            "item": "affected_transport_bookings equals 2",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected 2, got {data['affected_transport_bookings']}."
        })

    # 7. 检查没有额外字段 (10分)
    extra_keys = set(data.keys()) - {"flight_id", "affected_hotel_bookings", "affected_transport_bookings"}
    if extra_keys:
        details.append({
            "item": "No extra fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra fields found: {', '.join(sorted(extra_keys))}"
        })
    else:
        details.append({
            "item": "No extra fields",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "No extra fields."
        })
        total_score += 10

    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {result['total_score']}")
