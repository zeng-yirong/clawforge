import os
import json
import random

def build_env():
    # Create directory structure
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Helper to write JSON with formatting issues on purpose
    def write_json(path, obj, corrupt=False):
        if corrupt:
            # Write a malformed JSON (missing closing brace, extra commas)
            with open(path, "w") as f:
                f.write(json.dumps(obj, indent=2)[:-1] + ",\n  \"__corrupt\": true\n")
        else:
            with open(path, "w") as f:
                json.dump(obj, f, indent=2)

    # --- Reports ---
    reports = [
        {
            "report_id": "R-2025-001",
            "title": "Industrial AI Forecast Q3",
            "sector": "industrial_ai",
            "published_at": "2025-08-01",
            "tags": ["ai", "synaptic"],
            "summary": "Explores edge deployment of AetherMind Synaptic Core in factory settings.",
            "solution_aliases": ["AetherMind Synaptic Core"]
        },
        {
            "report_id": "R-2025-002",
            "title": "Logistics AI Review",
            "sector": "logistics_ai",
            "published_at": "2025-07-15",
            "tags": ["logistics", "neural"],
            "summary": "Mentions AetherMind only briefly; not core.",
            "solution_aliases": ["Neural Orchestrator"]   # does NOT match
        },
        {
            "report_id": "R-2025-003",
            "title": "Robotics Summit Report",
            "sector": "robotics",
            "published_at": "2025-08-10",
            "tags": ["robotics", "synaptic-core"],
            "summary": "Detailed analysis of AetherMind Synaptic Core integration with robotic arms.",
            "solution_aliases": ["AetherMind Synaptic Core", "AetherMind Legacy"]
        },
        {
            "report_id": "R-2025-004",
            "title": "Edge AI Benchmarking",
            "sector": "industrial_ai",
            "published_at": "2025-06-20",
            "tags": ["benchmark", "aether"],
            "summary": "No direct reference to synaptic core.",
            "solution_aliases": ["AetherMind Edge"]
        }
    ]
    write_json("data/reports/reports.json", {"reports": reports})

    # --- Presentations ---
    presentations = [
        {
            "presentation_id": "P-2025-101",
            "title": "AetherMind Synaptic Core – Product Deck",
            "owner": "partner_marketing",
            "updated_at": "2025-08-05",
            "tags": ["synaptic"],
            "summary": "Official launch presentation highlighting AetherMind Synaptic Core capabilities.",
            "solution_aliases": ["AetherMind Synaptic Core"]
        },
        {
            "presentation_id": "P-2025-102",
            "title": "Industrial AI Use Cases",
            "owner": "research_design",
            "updated_at": "2025-07-20",
            "tags": ["industrial", "ai"],
            "summary": "Covers multiple solutions; page 12 references AetherMind Synaptic Core.",
            "solution_aliases": ["AetherMind Synaptic Core", "HelioSync Edge"]
        },
        {
            "presentation_id": "P-2025-103",
            "title": "Partner Strategy Workshop",
            "owner": "strategy_team",
            "updated_at": "2025-06-30",
            "tags": ["strategy"],
            "summary": "No mention of AetherMind.",
            "solution_aliases": ["Quantum Neural Interface"]
        }
    ]
    # Deliberately write one presentation with a different alias (case variation) to be ignored
    presentations.append({
        "presentation_id": "P-2025-104",
        "title": "Legacy Deck v2",
        "owner": "partner_marketing",
        "updated_at": "2024-12-01",
        "tags": ["legacy"],
        "summary": "Old version that listed 'AetherMind synaptIC Core' (typo).",
        "solution_aliases": ["AetherMind synaptIC Core"]   # case mismatch – not exact match
    })
    write_json("data/presentations/presentations.json", {"presentations": presentations})

    # --- Media Samples ---
    media_samples = [
        {
            "sample_id": "M-2025-201",
            "title": "Podcast: AI at the Edge",
            "channel": "podcast_transcript",
            "captured_at": "2025-08-12",
            "tags": ["podcast", "aethermind"],
            "summary": "Interview discussing AetherMind Synaptic Core deployment challenges.",
            "solution_aliases": ["AetherMind Synaptic Core"]
        },
        {
            "sample_id": "M-2025-202",
            "title": "Keynote: Future of Industrial AI",
            "channel": "keynote_transcript",
            "captured_at": "2025-07-30",
            "tags": ["keynote", "synaptic"],
            "summary": "Mentions AetherMind Synaptic Core as key differentiator.",
            "solution_aliases": ["AetherMind Synaptic Core", "HelioSync Edge"]
        },
        {
            "sample_id": "M-2025-203",
            "title": "Editorial Draft: Robotics Redefined",
            "channel": "editorial_draft",
            "captured_at": "2025-08-01",
            "tags": ["robotics"],
            "summary": "Focused on hardware, no software reference.",
            "solution_aliases": ["Robotic Vision Suite"]
        }
    ]
    write_json("data/media_samples/media_samples.json", {"media_samples": media_samples})

    # --- Other support files (attachments, contacts) to add realism but not used for verification---
    attachments = [
        {"path": "solution_matching_notes.md", "title": "Solution Matching Notes", "kind": "matching_guide", "description": "Instructions for matching solution aliases."},
        {"path": "temp_record_guidelines.md", "title": "Temporary Record Guidelines", "kind": "record_schema", "description": "Schema for saving temporary clue records."}
    ]
    write_json("data/attachments.json", {"attachments": attachments})

    contacts = [
        {"contact_id": "C001", "name": "Dev Mehra", "role": "Archive Operations", "email": "dev.mehra@northstar.example.com"},
        {"contact_id": "C002", "name": "Keiko Han", "role": "Market Intelligence Partner", "email": "keiko.han@northstar.example.com"},
        {"contact_id": "C003", "name": "Rhea Morita", "role": "Signal Research Lead", "email": "rhea.morita@northstar.example.com"}
    ]
    write_json("data/contacts.json", {"contacts": contacts})

    # --- Write a corrupt reports file to test robustness ---
    # (we intentionally write it after the valid one to be replaced, but keep original as well? No, we overwrite)
    # Better: create a second fake directory that mimics old data
    os.makedirs("data/old_reports", exist_ok=True)
    old_report = {
        "report_id": "R-2024-999",
        "title": "Old AetherMind Study",
        "solution_aliases": ["AetherMind Synaptic Core"]
    }
    write_json("data/old_reports/report.json", [old_report])  # not a dict with wrapper – different structure

    # Create a dummy file in ops to ensure agent overwrites it
    with open("ops/clue_list.json", "w") as f:
        f.write("{}")

if __name__ == "__main__":
    build_env()
