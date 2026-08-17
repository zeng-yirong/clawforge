# Post-Mails Environment

`post_mails` is a CLI-first training environment for this task:

1. Search a noisy inbox for the latest approved brief.
2. Publish the official launch message on X and Reddit.
3. Reply to selected public threads using only approved facts.

The environment is built for parallel rollout:

- each rollout owns one isolated session
- session state is file-backed under a configurable state root
- mutable state is protected by a per-session lock
- there is no shared Flask process or port coordination

## Session Model

Session management is trainer-owned, not agent-owned.

- The trainer prepares one session per rollout sample.
- The trainer binds that session through environment variables.
- Agent commands do not need `--session-id`.

Trainer bootstrap:

```bash
python -m claw_envs.post_mails.cli prepare-rollout --scenario-id orbital_launch --show-bindings --show-task
```

The returned bindings should be injected into the rollout process:

- `POST_MAILS_SESSION_ID`
- `POST_MAILS_STATE_ROOT`
- `POST_MAILS_SCENARIO_ID`

## Agent Commands

After the rollout is prepared, the agent uses the CLI without session arguments:

```bash
python -m claw_envs.post_mails.cli task
python -m claw_envs.post_mails.cli list-emails --unread-only
python -m claw_envs.post_mails.cli read-email --email-id em_004
python -m claw_envs.post_mails.cli read-attachment --attachment-id att_orbital_brief_v3
python -m claw_envs.post_mails.cli list-posts --needs-response-only
python -m claw_envs.post_mails.cli view-post --post-id x_003
python -m claw_envs.post_mails.cli publish-post --platform x --content "<text>"
python -m claw_envs.post_mails.cli reply-post --post-id x_003 --content "<text>"
python -m claw_envs.post_mails.cli session-summary
```

## Data Layout

- `data/accounts.json`: workspace account profile and tone.
- `data/contacts.json`: people referenced in mail and social threads.
- `data/emails/*.json`: inbox items, including noise and stale drafts.
- `data/social/*.json`: public X and Reddit threads.
- `data/attachments/*.md`: briefs, FAQs, and social guardrails.
- `data/scenarios/*.json`: scenario prompts and rollout configuration.

## Concurrency Test

Use the stress script to validate isolation and locking:

```bash
python -m claw_envs.post_mails.concurrency_test --mode both --executor processes --sessions 16 --workers 8 --contention-loops 4 --report-json ./.tmp/post_mails_report.json
```

It checks both:

- isolated parallel sessions
- multi-worker contention on a shared session
