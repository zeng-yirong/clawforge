import json
import os
import sys
import re

def verify(workspace):
    score = 0
    details = []
    max_total = 100

    # 1. 检查必要的目录结构 (10分)
    required_dirs = ["ops"]
    for d in required_dirs:
        full = os.path.join(workspace, d)
        if os.path.isdir(full):
            details.append({
                "item": f"Directory '{d}' exists",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": f"Found directory {d}"
            })
            score += 5
        else:
            details.append({
                "item": f"Directory '{d}' exists",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Missing directory {d}"
            })

    # 2. 检查 ops/delay_response.json 存在且合法 (10分)
    result_path = os.path.join(workspace, "ops", "delay_response.json")
    if not os.path.isfile(result_path):
        details.append({
            "item": "ops/delay_response.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 继续检查其他项时跳过已缺失的文件
        # 但为了后续检查，我们仍尝试加载空数据
    else:
        details.append({
            "item": "ops/delay_response.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found valid file"
        })
        score += 10

        # 3. 文件格式合法 (10分)
        try:
            with open(result_path, "r") as f:
                data = json.load(f)
            details.append({
                "item": "Valid JSON format",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "JSON parse succeeded"
            })
            score += 10
        except (json.JSONDecodeError, ValueError):
            data = None
            details.append({
                "item": "Valid JSON format",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "File is not valid JSON"
            })

        if data is not None:
            # 4. 包含必要字段 (10分) – 至少需要有 affected_flight, hotel_adjustments, transport_adjustments, notification_sent
            required_fields = ["affected_flight", "hotel_adjustments", "transport_adjustments", "notification_sent"]
            missing = [f for f in required_fields if f not in data]
            if not missing:
                details.append({
                    "item": "Contains all required fields",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": f"Fields present: {required_fields}"
                })
                score += 10
            else:
                details.append({
                    "item": "Contains all required fields",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"Missing fields: {missing}"
                })

            # 5. affected_flight 正确识别 UA123 (20分)
            if data.get("affected_flight") == "UA123":
                details.append({
                    "item": "Affected flight identified correctly",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": "UA123 is the delayed flight affecting the traveler"
                })
                score += 20
            else:
                details.append({
                    "item": "Affected flight identified correctly",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"Expected 'UA123', got '{data.get('affected_flight')}'"
                })

            # 6. hotel_adjustments 正确更新 John Smith 的预订 (20分)
            # 期望：将 HB001 的 check_in 改为 2025-06-16，保留其他不变
            hotel_adj = data.get("hotel_adjustments", [])
            if isinstance(hotel_adj, list) and len(hotel_adj) == 1:
                adj = hotel_adj[0]
                if (adj.get("booking_id") == "HB001" and
                    adj.get("new_check_in") == "2025-06-16" and
                    adj.get("new_check_out") == "2025-06-18"):
                    details.append({
                        "item": "Hotel adjustment correct for John Smith",
                        "score": 20,
                        "max_score": 20,
                        "passed": True,
                        "reason": "Booking HB001 check-in adjusted to 2025-06-16"
                    })
                    score += 20
                else:
                    details.append({
                        "item": "Hotel adjustment correct for John Smith",
                        "score": 0,
                        "max_score": 20,
                        "passed": False,
                        "reason": f"Expected HB001 with check_in 2025-06-16, got {adj}"
                    })
            else:
                details.append({
                    "item": "Hotel adjustment correct for John Smith",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"Expected 1 adjustment, got {len(hotel_adj) if isinstance(hotel_adj, list) else 'non-list'}"
                })

            # 7. transport_adjustments 正确重新安排 John Smith 的接机 (20分)
            # 期望：TB001 的 pickup_time 改为 2025-06-15T21:00:00-05:00（原19:00 + 2小时）
            trans_adj = data.get("transport_adjustments", [])
            if isinstance(trans_adj, list) and len(trans_adj) == 1:
                adj = trans_adj[0]
                if (adj.get("booking_id") == "TB001" and
                    ("2025-06-15T21:00:00-05:00" in str(adj.get("new_pickup_time")) or
                     adj.get("new_pickup_time") == "2025-06-15T21:00:00-05:00")):
                    details.append({
                        "item": "Transport adjustment correct for John Smith",
                        "score": 20,
                        "max_score": 20,
                        "passed": True,
                        "reason": "Booking TB001 pickup time adjusted to 21:00"
                    })
                    score += 20
                else:
                    details.append({
                        "item": "Transport adjustment correct for John Smith",
                        "score": 0,
                        "max_score": 20,
                        "passed": False,
                        "reason": f"Expected TB001 pickup 2025-06-15T21:00:00-05:00, got {adj}"
                    })
            else:
                details.append({
                    "item": "Transport adjustment correct for John Smith",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"Expected 1 adjustment, got {len(trans_adj) if isinstance(trans_adj, list) else 'non-list'}"
                })

            # 8. notification_sent 为 true (10分)
            if data.get("notification_sent") is True:
                details.append({
                    "item": "Notification sent flag set to true",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "Notification was marked as sent"
                })
                score += 10
            else:
                details.append({
                    "item": "Notification sent flag set to true",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"Expected true, got {data.get('notification_sent')}"
                })

    # 如果文件不存在，则无法进行后续检查，我们直接设定剩余项为0分
    if not os.path.isfile(result_path):
        # 补充缺失的条目以避免总分为0但无解释
        for item_text, max_s in [("Valid JSON format",10),("Contains all required fields",10),
                                 ("Affected flight identified correctly",20),("Hotel adjustment correct for John Smith",20),
                                 ("Transport adjustment correct for John Smith",20),("Notification sent flag set to true",10)]:
            details.append({
                "item": item_text,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "Result file missing, skip"
            })

    # 总分裁剪
    total_score = min(score, max_total)

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total_score}/{max_total}")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
