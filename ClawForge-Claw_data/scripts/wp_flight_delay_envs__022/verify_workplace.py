"""
verify_workplace.py — 纯代码验证 agent 产物
读取 ops/disruption_report.json 并根据预定义真相逐项评分
"""
import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score_details = []
total_score = 0

def add_item(name, score, max_score, passed, reason):
    score_details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    global total_score
    total_score += score

# 1. 检查 ops 目录是否存在 (10分)
ops_path = os.path.join(workspace, "ops")
if not os.path.isdir(ops_path):
    add_item("ops 目录存在", 0, 10, False, "ops 目录不存在")
    # 如果目录不存在，后续检查全部失败，直接输出
    result = {"total_score": 0, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)
else:
    add_item("ops 目录存在", 10, 10, True, "ops 目录已创建")

# 2. 检查 disruption_report.json 存在 (15分)
report_path = os.path.join(workspace, "ops", "disruption_report.json")
if not os.path.isfile(report_path):
    add_item("disruption_report.json 存在", 0, 15, False, "文件不存在")
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)
else:
    add_item("disruption_report.json 存在", 15, 15, True, "文件存在")

# 3. JSON 格式合法性 (10分)
try:
    with open(report_path, "r") as f:
        data = json.load(f)
    add_item("JSON 格式合法", 10, 10, True, "解析成功")
except Exception as e:
    add_item("JSON 格式合法", 0, 10, False, f"解析失败: {e}")
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 4. 包含 required 顶级键 (10分)
required_keys = ["affected_hotels", "affected_transports", "affected_contacts"]
present_keys = [k for k in required_keys if k in data]
if set(required_keys) == set(present_keys):
    add_item("包含 required 键", 10, 10, True, "所有必要键存在")
else:
    missing = [k for k in required_keys if k not in data]
    add_item("包含 required 键", 0, 10, False, f"缺少键: {missing}")
    # 仍可继续检查，但跳过后续依赖项的部分分数

# 5. 检查 affected_hotels 正确性 (20分)
hotels_score = 0
hotels_max = 20
hotels_reason = ""
try:
    hotels = data.get("affected_hotels", [])
    if not isinstance(hotels, list):
        hotels_reason = "affected_hotels 不是列表"
        hotels_score = 0
    else:
        # 预期只有一条记录：BKH01, HTL01, jane.doe@example.com
        expected = [{"booking_id": "BKH01", "hotel_id": "HTL01", "guest_email": "jane.doe@example.com"}]
        # 允许顺序不同，且允许有额外字段，但必须包含这些字段且值正确
        actual = []
        for h in hotels:
            if isinstance(h, dict) and "booking_id" in h and "hotel_id" in h and "guest_email" in h:
                actual.append({"booking_id": h["booking_id"], "hotel_id": h["hotel_id"], "guest_email": h["guest_email"]})
        if actual == expected:
            hotels_score = 20
            hotels_reason = "准确包含唯一受影响的酒店预订 (BKH01 / HTL01 / jane.doe@example.com)"
        elif len(actual) == 0:
            hotels_reason = "列表为空"
        else:
            hotels_reason = f"内容不匹配: 期望 {expected}, 实际 {actual}"
except Exception as e:
    hotels_reason = f"检查异常: {e}"
add_item("affected_hotels 正确", hotels_score, hotels_max, hotels_score == hotels_max, hotels_reason)

# 6. 检查 affected_transports 正确性 (20分)
trans_score = 0
trans_max = 20
trans_reason = ""
try:
    transports = data.get("affected_transports", [])
    if not isinstance(transports, list):
        trans_reason = "affected_transports 不是列表"
    else:
        expected = [{"booking_id": "BKT01", "transport_id": "TR001", "guest_email": "jane.doe@example.com"}]
        actual = []
        for t in transports:
            if isinstance(t, dict) and "booking_id" in t and "transport_id" in t and "guest_email" in t:
                actual.append({"booking_id": t["booking_id"], "transport_id": t["transport_id"], "guest_email": t["guest_email"]})
        if actual == expected:
            trans_score = 20
            trans_reason = "准确包含唯一受影响的交通预订 (BKT01 / TR001 / jane.doe@example.com)"
        elif len(actual) == 0:
            trans_reason = "列表为空"
        else:
            trans_reason = f"内容不匹配: 期望 {expected}, 实际 {actual}"
except Exception as e:
    trans_reason = f"检查异常: {e}"
add_item("affected_transports 正确", trans_score, trans_max, trans_score == trans_max, trans_reason)

# 7. 检查 affected_contacts 正确性 (15分)
cont_score = 0
cont_max = 15
cont_reason = ""
try:
    contacts = data.get("affected_contacts", [])
    if not isinstance(contacts, list):
        cont_reason = "affected_contacts 不是列表"
    else:
        # 预期只有一个邮箱：jane.doe@example.com
        expected = ["jane.doe@example.com"]
        # 应全部为字符串
        actual = [c for c in contacts if isinstance(c, str)]
        if actual == expected:
            cont_score = 15
            cont_reason = "准确包含唯一受影响的联系人邮箱"
        elif len(actual) == 0:
            cont_reason = "列表为空"
        else:
            cont_reason = f"内容不匹配: 期望 {expected}, 实际 {actual}"
except Exception as e:
    cont_reason = f"检查异常: {e}"
add_item("affected_contacts 正确", cont_score, cont_max, cont_score == cont_max, cont_reason)

# 汇总
final_score = min(total_score, 100)  # 防止溢出
result = {"total_score": final_score, "details": score_details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
