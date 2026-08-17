import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 初始空目录，Agent需写入文件

    # 邮件数据
    emails = [
        {
            "id": "em_001",
            "thread_id": "th_001",
            "folder": "inbox",
            "sender_id": "tech",
            "subject": "System Update",
            "timestamp": "2025-04-01T10:00:00Z",
            "importance": "low",
            "labels": ["released"],
            "body": "The system update is complete.",
            "attachments": []
        },
        {
            "id": "em_002",
            "thread_id": "th_002",
            "folder": "inbox",
            "sender_id": "finance",
            "subject": "Reimbursement Request Q1",
            "timestamp": "2025-04-02T09:30:00Z",
            "importance": "high",
            "labels": ["approved", "urgent"],
            "body": "Please process the reimbursement for Q1.",
            "attachments": ["att_002"]
        },
        {
            "id": "em_003",
            "thread_id": "th_003",
            "folder": "inbox",
            "sender_id": "finance",
            "subject": "Draft Reimbursement",
            "timestamp": "2025-04-03T11:00:00Z",
            "importance": "medium",
            "labels": ["pending"],
            "body": "This is a draft, not approved yet.",
            "attachments": ["att_003"]
        },
        {
            "id": "em_004",
            "thread_id": "th_004",
            "folder": "inbox",
            "sender_id": "finance",
            "subject": "Reimbursement Request Q2",
            "timestamp": "2025-04-04T08:00:00Z",
            "importance": "high",
            "labels": ["approved"],
            "body": "Please process Q2 reimbursement.",
            "attachments": ["att_004"]
        },
        {
            "id": "em_005",
            "thread_id": "th_005",
            "folder": "inbox",
            "sender_id": "finance",
            "subject": "Travel Expenses March",
            "timestamp": "2025-04-05T14:00:00Z",
            "importance": "high",
            "labels": ["approved"],
            "body": "Travel expenses for March.",
            "attachments": ["att_005"]
        },
        {
            "id": "em_006",
            "thread_id": "th_006",
            "folder": "inbox",
            "sender_id": "marketing",
            "subject": "Campaign Budget",
            "timestamp": "2025-04-06T10:30:00Z",
            "importance": "high",
            "labels": ["approved"],
            "body": "Marketing campaign budget approval.",
            "attachments": ["att_006"]
        },
        {
            "id": "em_007",
            "thread_id": "th_007",
            "folder": "inbox",
            "sender_id": "finance",
            "subject": "Minor Reimbursement",
            "timestamp": "2025-04-07T16:00:00Z",
            "importance": "medium",
            "labels": ["approved"],
            "body": "Small reimbursement for office supplies.",
            "attachments": ["att_007"]
        }
    ]

    for email in emails:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f, indent=2)

    # 附件数据
    attachments = {
        "att_002": {
            "attachment_id": "att_002",
            "filename": "invoice_q1.pdf",
            "content_type": "application/pdf",
            "amount": 150.0,
            "currency": "USD",
            "approved": True
        },
        "att_003": {
            "attachment_id": "att_003",
            "filename": "draft_invoice.pdf",
            "content_type": "application/pdf",
            "amount": 80.0,
            "currency": "USD",
            "approved": True
        },
        "att_004": {
            "attachment_id": "att_004",
            "filename": "invoice_q2.pdf",
            "content_type": "application/pdf",
            "amount": 120.0,
            "currency": "USD",
            "approved": False
        },
        "att_005": {
            "attachment_id": "att_005",
            "filename": "travel_expenses_mar.pdf",
            "content_type": "application/pdf",
            "amount": 200.0,
            "currency": "USD",
            "approved": True
        },
        "att_006": {
            "attachment_id": "att_006",
            "filename": "campaign_budget.pdf",
            "content_type": "application/pdf",
            "amount": 250.0,
            "currency": "USD",
            "approved": True
        },
        "att_007": {
            "attachment_id": "att_007",
            "filename": "office_supplies.pdf",
            "content_type": "application/pdf",
            "amount": 0.0,
            "currency": "USD",
            "approved": True
        }
    }

    for att_id, att_data in attachments.items():
        with open(f"data/attachments/{att_id}.json", "w") as f:
            json.dump(att_data, f, indent=2)

if __name__ == "__main__":
    build_env()
