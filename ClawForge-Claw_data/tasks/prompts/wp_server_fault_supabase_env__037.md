Subject: Urgent – Remediation plan needed for power & service incidents

Team,

Monitoring just escalated a batch of open risk work orders. I've dropped the incident list into `incidents/incident_pool.json`. We need to act *now* on the ones that are either **UPS power failures** (`ups_outage`) or **service down** events (`service_down`) – only those with high or critical priority and still in open status.

The standard runbook covering both categories is in `attachments/runbook_ups_and_service.md`. Each category has a specific action you must follow.

Please generate a remediation plan with one entry per qualifying incident. Each entry should hold the incident ID and the corresponding action from the runbook. Write the result to `ops/remediation_plan.json`. Keep it clean – I'll forward it straight to the on‑call team.

Need this in under 5 minutes. Thanks.

– Lena
