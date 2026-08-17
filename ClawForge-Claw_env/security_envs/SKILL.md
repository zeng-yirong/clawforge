---
name: security-intrusion-response
description: Work inside the `claw_envs/security_envs` scenario for home/office intrusion detection and response. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Security Monitoring - Intrusion Response

Use `python -m claw_envs.security_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `task` to understand the security monitoring and intrusion response goal.
2. Use `zones arm-all` to arm all security zones for monitoring.
3. Use `alerts check` to check if any intrusion is currently detected.
4. Use `doors lock-all` to lock all doors when intrusion is detected.
5. Use `emergency dial` to call police/fire/ambulance services.
6. Use `evidence save` or `evidence snapshot` to preserve evidence.
7. Use `notifications create` or `notifications compose` to notify security contacts.
8. Use `status` to review overall security state.
9. Use `evaluate` to score response quality.

## Closed-Loop Response Chain

```
Detect Intrusion → Lock All Doors → Dial Emergency → Save Evidence → Notify Contacts
```

## Rules

- Always verify zone armed status before relying on intrusion detection.
- Lock doors immediately upon intrusion detection to contain the threat.
- Call emergency services before saving evidence when intrusion is active.
- Notify security contacts after emergency call is placed.
- Preserve evidence before the scene is disturbed.
- Do not inspect implementation files to extract the answer directly.
