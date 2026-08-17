Hey, this is Harper from NOC. We had a UPS hiccup last night and some open work orders still need immediate action.

I've dropped our current incident pool snapshot at `incidents/incident_pool.json` and the relevant runbook at `data/runbook_ups_and_service.json`. The runbook defines what actions to take per severity for UPS‑related outages.

Could you please:

1. Go through the incident pool and pull out every **UPS outage** ticket (category is `ups_outage`) that is still **open** and has a severity of **critical** or **high**.
2. Look up the correct action for each ticket from the runbook (it's a clear mapping by category → severity).
3. Write a clean list of resolution records to `ops/ups_resolutions.json`. Each record must contain the `incident_id` and the `action` you extracted from the runbook. Keep the list sorted by `incident_id` ascending.

No need to touch other categories or already‑triaged tickets. I just need the actionable ones – double check only the ones that truly match. Thanks!
