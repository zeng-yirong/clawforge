import os
import json

def build_env():
    # 确保工作区根目录已存在（当前cwd即是.）
    root = os.getcwd()
    
    # 创建必要的子目录
    dirs = [
        "data/reports",
        "data/presentations",
        "data/media_samples",
        "data/attachments",
        "ops"
    ]
    for d in dirs:
        os.makedirs(os.path.join(root, d), exist_ok=True)
    
    # ── data/reports/reports.json ──
    reports = [
        {
            "report_id": "report_001",
            "title": "Edge Inference in Smart Logistics",
            "sector": "logistics_ai",
            "published_at": "2026-02-10",
            "tags": ["edge", "inference", "logistics"],
            "summary": "HelioSync Edge Inference Fabric is used in smart logistics for real-time AI at the edge.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF"],
            "content": "Detailed report content..."
        },
        {
            "report_id": "report_002",
            "title": "NovaCore AI Platform Review",
            "sector": "industrial_ai",
            "published_at": "2026-01-15",
            "tags": ["AI", "platform"],
            "summary": "NovaCore provides centralized AI training.",
            "solution_aliases": ["NovaCore AI"],
            "content": "NovaCore details..."
        },
        {
            "report_id": "report_003",
            "title": "TensorFlow Edge Deployment Guide",
            "sector": "robotics",
            "published_at": "2025-11-20",
            "tags": ["tensorflow", "edge"],
            "summary": "Guide to deploying TensorFlow models on edge devices.",
            "solution_aliases": ["TensorFlow Edge"],
            "content": "TF Edge guide..."
        }
    ]
    with open(os.path.join(root, "data/reports/reports.json"), "w") as f:
        json.dump({"reports": reports}, f, indent=2)
    
    # ── data/presentations/presentations.json ──
    presentations = [
        {
            "presentation_id": "pres_001",
            "title": "HEIF Deployment in Manufacturing",
            "owner": "partner_marketing",
            "updated_at": "2026-03-01",
            "tags": ["manufacturing", "edge"],
            "summary": "Presentation on HEIF deployment in manufacturing.",
            "solution_aliases": ["HEIF", "HelioSync"],
            "deck_notes": "Notes..."
        },
        {
            "presentation_id": "pres_002",
            "title": "Cloud AI vs Edge AI",
            "owner": "strategy_team",
            "updated_at": "2026-02-20",
            "tags": ["strategy", "comparison"],
            "summary": "Comparing cloud and edge AI approaches.",
            "solution_aliases": ["Cloud AI"],
            "deck_notes": "Notes..."
        },
        {
            "presentation_id": "pres_003",
            "title": "Robotics Vision Update",
            "owner": "research_design",
            "updated_at": "2025-12-05",
            "tags": ["robotics", "vision"],
            "summary": "Latest vision models for robotics.",
            "solution_aliases": ["Vision AI"],
            "deck_notes": "Notes..."
        }
    ]
    with open(os.path.join(root, "data/presentations/presentations.json"), "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)
    
    # ── data/media_samples/media_samples.json ──
    media_samples = [
        {
            "sample_id": "media_001",
            "title": "Edge Inference in Chinese Market",
            "channel": "podcast_transcript",
            "captured_at": "2026-03-15",
            "tags": ["china", "edge", "inference"],
            "summary": "Podcast discussing edge inference frameworks in Chinese market.",
            "solution_aliases": ["边缘推理框架", "HelioSync"],
            "content": "Transcript content..."
        },
        {
            "sample_id": "media_002",
            "title": "AI Safety Standards",
            "channel": "keynote_transcript",
            "captured_at": "2026-01-30",
            "tags": ["safety", "standards"],
            "summary": "Keynote on AI safety standards.",
            "solution_aliases": ["AI Safety"],
            "content": "Safety transcript..."
        },
        {
            "sample_id": "media_003",
            "title": "Edge Computing 101",
            "channel": "editorial_draft",
            "captured_at": "2025-10-10",
            "tags": ["edge", "introduction"],
            "summary": "Introductory article on edge computing.",
            "solution_aliases": ["Edge Computing"],
            "content": "Draft content..."
        }
    ]
    with open(os.path.join(root, "data/media_samples/media_samples.json"), "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)
    
    # ── data/attachments/solution_matching_notes.md ──
    notes_content = """# Solution Matching Notes

When identifying documents related to HelioSync Edge Inference Fabric, use the following aliases (case-insensitive):
- HelioSync Edge Inference Fabric
- HEIF
- 边缘推理框架

A document is considered a match if its `solution_aliases` list contains any of the above strings (exact match after lowercasing).
"""
    with open(os.path.join(root, "data/attachments/solution_matching_notes.md"), "w") as f:
        f.write(notes_content)
    
    # 其他附件（占位）
    with open(os.path.join(root, "data/attachments/temp_record_guidelines.md"), "w") as f:
        f.write("# Temporary Record Guidelines\nPlaceholder.\n")
    
    # 可选：accounts.json 和 contacts.json（仅供上下文，agent不需要）
    accounts = [
        {"account_id": "acc_001", "display_name": "Nebula AI", "department": "R&D", "email": "contact@nebula.example.com", "permissions": ["read"], "default_region": "us-east", "voice": ["en"]}
    ]
    with open(os.path.join(root, "data/accounts.json"), "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)
    
    contacts = [
        {"contact_id": "c_001", "name": "Rhea Morita", "role": "Signal Research Lead", "email": "rhea.morita@northstar.example.com"}
    ]
    with open(os.path.join(root, "data/contacts.json"), "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)
    
    # ops 目录已创建，不写任何文件，留给 agent

if __name__ == "__main__":
    build_env()
