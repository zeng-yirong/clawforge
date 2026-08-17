import os
import json

def build_env():
    # 创建三个子目录
    for d in ("reports", "presentations", "media_samples"):
        os.makedirs(d, exist_ok=True)

    # ---------- reports ----------
    reports = [
        {
            "report_id": "RPT-2026-Q2-013",
            "title": "Edge AI Deployment in Industrial IoT",
            "sector": "industrial_ai",
            "published_at": "2026-05-20",
            "tags": ["edge_inference", "iot", "heliosync"],
            "summary": "Deployment report for HelioSync Edge Inference Fabric in factory floor.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "HEIF"],
            "content": "The rollout covered 12 sites. CLUE: HYDRA-7X. Latency dropped by 40%."
        },
        {
            "report_id": "RPT-2026-Q2-999",
            "title": "Classic Edge Migration Study",
            "sector": "industrial_ai",
            "published_at": "2026-06-01",
            "tags": ["edge", "legacy"],
            "summary": "Legacy HelioSync Classic Edge analysis.",
            "solution_aliases": ["HelioSync Classic Edge", "HCE"],
            "content": "The classic version lacks dynamic routing. CLUE: PHANTOM-1."
        },
        {
            "report_id": "RPT-2026-Q2-077",
            "title": "Warehouse Robotics Update",
            "sector": "robotics",
            "published_at": "2026-05-10",
            "tags": ["warehouse", "robotics"],
            "summary": "No relevant solution mentioned.",
            "solution_aliases": ["WareRobo"],
            "content": "Standard warehouse operations. No clue here."
        }
    ]
    # 缺失 solution_aliases 的 dirty record
    reports.append({
        "report_id": "RPT-DIRTY-001",
        "title": "Corrupted Data Point",
        "sector": "logistics_ai",
        "published_at": "2026-04-01",
        "tags": [],
        "summary": "Incomplete record.",
        "content": "Missing aliases field."
    })
    with open("reports/reports.json", "w") as f:
        json.dump({"reports": reports}, f, indent=2)

    # ---------- presentations ----------
    presentations = [
        {
            "presentation_id": "PRES-2026-Q2-007",
            "title": "HelioSync Fabric Pitch Deck",
            "owner": "partner_marketing",
            "updated_at": "2026-05-25",
            "tags": ["edge", "fabric", "pitch"],
            "summary": "Deck highlighting HelioSync Edge Inference Fabric benefits.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Slide 7 shows performance benchmarks.",
            "content": "CLUE: ZETA-22. The fabric supports sub-5ms latency."
        },
        {
            "presentation_id": "PRES-2026-Q2-021",
            "title": "General Edge Inference Trends",
            "owner": "research_design",
            "updated_at": "2026-06-03",
            "tags": ["trends", "edge"],
            "summary": "Covers multiple edge inference solutions.",
            "solution_aliases": ["Edge Inference Fabric"],  # 缺少 HelioSync
            "deck_notes": "No specific vendor mentioned.",
            "content": "CLUE: OMEGA-9. Generic discussion."
        },
        {
            "presentation_id": "PRES-2026-Q2-100",
            "title": "Q2 Internal Review",
            "owner": "strategy_team",
            "updated_at": "2026-06-10",
            "tags": ["review"],
            "summary": "Quarterly review deck.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Mentions fabric in passing.",
            "content": "CLUE: KAPPA-13. This is a duplicate entry to be ignored if agent correctly deduplicates? We'll keep it to test strictness."
        }
    ]
    with open("presentations/presentations.json", "w") as f:
        json.dump({"presentations": presentations}, f, indent=2)

    # ---------- media_samples ----------
    media_samples = [
        {
            "sample_id": "MED-2026-Q2-021",
            "title": "Podcast: Fabric Deep Dive",
            "channel": "podcast_transcript",
            "captured_at": "2026-05-22",
            "tags": ["heliosync", "podcast"],
            "summary": "Transcript discussing HelioSync Edge Inference Fabric architecture.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "CLUE: THETA-5B. The fabric uses a novel consensus algorithm."
        },
        {
            "sample_id": "MED-2026-Q2-045",
            "title": "Editorial Draft: Edge AI Roundup",
            "channel": "editorial_draft",
            "captured_at": "2026-06-05",
            "tags": ["edge", "ai"],
            "summary": "Covers various edge AI products including HelioSync Classic.",
            "solution_aliases": ["HelioSync Classic Edge"],
            "content": "CLUE: LAMBDA-7. Not our target."
        }
    ]
    with open("media_samples/media_samples.json", "w") as f:
        json.dump({"media_samples": media_samples}, f, indent=2)

if __name__ == "__main__":
    build_env()
