import os
import json

def build_env():
    # ---------- reports ----------
    reports_data = [
        {
            "report_id": "RPT-2026-001",
            "title": "Industrial AI Q2 Forecast",
            "sector": "industrial_ai",
            "published_at": "2026-02-15",
            "tags": ["edge", "inference"],
            "summary": "Covers edge inference growth.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HelioSync Fabric"],
            "content": "..."  # placeholder
        },
        {
            "report_id": "RPT-2026-002",
            "title": "Logistics Automation Review",
            "sector": "logistics_ai",
            "published_at": "2026-03-01",
            "tags": ["automation"],
            "summary": "Focuses on warehouse robotics.",
            "solution_aliases": ["WareBrain AI", "HelioSync Edge Inference Fabric"],
            "content": "..."
        },
        {
            "report_id": "RPT-2026-003",
            "title": "Robotics & Edge Synergy",
            "sector": "robotics",
            "published_at": "2026-03-10",
            "tags": ["edge", "robotics"],
            "summary": "Discusses edge deployment.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "..."
        },
        {
            "report_id": "RPT-2026-004",
            "title": "Edge Computing 2025 Recap",
            "sector": "industrial_ai",
            "published_at": "2025-12-20",
            "tags": ["edge"],
            "summary": "Summary of last year.",
            "solution_aliases": [],  # empty – should be skipped
            "content": "..."
        },
        {
            "report_id": "RPT-2026-005",
            "title": "HelioSync Fabric Deep Dive",
            "sector": "industrial_ai",
            "published_at": "2026-04-01",
            "tags": ["HelioSync"],
            "summary": "Detailed analysis.",
            "solution_aliases": None,  # missing – skip
            "content": "..."
        }
    ]
    os.makedirs("data/reports", exist_ok=True)
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports_data}, f, indent=2)

    # ---------- presentations ----------
    presentations_data = [
        {
            "presentation_id": "PRES-2026-001",
            "title": "Partner Marketing Deck Q1",
            "owner": "partner_marketing",
            "updated_at": "2026-01-20",
            "tags": ["marketing"],
            "summary": "Overview of partnerships.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HelioSync Fabric"],
            "deck_notes": "Slide 5 mentions edge."  # placeholder
        },
        {
            "presentation_id": "PRES-2026-002",
            "title": "Research Design Workshop",
            "owner": "research_design",
            "updated_at": "2026-02-10",
            "tags": ["research", "edge"],
            "summary": "Design principles.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "..."
        },
        {
            "presentation_id": "PRES-2026-003",
            "title": "Strategy Team Offsite",
            "owner": "strategy_team",
            "updated_at": "2026-03-05",
            "tags": ["strategy"],
            "summary": "Long-term roadmap.",
            "solution_aliases": ["SomeOtherSolution"],  # no HelioSync
            "deck_notes": "..."
        },
        # duplicate ID but last occurrence should be taken? No, presentations have unique IDs in this sample.
    ]
    os.makedirs("data/presentations", exist_ok=True)
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations_data}, f, indent=2)

    # ---------- media samples ----------
    # Two entries with the same sample_id "MED-2026-001" – keep the second (last)
    media_samples_data = [
        {
            "sample_id": "MED-2026-001",
            "title": "HelioSync Edge Interview",
            "channel": "podcast_transcript",
            "captured_at": "2026-02-01",
            "tags": ["podcast"],
            "summary": "Interview with CTO.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "..."
        },
        {
            "sample_id": "MED-2026-001",  # duplicate ID (older version)
            "title": "HelioSync Edge Interview (revised)",
            "channel": "podcast_transcript",
            "captured_at": "2026-02-10",
            "tags": ["podcast", "revised"],
            "summary": "Revised transcript.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "..."
        },
        {
            "sample_id": "MED-2026-002",
            "title": "Keynote – AI at Scale",
            "channel": "keynote_transcript",
            "captured_at": "2026-03-15",
            "tags": ["keynote"],
            "summary": "Keynote speech.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "..."
        },
        {
            "sample_id": "MED-2026-003",
            "title": "Editorial Draft – Edge Trends",
            "channel": "editorial_draft",
            "captured_at": "2026-04-01",
            "tags": ["editorial"],
            "summary": "Draft article.",
            "solution_aliases": ["EdgeSync"],  # different alias – no HelioSync
            "content": "..."
        }
    ]
    os.makedirs("data/media_samples", exist_ok=True)
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples_data}, f, indent=2)

    # ---------- attachments ----------
    attachments_data = [
        {
            "path": "attachments/solution_matching_notes.md",
            "title": "Solution Matching Notes",
            "kind": "matching_guide",
            "description": "Maps document IDs to clue IDs for HelioSync Edge Inference Fabric."
        },
        {
            "path": "attachments/temp_record_guidelines.md",
            "title": "Temporary Record Guidelines",
            "kind": "record_schema",
            "description": "Schema for temporary clue records (not used here)."
        }
    ]
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments_data}, f, indent=2)

    # ---------- actual attachment files ----------
    mapping_content = """# Solution Matching Notes – HelioSync Edge Inference Fabric

## Reports
RPT-2026-001 -> HSEIF-REP-001
RPT-2026-002 -> HSEIF-REP-002
RPT-2026-003 -> HSEIF-REP-003

## Presentations
PRES-2026-001 -> HSEIF-PRES-001
PRES-2026-002 -> HSEIF-PRES-002

## Media Samples
MED-2026-001 -> HSEIF-MED-001
MED-2026-002 -> HSEIF-MED-002
"""
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write(mapping_content)

    guidelines_content = """# Temporary Record Guidelines
This file defines the schema for temporary clue records. Not relevant for the current task.
"""
    with open("data/attachments/temp_record_guidelines.md", "w") as f:
        f.write(guidelines_content)

if __name__ == "__main__":
    build_env()
