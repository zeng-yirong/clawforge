Hey there,

We're revamping our customer tier labels and I need you to handle the data crunching. 

I've put the new segmentation rules in `ops/tier_rules.json` – please read those carefully. Our customer profiles live in `data/customers/customers.json`, and the raw logs (consumption and activity) are in `data/logs/`. There might be some noise in the logs – negative spend values, missing data – but I trust you to figure out what's relevant.

For each customer in the profiles, calculate the correct tier label according to the rules, then write the result to `ops/updated_labels.json`. The file should be a JSON array of objects, each with `customer_id` and a `labels` array containing the new tier string (e.g., `["gold"]`). Keep it clean – no extra fields, no missing customers.

Let me know if anything looks off. Thanks!
