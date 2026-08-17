import os
import json
import shutil

def build_env():
    # Clean slate
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("cache"):
        shutil.rmtree("cache")
    if os.path.exists("docs"):
        shutil.rmtree("docs")

    # Create main papers directory
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("cache", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    # Define canonical papers.json (the ground truth)
    papers = [
        {
            "paper_id": "ai001",
            "title": "Deep Learning for NLP",
            "direction": "AI",
            "year": 2021,
            "keywords": ["deep learning", "NLP", "transformer"],
            "abstract": "We propose a transformer-based model for NLP tasks.",
            "citation_ids": ["ai003", "ai005"]
        },
        {
            "paper_id": "ai002",
            "title": "Reinforcement Learning in Robotics",
            "direction": "AI",
            "year": 2022,
            "keywords": ["reinforcement learning", "robotics"],
            "abstract": "A survey of RL applications in robotics.",
            "citation_ids": ["ai001"]
        },
        {
            "paper_id": "ai003",
            "title": "Attention Is All You Need",
            "direction": "AI",
            "year": 2017,
            "keywords": ["attention", "transformer"],
            "abstract": "The original transformer paper.",
            "citation_ids": []
        },
        {
            "paper_id": "ai004",
            "title": "Generative Adversarial Networks",
            "direction": "AI",
            "year": 2014,
            "keywords": ["GAN", "generative"],
            "abstract": "Proposal of GAN framework.",
            "citation_ids": ["ai001", "ai003"]
        },
        {
            "paper_id": "ai005",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "direction": "AI",
            "year": 2019,
            "keywords": ["BERT", "pre-training"],
            "abstract": "BERT model for language understanding.",
            "citation_ids": ["ai003"]
        },
        {
            "paper_id": "ai006",
            "title": "Vision Transformer",
            "direction": "AI",
            "year": 2020,
            "keywords": ["ViT", "image recognition"],
            "abstract": "Applying transformer to image patches.",
            "citation_ids": ["ai003", "ai005"]
        },
        {
            "paper_id": "bio001",
            "title": "CRISPR-Cas9 Gene Editing",
            "direction": "Biology",
            "year": 2020,
            "keywords": ["CRISPR", "gene"],
            "abstract": "Gene editing using CRISPR-Cas9.",
            "citation_ids": ["bio002"]
        },
        {
            "paper_id": "bio002",
            "title": "DNA Sequencing Advances",
            "direction": "Biology",
            "year": 2021,
            "keywords": ["sequencing", "DNA"],
            "abstract": "New methods for DNA sequencing.",
            "citation_ids": []
        },
        {
            "paper_id": "bio003",
            "title": "Protein Folding with AlphaFold",
            "direction": "Biology",
            "year": 2021,
            "keywords": ["protein", "AlphaFold"],
            "abstract": "Deep learning for protein structure prediction.",
            "citation_ids": ["bio001"]
        },
        {
            "paper_id": "bio004",
            "title": "Single-Cell RNA Sequencing",
            "direction": "Biology",
            "year": 2022,
            "keywords": ["single-cell", "RNA"],
            "abstract": "Analysis of single-cell transcriptomics.",
            "citation_ids": ["bio002"]
        }
    ]

    # Write standard papers.json
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # Interference: old backup with different IDs and directions
    old_papers = [
        {"paper_id": "old001", "title": "Old ML Survey", "direction": "AI", "year": 2015,
         "keywords": ["survey"], "abstract": "Outdated", "citation_ids": []},
        {"paper_id": "old002", "title": "Legacy Biology", "direction": "Biology", "year": 2012,
         "keywords": ["legacy"], "abstract": "Old stuff", "citation_ids": ["old001"]}
    ]
    with open("data/papers/papers_old_backup.json", "w") as f:
        json.dump({"papers": old_papers}, f, indent=2)

    # Interference: extra file with duplicate paper_id (ai001) but different direction
    extra_papers = [
        {"paper_id": "ai001", "title": "Dummy duplicate", "direction": "Biology", "year": 2023,
         "keywords": ["fake"], "abstract": "Should be ignored", "citation_ids": []}
    ]
    with open("data/papers/extra_papers.json", "w") as f:
        json.dump({"papers": extra_papers}, f, indent=2)

    # Interference: a CSV file that looks like a paper list but is not JSON
    with open("data/papers/paper_list.csv", "w") as f:
        f.write("paper_id,title,direction,year\n")
        f.write("csv001,Fake CSV Paper,AI,2020\n")

    # Interference: a docs folder with unrelated text
    with open("docs/readme.txt", "w") as f:
        f.write("These are just documentation files.\n")

    # Ensure cache directory is empty
    with open("cache/.gitkeep", "w") as f:
        f.write("")

    # Success indicator
    print("Environment built with canonical papers.json and 4 interference items.")

if __name__ == "__main__":
    build_env()
