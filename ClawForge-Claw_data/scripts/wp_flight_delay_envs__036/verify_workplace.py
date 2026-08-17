import json
import sys
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops/quick_fix.json 是否存在 (10分)
    ops_file = os.path.join(workspace, "ops", "quick_fix.json")
    if os.path.exists(ops_file):
        score_details.append({"item": "ops/quick_fix.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "ops/quick_fix.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        # 后续检查无法进行，直接输出
        write_score(workspace, total_score, score_details)
        return

    # 2. 解析 JSON 是否合法 (10分)
    try:
        with open(ops_file, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(workspace, total_score, score_details)
        return

    # 3. 数据必须是列表 (5分)
    if isinstance(data, list):
        score_details.append({"item": "顶层结构为列表", "score": 5, "max_score": 5, "passed": True, "reason": "是列表"})
        total_score += 5
    else:
        score_details.append({"item": "顶层结构为列表", "score": 0, "max_score": 5, "passed": False, "reason": f"实际类型: {type(data).__name__}"})
        # 继续尝试，若列表则宽松

    # 4. 列表长度应为2 (5分)
    expected_len = 2  # hb_001 and tb_001
    if len(data) == expected_len:
        score_details.append({"item": "列表长度正确", "score": 5, "max_score": 5, "passed": True, "reason": f"包含 {expected_len} 项"})
        total_score += 5
    else:
        score_details.append({"item": "列表长度正确", "score": 0, "max_score": 5, "passed": False, "reason": f"实际长度 {len(data)}, 期望 {expected_len}"})
        # 继续尝试检查部分内容

    # 5. 检查每个条目的结构 (每项 10分, 共20分)
    score_hb = 0
    score_tb = 0
    hb_found = False
    tb_found = False
    for entry in data:
        if not isinstance(entry, dict):
            continue
        booking_id = entry.get("booking_id", "")
        entry_type = entry.get("type", "")
        adjustments = entry.get("adjustments", {})
        if booking_id == "hb_001" and entry_type == "hotel":
            hb_found = True
            # 检查 adjustments 字段
            required_fields = ["new_check_in", "new_check_out"]
            if all(f in adjustments for f in required_fields):
                if adjustments["new_check_in"] == "2025-04-11" and adjustments["new_check_out"] == "2025-04-14":
                    score_hb = 10
                elif adjustments["new_check_in"] == "2025-04-11" or adjustments["new_check_out"] == "2025-04-14":
                    score_hb = 5  # 部分正确
                else:
                    score_hb = 2  # 值错误但字段存在
            else:
                score_hb = 3  # 缺少字段
        elif booking_id == "tb_001" and entry_type == "transport":
            tb_found = True
            if "new_pickup_datetime" in adjustments:
                if adjustments["new_pickup_datetime"] == "2025-04-10T12:00":
                    score_tb = 10
                else:
                    score_tb = 5  # 值错误
            else:
                score_tb = 3  # 缺少字段

    score_details.append({"item": "酒店预订 hb_001 调整正确", "score": score_hb, "max_score": 10, "passed": score_hb >= 10, "reason": f"得分 {score_hb}/10"})
    total_score += score_hb
    score_details.append({"item": "交通预订 tb_001 调整正确", "score": score_tb, "max_score": 10, "passed": score_tb >= 10, "reason": f"得分 {score_tb}/10"})
    total_score += score_tb

    # 6. 检查是否包含了不应出现的条目 (20分)
    # 不应包含 hb_003 (已取消) 或任何其他无关预订
    illegal_ids = {"hb_003", "hb_002", "tb_002"}
    found_illegal = [entry.get("booking_id") for entry in data if isinstance(entry, dict) and entry.get("booking_id") in illegal_ids]
    if not found_illegal:
        score_details.append({"item": "未包含无关预订", "score": 20, "max_score": 20, "passed": True, "reason": "没有无关预订"})
        total_score += 20
    else:
        score_details.append({"item": "未包含无关预订", "score": 0, "max_score": 20, "passed": False, "reason": f"包含了无关预订: {found_illegal}"})

    # 7. 检查键名规范性 (额外5分，不允许多余顶层字段？我们只检查必要的，多余不扣分，但这里作为可选加分？不，设为必检项：每个entry必须有booking_id, type, adjustments)
    all_entries_valid = True
    for entry in data:
        if not isinstance(entry, dict):
            all_entries_valid = False
            break
        if not all(k in entry for k in ("booking_id", "type", "adjustments")):
            all_entries_valid = False
            break
    if all_entries_valid:
        score_details.append({"item": "条目字段完整 (booking_id, type, adjustments)", "score": 5, "max_score": 5, "passed": True, "reason": "所有条目包含必要字段"})
        total_score += 5
    else:
        score_details.append({"item": "条目字段完整 (booking_id, type, adjustments)", "score": 0, "max_score": 5, "passed": False, "reason": "存在缺少字段的条目"})

    # 总分修正：确保不超过100
    total_score = min(total_score, 100)
    write_score(workspace, total_score, score_details)

def write_score(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {score_file}")

if __name__ == "__main__":
    main()
