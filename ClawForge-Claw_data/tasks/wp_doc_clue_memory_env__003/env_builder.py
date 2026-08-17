import os
import json

def build_env():
    # 确保各子目录存在
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 留给 agent 输出

    # ---- accounts.json ----
    accounts = {
        "accounts": [
            {
                "account_id": "acc-001",
                "display_name": "NorthStar Analytics",
                "department": "Product",
                "email": "ops@northstar.example.com",
                "permissions": ["read", "write"],
                "default_region": "us-east",
                "voice": ["en-US"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- contacts.json ----
    contacts = {
        "contacts": [
            {
                "contact_id": "c-001",
                "name": "Dev Mehra",
                "role": "Archive Operations",
                "email": "dev.mehra@northstar.example.com"
            },
            {
                "contact_id": "c-002",
                "name": "Keiko Han",
                "role": "Market Intelligence Partner",
                "email": "keiko.han@northstar.example.com"
            },
            {
                "contact_id": "c-003",
                "name": "Rhea Morita",
                "role": "Signal Research Lead",
                "email": "rhea.morita@northstar.example.com"
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---- attachments.json ----
    attachments = {
        "attachments": [
            {
                "path": "solution_matching_notes.md",
                "title": "Solution Matching Notes",
                "kind": "matching_guide",
                "description": "Guide to matching solution aliases across documents."
            },
            {
                "path": "temp_record_guidelines.md",
                "title": "Temporary Record Guidelines",
                "kind": "record_schema",
                "description": "Schema for temporary records in signal tracing."
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ---- reports ----
    reports = {
        "reports": [
            {
                "report_id": "RPT-001",
                "title": "Edge AI Inference at Scale",
                "sector": "industrial_ai",
                "published_at": "2026-02-15",
                "tags": ["edge", "inference"],
                "summary": "This report covers deployment of HelioSync Edge Inference Fabric across manufacturing sites.",
                "solution_aliases": ["HelioSync Edge Inference Fabric", "Edge Inference"],
                "content": "..."
            },
            {
                "report_id": "RPT-002",
                "title": "Logistics AI Trends 2026",
                "sector": "logistics_ai",
                "published_at": "2026-01-20",
                "tags": ["logistics"],
                "summary": "Overview of AI adoption in logistics.",
                "solution_aliases": ["LogisticsAI"],
                "content": "..."
            },
            {
                "report_id": "RPT-003",
                "title": "Industrial Robotics Update",
                "sector": "robotics",
                "published_at": "2025-11-10",
                "tags": ["robotics"],
                "summary": "Analysis of HelioSync Edge Inference Fabric in robotics.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "..."
            },
            {
                "report_id": "RPT-004",
                "title": "HelioSync Edge Overview",
                "sector": "industrial_ai",
                "published_at": "2025-06-01",
                "tags": ["heliosync"],
                "summary": "Overview of HelioSync Edge (pre-rebrand).",
                "solution_aliases": ["HelioSync Edge"],
                "content": "..."
            },
            {
                "report_id": "RPT-005",
                "title": "Generic Edge AI",
                "sector": "industrial_ai",
                "published_at": "2026-03-01",
                "tags": ["edge"],
                "summary": "General edge AI trends.",
                "solution_aliases": ["Edge AI"],
                "content": "..."
            }
        ]
    }
    with open("data/reports/reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    # ---- presentations ----
    presentations = {
        "presentations": [
            {
                "presentation_id": "PRES-001",
                "title": "HelioSync Edge Fabric Demo",
                "owner": "partner_marketing",
                "updated_at": "2026-03-10",
                "tags": ["heliosync", "edge"],
                "summary": "Live demo deck for HelioSync Edge Inference Fabric.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "deck_notes": "..."
            },
            {
                "presentation_id": "PRES-002",
                "title": "Supply Chain AI Summit",
                "owner": "strategy_team",
                "updated_at": "2026-02-28",
                "tags": ["supply-chain"],
                "summary": "Keynote on supply chain AI.",
                "solution_aliases": ["SupplyChainAI"],
                "deck_notes": "..."
            },
            {
                "presentation_id": "PRES-003",
                "title": "Edge Inference Workshop",
                "owner": "research_design",
                "updated_at": "2025-12-01",
                "tags": ["edge"],
                "summary": "Workshop on edge inference techniques.",
                "solution_aliases": ["Edge Inference"],
                "deck_notes": "..."
            },
            {
                "presentation_id": "PRES-004",
                "title": "HelioSync Launch Deck",
                "owner": "partner_marketing",
                "updated_at": "2025-08-15",
                "tags": ["heliosync"],
                "summary": "Launch presentation for HelioSync platform.",
                "solution_aliases": ["HelioSync"],
                "deck_notes": "..."
            }
        ]
    }
    with open("data/presentations/presentations.json", "w") as f:
        json.dump(presentations, f, indent=2)

    # ---- media_samples ----
    media_samples = {
        "media_samples": [
            {
                "sample_id": "MED-001",
                "title": "Edge AI Podcast Episode 12",
                "channel": "podcast_transcript",
                "captured_at": "2026-03-05",
                "tags": ["edge", "ai"],
                "summary": "Discussion on HelioSync Edge Inference Fabric with industry experts.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "..."
            },
            {
                "sample_id": "MED-002",
                "title": "Keynote 2026 - AI Future",
                "channel": "keynote_transcript",
                "captured_at": "2026-01-15",
                "tags": ["keynote", "ai"],
                "summary": "CEO keynote on AI strategy.",
                "solution_aliases": ["AI Strategy"],
                "content": "..."
            },
            {
                "sample_id": "MED-003",
                "title": "HelioSync Edge Editorial Draft",
                "channel": "editorial_draft",
                "captured_at": "2025-11-20",
                "tags": ["heliosync"],
                "summary": "Draft article about HelioSync Edge.",
                "solution_aliases": ["HelioSync Edge"],
                "content": "..."
            },
            {
                "sample_id": "MED-004",
                "title": "Robotics Podcast",
                "channel": "podcast_transcript",
                "captured_at": "2026-02-10",
                "tags": ["robotics"],
                "summary": "Robotics AI discussion.",
                "solution_aliases": ["RoboticsAI"],
                "content": "..."
            }
        ]
    }
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump(media_samples, f, indent=2)

if __name__ == "__main__":
    build_env()
