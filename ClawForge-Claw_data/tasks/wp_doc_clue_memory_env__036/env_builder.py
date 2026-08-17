import os
import json
import random

def build_env():
    # 创建必要目录
    for d in ['data/reports', 'data/presentations', 'data/media_samples', 'data']:
        os.makedirs(d, exist_ok=True)

    # ===== 报告数据 =====
    reports = []
    target_sol = "HelioSync Edge Inference Fabric"

    # 正确匹配的报告1
    reports.append({
        "report_id": "RPT-2042",
        "title": "Edge Inference Market Landscape Q2 2026",
        "sector": "industrial_ai",
        "published_at": "2026-04-15",
        "tags": ["edge ai", "inference", "helio"],
        "summary": "HelioSync Edge Inference Fabric emerges as a leading solution for real-time AI at the edge.",
        "solution_aliases": [target_sol, "HelioSync Edge"],
        "content": "Detailed analysis of edge inference solutions..."
    })
    # 正确匹配的报告2
    reports.append({
        "report_id": "RPT-301",
        "title": "Industrial AI Use Case Compendium",
        "sector": "industrial_ai",
        "published_at": "2026-03-01",
        "tags": ["industrial ai", "edge"],
        "summary": "HelioSync Edge Inference Fabric deployed in smart manufacturing pilot.",
        "solution_aliases": [target_sol],
        "content": "Case studies of industrial AI deployments..."
    })
    # 干扰报告1：名字类似但实际不是（少Fabric）
    reports.append({
        "report_id": "RPT-99",
        "title": "HelioSync Edge Inference Trends",
        "sector": "logistics_ai",
        "published_at": "2026-02-10",
        "tags": ["edge", "helio"],
        "summary": "Examines HelioSync Edge Inference platform capabilities.",
        "solution_aliases": ["HelioSync Edge Inference"],
        "content": "..." 
    })
    # 干扰报告2：完全不相关
    reports.append({
        "report_id": "RPT-512",
        "title": "Logistics Automation Outlook",
        "sector": "logistics_ai",
        "published_at": "2025-12-01",
        "tags": ["logistics", "automation"],
        "summary": "Analysis of autonomous warehouse solutions.",
        "solution_aliases": ["Edge Sync Logistics"],
        "content": "..."
    })

    with open('data/reports/reports.json', 'w') as f:
        json.dump({"reports": reports}, f, indent=2)

    # ===== 演示文稿数据 =====
    presentations = []
    # 正确匹配的演示
    presentations.append({
        "presentation_id": "PRES-007",
        "title": "Partner Tech Showcase: Edge Inference Fabric",
        "owner": "partner_marketing",
        "updated_at": "2026-04-20",
        "tags": ["partner", "edge", "inference"],
        "summary": "HelioSync Edge Inference Fabric integration demo for industrial vision.",
        "solution_aliases": [target_sol],
        "deck_notes": "Slide deck with performance benchmarks..."
    })
    # 干扰演示1：名字相近但内容无关
    presentations.append({
        "presentation_id": "PRES-023",
        "title": "HelioSync Edge Sync Strategy",
        "owner": "strategy_team",
        "updated_at": "2026-01-15",
        "tags": ["helio", "strategy"],
        "summary": "Overview of HelioSync Edge synchronization protocol.",
        "solution_aliases": ["HelioSync Edge"],
        "deck_notes": "..."
    })
    # 干扰演示2：完全无关
    presentations.append({
        "presentation_id": "PRES-112",
        "title": "Robotics Fleet Management",
        "owner": "research_design",
        "updated_at": "2025-11-01",
        "tags": ["robotics", "fleet"],
        "summary": "Managing large-scale robot fleets.",
        "solution_aliases": [],
        "deck_notes": "..."
    })

    with open('data/presentations/presentations.json', 'w') as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # ===== 媒体样本数据 =====
    media_samples = []
    # 正确匹配的媒体样本
    media_samples.append({
        "sample_id": "MS-042",
        "title": "Edge AI at the Factory Floor – Podcast",
        "channel": "podcast_transcript",
        "captured_at": "2026-04-22",
        "tags": ["edge", "ai", "helio"],
        "summary": "Discussion on HelioSync Edge Inference Fabric deployment in automotive manufacturing.",
        "solution_aliases": [target_sol],
        "content": "Full transcript..."
    })
    # 干扰媒体1：名称包含但实际不完整
    media_samples.append({
        "sample_id": "MS-088",
        "title": "HelioSync Edge Inference Explained",
        "channel": "keynote_transcript",
        "captured_at": "2026-03-10",
        "tags": ["helio", "edge"],
        "summary": "Keynote on HelioSync Edge Inference architecture.",
        "solution_aliases": ["HelioSync Edge Inference"],
        "content": "..."
    })
    # 干扰媒体2：无关
    media_samples.append({
        "sample_id": "MS-201",
        "title": "Warehouse Robotics Update",
        "channel": "editorial_draft",
        "captured_at": "2026-01-05",
        "tags": ["warehouse", "robotics"],
        "summary": "Latest trends in warehouse automation.",
        "solution_aliases": [],
        "content": "..."
    })

    with open('data/media_samples/media_samples.json', 'w') as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # ===== 其他干扰数据（账户、联系人、附件）—— 保持存在但不影响答案 =====
    accounts = [
        {"account_id": "ACC-001", "display_name": "Industrial AI Co.", "department": "R&D", "email": "contact@industrial-ai.example.com", "permissions": ["read"], "default_region": "us-east", "voice": ["en"]},
        {"account_id": "ACC-022", "display_name": "Edge Solutions Inc.", "department": "Marketing", "email": "info@edgesol.example.com", "permissions": ["read", "write"], "default_region": "eu-west", "voice": ["en", "de"]}
    ]
    with open('data/accounts.json', 'w') as f:
        json.dump({"accounts": accounts, "wrapper": "accounts", "key": "account_id"}, f, indent=2)

    contacts = [
        {"contact_id": "C-101", "name": "Dev Mehra", "role": "Archive Operations", "email": "dev.mehra@northstar.example.com"},
        {"contact_id": "C-102", "name": "Keiko Han", "role": "Market Intelligence Partner", "email": "keiko.han@northstar.example.com"},
        {"contact_id": "C-103", "name": "Rhea Morita", "role": "Signal Research Lead", "email": "rhea.morita@northstar.example.com"}
    ]
    with open('data/contacts.json', 'w') as f:
        json.dump({"contacts": contacts, "wrapper": "contacts", "key": "contact_id"}, f, indent=2)

    attachments = [
        {"path": "solution_matching_notes.md", "title": "Solution Matching Notes", "kind": "matching_guide", "description": "Guide for matching solution aliases."},
        {"path": "temp_record_guidelines.md", "title": "Temporary Record Guidelines", "kind": "record_schema", "description": "Schema for temporary records."}
    ]
    with open('data/attachments.json', 'w') as f:
        json.dump({"attachments": attachments, "wrapper": "attachments", "key": None}, f, indent=2)

    # 确保 clues 目录不存在（Agent需要自己创建）
    if os.path.exists('clues'):
        import shutil
        shutil.rmtree('clues')

if __name__ == '__main__':
    build_env()
