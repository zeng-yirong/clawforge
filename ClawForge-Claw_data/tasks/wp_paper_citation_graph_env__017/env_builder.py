import os
import json

def build_env() -> None:
    # Core directories
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("cache", exist_ok=True)
    # Distractor directories
    os.makedirs("old_versions", exist_ok=True)
    os.makedirs("notes", exist_ok=True)

    # Main papers.json (ground truth source)
    papers = [
        {"paper_id": "p001", "title": "A novel approach", "direction": "CS", "year": 2024, "keywords": ["AI"], "abstract": "This work builds upon [p002] and [p003]. See also [p004] for a different approach.", "citation_ids": []},
        {"paper_id": "p002", "title": "Classical method", "direction": "Math", "year": 2023, "keywords": ["algebra"], "abstract": "The method from [P001] is outdated.", "citation_ids": []},
        {"paper_id": "p003", "title": "Framework extension", "direction": "CS", "year": 2024, "keywords": ["ML"], "abstract": "We extend the framework of [p005].", "citation_ids": []},
        {"paper_id": "p004", "title": "Different approach", "direction": "Physics", "year": 2022, "keywords": ["quantum"], "abstract": "No references.", "citation_ids": []},
        {"paper_id": "p005", "title": "Combination method", "direction": "CS", "year": 2023, "keywords": ["AI", "ML"], "abstract": "Combining [p001] and [p003] yields ...", "citation_ids": []},
        {"paper_id": "p006", "title": "Related work", "direction": "Bio", "year": 2024, "keywords": ["genomics"], "abstract": "Related work includes [p002] and [p007].", "citation_ids": []},
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # Distractor: old version with different content
    old_papers = [
        {"paper_id": "p001", "title": "Old version", "direction": "CS", "year": 2020, "keywords": ["old"], "abstract": "Old abstract.", "citation_ids": ["p002"]},
    ]
    with open("old_versions/papers.json", "w") as f:
        json.dump({"papers": old_papers}, f, indent=2)

    # Distractor: a stale graph already in cache
    stale_graph = {"edges": [{"source": "p001", "target": "p002"}]}
    with open("cache/citation_graph.json", "w") as f:
        json.dump(stale_graph, f, indent=2)

    # Distractor files
    with open("notes/readme.txt", "w") as f:
        f.write("This is a note about citation extraction pipeline.\n")
    with open("data/some_metadata.csv", "w") as f:
        f.write("id,value\np001,1.0\n")

if __name__ == "__main__":
    build_env()
