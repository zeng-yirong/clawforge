import os
import json

def build_env():
    # Create directories
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- reports ----------
    reports = [
        {
            "report_id": "rpt_001",
            "title": "Edge Inference at Scale",
            "sector": "industrial_ai",
            "published_at": "2026-01-15",
            "tags": ["edge", "inference", "HelioSync"],
            "summary": "Evaluates HelioSync Edge Inference Fabric for factory-floor AI deployment.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Full report..."
        },
        {
            "report_id": "rpt_002",
            "title": "Logistics AI Roundup",
            "sector": "logistics_ai",
            "published_at": "2026-02-01",
            "tags": ["logistics", "vision"],
            "summary": "Overview of vision-based sorting systems.",
            "solution_aliases": ["Aurora Vision"],
            "content": "Full report..."
        },
        {
            "report_id": "rpt_003",
            "title": "HelioSync Early Benchmarks",
            "sector": "industrial_ai",
            "published_at": "2025-11-01",
            "tags": ["obsolete", "HelioSync"],
            "summary": "Early benchmarks for HelioSync (pre‑production).",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],  # matches but old version – still a valid clue according to Keiko
            "content": "Benchmark data..."
        }
    ]

    # ---------- presentations ----------
    presentations = [
        {
            "presentation_id": "pres_101",
            "title": "Partner Tech Dive: HelioSync",
            "owner": "partner_marketing",
            "updated_at": "2026-03-10",
            "tags": ["HelioSync", "edge"],
            "summary": "Deep‑dive deck on HelioSync Edge Inference Fabric architecture.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Slides 12-18 cover integration."
        },
        {
            "presentation_id": "pres_102",
            "title": "Robotics Vision Update",
            "owner": "research_design",
            "updated_at": "2026-02-20",
            "tags": ["robotics", "vision"],
            "summary": "New camera module for pick‑and‑place.",
            "solution_aliases": ["RoboVision"],
            "deck_notes": "No HelioSync content."
        }
    ]

    # ---------- media samples ----------
    media_samples = [
        {
            "sample_id": "med_201",
            "title": "Podcast: Edge AI Outlook",
            "channel": "podcast_transcript",
            "captured_at": "2026-03-01",
            "tags": ["edge", "AI", "HelioSync"],
            "summary": "Interview discussing HelioSync Edge Inference Fabric market positioning.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Transcript..."
        },
        {
            "sample_id": "med_202",
            "title": "Keynote: Industrial Digital Twins",
            "channel": "keynote_transcript",
            "captured_at": "2026-01-25",
            "tags": ["digital twin", "industrial"],
            "summary": "Keynote on simulation platforms.",
            "solution_aliases": ["SimCore"],
            "content": "Transcript..."
        }
    ]

    # Write index files
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # ---------- extra attachments (distractor) ----------
    attachments = [
        {
            "path": "solution_matching_notes.md",
            "title": "Solution Matching Notes",
            "kind": "matching_guide",
            "description": "Internal guide for alias matching – not a source of clues."
        },
        {
            "path": "temp_record_guidelines.md",
            "title": "Temporary Record Guidelines",
            "kind": "record_schema",
            "description": "Schema for clue list output."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # Create empty placeholder files to show they exist
    with open("data/solution_matching_notes.md", "w") as f:
        f.write("# Solution Matching Notes\nDo not treat this file as a clue source.\n")
    with open("data/temp_record_guidelines.md", "w") as f:
        f.write("# Temporary Record Guidelines\nClue list schema: ...\n")

if __name__ == "__main__":
    build_env()
