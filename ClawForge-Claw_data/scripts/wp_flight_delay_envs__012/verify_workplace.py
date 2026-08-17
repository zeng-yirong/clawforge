import os
import sys
import json

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "目录存在" if dir_exists else "ops 目录缺失"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 affected_bookings.json 是否存在 (10分)
    target_file = os.path.join(ops_path, "affected_bookings.json")
    file_exists = os.path.isfile(target_file)
    details.append({
        "item": "affected_bookings.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件缺失"
    })
    if file_exists:
        total_score += 10
    else:
        # 后续检查无法进行，直接返回
        _write_score(total_score, details, workspace)
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        json_ok = True
        reason = "JSON 格式合法"
    except Exception as e:
        json_ok = False
        reason = f"JSON 解析失败: {str(e)}"
    details.append({
        "item": "JSON 格式合法",
        "score": 10 if json_ok else 0,
        "max_score": 10,
        "passed": json_ok,
        "reason": reason
    })
    if json_ok:
        total_score += 10
    else:
        _write_score(total_score, details, workspace)
        return

    # 4. 检查数据是否为列表 (10分)
    is_list = isinstance(data, list)
    details.append({
        "item": "顶层结构为列表",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "顶层是列表" if is_list else "顶层不是列表"
    })
    if is_list:
        total_score += 10
    else:
        _write_score(total_score, details, workspace)
        return

    # 5. 检查列表长度 = 2 (20分)，惩罚长度不对
    length_ok = len(data) == 2
    details.append({
        "item": "列表长度应为 2（酒店 + 交通各一个）",
        "score": 20 if length_ok else 0,
        "max_score": 20,
        "passed": length_ok,
        "reason": f"长度 {len(data)}" if length_ok else f"实际长度 {len(data)}，预期 2"
    })
    if length_ok:
        total_score += 20
    else:
        _write_score(total_score, details, workspace)
        return

    # 6. 检查每个条目必需字段 (每个15分，共30分)
    required_fields = ["booking_id", "reason"]
    field_scores = 0
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            continue
        if all(f in entry for f in required_fields):
            field_scores += 15
        else:
            missing = [f for f in required_fields if f not in entry]
            details[-1]["reason"] += f" | 第{i+1}条缺失字段: {missing}"
    details.append({
        "item": "每个条目包含 booking_id 和 reason",
        "score": field_scores,
        "max_score": 30,
        "passed": field_scores == 30,
        "reason": "所有条目字段完整" if field_scores == 30 else f"仅得 {field_scores} 分"
    })
    if field_scores == 30:
        total_score += 30
    else:
        _write_score(total_score, details, workspace)
        return

    # 7. 验证具体的 booking_id 和 reason 内容 (20分)
    expected_bookings = {"HB-001", "TB-001"}
    actual_ids = {entry.get("booking_id") for entry in data}
    id_match = actual_ids == expected_bookings
    details.append({
        "item": "booking_id 正确 (HB-001, TB-001)",
        "score": 10 if id_match else 0,
        "max_score": 10,
        "passed": id_match,
        "reason": f"实际IDs: {actual_ids}" if id_match else f"预期 {{'HB-001','TB-001'}}，实际 {actual_ids}"
    })
    if id_match:
        total_score += 10

    # 检查 reason 是否包含延误相关关键词 (如 "delay") (10分)
    reasons_ok = True
    for entry in data:
        reason_text = entry.get("reason", "")
        if "delay" not in reason_text.lower():
            reasons_ok = False
            break
    details.append({
        "item": "每条 reason 包含延误相关说明",
        "score": 10 if reasons_ok else 0,
        "max_score": 10,
        "passed": reasons_ok,
        "reason": "所有 reason 合理" if reasons_ok else "部分 reason 不合理"
    })
    if reasons_ok:
        total_score += 10

    _write_score(total_score, details, workspace)


def _write_score(total, details, workspace):
    score_file = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total,
        "details": details
    }
    with open(score_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
