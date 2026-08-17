import os
import json

def build_env():
    # 确保关键目录存在
    for d in ["data/reports", "data/presentations", "data/media_samples", "data/attachments", "ops"]:
        os.makedirs(d, exist_ok=True)

    # ---- reports.json ----
    reports = [
        {
            "report_id": "RPT-2026-001",
            "title": "Edge Inference at Scale",
            "sector": "industrial_ai",
            "published_at": "2026-03-15",
            "tags": ["edge", "inference", "helio"],
            "summary": "Evaluating HelioSync Edge Inference Fabric for industrial control systems.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF"],
            "content": "Detailed analysis of HelioSync Edge Inference Fabric performance benchmarks."
        },
        {
            "report_id": "RPT-2026-002",
            "title": "Cloud-Native AI Trends",
            "sector": "industrial_ai",
            "published_at": "2026-02-10",
            "tags": ["cloud", "ai"],
            "summary": "Overview of cloud AI platforms.",
            "solution_aliases": ["NovaCore AI"],
            "content": "Trends in cloud-native AI."
        },
        {
            "report_id": "RPT-2026-003",
            "title": "HelioSync Deployment Guide",
            "sector": "logistics_ai",
            "published_at": "2026-04-01",
            "tags": ["helio", "deployment"],
            "summary": "Step-by-step guide for deploying HelioSync Edge Inference Fabric in logistics.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Guide for deployment in warehouse environments."
        },
        {
            "report_id": "RPT-2026-004",
            "title": "Edge Computing for Logistics",
            "sector": "logistics_ai",
            "published_at": "2026-01-20",
            "tags": ["edge", "logistics"],
            "summary": "Exploring HelioSync Edge capabilities.",
            "solution_aliases": ["HelioSync Edge"],
            "content": "Partial mention of edge computing."
        },
        {
            "report_id": "RPT-2026-005",
            "title": "Legacy Report",
            "sector": "robotics",
            "published_at": "2025-12-01",
            "tags": ["legacy"],
            "summary": "Old report with no solution aliases.",
            "solution_aliases": None,
            "content": "Outdated content."
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # ---- presentations.json ----
    presentations = [
        {
            "presentation_id": "PRES-2026-001",
            "title": "AI in Manufacturing",
            "owner": "partner_marketing",
            "updated_at": "2026-03-20",
            "tags": ["manufacturing", "ai"],
            "summary": "General AI overview.",
            "solution_aliases": ["NovaCore AI"],
            "deck_notes": "Slide deck for manufacturing summit."
        },
        {
            "presentation_id": "PRES-2026-002",
            "title": "HelioSync Inference Fabric Pitch",
            "owner": "strategy_team",
            "updated_at": "2026-04-05",
            "tags": ["helio", "inference", "pitch"],
            "summary": "Pitch deck for HelioSync Edge Inference Fabric targeting logistics.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Key slides include ROI analysis."
        },
        {
            "presentation_id": "PRES-2026-003",
            "title": "Edge Rollout Q2",
            "owner": "research_design",
            "updated_at": "2026-03-30",
            "tags": ["edge", "rollout"],
            "summary": "Edge rollout plan for various solutions.",
            "solution_aliases": ["HelioSync Edge", "EdgeCore"],
            "deck_notes": "Rollout timeline."
        },
        {
            "presentation_id": "PRES-2026-004",
            "title": "Misc Deck",
            "owner": "partner_marketing",
            "updated_at": "2026-02-01",
            "tags": ["misc"],
            "summary": "No solution aliases field.",
            "deck_notes": "No aliases"
        }
    ]
    # 第四个记录故意没有 solution_aliases 键
    presentations[3].pop("solution_aliases", None)
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # ---- media_samples.json ----
    media_samples = [
        {
            "sample_id": "MS-2026-001",
            "title": "Interview: HelioSync Fabric Lead",
            "channel": "podcast_transcript",
            "captured_at": "2026-04-10",
            "tags": ["interview", "helio", "fabric"],
            "summary": "Lead architect discusses HelioSync Edge Inference Fabric architecture.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Transcript of the interview."
        },
        {
            "sample_id": "MS-2026-002",
            "title": "Keynote: Future of AI",
            "channel": "keynote_transcript",
            "captured_at": "2026-03-01",
            "tags": ["keynote", "ai"],
            "summary": "General AI keynote.",
            "solution_aliases": ["General AI"],
            "content": "Keynote transcript."
        },
        {
            "sample_id": "MS-2026-003",
            "title": "Editorial: HelioSync Updates",
            "channel": "editorial_draft",
            "captured_at": "2026-02-15",
            "tags": ["helio", "update"],
            "summary": "HelioSync Edge update summary.",
            "solution_aliases": ["HelioSync Edge"],
            "content": "Draft editorial."
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # ---- attachments.json ----
    attachments = [
        {
            "path": "data/attachments/solution_matching_notes.md",
            "title": "Solution Matching Notes",
            "kind": "matching_guide",
            "description": "Guidelines for which documents to include."
        },
        {
            "path": "data/attachments/temp_record_guidelines.md",
            "title": "Temporary Record Guidelines",
            "kind": "record_schema",
            "description": "Format for output clue list."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---- 附件文件内容 ----
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write("""# Solution Matching Notes
Only include documents whose `solution_aliases` field contains exactly "HelioSync Edge Inference Fabric". Do not include documents with partial or similar strings.
""")
    with open("data/attachments/temp_record_guidelines.md", "w") as f:
        f.write("""# Temporary Record Guidelines
Each clue entry must be an object with the following fields:
- source: one of "report", "presentation", "media_sample"
- id: the document identifier (e.g., report_id)
- snippet: the document's summary text
Save the list as a JSON file at the workspace root under the path "ops/collected_clues.json". The JSON should have a top-level object with a key "clues" containing the array of clue objects.
""")

if __name__ == "__main__":
    build_env()
