import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # 确保目录存在
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 定义一个基准时间
    base_time = datetime(2025, 4, 1, 9, 0, 0)

    emails_data = []

    # 先定义所有邮件的生成参数 (id, has_read, importance, labels, body_lines, timestamp_offset_minutes)
    # body_lines 中每一条可能是TODO行或普通行，以 "TODO:" 开头表示待办
    mail_defs = [
        # 1. 符合条件的：未读，重要性normal，labels含action，无spam，包含两个TODO
        ("em001", False, "normal", ["action"], ["今日任务：", "TODO: 完成登录页UI设计", "TODO: 修复用户头像上传bug", "备注：还需测试"], 10),
        # 2. 符合条件的：未读，重要性high，labels含action和important
        ("em002", False, "high", ["action", "important"], ["紧急！", "TODO: 处理服务器证书过期", "TODO: 更新运维手册"], 30),
        # 3. 符合条件的：未读，重要性normal，labels含action，只有一个TODO
        ("em003", False, "normal", ["action"], ["TODO: 编写API文档", "其他无关内容"], 60),
        # 4. 干扰：已读，重要性normal，labels含action，有TODO，但已读
        ("em004", True, "normal", ["action"], ["TODO: 这个应该已读不处理"], 120),
        # 5. 干扰：未读，重要性low，labels含action，有TODO，但重要性低
        ("em005", False, "low", ["action"], ["TODO: 低优先级任务"], 180),
        # 6. 干扰：未读，重要性normal，labels不含action，有TODO（但没有action标签）
        ("em006", False, "normal", ["urgent"], ["TODO: 无标签任务"], 200),
        # 7. 干扰：未读，重要性normal，labels含action和spam，应排除
        ("em007", False, "normal", ["action", "spam"], ["TODO: 这是垃圾邮件里的任务"], 240),
        # 8. 干扰：未读，重要性normal，labels含action，但body里没有TODO，只有普通文本
        ("em008", False, "normal", ["action"], ["这只是个普通邮件，没有待办"], 300),
        # 9. 干扰：未读，重要性normal，labels含action，body里有类似todo:（小写）的行，但不应匹配
        ("em009", False, "normal", ["action"], ["todo: 小写不被识别", "这不是 TODO:"], 360),
        # 10. 干扰：未读，重要性normal，labels含action，body里有"TODO:"但前面有空格
        ("em010", False, "normal", ["action"], ["   TODO: 前面有空格，按规则也应匹配？但规则是行首以TODO:开头，空格不算，所以本行不应提取"], 400),
        # 11. 包含重复TODO内容（与em002的"TODO: 处理服务器证书过期"相同），但时间更晚，去重后应保留em002的
        ("em011", False, "normal", ["action"], ["TODO: 处理服务器证书过期（重复，应被去重）"], 500),
        # 12. 另一个有效TODO且与前面不同
        ("em012", False, "normal", ["action"], ["TODO: 制定Q2计划"], 600),
        # 13. 一个邮件中有多个TODO，其中一个与em001重复（"TODO: 完成登录页UI设计"）
        ("em013", False, "normal", ["action"], ["TODO: 完成登录页UI设计（重复）", "TODO: 新增测试用例"], 700),
        # 14. 有效但时间最早的一个TODO（单独出现）
        ("em014", False, "normal", ["action"], ["TODO: 初始化项目仓库"], 0),
    ]

    for mail_id, has_read, importance, labels, body_lines, offset_min in mail_defs:
        ts = (base_time + timedelta(minutes=offset_min)).isoformat() + "Z"
        body = "\n".join(body_lines)
        email = {
            "id": mail_id,
            "thread_id": "thread_" + mail_id,
            "folder": "inbox",
            "sender_id": "someone@company.com",
            "subject": f"Subject of {mail_id}",
            "timestamp": ts,
            "importance": importance,
            "labels": labels,
            "has_read": has_read,
            "body": body,
            "attachments": [],
            "auto_classify_suggestion": "work"
        }
        # 写入文件
        with open(f"data/emails/{mail_id}.json", "w") as f:
            json.dump(email, f, indent=2)
        emails_data.append(email)

    # 额外增加一些干扰文件（比如空文件、其他格式），但非必须
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

if __name__ == "__main__":
    build_env()
