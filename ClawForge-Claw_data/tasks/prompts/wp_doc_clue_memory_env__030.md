Hey there, I'm from the Market Intelligence team. We're tracking a solution called **OptiFlow Nexus** for an upcoming quarterly review. I've dumped all our latest reports, presentations, and media samples under the `data/` folder, but I don't have time to comb through every single one.

Here's the deal:
- Each document file is a JSON bundle inside its respective directory (`data/reports/reports.json`, `data/presentations/presentations.json`, `data/media_samples/media_samples.json`).
- Each document has a field called `solution_aliases` – that's the list of solutions it touches. I need only documents that explicitly list *"OptiFlow Nexus"* (exact match, case‑sensitive).
- Inside the `content` of those matching documents, our team always marks the key takeaway with a line that starts with **`CLUE:`**. Grab that whole line (the part after "CLUE:") – that's the clue bullet I need.
- For every such document, write down: what type of document it is (say "report", "presentation", or "media_sample"), its ID (e.g., `report_id`, `presentation_id`, `sample_id`), and the clue text you found.

Collect all of them into a single JSON file at `temp_records/clue_list.json`. The format is up to you – just make it easy for me to load programmatically. No duplicates, no extra fluff. I need the real deal.

Thanks – I'll grab that file when you're done.
