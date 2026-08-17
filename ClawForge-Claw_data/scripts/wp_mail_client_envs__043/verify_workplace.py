import json
import os
import sys
from pathlib import Path

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
ws = Path(workspace)

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def compute_expected():
    """从工作区数据中计算正确的结果"""
    contacts_path = ws / "data" / "contacts.json"
    contacts = load_json(contacts_path)
    # 构建 contact_id -> role 映射
    role_map = {}
    for c in contacts:
        role_map[c["contact_id"]] = c["role"]
    
    # 扫描所有邮件
    emails_dir = ws / "data" / "emails"
    high_priority_senders = set()
    for fname in os.listdir(emails_dir):
        if not fname.endswith(".json"):
            continue
        fpath = emails_dir / fname
        try:
            email = load_json(fpath)
        except:
            continue
        if email.get("importance") == "high":
            sender = email.get("sender_id")
            if sender:
                high_priority_senders.add(sender)
    
    # 保留 role 为 Client 或 Vendor 的
    allowed_roles = {"Client", "Vendor"}
    result = []
    for sid in high_priority_senders:
        role = role_map.get(sid)
        if role in allowed_roles:
            result.append(sid)
    result.sort()
    return result

def verify():
    details = []
    total_score = 0
    max_total = 100
    
    # 1. 目录结构检查 (10分)
    ops_dir = ws / "ops"
    target_file = ops_dir / "important_contacts.json"
    item = {"item": "ops 目录存在", "max_score": 5}
    if ops_dir.is_dir():
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "ops 目录存在"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops 目录不存在"
    details.append(item)
    total_score += item["score"]
    
    item = {"item": "important_contacts.json 存在", "max_score": 5}
    if target_file.is_file():
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "文件存在"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "文件不存在"
    details.append(item)
    total_score += item["score"]
    
    if not target_file.is_file():
        # 不再继续
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    
    # 2. 格式合法性 (10分)
    try:
        data = load_json(target_file)
        item = {"item": "JSON 格式合法", "max_score": 5}
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "可解析为 JSON"
    except:
        item = {"item": "JSON 格式合法", "max_score": 5}
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "JSON 解析失败"
    details.append(item)
    total_score += item["score"]
    
    item = {"item": "输出为列表", "max_score": 5}
    if isinstance(data, list):
        item["score"] = 5
        item["passed"] = True
        item["reason"] = "数据类型为 list"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"数据类型为 {type(data).__name__}，需为 list"
    details.append(item)
    total_score += item["score"]
    
    if not isinstance(data, list):
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
    
    # 3. 内容正确性 (80分)
    expected = compute_expected()
    expected_set = set(expected)
    actual_set = set(data)
    
    # 检查长度 (10分)
    item = {"item": "列表长度正确", "max_score": 10}
    if len(data) == len(expected):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"长度均为 {len(expected)}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"预期长度 {len(expected)}，实际长度 {len(data)}"
    details.append(item)
    total_score += item["score"]
    
    # 检查是否包含所有预期元素 (每个预期元素10分，最多20分)
    missing = expected_set - actual_set
    extra = actual_set - expected_set
    score_contain = 0
    for e in expected:
        if e in actual_set:
            score_contain += 10
    score_contain = min(score_contain, 20)  # 最多20分
    item = {"item": "包含所有预期元素", "max_score": 20}
    if not missing:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "包含全部预期 contact_id"
    else:
        item["score"] = score_contain
        item["passed"] = False
        item["reason"] = f"缺少: {sorted(missing)}"
    details.append(item)
    total_score += item["score"]
    
    # 检查没有多余元素 (10分)
    if not extra:
        extra_score = 10
    else:
        extra_score = 0
    item = {"item": "没有多余元素", "max_score": 10}
    if not extra:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "无多余元素"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"多余: {sorted(extra)}"
    details.append(item)
    total_score += item["score"]
    
    # 检查排序 (10分)
    if isinstance(data, list):
        sorted_correct = True
        for a, b in zip(data, data[1:]):
            if a > b:
                sorted_correct = False
                break
    else:
        sorted_correct = False
    item = {"item": "元素按字母序排序", "max_score": 10}
    if sorted_correct:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "已排序"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "未按字母序排序"
    details.append(item)
    total_score += item["score"]
    
    # 精确集合匹配额外奖励 (20分) —— 如果所有前面都正确，额外给20分；否则按缺失/多余扣减后给部分
    # 更简单的做法：如果 data 与 expected 完全一致（顺序和内容），给20分
    item = {"item": "精确匹配（内容与顺序）", "max_score": 20}
    if data == expected:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "完全匹配"
    else:
        # 部分匹配：如果内容相同但顺序不对，给10分；如果内容不同，0分
        if set(data) == set(expected) and len(data) == len(expected):
            item["score"] = 10
            item["passed"] = False
            item["reason"] = "内容相同但顺序错误"
        else:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = "内容不一致"
    details.append(item)
    total_score += item["score"]
    
    # 确保总分不超过100
    total_score = min(total_score, 100)
    
    with open(ws / "workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
