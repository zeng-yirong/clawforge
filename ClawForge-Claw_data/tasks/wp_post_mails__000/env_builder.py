import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("drafts", exist_ok=True)
    os.makedirs("data/social", exist_ok=True)

    # 目标邮件（最新 approved）
    email_target = {
        "id": "em_005",
        "thread_id": "tr_nova_launch",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "FINAL APPROVED: Nova II Launch Brief",
        "timestamp": "2025-10-15T09:00:00Z",
        "importance": "high",
        "labels": ["approved", "launch", "final"],
        "body": "Here is the final approved brief. Use this for the launch post.",
        "attachments": [{"attachment_id": "att_approval_v3", "filename": "approved_brief.json"}]
    }
    # 干扰邮件1：旧版本（v2 draft）
    email_old = {
        "id": "em_002",
        "thread_id": "tr_nova_launch",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Draft: Nova II Launch Brief v2",
        "timestamp": "2025-10-10T14:00:00Z",
        "importance": "medium",
        "labels": ["draft", "launch"],
        "body": "This is an earlier draft, not approved.",
        "attachments": [{"attachment_id": "att_approval_v2", "filename": "draft_brief_v2.json"}]
    }
    # 干扰邮件2：未批准讨论
    email_unapproved = {
        "id": "em_003",
        "thread_id": "tr_nova_launch",
        "folder": "inbox",
        "sender_id": "owen.park@auroralabs.com",
        "subject": "Re: Nova II launch ideas",
        "timestamp": "2025-10-13T08:30:00Z",
        "importance": "low",
        "labels": ["discussion", "launch"],
        "body": "Some ideas for the launch, not official.",
        "attachments": []
    }
    # 干扰邮件3：完全无关主题
    email_other = {
        "id": "em_001",
        "thread_id": "tr_infra",
        "folder": "inbox",
        "sender_id": "nina.santos@auroralabs.com",
        "subject": "Server maintenance schedule",
        "timestamp": "2025-10-14T11:00:00Z",
        "importance": "medium",
        "labels": ["ops", "infra"],
        "body": "Please review the maintenance plan.",
        "attachments": []
    }
    # 干扰邮件4：有附件但非 brief
    email_other_att = {
        "id": "em_004",
        "thread_id": "tr_nova_launch",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Nova II Design Assets",
        "timestamp": "2025-10-12T16:00:00Z",
        "importance": "medium",
        "labels": ["design", "assets"],
        "body": "Here are the design files for the launch.",
        "attachments": [{"attachment_id": "att_design", "filename": "design_assets.zip"}]
    }

    # 写入所有邮件文件
    emails = [email_target, email_old, email_unapproved, email_other, email_other_att]
    for em in emails:
        with open(f"data/emails/{em['id']}.json", "w") as f:
            json.dump(em, f, indent=2)

    # 创建目标附件（approved brief）
    with open("data/attachments/approved_brief.json", "w") as f:
        json.dump({
            "launch_date": "2025-10-20",
            "product_name": "Nova II",
            "tagline": "Redefining the horizon",
            "platforms": ["x", "reddit"],
            "target_audience": "tech enthusiasts"
        }, f, indent=2)

    # 创建旧版附件干扰
    with open("data/attachments/draft_brief_v2.json", "w") as f:
        json.dump({
            "launch_date": "2025-10-15",
            "product_name": "Nova II",
            "tagline": "Next-gen computing",
            "platforms": ["x", "reddit", "linkedin"],
            "target_audience": "developers"
        }, f, indent=2)

    # 创建非 JSON 附件干扰
    with open("data/attachments/design_assets.zip", "w") as f:
        f.write("binary content placeholder")

if __name__ == "__main__":
    build_env()
