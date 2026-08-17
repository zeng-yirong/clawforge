---
name: travel-policy
description: Work inside the `claw_envs/travel_policy_envs` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Travel Policy

Use `python -m claw_envs.travel_policy_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `task`.
2. Use `list-platforms` and `compare-platform-prices` to survey available options.
3. Use `list-policies` and `get-policy-restrictions` to understand travel policy.
4. Use `validate-booking-against-policy` to check compliance.
5. Use `initiate-approval-request` for required approvals.
6. Use `create-booking` once approved.
7. Finish with `session-summary`.

## Rules

- Use only approved platforms from the policy preferred vendors list.
- Always validate booking against policy before initiating approval.
- Check platform fee structure before finalizing booking.
- Do not inspect implementation files to extract the answer directly.
