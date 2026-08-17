import os
import json
import random

def build_env():
    # --- reports ---
    reports_dir = "data/reports"
    os.makedirs(reports_dir, exist_ok=True)
    reports = [
        {
            "report_id": "RPT-001",
            "title": "Industrial Edge Deployments Q1 Summary",
            "sector": "industrial_ai",
            "published_at": "2026-02-15",
            "tags": ["edge", "inference", "helio"],
            "summary": "Analysis of HelioSync Edge Inference Fabric adoption in manufacturing.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HelioSync EI"],
            "content": "Deployment case studies show 40% latency reduction..."
        },
        {
            "report_id": "RPT-002",
            "title": "Logistics AI White Paper",
            "sector": "logistics_ai",
            "published_at": "2026-01-20",
            "tags": ["logistics", "AI"],
            "summary": "Overview of AI in logistics, mentions HelioSync for routing.",
            "solution_aliases": ["HelioSync Lite", "LogiSync"],
            "content": "HelioSync Lite provides basic routing optimization..."
        },
        {
            "report_id": "RPT-003",
            "title": "Robotics Inference Benchmark",
            "sector": "robotics",
            "published_at": "2026-03-01",
            "tags": ["robotics", "inference"],
            "summary": "Benchmark of Edge Inference engines for robotics.",
            "solution_aliases": ["Edge Inference Fabric", "Helio"],
            "content": "Comparing various edge inference platforms..."
        },
        {
            "report_id": "RPT-004",
            "title": "HelioSync Edge Field Trial",
            "sector": "industrial_ai",
            "published_at": "2026-02-28",
            "tags": ["helio", "edge", "field"],
            "summary": "Field trial results for HelioSync Edge Inference Fabric in factory settings.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "The fabric demonstrated 99.97% uptime over 30 days..."
        }
    ]
    with open(os.path.join(reports_dir, "reports.json"), "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # --- presentations ---
    pres_dir = "data/presentations"
    os.makedirs(pres_dir, exist_ok=True)
    presentations = [
        {
            "presentation_id": "PRES-101",
            "title": "Partner Marketing Deck Q2",
            "owner": "partner_marketing",
            "updated_at": "2026-03-10",
            "tags": ["marketing", "helio"],
            "summary": "Deck highlighting HelioSync Edge Inference Fabric for partners.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF"],
            "deck_notes": "Slide 7 contains flagship diagram."
        },
        {
            "presentation_id": "PRES-102",
            "title": "Edge AI Research Overview",
            "owner": "research_design",
            "updated_at": "2026-02-20",
            "tags": ["research", "edge"],
            "summary": "Overview of edge AI research including Edge Inference Fabric.",
            "solution_aliases": ["Edge Inference Fabric"],
            "deck_notes": "Focus on model compression."
        },
        {
            "presentation_id": "PRES-103",
            "title": "Strategy Roadmap 2026",
            "owner": "strategy_team",
            "updated_at": "2026-01-15",
            "tags": ["strategy", "helio"],
            "summary": "Strategic roadmap with HelioSync Edge as key platform.",
            "solution_aliases": ["HelioSync Edge", "HelioSync Edge Inference"],
            "deck_notes": "Pages 12-15 detail the edge rollout."
        }
    ]
    with open(os.path.join(pres_dir, "presentations.json"), "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # --- media samples ---
    media_dir = "data/media_samples"
    os.makedirs(media_dir, exist_ok=True)
    samples = [
        {
            "sample_id": "MED-201",
            "title": "TechDay Keynote Transcript",
            "channel": "keynote_transcript",
            "captured_at": "2026-03-05T10:00:00Z",
            "tags": ["keynote", "helio"],
            "summary": "Keynote introducing HelioSync Edge Inference Fabric to developers.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Today we unveil the HelioSync Edge Inference Fabric..."
        },
        {
            "sample_id": "MED-202",
            "title": "Podcast: Edge AI Roundtable",
            "channel": "podcast_transcript",
            "captured_at": "2026-02-22T14:30:00Z",
            "tags": ["podcast", "edge"],
            "summary": "Discussion about edge inference challenges, mentions HelioSync briefly.",
            "solution_aliases": ["HelioSync", "Edge AI"],
            "content": "HelioSync is one of the contenders in edge inference..."
        },
        {
            "sample_id": "MED-203",
            "title": "Editorial Draft: HelioSync Deep Dive",
            "channel": "editorial_draft",
            "captured_at": "2026-03-12T08:00:00Z",
            "tags": ["draft", "helio"],
            "summary": "Draft article covering HelioSync Edge Inference Fabric architecture.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HelioSync"],
            "content": "The fabric's distributed architecture enables sub-millisecond inference..."
        }
    ]
    with open(os.path.join(media_dir, "media_samples.json"), "w") as f:
        json.dump({"media_samples": samples}, f, indent=2)

    # --- pre-create ops/ empty (will be created by agent if needed) ---
    ops_dir = "ops"
    os.makedirs(ops_dir, exist_ok=True)

if __name__ == "__main__":
    build_env()
