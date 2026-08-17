Hey team,

Just pulled the latest reproduction attempt logs from our shared drive. You'll find `project_ledgers.csv` at the root with all the tries we've made, and `data/projects/project_docs.json` with metadata for each project.

We need to compile a clean reproduction ledger for the knowledge base archive. Only include attempts that were successfully reproduced (reproducibility marked as 'yes'). For each project, take the most recent successful attempt (by date). But skip any project that is already marked as 'archived' in the project docs.

The final output should be a JSON file at `ops/reproduction_ledger_archive.json`. It should be a list of objects, each containing the project name, the issue ID, the reproduction date, and the notes from that attempt. Sort the list alphabetically by project name.

I'll feed this directly into the archiver. Make sure it's clean and accurate. Thanks!
