import os
import json

def build_env():
    # 创建 data 子目录
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，留给 agent 写入

    # ========== reports ==========
    reports = [
        {
            "report_id": "RPT-001",
            "title": "Edge Inference in Manufacturing",
            "sector": "industrial_ai",
            "published_at": "2026-02-15",
            "tags": ["edge", "inference", "manufacturing"],
            "summary": "Explores deployment of HelioSync at factory floor for real-time defect detection.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Full report content... (abbreviated)"
        },
        {
            "report_id": "RPT-002",
            "title": "Logistics AI Trends 2026",
            "sector": "logistics_ai",
            "published_at": "2026-03-01",
            "tags": ["logistics", "AI", "trends"],
            "summary": "Covers HelioSync for warehouse optimization and route planning.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "QuantumRoute"],
            "content": "Trend analysis... (abbreviated)"
        },
        {
            "report_id": "RPT-003",
            "title": "Robotics Automation 2026",
            "sector": "robotics",
            "published_at": "2026-01-20",
            "tags": ["robotics", "automation"],
            "summary": "Focuses on general robotics, no edge inference.",
            "solution_aliases": ["EdgeCore"],
            "content": "Robotics report..."
        },
        {
            "report_id": "RPT-004",
            "title": "HelioSync Edge Deployment Guide",
            "sector": "industrial_ai",
            "published_at": "2026-02-28",
            "tags": ["edge", "guide"],
            "summary": "Deployment guide missing the Fabric keyword (intentional interference).",
            "solution_aliases": ["HelioSync Edge"],
            "content": "Deployment guide..."
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # ========== presentations ==========
    presentations = [
        {
            "presentation_id": "PRES-001",
            "title": "HelioSync Product Overview",
            "owner": "partner_marketing",
            "updated_at": "2026-03-10",
            "tags": ["product", "edge", "overview"],
            "summary": "Slide deck introducing HelioSync features and target market.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Contains architecture diagrams."
        },
        {
            "presentation_id": "PRES-002",
            "title": "Partner Ecosystem Update",
            "owner": "strategy_team",
            "updated_at": "2026-03-12",
            "tags": ["partner", "ecosystem"],
            "summary": "Includes HelioSync integration case study with major logistics provider.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "EdgeCore"],
            "deck_notes": "Case study on slide 24-32."
        },
        {
            "presentation_id": "PRES-003",
            "title": "QuantumRoute Architecture",
            "owner": "research_design",
            "updated_at": "2026-02-20",
            "tags": ["quantum", "routing"],
            "summary": "Completely unrelated to HelioSync.",
            "solution_aliases": ["QuantumRoute"],
            "deck_notes": "No overlap."
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # ========== media_samples ==========
    media_samples = [
        {
            "sample_id": "MS-001",
            "title": "Podcast: Edge AI Revolution",
            "channel": "podcast_transcript",
            "captured_at": "2026-02-22",
            "tags": ["podcast", "edge", "AI"],
            "summary": "Interview with VP of Engineering on HelioSync rollout in smart factories.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Transcript of the podcast..."
        },
        {
            "sample_id": "MS-002",
            "title": "Keynote: AI at the Edge",
            "channel": "keynote_transcript",
            "captured_at": "2026-01-15",
            "tags": ["keynote", "edge"],
            "summary": "General edge AI keynote without specific solution mention.",
            "solution_aliases": [],
            "content": "Keynote transcript..."
        },
        {
            "sample_id": "MS-003",
            "title": "Editorial Draft: HelioSync Early Access",
            "channel": "editorial_draft",
            "captured_at": "2026-03-05",
            "tags": ["editorial", "early access"],
            "summary": "Draft article about HelioSync Edge (missing Fabric) – should not match.",
            "solution_aliases": ["HelioSync Edge"],
            "content": "Draft content..."
        },
        # 重复 ID 干扰：MS-001 的另一个版本，但 solution_aliases 不含目标（这样不会入选）
        {
            "sample_id": "MS-001",
            "title": "Old Podcast Version (Outdated)",
            "channel": "podcast_transcript",
            "captured_at": "2026-02-10",
            "tags": ["podcast"],
            "summary": "Earlier recording not mentioning HelioSync Fabric.",
            "solution_aliases": ["EdgeCore"],
            "content": "Old transcript..."
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # ========== 其他干扰文件 ==========
    os.makedirs("db_dumps", exist_ok=True)
    with open("db_dumps/backup_report.json", "w") as f:
        json.dump({"note": "This is a decoy file, not part of the task."}, f)

    # 在 accounts.json / contacts.json / attachments.json 中放入无关数据（可选）
    accounts = [
        {"account_id": "ACC-001", "display_name": "Alice", "department": "Engineering", "email": "alice@example.com", "permissions": ["read"], "default_region": "us-east", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "C-001", "name": "Dev Mehra", "role": "Archive Operations", "email": "dev.mehra@northstar.example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    attachments = [
        {"path": "solution_matching_notes.md", "title": "Solution Matching Notes", "kind": "matching_guide", "description": "Not relevant to this task."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

if __name__ == "__main__":
    build_env()
