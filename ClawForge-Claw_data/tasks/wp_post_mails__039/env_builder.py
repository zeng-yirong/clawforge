import os
import json
from datetime import datetime, timedelta

def build_env():
    # 创建目录
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ----- 附件 -----
    # 被批准的最终版（正确答案依据）
    approved_content = """# Orbital Launch Brief v4
**Product:** SkyLink Pro
**Launch Date:** 2025-08-15
**Headline:** Reach Beyond the Stars
**Body:** SkyLink Pro connects remote teams with zero latency. Available now.
**CTA:** Pre-order at skylinkpro.io
"""
    with open("data/attachments/att_orbital_brief_v4.md", "w") as f:
        f.write(approved_content)

    # 干扰附件1 – 旧版草案
    draft_v2_content = """# Orbital Launch Brief v2
**Product:** SkyLink Pro
**Launch Date:** 2025-08-15
**Headline:** Connect the Unconnected
**Body:** Our new satellite network brings low-latency links to the most remote places.
**CTA:** Sign up for early access at skylinkpro.io
"""
    with open("data/attachments/att_skylink_draft_v2.md", "w") as f:
        f.write(draft_v2_content)

    # 干扰附件2 – 另一产品（诱饵）
    old_brief_content = """# Lunar Gateway Brief v1
**Product:** LunaNet
**Launch Date:** 2026-01-20
**Headline:** The Moon is Closer Than Ever
**Body:** LunaNet provides high-speed connectivity for lunar missions.
**CTA:** Contact sales at lunanet.space
"""
    with open("data/attachments/att_luna_old_brief.md", "w") as f:
        f.write(old_brief_content)

    # 干扰附件3 – 没有批准标记的版本
    other_draft = """# Orbital Launch Brief v3
**Product:** SkyLink Pro
**Launch Date:** 2025-08-15
**Headline:** Reach Beyond the Horizon
**Body:** SkyLink Pro brings reliable connectivity to field teams worldwide.
**CTA:** Learn more at skylinkpro.io
"""
    with open("data/attachments/att_skylink_draft_v3.md", "w") as f:
        f.write(other_draft)

    # ----- 邮件 -----
    base_time = datetime(2025, 7, 20, 12, 0, 0)

    # 正确邮件（最新批准）
    correct_email = {
        "id": "em_001",
        "thread_id": "th_orbital_launch",
        "folder": "inbox",
        "sender_id": "nina.santos@auroralabs.com",
        "subject": "FINAL APPROVED: Orbital Launch Brief v4",
        "timestamp": (base_time + timedelta(hours=3)).isoformat() + "Z",
        "importance": "high",
        "labels": ["approved", "launch", "marketing"],
        "body": "Please use the attached brief for the official launch announcement.",
        "attachments": [
            {
                "attachment_id": "att_orbital_brief_v4",
                "filename": "approved_brief_v4.md"
            }
        ]
    }
    with open("data/emails/em_001.json", "w") as f:
        json.dump(correct_email, f)

    # 干扰邮件1 – 旧版草案（也有approved标签，但时间更早）
    draft_email = {
        "id": "em_002",
        "thread_id": "th_orbital_launch",
        "folder": "inbox",
        "sender_id": "nina.santos@auroralabs.com",
        "subject": "DRAFT v2 for review",
        "timestamp": (base_time - timedelta(days=2)).isoformat() + "Z",
        "importance": "medium",
        "labels": ["draft", "launch"],
        "body": "Please review the attached draft.",
        "attachments": [
            {
                "attachment_id": "att_skylink_draft_v2",
                "filename": "skyLink_draft_v2.md"
            }
        ]
    }
    with open("data/emails/em_002.json", "w") as f:
        json.dump(draft_email, f)

    # 干扰邮件2 – 另一产品（没有approved标签）
    other_email = {
        "id": "em_003",
        "thread_id": "th_lunar_gateway",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "LunaNet briefing",
        "timestamp": (base_time + timedelta(hours=1)).isoformat() + "Z",
        "importance": "low",
        "labels": ["info"],
        "body": "See attached for the lunar project overview.",
        "attachments": [
            {
                "attachment_id": "att_luna_old_brief",
                "filename": "luna_old_brief.md"
            }
        ]
    }
    with open("data/emails/em_003.json", "w") as f:
        json.dump(other_email, f)

    # 干扰邮件3 – 最新但没有approved标签，且附件是v3
    no_approve_email = {
        "id": "em_004",
        "thread_id": "th_orbital_launch",
        "folder": "inbox",
        "sender_id": "nina.santos@auroralabs.com",
        "subject": "Updated draft v3 for review",
        "timestamp": (base_time + timedelta(hours=2)).isoformat() + "Z",
        "importance": "medium",
        "labels": ["draft", "launch", "waiting"],
        "body": "Latest draft before final approval.",
        "attachments": [
            {
                "attachment_id": "att_skylink_draft_v3",
                "filename": "skylink_draft_v3.md"
            }
        ]
    }
    with open("data/emails/em_004.json", "w") as f:
        json.dump(no_approve_email, f)

if __name__ == "__main__":
    build_env()
