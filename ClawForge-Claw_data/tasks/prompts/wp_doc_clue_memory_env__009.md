Hi there,

I'm deep in a market signal trace for our upcoming product launch. The raw materials are dumped under `data/`:

- `data/reports/`
- `data/presentations/`
- `data/media_samples/`

Each directory contains a JSON file with a collection of records. I've been buried in them and need you to pull out only the **published** (正式发布) records that explicitly mention **"HelioSync Edge Inference Fabric"** in their `solution_aliases` field. There are plenty of unrelated docs and draft versions in there – please ignore those.

For each matching document, grab its **ID** (the unique identifier field) and **one representative clue** (a short, meaningful sentence from the document's `summary` or `content`). Organise everything by document type and dump it into a single JSON file at `ops/signals.json` in this format:

{
  "reports": [
    {"id": "...", "clue": "..."}
  ],
  "presentations": [
    {"id": "...", "clue": "..."}
  ],
  "media_samples": [
    {"id": "...", "clue": "..."}
  ]
}
Only include documents that are **published** (status is exactly "published"). No drafts, no test entries, no unrelated solutions. I need the final file ready before the afternoon standup. Cheers!
