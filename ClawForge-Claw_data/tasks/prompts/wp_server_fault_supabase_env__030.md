Subject: Urgent – UPS outage follow-up needed

Hey,

Nikhil here from NOC. Last night’s UPS failure took out a chunk of our edge services. I’ve dumped the incident pool into `data/incidents/incident_pool.json` – but someone mixed up ticket types, and half the “watchlist” entries shouldn’t be there. We only care about actual risk work orders tied to UPS outages.

I also kept the attachments manifest in `data/attachments.json`. The runbook named *UPS and Service Outage Runbook* contains the exact transaction ID we need to kill. Grab that ID, then write it into `ops/kill_targets.json`. I want the file to contain a JSON object with a single field `"targets"` that holds an array of strings – just the one ID.

Only incidents that are both category `ups_outage` and ticket type `risk_work_order`, and whose attachment points to the UPS runbook, should be processed. Ignore everything else.

Let me know if anything’s missing.

– Nikhil
