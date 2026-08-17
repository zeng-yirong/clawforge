import os
import json
import random

def build_env():
    # --- 确保目录结构 ---
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # ====== 行业报告 ======
    reports = [
        {
            "report_id": "rpt-021",
            "title": "边缘推理在工业AI中的应用",
            "sector": "industrial_ai",
            "published_at": "2025-11-15",
            "tags": ["edge", "inference", "HelioSync"],
            "summary": "HelioSync 架构在5ms延迟内实现了边缘推理，适用于工业质检场景。",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "详细内容略..."
        },
        {
            "report_id": "rpt-045",
            "title": "物流AI中的HelioSync集成案例",
            "sector": "logistics_ai",
            "published_at": "2026-01-20",
            "tags": ["logistics", "HelioSync"],
            "summary": "案例研究显示HelioSync在物流分拣中降低了30%的延迟。",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "Kronos Edge"],
            "content": "详细内容略..."
        },
        {
            "report_id": "rpt-099",
            "title": "Aurora AI在机器人领域的部署",
            "sector": "robotics",
            "published_at": "2025-09-10",
            "tags": ["robotics", "Aurora"],
            "summary": "Aurora AI边缘计算方案在机器人视觉中的表现。",
            "solution_aliases": ["Aurora AI Edge"],
            "content": "详细内容略..."
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # ====== 演示文稿 ======
    presentations = [
        {
            "presentation_id": "pres-010",
            "title": "HelioSync 合作伙伴启动会",
            "owner": "partner_marketing",
            "updated_at": "2026-02-01",
            "tags": ["HelioSync", "launch", "partner"],
            "summary": "面向合作伙伴的HelioSync发布演示，涵盖架构与路线图。",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "包含关键客户案例。"
        },
        {
            "presentation_id": "pres-032",
            "title": "Kronos Edge 硬件评估",
            "owner": "research_design",
            "updated_at": "2025-12-10",
            "tags": ["Kronos", "edge", "hardware"],
            "summary": "Kronos Edge硬件与竞品对比分析。",
            "solution_aliases": ["Kronos Edge"],
            "deck_notes": "无"
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # ====== 媒体素材 ======
    media_samples = [
        {
            "sample_id": "med-003",
            "title": "播客：HelioSync 边缘计算实战",
            "channel": "podcast_transcript",
            "captured_at": "2026-01-28",
            "tags": ["HelioSync", "podcast", "edge"],
            "summary": "讨论了HelioSync在工业边缘场景下的部署难点与收益。",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "完整播客文本..."
        },
        {
            "sample_id": "med-017",
            "title": "Aurora AI 产品发布编辑稿",
            "channel": "editorial_draft",
            "captured_at": "2025-11-20",
            "tags": ["Aurora", "launch"],
            "summary": "Aurora AI 边缘推理产品正式发布。",
            "solution_aliases": ["Aurora AI Edge"],
            "content": "全文..."
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # ====== 其他干扰文件 ======
    # 一个无关的 accounts.json
    accounts = [
        {"account_id": "acc-01", "display_name": "Acme Corp", "department": "logistics", "email": "info@acme.com", "permissions": ["read"], "default_region": "us-east", "voice": ["en"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # attachments.json（不包含目标方案）
    attachments = [
        {"path": "solution_matching_notes.md", "title": "Solution Matching Notes", "kind": "matching_guide", "description": "如何匹配方案别名。"},
        {"path": "temp_record_guidelines.md", "title": "Temporary Record Guidelines", "kind": "record_schema", "description": "临时记录格式。"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 一个额外的未使用文件，模拟脏数据
    with open("data/reports/.old_cache.json", "w") as f:
        f.write("{corrupted: true")

if __name__ == "__main__":
    build_env()
