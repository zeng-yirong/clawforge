Hi there,

We just got a fresh dump of ArXiv abstracts for computer vision and AI agents. I pulled them into `data/papers/papers.json`, but it's a bit messy — some papers are not relevant, and I noticed a few entries have formatting issues. Also check `data/attachments/notes.txt` and `data/cache/summaries.json` if you need extra hints.

I need you to focus on the research direction "efficient_vision". Please go through the papers, filter out the ones that truly belong to this direction (ignore anything with wrong or missing direction, and skip any entry where the year is not a proper integer). Then create a structured summary in `review.json` with the following:
- The target direction.
- A list of the valid papers, each with its paper_id, title, year, and keywords. Sort the list by year ascending, and for same year by paper_id ascending.
- The total number of valid papers.
- The sum of all their years (as an integer).

Also, I'd like a visual timeline. Generate a Mermaid timeline diagram in `roadmap.mmd` that shows these papers along the years. Use each paper's ID as the node label (e.g., `p001["Paper Title"]`) so I can quickly cross-reference.

Thanks,
Alex
