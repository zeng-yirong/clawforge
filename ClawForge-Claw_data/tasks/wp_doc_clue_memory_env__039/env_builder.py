import os
import json

def build_env():
    # 创建所有需要的子目录（cwd 已为 .）
    dirs = [
        "data/reports",
        "data/presentations",
        "data/media_samples",
        "data/attachments",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ---------- 1. 报告 ----------
    reports = [
        {
            "report_id": "report-001",
            "title": "HelioSync Edge Inference Fabric Performance Benchmark",
            "sector": "industrial_ai",
            "published_at": "2026-02-10",
            "tags": ["published", "benchmark"],
            "summary": "Latency measurements under load.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": (
                "We tested the HelioSync Edge Inference Fabric across multiple edge nodes.\n"
                "# Clue: Real-time edge inference at 2ms latency.\n"
                "The system maintained consistent throughput."
            )
        },
        {
            "report_id": "report-002",
            "title": "AetherNet Distributed Inference Analysis",
            "sector": "robotics",
            "published_at": "2026-01-20",
            "tags": ["published", "analysis"],
            "summary": "Comparison of distributed inference frameworks.",
            "solution_aliases": ["AetherNet"],
            "content": (
                "AetherNet provides a viable alternative to cloud-based inference.\n"
                "# Clue: AetherNet achieves 50ms latency in simulation.\n"
                "Further optimization is required."
            )
        },
        {
            "report_id": "report-003",
            "title": "HelioSync AI Bandwidth Optimization Report",
            "sector": "logistics_ai",
            "published_at": "2026-03-05",
            "tags": ["published", "optimization"],
            "summary": "Reducing backhaul bandwidth using HelioSync AI.",
            "solution_aliases": ["HelioSync AI"],
            "content": (
                "We deployed HelioSync AI in a real logistics network.\n"
                "# Clue: HelioSync AI can reduce bandwidth by 40%.\n"
                "The results were consistent over two weeks."
            )
        },
        {
            "report_id": "report-004",
            "title": "HelioSync AI Draft Architecture Review",
            "sector": "industrial_ai",
            "published_at": "2026-02-28",
            "tags": ["draft", "internal"],
            "summary": "Internal draft of HelioSync AI architecture.",
            "solution_aliases": ["HelioSync AI"],
            "content": (
                "This is a preliminary draft not ready for release.\n"
                "# Clue: Draft version not ready.\n"
                "Do not use for external presentations."
            )
        },
        {
            "report_id": "report-005",
            "title": "Edge Computing Survey: HelioSync Edge",
            "sector": "robotics",
            "published_at": "2026-03-10",
            "tags": ["published", "survey"],
            "summary": "Survey includes partial mention of HelioSync Edge.",
            "solution_aliases": ["HelioSync Edge"],
            "content": (
                "HelioSync Edge is a subset of the larger fabric.\n"
                "# Clue: Partial match.\n"
                "Not the complete solution."
            )
        }
    ]
    with open("data/reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # ---------- 2. 演示 ----------
    presentations = [
        {
            "presentation_id": "pres-001",
            "title": "QuantumLoop Next-Gen Inference",
            "owner": "partner_marketing",
            "updated_at": "2026-02-15",
            "tags": ["published", "marketing"],
            "summary": "Overview of QuantumLoop inference engine.",
            "solution_aliases": ["QuantumLoop"],
            "deck_notes": "No mention of HelioSync.",
            "content": (
                "QuantumLoop delivers 1000 inferences per second.\n"
                "# Clue: QuantumLoop TPS benchmark.\n"
                "Not related to HelioSync."
            )
        },
        {
            "presentation_id": "pres-002",
            "title": "Deploying HelioSync Edge Fabric in 5G Networks",
            "owner": "strategy_team",
            "updated_at": "2026-03-01",
            "tags": ["published", "strategy"],
            "summary": "Technical deployment guide for HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Includes network topology diagrams.",
            "content": (
                "The HelioSync Edge Inference Fabric integrates seamlessly with 5G.\n"
                "# Clue: Edge fabric deployment in 5G networks.\n"
                "See appendix for detailed architecture."
            )
        },
        {
            "presentation_id": "pres-003",
            "title": "HelioSync AI Early Concepts (Draft)",
            "owner": "research_design",
            "updated_at": "2026-02-20",
            "tags": ["draft", "research"],
            "summary": "Early draft of HelioSync AI design.",
            "solution_aliases": ["HelioSync AI"],
            "deck_notes": "Not approved for external use.",
            "content": (
                "Early ideas around HelioSync AI.\n"
                "# Clue: Draft.\n"
                "Should not be included."
            )
        }
    ]
    with open("data/presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # ---------- 3. 媒体样本 ----------
    media_samples = [
        {
            "sample_id": "media-001",
            "title": "Podcast: CTO on HelioSync Edge Fabric",
            "channel": "podcast_transcript",
            "captured_at": "2026-03-02",
            "tags": ["published", "podcast"],
            "summary": "Interview with CTO discussing edge inference.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": (
                "In this episode we dive deep into the HelioSync Edge Inference Fabric.\n"
                "# Clue: Podcast interview with CTO on HelioSync.\n"
                "The CTO highlighted the 2ms latency achievement."
            )
        },
        {
            "sample_id": "media-002",
            "title": "AetherNet Webinar Recording",
            "channel": "editorial_draft",
            "captured_at": "2026-02-25",
            "tags": ["published", "webinar"],
            "summary": "Webinar on AetherNet deployment.",
            "solution_aliases": ["AetherNet"],
            "content": (
                "AetherNet webinar content.\n"
                "# Clue: AetherNet webinar.\n"
                "No HelioSync references."
            )
        }
    ]
    with open("data/media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

    # ---------- 4. 附件 ----------
    # 解决方案匹配指南
    solution_notes = """# Solution Matching Notes

## Expected clue list format

Write the results to `ops/clue_list.json` as an array of objects.
Each object must include:

- `document_id`: the report_id, presentation_id, or sample_id of the matched document.
- `type`: one of "report", "presentation", "media".
- `title`: the original title field from the document.
- `clue`: the text that appears after `# Clue: ` in the document's content (do not include the prefix).

Example:
[
  {
    "document_id": "report-001",
    "type": "report",
    "title": "HelioSync Edge Inference Fabric Performance Benchmark",
    "clue": "Real-time edge inference at 2ms latency."
  }
]
"""
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write(solution_notes)

    # 临时记录指南（纯粹干扰）
    temp_guidelines = """# Temporary Record Guidelines

This file describes how to store temporary clue records during a session.
It is not needed for the final output.
"""
    with open("data/attachments/temp_record_guidelines.md", "w") as f:
        f.write(temp_guidelines)

if __name__ == "__main__":
    build_env()
