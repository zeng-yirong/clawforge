---
name: finance-investment-brief
description: Work inside the `claw_envs/finance_envs` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Use bash for environment actions and read/write/edit for local notes and drafts.
---

# Investment Brief Generation

Use `python -m finance_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft research.

## Workflow

1. Run `task` to get the assignment.
2. Use `list-stocks`, `get-stock`, and `screen-stocks` to analyze the market.
3. Use `list-news` and `get-news` to check relevant news.
4. Use `list-earnings` and `get-earnings` to review earnings data.
5. Use `create-earnings-summary` to synthesize earnings findings.
6. Use `generate-sector-overview` and `provide-recommendations` for analysis.
7. Use `create-brief` to draft the investment brief with all required sections.
8. Use `update-brief` to refine until ready.
9. Use `submit-brief` when complete.
10. Finish with `session-summary`.

## Rules

- Cite specific data points from news, earnings, and market data.
- Focus on the sector and tickers assigned in the task.
- Follow investment research standards for the brief structure.
- Do not inspect implementation files to extract answers directly.
