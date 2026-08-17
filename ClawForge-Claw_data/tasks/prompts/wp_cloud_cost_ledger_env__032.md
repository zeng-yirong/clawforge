Subject: Urgent: Ads‑ranking cost report needed for June audit

Hey,

We’re in the middle of the quarterly audit and the FinOps team flagged that the June cost figures for **ads‑ranking** don’t match what we submitted last month. I need you to rebuild the report from scratch so we can cross‑check.

I’ve staged the raw resource snapshot under `db_dumps/resource_ledger.json` – it has all clusters for the last few months, so just pull what belongs to ads‑ranking. The pricing catalog lives in `pricing/pricing_catalogs.json`; use the **active** one (ignore archived versions – someone already burned us with that mistake).

Drop the result into `ops/cost_report.json`. Keep it lean: cluster name, billing month, total cost in USD, and a breakdown per resource (resource name + cost). I don’t need essays – just the numbers I can feed to the auditor.

Thanks,
Daniel
