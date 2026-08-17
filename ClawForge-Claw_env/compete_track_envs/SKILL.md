---
name: compete-track
description: Work inside the `claw_envs/compete_track_envs` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# CompeteTrack

Use `python -m claw_envs.compete_track_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `task`.
2. Use `list-competitors` and `get-competitor` to inspect competitor data.
3. Use `list-policies` and `get-policy` to review regulatory landscape.
4. Use `list-users` and `screen-users` to analyze user acquisition.
5. Use `create-alert` for monitoring alerts.
6. Use `create-market-report` and `generate-competitive-landscape` for reporting.
7. Finish with `session-summary`.

## Rules

- Use only data from the environment CLI commands.
- Check regulatory impact before competitive analysis.
- Analyze user acquisition sources before cohort comparisons.
- Do not inspect implementation files to extract the answer directly.
