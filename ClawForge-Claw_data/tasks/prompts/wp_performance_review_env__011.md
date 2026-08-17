Hey there,

I'm drowning in spreadsheets. Every month I have to manually dig through `data/employees/employees.json`, pull the latest numbers from `data/ledgers/monthly_outputs.json`, and cross‑check the scoring rules in `data/rules/scoring_rules.json` — just to figure out who deserves what. It's taking hours and I keep making typos.

Could you whip up a quick script that automates this for me? Here's what I need:

- Grab every employee listed in the employee roster.
- For each one, look up their latest output scores and their role‑specific scoring rule.
- Calculate a **total performance score** by combining the three output metrics with the rule's weights (simple weighted sum).
- Then assign a **grade** based on the total:
  - **A** if total >= 90
  - **B** if total >= 75 and < 90
  - **C** otherwise.
- Finally, save the results into `reports/performance_scores.json`. I want it sorted from highest total to lowest, and each entry should include `employee_id`, `name`, `department`, `total_score`, and `grade`.

Please make sure you read only the current month's output ledger (the one in that exact file) and the active scoring rules. The output file should be clean and ready for me to share with the team.

Thanks a ton!

— HR
