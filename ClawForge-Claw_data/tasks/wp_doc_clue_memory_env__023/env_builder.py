import json
import os
import random
import string

def build_env():
    # reports
    reports_dir = "data/reports"
    os.makedirs(reports_dir, exist_ok=True)
    reports = [
        { "report_id": "RPT-001", "title": "Edge AI Market Overview", "sector": "industrial_ai", "published_at": "2026-02-10", "tags": ["edge", "AI"], "summary": "Analysis of HelioSync's edge inference fabric market position and future outlook.", "solution_aliases": ["HelioSync Edge Inference Fabric", "NovaCore"], "content": "..." },
        { "report_id": "RPT-002", "title": "Logistics Robotics 2026", "sector": "logistics_ai", "published_at": "2026-01-20", "tags": ["logistics", "robotics"], "summary": "Overview of logistics AI and HelioSync's edge offerings.", "solution_aliases": ["HelioSync Edge", "RoboFlow"], "content": "..." },  # 诱饵：缺少 "Inference Fabric"
        { "report_id": "RPT-003", "title": "Industrial AI Transformation", "sector": "industrial_ai", "published_at": "2026-03-05", "tags": ["industrial", "AI"], "summary": "Deep dive on industrial AI with HelioSync Edge Inference Fabric integration cases.", "solution_aliases": ["HelioSync Edge Inference Fabric", "TensorCore"], "content": "..." },
        { "report_id": "RPT-004", "title": "Robotics Trends", "sector": "robotics", "published_at": "2025-12-01", "tags": ["robotics"], "summary": "No mention of HelioSync.", "solution_aliases": ["OmniDrive"], "content": "..." },
        { "report_id": "RPT-005", "title": "Edge Computing Annual", "sector": "industrial_ai", "published_at": "2026-04-15", "tags": ["edge", "annual"], "summary": "Annual report on edge computing including HelioSync Edge Inference Fabric benchmarks.", "solution_aliases": ["HelioSync Edge Inference Fabric"], "content": "..." },
        { "report_id": "RPT-DIRTY", "title": "Dirty Record", "sector": "industrial_ai", "published_at": "2026-02-01", "tags": ["test"], "summary": "This is a dirty record with malformed solution_aliases.", "solution_aliases": "HelioSync Edge Inference Fabric", "content": "..." }  # 格式错误，期望 agent 跳过
    ]
    with open(os.path.join(reports_dir, "reports.json"), "w") as f:
        json.dump({"wrapper": "reports", "data": reports}, f, indent=2)

    # presentations
    pres_dir = "data/presentations"
    os.makedirs(pres_dir, exist_ok=True)
    presentations = [
        { "presentation_id": "PRES-001", "title": "Strategy Deck Q2", "owner": "partner_marketing", "updated_at": "2026-05-01", "tags": ["strategy", "deck"], "summary": "Strategic alignment of HelioSync Edge Inference Fabric in partner marketing.", "solution_aliases": ["HelioSync Edge Inference Fabric"], "deck_notes": "..." },
        { "presentation_id": "PRES-002", "title": "Research Design Update", "owner": "research_design", "updated_at": "2026-04-20", "tags": ["research", "design"], "summary": "Research design using HelioSync Edge.", "solution_aliases": ["HelioSync Edge"], "deck_notes": "..." },  # 诱饵
        { "presentation_id": "PRES-003", "title": "Tech Roadmap", "owner": "strategy_team", "updated_at": "2026-05-10", "tags": ["tech", "roadmap"], "summary": "Technical roadmap incorporating HelioSync Edge Inference Fabric.", "solution_aliases": ["HelioSync Edge Inference Fabric", "NovaCore"], "deck_notes": "..." },
        { "presentation_id": "PRES-004", "title": "Old Deck 2024", "owner": "partner_marketing", "updated_at": "2024-11-30", "tags": ["old"], "summary": "Outdated version of HelioSync Edge Inference Fabric analysis.", "solution_aliases": ["HelioSync Edge Inference Fabric"], "deck_notes": "..." }
    ]
    with open(os.path.join(pres_dir, "presentations.json"), "w") as f:
        json.dump({"wrapper": "presentations", "data": presentations}, f, indent=2)

    # media_samples
    media_dir = "data/media_samples"
    os.makedirs(media_dir, exist_ok=True)
    media_samples = [
        { "sample_id": "MED-001", "title": "Podcast: Edge AI", "channel": "podcast_transcript", "captured_at": "2026-03-20", "tags": ["podcast"], "summary": "Podcast transcript discussing HelioSync Edge Inference Fabric capabilities.", "solution_aliases": ["HelioSync Edge Inference Fabric"], "content": "..." },
        { "sample_id": "MED-002", "title": "Editorial: Edge Trends", "channel": "editorial_draft", "captured_at": "2026-02-15", "tags": ["editorial"], "summary": "Editorial on edge trends focusing on HelioSync Edge.", "solution_aliases": ["HelioSync Edge"], "content": "..." },  # 诱饵
        { "sample_id": "MED-003", "title": "Keynote: AI at Scale", "channel": "keynote_transcript", "captured_at": "2026-04-01", "tags": ["keynote", "AI"], "summary": "Keynote transcript covering HelioSync Edge Inference Fabric and scale AI.", "solution_aliases": ["HelioSync Edge Inference Fabric", "AiScale"], "content": "..." },
        { "sample_id": "MED-004", "title": "Draft: Misc", "channel": "editorial_draft", "captured_at": "2026-01-10", "tags": ["draft"], "summary": "Draft document with preliminary HelioSync Edge Inference Fabric notes.", "solution_aliases": ["HelioSync Edge Inference Fabric"], "content": "..." }
    ]
    with open(os.path.join(media_dir, "media_samples.json"), "w") as f:
        json.dump({"wrapper": "media_samples", "data": media_samples}, f, indent=2)

    # Optional: other required files (accounts, attachments, contacts) – minimal stubs
    data_dir = "data"
    accounts = [
        { "account_id": "acc001", "display_name": "Alice", "department": "Engineering", "email": "alice@example.com", "permissions": ["read"], "default_region": "us", "voice": [] }
    ]
    with open(os.path.join(data_dir, "accounts.json"), "w") as f:
        json.dump({"wrapper": "accounts", "data": accounts}, f, indent=2)
    attachments = []
    with open(os.path.join(data_dir, "attachments.json"), "w") as f:
        json.dump({"wrapper": "attachments", "data": attachments}, f, indent=2)
    contacts = []
    with open(os.path.join(data_dir, "contacts.json"), "w") as f:
        json.dump({"wrapper": "contacts", "data": contacts}, f, indent=2)

    # Create a decoy directory with old data
    archive_dir = "data/archive"
    os.makedirs(archive_dir, exist_ok=True)
    # Copy a modified version of reports to archive – mismatched summaries
    fake_reports = [
        { "report_id": "RPT-001", "title": "Edge AI Market Overview", "sector": "industrial_ai", "published_at": "2025-01-01", "tags": ["old"], "summary": "Old summary, not matching.", "solution_aliases": ["HelioSync Edge Inference Fabric"], "content": "..." }
    ]
    with open(os.path.join(archive_dir, "reports.json"), "w") as f:
        json.dump({"wrapper": "reports", "data": fake_reports}, f, indent=2)

    # Create ops directory (empty) so agent can write into it
    os.makedirs("ops", exist_ok=True)

    # Create a README.txt as another distraction
    with open("data/README.txt", "w") as f:
        f.write("All current data files are in this directory. Archive contains outdated copies.\n")

if __name__ == "__main__":
    build_env()
