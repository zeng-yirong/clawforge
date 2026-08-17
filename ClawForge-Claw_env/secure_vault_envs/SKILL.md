---
name: secure-vault
description: Work inside the `claw_envs/secure_vault_envs` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Secure Vault

Use `python -m claw_envs.secure_vault_envs.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `list-credentials` to see existing credentials.
2. Run `generate-password` to create secure passwords.
3. Run `store-credential` to save new credentials.
4. Run `retrieve-credential` when you need to access credentials.
5. Run `classify-credential` to organize credentials into categories.
6. Run `setup-autofill` to configure autofill for platforms.
7. Run `check-strength` to evaluate password security.
8. Finish with `session-summary`.

## Rules

- Use strong password generation for security.
- Organize credentials into proper categories.
- Setup autofill for frequently used platforms.
- Do not inspect implementation files to extract the answer directly.
