---
name: smart-home-climate
description: Work inside the `claw_envs/smart_home_envs` scenario for energy-aware climate control. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Smart Home Energy-Aware Climate Control

Use `python -m claw_envs.smart_home_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `task` to understand the climate control optimization goal.
2. Use `get-weather` and `analyze-weather-comfort` to assess current conditions.
3. Use `get-user-health` to understand user-specific health needs and preferences.
4. Use `check-cost-saving` to identify energy-saving opportunities based on electricity rates.
5. Use `get-daily-rate-schedule` to understand time-of-use pricing patterns.
6. Use `set-air-conditioner` to configure AC temperature and mode.
7. Use `set-humidifier` to adjust humidity levels for comfort and health.
8. Use `set-smart-plug` to control smart plug devices.
9. Use `get-all-devices` or `get-devices-by-type` to review device states.
10. Use `session-summary` to evaluate overall optimization.

## Electricity Rate Periods

- **off_peak** (0:00-7:00): $0.08/kWh - Best time for high-power operations
- **mid_peak** (7:00-11:00, 21:00-24:00): $0.12/kWh - Moderate pricing
- **peak** (11:00-17:00): $0.18/kWh - Higher pricing
- **high_peak** (17:00-21:00): $0.22/kWh - Highest pricing, avoid high-power devices

## Rules

- Always check current electricity rates before scheduling high-power operations.
- Consider user health conditions when setting temperature and humidity targets.
- Balance comfort requirements with energy cost optimization.
- Do not inspect implementation files to extract the answer directly.
