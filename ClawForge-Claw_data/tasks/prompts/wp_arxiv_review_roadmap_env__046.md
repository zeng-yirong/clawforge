Hey there, fast learner!

I'm Karen from the AI Strategy team. We've got a group presentation next Thursday on **Tool-Augmented Reasoning** — you know, those LLMs that call external tools to reason better. I've dumped the raw data from our internal ArXiv snapshot into the workspace. The key stuff is under `data/papers/papers.json`, but I've also left some auxiliary files in `data/` that you might find distracting — just ignore the noise.

Look, we need two things for the review:

1. **A Markdown review** that covers all the papers we have on this direction. I want a proper title, a short abstract-style intro, then for each relevant paper: its paper_id, title, year, keywords, and a one-sentence takeaway from its abstract. Don't miss any — we have exactly five papers on tool-augmented reasoning in that JSON.
2. **A Mermaid roadmap** that plots those five papers in chronological order (by year) as nodes, connected by arrows showing the progression. Use `graph TD` layout, and label each node with the paper_id and year, e.g. `TAR-2020[2020]`. The graph should start from the earliest paper and end with the latest.

Save the Markdown file as `review/tool_augmented_reasoning_review.md`, and the Mermaid file as `review/roadmap.mmd`. Please make sure both files are clean and well‑formatted — I'll be copy‑pasting them straight into our slide deck.

Oh, and one more thing: there's a file called `data/attachments.json` that has some extra notes, but they're not needed. Focus on `papers.json`. You'll know which papers belong to the right direction — the `direction` field says exactly "tool_augmented_reasoning".

Thanks! Let me know if you have questions.
