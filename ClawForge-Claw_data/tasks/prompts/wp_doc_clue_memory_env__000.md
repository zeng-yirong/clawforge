Hi team,

I'm Rhea from Signal Research. We're wrapping up Q2 tech solution tracking and need to consolidate every explicit reference to **"HelioSync Edge Inference Fabric"** across our internal document library.

I've just synced the latest data snapshots to this workspace – you'll find them under `data/reports`, `data/presentations`, and `data/media_samples`. Each directory holds a JSON file containing records with fields like `report_id`, `presentation_id`, `sample_id`, and `summary`. There's also a `solution_aliases` list per record – that's where the exact solution name should appear.

Please comb through all three collections, identify every document that **exactly** matches the solution name (case‑sensitive, full string), and extract each document's unique identifier (the ID field) along with its key summary line. Save the result as a JSON array in `ops/clue_list.json`. Each entry should be an object with the identifier and summary.

Keep it neat – no extra fields, no unrelated entries. I need this ready for the final review pack.

Thanks,
Rhea
