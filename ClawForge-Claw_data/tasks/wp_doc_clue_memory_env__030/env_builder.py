import os
import json

def build_env():
    # Create directory structure
    dirs = [
        "data/reports",
        "data/presentations",
        "data/media_samples",
        "data/attachments",
        "temp_records"  # empty, agent must write into it
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ---- accounts.json (distractor) ----
    accounts = {
        "accounts": [
            {"account_id": "ACCT-001", "display_name": "Acme Corp", "department": "R&D",
             "email": "acme@example.com", "permissions": ["read", "write"],
             "default_region": "us-east", "voice": ["en"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- contacts.json (distractor) ----
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Dev Mehra", "role": "Archive Operations",
             "email": "dev.mehra@northstar.example.com"},
            {"contact_id": "C002", "name": "Keiko Han", "role": "Market Intelligence Partner",
             "email": "keiko.han@northstar.example.com"},
            {"contact_id": "C003", "name": "Rhea Morita", "role": "Signal Research Lead",
             "email": "rhea.morita@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---- attachments (hint file, not mandatory) ----
    notes = "# Solution Matching Notes\n\n" \
            "To match a document to a target solution, check the `solution_aliases` list " \
            "for the exact string (case‑sensitive).\n" \
            "Each matching document has a line starting with `CLUE:` in its `content` field."
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write(notes)

    # ---- reports ----
    reports = {
        "reports": [
            {
                "report_id": "RPT-2026-001",
                "title": "Supply Chain Automation Q2",
                "sector": "logistics_ai",
                "published_at": "2026-03-15",
                "tags": ["automation", "routing"],
                "summary": "Deep dive into automated routing for logistics.",
                "solution_aliases": ["OptiFlow Nexus", "LogiSync"],
                "content": "Executive summary...\nCLUE: Automated routing optimization for supply chains\nConclusion..."
            },
            {
                "report_id": "RPT-2026-002",
                "title": "Warehouse Robotics Update",
                "sector": "robotics",
                "published_at": "2026-04-01",
                "tags": ["robotics", "warehouse"],
                "summary": "Latest robotics deployments.",
                "solution_aliases": ["OptiFlow Nexus Lite"],
                "content": "Intro...\nCLUE: Enhanced picking efficiency\nNote..."
            },
            {
                "report_id": "RPT-2026-003",
                "title": "Edge Computing for Manufacturing",
                "sector": "industrial_ai",
                "published_at": "2026-05-10",
                "tags": ["edge", "manufacturing"],
                "summary": "Edge deployment case studies.",
                "solution_aliases": ["OptiFlow Nexus", "EdgeFusion"],
                "content": "Background...\nCLUE: Predictive capacity planning for warehouses\nFinal thoughts..."
            },
            {
                "report_id": "RPT-2026-004",
                "title": "Fleet Management Trends",
                "sector": "logistics_ai",
                "published_at": "2026-02-20",
                "tags": ["fleet", "optimization"],
                "summary": "Fleet optimization overview.",
                "solution_aliases": ["FleetFlow"],
                "content": "Intro...\nCLUE: Fuel consumption reduction\n..."
            }
        ]
    }
    with open("data/reports/reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    # ---- presentations ----
    presentations = {
        "presentations": [
            {
                "presentation_id": "PRES-2026-001",
                "title": "OptiFlow Nexus Capabilities Deck",
                "owner": "partner_marketing",
                "updated_at": "2026-05-20",
                "tags": ["nexus", "capabilities"],
                "summary": "Overview of OptiFlow Nexus features.",
                "solution_aliases": ["OptiFlow Nexus", "OptiFlow Suite"],
                "deck_notes": "Slide 14 demo script.",
                "content": "Slide content...\nCLUE: Real-time fleet optimization for deliveries\nQ&A..."
            },
            {
                "presentation_id": "PRES-2026-002",
                "title": "Logistics AI Roundtable",
                "owner": "strategy_team",
                "updated_at": "2026-04-10",
                "tags": ["logistics", "ai"],
                "summary": "Discussion on AI in logistics.",
                "solution_aliases": ["OptiFlow Nexus Lite", "CloudLog"],
                "deck_notes": "No demo.",
                "content": "Key points...\nCLUE: Hybrid cloud integration\n..."
            },
            {
                "presentation_id": "PRES-2026-003",
                "title": "Industrial IoT Security",
                "owner": "research_design",
                "updated_at": "2026-06-01",
                "tags": ["iot", "security"],
                "summary": "Security best practices for IIoT.",
                "solution_aliases": ["SecureEdge"],
                "deck_notes": "N/A",
                "content": "Overview...\nCLUE: Zero-trust architecture\n..."
            }
        ]
    }
    with open("data/presentations/presentations.json", "w") as f:
        json.dump(presentations, f, indent=2)

    # ---- media samples ----
    media_samples = {
        "media_samples": [
            {
                "sample_id": "MEDIA-2026-001",
                "title": "Interview: OptiFlow Nexus Launch",
                "channel": "podcast_transcript",
                "captured_at": "2026-05-15T10:00:00Z",
                "tags": ["launch", "interview"],
                "summary": "Podcast interview with product lead.",
                "solution_aliases": ["OptiFlow Nexus", "EdgeFusion"],
                "content": "Host: Welcome...\nCLUE: Edge deployment for manufacturing IoT\nGuest: ..."
            },
            {
                "sample_id": "MEDIA-2026-002",
                "title": "Editorial: Warehouse Robotics",
                "channel": "editorial_draft",
                "captured_at": "2026-04-20T14:30:00Z",
                "tags": ["robotics", "warehouse"],
                "summary": "Draft article on warehouse automation.",
                "solution_aliases": ["OptiFlow Nexus Lite"],
                "content": "Intro...\nCLUE: Autonomous pallet moving\n..."
            },
            {
                "sample_id": "MEDIA-2026-003",
                "title": "Keynote: Future of Supply Chain",
                "channel": "keynote_transcript",
                "captured_at": "2026-03-30T09:00:00Z",
                "tags": ["supply-chain", "keynote"],
                "summary": "Keynote at SupplyCon 2026.",
                "solution_aliases": ["GlobalChain"],
                "content": "Opening...\nCLUE: Blockchain provenance tracking\n..."
            }
        ]
    }
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump(media_samples, f, indent=2)

if __name__ == "__main__":
    build_env()
