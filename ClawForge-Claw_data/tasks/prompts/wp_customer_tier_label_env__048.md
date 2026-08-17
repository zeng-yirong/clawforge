Hey, quick favor — I need you to re-tag our customer tiers for the upcoming campaign.  

The data team just dumped the latest quarter’s consumption logs into `data/logs/consumption_logs.json` and the activity snapshots into `data/logs/activity_logs.json`. Our new segmentation rules are sitting in `rules/segmentation_rules.json` — I spent last week tweaking them, so use that file.  

I want you to figure out the correct tier label for each customer based on **both** their spending and recent activity, then write the results into `ops/customer_tiers.json`. The format should be a simple JSON object mapping `customer_id` → `tier_name` (e.g. `{"C001": "Gold"}`).  

Be careful — there are a few old backup files lying around that might confuse things, but the ones I mentioned above are the real deal. Also, some logs might have duplicate entries; only the **latest** record per customer should matter (they're already timestamped correctly, just ignore duplicates if any).  

Once you’re done, drop the file and ping me. I’ll double-check it before the marketing team runs with it.  

Thanks!
