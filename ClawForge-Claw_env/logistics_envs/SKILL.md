---
name: logistics
description: Work inside the `claw_envs/logistics_envs` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Logistics Environment

Use `python -m claw_envs.logistics_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft documents.

## Workflow

1. Run `task` to understand the assigned operations work.
2. Read attachments (`read-attachment`) for policy documents before taking actions.
3. Process returns:
   - `list-returns --status pending_review` to find returns needing review
   - `get-return --return-id` to inspect return details
   - `approve-return` or `reject-return` based on policy
   - `inspect-return` for returns requiring inspection
4. Update shipment status:
   - `list-shipments --status processing` to find shipments to update
   - `update-shipment-status` when status changes occur
5. Manage inventory:
   - `list-inventory --low-stock-only` to find items needing attention
   - `adjust-inventory` to record discrepancies with proper reason codes
   - `reserve-inventory` when allocating stock
6. Generate reconciliation report:
   - `generate-reconciliation-report` to document inventory state
7. Finish with `session-summary`.

## Policy Reminders

- Returns must be inspected within 5 days of receipt
- Refunds over $100 require manager approval
- All inventory adjustments must have a valid reason code (DAMAGE, THEFT, EXPIRED, INTERNAL_USE, SYSTEM_CORRECTION, RECOUNT, RETURN_DAMAGED)
- Follow proper status transition flow for returns (requested -> pending_review -> approved/rejected -> pending_inspection -> inspected -> resolved)

## Rules

- Use only approved policies and procedures from attachments
- Document all actions with appropriate notes and reason codes
- Do not inspect implementation files to extract the answer directly
