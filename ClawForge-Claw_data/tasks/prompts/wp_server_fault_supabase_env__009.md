Hey Nikhil here – sorry to drop this on you at 2 AM. The west4-spine-uplink started throwing packet loss alarms about an hour ago, and the power team thinks it's a cascading UPS issue from the edge cluster. I've dumped the latest incident snapshot into `data/incidents/incident_pool.json` – you'll find all sorts of noise in there. The runbook we need to follow is sitting in `data/attachments.json` under the "UPS and Service Outage Runbook" entry.

I need you to:

- Pull every incident that looks like a real UPS failure or service outage risk (not the ones that are just watchlist items – only the actual risk work orders).
- For each of those, figure out the right action based on what the runbook tells us to do for that incident category.
- Write a clean remediation plan into `ops/remediation_plan.json` – something I can hand straight to the NOC shift to execute.

Keep it tight, no extra fluff. I just need the incident IDs and the action we agreed on. Let me know if anything's unclear.

Thanks,
Nikhil
