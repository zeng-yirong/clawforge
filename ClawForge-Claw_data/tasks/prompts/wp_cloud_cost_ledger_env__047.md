**From:** Tara Ng <tara.ng@northstar.example.com>  
**To:** [Agent]  
**Subject:** Urgent: June cost report for business clusters needs redo

Hey Agent,

The Q2 FinOps review is tomorrow and I just noticed last month's cost report used the wrong price catalog – someone pulled the March archive instead of the June live one. The board expects accurate numbers for our three business clusters (ads-ranking, lakehouse-analytics, retail-core). Shared platform clusters like shared-ops should not be included.

All the raw data is still in the workspace: cluster definitions are in `data/resources/clusters.json`, usage ledger in `data/resources/resource_ledger.json`, and the pricing catalogs are in `data/pricing/pricing_catalogs.json`. Please pick the **currently active and approved** June 2026 catalog – you’ll see two versions; the archived one is stale.

I need a single JSON file `monthly_cost_report.json` placed in the current directory, structured with the report month and a list of business clusters, each showing its total cost. The calculation should aggregate all compute and storage entries for each cluster (sum quantity × unit price from the correct catalog). Only entries belonging to business clusters should be considered – discard any stray records that don't match.

Get this done ASAP, please. The report will be sent to Daniel and Leah for review after you finish.

Best,
Tara
