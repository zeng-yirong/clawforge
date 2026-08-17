import os
import json

def build_env():
    # 创建目录结构
    dirs = [
        "data/reports",
        "data/presentations",
        "data/media_samples",
        "ops",
        "data"  # 用于 accounts.json, contacts.json, attachments.json
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ========== 报告 ==========
    reports = [
        {
            "report_id": "RPT-2026-001",
            "title": "Industrial AI Market Trends",
            "sector": "industrial_ai",
            "published_at": "2026-03-15",
            "tags": ["q2", "ai"],
            "summary": "Analysis of HelioSync Edge Inference Fabric in smart manufacturing.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HelioSync"],
            "content": "（内容略）"
        },
        {
            "report_id": "RPT-2026-002",
            "title": "HelioSync Edge Evaluation",
            "sector": "robotics",
            "published_at": "2026-01-20",
            "tags": ["obsolete", "q1"],
            "summary": "Early evaluation of HelioSync Edge fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "（内容略）"
        },
        {
            "report_id": "RPT-2026-003",
            "title": "Warehouse Robotics",
            "sector": "logistics_ai",
            "published_at": "2026-02-10",
            "tags": [],
            "summary": "Some warehouse automation trends.",
            "solution_aliases": ["OptiPath"],
            "content": "（内容略）"
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    # ========== 演示文稿 ==========
    presentations = [
        {
            "presentation_id": "PRES-2026-001",
            "title": "HelioSync Edge Fabric Launch",
            "owner": "partner_marketing",
            "updated_at": "2026-04-01",
            "tags": ["launch", "q2"],
            "summary": "Launch deck for HelioSync Edge Inference Fabric with benchmarks.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "（笔记略）"
        },
        {
            "presentation_id": "PRES-2026-002",
            "title": "Supply Chain AI",
            "owner": "research_design",
            "updated_at": "2026-03-20",
            "tags": ["draft"],
            "summary": "Draft on supply chain",
            "solution_aliases": ["HelioSync Edge"],
            "deck_notes": "（笔记略）"
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump(presentations, f, indent=2)

    # ========== 媒体样本 ==========
    media_samples = [
        {
            "sample_id": "MEDIA-2026-001",
            "title": "HelioSync Edge Inference Interview",
            "channel": "podcast_transcript",
            "captured_at": "2026-04-10",
            "tags": ["podcast", "q2"],
            "summary": "Transcript discussing HelioSync Edge Inference Fabric deployment.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "（内容略）"
        },
        {
            "sample_id": "MEDIA-2026-002",
            "title": "Robotics Roundtable",
            "channel": "keynote_transcript",
            "captured_at": "2026-01-05",
            "tags": ["obsolete"],
            "summary": "Obsolete keynote about general AI",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "（内容略）"
        },
        {
            "sample_id": "MEDIA-2026-003",
            "title": "Media Trends",
            "channel": "editorial_draft",
            "captured_at": "2026-03-01",
            "tags": [],
            "summary": "Editorial on media trends",
            "solution_aliases": ["Edge Computing"],
            "content": "（内容略）"
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump(media_samples, f, indent=2)

    # ========== 干扰附件、账户、联系人（不影响答案） ==========
    attachments = [
        {"path": "solution_matching_notes.md", "title": "Solution Matching Notes",
         "kind": "matching_guide", "description": "How to match solutions."},
        {"path": "temp_record_guidelines.md", "title": "Temporary Record Guidelines",
         "kind": "record_schema", "description": "Guidelines for record storage."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    accounts = [
        {"account_id": "acc-001", "display_name": "Northstar", "department": "R&D",
         "email": "northstar@example.com", "permissions": ["read", "write"],
         "default_region": "us-east", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = [
        {"contact_id": "c-001", "name": "Dev Mehra", "role": "Archive Operations",
         "email": "dev.mehra@northstar.example.com"},
        {"contact_id": "c-002", "name": "Keiko Han", "role": "Market Intelligence Partner",
         "email": "keiko.han@northstar.example.com"},
        {"contact_id": "c-003", "name": "Rhea Morita", "role": "Signal Research Lead",
         "email": "rhea.morita@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ops 目录留空，等待 agent 写入

if __name__ == "__main__":
    build_env()
