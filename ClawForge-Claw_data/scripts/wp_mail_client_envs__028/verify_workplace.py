#!/usr/bin/env python3
"""Verify the agent output for wp_mail_client_envs__028."""
import sys
import json
import os
import re

def load_contacts(workspace):
    contacts_path = os.path.join(workspace, "data", "contacts.json")
    if not os.path.isfile(contacts_path):
        return None
    with open(contacts_path, "r") as f:
        data = json.load(f)
    return {c["contact_id"]: c for c in data.get("contacts", [])}

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # === 1. 检查目录结构 (10分) ===
    # 期望存在 data/contacts.json, data/accounts.json, data/emails/ 等（作为基础环境）
    # agent 必须创建 todo/task_list.json
    expected_dirs = ["data/emails", "data", "todo"]
    for d in expected_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            details.append({"item": f"目录 {d} 不存在", "score": 0, "max_score": 0, "passed": False, "reason": "缺失"})
        else:
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 0, "passed": True, "reason": ""})
    # 主要检查 todo/task_list.json 是否存在
    task_list_path = os.path.join(workspace, "todo", "task_list.json")
    if not os.path.isfile(task_list_path):
        details.append({"item": "todo/task_list.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
    else:
        details.append({"item": "todo/task_list.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total += 10

    if total < 10:
        # 无法继续，直接输出
        _write_score(workspace, total, details)
        return

    # === 2. 文件格式合法性 (10分) ===
    try:
        with open(task_list_path, "r") as f:
            tasks = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        details.append({"item": "JSON 解析合法", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        _write_score(workspace, total, details)
        return

    if not isinstance(tasks, list):
        details.append({"item": "JSON 顶层层数为数组", "score": 0, "max_score": 10, "passed": False, "reason": "不是数组"})
        _write_score(workspace, total, details)
        return
    details.append({"item": "JSON 解析合法且为数组", "score": 10, "max_score": 10, "passed": True, "reason": ""})
    total += 10

    # === 3. 每个元素字段完整性 (10分) ===
    field_ok = True
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            details.append({"item": f"元素 {i} 为字典", "score": 0, "max_score": 10, "passed": False, "reason": "不是字典"})
            field_ok = False
            break
        for key in ["sender_name", "subject", "due_date"]:
            if key not in task:
                details.append({"item": f"元素 {i} 缺失字段 {key}", "score": 0, "max_score": 10, "passed": False, "reason": ""})
                field_ok = False
                break
        if not field_ok:
            break
    if field_ok:
        details.append({"item": "所有元素包含必需字段", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total += 10
    else:
        details.append({"item": "所有元素包含必需字段", "score": 0, "max_score": 10, "passed": False, "reason": "缺失字段"})

    # === 4. 筛选逻辑 (30分) ===
    # 正确结果应有且仅有2条：e001 和 e002，按时间升序
    contacts = load_contacts(workspace)
    if contacts is None:
        details.append({"item": "筛选逻辑正确", "score": 0, "max_score": 30, "passed": False, "reason": "无法加载 contacts.json"})
        _write_score(workspace, total, details)
        return

    # 预期输出
    expected_sender = contacts["sarah"]["name"]  # "Sarah Developer"
    expected = [
        {"sender_name": expected_sender, "subject": "Project Phoenix update", "due_date": "2025-03-20"},
        {"sender_name": expected_sender, "subject": "Phoenix deployment checklist", "due_date": "2025-03-22"}
    ]

    # 检查数量
    if len(tasks) != 2:
        details.append({"item": "筛选结果数量为2", "score": 0, "max_score": 30, "passed": False, "reason": f"实际 {len(tasks)} 条"})
        total += 0
    else:
        # 检查每条字段值
        match = True
        for i, (t, e) in enumerate(zip(tasks, expected)):
            if t.get("sender_name") != e["sender_name"]:
                match = False
                break
            if t.get("subject") != e["subject"]:
                match = False
                break
            if t.get("due_date") != e["due_date"]:
                match = False
                break
        if match:
            details.append({"item": "筛选结果内容与排序正确", "score": 30, "max_score": 30, "passed": True, "reason": ""})
            total += 30
        else:
            details.append({"item": "筛选结果内容或排序错误", "score": 0, "max_score": 30, "passed": False, "reason": "字段值不匹配"})

    # === 5. 不存在多余字段 + 没有引入无关数据 (10分) ===
    allowed_keys = {"sender_name", "subject", "due_date"}
    extra = False
    for t in tasks:
        if set(t.keys()) - allowed_keys:
            extra = True
            break
    if extra:
        details.append({"item": "无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "存在未指定字段"})
    else:
        details.append({"item": "无多余字段", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total += 10

    # === 6. 关键字段值精确性（双重确认） (10分) ===
    # 再次精确匹配 due_date 格式
    date_ok = True
    for t in tasks:
        due = t.get("due_date", "")
        if due not in ["2025-03-20", "2025-03-22"]:
            date_ok = False
            break
    if date_ok:
        details.append({"item": "due_date 精确值正确", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total += 10
    else:
        details.append({"item": "due_date 精确值错误", "score": 0, "max_score": 10, "passed": False, "reason": "日期不匹配"})

    # === 7. 时间顺序 (10分) ===
    # 已根据 expected 顺序检查过，但独立考察排序
    # 提取 task 中的 subject 顺序
    if len(tasks) == 2:
        if tasks[0]["subject"] == "Project Phoenix update" and tasks[1]["subject"] == "Phoenix deployment checklist":
            details.append({"item": "按时间升序排列", "score": 10, "max_score": 10, "passed": True, "reason": ""})
            total += 10
        else:
            details.append({"item": "按时间升序排列", "score": 0, "max_score": 10, "passed": False, "reason": "顺序错误"})
    else:
        details.append({"item": "按时间升序排列（数量不对跳过）", "score": 0, "max_score": 10, "passed": False, "reason": "结果数量为0或1"})

    # === 8. 额外加分（无，满分100） ===
    # 确保总分不超过100
    total = min(total, 100)
    _write_score(workspace, total, details)

def _write_score(workspace, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/100")

if __name__ == "__main__":
    verify()
