# Server Fault Supabase Environment

`server_fault_supabase_env` is a CLI-first training environment for this workflow:

1. Traverse a preset server fault incident pool.
2. Screen UPS outage and service-down risk tickets.
3. Execute remediation logic on the actionable incidents.
4. Write processed rows into a simulated Supabase in-memory table.
5. Preserve audit logs for every action during the rollout.

The environment follows the rollout/session pattern defined in `claw_env_recipe.md`:

- each rollout owns one isolated session
- mutable state is file-backed under a configurable state root
- per-session locking protects concurrent writes
- agent commands do not require `--session-id`

## Session Model

Session management is trainer-owned, not agent-owned.

- The trainer prepares one session per rollout sample.
- The trainer binds that session through environment variables.
- Agent commands read those bindings automatically.

Trainer bootstrap:

```bash
python -m without_skill.server_fault_supabase_env.cli prepare-rollout --scenario-id server_fault_triage_q2_2026 --show-bindings --show-task
```

Returned bindings:

- `SERVER_FAULT_SUPABASE_SESSION_ID`
- `SERVER_FAULT_SUPABASE_STATE_ROOT`
- `SERVER_FAULT_SUPABASE_SCENARIO_ID`

## Agent Commands

After rollout preparation, the agent uses the CLI without session arguments:

```bash
python -m without_skill.server_fault_supabase_env.cli task
python -m without_skill.server_fault_supabase_env.cli screen-risk-incidents --categories ups_outage,service_down
python -m without_skill.server_fault_supabase_env.cli get-incident --incident-id inc_ups_001
python -m without_skill.server_fault_supabase_env.cli read-attachment --attachment-path runbook_ups_and_service.md
python -m without_skill.server_fault_supabase_env.cli remediate-incident --incident-id inc_srv_001 --remediation-mode guided --operator-note "Restarted affected service and validated health checks."
python -m without_skill.server_fault_supabase_env.cli write-supabase-resolution --incident-id inc_srv_001
python -m without_skill.server_fault_supabase_env.cli list-supabase-rows
python -m without_skill.server_fault_supabase_env.cli list-audit-logs
python -m without_skill.server_fault_supabase_env.cli session-summary
```

## Data Layout

- `data/accounts.json`: workspace account profile and permissions.
- `data/contacts.json`: stakeholders and escalation contacts.
- `data/attachments.json`: attachment manifest for runbooks and write contracts.
- `data/incidents/incident_pool.json`: fault event and work-order samples.
- `data/attachments/*.md`: remediation runbook and simulated Supabase write contract.
- `data/scenarios/*.json`: scenario prompts and evaluation metadata.

## Simulated Supabase Memory

Processed incident rows are stored in `supabase_memory.incident_resolutions`.

Use:

- `list-supabase-rows`
- `get-supabase-row`

Audit logs are stored separately and exposed through:

- `list-audit-logs`
- `get-audit-log`

## Concurrency Test

Use the stress script to validate session isolation and locking:

```bash
python -m without_skill.server_fault_supabase_env.concurrency_test --mode both --executor processes --sessions 16 --workers 6 --report-json ./.tmp/server_fault_supabase_report.json
```

It checks both:

- isolated parallel sessions
- multi-worker contention on a shared session
