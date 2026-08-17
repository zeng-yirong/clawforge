import os
import json
import random

def build_env():
    # 确保 ops 目录存在
    os.makedirs("ops", exist_ok=True)

    # ========== 数据定义 ==========
    # 正确匹配的方案名称
    target = "HelioSync Edge Inference Fabric"

    # ---- 报告 ----
    reports = [
        {
            "report_id": "RPT-2024-001",
            "title": "Edge AI Landscape 2024",
            "sector": "industrial_ai",
            "published_at": "2024-02-15",
            "tags": ["edge", "AI", "industrial"],
            "summary": "HelioSync Edge Inference Fabric 在工业视觉检测中实现了99.2%的准确率，彻底改变了传统方案。",
            "solution_aliases": [target, "Edge AI Suite"]
        },
        {
            "report_id": "RPT-2024-002",
            "title": "Industrial Automation Quarterly",
            "sector": "industrial_ai",
            "published_at": "2024-05-20",
            "tags": ["automation", "edge"],
            "summary": "多家工厂部署了基于HelioSync Edge Inference Fabric的实时质检系统，产能提升30%。",
            "solution_aliases": [target, "StreamAnalytics"]
        },
        {
            "report_id": "RPT-2024-003",
            "title": "Logistics AI Review",
            "sector": "logistics_ai",
            "published_at": "2024-08-10",
            "tags": ["logistics", "AI", "edge"],
            "summary": "HelioSync Edge Inference Fabric 被集成到仓储自动导引车中，路径规划延迟低于5ms。",
            "solution_aliases": [target]
        },
        # 干扰项：名字接近但不完全匹配
        {
            "report_id": "RPT-2024-004",
            "title": "Robotics Innovation Report",
            "sector": "robotics",
            "published_at": "2024-11-01",
            "tags": ["robotics", "edge"],
            "summary": "HelioSync Edge 在机器人抓取任务中表现优异，但缺少推理加速单元。",
            "solution_aliases": ["HelioSync Edge", "Inference Fabric"]  # 拆开了
        },
        {
            "report_id": "RPT-2024-005",
            "title": "Smart Factory Case Studies",
            "sector": "industrial_ai",
            "published_at": "2024-03-22",
            "tags": ["factory", "case study"],
            "summary": "我们评估了HelioSync Fabric方案，发现其在低功耗场景下优势明显。",
            "solution_aliases": ["HelioSync Fabric"]  # 缺少 Edge 和 Inference
        },
        # 重复/过时的记录（应当忽略，但内容正确）
        {
            "report_id": "RPT-2024-001",  # 重复ID
            "title": "Edge AI Landscape 2024 (v2)",
            "sector": "industrial_ai",
            "published_at": "2024-02-10",
            "tags": ["edge", "AI", "industrial"],
            "summary": "旧版摘要：HelioSync Edge Inference Fabric初步验证通过。",
            "solution_aliases": [target]
        },
        {
            "report_id": "RPT-2024-003",  # 重复ID（但内容不同，视为过时）
            "title": "Logistics AI Review (draft)",
            "sector": "logistics_ai",
            "published_at": "2024-07-01",
            "tags": ["draft"],
            "summary": "草稿：HelioSync Edge Inference Fabric预期延迟低于10ms。",
            "solution_aliases": [target]
        }
    ]

    # ---- 演示 ----
    presentations = [
        {
            "presentation_id": "PRES-2024-A1",
            "title": "Partner Marketing: HelioSync Overview",
            "owner": "partner_marketing",
            "updated_at": "2024-06-15",
            "tags": ["partner", "overview"],
            "summary": "HelioSync Edge Inference Fabric是下一代边缘推理平台，支持多模型并发。",
            "solution_aliases": [target, "Edge AI Suite"],
            "deck_notes": "内部仅供合作伙伴"
        },
        {
            "presentation_id": "PRES-2024-B2",
            "title": "Research Design: Edge Inference Benchmark",
            "owner": "research_design",
            "updated_at": "2024-09-01",
            "tags": ["benchmark", "research"],
            "summary": "对比测试显示HelioSync Edge Inference Fabric的吞吐量是竞品的2.3倍。",
            "solution_aliases": [target]
        },
        # 干扰项
        {
            "presentation_id": "PRES-2024-C3",
            "title": "Strategy Team: New Product Roadmap",
            "owner": "strategy_team",
            "updated_at": "2024-04-20",
            "tags": ["roadmap"],
            "summary": "下一代产品将基于HelioSync Edge Inference Fabric开发，但尚未确认。",
            "solution_aliases": [target]  # 实际上包含，但内容为“尚未确认”，仍是有效线索
        },
        {
            "presentation_id": "PRES-2024-D4",
            "title": "Legacy Edge Inference",
            "owner": "research_design",
            "updated_at": "2023-12-01",
            "tags": ["legacy"],
            "summary": "旧版方案HelioSync Edge Inference Fabric已被弃用，不再维护。",
            "solution_aliases": [target]  # 虽然过时，但包含目标名称，Agent应该保留（提示说忽略明显过时版本，但这里ID不同，且日期较旧，可以认为是有效记录？为了唯一性，我们规定：重复ID才忽略，不同ID即使旧也保留。此处ID不同，应保留）
        }
    ]

    # ---- 媒体样本 ----
    media_samples = [
        {
            "sample_id": "MED-2024-K01",
            "title": "Keynote: HelioSync Launch Event",
            "channel": "keynote_transcript",
            "captured_at": "2024-07-30",
            "tags": ["launch", "keynote"],
            "summary": "HelioSync Edge Inference Fabric正式发布，首批用户包括三家世界500强企业。",
            "solution_aliases": [target, "Edge AI Suite"],
            "content": "（完整内容省略）"
        },
        {
            "sample_id": "MED-2024-P02",
            "title": "Podcast: Edge AI Deep Dive",
            "channel": "podcast_transcript",
            "captured_at": "2024-08-15",
            "tags": ["podcast", "deep dive"],
            "summary": "技术专家深入解析HelioSync Edge Inference Fabric的架构设计。",
            "solution_aliases": [target],
            "content": "..."
        },
        {
            "sample_id": "MED-2024-E03",
            "title": "Editorial Draft: HelioSync Case Study",
            "channel": "editorial_draft",
            "captured_at": "2024-09-01",
            "tags": ["case study", "draft"],
            "summary": "HelioSync Edge Inference Fabric 在智慧零售场景的落地分析。",
            "solution_aliases": [target]
        },
        # 干扰：名字不完整
        {
            "sample_id": "MED-2024-P04",
            "title": "Podcast: Edge Inference Trends",
            "channel": "podcast_transcript",
            "captured_at": "2024-05-10",
            "tags": ["trends"],
            "summary": "讨论HelioSync Edge Inference的局限性，未提及Fabric。",
            "solution_aliases": ["HelioSync Edge Inference"]  # 缺少Fabric
        }
    ]

    # ---- 写入文件 ----
    os.makedirs("data/reports", exist_ok=True)
    os.makedirs("data/presentations", exist_ok=True)
    os.makedirs("data/media_samples", exist_ok=True)

    with open("data/reports/reports.json", "w", encoding="utf-8") as f:
        json.dump({"reports": reports}, f, indent=2, ensure_ascii=False)

    with open("data/presentations/presentations.json", "w", encoding="utf-8") as f:
        json.dump({"presentations": presentations}, f, indent=2, ensure_ascii=False)

    with open("data/media_samples/media_samples.json", "w", encoding="utf-8") as f:
        json.dump({"media_samples": media_samples}, f, indent=2, ensure_ascii=False)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
