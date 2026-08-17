import os
import json

def build_env():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # ---------- Reports ----------
    reports = [
        {
            "report_id": "RPT-2026-001",
            "title": "Edge Computing in Industrial AI: A Q2 Assessment",
            "sector": "industrial_ai",
            "published_at": "2026-04-15",
            "tags": ["edge", "industrial", "low-latency"],
            "summary": "Evaluates edge inference solutions for factory floors.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HelioSync"],
            "content": (
                "HelioSync Edge Inference Fabric delivers sub-10ms inference latency "
                "on commodity hardware, making it ideal for real-time quality inspection."
            )
        },
        {
            "report_id": "RPT-2026-002",
            "title": "Logistics AI Forecast 2026",
            "sector": "logistics_ai",
            "published_at": "2026-03-22",
            "tags": ["logistics", "automation"],
            "summary": "High-level trends in AI for supply chain.",
            "solution_aliases": ["EdgeAI Pro"],
            "content": (
                "Many logistics providers are adopting EdgeAI Pro for warehouse automation."
            )
        },
        {
            "report_id": "RPT-2026-003",
            "title": "Robotics and On-Device Intelligence",
            "sector": "robotics",
            "published_at": "2026-05-01",
            "tags": ["robotics", "inference"],
            "summary": "Survey of on-device inference frameworks.",
            "solution_aliases": ["TensorRT Lite", "HelioSync"],
            "content": (
                "HelioSync is often compared to TensorRT Lite in benchmark tests."
            )
        }
    ]

    with open("data/reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    # ---------- Presentations ----------
    presentations = [
        {
            "presentation_id": "PRES-2026-101",
            "title": "HelioSync Deep Dive: Architecture & Benchmarks",
            "owner": "research_design",
            "updated_at": "2026-04-28",
            "tags": ["edge", "benchmark"],
            "summary": "Internal technical review of HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": (
                "HelioSync Edge Inference Fabric achieves 98% model accuracy "
                "while reducing memory footprint by 40% compared to baseline."
            )
        },
        {
            "presentation_id": "PRES-2026-102",
            "title": "Partner Marketing Q2 Campaign Ideas",
            "owner": "partner_marketing",
            "updated_at": "2026-05-10",
            "tags": ["marketing", "partnership"],
            "summary": "Ideas for co-marketing with edge solution vendors.",
            "solution_aliases": ["HelioSync Lite"],
            "deck_notes": (
                "We might feature HelioSync Lite as a case study in the newsletter."
            )
        }
    ]

    with open("data/presentations.json", "w") as f:
        json.dump(presentations, f, indent=2)

    # ---------- Media Samples ----------
    media_samples = [
        {
            "sample_id": "MED-2026-201",
            "title": "Keynote: The Future of Edge AI",
            "channel": "keynote_transcript",
            "captured_at": "2026-04-20T09:00:00Z",
            "tags": ["keynote", "edge"],
            "summary": "CEO keynote introducing HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HelioSync"],
            "content": (
                "Today we unveil HelioSync Edge Inference Fabric, our newest solution "
                "that brings cloud-grade inference to the edge with zero compromise."
            )
        },
        {
            "sample_id": "MED-2026-202",
            "title": "Podcast: Edge Inference Deep Dive",
            "channel": "podcast_transcript",
            "captured_at": "2026-04-25T14:00:00Z",
            "tags": ["podcast", "technical"],
            "summary": "Engineering lead explains HelioSync architecture.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": (
                "The key innovation in HelioSync Edge Inference Fabric is its "
                "adaptive quantization pipeline that shrinks models by 5x."
            )
        },
        {
            "sample_id": "MED-2026-203",
            "title": "Editorial Draft: Edge AI Trends",
            "channel": "editorial_draft",
            "captured_at": "2026-04-18T10:30:00Z",
            "tags": ["editorial", "trends"],
            "summary": "Draft article about rising edge inference platforms.",
            "solution_aliases": ["TensorRT Edge", "HelioSync Core"],
            "content": (
                "HelioSync Core is positioned as a direct competitor to TensorRT Edge."
            )
        }
    ]

    with open("data/media_samples.json", "w") as f:
        json.dump(media_samples, f, indent=2)

    # ---------- Distractor files ----------
    os.makedirs("ops", exist_ok=True)  # target output dir
    with open("data/old_reports.json", "w") as f:
        f.write("[]")
    with open("notes.txt", "w") as f:
        f.write("Check the data folder for recent exports.\n")

if __name__ == "__main__":
    build_env()
