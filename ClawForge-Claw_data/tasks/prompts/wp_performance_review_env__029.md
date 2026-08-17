Hi there, hope you're having a good day.

I'm Lin, the HR ops lead. Last night's migration script went sideways and wiped the monthly performance scores we'd just computed. I've pieced together the raw ingredients from backups:

- Employee roster: `data/employees/employees.json` – includes everyone active this month.
- Output ledger: `data/ledgers/monthly_outputs.json` – the actual feature delivery, quality, and collaboration numbers for each person.
- Scoring rules: `data/rules/scoring_rules.json` – the per-role weights that the compensation committee approved yesterday.

Could you please recompute the composite performance score for each employee? The score is the weighted sum of the three components using the weights from their role. I need the output as a single JSON file saved under `ops/review/performance_review.json`. For each employee, include their ID, name, department, and the total score. Only include employees who have a matching record in the output ledger – some folks were on leave and won't have one.

I'll take it from there and feed it to the managers. Thanks!

— Lin
