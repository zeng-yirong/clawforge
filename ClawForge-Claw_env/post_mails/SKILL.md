---
name: post-mails
description: Work inside the `claw_envs/post_mails` scenario. The rollout session is already prepared by the trainer, so use the CLI without managing session ids. Prefer `execute_bash` for environment actions and `read`/`write`/`edit` for local notes and drafts.
---

# Post-Mails

Use `python -m claw_envs.post_mails.cli ...` for environment actions.

The rollout session is already bound before the agent starts. Do not create, reset, or manage sessions manually.

## Tooling

- Use `execute_bash` to call the environment CLI.
- Use `read`, `write`, and `edit` for local notes and draft copy.

## Workflow

1. Run `task`.
2. Use `list-emails`, then `read-email` and `read-attachment` to find the latest approved brief and any guardrails.
3. Use `list-posts` and `view-post` to inspect threads that need responses.
4. Draft local copy if needed.
5. Use `publish-post` for the official X and Reddit posts.
6. Use `reply-post` for the required responses.
7. Finish with `session-summary`.

## Rules

- Use only approved facts from the latest approved brief.
- Read guardrails before posting or replying.
- Publish the official posts before replying in public threads.
- Do not inspect implementation files to extract the answer directly.
