import json
import os

def build_env():
    # --- reports ---
    reports = [
        {
            "report_id": "RPT-2026-0421",
            "title": "Industrial AI Edge Adoption Trends",
            "sector": "industrial_ai",
            "published_at": "2026-04-21",
            "tags": ["edge inference", "industrial", "HelioSync"],
            "summary": "Analysis of edge inference adoption in manufacturing.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "Industrial Edge Platform"],
            "content": "Report content..."
        },
        {
            "report_id": "RPT-2026-0418",
            "title": "Logistics Automation Report Q2",
            "sector": "logistics_ai",
            "published_at": "2026-04-18",
            "tags": ["logistics", "automation", "computer vision"],
            "summary": "Focus on warehouse robotics and vision systems.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "LogiVision"],
            "content": "Report content..."
        },
        {
            "report_id": "RPT-2026-0405",
            "title": "Robotics Controller Benchmark",
            "sector": "robotics",
            "published_at": "2026-04-05",
            "tags": ["robotics", "controller", "FPGA"],
            "summary": "Benchmark of low-latency controllers for robotics.",
            "solution_aliases": ["HelioSync Edge Inference Platform"],  # 诱饵：少 "Fabric"
            "content": "Report content..."
        }
    ]

    # --- presentations ---
    presentations = [
        {
            "presentation_id": "PRES-2026-0312",
            "title": "HelioSync Edge Deployment Case Study",
            "owner": "partner_marketing",
            "updated_at": "2026-03-12",
            "tags": ["case study", "edge deployment", "HelioSync"],
            "summary": "How a large retailer deployed HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "Retail AI"],
            "deck_notes": "Full deck available."
        },
        {
            "presentation_id": "PRES-2026-0215",
            "title": "Next-Gen Inference Accelerators",
            "owner": "research_design",
            "updated_at": "2026-02-15",
            "tags": ["accelerator", "FPGA", "prototype"],
            "summary": "Internal research on custom inference chips.",
            "solution_aliases": ["HelioSync Edge Inference"],  # 诱饵：缺 "Fabric"
            "deck_notes": "Confidential."
        }
    ]

    # --- media_samples ---
    media_samples = [
        {
            "sample_id": "MED-2026-0503",
            "title": "Interview with HelioSync CTO",
            "channel": "podcast_transcript",
            "captured_at": "2026-05-03",
            "tags": ["interview", "HelioSync", "edge AI"],
            "summary": "CTO discusses HelioSync Edge Inference Fabric capabilities.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "Edge AI Suite"],
            "content": "Transcript content..."
        },
        {
            "sample_id": "MED-2026-0428",
            "title": "Edge Fabric Whitepaper Summary",
            "channel": "editorial_draft",
            "captured_at": "2026-04-28",
            "tags": ["whitepaper", "edge fabric", "inference"],
            "summary": "Draft summary of the HelioSync Edge Inference Fabric whitepaper.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Draft content..."
        },
        {
            "sample_id": "MED-2026-0401",
            "title": "Keynote: Future of Edge",
            "channel": "keynote_transcript",
            "captured_at": "2026-04-01",
            "tags": ["keynote", "edge computing", "future"],
            "summary": "Keynote from AI Summit covering multiple edge solutions.",
            "solution_aliases": ["HelioSync Fabric", "Edge AI"],  # 诱饵：少 "Edge Inference"
            "content": "Keynote transcript..."
        }
    ]

    # --- attachments (干扰项，不包含匹配规则) ---
    attachments = [
        {"path": "solution_matching_notes.md", "title": "Solution Matching Notes", "kind": "matching_guide",
         "description": "Guidelines on how to match solution aliases."},
        {"path": "temp_record_guidelines.md", "title": "Temporary Record Guidelines", "kind": "record_schema",
         "description": "Schema for saving clue lists."}
    ]

    # --- 目录结构 ---
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 写入文件
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 额外诱饵: 一个空json或无关文件
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f, indent=2)
    with open("ops/irrelevant_notes.txt", "w") as f:
        f.write("This file is not needed.\n")

if __name__ == "__main__":
    build_env()
