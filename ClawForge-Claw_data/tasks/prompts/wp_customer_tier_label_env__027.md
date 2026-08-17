Subject: Urgent: Customer tier labels are a mess – need recalc

Hi Agent,

This is Sarah from Operations. Our customer tier labels haven't been updated in months and the sales team is complaining about wrong discount assignments. I've just pulled the latest data dumps into the workspace under `raw_data/`. The customer master list is in `customers/customers.json`. The consumption logs are in `raw_data/consumption_logs.json` and the activity logs are in `raw_data/activity_logs.json`. There's also some old backup files lying around – please ignore anything that's obviously stale.

Here's the business logic we agreed on with Finance:

- Customers with quarterly spend >= 50,000 AND last active <= 7 days AND risk level = 'low' → **platinum**
- Customers with quarterly spend >= 20,000 AND < 50,000 AND last active <= 30 days → **gold**
- Customers with quarterly spend >= 5,000 AND < 20,000 → **silver**
- All others → **bronze**

For each customer, I need you to update their `labels` list: keep any existing label that does NOT start with `"tier:"`, then add a single new label like `"tier:platinum"` (or whichever tier they belong to). If the customer already has a `"tier:"` label, replace it with the new one.

Please write the results into a JSON file at `ops/customer_tier_updates.json`. The file should contain an array of objects, each with `customer_id` and `new_labels` (the final labels list after applying the rule above). Only include customers that have valid records in BOTH consumption_logs and activity_logs – skip anyone who is missing data or has obviously corrupted entries (e.g., negative spend).

Thanks! I need this done before the next sales call.

— Sarah
