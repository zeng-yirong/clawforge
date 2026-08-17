import os
import json

def build_env():
    # Create required directories
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    target = "HelioSync Edge Inference Fabric"

    # --- Reports ---
    reports = [
        {
            "report_id": "rpt-001",
            "title": "Q2 2026 Edge Inference Forecast",
            "sector": "industrial_ai",
            "published_at": "2026-05-15",
            "tags": ["edge", "inference", "forecast"],
            "summary": "HelioSync Edge Inference Fabric will lead the market in low-latency AI inference at the edge.",
            "solution_aliases": [target],
            "content": "Detailed forecast ..."
        },
        {
            "report_id": "rpt-002",
            "title": "Industrial AI Summit Recap",
            "sector": "industrial_ai",
            "published_at": "2026-06-01",
            "tags": ["summit", "AI"],
            "summary": "Keynotes highlighted HelioSync Edge Inference Fabric as a game-changer for factory automation.",
            "solution_aliases": [target],
            "content": "Summit highlights ..."
        },
        {
            "report_id": "rpt-003",
            "title": "HelioSync Edge Overview",
            "sector": "industrial_ai",
            "published_at": "2025-12-01",
            "tags": ["heliosync", "edge"],
            "summary": "Covers HelioSync Edge platform without Inference Fabric.",
            "solution_aliases": ["HelioSync Edge"],   # wrong variant
            "content": "..."
        },
        {
            "report_id": "rpt-004",
            "title": "Logistics Robotics 2026",
            "sector": "logistics_ai",
            "published_at": "2026-02-20",
            "tags": ["logistics", "robotics"],
            "summary": "Focus on warehouse automation.",
            "solution_aliases": ["WarehouseBot"],
            "content": "..."
        },
        {
            "report_id": "rpt-005",
            "title": "Deprecated Report",
            "sector": "robotics",
            "published_at": "2024-01-01",
            "tags": [],
            "summary": "Old report with missing aliases.",
            "solution_aliases": None,   # dirty data
            "content": "..."
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f)

    # --- Presentations ---
    presentations = [
        {
            "presentation_id": "pst-001",
            "title": "HelioSync Edge Fabric Overview",
            "owner": "partner_marketing",
            "updated_at": "2026-04-10",
            "tags": ["heliosync", "edge", "fabric"],
            "summary": "Introducing HelioSync Edge Inference Fabric for partners.",
            "solution_aliases": [target],
            "deck_notes": "partner slides"
        },
        {
            "presentation_id": "pst-002",
            "title": "Partner Enablement Deck 2026",
            "owner": "strategy_team",
            "updated_at": "2026-05-20",
            "tags": ["enablement"],
            "summary": "Includes section on HelioSync Edge Inference Fabric deployment.",
            "solution_aliases": [target],
            "deck_notes": "deployment guide"
        },
        {
            "presentation_id": "pst-003",
            "title": "HelioSync Edge Inference (Old)",
            "owner": "research_design",
            "updated_at": "2025-08-15",
            "tags": ["heliosync"],
            "summary": "Mentions HelioSync Edge Inference but not Fabric.",
            "solution_aliases": ["HelioSync Edge Inference"],   # wrong variant
            "deck_notes": "old"
        },
        {
            "presentation_id": "pst-004",
            "title": "Robotics Market Overview",
            "owner": "partner_marketing",
            "updated_at": "2026-01-01",
            "tags": ["robotics"],
            "summary": "No HelioSync.",
            "solution_aliases": ["AvaBot"],
            "deck_notes": ""
        },
        {
            "presentation_id": "pst-005",
            "title": "Misc Presentation",
            "owner": "strategy_team",
            "updated_at": "2026-03-01",
            "tags": [],
            "summary": "This presentation has malformed aliases.",
            "solution_aliases": target,   # string instead of list (dirty)
            "deck_notes": "corrupted"
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f)

    # --- Media Samples ---
    media_samples = [
        {
            "sample_id": "med-001",
            "title": "Podcast: Edge AI Revolution",
            "channel": "podcast_transcript",
            "captured_at": "2026-05-30",
            "tags": ["edge", "ai", "podcast"],
            "summary": "Discussion on HelioSync Edge Inference Fabric and its impact.",
            "solution_aliases": [target],
            "content": "..."
        },
        {
            "sample_id": "med-002",
            "title": "Keynote Transcript: HelioSync Launch",
            "channel": "keynote_transcript",
            "captured_at": "2026-03-15",
            "tags": ["launch", "heliosync"],
            "summary": "Focuses on HelioSync Edge platform, not Inference Fabric.",
            "solution_aliases": ["HelioSync Edge"],   # wrong variant
            "content": "..."
        },
        {
            "sample_id": "med-003",
            "title": "Editorial Draft - AI Trends",
            "channel": "editorial_draft",
            "captured_at": "2026-06-01",
            "tags": ["ai"],
            "summary": "Missing solution_aliases field.",
            "content": "..."
        }
    ]
    # med-003 intentionally lacks solution_aliases (dirty)
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f)

    # --- Attachments ---
    attachments = [
        {
            "path": "data/attachments/solution_matching_notes.md",
            "title": "Solution Matching Notes",
            "kind": "matching_guide",
            "description": "Notes on which documents to include."
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f)

    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write("Some notes about matching: check rpt-001 and pst-002.\n")

if __name__ == "__main__":
    build_env()
