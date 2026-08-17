---
name: device-scheduling
description: Work inside the `claw_envs/scheduling_envs` scenario for device automation with custom timed tasks. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Device Scheduling - Custom Timed Tasks for Home Automation

Use `python -m claw_envs.scheduling_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `task` to understand the device scheduling goal.
2. Use `devices list` to view all available devices.
3. Use `devices status <device_id>` to check specific device status.
4. Use `devices on/off <device_id>` to manually control devices.
5. Use `schedules create` to create new schedules with time and repeat type.
6. Use `schedules list` to view all created schedules.
7. Use `schedules enable/disable <schedule_id>` to enable or disable schedules.
8. Use `tasks execute` to trigger execution of due scheduled tasks.
9. Use `tasks upcoming` to see next scheduled tasks.
10. Use `status` to review overall scheduling state.
11. Use `evaluate` to score scheduling performance.

## Repeat Types

- **once**: Execute a single time at specified date/time
- **daily**: Execute every day at the specified time
- **weekly**: Execute on specified days of the week
- **custom**: Execute on custom selected days

## Device Types

- **light**: Smart lights with brightness and color control
- **ac**: Air conditioners with temperature and mode control
- **humidifier**: Humidifiers with humidity level control
- **smart_plug**: Smart plugs for on/off control

## Rules

- Create recurring schedules for regular automation tasks.
- Use appropriate repeat types based on task frequency needs.
- Execute scheduled tasks to trigger device automation.
- Monitor task execution history to verify automation is working.
- Do not inspect implementation files to extract the answer directly.
