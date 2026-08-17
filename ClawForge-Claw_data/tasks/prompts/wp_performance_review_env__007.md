Hi team,

I'm the HR ops lead. Our quarterly performance cycle just closed, and I urgently need the consolidated scores for all active employees. I've dumped the raw data into three files under `data/`:

- `data/employees/employees.json` — everyone's basic info (ID, name, department, role code).
- `data/ledgers/monthly_outputs.json` — this month's output metrics for each person (feature delivery, quality, collaboration).
- `data/rules/scoring_rules.json` — the role-specific weighting rules we agreed on last sprint.

Please compute the **total composite score** for each employee using the weights from `scoring_rules.json` and the metrics from `monthly_outputs.json`. The formula is:

total = (feature_delivery × feature_weight) + (quality_score × quality_weight) + (collaboration_score × collaboration_weight)

Round each total to one decimal place. Then write a single JSON file at `ops/performance_profiles.json` that contains **one array of objects** — one object per employee, in the same order as they appear in `employees.json`. Each object must have these fields:

- `employee_id`
- `employee_name`
- `department`
- `role_code`
- `feature_delivery`
- `quality_score`
- `collaboration_score`
- `total_score`

That's it. I'll use this file to auto-update our employee memory store. Please make sure the numbers are precise — I'm already getting flak from the VP for last quarter's miscalc.

Thanks,
Mia
