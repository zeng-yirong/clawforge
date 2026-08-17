Hey there,

I'm deep into a Market Intelligence scan for a key technology: **HelioSync Edge Inference Fabric**. I've dropped all the raw material into the `data/` folder — it's a mix of industry reports, presentation decks, and media transcripts. The thing is, some docs are stale or only mention similar buzzwords (like "HelioSync Edge" or "Edge Inference Fabric" alone), and I don't want those diluting our analysis.

Could you go through everything under `data/` and pull out only those documents that explicitly reference the full phrase **"HelioSync Edge Inference Fabric"** (case-sensitivity shouldn't matter, but the exact string must be present in the document's alias list)? For each matching document, I need two pieces: its **document identifier** (like a report_id, presentation_id, or sample_id) and the **key clue** found in its summary field.

Please compile the results into a single JSON file at `ops/clue_list.json` using this structure:

{
  "clues": [
    {"doc_id": "...", "clue_bullet": "..."},
    ...
  ]
}
No other fields, no extra nesting. I need it clean and accurate — don't let the decoys fool you.

Thanks!
