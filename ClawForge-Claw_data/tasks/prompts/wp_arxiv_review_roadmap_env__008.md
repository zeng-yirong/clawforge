Hi,

I'm in a rush — need a structured review + citation roadmap for the "tool_augmented_reasoning" direction from our ArXiv abstract store. All data is in the `data/` folder: there's a paper index (`papers.json`) and some attachments that might help. Please produce a single JSON file at `output/review.json` with three fields:
- "direction": the target direction string.
- "papers": an array of objects, each with "paper_id", "title", and "year", for every paper belonging to that direction.
- "roadmap": a Mermaid graph (graph TD) using paper_id as node labels and "-->" for arrows that reflect the citation relationships you find in the data.

Keep the output clean and machine‑readable. Thanks!
