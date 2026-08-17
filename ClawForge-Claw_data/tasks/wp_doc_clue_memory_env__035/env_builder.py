import os
import json
import random

def build_env():
    # Create directories
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("temp", exist_ok=True)  # distraction directory

    # --- Reports ---
    reports = [
        {
            "report_id": "RPT-2025-001",
            "title": "Industrial AI: Edge Computing Beyond the Hype",
            "sector": "industrial_ai",
            "published_at": "2025-03-15",
            "tags": ["edge", "inference", "HelioSync"],
            "summary": "HelioSync Edge Inference Fabric enables real-time model deployment on factory floor gateways. This report reviews three production pilots.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"]
        },
        {
            "report_id": "RPT-2025-002",
            "title": "Logistics AI: Autonomous Sorting at Scale",
            "sector": "logistics_ai",
            "published_at": "2025-02-20",
            "tags": ["sorting", "robotics", "HelioSync"],
            "summary": "We explore the use of HelioSync for cross-docking optimization. Note that the Edge Inference Fabric is not mentioned in this work.",
            "solution_aliases": ["HelioSync"]  # partial match, should be excluded
        },
        {
            "report_id": "RPT-2025-003",
            "title": "Robotics Fleet Management with Nebula Core",
            "sector": "robotics",
            "published_at": "2025-01-10",
            "tags": ["fleet", "Nebula"],
            "summary": "A comparative analysis of fleet orchestration platforms. No mention of HelioSync.",
            "solution_aliases": []  # empty list, exclude
        },
        {
            "report_id": "RPT-2025-004",
            "title": "Edge Inference Fabric: Deployment Guide",
            "sector": "industrial_ai",
            "published_at": "2025-04-01",
            "tags": ["edge", "inference", "HelioSync", "security"],
            "summary": "HelioSync Edge Inference Fabric requires TPM 2.0 and kernel 5.10+. This guide covers setup and monitoring.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "Aurora Core"]
        },
        {
            "report_id": "RPT-2025-005",
            "title": "Warehouse Automation Trends 2025",
            "sector": "logistics_ai",
            "published_at": "2025-03-01",
            "tags": ["automation", "trends"],
            "summary": "Overview of major trends. The HelioSync brand appears only in a footnote.",  # not in solution_aliases, exclude
            "solution_aliases": ["Nexus Vision"]
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # --- Presentations ---
    presentations = [
        {
            "presentation_id": "PRES-2025-101",
            "title": "Nebula Core: Next-Gen Orchestrator",
            "owner": "strategy_team",
            "updated_at": "2025-02-28",
            "tags": ["Nebula", "orchestration"],
            "summary": "Nebula Core architecture overview. No HelioSync content.",
            "solution_aliases": ["Nebula Core"]
        },
        {
            "presentation_id": "PRES-2025-102",
            "title": "HelioSync Edge Inference Fabric – Partner Summit",
            "owner": "partner_marketing",
            "updated_at": "2025-03-22",
            "tags": ["HelioSync", "edge", "partner"],
            "summary": "HelioSync Edge Inference Fabric integration patterns for industrial partners. Key API changes in v2.1.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"]
        },
        {
            "presentation_id": "PRES-2025-103",
            "title": "Edge Inference without the Fabric?",
            "owner": "research_design",
            "updated_at": "2025-01-15",
            "tags": ["edge", "inference"],
            "summary": "Discussion of alternative deployment models. HelioSync is mentioned but not as the target fabric.",
            "solution_aliases": ["HelioSync Edge Inference"]  # missing "Fabric", exclude
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # --- Media Samples ---
    media_samples = [
        {
            "sample_id": "MED-2025-001",
            "title": "Interview: HelioSync CEO on Edge Vision",
            "channel": "podcast_transcript",
            "captured_at": "2025-03-10",
            "tags": ["HelioSync", "CEO", "vision"],
            "summary": "The CEO discusses the strategic importance of the HelioSync Edge Inference Fabric for IoT deployments.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"]
        },
        {
            "sample_id": "MED-2025-002",
            "title": "Marketing Draft: Fabric vs. Competitors",
            "channel": "editorial_draft",
            "captured_at": "2025-02-14",
            "tags": ["competitive", "draft"],
            "summary": "Draft blog post comparing HelioSync Edge Inference Fabric to AWS IoT Greengrass. Not final.",
            "solution_aliases": ["Edge Inference Fabric", "HelioSync"]  # two partial, but not the exact phrase
        },
        {
            "sample_id": "MED-2025-003",
            "title": "Keynote: Building with HelioSync",
            "channel": "keynote_transcript",
            "captured_at": "2025-04-05",
            "tags": ["keynote", "HelioSync"],
            "summary": "HelioSync Edge Inference Fabric enables sub-5ms inference at the edge. Demo with a robotic arm.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "Nebula"]
        },
        {
            "sample_id": "MED-2025-004",
            "title": "Podcast: HelioSync vs. Aurora",
            "channel": "podcast_transcript",
            "captured_at": "2025-01-20",
            "tags": ["HelioSync", "Aurora"],
            "summary": "Comparison of two edge solutions. The host mentions HelioSync but not the Fabric.",
            "solution_aliases": []  # empty, exclude
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # --- Attachments (template + guide) ---
    attachments = [
        {
            "path": "solution_matching_notes.md",
            "title": "Solution Matching Notes",
            "kind": "matching_guide",
            "description": "Instructions on how to identify target solutions by reading solution_aliases."
        },
        {
            "path": "temp_record_guidelines.md",
            "title": "Temporary Record Guidelines",
            "kind": "record_schema",
            "description": "Standard format for clue list JSON used by downstream ingestion."
        }
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # Write the actual attachment files
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write("# Solution Matching Notes\n\n")
        f.write("To match a document, check the `solution_aliases` array. The target phrase must appear **exactly** as given (case-sensitive).\n")
        f.write("Ignore documents with empty or missing `solution_aliases`.\n")

    with open("data/attachments/temp_record_guidelines.md", "w") as f:
        f.write("# Temporary Record Guidelines\n\n")
        f.write("Use the following JSON structure for clue lists:\n\n")
        f.write("```json\n")
        f.write("{\n")
        f.write('  "clues": [\n')
        f.write("    {\n")
        f.write('      "id": "<document unique id>",\n')
        f.write('      "type": "<report|presentation|media_sample>",\n')
        f.write('      "clue": "<first 80 characters of the document summary>"\n')
        f.write("    }\n")
        f.write("  ]\n")
        f.write("}\n")
        f.write("```\n\n")
        f.write("Each clue string must be exactly the first 80 characters (including spaces and punctuation) of the `summary` field.\n")
        f.write("Do not truncate earlier or later.\n")

    # --- Distraction files (non-standard format) ---
    # Create a fake CSV and a log file to add noise
    with open("temp/old_records.csv", "w") as f:
        f.write("id,status\n001,pending\n002,archived\n")
    with open("data/stale_notes.txt", "w") as f:
        f.write("Some random notes about HelioSync that should be ignored.\n")

    # Additional noise: a report with missing solution_aliases field (JSON will have it omitted)
    # We already have a report with empty list; missing field would be invalid according to schema but we can add one.
    # Let's add a secondary reports file that is not supposed to be read? No, we stick to the main file.
    # Instead, we can duplicate one report with a different ID but same data? not needed.

    print("Environment built successfully. Target solution: HelioSync Edge Inference Fabric")
    print("Matching documents (expected in clue_list):")
    print("  RPT-2025-001, RPT-2025-004, PRES-2025-102, MED-2025-001, MED-2025-003")

if __name__ == "__main__":
    build_env()
