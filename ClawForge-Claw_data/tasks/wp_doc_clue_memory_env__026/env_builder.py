import os
import json
import random
from pathlib import Path

def build_env():
    # 确保当前工作目录正确（CWD 已是 .）
    base = Path(".")
    
    # 清理可能残留的旧产物（但保留其他可能已有的文件？为保证确定性，只创建不删除）
    # 但为了干净，我们只创建所需目录
    dirs = ["data/reports", "data/presentations", "data/media_samples", "data/attachments", "ops"]
    for d in dirs:
        (base / d).mkdir(parents=True, exist_ok=True)
    
    # ========== 定义目标 solution alias ==========
    TARGET = "HelioSync Edge Inference Fabric"
    
    # ========== 1. reports.json (6 个报告，其中 2 个匹配, 2 个近似, 2 个不相关) ==========
    reports = [
        {
            "report_id": "RPT-001",
            "title": "Edge AI Deployment in Manufacturing",
            "sector": "industrial_ai",
            "published_at": "2025-11-15",
            "tags": ["edge", "manufacturing"],
            "summary": "Covers on-premise inference deployments.",
            "solution_aliases": [TARGET],
            "content": "Report content... CLUE_BULLET: Edge-deploy-rpt-001"
        },
        {
            "report_id": "RPT-002",
            "title": "HelioSync Edge Inference Fabric – Field Test Results",
            "sector": "industrial_ai",
            "published_at": "2025-12-01",
            "tags": ["helio", "edge", "inference"],
            "summary": "Internal field test summary for HelioSync Edge.",
            "solution_aliases": [TARGET],
            "content": "Report content... CLUE_BULLET: Edge-test-rpt-002"
        },
        {
            "report_id": "RPT-003",
            "title": "HelioSync Edge Inference Fabric Lite Overview",
            "sector": "logistics_ai",
            "published_at": "2025-10-20",
            "tags": ["helio", "edge", "lite"],
            "summary": "A lighter variant – not the full fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric Lite"],
            "content": "CLUE_BULLET: fake-lite-rpt-003"
        },
        {
            "report_id": "RPT-004",
            "title": "HelioSync Edge Inference (no fabric)",
            "sector": "robotics",
            "published_at": "2025-09-10",
            "tags": ["helio", "inference"],
            "summary": "Discusses only the inference component.",
            "solution_aliases": ["HelioSync Edge Inference"],
            "content": "CLUE_BULLET: fake-inference-only-rpt-004"
        },
        {
            "report_id": "RPT-005",
            "title": "Industrial IoT Edge Analytics",
            "sector": "industrial_ai",
            "published_at": "2025-08-05",
            "tags": ["iot", "analytics"],
            "summary": "Unrelated to HelioSync.",
            "solution_aliases": [],
            "content": "CLUE_BULLET: unrelated-rpt-005"
        },
        {
            "report_id": "RPT-006",
            "title": "Competitor Landscape Report",
            "sector": "logistics_ai",
            "published_at": "2025-07-01",
            "tags": ["competitor"],
            "summary": "Mentions HelioSync briefly but not as a solution alias.",
            "solution_aliases": ["OtherFabric"],
            "content": "CLUE_BULLET: competitor-rpt-006"
        }
    ]
    with open(base / "data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)
    
    # ========== 2. presentations.json (5 个演示，2 个匹配，1 个近似，2 个无关) ==========
    presentations = [
        {
            "presentation_id": "PRES-001",
            "title": "HelioSync Edge Inference Fabric – Architecture Deep Dive",
            "owner": "partner_marketing",
            "updated_at": "2025-11-20",
            "tags": ["helio", "architecture"],
            "summary": "Detailed architecture deck.",
            "solution_aliases": [TARGET],
            "deck_notes": "Slide 23 contains deployment topology. CLUE_BULLET: arch-deck-pres-001"
        },
        {
            "presentation_id": "PRES-002",
            "title": "Q4 Portfolio Review – Edge Solutions",
            "owner": "strategy_team",
            "updated_at": "2025-12-15",
            "tags": ["portfolio", "edge"],
            "summary": "Reviews multiple edge offerings including HelioSync Edge Inference Fabric.",
            "solution_aliases": [TARGET, "OtherEdge"],
            "deck_notes": "Slide 7 – HelioSync Edge Inference Fabric highlights. CLUE_BULLET: q4-review-pres-002"
        },
        {
            "presentation_id": "PRES-003",
            "title": "HelioSync Edge Inference (Preliminary)",
            "owner": "research_design",
            "updated_at": "2025-10-05",
            "tags": ["helio", "prelim"],
            "summary": "Early research, not the full fabric.",
            "solution_aliases": ["HelioSync Edge Inference"],
            "deck_notes": "CLUE_BULLET: preliminary-pres-003"
        },
        {
            "presentation_id": "PRES-004",
            "title": "Annual Sales Kickoff – Keynote",
            "owner": "partner_marketing",
            "updated_at": "2025-06-10",
            "tags": ["sales", "keynote"],
            "summary": "No mention of HelioSync.",
            "solution_aliases": [],
            "deck_notes": "CLUE_BULLET: sales-kickoff-pres-004"
        },
        {
            "presentation_id": "PRES-005",
            "title": "Edge Inference Fabric Comparison",
            "owner": "research_design",
            "updated_at": "2025-11-30",
            "tags": ["comparison", "edge"],
            "summary": "Compares multiple fabrics; includes HelioSync Edge Inference Fabric as one entry.",
            "solution_aliases": [TARGET, "FabricX", "FabricY"],
            "deck_notes": "Slide 12 – HelioSync row. CLUE_BULLET: comparison-pres-005"
        }
    ]
    with open(base / "data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)
    
    # ========== 3. media_samples.json (4 个样本，1 个匹配，1 个近似，2 个无关) ==========
    media_samples = [
        {
            "sample_id": "MEDIA-001",
            "title": "Podcast: HelioSync Edge Inference Fabric Launch",
            "channel": "podcast_transcript",
            "captured_at": "2025-12-10",
            "tags": ["helio", "launch"],
            "summary": "Podcast transcript discussing the launch.",
            "solution_aliases": [TARGET],
            "content": "Transcript content... CLUE_BULLET: podcast-media-001"
        },
        {
            "sample_id": "MEDIA-002",
            "title": "Editorial Draft – HelioSync Edge Inference",
            "channel": "editorial_draft",
            "captured_at": "2025-11-25",
            "tags": ["draft", "editorial"],
            "summary": "Draft about HelioSync Edge Inference (Lite).",
            "solution_aliases": ["HelioSync Edge Inference Lite"],
            "content": "CLUE_BULLET: draft-lite-media-002"
        },
        {
            "sample_id": "MEDIA-003",
            "title": "Keynote Transcript – AI Summit 2025",
            "channel": "keynote_transcript",
            "captured_at": "2025-09-15",
            "tags": ["summit", "ai"],
            "summary": "No HelioSync mention.",
            "solution_aliases": [],
            "content": "CLUE_BULLET: summit-transcript-media-003"
        },
        {
            "sample_id": "MEDIA-004",
            "title": " HelioSync Edge Inference Fabric – Customer Testimonial",
            "channel": "editorial_draft",
            "captured_at": "2025-12-20",
            "tags": ["testimonial", "helio"],
            "summary": "Customer testimonial about HelioSync Edge Inference Fabric.",
            "solution_aliases": [TARGET],
            "content": "CLUE_BULLET: testimonial-media-004"
        }
    ]
    with open(base / "data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)
    
    # ========== 4. attachments.json (两个附件，仅用于提供上下文) ==========
    attachments = [
        {
            "path": "solution_matching_notes.md",
            "title": "Solution Matching Notes",
            "kind": "matching_guide",
            "description": "HelioSync solution aliases must match exactly – partial or alternative names are not acceptable."
        },
        {
            "path": "temp_record_guidelines.md",
            "title": "Temporary Record Guidelines",
            "kind": "record_schema",
            "description": "Clue list should be saved as JSON with document IDs as keys and an array of clue bullets as values."
        }
    ]
    with open(base / "data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)
    
    # 创建附件内容文件
    with open(base / "data/attachments/solution_matching_notes.md", "w") as f:
        f.write("# Solution Matching Notes\n\n"
                "Only documents whose `solution_aliases` contain the exact string "
                "`HelioSync Edge Inference Fabric` should be considered matching. "
                "Do **not** include documents with near matches like "
                "`HelioSync Edge Inference` or `HelioSync Edge Inference Fabric Lite`.\n")
    
    with open(base / "data/attachments/temp_record_guidelines.md", "w") as f:
        f.write("# Temporary Record Guidelines\n\n"
                "The output file should be named `ops/clue_list.json` and must contain "
                "a JSON object where keys are document IDs and values are arrays of "
                "clue bullet strings found in that document's `content` or `deck_notes`.\n")
    
    # ========== 5. 额外干扰：data/contacts.json 和 data/accounts.json (无关但存在) ==========
    contacts = [
        {"contact_id": "C001", "name": "Rhea Morita", "role": "Signal Research Lead",
         "email": "rhea.morita@northstar.example.com"},
        {"contact_id": "C002", "name": "Dev Mehra", "role": "Archive Operations",
         "email": "dev.mehra@northstar.example.com"}
    ]
    with open(base / "data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)
    
    accounts = [
        {"account_id": "A001", "display_name": "NorthStar", "department": "Research",
         "email": "northstar@example.com", "permissions": ["read","write"], "default_region": "us-east",
         "voice": ["en"]}
    ]
    with open(base / "data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)
    
    # 确保 ops 目录存在（但为空，agent 需要写入）
    (base / "ops").mkdir(exist_ok=True)
    # 写入一个隐藏文件测试？（不需要）

if __name__ == "__main__":
    build_env()
