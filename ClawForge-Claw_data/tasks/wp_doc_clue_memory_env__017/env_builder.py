import os
import json
import random

def build_env():
    target_alias = "HelioSync Edge Inference Fabric"
    
    # --- Reports ---
    reports_dir = "data/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    reports = [
        {
            "report_id": "R-001",
            "title": "Q2 Industrial AI Report",
            "sector": "industrial_ai",
            "published_at": "2026-05-15",
            "tags": ["edge", "inference", "manufacturing"],
            "summary": "Adoption of HelioSync Edge Inference Fabric in manufacturing reduced latency by 40%.",
            "solution_aliases": [target_alias],
            "content": "Full report content..."
        },
        {
            "report_id": "R-002",
            "title": "Logistics AI Trends",
            "sector": "logistics_ai",
            "published_at": "2026-04-20",
            "tags": ["edge", "logistics"],
            "summary": "Logistics firms are testing HelioSync Edge for real-time tracking.",
            "solution_aliases": ["HelioSync Edge"],
            "content": "..."
        },
        {
            "report_id": "R-003",
            "title": "Robotics Innovations",
            "sector": "robotics",
            "published_at": "2026-03-10",
            "tags": ["robotics", "inference"],
            "summary": "Edge Inference Fabric is gaining traction in autonomous robots.",
            "solution_aliases": ["Edge Inference Fabric"],
            "content": "..."
        },
        {
            "report_id": "R-004",
            "title": "Industrial AI Overview",
            "sector": "industrial_ai",
            "published_at": "2025-12-01",
            "tags": ["industrial", "ai"],
            "summary": "V2 of HelioSync Edge Inference Fabric v2 promises lower power draw.",
            "solution_aliases": ["HelioSync Edge Inference Fabric v2"],
            "content": "..."
        },
        {
            "report_id": "R-005",
            "title": "Market Analysis",
            "sector": "logistics_ai",
            "published_at": "2026-06-01",
            "tags": ["market", "helio"],
            "summary": "HelioSync is just a brand name, not the full stack.",
            "solution_aliases": ["HelioSync"],
            "content": "..."
        }
    ]
    with open(os.path.join(reports_dir, "reports.json"), "w") as f:
        json.dump(reports, f, indent=2)
    
    # corrupted report file (invalid json)
    with open(os.path.join(reports_dir, "corrupted_report.json"), "w") as f:
        f.write("{this is not valid json")
    
    # --- Presentations ---
    pres_dir = "data/presentations"
    os.makedirs(pres_dir, exist_ok=True)
    
    presentations = [
        {
            "presentation_id": "P-001",
            "title": "HelioSync Edge Inference Fabric Deck",
            "owner": "strategy_team",
            "updated_at": "2026-05-22",
            "tags": ["edge", "inference", "fabric"],
            "summary": "Deck highlights deployment architecture for HelioSync Edge Inference Fabric.",
            "solution_aliases": [target_alias],
            "deck_notes": "Includes network topology diagrams."
        },
        {
            "presentation_id": "P-002",
            "title": "Partner Marketing Q3",
            "owner": "partner_marketing",
            "updated_at": "2026-04-10",
            "tags": ["marketing", "partners"],
            "summary": "Partner collaterals focus on HelioSync branding.",
            "solution_aliases": ["HelioSync"],
            "deck_notes": "No technical details."
        },
        {
            "presentation_id": "P-003",
            "title": "Research Design Review",
            "owner": "research_design",
            "updated_at": "2026-02-28",
            "tags": ["research", "edge"],
            "summary": "Edge Inference design patterns for low latency.",
            "solution_aliases": ["Edge Inference"],
            "deck_notes": "Early stage concepts."
        }
    ]
    with open(os.path.join(pres_dir, "presentations.json"), "w") as f:
        json.dump(presentations, f, indent=2)
    
    # corrupted presentation file
    with open(os.path.join(pres_dir, "broken_pres.json"), "w") as f:
        f.write("Not JSON at all")
    
    # --- Media Samples ---
    media_dir = "data/media_samples"
    os.makedirs(media_dir, exist_ok=True)
    
    media_samples = [
        {
            "sample_id": "M-001",
            "title": "Podcast: HelioSync Edge Inference Fabric",
            "channel": "podcast_transcript",
            "captured_at": "2026-06-05T14:30:00Z",
            "tags": ["podcast", "edge", "inference"],
            "summary": "Podcast discusses the impact of HelioSync Edge Inference Fabric on edge computing.",
            "solution_aliases": [target_alias],
            "content": "Transcript of the podcast..."
        },
        {
            "sample_id": "M-002",
            "title": "Keynote Transcript",
            "channel": "keynote_transcript",
            "captured_at": "2026-05-18T09:00:00Z",
            "tags": ["keynote", "helio"],
            "summary": "Keynote mentions HelioSync briefly.",
            "solution_aliases": ["HelioSync"],
            "content": "..."
        },
        {
            "sample_id": "M-003",
            "title": "Editorial Draft",
            "channel": "editorial_draft",
            "captured_at": "2026-04-22T11:15:00Z",
            "tags": ["draft", "edge"],
            "summary": "Draft article covers Edge Inference Fabric but not the HelioSync brand.",
            "solution_aliases": ["Edge Inference Fabric"],
            "content": "..."
        }
    ]
    with open(os.path.join(media_dir, "media_samples.json"), "w") as f:
        json.dump(media_samples, f, indent=2)
    
    # corrupted media file
    with open(os.path.join(media_dir, "corrupted_media.json"), "w") as f:
        f.write("{\"garbage")
    
    # Also create a few decoy directories with unrelated files
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)
    with open("data/accounts/accounts.json", "w") as f:
        json.dump([], f)
    with open("data/temp/notes.txt", "w") as f:
        f.write("some notes")

if __name__ == "__main__":
    build_env()
