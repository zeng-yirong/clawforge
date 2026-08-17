Hey team,

Our customer tier labels are a mess right now – some high‑value accounts are still marked as “inactive” while some churning ones still wear the “vip” badge. I’ve dumped the latest activity and consumption snapshots into **data/logs/**. You’ll find the customer profiles under **data/customers/customers.json**.

Here’s the business rule we need to apply:

- If a customer spent **$10,000 or more** in the past quarter **AND** was active within the last **30 days**, append the label `"high_value"` to their existing labels.
- If a customer spent **less than $2,000** in the past quarter **AND** has been inactive for **more than 120 days**, append the label `"low_value"`.
- Everyone else keeps their current labels untouched.

Please update every customer’s labels accordingly and write the result as a JSON object (mapping `customer_id` → updated labels array) into **results/updated_labels.json**.

Thanks,
Mike (Ops)
