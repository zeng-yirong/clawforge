Hi, I'm Harper Zhou from DRE.

We had a rough night – West4 UPS alarm fired at 3 AM and the billing-api went down shortly after. I dumped the latest incident snapshot into `data/incidents/incident_pool.json` and the standard runbook is sitting at `data/runbook_ups_and_service.md`. The runbook spells out exactly which incidents we should act on and how.

Could you please:
- Go through the incident pool, follow the runbook criteria, and pick out only the incidents that need immediate remediation.
- Perform the remediation steps described in the runbook.
- Write a resolution record as if we were pushing it into the Supabase resolution table.

Drop the outputs into the `ops/` folder. I need three files there:
  - `ops/screened.json` – the list of incident IDs that passed the screening.
  - `ops/remediation.json` – the remediation log (one entry per incident).
  - `ops/resolution.json` – the resolution records ready for Supabase.

Thanks – I'll review them before the morning standup.
