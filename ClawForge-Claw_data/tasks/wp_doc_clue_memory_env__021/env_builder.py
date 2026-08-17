import os
import json

def build_env():
    # 创建目录
    os.makedirs("reports", exist_ok=True)
    os.makedirs("presentations", exist_ok=True)
    os.makedirs("media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 报告
    reports = [
        {
            "id": "RPT-101",
            "title": "Q1 Edge Inference Deployment Study",
            "summary": "Early benchmark results for HelioSync Edge Inference Fabric show 40% latency reduction.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "status": "active"
        },
        {
            "id": "RPT-202",
            "title": "Archived: HelioSync Edge Inference Fabric Review",
            "summary": "Outdated analysis from last fiscal year, not relevant.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "status": "archived"
        },
        {
            "id": "RPT-303",
            "title": "Industrial AI and Edge Trends",
            "summary": "General edge computing overview, no specific product mention.",
            "solution_aliases": ["Edge Computing"],
            "status": "active"
        }
    ]
    with open("reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # 演示文稿
    presentations = [
        {
            "id": "PRES-001",
            "title": "Partner Marketing Deck - HelioSync Edge",
            "summary": "Slides covering HelioSync Edge Inference Fabric go-to-market strategy.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "status": "active"
        },
        {
            "id": "PRES-022",
            "title": "Research Design - HelioSync Edge Lite",
            "summary": "Discusses a different variant 'HelioSync Edge Lite', not the Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Lite"],
            "status": "active"
        },
        {
            "id": "PRES-103",
            "title": "Strategy Team Offsite Slides",
            "summary": "Contains a slide mentioning 'HelioSync Edge Inference Fabric' but version is deprecated.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "status": "archived"
        }
    ]
    with open("presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # 媒体样本
    media_samples = [
        {
            "id": "MED-007",
            "title": "Podcast Transcript: Edge AI Deep Dive",
            "summary": "Interview with engineer about HelioSync Edge Inference Fabric architecture.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "status": "active"
        },
        {
            "id": "MED-012",
            "title": "Keynote Transcript: HelioSync Edge (old version)",
            "summary": "Transcript from Q3 2025 keynote about first generation HelioSync Edge.",
            "solution_aliases": ["HelioSync Edge"],
            "status": "archived"
        },
        {
            "id": "MED-019",
            "title": "Editorial Draft: HelioSync Fabric Overview",
            "summary": "Draft article mistakenly uses 'HelioSync Fabric' abbreviation, not full product name.",
            "solution_aliases": ["HelioSync Fabric"],
            "status": "active"
        }
    ]
    with open("media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

if __name__ == "__main__":
    build_env()
