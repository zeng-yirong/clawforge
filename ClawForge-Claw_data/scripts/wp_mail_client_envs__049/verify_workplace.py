import json
import os
import sys
import re

def verify(workspace: str):
    details = []
    total_score = 0
    max_possible = 100

    # 1. 检查预期产物是否存在 (10分)
    target_path = os.path.join(workspace, "ops", "security_review.json")
    if os.path.isfile(target_path):
        details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/security_review.json 已创建"})
        total_score += 10
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 ops/security_review.json"})
        # 提前返回，因为后续无法检查
        write_score(details, total_score, workspace)
        return

    # 2. 检查 JSON 合法性 (10分)
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        write_score(details, total_score, workspace)
        return

    # 3. 检查数据类型为列表 (10分)
    if not isinstance(data, list):
        details.append({"item": "数据类型为列表", "score": 0, "max_score": 10, "passed": False, "reason": f"期望列表，实际得到 {type(data)}"})
        write_score(details, total_score, workspace)
        return
    details.append({"item": "数据类型为列表", "score": 10, "max_score": 10, "passed": True, "reason": "顶层是列表"})
    total_score += 10

    # 4. 检查每个元素字段完整性 (10分)
    required_fields = {"id", "subject", "sender_email"}
    field_ok = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            details.append({"item": f"元素 {i} 字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"元素 {i} 不是字典"})
            field_ok = False
            break
        missing = required_fields - set(item.keys())
        if missing:
            details.append({"item": f"元素 {i} 字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {missing}"})
            field_ok = False
            break
    if field_ok:
        details.append({"item": "所有元素字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "每个条目均包含 id, subject, sender_email"})
        total_score += 10

    # 5. 核心计算：对比预期结果 (60分)
    # 从工作区读取所有邮件和联系人，自动计算预期列表
    contacts_path = os.path.join(workspace, "data", "contacts.json")
    emails_dir = os.path.join(workspace, "data", "emails")
    if not os.path.isfile(contacts_path) or not os.path.isdir(emails_dir):
        details.append({"item": "核心计算环境", "score": 0, "max_score": 60, "passed": False, "reason": "缺少 data/contacts.json 或 data/emails/ 目录"})
        write_score(details, total_score, workspace)
        return

    with open(contacts_path, "r", encoding="utf-8") as f:
        contacts_data = json.load(f)
    contacts = contacts_data.get("contacts", {})

    expected = []
    # 遍历所有邮件文件
    for fname in os.listdir(emails_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(emails_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            mail = json.load(f)
        # 条件：
        # 1. 未读 has_read == False
        # 2. 文件夹不是 spam
        # 3. 发件人来自外部域（非 company.com）
        # 4. 主题包含“紧急”或“重要”
        if mail.get("has_read", True):
            continue
        if mail.get("folder") == "spam":
            continue
        sender_id = mail.get("sender_id")
        contact = contacts.get(sender_id)
        if not contact:
            continue
        email = contact.get("email", "")
        # 判断域名
        domain_match = re.search(r'@(.+)$', email)
        if not domain_match:
            continue
        domain = domain_match.group(1)
        if domain == "company.com":
            continue
        subject = mail.get("subject", "")
        if "紧急" not in subject and "重要" not in subject:
            continue
        expected.append({
            "id": mail["id"],
            "subject": subject,
            "sender_email": email
        })
    # 排序期望列表（按 id 稳定排序）
    expected_sorted = sorted(expected, key=lambda x: x["id"])
    # 对 agent 输出也排序（允许无序）
    agent_sorted = sorted(data, key=lambda x: x.get("id", ""))
    # 比较
    if len(agent_sorted) != len(expected_sorted):
        details.append({"item": "核心计算 – 条目数量", "score": 0, "max_score": 60, "passed": False,
                        "reason": f"期望 {len(expected_sorted)} 条，实际 {len(agent_sorted)} 条"})
        write_score(details, total_score, workspace)
        return
    # 逐条比较
    match = True
    for i, (exp, act) in enumerate(zip(expected_sorted, agent_sorted)):
        if exp["id"] != act.get("id") or exp["subject"] != act.get("subject") or exp["sender_email"] != act.get("sender_email"):
            match = False
            details.append({"item": "核心计算 – 条目内容匹配", "score": 0, "max_score": 60, "passed": False,
                            "reason": f"第 {i} 条不匹配: 期望 {exp}，实际 {act}"})
            break
    if match:
        details.append({"item": "核心计算 – 完全匹配", "score": 60, "max_score": 60, "passed": True,
                        "reason": f"共 {len(expected_sorted)} 条，全部正确"})
        total_score += 60
    else:
        # 如果已经添加了失败原因，则分数为0
        pass

    # 写入最终得分
    write_score(details, total_score, workspace)

def write_score(details, total_score, workspace):
    result = {
        "total_score": min(total_score, 100),
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
