import os
import json

def build_env():
    # Ensure data and cache directories exist
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("cache", exist_ok=True)

    # Write papers.json with valid, invalid, duplicate citations
    papers = [
        {
            "paper_id": "paper_001",
            "title": "Deep Learning for NLP",
            "direction": "CS",
            "year": 2020,
            "keywords": ["deep learning", "NLP"],
            "abstract": "This paper explores ...",
            "citation_ids": ["paper_002", "paper_003", "paper_004"]  # 004 does not exist
        },
        {
            "paper_id": "paper_002",
            "title": "Transformer Architectures",
            "direction": "CS",
            "year": 2021,
            "keywords": ["transformer", "attention"],
            "abstract": "We propose ...",
            "citation_ids": ["paper_001", "paper_001", "paper_003"]  # duplicate 001
        },
        {
            "paper_id": "paper_003",
            "title": "Graph Neural Networks",
            "direction": "CS",
            "year": 2022,
            "keywords": ["GNN", "graphs"],
            "abstract": "GNNs ...",
            "citation_ids": ["paper_002", "paper_005"]  # 005 does not exist
        }
    ]

    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # Create a distracting old cache file
    old_cache = {"edges": [{"source": "paper_001", "target": "ghost"}]}
    with open("cache/citation_graph_old.json", "w") as f:
        json.dump(old_cache, f)

if __name__ == "__main__":
    build_env()
