import os
import json
import random
random.seed(42)

def build_env():
    # 确保基础目录存在
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    
    # accounts.json (未使用，但保留schema)
    accounts = [
        {"account_id": "acc_001", "display_name": "NorthStar AI", "department": "R&D",
         "email": "northstar@example.com", "permissions": ["read", "write"], "default_region": "us-east",
         "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)
    
    # contacts.json
    contacts = [
        {"contact_id": "c001", "name": "Dev Mehra", "role": "Archive Operations",
         "email": "dev.mehra@northstar.example.com"},
        {"contact_id": "c002", "name": "Keiko Han", "role": "Market Intelligence Partner",
         "email": "keiko.han@northstar.example.com"},
        {"contact_id": "c003", "name": "Rhea Morita", "role": "Signal Research Lead",
         "email": "rhea.morita@northstar.example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # attachments.json 包含匹配指南
    attachments = [
        {"path": "solution_matching_notes.md", "title": "Solution Matching Notes",
         "kind": "matching_guide",
         "description": "Instructions for identifying target solution name across documents."},
        {"path": "temp_record_guidelines.md", "title": "Temporary Record Guidelines",
         "kind": "record_schema",
         "description": "Schema for saving clue records."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 创建 solution_matching_notes.md（帮助agent确认目标名称）
    notes_content = """# Solution Matching Notes

Target solution: **HelioSync Edge Inference Fabric**

Do NOT include:
- HelioSync Edge (missing "Inference Fabric")
- HelioSync Edge Inference Platform (different platform)
- HelioSync Edge Fabric (incomplete)

Only exact string match qualifies.
"""
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write(notes_content)

    # 创建 temp_record_guidelines.md
    with open("data/attachments/temp_record_guidelines.md", "w") as f:
        f.write("# Temporary Record Guidelines\nOutput JSON array with fields: id, title, type.\n")

    # ----- reports -----
    reports = [
        {
            "report_id": "rpt_001",
            "title": "Industrial Edge Inference Landscape 2026",
            "sector": "industrial_ai",
            "published_at": "2026-03-10",
            "tags": ["edge", "inference", "helio"],
            "summary": "Covers HelioSync Edge Inference Fabric deployment in factory settings.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Detailed analysis..."
        },
        {
            "report_id": "rpt_002",
            "title": "HelioSync Edge Deployment Benchmarks",
            "sector": "industrial_ai",
            "published_at": "2026-02-20",
            "tags": ["edge", "helio"],
            "summary": "Focuses on HelioSync Edge without inference fabric.",
            "solution_aliases": ["HelioSync Edge"],
            "content": "This is a distractor - only mentions HelioSync Edge."
        },
        {
            "report_id": "rpt_003",
            "title": "Logistics AI Summit Report",
            "sector": "logistics_ai",
            "published_at": "2026-04-05",
            "tags": ["logistics", "inference", "fabric"],
            "summary": "References HelioSync Edge Inference Fabric in warehouse automation.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Includes case study..."
        },
        {
            "report_id": "rpt_004",
            "title": "Robotics Edge Platform Review",
            "sector": "robotics",
            "published_at": "2026-01-15",
            "tags": ["robotics", "platform"],
            "summary": "Discusses HelioSync Edge Inference Platform (different product).",
            "solution_aliases": ["HelioSync Edge Inference Platform"],
            "content": "Not our target."
        },
        {
            "report_id": "rpt_005",
            "title": "Inference Fabric for Autonomous Robots",
            "sector": "robotics",
            "published_at": "2026-05-01",
            "tags": ["fabric", "inference", "helio"],
            "summary": "Direct mention of HelioSync Edge Inference Fabric in robotics.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Key findings..."
        },
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # ----- presentations -----
    presentations = [
        {
            "presentation_id": "pres_001",
            "title": "Partner Marketing Q2 Deck",
            "owner": "partner_marketing",
            "updated_at": "2026-03-22",
            "tags": ["edge", "inference", "fabric"],
            "summary": "Slides about HelioSync Edge Inference Fabric go-to-market.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Final version."
        },
        {
            "presentation_id": "pres_002",
            "title": "Tech Deep Dive: HelioSync Edge",
            "owner": "research_design",
            "updated_at": "2026-02-28",
            "tags": ["edge", "helio"],
            "summary": "Deep dive into HelioSync Edge hardware (missing 'Inference Fabric').",
            "solution_aliases": ["HelioSync Edge"],
            "deck_notes": "Old version."
        },
        {
            "presentation_id": "pres_003",
            "title": "Inference Fabric Roadmap 2026",
            "owner": "strategy_team",
            "updated_at": "2026-04-12",
            "tags": ["fabric", "inference", "helio"],
            "summary": "Strategic roadmap for HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Internal only."
        },
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # ----- media_samples -----
    media_samples = [
        {
            "sample_id": "sample_001",
            "title": "Podcast: Edge Computing Trends",
            "channel": "podcast_transcript",
            "captured_at": "2026-03-01T10:00:00Z",
            "tags": ["edge", "podcast"],
            "summary": "General edge discussion, mentions HelioSync Edge once.",
            "solution_aliases": ["HelioSync Edge"],
            "content": "Transcription with no fabric mention."
        },
        {
            "sample_id": "sample_002",
            "title": "Keynote: HelioSync Fabric Launch",
            "channel": "keynote_transcript",
            "captured_at": "2026-04-18T14:30:00Z",
            "tags": ["fabric", "launch", "helio"],
            "summary": "Full keynote announcing HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "This is the one."
        },
        {
            "sample_id": "sample_003",
            "title": "Editorial Draft: Inference at the Edge",
            "channel": "editorial_draft",
            "captured_at": "2026-05-05T09:00:00Z",
            "tags": ["inference", "edge"],
            "summary": "Draft article about edge inference platforms – mentions HelioSync Edge Inference Platform.",
            "solution_aliases": ["HelioSync Edge Inference Platform"],
            "content": "Not our target."
        },
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # 额外干扰文件：旧备份
    os.makedirs("archive", exist_ok=True)
    with open("archive/old_reports.json", "w") as f:
        f.write('{"reports": []}')

    # 在ops下放一个占位文件，但最终答案文件是 target_clues.json（由agent创建）
    with open("ops/README.txt", "w") as f:
        f.write("Place gathered clues here.\n")

if __name__ == "__main__":
    build_env()
