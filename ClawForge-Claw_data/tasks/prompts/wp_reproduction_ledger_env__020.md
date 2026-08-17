Hey there! I just wrapped up a batch of reproduction tests for the **Proj-Repro-001** initiative. The complete document index is sitting in `data/projects/project_docs.json` — it lists every documentation sample we've worked with, along with their actual files under `data/docs/`.  

I need you to consolidate all the reproduction outcomes for this specific project into a single summary file. Please put it at the root of the workspace and name it `reproduction_ledger.json`. The file should capture, for each doc that belongs to Proj-Repro-001, its reproduction status (you'll find a `"status"` field inside each doc file), plus a quick tally of how many succeeded and how many failed.  

Oh, and ignore any docs that belong to other projects — there are a few stragglers in the index that I don't care about. Also, some doc files might have missing fields or extra clutter; just skip any that don't have a clear `"status"` value.  

That's it — once you've got the ledger ready, I'll use it for the final archive. Thanks!  
