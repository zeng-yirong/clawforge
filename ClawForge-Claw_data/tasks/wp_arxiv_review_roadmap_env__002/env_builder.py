import os
import json
import random

def build_env():
    # Ensure cwd is already the asset root ()
    # Create directory structure
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/notes", exist_ok=True)  # Decoy directory

    # --- Papers ---
    # Target direction: tool_augmented_reasoning
    # We create 5 target papers, plus 5 distractor papers (other directions, duplicates, missing fields)
    papers = []

    # Target papers (tool_augmented_reasoning)
    target_ids = ["TAR-001", "TAR-002", "TAR-003", "TAR-004", "TAR-005"]
    target_titles = [
        "Tool Synthesis for Complex Tasks",
        "Router-Based Multi-Tool Orchestration",
        "Integrated Controller for Tool-Augmented Agents",
        "Learning to Compose Tools via Feedback",
        "Efficient Tool Sequencing with LLMs"
    ]
    target_abstracts = [
        "We propose a framework that synthesizes new tools from existing APIs to handle novel tasks.",
        "This paper introduces a router module that selects optimal tools based on task decomposition.",
        "An integrated controller that unifies tool invocation and reasoning in a single agent.",
        "A reinforcement learning approach to learn tool composition policies from interaction feedback.",
        "We study how to sequence multiple tools efficiently using large language models as planners."
    ]
    target_keywords = [
        ["tool synthesis", "API", "framework"],
        ["router", "orchestration", "task decomposition"],
        ["integrated controller", "agent", "unified"],
        ["reinforcement learning", "tool composition", "feedback"],
        ["tool sequencing", "LLM", "planning"]
    ]
    target_year = 2024
    for i, pid in enumerate(target_ids):
        papers.append({
            "paper_id": pid,
            "title": target_titles[i],
            "direction": "tool_augmented_reasoning",
            "year": target_year,
            "keywords": target_keywords[i],
            "abstract": target_abstracts[i],
            "citation_ids": []
        })

    # Distractors: different direction
    distractor_ids = ["DIST-001", "DIST-002", "DIST-003"]
    distractor_titles = [
        "Vision Transformers for Image Segmentation",
        "Efficient Attention Mechanisms in Vision",
        "Self-Supervised Learning for Medical Imaging"
    ]
    for i, pid in enumerate(distractor_ids):
        papers.append({
            "paper_id": pid,
            "title": distractor_titles[i],
            "direction": "efficient_vision",
            "year": 2023,
            "keywords": ["vision", "transformer"],
            "abstract": "This paper explores vision models for segmentation tasks.",
            "citation_ids": []
        })

    # Duplicate (old version with same paper_id as TAR-001)
    papers.append({
        "paper_id": "TAR-001",
        "title": "Tool Synthesis for Complex Tasks (v1)",
        "direction": "tool_augmented_reasoning",
        "year": 2023,
        "keywords": ["tool synthesis", "v1"],
        "abstract": "Early version of the tool synthesis framework.",
        "citation_ids": []
    })

    # Missing abstract (should be ignored by agent)
    papers.append({
        "paper_id": "MISS-001",
        "title": "Incomplete Paper",
        "direction": "tool_augmented_reasoning",
        "year": 2024,
        "keywords": [],
        "abstract": "",  # empty abstract
        "citation_ids": []
    })

    # Another direction with same paper_id as one target? No, avoid confusion.

    # Write papers.json
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # --- Attachments ---
    attachments = []
    # For each target paper, create an attachment with detailed notes
    attachment_descriptions = [
        "This paper proposes a novel tool synthesis method. Key idea: use APIs as Lego blocks.",
        "Router-based approach; figure 3 shows the decision tree.",
        "Integrated controller unifies reasoning and tool use; see the architecture diagram.",
        "RL-based composition; reward function is critical.",
        "Sequencing experiments show 20% improvement over baseline."
    ]
    for i, pid in enumerate(target_ids):
        attachments.append({
            "path": f"data/attachments/{pid}_notes.txt",
            "title": f"Notes for {pid}",
            "kind": "reading_note",
            "description": attachment_descriptions[i]
        })
        # Create actual file
        with open(f"data/attachments/{pid}_notes.txt", "w") as f:
            f.write(attachment_descriptions[i])

    # Decoy attachments (pointing to non-existent files)
    attachments.append({
        "path": "data/attachments/extra_notes.txt",
        "title": "Extra Notes",
        "kind": "reading_note",
        "description": "This is a decoy attachment.",
    })
    # This file does not exist, so agent needs to handle.

    # Write attachments.json
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # --- Decoy notes directory with unrelated files ---
    with open("data/notes/class_notes.txt", "w") as f:
        f.write("Today we discussed gradient descent optimization.")
    with open("data/notes/lab_results.csv", "w") as f:
        f.write("epoch,loss\n1,0.5\n2,0.3\n")

    # Also create a hidden clue? No, unnecessary.

if __name__ == "__main__":
    build_env()
