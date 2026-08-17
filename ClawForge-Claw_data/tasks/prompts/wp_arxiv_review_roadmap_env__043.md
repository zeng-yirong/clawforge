Hey there! I'm a postdoc in our lab, and we're putting together a comprehensive survey on efficient vision. I've dumped the paper database into `data/papers/papers.json` — it has all the papers we've collected across different directions. Could you please sift through it, pick out every paper that belongs to the 'efficient_vision' direction (not the tool-augmented one), and compile them into a nice Markdown review? Also, I need a Mermaid timeline roadmap to visualize the progress over the years.

For consistency, please follow the format we used last time:
- In `review.md`, list each paper as a bullet point: `- PAPER_ID: Title`
- In `roadmap.mmd`, use a Mermaid timeline block like:

timeline
    title Efficient Vision Roadmap
    YEAR : PAPER_ID : Title
(Include all papers, sorted by year ascending.)
Place both files in the `outputs/` directory. Watch out — the database might have some messy entries (typos, wrong directions); only include the ones that are explicitly marked as 'efficient_vision'. Thanks!
