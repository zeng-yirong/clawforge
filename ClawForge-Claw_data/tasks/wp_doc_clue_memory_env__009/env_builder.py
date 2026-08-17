import os, json

def build_env():
    # Create directory structure
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty dir for output

    # --- reports.json ---
    reports = {
        "reports": [
            {
                "report_id": "rpt-001",
                "title": "Industrial AI Market Trends Q1",
                "sector": "industrial_ai",
                "published_at": "2025-03-01",
                "tags": ["AI", "edge"],
                "summary": "Overview of AI adoption in factories.",
                "solution_aliases": ["Nexus Core AI Platform"],
                "content": "Detailed report...",
                "status": "published"
            },
            {
                "report_id": "rpt-002",
                "title": "Logistics Robotics Outlook",
                "sector": "logistics_ai",
                "published_at": "2025-04-10",
                "tags": ["robotics"],
                "summary": "Robotics in warehouse automation.",
                "solution_aliases": [],
                "content": "Content...",
                "status": "draft"
            },
            {
                "report_id": "rpt-003",
                "title": "Edge Computing for Manufacturing",
                "sector": "industrial_ai",
                "published_at": "2025-05-20",
                "tags": ["edge", "manufacturing"],
                "summary": "HelioSync Edge Inference Fabric reduces latency by 40% in edge deployments. Highly recommended for real-time control.",
                "solution_aliases": ["HelioSync Edge Inference Fabric", "Nexus Core"],
                "content": "Full report...",
                "status": "draft"
            },
            {
                "report_id": "rpt-004",
                "title": "AI at the Edge 2025",
                "sector": "industrial_ai",
                "published_at": "2025-06-01",
                "tags": ["edge", "AI"],
                "summary": "Comparison of edge AI platforms.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "Content...",
                "status": "published"
            }
        ]
    }
    with open("data/reports/reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    # --- presentations.json ---
    presentations = {
        "presentations": [
            {
                "presentation_id": "prs-001",
                "title": "Partner Marketing Deck Q2",
                "owner": "partner_marketing",
                "updated_at": "2025-02-15",
                "tags": ["marketing"],
                "summary": "General partner strategy.",
                "solution_aliases": ["Nexus Core AI Platform"],
                "deck_notes": "Notes...",
                "status": "published"
            },
            {
                "presentation_id": "prs-002",
                "title": "Research Design – Edge Solutions",
                "owner": "research_design",
                "updated_at": "2025-03-20",
                "tags": ["edge", "research"],
                "summary": "HelioSync Edge Inference Fabric enables real-time video analytics at the edge. Key architecture overview.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "deck_notes": "Detailed architecture...",
                "status": "draft"
            },
            {
                "presentation_id": "prs-003",
                "title": "Strategy Team – Edge AI Rollout",
                "owner": "strategy_team",
                "updated_at": "2025-04-28",
                "tags": ["strategy", "edge"],
                "summary": "HelioSync Edge Inference Fabric enables real-time video analytics at the edge. deployment plan included.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "deck_notes": "Deployment timeline...",
                "status": "published"
            }
        ]
    }
    with open("data/presentations/presentations.json", "w") as f:
        json.dump(presentations, f, indent=2)

    # --- media_samples.json ---
    media_samples = {
        "media_samples": [
            {
                "sample_id": "med-001",
                "title": "Editorial: AI in Logistics",
                "channel": "editorial_draft",
                "captured_at": "2025-04-01",
                "tags": ["logistics"],
                "summary": "Discussion on AI trends.",
                "solution_aliases": ["Nexus Core AI Platform"],
                "content": "Content...",
                "status": "published"
            },
            {
                "sample_id": "med-002",
                "title": "Keynote: HelioSync Launch",
                "channel": "keynote_transcript",
                "captured_at": "2025-05-10",
                "tags": ["launch", "edge"],
                "summary": "HelioSync Edge Inference Fabric reduces latency by 40% in edge deployments.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "Full transcript...",
                "status": "draft"
            },
            {
                "sample_id": "med-003",
                "title": "Podcast: Edge AI Realities",
                "channel": "podcast_transcript",
                "captured_at": "2025-06-05",
                "tags": ["podcast", "edge"],
                "summary": "Guest discusses challenges of edge AI.",
                "solution_aliases": ["Nexus Core AI Platform"],
                "content": "Transcript...",
                "status": "published"
            },
            {
                "sample_id": "med-004",
                "title": "Podcast: HelioSync Manufacturing",
                "channel": "podcast_transcript",
                "captured_at": "2025-06-20",
                "tags": ["podcast", "manufacturing", "edge"],
                "summary": "Podcast discussion on deploying HelioSync Edge Inference Fabric in manufacturing environments. Key takeaway: reduced latency and real-time control.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "Full podcast transcript...",
                "status": "published"
            }
        ]
    }
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump(media_samples, f, indent=2)

if __name__ == "__main__":
    build_env()
