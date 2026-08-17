Hey, hope you’re on shift. The NOC just flagged a bunch of Q2 incidents that need triage before the end of the week. I’ve dumped the full incident pool into `data/incidents/incident_pool.json` – it’s got everything from replica lag to power failures.

The Operations Runbook (you’ll find it at `data/attachments/runbook_ups_and_service.md`) explicitly says **only** incidents opened after a certain date should be escalated for remediation. I need you to pull out every **UPS outage** and **service-down** incident that qualifies as a **risk work order** (not watchlist) and is still **open**. Then apply the runbook’s date filter – don’t even look at anything earlier than that cutoff.

Once you’ve got the list, rank them by severity: critical first, then high, then medium. If two share the same severity, the **newer** one (most recent `opened_at`) goes first. Save the ordered list of incident IDs (nothing else) into `ops/remediation_targets.json`. I just need the IDs; my remediation script will handle the rest.

Oh, and double-check that the IDs match exactly what’s in the pool – no typos, no extra fields. The file should be a plain JSON array of strings.

Let me know if the path `data/attachments/` looks messed up – I haven’t checked permissions there.
