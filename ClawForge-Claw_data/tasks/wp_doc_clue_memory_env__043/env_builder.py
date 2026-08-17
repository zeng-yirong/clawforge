import os
import json

def build_env():
    # Ensure base data directories
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # Add a decoy directory
    os.makedirs("data/old_reports", exist_ok=True)

    # ----- Reports -----
    reports = [
        {
            "report_id": "R-2026-001",
            "title": "Edge AI Deployment Patterns in Logistics",
            "sector": "logistics_ai",
            "published_at": "2026-02-15",
            "tags": ["edge", "inference", "logistics"],
            "summary": "Explores real‑time inference at the edge for warehouse robots.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF"],
            "content": "..."
        },
        {
            "report_id": "R-2026-002",
            "title": "Industrial Robotics: 2026 Outlook",
            "sector": "industrial_ai",
            "published_at": "2026-01-20",
            "tags": ["robotics", "vision"],
            "summary": "General overview of industrial robots.",
            "solution_aliases": ["HelioSync Edge", "HE"],   # partial match – should NOT be selected
            "content": "..."
        },
        {
            "report_id": "R-2026-003",
            "title": "Edge Inference at Scale for Smart Warehouses",
            "sector": "logistics_ai",
            "published_at": "2026-03-01",
            "tags": ["edge", "inference", "warehouse"],
            "summary": "Case studies on HelioSync Edge Inference Fabric deployments.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF-cluster"],
            "content": "..."
        },
        {
            "report_id": "R-2026-004",
            "title": "Last‑Mile Delivery Drones",
            "sector": "logistics_ai",
            "published_at": "2026-04-10",
            "tags": ["drones"],
            "summary": "Drone routing algorithms.",
            "solution_aliases": ["AerialSync"],   # no match
            "content": "..."
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f)

    # ----- Presentations -----
    presentations = [
        {
            "presentation_id": "PPT-2026-001",
            "title": "Partner Marketing Q2 Deck",
            "owner": "partner_marketing",
            "updated_at": "2026-03-15",
            "tags": ["partnership", "go-to-market"],
            "summary": "Quarterly partner update.",
            "solution_aliases": ["Heliosync Edge Inference Fabric"],   # casing mismatch (lowercase 's') – should NOT match
            "deck_notes": "..."
        },
        {
            "presentation_id": "PPT-2026-002",
            "title": "HelioSync Fabric Technical Overview",
            "owner": "research_design",
            "updated_at": "2026-02-28",
            "tags": ["edge", "inference", "fabric"],
            "summary": "Deep dive into HelioSync Edge Inference Fabric architecture.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF-arch"],
            "deck_notes": "..."
        },
        {
            "presentation_id": "PPT-2026-003",
            "title": "Strategy Roadmap 2026",
            "owner": "strategy_team",
            "updated_at": "2026-01-10",
            "tags": ["strategy"],
            "summary": "Company‑wide strategy.",
            "solution_aliases": ["HelioSync Edge Inference"],   # missing "Fabric" – should NOT match
            "deck_notes": "..."
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f)

    # ----- Media Samples -----
    media_samples = [
        {
            "sample_id": "MS-2026-001",
            "title": "Keynote: Edge AI Revolution",
            "channel": "keynote_transcript",
            "captured_at": "2026-03-20",
            "tags": ["edge", "keynote"],
            "summary": "CEO announces HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF"],
            "content": "..."
        },
        {
            "sample_id": "MS-2026-002",
            "title": "Podcast: Robotics in 2026",
            "channel": "podcast_transcript",
            "captured_at": "2026-02-01",
            "tags": ["podcast"],
            "summary": "Discussion on general robotics trends.",
            "solution_aliases": ["RoboCore"],   # no match
            "content": "..."
        },
        {
            "sample_id": "MS-2026-003",
            "title": "Editorial: Edge vs Cloud",
            "channel": "editorial_draft",
            "captured_at": "2026-04-05",
            "tags": ["edge", "cloud"],
            "summary": "Comparison of edge and cloud inference.",
            "solution_aliases": ["HelioSync Edge"],   # partial – should NOT match
            "content": "..."
        },
        {
            "sample_id": "MS-2026-004",
            "title": "Podcast: HelioSync Fabric Deep Dive",
            "channel": "podcast_transcript",
            "captured_at": "2026-03-25",
            "tags": ["podcast", "fabric"],
            "summary": "Engineers walk through HelioSync Edge Inference Fabric internals.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "..."
        },
        # Decoy with exact alias but from wrong channel – still valid
        {
            "sample_id": "MS-2026-005",
            "title": "B‑roll footage notes",
            "channel": "editorial_draft",
            "captured_at": "2026-01-15",
            "tags": ["b-roll"],
            "summary": "Notes from B‑roll shoot; not used.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "..."
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f)

    # ----- Decoy files to clutter the environment -----
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": []}, f)   # empty, not relevant
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

    # Old reports with similar name structure
    old_report = {
        "report_id": "OLD-R-2025-009",
        "title": "Legacy Edge Inference Report",
        "solution_aliases": ["HelioSync Edge Inference Fabric (deprecated)"],
        "summary": "Old version."
    }
    with open("data/old_reports/old_report.json", "w") as f:
        json.dump(old_report, f)

if __name__ == "__main__":
    build_env()
