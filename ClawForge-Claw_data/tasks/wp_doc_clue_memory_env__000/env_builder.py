import os
import json

def build_env():
    # Create directory structure
    for d in ["data/reports", "data/presentations", "data/media_samples"]:
        os.makedirs(d, exist_ok=True)

    # --- Reports ---
    reports = {
        "reports": [
            {
                "report_id": "RPT-2026-0031",
                "title": "Edge Inference at Scale",
                "sector": "industrial_ai",
                "published_at": "2026-02-14",
                "tags": ["edge", "inference", "fabric"],
                "summary": "HelioSync Edge Inference Fabric reduces latency by 40% in factory-floor deployments.",
                "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF"],
                "content": "Deep dive into edge inference performance..."
            },
            {
                "report_id": "RPT-2026-0029",
                "title": "Edge Inference Trends",
                "sector": "industrial_ai",
                "published_at": "2026-01-20",
                "tags": ["edge", "inference"],
                "summary": "Overview of HelioSync Edge Inference architecture without fabric layer.",
                "solution_aliases": ["HelioSync Edge Inference"],
                "content": "Trends in edge computing..."
            },
            {
                "report_id": "RPT-2026-0030",
                "title": "Fabric Deployments Q1",
                "sector": "industrial_ai",
                "published_at": "2026-01-30",
                "tags": ["fabric", "deployment"],
                "summary": "Analysis of HelioSync Edge Infernce Fabric (typo) in production.",
                "solution_aliases": ["HelioSync Edge Infernce Fabric"],
                "content": "Deployment metrics..."
            },
            {
                "report_id": "RPT-2026-0032",
                "title": "Logistics AI 2026 Outlook",
                "sector": "logistics_ai",
                "published_at": "2026-03-01",
                "tags": ["logistics"],
                "summary": "Global logistics AI market forecast.",
                "solution_aliases": ["LogiSync Optimizer"],
                "content": "Market sizing..."
            }
        ]
    }
    with open("data/reports/reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    # --- Presentations ---
    presentations = {
        "presentations": [
            {
                "presentation_id": "PRES-2026-0022",
                "title": "HelioSync Fabric Deep Dive",
                "owner": "partner_marketing",
                "updated_at": "2026-02-28",
                "tags": ["fabric", "deep-dive"],
                "summary": "Technical deep dive into HelioSync Edge Inference Fabric architecture.",
                "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF"],
                "deck_notes": "Includes performance benchmarks."
            },
            {
                "presentation_id": "PRES-2026-0021",
                "title": "Edge Inference Overview",
                "owner": "research_design",
                "updated_at": "2026-02-10",
                "tags": ["edge", "overview"],
                "summary": "General edge inference landscape.",
                "solution_aliases": ["HelioSync Edge Inference"],
                "deck_notes": "No fabric focus."
            },
            {
                "presentation_id": "PRES-2026-0023",
                "title": "Robotics Platform Update",
                "owner": "strategy_team",
                "updated_at": "2026-03-05",
                "tags": ["robotics"],
                "summary": "New robotics SDK capabilities.",
                "solution_aliases": ["RoboCore"],
                "deck_notes": "No HelioSync reference."
            }
        ]
    }
    with open("data/presentations/presentations.json", "w") as f:
        json.dump(presentations, f, indent=2)

    # --- Media Samples ---
    media_samples = {
        "media_samples": [
            {
                "sample_id": "SMPL-2026-0014",
                "title": "Podcast: Edge Inference Revolution",
                "channel": "podcast_transcript",
                "captured_at": "2026-02-21",
                "tags": ["edge", "podcast"],
                "summary": "Discussion on HelioSync Edge Inference Fabric and its impact on logistics.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "Full transcript..."
            },
            {
                "sample_id": "SMPL-2026-0013",
                "title": "Keynote: Next-Gen Edge",
                "channel": "keynote_transcript",
                "captured_at": "2026-02-15",
                "tags": ["keynote"],
                "summary": "Keynote on HelioSync Edge Inference (no fabric).",
                "solution_aliases": ["HelioSync Edge Inference"],
                "content": "Keynote transcript..."
            },
            {
                "sample_id": "SMPL-2026-0015",
                "title": "Editorial Draft: Fabric Use Cases",
                "channel": "editorial_draft",
                "captured_at": "2026-02-25",
                "tags": ["fabric"],
                "summary": "Use cases for HelioSync Edge Infernce Fabric (typo).",
                "solution_aliases": ["HelioSync Edge Infernce Fabric"],
                "content": "Draft content..."
            }
        ]
    }
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump(media_samples, f, indent=2)

if __name__ == "__main__":
    build_env()
