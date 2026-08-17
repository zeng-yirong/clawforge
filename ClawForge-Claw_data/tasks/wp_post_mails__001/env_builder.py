import os
import json
import shutil

def build_env():
    # 创建目录结构
    os.makedirs("emails", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    if os.path.exists("launch"):
        shutil.rmtree("launch")
    os.makedirs("launch", exist_ok=True)

    # ===== 邮件 =====

    # 1) 旧草稿 v1（未批准）
    email_v1 = {
        "id": "em_001",
        "thread_id": "th_orbital",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Draft: Orbital Aurora Brief v1",
        "timestamp": "2025-06-10T08:00:00Z",
        "importance": "low",
        "labels": ["draft"],
        "body": "Please review the initial brief.",
        "attachments": ["brief_v1.md"]
    }
    with open("emails/em_001.json", "w") as f:
        json.dump(email_v1, f)

    # 2) 预算邮件（干扰）
    email_budget = {
        "id": "em_002",
        "thread_id": "th_budget",
        "folder": "inbox",
        "sender_id": "priya.dev@auroralabs.com",
        "subject": "Budget for Q3",
        "timestamp": "2025-06-15T10:30:00Z",
        "importance": "high",
        "labels": ["finance"],
        "body": "Attaching the budget spreadsheet.",
        "attachments": ["budget.xlsx"]
    }
    with open("emails/em_002.json", "w") as f:
        json.dump(email_budget, f)

    # 3) 最终批准邮件（唯一正确来源）
    email_approved = {
        "id": "em_003",
        "thread_id": "th_orbital",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Approved: Orbital Aurora Brief v3",
        "timestamp": "2025-07-01T14:00:00Z",
        "importance": "high",
        "labels": ["approved", "final"],
        "body": "The final brief has been approved by legal and marketing.",
        "attachments": ["brief_v3.md"]
    }
    with open("emails/em_003.json", "w") as f:
        json.dump(email_approved, f)

    # 4) 另一个项目邮件（干扰）
    email_mars = {
        "id": "em_004",
        "thread_id": "th_mars",
        "folder": "inbox",
        "sender_id": "owen.park@auroralabs.com",
        "subject": "Mars Mission Update",
        "timestamp": "2025-06-20T09:00:00Z",
        "importance": "medium",
        "labels": ["mars"],
        "body": "Mars mission timeline.",
        "attachments": []
    }
    with open("emails/em_004.json", "w") as f:
        json.dump(email_mars, f)

    # ===== 附件 =====

    # brief_v1.md 旧版（未批准）
    with open("attachments/brief_v1.md", "w") as f:
        f.write("""# Mission Brief v1
Mission: Orbital Aurora
Launch Date: 2025-07-15
Approved By: (not yet)
Status: Draft
""")

    # brief_v2.md 旧版（待审）
    with open("attachments/brief_v2.md", "w") as f:
        f.write("""# Mission Brief v2
Mission: Orbital Aurora
Launch Date: 2025-07-18
Approved By: (pending)
Status: Under Review
""")

    # brief_v3.md 最终批准版本（唯一正确答案来源）
    with open("attachments/brief_v3.md", "w") as f:
        f.write("""# Mission Brief v3 - FINAL
Mission: Orbital Aurora
Launch Date: 2025-07-20
Approved By: Mira Chen
Status: Approved
""")

    # 干扰附件：预算文件
    with open("attachments/budget.xlsx", "w") as f:
        f.write("This is a binary placeholder for budget spreadsheet.\n")

    # 干扰附件：会议记录
    with open("attachments/meeting_notes.txt", "w") as f:
        f.write("Meeting notes from June.\n")

    print("Environment built successfully.")
