import os
import json

def build_env():
    # --- data/reports ---
    os.makedirs("data/reports", exist_ok=True)
    reports = [
        {
            "report_id": "RPT-2026-001",
            "title": "Edge AI Deployment with HelioSync Edge Inference Fabric",
            "sector": "industrial_ai",
            "published_at": "2026-03-15",
            "tags": ["helio", "edge", "ai"],
            "summary": "Overview of HelioSync Edge Inference Fabric in factory settings.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "HelioSync Edge Inference Fabric delivers 3x throughput over previous generation. Deployed in 12 factories."
        },
        {
            "report_id": "RPT-2026-002",
            "title": "Legacy HelioStream Integration Guide",
            "sector": "logistics_ai",
            "published_at": "2025-11-20",
            "tags": ["helio", "legacy"],
            "summary": "Old HelioStream v2 documentation, not Edge Inference Fabric.",
            "solution_aliases": ["HelioStream"],
            "content": "HelioStream v2 does not support edge inference. Use HelioSync instead."
        },
        {
            "report_id": "RPT-2026-003",
            "title": "Robotics Vision Update Q1",
            "sector": "robotics",
            "published_at": "2026-01-10",
            "tags": ["robotics", "vision"],
            "summary": "No HelioSync mention.",
            "solution_aliases": [],
            "content": "Vision updates for robotic arms."
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # --- data/presentations ---
    os.makedirs("data/presentations", exist_ok=True)
    presentations = [
        {
            "presentation_id": "PRES-2026-001",
            "title": "HelioSync Edge Inferencing Fabric Launch Deck",
            "owner": "partner_marketing",
            "updated_at": "2026-04-01",
            "tags": ["helio", "edge", "launch"],
            "summary": "Presentation about HelioSync Edge Inferencing Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "This deck covers HelioSync Edge Inference Fabric performance benchmarks."
        },
        {
            "presentation_id": "PRES-2026-002",
            "title": "Q1 Partner Review",
            "owner": "strategy_team",
            "updated_at": "2026-03-20",
            "tags": ["partner", "review"],
            "summary": "General review, no specific solution.",
            "solution_aliases": [],
            "deck_notes": "Discussed various partnerships, not HelioSync."
        },
        {
            "presentation_id": "PRES-2026-003",
            "title": "Edge Compute Comparison",
            "owner": "research_design",
            "updated_at": "2026-02-28",
            "tags": ["edge", "compute"],
            "summary": "Compares edge solutions, mentions HelioSync only in passing.",
            "solution_aliases": ["HelioSync"],
            "deck_notes": "Contains a slide referencing HelioSync (not full Edge Inference Fabric)."
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # --- data/media_samples ---
    os.makedirs("data/media_samples", exist_ok=True)
    media_samples = [
        {
            "sample_id": "MED-2026-001",
            "title": "HelioSync Edge Inference Fabric Podcast",
            "channel": "podcast_transcript",
            "captured_at": "2026-04-10",
            "tags": ["helio", "edge", "podcast"],
            "summary": "Transcript discussing HelioSync Edge Inference Fabric use cases.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "We talked about HelioSync Edge Inference Fabric enabling real-time inference."
        },
        {
            "sample_id": "MED-2026-002",
            "title": "Industrial IoT Roundtable",
            "channel": "keynote_transcript",
            "captured_at": "2026-03-25",
            "tags": ["iot", "industrial"],
            "summary": "Roundtable not related to HelioSync.",
            "solution_aliases": [],
            "content": "Discussion on general IoT challenges."
        },
        {
            "sample_id": "MED-2026-003",
            "title": "Edge AI Editorial Draft",
            "channel": "editorial_draft",
            "captured_at": "2026-04-05",
            "tags": ["edge", "ai", "draft"],
            "summary": "Draft article mentions HelioSync in a list.",
            "solution_aliases": ["HelioSync"],
            "content": "Several vendors offer edge AI, including HelioSync."
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # --- data/attachments ---
    attachments = [
        {
            "path": "solution_matching_notes.md",
            "title": "Solution Matching Notes",
            "kind": "matching_guide",
            "description": "Guidelines: only documents with solution_aliases containing exact 'HelioSync Edge Inference Fabric' should be considered."
        },
        {
            "path": "temp_record_guidelines.md",
            "title": "Temporary Record Guidelines",
            "kind": "record_schema",
            "description": "Schema for saving temporary records."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # --- create output directory (empty) ---
    os.makedirs("clues", exist_ok=True)

if __name__ == "__main__":
    build_env()
