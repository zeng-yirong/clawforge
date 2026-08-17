import os
import json

def build_env():
    reports = [
        {"id": "RPT-001", "title": "工业AI边缘推理部署报告", "sector": "industrial_ai",
         "published_at": "2026-01-15", "tags": ["edge", "industrial"], "summary": "HelioSync Edge Inference Fabric在工业场景实现毫秒级推理。",
         "solution_aliases": ["HelioSync Edge Inference Fabric"], "content": "详细部署方案..."},
        {"id": "RPT-002", "title": "HelioSync Edge初探", "sector": "industrial_ai",
         "published_at": "2025-11-01", "tags": ["edge"], "summary": "初步了解边缘计算概念。",
         "solution_aliases": ["HelioSync Edge Fabric"], "content": "早期研究..."},
        {"id": "RPT-003", "title": "物流AI变革白皮书", "sector": "logistics_ai",
         "published_at": "2026-02-20", "tags": ["logistics", "edge"], "summary": "HelioSync Edge Inference Fabric在物流分拣线实现实时决策。",
         "solution_aliases": ["HelioSync Edge Inference Fabric"], "content": "物流应用细节..."},
        {"id": "RPT-004", "title": "机器人导航技术", "sector": "robotics",
         "published_at": "2026-03-10", "tags": ["robotics"], "summary": "非相关技术。",
         "solution_aliases": ["SomeOther"], "content": "其他内容..."}
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    presentations = [
        {"id": "PRES-001", "title": "边缘计算概览", "owner": "partner_marketing",
         "updated_at": "2026-01-10", "tags": ["edge"], "summary": "边缘计算基础概念。",
         "solution_aliases": ["HelioSync Edge"], "deck_notes": "无针对性内容。"},
        {"id": "PRES-002", "title": "Q2边缘计算战略演示", "owner": "strategy_team",
         "updated_at": "2026-02-05", "tags": ["edge", "strategy"], "summary": "HelioSync Edge Inference Fabric是下一代边缘计算核心。",
         "solution_aliases": ["HelioSync Edge Inference Fabric"], "deck_notes": "重点介绍部署路径。"},
        {"id": "PRES-003", "title": "行业周报分享", "owner": "research_design",
         "updated_at": "2026-01-20", "tags": ["general"], "summary": "不涉及目标技术。",
         "solution_aliases": ["Other"], "deck_notes": "无关。"}
    ]
    os.makedirs("presentations", exist_ok=True)
    with open("presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    media_samples = [
        {"id": "MED-001", "title": "科技前沿播客访谈", "channel": "podcast_transcript",
         "captured_at": "2026-02-28", "tags": ["edge", "podcast"], "summary": "我们深度讨论了HelioSync Edge Inference Fabric的架构设计。",
         "solution_aliases": ["HelioSync Edge Inference Fabric"], "content": "播客全文..."},
        {"id": "MED-002", "title": "市场分析报告", "channel": "editorial_draft",
         "captured_at": "2026-01-05", "tags": ["market"], "summary": "无关内容。",
         "solution_aliases": ["Other"], "content": "分析全文..."},
        {"id": "MED-003", "title": "边缘计算主题演讲", "channel": "keynote_transcript",
         "captured_at": "2026-03-01", "tags": ["edge", "keynote"], "summary": "讲解边缘推理框架。",
         "solution_aliases": ["HelioSync Edge"], "content": "提到HelioSync Edge但未提Inference Fabric。"}
    ]
    os.makedirs("media_samples", exist_ok=True)
    with open("media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
