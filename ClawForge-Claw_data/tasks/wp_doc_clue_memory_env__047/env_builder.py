import os
import json

def build_env():
    # 确保容器工作区根目录
    # cwd 已经由 runtime 设置为 
    # 直接使用相对路径

    # ==================== 数据目录 ====================
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # ==================== 匹配指南文件 ====================
    guide_content = """# Solution Matching Notes

When searching for documents related to a target technology solution, use the following criteria:
- Only consider documents where `solution_aliases` (array in JSON) contains the exact target solution string (case-sensitive).
- Exclude any documents that are missing the `solution_aliases` field or have an empty array.
- For each matching document, extract:
  - doc_id: the unique identifier from the document (e.g., report_id, presentation_id, sample_id)
  - doc_type: one of "report", "presentation", "media_sample"
  - title: the document title
  - clue_bullet: the document's summary (use `summary` field; if `summary` is not present, fallback to `deck_notes` for presentations, but all relevant documents have a summary)
Save the results as a JSON array in a file named `clue_list.json` in the workplace root.
"""
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write(guide_content)

    # ==================== accounts.json (干扰项) ====================
    accounts = {
        "accounts": [
            {
                "account_id": "ACC-001",
                "display_name": "NovaTech Industries",
                "department": "Engineering",
                "email": "contact@novatech.example.com",
                "permissions": ["read", "write"],
                "default_region": "us-east-1",
                "voice": ["en-US"]
            },
            {
                "account_id": "ACC-002",
                "display_name": "HelioSync Corp",
                "department": "Product",
                "email": "info@heliosync.example.com",
                "permissions": ["admin"],
                "default_region": "eu-west-1",
                "voice": ["en-GB"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ==================== contacts.json (干扰项) ====================
    contacts = {
        "contacts": [
            {
                "contact_id": "CT-101",
                "name": "Dev Mehra",
                "role": "Archive Operations",
                "email": "dev.mehra@northstar.example.com"
            },
            {
                "contact_id": "CT-102",
                "name": "Keiko Han",
                "role": "Market Intelligence Partner",
                "email": "keiko.han@northstar.example.com"
            },
            {
                "contact_id": "CT-103",
                "name": "Rhea Morita",
                "role": "Signal Research Lead",
                "email": "rhea.morita@northstar.example.com"
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ==================== reports.json ====================
    reports = {
        "reports": [
            {
                "report_id": "RPT-2026-042",
                "title": "Industrial AI Market Analysis 2026 Q2",
                "sector": "industrial_ai",
                "published_at": "2026-05-15",
                "tags": ["edge inference", "industrial AI", "HelioSync"],
                "summary": "This report examines the adoption of HelioSync Edge Inference Fabric across manufacturing sectors.",
                "solution_aliases": ["HelioSync Edge Inference Fabric", "Neural Edge"],
                "content": "Detailed market analysis..."
            },
            {
                "report_id": "RPT-2026-071",
                "title": "Logistics AI Trends 2026",
                "sector": "logistics_ai",
                "published_at": "2026-06-01",
                "tags": ["logistics", "edge"],
                "summary": "Overview of edge AI in logistics, including legacy HelioSync Edge Inference Fabric v1 deployments.",
                "solution_aliases": ["HelioSync Edge Inference Fabric v1"],
                "content": "Legacy systems..."
            },
            {
                "report_id": "RPT-2025-099",
                "title": "Robotics Edge Survey",
                "sector": "robotics",
                "published_at": "2025-12-10",
                "tags": ["robotics", "edge"],
                "summary": "Survey of edge computing solutions for robotics (no specific vendor).",
                "solution_aliases": []
                # 空的 solution_aliases，应排除
            },
            {
                "report_id": "RPT-2026-113",
                "title": "AI Hardware Benchmark 2026",
                "sector": "industrial_ai",
                "published_at": "2026-07-20",
                "tags": ["benchmark", "HelioSync"],
                "summary": "Benchmark results for various AI accelerators; HelioSync Edge Inference Fabric is mentioned in passing.",
                # missing solution_aliases field -> 应排除
                "content": "Benchmark data..."
            }
        ]
    }
    with open("data/reports/reports.json", "w") as f:
        json.dump(reports, f, indent=2)

    # ==================== presentations.json ====================
    presentations = {
        "presentations": [
            {
                "presentation_id": "PRES-2026-021",
                "title": "HelioSync Edge Architecture Overview",
                "owner": "strategy_team",
                "updated_at": "2026-04-28",
                "tags": ["edge", "architecture", "HelioSync"],
                "summary": "Detailed architecture of HelioSync Edge Inference Fabric and its deployment patterns.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "deck_notes": "Includes network topology and hardware specs."
            },
            {
                "presentation_id": "PRES-2026-022",
                "title": "Edge Inference at Scale",
                "owner": "partner_marketing",
                "updated_at": "2026-05-10",
                "tags": ["scaling", "edge", "HelioSync"],
                "summary": "Scaling strategies for HelioSync Edge Inference Fabric in large-scale deployments.",
                "solution_aliases": ["HelioSync Edge Inference Fabric", "Edge Runtime"],
                "deck_notes": "Case studies from two deployments."
            },
            {
                "presentation_id": "PRES-2025-045",
                "title": "Edge Runtime Overview",
                "owner": "research_design",
                "updated_at": "2025-11-20",
                "tags": ["edge runtime"],
                "summary": "General overview of Edge Runtime (not tied to HelioSync).",
                "solution_aliases": ["Edge Runtime"],
                "deck_notes": "No HelioSync reference."
            },
            {
                "presentation_id": "PRES-2026-033",
                "title": "HelioSync Edge v1 Migration",
                "owner": "strategy_team",
                "updated_at": "2026-06-12",
                "tags": ["migration", "HelioSync"],
                "summary": "Migration path from HelioSync Edge Inference Fabric v1 to v2.",
                "solution_aliases": ["heliosync edge inference fabric"],  # 小写，不匹配
                "deck_notes": "Legacy migration."
            }
        ]
    }
    with open("data/presentations/presentations.json", "w") as f:
        json.dump(presentations, f, indent=2)

    # ==================== media_samples.json ====================
    media_samples = {
        "media_samples": [
            {
                "sample_id": "MED-2026-019",
                "title": "Podcast: Edge Inference Revolution",
                "channel": "podcast_transcript",
                "captured_at": "2026-05-22",
                "tags": ["podcast", "HelioSync", "edge"],
                "summary": "Discussion on how HelioSync Edge Inference Fabric is transforming real-time AI inference.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "Transcript of the podcast..."
            },
            {
                "sample_id": "MED-2026-020",
                "title": "Keynote: HelioSync Edge at Industrie 4.0",
                "channel": "keynote_transcript",
                "captured_at": "2026-06-05",
                "tags": ["keynote", "HelioSync", "edge"],
                "summary": "Keynote presentation introducing HelioSync Edge Inference Fabric for smart factories.",
                "solution_aliases": ["HelioSync Edge Inference Fabric"],
                "content": "Keynote transcript..."
            },
            {
                "sample_id": "MED-2025-101",
                "title": "Editorial Draft: Edge AI Trends",
                "channel": "editorial_draft",
                "captured_at": "2025-09-18",
                "tags": ["editorial", "edge"],
                "summary": "Draft article about edge AI trends, no specific vendor.",
                "solution_aliases": ["General Edge"],
                "content": "Draft content..."
            },
            {
                "sample_id": "MED-2026-022",
                "title": "Podcast: HelioSync v1 Recap",
                "channel": "podcast_transcript",
                "captured_at": "2026-07-01",
                "tags": ["HelioSync", "v1"],
                "summary": "Recap of HelioSync Edge Inference Fabric v1 features and limitations.",
                "solution_aliases": ["HelioSync Edge Inference Fabric v1"],
                "content": "Transcript..."
            }
        ]
    }
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump(media_samples, f, indent=2)

    # ==================== 额外干扰目录 ====================
    os.makedirs("data/obsolete", exist_ok=True)
    with open("data/obsolete/reports_2024.json", "w") as f:
        json.dump({"reports": []}, f)
    os.makedirs("backup", exist_ok=True)
    with open("backup/old_presentations.json", "w") as f:
        json.dump({"presentations": []}, f)

if __name__ == "__main__":
    build_env()
