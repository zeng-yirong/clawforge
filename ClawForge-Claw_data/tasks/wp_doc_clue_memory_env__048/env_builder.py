import os
import json

def build_env():
    # 确保工作区根目录在 
    # 所有相对路径均以此为基准

    # 创建目录结构
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. reports
    reports = {
        "reports": [
            {
                "report_id": "rpt-001",
                "title": "Edge AI Deployment in Logistics",
                "sector": "logistics_ai",
                "published_at": "2025-11-01",
                "tags": ["edge", "inference", "logistics"],
                "summary": "Evaluation of HelioSync Edge Inference Fabric in warehouse automation.",
                "solution_aliases": ["HelioSync Edge Inference Fabric", "HelioSync Edge"],
                "content": "The deployment showed promising latency reduction. CLUE:RPT001 further analysis needed."
            },
            {
                "report_id": "rpt-002",
                "title": "IoT Gateway Performance",
                "sector": "industrial_ai",
                "published_at": "2025-10-15",
                "tags": ["iot", "gateway"],
                "summary": "Testing HelioSync Edge on gateways.",
                "solution_aliases": ["HelioSync Edge"],
                "content": "CLUE:RPT002 is not the target."
            },
            {
                "report_id": "rpt-003",
                "title": "HelioSync Fabric for Robotics",
                "sector": "robotics",
                "published_at": "2025-12-01",
                "tags": ["robotics", "fabric"],
                "summary": "Integrated HelioSync Edge Inference Fabric with ROS2.",
                "solution_aliases": ["HelioSync Edge Inference Fabric", "Quantum Grid"],
                "content": "CLUE:RPT003 found in Section 4."
            },
            {
                "report_id": "rpt-004",
                "title": "Quantum Grid Review",
                "sector": "industrial_ai",
                "published_at": "2025-09-01",
                "tags": ["quantum"],
                "summary": "Analysis of Quantum Grid.",
                "solution_aliases": ["Quantum Grid"],
                "content": "No CLUE here."
            }
        ]
    }
    with open("data/reports/reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    # 2. presentations
    presentations = {
        "presentations": [
            {
                "presentation_id": "pres-001",
                "title": "Company Overview",
                "owner": "partner_marketing",
                "updated_at": "2025-11-20",
                "tags": ["overview"],
                "summary": "General presentation.",
                "solution_aliases": [],
                "deck_notes": "Nothing relevant."
            },
            {
                "presentation_id": "pres-002",
                "title": "HelioSync Edge Case Study",
                "owner": "research_design",
                "updated_at": "2025-12-10",
                "tags": ["helio", "edge", "case-study"],
                "summary": "Detailed case study of HelioSync Edge Inference Fabric.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "deck_notes": "Slide 7: CLUE:PRES002 customer feedback."
            },
            {
                "presentation_id": "pres-003",
                "title": "Future Tech Trends",
                "owner": "strategy_team",
                "updated_at": "2025-11-01",
                "tags": ["trends"],
                "summary": "Upcoming technologies.",
                "solution_aliases": ["HelioSync Edge Inference Fabric v2"],
                "deck_notes": "CLUE:PRES003 v2 note."
            }
        ]
    }
    with open("data/presentations/presentations.json", "w") as f:
        json.dump(presentations, f, indent=2)

    # 3. media_samples
    media_samples = {
        "media_samples": [
            {
                "sample_id": "sample-001",
                "title": "Podcast: HelioSync in Production",
                "channel": "podcast_transcript",
                "captured_at": "2025-12-05",
                "tags": ["podcast", "helio"],
                "summary": "Transcript discussing HelioSync Edge Inference Fabric.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "Interviewer: Can you tell us about HelioSync Edge Inference Fabric? Interviewee: Sure, CLUE:SAMPLE001 it's a game changer."
            },
            {
                "sample_id": "sample-002",
                "title": "Editorial: Edge AI Roundup",
                "channel": "editorial_draft",
                "captured_at": "2025-11-20",
                "tags": ["editorial"],
                "summary": "Covers multiple edge solutions.",
                "solution_aliases": [],
                "content": "No specific CLUE."
            },
            {
                "sample_id": "sample-003",
                "title": "Keynote: Industrial AI",
                "channel": "keynote_transcript",
                "captured_at": "2025-10-30",
                "tags": ["keynote"],
                "summary": "Keynote on industrial AI.",
                "solution_aliases": ["HelioSync Edge"],
                "content": "CLUE:SAMPLE003 is not the intended clue."
            },
            {
                "sample_id": "sample-004",
                "title": "Podcast: Quantum Grid",
                "channel": "podcast_transcript",
                "captured_at": "2025-12-01",
                "tags": ["quantum"],
                "summary": "Discussing Quantum Grid.",
                "solution_aliases": ["Quantum Grid"],
                "content": "No CLUE."
            }
        ]
    }
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump(media_samples, f, indent=2)

    # 4. attachments (as a JSON index pointing to the actual file)
    attachments = {
        "attachments": [
            {
                "path": "data/attachments/solution_matching_notes.md",
                "title": "Solution Matching Notes",
                "kind": "matching_guide",
                "description": "Describes target solution aliases for HelioSync Edge Inference Fabric."
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 5. the actual notes file
    notes_content = """# Solution Matching Notes

The target solution we are tracking is **HelioSync Edge Inference Fabric**.

Aliases to match exactly:
- HelioSync Edge Inference Fabric

Do not include:
- HelioSync Edge
- HelioSync Edge Inference Fabric v2
- any other variant
"""
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write(notes_content)

    # 6. minor distracting data (not required by prompt)
    accounts = {
        "accounts": [
            {"account_id": "acc-1", "display_name": "Alpha Corp", "department": "IoT", "email": "a@corp.com", "permissions": ["read"], "default_region": "us-east", "voice": []}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "c-1", "name": "Dev Mehra", "role": "Archive Operations", "email": "dev.mehra@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
