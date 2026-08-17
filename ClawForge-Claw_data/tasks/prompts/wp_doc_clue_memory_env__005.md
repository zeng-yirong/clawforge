Hey team, quick one — we're trying to lock down the full signal trace for **HelioSync Edge Inference Fabric** across all our archived content. I've dumped the raw indexes into `data/`:

- `data/reports/reports.json` — sector reports
- `data/presentations/presentations.json` — deck records
- `data/media_samples/media_samples.json` — editorial / podcast / keynote transcripts

Each of those lists entries tagged with `solution_aliases`. I need you to fish out **every entry that explicitly references "HelioSync Edge Inference Fabric"** (check the aliases array). Some entries have empty or missing aliases — skip those. There's also a duplicate entry in the media samples (same `sample_id` appears twice); keep only the **last occurrence** (most recent version).

We also have a helper doc at `data/attachments/solution_matching_notes.md` that maps each qualifying document to a unique clue ID. Follow that mapping. Ignore the other attachment — it's just schema reference.

Once you've collected all the valid documents and their clue IDs from the mapping, compile them into a single JSON file at `ops/clue_summary.json`. Each object in the array must have exactly three fields: `document_id` (the report/presentation/sample ID), `document_type` (one of `"report"`, `"presentation"`, `"media_sample"`), and `clue_id` (the string from the mapping doc). Make sure there's **no extra or missing records** — I'll compare it against the ground truth tomorrow. Keep the array sorted by `document_type` then `document_id` for readability.

Oh and one more thing — the mapping doc says the clue IDs for presentations are prefixed `HSEIF-PRES-`, for reports `HSEIF-REP-`, and for media samples `HSEIF-MED-`. So don't invent your own.

Let me know when it's done!
