import os
import json

def build_env():
    # media_samples
    os.makedirs("data/media_samples", exist_ok=True)
    media_samples = [
        {
            "sample_id": "ms-001",
            "title": "Edge Fabric Overview",
            "channel": "keynote_transcript",
            "captured_at": "2026-02-10",
            "tags": ["edge", "inference"],
            "summary": "Explores deployment patterns for HelioSync Edge Inference Fabric in edge environments.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "This transcript covers the HelioSync Edge Inference Fabric deployment..."
        },
        {
            "sample_id": "ms-002",
            "title": "HelioSync v2 Launch",
            "channel": "podcast_transcript",
            "captured_at": "2025-11-20",
            "tags": ["heliosync", "v2"],
            "summary": "Introduces HelioSync Edge Inference Fabric 2.0",
            "solution_aliases": ["HelioSync Edge Inference Fabric 2.0"],
            "content": "We are excited to announce HelioSync Edge Inference Fabric 2.0..."
        },
        {
            "sample_id": "ms-003",
            "title": "Data Center Trends",
            "channel": "editorial_draft",
            "captured_at": "2026-03-01",
            "tags": ["data center"],
            "summary": "General trends in edge computing.",
            "solution_aliases": [],
            "content": "Edge computing is transforming data centers..."
        },
        {
            "sample_id": "ms-004",
            "title": "Edge Fabric Deployment",
            "channel": "podcast_transcript",
            "captured_at": "2026-02-20",
            "tags": ["deployment", "heliosync"],
            "summary": "Detailed guide for HelioSync Edge Inference Fabric deployment.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Step-by-step guide for deploying HelioSync Edge Inference Fabric..."
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # presentations
    os.makedirs("data/presentations", exist_ok=True)
    presentations = [
        {
            "presentation_id": "pres-001",
            "title": "Partner Briefing Q1 2026",
            "owner": "partner_marketing",
            "updated_at": "2026-01-15",
            "tags": ["briefing", "heliosync"],
            "summary": "Highlights the HelioSync Edge Inference Fabric roadmap.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Focus on new features..."
        },
        {
            "presentation_id": "pres-002",
            "title": "Old Deck",
            "owner": "research_design",
            "updated_at": "2025-12-20",
            "tags": ["heliosync"],
            "summary": "Mentions HelioSync Edge Inference Fabric but outdated.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Deprecated."
        },
        {
            "presentation_id": "pres-003",
            "title": "Alternative Tech",
            "owner": "strategy_team",
            "updated_at": "2026-02-01",
            "tags": ["edge", "inference"],
            "summary": "Focus on HelioSync Edge Inference.",
            "solution_aliases": ["HelioSync Edge Inference"],
            "deck_notes": "Different product."
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # reports (distractors)
    os.makedirs("data/reports", exist_ok=True)
    reports = [
        {
            "report_id": "rpt-001",
            "title": "Industrial AI Report",
            "sector": "industrial_ai",
            "published_at": "2026-02-01",
            "tags": ["ai", "industry"],
            "summary": "Discusses HelioSync Edge Inference Fabric in industrial settings.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Industrial AI benefits from HelioSync Edge Inference Fabric..."
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # attachments
    os.makedirs("data/attachments", exist_ok=True)
    attachments = [
        {
            "path": "data/attachments/solution_matching_notes.md",
            "title": "Solution Matching Notes",
            "kind": "matching_guide",
            "description": "Guide for matching solutions."
        },
        {
            "path": "data/attachments/temp_record_guidelines.md",
            "title": "Temporary Record Guidelines",
            "kind": "record_schema",
            "description": "Schema for temporary records."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # attachment files
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write("""# Solution Matching Notes

- Use **exact string match** against the `solution_aliases` array.
- Only consider records where the date (`captured_at` for media, `updated_at` for presentations) is **on or after 2026-01-01**.
- Ignore reports for now.
- If a record has no `solution_aliases` or an empty array, skip it.
""")

    with open("data/attachments/temp_record_guidelines.md", "w") as f:
        f.write("""# Temporary Record Guidelines

(Not relevant to this task.)
""")

    # output directory
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
