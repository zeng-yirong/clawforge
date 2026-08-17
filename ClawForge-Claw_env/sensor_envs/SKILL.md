---
name: sensor-monitoring
description: Work inside the `claw_envs/sensor_envs` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Sensor Monitoring

Use `python -m sensor_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and drafts.

## Workflow

1. Run `sensors list` to see all available sensors.
2. Use `sensors read <sensor_id>` to get current readings.
3. Use `monitoring check` to detect anomalies.
4. Use `alerts list` and `alerts create` to manage alerts.
5. Use `reports hourly`, `reports daily`, or `reports monthly` to generate reports.
6. Use `trends analyze <sensor_id>` for trend analysis.
7. Use `notifications create` to send notifications.
8. Finish with `evaluate` to score the session.

## Rules

- Check sensor thresholds before creating alerts.
- Generate reports for the appropriate time periods.
- Send notifications for significant anomalies only.
- Do not inspect implementation files to extract the answer directly.