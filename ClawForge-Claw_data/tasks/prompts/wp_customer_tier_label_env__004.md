Hey there,

I just finished crunching the Q3 numbers and pulled the latest activity data. The files are all ready in this workspace:

- `customers/customers.json` – our current customer roster with existing tiers and labels.
- `logs/activity_logs.json` – the last active day and usage trend per customer.
- `logs/consumption_logs.json` – the quarterly spend per customer.

We need to refresh the customer tier labels based on the following business rules (which I worked out with the VP of Sales):

- **Platinum**: quarterly spend ≥ $50,000 AND last active within 30 days.
- **Gold**: quarterly spend ≥ $20,000 AND last active within 60 days.
- **Silver**: quarterly spend ≥ $10,000 AND last active within 90 days.
- **Bronze**: everyone else.

Please create a new file at `ops/segment_result.json` that contains the updated tier for each customer. The structure should be a list of objects, each with two fields: `customer_id` and `new_tier`.

I need this before the board meeting tomorrow – make sure only the customers from the main roster are included, and base your calculation strictly on the data in the files I mentioned. Don't overthink it, just apply the rules.

Thanks!
