import os
import json

def build_env():
    # --- reports ---
    reports_path = "reports"
    os.makedirs(reports_path, exist_ok=True)
    reports = [
        {
            "report_id": "RPT-2026-001",
            "title": "HelioSync Edge Inference Fabric Deployment Study",
            "sector": "industrial_ai",
            "published_at": "2026-02-15",
            "tags": ["edge", "inference", "heliosync"],
            "summary": "Deployment metrics for HelioSync Edge Inference Fabric in manufacturing.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HS-Edge-IF"]
        },
        {
            "report_id": "RPT-2026-002",
            "title": "HelioSync Edge Performance Benchmarks",
            "sector": "industrial_ai",
            "published_at": "2026-01-20",
            "tags": ["edge", "benchmark", "heliosync"],
            "summary": "Benchmark results for the HelioSync Edge platform (pre-fabric).",
            "solution_aliases": ["HelioSync Edge", "HelioSync Edge Platform"]
        },
        {
            "report_id": "RPT-2026-003",
            "title": "Inference Fabric for Logistics AI",
            "sector": "logistics_ai",
            "published_at": "2026-03-01",
            "tags": ["inference", "fabric", "logistics"],
            "summary": "Logistics AI using general Inference Fabric, unrelated to HelioSync.",
            "solution_aliases": ["Inference Fabric", "Logistics Inference Fabric"]
        },
        {
            "report_id": "RPT-2026-004",
            "title": "HelioSync Edge Inference Fabric Security Audit",
            "sector": "industrial_ai",
            "published_at": "2026-03-10",
            "tags": ["security", "heliosync", "fabric"],
            "summary": "Security audit findings for HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HS-Edge-IF-SEC"]
        }
    ]
    with open(os.path.join(reports_path, "reports.json"), "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # --- presentations ---
    presentations_path = "presentations"
    os.makedirs(presentations_path, exist_ok=True)
    presentations = [
        {
            "presentation_id": "PRES-2026-101",
            "title": "Q2 HelioSync Edge Inference Fabric Roadmap",
            "owner": "partner_marketing",
            "updated_at": "2026-02-28",
            "tags": ["roadmap", "heliosync", "edge"],
            "summary": "Roadmap slides for HelioSync Edge Inference Fabric Q2-Q3.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"]
        },
        {
            "presentation_id": "PRES-2026-102",
            "title": "HelioSync Edge Overview for Partners",
            "owner": "partner_marketing",
            "updated_at": "2026-01-10",
            "tags": ["heliosync", "edge", "partner"],
            "summary": "Partner deck covering HelioSync Edge (pre-fabric) capabilities.",
            "solution_aliases": ["HelioSync Edge"]
        },
        {
            "presentation_id": "PRES-2026-103",
            "title": "Fabric AI Architecture Review",
            "owner": "research_design",
            "updated_at": "2026-02-20",
            "tags": ["architecture", "fabric", "ai"],
            "summary": "Internal architecture review of Fabric AI, not HelioSync specific.",
            "solution_aliases": ["Fabric AI", "General Fabric"]
        }
    ]
    with open(os.path.join(presentations_path, "presentations.json"), "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # --- media_samples ---
    media_path = "media_samples"
    os.makedirs(media_path, exist_ok=True)
    media_samples = [
        {
            "sample_id": "MEDIA-2026-201",
            "title": "HelioSync Edge Inference Fabric Launch Podcast",
            "channel": "podcast_transcript",
            "captured_at": "2026-02-22",
            "tags": ["launch", "heliosync", "podcast"],
            "summary": "Transcript of the HelioSync Edge Inference Fabric launch podcast.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"]
        },
        {
            "sample_id": "MEDIA-2026-202",
            "title": "Edge Inference Fabric vs. HelioSync Edge",
            "channel": "editorial_draft",
            "captured_at": "2026-03-05",
            "tags": ["comparison", "edge", "fabric"],
            "summary": "Draft comparing generic Edge Inference Fabric with HelioSync Edge.",
            "solution_aliases": ["Edge Inference Fabric", "HelioSync Edge"]
        },
        {
            "sample_id": "MEDIA-2026-203",
            "title": "HelioSync Edge Inference Fabric Customer Testimonial",
            "channel": "keynote_transcript",
            "captured_at": "2026-02-28",
            "tags": ["testimonial", "heliosync"],
            "summary": "Customer success story for HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"]
        }
    ]
    with open(os.path.join(media_path, "media_samples.json"), "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # --- decoy files (other data from the schema) ---
    data_path = "data"
    os.makedirs(data_path, exist_ok=True)
    contacts = [
        {"contact_id": "C001", "name": "Dev Mehra", "role": "Archive Operations", "email": "dev.mehra@northstar.example.com"},
        {"contact_id": "C002", "name": "Keiko Han", "role": "Market Intelligence Partner", "email": "keiko.han@northstar.example.com"}
    ]
    with open(os.path.join(data_path, "contacts.json"), "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    accounts = [
        {"account_id": "A001", "display_name": "NorthStar Industrial", "department": "R&D", "email": "rd@northstar.example.com", "permissions": ["read"], "default_region": "na", "voice": []}
    ]
    with open(os.path.join(data_path, "accounts.json"), "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    attachments = [
        {"path": "solution_matching_notes.md", "title": "Solution Matching Notes", "kind": "matching_guide", "description": "Guidelines for matching solutions."}
    ]
    with open(os.path.join(data_path, "attachments.json"), "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # --- an extra plain text file as decoy ---
    with open("README_old.txt", "w") as f:
        f.write("This is an old readme, ignore.\n")

    # --- ensure clue_list.json does NOT exist initially ---
    if os.path.exists("clue_list.json"):
        os.remove("clue_list.json")

if __name__ == "__main__":
    build_env()
