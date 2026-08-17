Hi there! This is Keiko from Market Intelligence. I'm chasing down every piece of material that explicitly mentions "HelioSync Edge Inference Fabric" – our new edge AI solution. I've dumped a bunch of files into the `data/` directory: reports, presentations, and media samples. Each subfolder has a JSON manifest with metadata.

Could you please go through all three manifests, pick out any document whose `solution_aliases` list contains exactly that phrase (case‑sensitive), and save the results? For each matched document, I need its unique ID (either `report_id`, `presentation_id`, or `sample_id`) and the `summary` text.

Name the output file `ops/clue_list.json`. The structure should be a JSON list of objects, each with two fields: `"id"` (the document ID) and `"clue"` (the summary). That's all I need – just the clean, matched set. Thanks!
