Hey,

Our datacenter west4 just lit up like a Christmas tree – UPS alarms going off and billing-api is returning 503s. I’ve exported the current incident pool from our fault tracker and dumped the latest on-call runbook into the workspace.

Could you dig through the incidents under `data/incidents/incident_pool.json` and figure out which ones are the real threats? I need you to pull up the runbook in `data/attachments/runbook_ups_and_service.md` – that’s the one Lena finally approved last week – and for each incident that fits the UPS outage or service-down profile, note what immediate action the runbook prescribes.

I want the results cleanly organized in a file at `ops/priority_incidents.json`. Structure it as a list of incidents, each with its ID and the exact action from the runbook. Only include incidents that still need handling – no closed tickets, and nothing that doesn't match the categories we care about right now.

Don’t overthink it: open the pool, cross‑check the runbook, write the priority list. If the runbook says “Power cycle the UPS” for an outage, then that’s what goes in.

Thanks –  
Lena Park  
Facilities Power Coordinator
