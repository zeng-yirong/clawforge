Subject: Urgent: Q2 cost discrepancy – need accurate compute for ads-ranking

Hi there,

Hope you had a good weekend. Our monthly cost report for June just landed, but something’s off – the Finance team flagged a huge jump in the Ads ranking cluster line. I dug into the source files and I think the pricing catalog used in the last run was the archived March version.

Could you please recalculate the total cost for the **ads-ranking** cluster using the **active** pricing catalog (the one approved for June 2026)? All the data you need is in the `data/` directory:

- `data/resources/resource_ledger.json` – raw usage entries
- `data/resources/clusters.json` – cluster definitions (you’ll find the cluster ID for ads-ranking there)
- `data/pricing/pricing_catalogs.json` – both archived and active catalogs
- `attachments/cost_accounting_rules.md` has the general policy (but the active catalog’s rates are the source of truth)

Once you have the correct total, write it into a JSON file at `ops/final_cost.json` with the following structure:

{
  "cluster_name": "ads-ranking",
  "billing_month": "2026-06",
  "currency": "USD",
  "total_cost": <number>
}
I need this ASAP so we can fix the report before the board review. Thanks!

– Daniel Song  
Cloud FinOps Lead
