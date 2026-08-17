From: Leah Kumar (Cloud Operations Manager) <leah.kumar@northstar.example.com>
To: Cloud Cost Analyst
Subject: Urgent: Ads Ranking cluster cost anomaly – need June 2026 breakdown

Hi,

We’re seeing a weird spike in our Ads Ranking (ads-ranking) cluster cost for June 2026. Can you please pull together a detailed cost report from the raw ledger and the latest pricing catalog?

The raw resource ledger is in `resource_ledger.json` – includes all clusters. The pricing catalogs are under `pricing_catalogs.json`. Please be careful: we only want to use the **active** catalog for June (ignore any archived ones). Also I noticed there might be some test entries that have zero quantity or incorrect units (like “GB” instead of “GiB”) – those should be excluded from the calculation.

We need a machine-readable JSON report saved as `cost_reports/ads_ranking_cost_report.json` with the total cost and a breakdown by resource type. Only Report the costs for the ads‑ranking cluster, nothing else.

Thanks,
Leah
