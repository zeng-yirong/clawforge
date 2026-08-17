**Subject: Urgent: ads-ranking cost spike in June – need precise figure for audit**

Hi Team,

I’m seeing a weird blip in the cost attribution for the ads-ranking cluster last month (June 2026). The FinOps dashboard shows a spike, but I want to confirm the exact total cost from the raw ledger before I take it to the VP.

I’ve dumped the latest resource ledger snapshot into `data/resource_ledger.json` – it has all clusters mixed in, so you’ll need to filter for ads-ranking. The cluster metadata is in `data/clusters.json`. Our approved pricing catalog for June is in `data/pricing/pricing_catalogs.json` – make sure you pick the one that’s both active and approved for reporting.

There’s also some old pricing data floating around in that folder from March; ignore anything not marked for June.

Please crunch the numbers:
- Total cost for ads-ranking across both compute and storage.
- Break out compute and storage costs separately in the output.

Drop the result into `ops/cost_report.json` with a clean structure so I can copy-paste it into the audit template. I only need the final numbers – no commentary, no steps.

Thanks,
Daniel Song
Cloud FinOps Lead
