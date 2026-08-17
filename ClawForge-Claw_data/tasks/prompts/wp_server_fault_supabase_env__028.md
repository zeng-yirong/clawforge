**Subject**: 🚨 Critical: West4 UPS & Billing API Outage – Immediate action required

Hey team,

NOC here. We've got a double whammy – the UPS in West4 is on the brink, and our billing API just went dark. I've pulled the latest incident pool snapshot into `data/incidents/incident_pool.json`. Also, there's a runbook at `data/attachments/runbook_ups_and_service.md` that outlines the remediation steps.

I need you to go through the pool, pick out the **risk work orders** (we're only interested in those) that are related to UPS outages or service downs and need immediate attention. Cross-reference with the runbook, and for each one, note the specific action that should be taken.

Then drop the final action plan into `ops/final_action_list.json`. Make it clean and self-explanatory so I can hand it off to the on-call guys.

Thanks,
Nikhil
