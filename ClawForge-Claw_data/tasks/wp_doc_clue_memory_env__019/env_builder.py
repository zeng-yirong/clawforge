import os
import json
import random
import shutil

def build_env():
    """Build initial file tree for doc_clue_memory_env task 019."""
    # Clean slate
    if os.path.exists("reports"):
        shutil.rmtree("reports")
    if os.path.exists("presentations"):
        shutil.rmtree("presentations")
    if os.path.exists("media_samples"):
        shutil.rmtree("media_samples")
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    os.makedirs("reports", exist_ok=True)
    os.makedirs("presentations", exist_ok=True)
    os.makedirs("media_samples", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Helper to write JSON file ---
    def write_json(subdir, filename, data):
        path = os.path.join(subdir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ========================
    # Reports
    # ========================
    # r001: match (contains exact phrase)
    write_json("reports", "r001.json", {
        "report_id": "r001",
        "title": "Edge AI Deployment Trends 2026",
        "sector": "industrial_ai",
        "published_at": "2026-02-15",
        "tags": ["edge", "ai", "quantum"],
        "summary": "Overview of edge inference solutions including QuantumEdge Neural Accelerator.",
        "solution_aliases": ["QNA"],
        "content": "The QuantumEdge Neural Accelerator has shown 4x throughput improvement over traditional GPU-based edge nodes. Early adopters report 30% lower latency."
    })
    # r002: distractor – typo (QuatumEdge Neural Accelerator)
    write_json("reports", "r002.json", {
        "report_id": "r002",
        "title": "Neural Accelerator Benchmark Q4",
        "sector": "robotics",
        "published_at": "2025-11-20",
        "tags": ["neural", "benchmark"],
        "summary": "Benchmark of various neural accelerators.",
        "solution_aliases": [],
        "content": "The QuatumEdge Neural Accelerator (typo) was tested but results are inconclusive. Actually the correct name is QuantumEdge Neural Accelerator, but we kept the typo in the draft."
    })
    # r003: distractor – only "QuantumEdge" without "Neural Accelerator"
    write_json("reports", "r003.json", {
        "report_id": "r003",
        "title": "QuantumEdge Platform Overview",
        "sector": "logistics_ai",
        "published_at": "2026-01-10",
        "tags": ["quantum", "platform"],
        "summary": "Overview of QuantumEdge platform features.",
        "solution_aliases": [],
        "content": "The QuantumEdge platform provides low-latency inference, but the Neural Accelerator module is not included in this report."
    })

    # ========================
    # Presentations
    # ========================
    # p001: match (contains exact phrase)
    write_json("presentations", "p001.json", {
        "presentation_id": "p001",
        "title": "QNA Deployment Playbook",
        "owner": "partner_marketing",
        "updated_at": "2026-03-01",
        "tags": ["quantum", "edge", "deployment"],
        "summary": "Deployment steps for QuantumEdge Neural Accelerator.",
        "solution_aliases": ["QNA"],
        "deck_notes": "Slide 12 highlights the QuantumEdge Neural Accelerator power savings.",
        "content": "The QuantumEdge Neural Accelerator is now certified for production workloads. Key partners include NorthStar and HelioSync."
    })
    # p002: distractor – phrase appears but inside a table header? still exact match, so we mark it as non-match by breaking phrase? Actually we need it to be non-exact match.
    # Let's make it contain "QuantumEdge" and "Neural Accelerator" but not consecutively.
    write_json("presentations", "p002.json", {
        "presentation_id": "p002",
        "title": "Hardware Roadmap 2026",
        "owner": "research_design",
        "updated_at": "2026-02-28",
        "tags": ["hardware", "roadmap"],
        "summary": "Upcoming hardware accelerators.",
        "solution_aliases": [],
        "deck_notes": "Mentions QuantumEdge and Neural Accelerator separately.",
        "content": "We plan to release a new QuantumEdge chip in Q3. The Neural Accelerator line will follow in Q4. The combined product is not expected until 2027."
    })
    # p003: distractor – no mention at all
    write_json("presentations", "p003.json", {
        "presentation_id": "p003",
        "title": "Market Segmentation Analysis",
        "owner": "strategy_team",
        "updated_at": "2026-01-15",
        "tags": ["market", "analysis"],
        "summary": "Segmentation of edge AI customers.",
        "solution_aliases": [],
        "deck_notes": "No mention of QuantumEdge.",
        "content": "The edge AI market is growing at 25% CAGR. Major players include NVIDIA and Intel."
    })

    # ========================
    # Media Samples
    # ========================
    # m001: match (exact phrase)
    write_json("media_samples", "m001.json", {
        "sample_id": "m001",
        "title": "Podcast: Edge Innovation Spotlight",
        "channel": "podcast_transcript",
        "captured_at": "2026-03-12",
        "tags": ["podcast", "edge", "quantum"],
        "summary": "Interview discussing the QuantumEdge Neural Accelerator.",
        "solution_aliases": ["QNA"],
        "content": "Host: Let's talk about the QuantumEdge Neural Accelerator. Guest: It's a breakthrough for low-power edge inference."
    })
    # m002: match (exact phrase, but with version suffix? we keep exact phrase)
    write_json("media_samples", "m002.json", {
        "sample_id": "m002",
        "title": "TechCrunch Article Draft",
        "channel": "editorial_draft",
        "captured_at": "2026-03-10",
        "tags": ["article", "news"],
        "summary": "Draft article on QuantumEdge Neural Accelerator.",
        "solution_aliases": [],
        "content": "The QuantumEdge Neural Accelerator, announced yesterday, promises 10x efficiency. Sources inside NorthStar confirm the pricing."
    })
    # m003: distractor – phrase split by newline? keep it non-match
    write_json("media_samples", "m003.json", {
        "sample_id": "m003",
        "title": "Keynote Transcript: Future of AI",
        "channel": "keynote_transcript",
        "captured_at": "2026-02-20",
        "tags": ["keynote", "ai"],
        "summary": "Keynote speech on AI trends.",
        "solution_aliases": [],
        "content": "We are excited about the new QuantumEdge\nNeural Accelerator product line. Actually it's a different product."
    })

    # --- Optional: add some other files to increase realism (not used in verification) ---
    # data/contacts.json etc. but not required; skip to keep env manageable.

    # Touch a placeholder to confirm build
    with open("ops/.placeholder", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
