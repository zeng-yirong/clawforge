Hey, support team – quick one. HR just dumped the March performance data and it's a bit of a mess. I need you to pull together the final monthly scores for every active employee.

Everything you need is in `data/`:
- Employee master list → `data/employees/employees.json`
- March output ledger → `data/ledgers/monthly_outputs.json` (beware – there are some old test months and a few corrupted entries in there)
- Scoring weights & grade rules → `data/rules/scoring_rules.json` (each role has its own weights and grade cutoffs)

Please calculate the total performance score for each employee using the role-specific weights, then assign the grade (A / B / C) based on that role's grade thresholds. Only consider **March** records (the newest batch), and only for employees that exist in the master list. Remove any obviously invalid records (negative values, duplicates, etc.).

Write the result as an array of objects into `ops/performance_review.json`. Each object must contain:
- `employee_id` (string)
- `total_score` (number, one decimal place)
- `grade` (string, one of A/B/C)

I don't want any extra fields, no missing employees, and the file path must be exactly `ops/performance_review.json`. Let me know once it's done. Cheers.
