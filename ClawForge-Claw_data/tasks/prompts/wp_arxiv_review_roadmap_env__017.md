Hi there,

I'm Lin, a junior researcher in the lab. We're trying to put together a literature survey for the **tool_augmented_reasoning** direction, and I've dumped all our paper records into `data/papers/papers.json`. Unfortunately, that dataset is a mess — my previous lab mate threw in papers from other directions, and the `direction` field itself has typos, inconsistent casing, and even missing values. **The only correct direction string is `tool_augmented_reasoning`** (all lowercase, underscore-separated). Please ignore any papers whose `direction` is absent, uses hyphens, spaces, or anything else.

I need two deliverables from you:

1. **`review.md`** — A clean, well-structured Markdown file that lists all the valid `tool_augmented_reasoning` papers **sorted by year (ascending)**. For each paper, include its year, title, and a short 1-2 sentence summary in English (you can base it on the `abstract` field). Don't forget a title and an introductory sentence at the top.

2. **`roadmap.mmd`** — A Mermaid flowchart that visualises the same papers as a timeline. Each node should show the year and title (e.g., `2023 – Interactive Tool Use`). Connect them in chronological order with arrows (`-->`). Use a horizontal left-to-right layout (`graph LR`).

Please put both files in the root of the workspace. I'll present this to the group tomorrow morning. Thanks a ton!

— Lin
