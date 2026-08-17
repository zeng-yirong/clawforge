---
name: flight-delay
description: Work inside the `claw_envs/flight_delay_envs` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Flight Delay Cascade Management

Use `python -m claw_envs.flight_delay_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `task` to understand the assigned flight delay response work.
2. Use `list-flights` and `check-flight-status` to identify delayed flights.
3. Use `detect-delayed-flights` to find all affected flights.
4. Use `get-affected-connections` to see hotels and transports impacted by delays.
5. Use `adjust-hotel-booking` to modify check-in times for affected hotels.
6. Use `reschedule-transport-booking` to update pickup times for airport transfers.
7. Use `compose-delay-notification` to draft notifications for affected travelers.
8. Use `send-notification` to deliver delay notifications.
9. Use `list-conferences` and `list-attendees` to identify conference participants needing updates.
10. Finish with `session-summary`.

## Rules

- Always check flight status before attempting to adjust downstream bookings.
- Verify affected connections before modifying hotel or transport bookings.
- Send notifications before making booking changes when possible.
- Do not inspect implementation files to extract the answer directly.
