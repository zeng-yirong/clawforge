import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Reports ---
    reports = [
        {
            "report_id": "report-001",
            "title": "Edge AI Deployment Trends",
            "sector": "industrial_ai",
            "published_at": "2026-02-10",
            "tags": ["edge", "ai", "deployment"],
            "summary": "Analysis of HelioSync deployment patterns in manufacturing.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "NovaCore"],
            "content": "Full report content..."
        },
        {
            "report_id": "report-002",
            "title": "Logistics Automation 2026",
            "sector": "logistics_ai",
            "published_at": "2026-01-15",
            "tags": ["logistics", "automation"],
            "summary": "Report on logistics AI trends.",
            "solution_aliases": ["LogiFusion"],
            "content": "Full report content..."
        },
        {
            "report_id": "report-003",
            "title": "Industrial AI for Manufacturing",
            "sector": "industrial_ai",
            "published_at": "2026-03-01",
            "tags": ["industrial", "ai", "factory"],
            "summary": "HelioSync used in smart factories for predictive maintenance.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Full report content..."
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # --- Presentations ---
    presentations = [
        {
            "presentation_id": "presentation-001",
            "title": "Partner Marketing Q2",
            "owner": "partner_marketing",
            "updated_at": "2026-02-20",
            "tags": ["marketing", "q2"],
            "summary": "Marketing deck for partners.",
            "solution_aliases": ["CloudSync"],
            "deck_notes": "Slide notes..."
        },
        {
            "presentation_id": "presentation-002",
            "title": "HelioSync Product Overview",
            "owner": "strategy_team",
            "updated_at": "2026-03-05",
            "tags": ["helio", "product"],
            "summary": "Overview of HelioSync Edge Inference Fabric features.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Slide notes..."
        },
        {
            "presentation_id": "presentation-003",
            "title": "Robotics Innovations",
            "owner": "research_design",
            "updated_at": "2026-02-28",
            "tags": ["robotics", "innovation"],
            "summary": "Robotics trends survey.",
            "solution_aliases": ["RoboCore"],
            "deck_notes": "Slide notes..."
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # --- Media Samples ---
    media_samples = [
        {
            "sample_id": "media-001",
            "title": "HelioSync Podcast",
            "channel": "podcast_transcript",
            "captured_at": "2026-03-10",
            "tags": ["podcast", "helio"],
            "summary": "Podcast transcript discussing HelioSync Edge Inference Fabric deployment.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Full transcript..."
        },
        {
            "sample_id": "media-002",
            "title": "Keynote - Edge Computing",
            "channel": "keynote_transcript",
            "captured_at": "2026-01-25",
            "tags": ["keynote", "edge"],
            "summary": "Keynote on general edge computing.",
            "solution_aliases": ["EdgeCore"],
            "content": "Full transcript..."
        },
        {
            "sample_id": "media-003",
            "title": "Industrial AI Whitepaper",
            "channel": "editorial_draft",
            "captured_at": "2026-02-14",
            "tags": ["whitepaper", "industrial"],
            "summary": "Whitepaper on industrial AI.",
            "solution_aliases": ["NovaCore"],
            "content": "Full content..."
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # --- Decoy files (not needed for the task) ---
    os.makedirs("data/old_reports", exist_ok=True)
    with open("data/old_reports/2025_archived.json", "w") as f:
        json.dump({"placeholder": True}, f)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

if __name__ == "__main__":
    build_env()
