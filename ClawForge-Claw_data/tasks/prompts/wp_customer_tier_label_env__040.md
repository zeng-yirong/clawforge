Hi team,

It's time for our quarterly customer tier label update. I've dropped the latest data and rules in the workspace:

- Customer profiles: `data/customers/customers.json`
- Activity logs: `data/logs/activity_logs.json`
- Consumption logs: `data/logs/consumption_logs.json`
- Tier rules: `ops/tier_rules.json`

Please apply the rules to every customer in the profiles and write the new labels into `ops/updated_labels.json`. The rules cover edge cases — make sure each customer gets the right set of labels. Thanks!
