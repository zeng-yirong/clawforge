import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # ---------- 1. 目录结构 ----------
    max_dir = 10
    score_dir = 0
    reason_dir = ""
    raw_data_exists = os.path.isdir(os.path.join(workspace, "raw_data"))
    ops_exists = os.path.isdir(os.path.join(workspace, "ops"))
    if raw_data_exists and ops_exists:
        score_dir = 10
        reason_dir = "raw_data/ and ops/ directories exist"
    else:
        missing = []
        if not raw_data_exists: missing.append("raw_data/")
        if not ops_exists: missing.append("ops/")
        reason_dir = f"Missing directories: {', '.join(missing)}"
    details.append({"item": "目录结构", "score": score_dir, "max_score": max_dir, "passed": score_dir == max_dir, "reason": reason_dir})
    total_score += score_dir

    # ---------- 2. ops/response.json 存在且合法 JSON ----------
    max_json = 10
    score_json = 0
    reason_json = ""
    response_path = os.path.join(workspace, "ops", "response.json")
    if not os.path.isfile(response_path):
        reason_json = "ops/response.json not found"
    else:
        try:
            with open(response_path, 'r') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                reason_json = "response.json is not a JSON object"
            else:
                score_json = 10
                reason_json = "ops/response.json exists and is valid JSON"
        except (json.JSONDecodeError, Exception) as e:
            reason_json = f"Invalid JSON: {str(e)}"
    details.append({"item": "JSON合法性", "score": score_json, "max_score": max_json, "passed": score_json == max_json, "reason": reason_json})
    total_score += score_json

    # 后续检查依赖 data 有效
    data = None
    if score_json == 10:
        with open(response_path, 'r') as f:
            data = json.load(f)

    # ---------- 3. flight_id 正确 ----------
    max_fid = 15
    score_fid = 0
    reason_fid = "field 'flight_id' "
    if data is None:
        reason_fid += "not checkable (JSON invalid)"
    elif "flight_id" not in data:
        reason_fid += "missing"
    elif data["flight_id"] == "FL001":
        score_fid = 15
        reason_fid += "correct (FL001)"
    else:
        reason_fid += f"wrong: got '{data['flight_id']}', expected 'FL001'"
    details.append({"item": "flight_id", "score": score_fid, "max_score": max_fid, "passed": score_fid == max_fid, "reason": reason_fid})
    total_score += score_fid

    # ---------- 4. new_departure_time 正确 ----------
    max_ndt = 20
    score_ndt = 0
    reason_ndt = "field 'new_departure_time' "
    if data is None:
        reason_ndt += "not checkable"
    elif "new_departure_time" not in data:
        reason_ndt += "missing"
    elif data["new_departure_time"] == "2025-03-01T20:30:00":
        score_ndt = 20
        reason_ndt += "correct (2025-03-01T20:30:00)"
    else:
        reason_ndt += f"wrong: got '{data['new_departure_time']}', expected '2025-03-01T20:30:00'"
    details.append({"item": "new_departure_time", "score": score_ndt, "max_score": max_ndt, "passed": score_ndt == max_ndt, "reason": reason_ndt})
    total_score += score_ndt

    # ---------- 5. affected_hotel_booking_ids 正确（无序集合）----------
    max_hids = 20
    score_hids = 0
    reason_hids = "field 'affected_hotel_booking_ids' "
    if data is None:
        reason_hids += "not checkable"
    elif "affected_hotel_booking_ids" not in data:
        reason_hids += "missing"
    else:
        got = data["affected_hotel_booking_ids"]
        if not isinstance(got, list):
            reason_hids += "not a list"
        else:
            expected = ["HB001", "HB002"]
            got_set = set(got)
            expected_set = set(expected)
            if got_set == expected_set:
                score_hids = 20
                reason_hids += f"correct: {sorted(got)}"
            else:
                reason_hids += f"expected any order of {expected}, got {got}"
    details.append({"item": "affected_hotel_booking_ids", "score": score_hids, "max_score": max_hids, "passed": score_hids == max_hids, "reason": reason_hids})
    total_score += score_hids

    # ---------- 6. affected_transport_booking_ids 正确 ----------
    max_tids = 15
    score_tids = 0
    reason_tids = "field 'affected_transport_booking_ids' "
    if data is None:
        reason_tids += "not checkable"
    elif "affected_transport_booking_ids" not in data:
        reason_tids += "missing"
    else:
        got = data["affected_transport_booking_ids"]
        if not isinstance(got, list):
            reason_tids += "not a list"
        else:
            expected = ["TB001"]
            got_set = set(got)
            if got_set == set(expected):
                score_tids = 15
                reason_tids += f"correct: {got}"
            else:
                reason_tids += f"expected {expected}, got {got}"
    details.append({"item": "affected_transport_booking_ids", "score": score_tids, "max_score": max_tids, "passed": score_tids == max_tids, "reason": reason_tids})
    total_score += score_tids

    # ---------- 7. notification_contact_ids 正确 ----------
    max_cids = 10
    score_cids = 0
    reason_cids = "field 'notification_contact_ids' "
    if data is None:
        reason_cids += "not checkable"
    elif "notification_contact_ids" not in data:
        reason_cids += "missing"
    else:
        got = data["notification_contact_ids"]
        if not isinstance(got, list):
            reason_cids += "not a list"
        else:
            expected = ["C001", "C002"]
            got_set = set(got)
            expected_set = set(expected)
            if got_set == expected_set:
                score_cids = 10
                reason_cids += f"correct: {sorted(got)}"
            else:
                reason_cids += f"expected any order of {expected}, got {got}"
    details.append({"item": "notification_contact_ids", "score": score_cids, "max_score": max_cids, "passed": score_cids == max_cids, "reason": reason_cids})
    total_score += score_cids

    # ---------- 写入总分 ----------
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total_score}/100")

if __name__ == '__main__':
    main()
