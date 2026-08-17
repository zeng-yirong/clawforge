---
name: itinerary-planning
description: Work inside the `claw_envs/itinerary_envs` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Itinerary Planning

Use `python -m claw_envs.itinerary_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `list-cities` to see available cities.
2. Run `load-city` to get details for specific cities.
3. Run `search-routes` to find routes between origin and destination.
4. Run `compare-transport` to compare transport options.
5. Run `plan-transfer` for multi-stop journeys with waypoints.
6. Run `generate-itinerary` to create a detailed itinerary.
7. Run `optimize-route` to optimize based on your criteria.
8. Finish with `session-summary`.

## Rules

- Always search routes before comparing transport options.
- Plan transfers with waypoints for multi-stop journeys.
- Generate itinerary before optimizing route criteria.
- Do not inspect implementation files to extract the answer directly.
